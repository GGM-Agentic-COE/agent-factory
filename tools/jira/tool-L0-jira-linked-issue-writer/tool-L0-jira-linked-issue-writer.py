import os
import re
import requests
from typing import Any, Type, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth
import AVASecret


# ============================================================================
# CONFIGURATION  --  Jira connection values are read from AVASecret
# ============================================================================
JIRA_BASE_URL     = None                     # from AVASecret
JIRA_USER_EMAIL   = None                           # from AVASecret
JIRA_API_TOKEN    = None                      # from AVASecret
DEFAULT_LINK_TYPE  = "Relates"                                  # Jira link type used to relate a Task to its IssueID
# ============================================================================


class JiraTasksUploaderSchema(BaseModel):
    inputJSON: Dict[str, Any] = Field(...)


class JiraTasksUploader(BaseTool):
    name: str = "Jira Tasks Uploader"
    description: str = "Creates Jira issues of the issueType given in the payload and links each one to the IssueID given by IssueID as a related issue"
    args_schema: Type[BaseModel] = JiraTasksUploaderSchema
    base_url: str = JIRA_BASE_URL
    post_url: str = ""
    link_url: str = ""

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

    def _link_to_SourceIssueId(self, issue_key: str, SourceIssueId: str, link_type: str, headers, auth):
        payload = {
            "type": {"name": link_type},
            "inwardIssue": {"key": issue_key},
            "outwardIssue": {"key": SourceIssueId},
        }
        response = requests.post(self.link_url, json=payload, headers=headers, auth=auth)
        print("Link Status:", response.status_code)
        print("Link Response:", response.text)
        return response

    def _run(self, inputJSON: Dict[str, Any]) -> str:
        global JIRA_BASE_URL, JIRA_USER_EMAIL, JIRA_API_TOKEN
        # Secrets retrieved via AVASecret
        try:
            JIRA_BASE_URL   = AVASecret.getValue("base_url")
            JIRA_USER_EMAIL = AVASecret.getValue("id")
            JIRA_API_TOKEN  = AVASecret.getValue("api_key")
        except Exception as e:
            return f"Error retrieving secrets from AVASecret: {str(e)}"

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
            default_type = inputJSON.get("issueType")
            default_SourceIssueId = inputJSON.get("SourceIssueId")
            link_type = inputJSON.get("linkType") or DEFAULT_LINK_TYPE
            issues = inputJSON.get("issues", [])
            for issue in issues:
                response = None
                try:
                    labels = issue.get("label", [])
                    logical_id = labels[0] if labels else None
                    issue_type = issue.get("issueType") or default_type
                    SourceIssueId = issue.get("SourceIssueId") or default_SourceIssueId
                    if not issue_type:
                        results.append(f"Failed: {issue.get('summary')} → no issueType supplied in payload")
                        continue
                    if not SourceIssueId:
                        results.append(f"Failed: {issue.get('summary')} → no SourceIssueId supplied in payload")
                        continue
                    description_text = self._normalize_description(issue["description"])
                    description_adf = self._convert_description(description_text, id_map, base_url)
                    fields = {
                        "project": {"key": project_key},
                        "summary": issue["summary"],
                        "issuetype": {"name": issue_type},
                        "labels": labels,
                        "description": description_adf,
                    }
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
                    response = self._link_to_SourceIssueId(issue_key, SourceIssueId, link_type, headers, auth)
                    if not response.ok:
                        results.append(f"{issue_type} created: {issue_key} | Link to {SourceIssueId} failed "
                                       f"→ HTTP {response.status_code} | Detail: {response.text}")
                        continue
                    results.append(f"{issue_type} created: {issue_key} | Linked to {SourceIssueId} ({link_type})")
                except requests.RequestException as e:
                    detail = response.text if response is not None else "No response received"
                    results.append(f"Failed: {issue.get('summary')} → {str(e)} | Detail: {detail}")
        except Exception as e:
            return f"Fatal error: {str(e)}"
        return "\n".join(results)
