from crewai.tools import BaseTool
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pydantic import BaseModel, Field
import logging
import re
import os
import json
import boto3
from botocore.exceptions import ClientError
from typing import Type, Dict, Any


class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity."""
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
    SECRET_NAME: str = "<name-of-secret-in-aws-secrets-manager>"

    def _run(self) -> Dict[str, Any]:
        try:
            # SETUP-REQUIRED: AWS region where that secret lives
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
connection_string = secrets.get("azure_connection_string")
# SETUP-REQUIRED: set to your organization's Azure Blob Storage container name
container_name = "<your-azure-container-name>"
# SETUP-REQUIRED: set to your storage account's blob endpoint and container (shown in the success message only)
blob_storage_url = "<your-storage-account>.blob.core.windows.net/<your-azure-container-name>"


class AzureBlobWriterSchema(BaseModel):
    """Input schema for AzureBlobWriterTool."""
    folder_name: str = Field(..., description="Name of the folder to create in Azure Blob Storage. This will be used as a prefix for organizing files within the container.")
    file_name: str = Field(..., description="Name of the file to create in the specified folder. Should include the file extension (e.g., 'document.txt', 'data.json').")
    content: str = Field(..., description="Content to write to the file. This can be plain text, JSON, CSV, or any string-based content. Maximum size is 10 MB.")


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobWriterTool')


class AzureBlobWriterTool(BaseTool):
    """
    AzureBlobWriterTool - A tool to create folders and files in Azure Blob Storage.
    """
    name: str = "Azure Blob Storage Writer"
    description: str = "A tool to create folders and files in Azure Blob Storage using connection string retrieved from AWS Secrets Manager via Pod Identity."
    args_schema: Type[BaseModel] = AzureBlobWriterSchema

    def _sanitize_path_component(self, component):
        """
        Sanitizes path components to prevent directory traversal and other issues.
        """
        if not component:
            return "default"

        sanitized = re.sub(r'[\\/*?:"<>|]', '_', component)
        sanitized = re.sub(r'\.\.', '_', sanitized)
        sanitized = sanitized.lstrip('./\\')

        return sanitized if sanitized else "default"

    def _validate_content(self, content):
        """
        Validates content to ensure it's safe to upload.
        """
        if not isinstance(content, str):
            logger.warning("Content is not a string, converting to string")
            return str(content)

        max_size = 10 * 1024 * 1024
        if len(content.encode('utf-8')) > max_size:
            logger.warning("Content exceeds maximum allowed size")
            return content[:max_size]

        return content

    def create_folder_and_file_in_blob_storage(self, folder_name, file_name, content):
        """
        Creates a folder and a file in Azure Blob Storage.
        :param folder_name: string, name of the folder to create.
        :param file_name: string, name of the file to create.
        :param content: string, the content you want to save.
        """
        try:
            sanitized_folder_name = folder_name
            sanitized_file_name = self._sanitize_path_component(file_name)
            validated_content = self._validate_content(content)

            if sanitized_folder_name != folder_name:
                logger.warning(f"Folder name sanitized from '{folder_name}' to '{sanitized_folder_name}'")
            if sanitized_file_name != file_name:
                logger.warning(f"File name sanitized from '{file_name}' to '{sanitized_file_name}'")

            blob_service_client = BlobServiceClient.from_connection_string(connection_string)

            try:
                container_client = blob_service_client.get_container_client(container_name)
                if not container_client.exists():
                    container_client = blob_service_client.create_container(container_name)
                    result = f"Container '{container_name}' created successfully. blob_storage_url = '{blob_storage_url}'"
                else:
                    result = f"Container '{container_name}' already exists. blob_storage_url = '{blob_storage_url}'"
            except Exception as e:
                logger.error(f"Error checking/creating container: {str(e)}", exc_info=True)
                return "Error accessing container. Please try again later or contact support."

            folder_path = f"{sanitized_folder_name}/"
            folder_blob_client = container_client.get_blob_client(folder_path)

            try:
                folder_blob_client.upload_blob("", overwrite=True)
                result += f"\nFolder '{sanitized_folder_name}' created successfully."
            except Exception as e:
                logger.error(f"Error creating folder: {str(e)}", exc_info=True)
                return "Error creating folder. Please try again later or contact support."

            file_path = f"{sanitized_folder_name}/{sanitized_file_name}"
            file_blob_client = container_client.get_blob_client(file_path)

            try:
                file_blob_client.upload_blob(validated_content, overwrite=True)
                result += f"\nFile '{sanitized_file_name}' created successfully in folder '{sanitized_folder_name}'."
            except Exception as e:
                logger.error(f"Error creating file: {str(e)}", exc_info=True)
                return "Error creating file. Please try again later or contact support."

            return result

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while processing your request. Please try again later or contact support."

    def _run(self, folder_name: str, file_name: str, content: str) -> str:
        """
        Run method required by CrewAI BaseTool.
        """
        return self.create_folder_and_file_in_blob_storage(folder_name, file_name, content)