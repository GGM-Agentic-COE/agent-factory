import boto3
from datetime import datetime, timezone
from typing import Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from botocore.exceptions import ClientError


class S3UploadSchema(BaseModel):
    """Input schema for S3UploadTool."""
    folder_name: str = Field(
        ...,
        description="Name of the folder (prefix) in the S3 bucket to upload into, e.g. the workflow execution id.",
    )
    file_name: str = Field(
        ..., description="Exact name of the file to create, e.g. 'summary.md'."
    )
    contents: str = Field(
        ..., description="Text content to write into the file."
    )


class S3UploadTool(BaseTool):
    """
    S3UploadTool - Uploads text content to a fixed S3 bucket under a
    caller-specified folder, using the exact file name provided.
    Authentication is via Pod Identity; no credentials are passed in code.
    """
    name: str = "S3 Upload Tool"
    description: str = (
        "Uploads text content to the configured S3 bucket. Inputs are the "
        "folder name, the file name, and the contents to write. The file is "
        "stored under the exact name given. "
        "The pod is configured with pod identity for authentication."
    )
    args_schema: Type[BaseModel] = S3UploadSchema

    # SETUP-REQUIRED: set to your organization's S3 bucket name
    BUCKET_NAME: str = "<your-s3-bucket-name>"
    # SETUP-REQUIRED: set to the AWS region that bucket lives in
    AWS_REGION: str = "us-east-1"

    MAX_FILE_BYTES: int = 1_000_000  # reject anything larger

    def _run(self, folder_name: str, file_name: str, contents: str) -> dict:
        try:
            s3 = boto3.client("s3", region_name=self.AWS_REGION)
        except Exception as e:
            return {"status": "FAILED", "reason": f"S3_CLIENT_INIT_FAILED: {e}"}

        prefix = folder_name.strip("/") + "/"
        safe_name = file_name.strip("/").split("/")[-1]
        if not safe_name:
            return {"status": "FAILED", "reason": "INVALID_FILE_NAME"}

        body = contents.encode("utf-8")
        if len(body) > self.MAX_FILE_BYTES:
            return {
                "status": "FAILED",
                "reason": f"FILE_TOO_LARGE: {len(body)} bytes exceeds limit of {self.MAX_FILE_BYTES}",
            }

        object_key = f"{prefix}{safe_name}"

        try:
            s3.put_object(
                Bucket=self.BUCKET_NAME,
                Key=object_key,
                Body=body,
                ContentType="text/plain; charset=utf-8",
            )
        except ClientError as e:
            code = e.response["Error"]["Code"]
            message = e.response["Error"]["Message"]
            return {"status": "FAILED", "reason": f"S3_UPLOAD_FAILED ({code}): {message}"}
        except Exception as e:
            return {"status": "FAILED", "reason": f"S3_UPLOAD_FAILED: {e}"}

        return {
            "status": "SUCCESS",
            "bucket": self.BUCKET_NAME,
            "key": object_key,
            "file_name": safe_name,
            "folder": prefix,
            "size_bytes": len(body),
            "uploaded_at": datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S"),
        }