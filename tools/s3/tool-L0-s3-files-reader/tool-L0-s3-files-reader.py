import boto3
from typing import Type, List
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from botocore.exceptions import ClientError


class S3SpecificFileReaderSchema(BaseModel):
    """Input schema for S3SpecificFileReader."""
    folder_name: str = Field(
        ...,
        description="Name of the folder (prefix) in the S3 bucket, e.g. the workflow execution id.",
    )
    file_names: List[str] = Field(
        ...,
        description="List of file names to read from that folder, e.g. ['summary.md', 'findings.md'].",
    )


class S3SpecificFileReader(BaseTool):
    """
    S3SpecificFileReader - Reads the contents of one or more named files
    inside a given folder (prefix) of a fixed S3 bucket.
    Authentication is via Pod Identity; no credentials are passed in code.
    """
    name: str = "S3 Specific File Reader"
    description: str = (
        "Reads one or more specific files from a given folder of the configured "
        "S3 bucket and returns their contents. Inputs are the folder name and a "
        "list of file names. The pod is configured with pod identity for authentication."
    )
    args_schema: Type[BaseModel] = S3SpecificFileReaderSchema

    # SETUP-REQUIRED: set to your organization's S3 bucket name
    BUCKET_NAME: str = "aava-dev-agent-artifacts"
    # SETUP-REQUIRED: set to the AWS region that bucket lives in
    AWS_REGION: str = "us-east-1"

    MAX_FILE_BYTES: int = 1_000_000  # skip anything larger

    def _run(self, folder_name: str, file_names: List[str]) -> str:
        if not file_names:
            return "S3_RETRIEVE_FAILED: No file names provided"

        try:
            s3 = boto3.client("s3", region_name=self.AWS_REGION)
        except Exception as e:
            return f"S3_CLIENT_INIT_FAILED: {e}"

        prefix = folder_name.strip("/") + "/"

        parts = [
            "FILE_SOURCE: S3",
            f"BUCKET: {self.BUCKET_NAME}",
            f"FOLDER: {prefix}",
            f"FILE_COUNT: {len(file_names)}",
            "",
        ]

        found = 0
        for name in file_names:
            safe_name = name.strip("/").split("/")[-1]
            if not safe_name:
                parts.append(f"===== FILE: {name} =====\n[INVALID_FILE_NAME]\n")
                continue

            key = f"{prefix}{safe_name}"

            try:
                meta = s3.head_object(Bucket=self.BUCKET_NAME, Key=key)
            except ClientError as e:
                code = e.response["Error"]["Code"]
                if code in ("404", "NoSuchKey"):
                    parts.append(f"===== FILE: {key} =====\n[NOT_FOUND]\n")
                else:
                    parts.append(f"===== FILE: {key} =====\n[READ_FAILED: {code}]\n")
                continue
            except Exception as e:
                parts.append(f"===== FILE: {key} =====\n[READ_FAILED: {e}]\n")
                continue

            size = meta["ContentLength"]
            header = (
                f"===== FILE: {key} =====\n"
                f"LAST_MODIFIED: {meta['LastModified']}\n"
                f"SIZE_BYTES: {size}\n"
            )

            if size > self.MAX_FILE_BYTES:
                body = "[SKIPPED: file exceeds size limit]"
            else:
                try:
                    body = self._get_object_content(s3, key)
                    found += 1
                except Exception as e:
                    body = f"[READ_FAILED: {e}]"

            parts.append(f"{header}\n{body}\n")

        if found == 0:
            return f"S3_RETRIEVE_FAILED: None of the requested files could be read under '{prefix}'"

        return "\n".join(parts)

    def _get_object_content(self, s3, key: str) -> str:
        response = s3.get_object(Bucket=self.BUCKET_NAME, Key=key)
        raw = response["Body"].read()
        try:
            return raw.decode("utf-8")
        except UnicodeDecodeError:
            return f"[BINARY OR NON-UTF8 CONTENT: {len(raw)} bytes]"
 