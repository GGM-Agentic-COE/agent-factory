import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import boto3
from botocore.exceptions import ClientError

class AWSSecretReaderPodIdentitySchema(BaseModel):
    """Input schema for AWSSecretReaderPodIdentity."""
    secret_name: str = Field(..., description="The name of the AWS Secret to retrieve. This should be the full secret name as stored in AWS Secrets Manager.")

class AWSSecretReaderPodIdentity(BaseTool):
    """
    AWSSecretReaderPodIdentity - A tool to read AWS Secrets using Pod Identity and return all key-value pairs in a tabular format.
    """
    name: str = "AWS Secret Reader with Pod Identity"
    description: str = "Reads an AWS Secret using Pod Identity and lists all keys and values in a tabular format."
    args_schema: Type[BaseModel] = AWSSecretReaderPodIdentitySchema

    def _run(self, secret_name: str) -> str:
        try:
            # Use the default boto3 session (Pod Identity assumed to be configured)
            client = boto3.client('secretsmanager',region_name='us-east-2')
            get_secret_value_response = client.get_secret_value(SecretId=secret_name)
            secret_string = get_secret_value_response.get('SecretString', '{}')
            import json
            secret_dict = json.loads(secret_string)
            if not isinstance(secret_dict, dict):
                return f"Secret value is not a JSON object: {secret_dict}"
            # Prepare tabular output
            table = "| Key | Value |\n|-----|-------|\n"
            for k, v in secret_dict.items():
                table += f"| {k} | {v} |\n"
            return table
        except ClientError as e:
            return f"Error retrieving secret: {str(e)}"
        except Exception as ex:
            return f"Unexpected error: {str(ex)}"