import json
import boto3
import logging
from typing import Type, Dict, Any, List
from pydantic import BaseModel, Field, field_validator
from crewai.tools import BaseTool
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from botocore.exceptions import ClientError


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
    SECRET_NAME: str = "aava/temp/varun-temp-key-values"

    def _run(self) -> Dict[str, Any]:
        try:
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
connection_string = secrets.get("azure_connection_string")
container_name = "aava-ggm"


class AzureBlobReaderSchema(BaseModel):
    """Input schema for AzureBlobReaderTool."""
    folder_name: str = Field(..., description="Name of the folder in Azure Blob Storage that contains the files to be read")
    file_names: List[str] = Field(..., description="List of specific file names inside the folder to read, e.g. ['file-1.md', 'file-2.md']. Only these files will be read and all other files in the folder will be ignored")

    @field_validator("file_names", mode="before")
    @classmethod
    def coerce_file_names(cls, value):
        """
        Normalize file_names input to handle JSON strings or comma-separated strings.
        """
        if isinstance(value, str):
            stripped = value.strip()
            try:
                parsed = json.loads(stripped)
                value = parsed if isinstance(parsed, list) else [parsed]
            except (json.JSONDecodeError, ValueError):
                value = [part.strip() for part in stripped.split(",")]

        if not isinstance(value, (list, tuple)):
            value = [value]

        cleaned = [str(item).strip().strip('"').strip("'") for item in value]
        return [item for item in cleaned if item]


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobReaderTool')


class AzureBlobReaderTool(BaseTool):
    """
    AzureBlobReaderTool - A tool to read specific files from Azure Blob Storage folder.
    """
    name: str = "Azure Blob Reader Tool"
    description: str = "Reads and prints the contents of specific named files inside a folder in Azure Blob Storage. Requires a folder name and the list of file names to read."
    args_schema: Type[BaseModel] = AzureBlobReaderSchema

    @staticmethod
    def _resolve_blob_path(prefix, file_name):
        """
        Build the full blob path for a requested file name.
        """
        cleaned = file_name.strip().lstrip("/")
        if prefix and cleaned.startswith(prefix):
            return cleaned
        return f"{prefix}{cleaned}"

    def read_files_in_folder(self, folder_name, file_names):
        """
        Downloads only the named files under the given folder prefix and returns their contents.
        """
        try:
            validated = AzureBlobReaderSchema(folder_name=folder_name, file_names=file_names)
            folder_name = validated.folder_name
            file_names = validated.file_names

            if not file_names:
                msg = "No file names were provided. Provide at least one file name to read."
                logger.info(msg)
                print(msg)
                return msg

            prefix = folder_name.rstrip("/") + "/" if folder_name else ""
            blob_service_client = BlobServiceClient.from_connection_string(connection_string)
            container_client = blob_service_client.get_container_client(container_name)

            if not container_client.exists():
                msg = f"Container '{container_name}' does not exist."
                logger.error(msg)
                return msg

            output_sections = []
            missing_files = []
            failed_files = []
            file_count = 0
            seen = set()

            for file_name in file_names:
                blob_path = self._resolve_blob_path(prefix, file_name)

                if blob_path in seen:
                    continue
                seen.add(blob_path)

                blob_client = container_client.get_blob_client(blob_path)

                try:
                    if not blob_client.exists():
                        logger.info(f"Requested file not found: '{blob_path}'")
                        missing_files.append(blob_path)
                        section = f"===== FILE: {blob_path} =====\n[File not found in folder]\n"
                        output_sections.append(section)
                        print(section)
                        continue

                    downloaded = blob_client.download_blob().readall()
                except Exception as e:
                    logger.error(f"Error downloading '{blob_path}': {str(e)}", exc_info=True)
                    failed_files.append(blob_path)
                    section = f"===== FILE: {blob_path} =====\n[Error reading this file]\n"
                    output_sections.append(section)
                    print(section)
                    continue

                try:
                    text = downloaded.decode("utf-8")
                except UnicodeDecodeError:
                    text = f"[Binary content, {len(downloaded)} bytes — not displayed as text]"

                file_count += 1
                section = f"===== FILE: {blob_path} =====\n{text}\n"
                output_sections.append(section)
                print(section)

            if file_count == 0:
                msg = f"None of the requested files were readable in folder '{folder_name}'. Requested: {', '.join(file_names)}."
                logger.info(msg)
                print(msg)
                return msg

            header = f"Read {file_count} of {len(seen)} requested file(s) from folder '{folder_name}':\n\n"
            footer = ""
            if missing_files:
                footer += f"\nFiles not found: {', '.join(missing_files)}"
            if failed_files:
                footer += f"\nFiles that failed to download: {', '.join(failed_files)}"

            return header + "\n".join(output_sections) + footer

        except Exception as e:
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while reading the folder"

    def _run(self, folder_name: str, file_names: List[str]) -> str:
        """
        Run method required by CrewAI BaseTool.
        """
        return self.read_files_in_folder(folder_name, file_names)