import os         
import re
import requests
from typing import Any, Type, Dict
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth


import json
import boto3
from botocore.exceptions import ClientError


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
    SECRET_NAME: str = "aava-secret-manager-jira-credentials"


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

# ============================================================================
# CONFIGURATION  --  edit these values for your Jira space
# ============================================================================
JIRA_BASE_URL      = secrets.get("base_url")                     # from AWS Secrets Manager
JIRA_USER_EMAIL    = secrets.get("user_email")                   #from AWS Secrets Manager
JIRA_API_TOKEN     = secrets.get("api_token")                    #from AWS Secrets Manager
DEFAULT_ISSUE_TYPE = "Epic"                                     
# ============================================================================


class JiraIssueCreatorSchema(BaseModel):
    inputJSON: Dict[str, Any] = Field(...)


class JiraIssueCreator(BaseTool):

    name: str = "Jira Issue Creator"
    description: str = "Creates Jira issues with formatted descriptions and Jira links"
    args_schema: Type[BaseModel] = JiraIssueCreatorSchema

    base_url: str = JIRA_BASE_URL   
    post_url: str = ""

    def _format_heading(self, key: str) -> str:
        key = re.sub(r'([a-z])([A-Z])', r'\1 \2', key)
        key = key.replace('_', ' ')
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
            if text[i:i+2] == "**":
                end = text.find("**", i+2)
                if end != -1:
                    content.append({"type": "text", "text": text[i+2:end],
                                    "marks": [{"type": "strong"}]})
                    i = end + 2
                    continue
            if text[i] == "*":
                end = text.find("*", i+1)
                if end != -1:
                    content.append({"type": "text", "text": text[i+1:end],
                                    "marks": [{"type": "em"}]})
                    i = end + 1
                    continue
            match = re.match(r'E\d+(?:\.\w+)*', text[i:])
            if match:
                token = match.group(0)
                if token in id_map:
                    jira_key = id_map[token]
                    content.append({"type": "text", "text": jira_key,
                                    "marks": [{"type": "link",
                                               "attrs": {"href": f"{base_url}/browse/{jira_key}"}}]})
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
                blocks.append({"type": "bulletList",
                               "content": [{"type": "listItem",
                                            "content": [{"type": "paragraph",
                                                         "content": self._parse_inline(item, id_map, base_url)}]}
                                           for item in bullet_buffer]})
                bullet_buffer = []
            if not stripped:
                continue
            blocks.append({"type": "paragraph",
                           "content": self._parse_inline(stripped, id_map, base_url)})
        if bullet_buffer:
            blocks.append({"type": "bulletList",
                           "content": [{"type": "listItem",
                                        "content": [{"type": "paragraph",
                                                     "content": self._parse_inline(item, id_map, base_url)}]}
                                       for item in bullet_buffer]})
        return {"type": "doc", "version": 1, "content": blocks}

    def _run(self, inputJSON: Dict[str, Any]) -> str:
        results = []
        id_map = {}
        try:
            base_url = (inputJSON.get("baseUrl") or self.base_url or JIRA_BASE_URL).rstrip("/")
            self.base_url = base_url
            self.post_url = base_url + "/rest/api/3/issue"

            jira_user = inputJSON.get("userEmail") or JIRA_USER_EMAIL
            jira_token = inputJSON.get("apiToken") or JIRA_API_TOKEN or os.environ.get("JIRA_API_TOKEN", "")
            headers = {"Content-Type": "application/json", "Accept": "application/json"}
            auth = HTTPBasicAuth(jira_user, jira_token)

            project_key = inputJSON.get("projectKey")
            default_type = inputJSON.get("issueType") or DEFAULT_ISSUE_TYPE
            issues = inputJSON.get("issues", [])

            for issue in issues:
                response = None
                try:
                    labels = issue.get("label", [])
                    logical_id = labels[0] if labels else None

                    issue_type = issue.get("issueType") or default_type   # FIX #4/#5
                    description_text = self._normalize_description(issue["description"])
                    description_adf = self._convert_description(description_text, id_map, base_url)

                    fields = {
                        "project": {"key": project_key},                  # FIX #4
                        "summary": issue["summary"],
                        "issuetype": {"name": issue_type},                # FIX #4
                        "labels": labels,
                        "description": description_adf,
                    }
                    if issue.get("parentKey"):
                        fields["parent"] = {"key": issue["parentKey"]}

                    response = requests.post(self.post_url, json={"fields": fields},
                                             headers=headers, auth=auth)
                    print("Status:", response.status_code)
                    print("Response:", response.text)

                    if not response.ok:
                        results.append(f"Failed: {issue.get('summary')} "
                                       f"→ HTTP {response.status_code} | Detail: {response.text}")
                        continue

                    response.raise_for_status()
                    issue_key = response.json().get("key")
                    if logical_id:
                        id_map[logical_id] = issue_key
                    results.append(f"{issue_type} created: {issue_key}. jira_issue_link = {JIRA_BASE_URL}/browse/{issue_key}")  # FIX #5

                except requests.RequestException as e:
                    detail = response.text if response is not None else "No response received"
                    results.append(f"Failed: {issue.get('summary')} → {str(e)} | Detail: {detail}")

        except Exception as e:
            return f"Fatal error: {str(e)}"

        return "\n".join(results)
