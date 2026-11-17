import os
import re
import json
import requests
from typing import Any, Type, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth


import boto3
from botocore.exceptions import ClientError


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity."""
    pass


class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - Reads an AWS Secret using Pod Identity
    and returns the full key-value dict.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads a fixed AWS Secret (set in code) using Pod Identity, and returns all key-value pairs as a dict."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    # Review every line tagged "SETUP-REQUIRED:" below before deploying this tool to a new environment or client.
    # SETUP-REQUIRED: must match the secret name created in your AWS Secrets Manager
    SECRET_NAME: str = "<name-of-secret-in-aws-secrets-manager>"

    def _run(self) -> Dict[str, Any]:
        try:
            # SETUP-REQUIRED: AWS region where that secret lives
            client = boto3.client("secretsmanager", region_name="us-east-1")
            get_secret_value_response = client.get_secret_value(SecretId=self.SECRET_NAME)
            secret_string = get_secret_value_response.get("SecretString", "{}")
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

# ============================================================================
# CONFIGURATION -- Jira connection values are read from AWS Secrets Manager
# ============================================================================
JIRA_BASE_URL = secrets.get("base_url")
JIRA_USER_EMAIL = secrets.get("id")
JIRA_API_TOKEN = secrets.get("api_key")

DEFAULT_ISSUE_TYPE = "Task"
DEFAULT_LINK_TYPE = "Relates"
# ============================================================================


class JiraTasksUploaderSchema(BaseModel):
    inputJSON: Dict[str, Any] = Field(...)

    @field_validator("inputJSON")
    @classmethod
    def validate_input_json(cls, value: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(value, dict):
            raise ValueError("inputJSON must be a dictionary")
        if not value.get("projectKey"):
            raise ValueError("inputJSON.projectKey is required")
        issues = value.get("issues", [])
        if not isinstance(issues, list):
            raise ValueError("inputJSON.issues must be a list")
        for index, issue in enumerate(issues):
            if not isinstance(issue, dict):
                raise ValueError(f"issues[{index}] must be a dictionary")
            if not issue.get("summary"):
                raise ValueError(f"issues[{index}].summary is required")
            if "description" not in issue:
                raise ValueError(f"issues[{index}].description is required")
            if not issue.get("parentKey"):
                raise ValueError(f"issues[{index}].parentKey is required")
        return value


class JiraTasksUploader(BaseTool):
    name: str = "Jira Tasks Uploader"
    description: str = (
        "Creates Jira issues and links each created issue to any existing Jira issue "
        "provided in parentKey, so it appears under Related issues. parentKey is used "
        "as a related issue key, not as Jira's hierarchy parent field."
    )
    args_schema: Type[BaseModel] = JiraTasksUploaderSchema

    base_url: str = JIRA_BASE_URL
    post_url: str = ""
    link_url: str = ""

    def _format_heading(self, key: str) -> str:
        key = re.sub(r"([a-z])([A-Z])", r"\1 \2", key)
        key = key.replace("_", " ")
        return key.capitalize()

    def _normalize_description(self, description):
        if isinstance(description, str):
            return description
        if isinstance(description, dict):
            formatted = []
            for key, value in description.items():
                title = f"**{self._format_heading(key)}**"
                if isinstance(value, list):
                    items = "\n".join([f"- {str(v)}" for v in value])
                    formatted.append(f"{title}\n{items}")
                elif isinstance(value, dict):
                    nested = "\n".join([f"{k}: {v}" for k, v in value.items()])
                    formatted.append(f"{title}\n{nested}")
                else:
                    formatted.append(f"{title}\n{str(value)}")
            return "\n\n".join(formatted)
        return str(description)

    def _parse_inline(self, text: str, id_map: Dict[str, str], base_url: str):
        content = []
        i = 0
        while i < len(text):
            if text[i:i + 2] == "**":
                end = text.find("**", i + 2)
                if end != -1:
                    content.append({
                        "type": "text",
                        "text": text[i + 2:end],
                        "marks": [{"type": "strong"}],
                    })
                    i = end + 2
                    continue
            if text[i] == "*":
                end = text.find("*", i + 1)
                if end != -1:
                    content.append({
                        "type": "text",
                        "text": text[i + 1:end],
                        "marks": [{"type": "em"}],
                    })
                    i = end + 1
                    continue
            match = re.match(r"E\d+(?:\.\w+)*", text[i:])
            if match:
                token = match.group(0)
                if token in id_map:
                    jira_key = id_map[token]
                    content.append({
                        "type": "text",
                        "text": jira_key,
                        "marks": [{
                            "type": "link",
                            "attrs": {"href": f"{base_url}/browse/{jira_key}"},
                        }],
                    })
                else:
                    content.append({"type": "text", "text": token})
                i += len(token)
                continue
            content.append({"type": "text", "text": text[i]})
            i += 1
        return content

    def _convert_description(self, text: str, id_map: Dict[str, str], base_url: str):
        lines = text.split("\n")
        blocks = []
        bullet_buffer = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("- "):
                bullet_buffer.append(stripped[2:])
                continue
            if bullet_buffer:
                blocks.append({
                    "type": "bulletList",
                    "content": [
                        {
                            "type": "listItem",
                            "content": [{
                                "type": "paragraph",
                                "content": self._parse_inline(item, id_map, base_url),
                            }],
                        }
                        for item in bullet_buffer
                    ],
                })
                bullet_buffer = []
            if not stripped:
                continue
            blocks.append({
                "type": "paragraph",
                "content": self._parse_inline(stripped, id_map, base_url),
            })
        if bullet_buffer:
            blocks.append({
                "type": "bulletList",
                "content": [
                    {
                        "type": "listItem",
                        "content": [{
                            "type": "paragraph",
                            "content": self._parse_inline(item, id_map, base_url),
                        }],
                    }
                    for item in bullet_buffer
                ],
            })
        return {"type": "doc", "version": 1, "content": blocks}

    def _create_issue_link(
        self,
        created_issue_key: str,
        related_issue_key: str,
        link_type: str,
        headers: Dict[str, str],
        auth: HTTPBasicAuth,
    ) -> requests.Response:
        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": related_issue_key},
            "outwardIssue": {"key": created_issue_key},
        }
        return requests.post(
            self.link_url,
            json=payload,
            headers=headers,
            auth=auth,
            timeout=(5, 30),
        )

    def _run(self, inputJSON: Dict[str, Any]) -> str:
        results = []
        id_map = {}
        try:
            base_url = (inputJSON.get("baseUrl") or self.base_url or JIRA_BASE_URL).rstrip("/")
            self.base_url = base_url
            self.post_url = base_url + "/rest/api/3/issue"
            self.link_url = base_url + "/rest/api/3/issueLink"

            jira_user = inputJSON.get("userEmail") or JIRA_USER_EMAIL
            jira_token = JIRA_API_TOKEN or os.environ.get("JIRA_API_TOKEN", "")
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            auth = HTTPBasicAuth(jira_user, jira_token)

            project_key = inputJSON.get("projectKey")
            default_type = inputJSON.get("issueType") or DEFAULT_ISSUE_TYPE
            default_link_type = inputJSON.get("linkType") or DEFAULT_LINK_TYPE
            issues = inputJSON.get("issues", [])

            for issue in issues:
                create_response = None
                link_response = None
                try:
                    labels = issue.get("label", [])
                    logical_id = labels[0] if labels else None
                    issue_type = issue.get("issueType") or default_type
                    link_type = issue.get("linkType") or default_link_type
                    related_issue_key = issue.get("parentKey")

                    description_text = self._normalize_description(issue["description"])
                    description_adf = self._convert_description(description_text, id_map, base_url)

                    fields = {
                        "project": {"key": project_key},
                        "summary": issue["summary"],
                        "issuetype": {"name": issue_type},
                        "labels": labels,
                        "description": description_adf,
                    }

                    # Deliberately do not send Jira's fields.parent. Jira controls which
                    # issue types are allowed in its hierarchy. parentKey is instead used
                    # below to create a Related issues link to any existing issue type.
                    create_response = requests.post(
                        self.post_url,
                        json={"fields": fields},
                        headers=headers,
                        auth=auth,
                        timeout=(5, 30),
                    )
                    print("Create status:", create_response.status_code)
                    print("Create response:", create_response.text)

                    if not create_response.ok:
                        results.append(
                            f"Failed: {issue.get('summary')} -> HTTP {create_response.status_code} "
                            f"| Detail: {create_response.text}"
                        )
                        continue

                    issue_key = create_response.json().get("key")
                    if not issue_key:
                        results.append(
                            f"Failed: {issue.get('summary')} -> Jira returned no issue key "
                            f"| Detail: {create_response.text}"
                        )
                        continue

                    link_response = self._create_issue_link(
                        created_issue_key=issue_key,
                        related_issue_key=related_issue_key,
                        link_type=link_type,
                        headers=headers,
                        auth=auth,
                    )
                    print("Link status:", link_response.status_code)
                    print("Link response:", link_response.text)

                    if not link_response.ok:
                        results.append(
                            f"{issue_type} created: {issue_key}, but linking to "
                            f"{related_issue_key} failed -> HTTP {link_response.status_code} "
                            f"| Detail: {link_response.text}"
                        )
                        continue

                    if logical_id:
                        id_map[logical_id] = issue_key

                    results.append(
                        f"{issue_type} created: {issue_key} | Related to: "
                        f"{related_issue_key} | Link type: {link_type}"
                    )

                except requests.RequestException as e:
                    if link_response is not None:
                        detail = link_response.text
                    elif create_response is not None:
                        detail = create_response.text
                    else:
                        detail = "No response received"
                    results.append(
                        f"Failed: {issue.get('summary')} -> {str(e)} | Detail: {detail}"
                    )

        except Exception as e:
            return f"Fatal error: {str(e)}"

        return "\n".join(results)
