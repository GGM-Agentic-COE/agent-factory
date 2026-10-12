# RUN THE SECRETS MANAGER CODE HERE FROM OTHER TOOLS, IF NEEDS TO CONNECT WITH SECRETS MANAGER

## ADJUST THESE CREDENTIALS WHEN NEEDED ______________________________________________________________________
# Create the BlobServiceClient
connection_string = "REDACTED-SECRET-KEY"

# Use only the predefined container name
container_name = "aava-ggm"

from crewai.tools import BaseTool
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from pydantic import BaseModel, Field, field_validator
from typing import List
import logging
import json
import re
import os


# Define the args schema for your tool
class AzureBlobReaderSchema(BaseModel):
    folder_name: str = Field(..., description="Name of the folder in Azure Blob Storage that contains the files")
    file_names: List[str] = Field(
        ...,
        description=(
            "List of file names inside the folder to read, e.g. [\"file-1.md\", \"file-2.md\"]. "
            "Only these files are read; all other files in the folder are ignored."
        ),
    )

    @field_validator("file_names", mode="before")
    @classmethod
    def coerce_file_names(cls, value):
        """
        Agents often hand over the list as a JSON string or a comma-separated
        string instead of a real list. Normalize all of those into List[str].
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


# Set up secure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='azure_blob_operations.log'
)
logger = logging.getLogger('AzureBlobReaderTool')


class AzureBlobReaderTool(BaseTool):
    name: str = "Azure Blob Reader Tool"
    description: str = (
        "Reads and prints the contents of specific named files inside a folder in Azure Blob Storage. "
        "Requires a folder name and the list of file names to read."
    )
    args_schema: type[BaseModel] = AzureBlobReaderSchema

    def __init__(self):
        super().__init__(
            name="Azure Blob Reader Tool",
            description=(
                "Reads and prints the contents of specific named files inside a folder in Azure Blob Storage. "
                "Requires a folder name and the list of file names to read."
            )
        )

    @staticmethod
    def _resolve_blob_path(prefix, file_name):
        """
        Build the full blob path for a requested file name.

        Tolerates the caller passing either a bare file name ("file-1.md") or a
        path that already includes the folder ("my_folder/file-1.md").

        :param prefix: string, normalized folder prefix ending in "/" (or "").
        :param file_name: string, the requested file name.
        Returns:
            str: the full blob path inside the container.
        """
        cleaned = file_name.strip().lstrip("/")

        if prefix and cleaned.startswith(prefix):
            return cleaned

        return f"{prefix}{cleaned}"

    def read_files_in_folder(self, folder_name, file_names):
        """
        Downloads only the named files under the given folder prefix and
        returns (and prints) their contents.

        :param folder_name: string, name of the folder to read from.
        :param file_names: list of strings, the file names to read.
        Returns:
            str: A formatted dump of each requested file's name and content,
                 or an error message.
        """
        try:
            # Normalize the arguments coming in from an agent or a direct call.
            validated = AzureBlobReaderSchema(folder_name=folder_name, file_names=file_names)
            folder_name = validated.folder_name
            file_names = validated.file_names

            if not file_names:
                msg = "No file names were provided. Provide at least one file name to read."
                logger.info(msg)
                print(msg)
                return msg

            # Normalize the prefix so it always ends in exactly one slash.
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

                # Skip duplicates so the same file is never downloaded twice.
                if blob_path in seen:
                    continue
                seen.add(blob_path)

                blob_client = container_client.get_blob_client(blob_path)

                # Fetch only this file — no listing of the whole folder.
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

                # Try to decode as UTF-8 text; fall back to a note for binary content.
                try:
                    text = downloaded.decode("utf-8")
                except UnicodeDecodeError:
                    text = f"[Binary content, {len(downloaded)} bytes — not displayed as text]"

                file_count += 1
                section = f"===== FILE: {blob_path} =====\n{text}\n"
                output_sections.append(section)
                print(section)

            if file_count == 0:
                msg = (
                    f"None of the requested files were readable in folder '{folder_name}'. "
                    f"Requested: {', '.join(file_names)}."
                )
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
            # Log the full error details but return a generic message.
            logger.error(f"An error occurred: {str(e)}", exc_info=True)
            return "An error occurred while reading the folder"

    def _run(self, folder_name, file_names):
        """
        Run method required by CrewAI BaseTool.

        Args:
            folder_name (str): Name of the folder to read from.
            file_names (list[str]): The specific file names to read from that folder.

        Returns:
            str: The contents of the requested files.
        """
        return self.read_files_in_folder(folder_name, file_names)