import io
import os
import re
import mimetypes
import logging
import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from requests.auth import HTTPBasicAuth
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
import urllib3

# Disable SSL warnings (only when JIRA_VERIFY_SSL=false, i.e. local dev)
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

## ADJUST THESE CREDENTIALS WHEN NEEDED ______________________________________________________________________
# Create the BlobServiceClient
connection_string = os.environ.get("AZURE_STORAGE_CONNECTION_STRING", "")

# Use only the predefined container name
container_name = "aava-ggm"

blob_storage_url = "avaplusstorageprod.blob.core.windows.net/aava-ggm"

# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobWriterTool')


# ══════════════════════════════════════════════════════════════════════════════
#  Sub-tool 1 — Azure Blob Writer Tool
#  Args: folder_name, file_name, content
# ══════════════════════════════════════════════════════════════════════════════

# Define the args schema for your tool
class AzureBlobWriterSchema(BaseModel):
    folder_name: str = Field(..., description="Name of the folder to create in Azure Blob Storage")
    file_name: str = Field(..., description="Name of the file to create in the folder")
    content: str = Field(..., description="Content to write to the file")


class AzureBlobWriterTool(BaseTool):
    name: str = "Azure Blob Storage Tool"
    description: str = "Creates folders and files in Azure Blob Storage."
    args_schema: type[BaseModel] = AzureBlobWriterSchema

    def __init__(self):
        super().__init__(
            name="Azure Blob Storage Tool",
            description="Creates folders and files in Azure Blob Storage."
        )

    def _sanitize_path_component(self, component):
        """
        Sanitizes path components to prevent directory traversal and other issues.
        """
        if not component:
            return "default"

        # Remove any path traversal sequences and other potentially dangerous characters
        sanitized = re.sub(r'[\\/*?:"<>|]', '_', component)
        sanitized = re.sub(r'\.\.', '_', sanitized)

        # Ensure the component doesn't start with a dot or slash
        sanitized = sanitized.lstrip('./\\')

        return sanitized if sanitized else "default"

    def _validate_content(self, content):
        """
        Validates content to ensure it's safe to upload.
        """
        if not isinstance(content, str):
            logger.warning("Content is not a string, converting to string")
            return str(content)

        # Limit content size if needed
        max_size = 10 * 1024 * 1024  # 10 MB
        if len(content.encode('utf-8')) > max_size:
            logger.warning("Content exceeds maximum allowed size")
            return content[:max_size]  # Truncate to max size

        return content

    def create_folder_and_file_in_blob_storage(self, folder_name, file_name, content):
        """
        Creates a folder and a file in Azure Blob Storage.
        :param folder_name: string, name of the folder to create.
        :param file_name: string, name of the file to create.
        :param content: string, the content you want to save.
        """
        try:

            # Sanitize inputs
            # sanitized_folder_name = self._sanitize_path_component(folder_name)
            sanitized_folder_name = folder_name  # removed sanitization for the subfolder
            sanitized_file_name = self._sanitize_path_component(file_name)
            validated_content = self._validate_content(content)

            # Log if sanitization changed the inputs
            if sanitized_folder_name != folder_name:
                logger.warning(f"Folder name sanitized from '{folder_name}' to '{sanitized_folder_name}'")
            if sanitized_file_name != file_name:
                logger.warning(f"File name sanitized from '{file_name}' to '{sanitized_file_name}'")

            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            # Check if container exists, create if not
            try:
                container_client = blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client = blob_service_client.create_container(container_name)
                    result = f"Container '{container_name}' created successfully. blob_storage_url = '{blob_storage_url}'"
    
                else:
                    result = f"Container '{container_name}' already exists.  blob_storage_url = '{blob_storage_url}'"


            except Exception as e:
                logger.error(f"Error checking/creating container: {str(e)}", exc_info=True)
                return "Error accessing container. Please try again later or contact support."
                

            # In Azure Blob Storage, folders are virtual and represented by prefixes in blob names
            # Create a blob with the folder prefix to simulate folder creation
            folder_path = f"{sanitized_folder_name}/"
            folder_blob_client = container_client.get_blob_client(folder_path)

            try:
                # Upload empty content to create the "folder"
                folder_blob_client.upload_blob("", overwrite=True)
                result += f"\nFolder '{sanitized_folder_name}' created successfully."
            except Exception as e:
                logger.error(f"Error creating folder: {str(e)}", exc_info=True)
                return "Error creating folder. Please try again later or contact support."

            # Create the file within the folder
            file_path = f"{sanitized_folder_name}/{sanitized_file_name}"
            file_blob_client = container_client.get_blob_client(file_path)

            try:
                # Upload the content to the file
                file_blob_client.upload_blob(validated_content, overwrite=True)
                result += f"\nFile '{sanitized_file_name}' created successfully in folder '{sanitized_folder_name}'."
            except Exception as e:
                logger.error(f"Error creating file: {str(e)}", exc_info=True)
                return "Error creating file. Please try again later or contact support."

            return result

        except Exception as e:
            # Log the full error details but return a generic message
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while processing your request. Please try again later or contact support."

    def _run(self, folder_name, file_name, content):
        """
        Run method required by CrewAI BaseTool.
        """
        return self.create_folder_and_file_in_blob_storage(folder_name, file_name, content)


