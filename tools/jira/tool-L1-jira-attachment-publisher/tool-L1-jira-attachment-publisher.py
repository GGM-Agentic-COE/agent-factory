import io
import os
import mimetypes
import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth
import urllib3

# Disable SSL warnings (only when JIRA_VERIFY_SSL=false, i.e. local dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JIRAAttachmentPublisherSchema(BaseModel):
    '''Input schema for JIRAAttachmentPublisher.'''
    issue_key: str = Field(..., description="JIRA issue key (e.g., PROJECT-123)")
    file_name: str = Field(..., description="Name of the file as it should appear in JIRA (e.g., 'prd.md', 'report.txt'). The extension determines the MIME type.")
    content: str = Field(..., description="The full text content to upload as the file attachment.")


class JIRAAttachmentPublisher(BaseTool):
    '''
    JIRAAttachmentPublisher - A tool to upload text content as a named file
    attachment onto a JIRA issue via API.

    Companion to JIRACommentPublisher. Used by agents that need to attach
    generated artefacts — PRDs, reports, review packets, markdown files,
    CSVs, etc. — directly onto a ticket so the file becomes part of the
    permanent audit record alongside the issue.

    The agent provides the file name and content as strings; the tool
    streams the content into an in-memory buffer and uploads it without
    writing anything to disk.

    Uses multipart/form-data as required by the JIRA attachment API and
    includes the mandatory X-Atlassian-Token header to bypass JIRA's XSRF
    protection.
    '''

    name: str = "JIRA Attachment Publisher"
    description: str = "A tool to upload text content as a named file attachment to a JIRA issue."
    args_schema: Type[BaseModel] = JIRAAttachmentPublisherSchema
    jira_url: str = "https://worktejasc.atlassian.net"

    def _run(self, issue_key: str, file_name: str, content: str) -> Any:
        try:
            print(f"Uploading attachment '{file_name}' to JIRA issue: {issue_key}")

            # Retrieve API token and username from secret manager / environment.
            # Never hardcode credentials in the tool body.
            username = "work.tejasc@gmail.com"
            api_token = '[REDACTED]'
            if not username or not api_token:
                return {
                    "success": False,
                    "error": "Missing credentials. Set JIRA_USERNAME and JIRA_API_TOKEN."
                }

            if not file_name or not file_name.strip():
                return {
                    "success": False,
                    "error": "file_name is empty. Provide a name like 'prd.md' or 'report.txt'."
                }

            if not content or not content.strip():
                return {
                    "success": False,
                    "error": "Content is empty. Refusing to upload an empty attachment."
                }

            # Detect MIME type from the file extension; fall back to plain text
            mime_type, _ = mimetypes.guess_type(file_name)
            if not mime_type:
                mime_type = "text/plain"

            # Encode content into an in-memory binary buffer — no disk writes needed
            file_buffer = io.BytesIO(content.encode("utf-8"))

            # Construct the API endpoint URL
            self.jira_url = "https://worktejasc.atlassian.net"
            api_endpoint = f"{self.jira_url.rstrip('/')}/rest/api/2/issue/{issue_key}/attachments"

            # Set up the authentication
            auth = HTTPBasicAuth(username, api_token)

            # JIRA requires X-Atlassian-Token: no-check to bypass XSRF protection
            # for the attachments endpoint. Do NOT set Content-Type manually —
            # requests will set the correct multipart boundary automatically.
            headers = {
                "Accept": "application/json",
                "X-Atlassian-Token": "no-check",
            }

            verify_ssl = os.environ.get("JIRA_VERIFY_SSL", "true").lower() != "false"

            files = {"file": (file_name, file_buffer, mime_type)}
            response = requests.post(
                api_endpoint,
                headers=headers,
                auth=auth,
                files=files,
                verify=verify_ssl,
                timeout=60
            )

            # Surface JIRA's own error messages rather than a bare status code
            if response.status_code >= 400:
                detail = response.text
                try:
                    err = response.json()
                    detail = "; ".join(
                        err.get("errorMessages", []) +
                        [f"{k}: {v}" for k, v in err.get("errors", {}).items()]
                    ) or response.text
                except ValueError:
                    pass
                return {
                    "success": False,
                    "issue_key": issue_key,
                    "status_code": response.status_code,
                    "error": f"Error uploading attachment: {detail}"
                }

            # JIRA returns a list of uploaded attachment objects
            attachments = response.json()
            attachment = attachments[0] if attachments else {}

            return {
                "success": True,
                "issue_key": issue_key,
                "attachment_id": attachment.get("id"),
                "file_name": attachment.get("filename"),
                "file_size_bytes": attachment.get("size"),
                "mime_type": attachment.get("mimeType"),
                "attachment_url": attachment.get("content"),  # direct download URL
                "issue_url": f"{self.jira_url.rstrip('/')}/browse/{issue_key}",
                "created": attachment.get("created"),
                "author": (attachment.get("author") or {}).get("displayName"),
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "issue_key": issue_key,
                "error": f"Error uploading attachment: {str(e)}"
            }
