'''
sample JSON input

[
  { "src": { "filename": "main.py", "code": "def main():\n    print('hi')\n" } },
  { "src/utils": { "filename": "helpers.py", "code": "def add(a, b):\n    return a + b\n" } }
]

'''

import datetime
from typing import Any, Type, List
import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool


import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity. """
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads a AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Review every line tagged "SETUP-REQUIRED:" below before deploying this tool to a new environment or client.
    # SETUP-REQUIRED: must match the secret name created in your AWS Secrets Manager
    SECRET_NAME: str = "aava-secret-manager-github-credentials"


    def _run(self) -> Dict[str, Any]:
        try:

            # SETUP-REQUIRED: AWS region where that secret lives (us-east-1 or us-east-2 depending on deployment)

            client = boto3.client('secretsmanager', region_name='us-east-1')
            get_secret_value_response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = get_secret_value_response.get('SecretString', '{}')
            secret_dict = json.loads(secret_string)

            if not isinstance(secret_dict, dict):
                raise ValueError(f"Secret value is not a JSON object: {secret_dict}")

            return secret_dict

        except ClientError as e:
            raise RuntimeError(f"Error retrieving secret: {str(e)}")
        except Exception as ex:
            raise RuntimeError(f"Unexpected error: {str(ex)}")


reader = AWSSecretReaderPodIdentity()
secrets = reader._run()

# Secret retrieved from AWS Secrets Manager
github_token = secrets.get("github_token")

# SETUP-REQUIRED: set to your GitHub organization or username
repo_owner = "varun-ascendion"


class GithubCommitSchema(BaseModel):
    """Input schema for GithubCommitterTool."""
    files: List[dict] = Field(
        ...,
        description="List of dicts with 'filename' (path) and 'code' keys. Example: [{'filename': 'docs/api.txt', 'code': '...'}]"
    )
    repo_name: str = Field(..., description="The name of the repository. Example: 'SCIB-Inception'.")
    new_branch: str = Field(..., description="The new branch to create and commit to. Example: 'feature/auto-update'.")
    source_branch: str = Field(default="main", description="The branch to copy from. Defaults to 'main'.")


class GithubCommitterTool(BaseTool):
    name: str = "Github Branch Committer"
    description: str = "Creates a new branch from a source branch and commits files to it."
    args_schema: Type[BaseModel] = GithubCommitSchema

    def _run(self, files: List[dict], repo_name: str, new_branch: str, source_branch: str = "main") -> Any:
        try:

            headers = {
                "Authorization": f"token {github_token}",
                "Accept": "application/vnd.github+json",
                "User-Agent": "Automation-Agent"
            }
            base_api = f"https://api.github.com/repos/{repo_owner}/{repo_name}"

            # 1. Get current SHA of the SOURCE branch (e.g. main)
            resp = requests.get(f"{base_api}/git/ref/heads/{source_branch}", headers=headers)
            resp.raise_for_status()
            source_sha = resp.json()["object"]["sha"]

            # 2. Create the new branch ref pointing at the source SHA (the "copy")
            #    If it already exists, GitHub returns 422 — handle that gracefully.
            create_ref_resp = requests.post(
                f"{base_api}/git/refs",
                headers=headers,
                json={"ref": f"refs/heads/{new_branch}", "sha": source_sha},
            )
            if create_ref_resp.status_code == 422:
                # Branch already exists — fetch its current SHA and commit on top of it.
                existing = requests.get(f"{base_api}/git/ref/heads/{new_branch}", headers=headers)
                existing.raise_for_status()
                current_sha = existing.json()["object"]["sha"]
            else:
                create_ref_resp.raise_for_status()
                current_sha = source_sha

# 3. Normalize file descriptors (accept BOTH flat and nested formats)
            tree_items = []
            resolved_paths = []
            for file_info in files:
                folder = None
                data = file_info

                # Nested: {"<folder>": {"filename": ..., "code": ...}}
                if "filename" not in file_info and len(file_info) == 1:
                    key, value = next(iter(file_info.items()))
                    if isinstance(value, dict) and "filename" in value:
                        folder, data = key, value

                filename = (data.get("filename") or "script.py").lstrip("/")
                content = data.get("code", "")

                filepath = f"{folder.strip('/')}/{filename}" if folder else filename
                resolved_paths.append(filepath)

                tree_items.append({
                    "path": filepath,
                    "mode": "100644",
                    "type": "blob",
                    "content": content,
                })

            # 4. Create the Tree object (based on the new branch's current tree)
            tree_payload = {"base_tree": current_sha, "tree": tree_items}
            tree_resp = requests.post(f"{base_api}/git/trees", headers=headers, json=tree_payload)
            tree_resp.raise_for_status()
            new_tree_sha = tree_resp.json()["sha"]

            # 5. Create the Commit
            commit_payload = {
                "message": f"Automation Update: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                "tree": new_tree_sha,
                "parents": [current_sha],
            }
            commit_resp = requests.post(f"{base_api}/git/commits", headers=headers, json=commit_payload)
            commit_resp.raise_for_status()
            new_commit_sha = commit_resp.json()["sha"]

            # 6. Update the NEW branch reference
            ref_resp = requests.patch(
                f"{base_api}/git/refs/heads/{new_branch}",
                headers=headers,
                json={"sha": new_commit_sha},
            )
            ref_resp.raise_for_status()

            return {
                "status": "success",
                "branch": new_branch,
                "source_branch": source_branch,
                "updated_files": resolved_paths,
                "message": f"Created '{new_branch}' from '{source_branch}' and committed {len(files)} file(s).",
                "url": f"https://github.com/{repo_owner}/{repo_name}/tree/{new_branch}",
            }

        except Exception as e:
            return {"status": "failure", "message": str(e)}