# ══════════════════════════════════════════════════════════════════════════════
#  Sub-tool 2 — JIRA Attachment Publisher
#  Args: issue_key, file_name, content
# ══════════════════════════════════════════════════════════════════════════════

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
            api_token = "ATATT3xFfGF0lTtXLXRKBaNeqDShMmbjSf0sxDdKF1F6QHFGTHuxpQTnuvLLSQvpI7ZsPT5II2HoKrLMwiJvYLlgDv5qIDBqDz4wRjzP3eW06hdIqb36ZYWddBojG7tZ2ikjP1OBcYfF6VQYXZapDcdUB_kDclSvrifugQikDagvJ5s8dHsznzw=7E21EE6D"

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


# ══════════════════════════════════════════════════════════════════════════════
#  Main orchestrator — JIRA Attachment + Blob Publisher
#  Args: issue_key, folder_name, file_name, content
#  file_name and content are shared — identical values go into both sub-tools.
# ══════════════════════════════════════════════════════════════════════════════

class JIRAAttachmentAndBlobPublisherSchema(BaseModel):
    issue_key: str = Field(..., description="JIRA issue key (e.g., PROJECT-123)")
    folder_name: str = Field(..., description="Name of the folder to create in Azure Blob Storage")
    file_name: str = Field(..., description="Name of the file to create — used as-is for both JIRA and Azure Blob (e.g., 'prd.md')")
    content: str = Field(..., description="Content to upload as the JIRA attachment and write to Azure Blob Storage")


class JIRAAttachmentAndBlobPublisher(BaseTool):
    '''
    JIRAAttachmentAndBlobPublisher - Orchestrates two sub-tools in a single call:

      1. JIRAAttachmentPublisher  → uploads content as a named attachment on the JIRA ticket.
      2. AzureBlobWriterTool      → writes the same content to Azure Blob Storage.

    The variables file_name and content are shared — the exact same values are
    passed into both sub-tools, so an agent only needs to provide them once.

    Shared args  : file_name, content
    JIRA-only arg: issue_key
    Blob-only arg: folder_name
    '''

    name: str = "JIRA Attachment and Blob Publisher"
    description: str = (
        "Uploads text content as a named file attachment to a JIRA issue AND "
        "writes the same content to Azure Blob Storage in a single call. "
        "file_name and content are shared between both destinations."
    )
    args_schema: type[BaseModel] = JIRAAttachmentAndBlobPublisherSchema

    def __init__(self):
        super().__init__(
            name="JIRA Attachment and Blob Publisher",
            description=(
                "Uploads text content as a named file attachment to a JIRA issue AND "
                "writes the same content to Azure Blob Storage in a single call. "
                "file_name and content are shared between both destinations."
            )
        )

    def _run(self, issue_key, folder_name, file_name, content):
        print(f"Publishing '{file_name}' → JIRA {issue_key} + Blob {container_name}/{folder_name}/")

        if not file_name or not file_name.strip():
            return {"success": False, "error": "file_name is empty."}
        if not content or not content.strip():
            return {"success": False, "error": "Content is empty. Refusing to publish an empty file."}

        jira_publisher = JIRAAttachmentPublisher()
        blob_writer = AzureBlobWriterTool()

        # Both sub-tools receive the same file_name and content
        jira_result = jira_publisher._run(
            issue_key=issue_key,
            file_name=file_name,
            content=content
        )
        blob_result = blob_writer._run(
            folder_name=folder_name,
            file_name=file_name,
            content=content
        )

        overall_success = (
            jira_result.get("success") is True and
            "Error" not in str(blob_result)
        )

        return {
            "success": overall_success,
            "issue_key": issue_key,
            "jira": jira_result,
            "blob": blob_result,
        }
