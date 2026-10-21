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
    SECRET_NAME: str = "aava/temp/varun-temp-key-values"

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
connection_string = secrets.get("azure_connection_string")

# SETUP-REQUIRED: set to your organization's Azure Blob Storage container name
container_name = "aava-ggm"


# Define the args schema for your tool
class AzureBlobReaderSchema(BaseModel):
    folder_name: str = Field(..., description="Name of the folder in Azure Blob Storage whose files should be read")


# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobReaderTool')


class AzureBlobReaderTool(BaseTool):
    name: str = "Azure Blob Reader Tool"
    description: str = "Reads and prints the contents of all files inside a folder in Azure Blob Storage."
    args_schema: type[BaseModel] = AzureBlobReaderSchema

    def __init__(self):
        super().__init__(
            name="Azure Blob Reader Tool",
            description="Reads and prints the contents of all files inside a folder in Azure Blob Storage."
        )

    def read_all_files_in_folder(self, folder_name):
        """
        Lists every blob under the given folder prefix, downloads each one,
        and returns (and prints) their contents.

        :param folder_name: string, name of the folder to read from.
        Returns:
            str: A formatted dump of every file's name and content, or an error message.
        """
        try:
            # Normalize the prefix so it always ends in exactly one slash.
            prefix = folder_name.rstrip("/") + "/" if folder_name else ""

            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(container_name)

            if not container_client.exists():
                msg = f"Container '{container_name}' does not exist."
                logger.error(msg)
                return msg

            # List all blobs that live under this folder prefix.
            blob_list = list(container_client.list_blobs(name_starts_with=prefix))

            if not blob_list:
                msg = f"No files found in folder '{folder_name}'."
                logger.info(msg)
                print(msg)
                return msg

            output_sections = []
            file_count = 0

            for blob in blob_list:
                # Skip the virtual "folder" placeholder blob (the empty "folder_name/" blob).
                if blob.name == prefix or blob.name.endswith("/"):
                    continue

                blob_client = container_client.get_blob_client(blob.name)

                try:
                    downloaded = blob_client.download_blob().readall()
                except Exception as e:
                    logger.error(f"Error downloading '{blob.name}': {str(e)}", exc_info=True)
                    output_sections.append(
                        f"===== FILE: {blob.name} =====\n[Error reading this file]\n"
                    )
                    continue

                # Try to decode as UTF-8 text; fall back to a note for binary content.
                try:
                    text = downloaded.decode("utf-8")
                except UnicodeDecodeError:
                    text = f"[Binary content, {len(downloaded)} bytes — not displayed as text]"

                file_count += 1
                section = f"===== FILE: {blob.name} =====\n{text}\n"
                output_sections.append(section)
                print(section)

            if file_count == 0:
                msg = f"Folder '{folder_name}' contains no readable files (only the folder marker)."
                logger.info(msg)
                print(msg)
                return msg

            header = f"Read {file_count} file(s) from folder '{folder_name}':\n\n"
            return header + "\n".join(output_sections)

        except Exception as e:
            # Log the full error details but return a generic message.
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while reading the folder"

    def _run(self, folder_name):
        """
        Run method required by CrewAI BaseTool.

        Args:
            folder_name (str): Name of the folder to read from.

        Returns:
            str: The contents of all files in the folder.
        """
        return self.read_all_files_in_folder(folder_name)