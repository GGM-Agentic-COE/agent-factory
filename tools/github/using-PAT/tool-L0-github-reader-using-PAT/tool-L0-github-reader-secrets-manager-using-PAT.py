"""
GitHub File Reader Tool for CrewAI

This module implements a custom CrewAI tool that provides recursive file reading
capabilities from GitHub repositories using the GitHub REST API v3. It allows
authenticated access to repository contents and returns file data in a structured format.

Credentials:
    The GitHub Personal Access Token is retrieved from AWS Secrets Manager at
    import time (see AWSSecretReaderPodIdentity below) and never stored in this file.

Dependencies:
    - requests: HTTP library for GitHub API calls
    - pydantic: Data validation using Python type annotations
    - crewai: Framework for building AI agent tools
    - urllib.parse: URL encoding for API paths
    - base64: Decoding GitHub API's base64-encoded file contents

Typical Usage:
    >>> from github_file_reader import GithubReader
    >>> tool = GithubReader()
    >>> result = tool._run(
    ...     folder_location="src/components",
    ...     repo="my-repo",
    ...     branch="main"
    ... )
    >>> print(result["files"])
"""

import requests
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from urllib.parse import quote
import base64


import json
import boto3
from botocore.exceptions import ClientError
from typing import Dict


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
    SECRET_NAME: str = "aava-secret-manager-github-credentials"


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
GITHUB_TOKEN = secrets.get("github_token")


def _fetch_github_repo_owner(token: str) -> str:
    """
    Fetch the authenticated GitHub user's login name using the provided token.

    This function makes an authenticated request to the GitHub API's /user endpoint
    to retrieve the username associated with the provided Personal Access Token.
    This is necessary because the tool needs to construct repository URLs in the
    format "owner/repo", but only receives the repo name from the user.

    Args:
        token (str): GitHub Personal Access Token with appropriate scopes.
                    At minimum, requires 'repo' scope for private repositories
                    or 'public_repo' scope for public repositories only.

    Returns:
        str: The GitHub username (login) associated with the token.
            Example: "varun-ascendion" or "octocat"

    Raises:
        requests.exceptions.HTTPError: If the API request fails (e.g., invalid token,
                                      network issues, rate limiting)
        requests.exceptions.Timeout: If the request exceeds 30 seconds
        KeyError: If the API response doesn't contain the expected 'login' field

    API Reference:
        https://docs.github.com/en/rest/users/users#get-the-authenticated-user

    Example:
        >>> token = "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        >>> owner = _fetch_github_repo_owner(token)
        >>> print(owner)
        'varun-ascendion'
    """
    # Construct headers for GitHub API v3 authentication
    # Authorization: Bearer format is preferred over the older "token" format
    # Accept header ensures we receive the v3 REST API response format
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",  # GitHub API v3 media type
    }

    # Make GET request to the authenticated user endpoint
    # Timeout prevents indefinite hanging on network issues
    resp = requests.get("https://api.github.com/user", headers=headers, timeout=30)

    # Raise an exception for 4xx/5xx status codes
    # Common failures: 401 (bad token), 403 (insufficient scopes), 404 (token revoked)
    resp.raise_for_status()

    # Parse JSON response body
    user = resp.json()

    # Extract and return the 'login' field (username)
    # Returns None if 'login' key doesn't exist (graceful degradation)
    return user.get("login")


class GithubReaderSchema(BaseModel):
    """
    Pydantic input schema for the GithubReader tool.

    This schema defines and validates the three required parameters for reading
    files from a GitHub repository. Pydantic provides automatic validation,
    serialization, and documentation generation. The Field() descriptors are
    used by CrewAI agents to understand how to invoke the tool correctly.

    Attributes:
        folder_location (str): Path to the folder within the repository to read
                              recursively. Should not include leading/trailing slashes
                              as they are normalized by the tool.
                              Examples:
                                - "src" → reads all files under /src/
                                - "docs/api" → reads all files under /docs/api/
                                - "." or "" → reads entire repository (root level)

        repo (str): Repository name WITHOUT the owner prefix. The owner is automatically
                   determined by querying the authenticated user endpoint using the token.
                   Examples:
                     - "scib_demo" (not "varun-ascendion/scib_demo")
                     - "my-project-repo"
                     - "CrewAI-Tools"

        branch (str): Git branch name to read files from. Can be:
                     - Standard branch names: "main", "master", "develop"
                     - Feature branches: "feature/SCRUM-11691", "bugfix/issue-123"
                     - Tag names: "v1.0.0", "release-2.3"
                     Note: Must match exact branch name (case-sensitive)

    Validation:
        - All fields are required (Pydantic Field with ... as default)
        - All fields must be strings
        - Additional validation happens in GithubReader._run() method

    Usage by CrewAI Agents:
        Agents use the Field descriptions to understand parameter semantics
        and generate appropriate values when invoking the tool autonomously.
    """

    folder_location: str = Field(
        ...,  # Required field (ellipsis means no default value)
        description="Repository folder path to read recursively. Specify the exact folder path within the repository that you want to read all files from. Example: 'lld' for root level folder or 'project_k/lld' for nested folder structure.",
    )
    repo: str = Field(
        ...,  # Required field
        description="Repository name without owner prefix. This should be the exact name of the GitHub repository you want to access. Example: 'scib_demo' or 'my-project-repo'.",
    )
    branch: str = Field(
        ...,  # Required field
        description="Branch name to read files from. Specify the exact branch name where the files are located. Example: 'main', 'develop', or 'feature/SCRUM-11691'.",
    )


class GithubReader(BaseTool):
    """
    CrewAI tool for recursively reading all files from a GitHub repository folder.

    This tool extends CrewAI's BaseTool to provide agents with the ability to
    read and retrieve file contents from GitHub repositories. It uses the GitHub
    REST API v3 to authenticate, navigate repository structures, and download
    file contents. All files are decoded from base64 and returned as UTF-8 text.

    The tool performs the following operations:
    1. Validates input parameters
    2. Authenticates with GitHub and resolves repository owner
    3. Verifies repository and branch existence
    4. Retrieves the complete file tree for the branch
    5. Filters files under the specified folder
    6. Downloads and decodes each file's content
    7. Returns structured results with status indicators

    Class Attributes:
        name (str): Human-readable tool name displayed to agents
        description (str): Natural language description of tool capabilities,
                          used by agents to decide when to invoke this tool
        args_schema (Type[BaseModel]): Pydantic schema for input validation

    Methods:
        _run(folder_location, repo, branch): Main execution method (see below)

    Rate Limiting:
        GitHub API has rate limits:
        - Authenticated: 5,000 requests/hour
        - Unauthenticated: 60 requests/hour
        This tool uses authentication, but be aware of limits when processing
        large repositories or running in tight loops.

    API Endpoints Used:
        1. GET /user - Fetch authenticated user
        2. GET /repos/{owner}/{repo} - Verify repository exists
        3. GET /repos/{owner}/{repo}/contents/{path} - Check folder exists
        4. GET /repos/{owner}/{repo}/branches/{branch} - Get tree SHA
        5. GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1 - Get file tree
        6. GET /repos/{owner}/{repo}/contents/{path} - Download each file

    Example Output Structure:
        {
            "repository": "varun-ascendion/scib_demo",
            "branch": "main",
            "folder_location": "src/components",
            "files": {
                "src/components/Header.tsx": {
                    "status": "success",
                    "content": "import React from 'react'...",
                    "size": 1234,
                    "sha": "abc123..."
                },
                "src/components/image.png": {
                    "status": "binary_or_non_utf8",
                    "message": "File is not UTF-8 text; content not decoded.",
                    "size": 5678,
                    "sha": "def456..."
                }
            }
        }
    """

    # Tool metadata for CrewAI agent discovery and invocation
    name: str = "GitHub Reader"
    description: str = (
        "Tool to read all files from a folder in a GitHub repository. "
        "Accepts only folder location input and returns file contents recursively."
    )
    args_schema: Type[BaseModel] = GithubReaderSchema

    def _run(self, folder_location: str, repo: str, branch: str) -> Any:
        """
        Execute the GitHub file reading operation.

        This method orchestrates the complete workflow of authenticating with GitHub,
        navigating to the specified folder, retrieving all file contents recursively,
        and returning them in a structured format. It handles various edge cases
        including missing folders, binary files, and API errors.

        Workflow:
            1. Input Validation: Ensure folder_location is a non-empty string
            2. Authentication: Use token to fetch repository owner
            3. Repository Verification: Confirm repo exists and is accessible
            4. Folder Verification: Check that the target folder exists in the branch
            5. Tree Retrieval: Get complete recursive file tree from branch
            6. File Filtering: Identify all files under the target folder
            7. Content Download: Fetch and decode each file's content
            8. Result Aggregation: Build structured response dictionary

        Args:
            folder_location (str): Repository folder path (e.g., "src/components", "docs")
                                  Leading/trailing slashes are automatically stripped
            repo (str): Repository name without owner (e.g., "scib_demo")
            branch (str): Branch name (e.g., "main", "feature/xyz")

        Returns:
            dict | str: On success, returns a dictionary with structure:
                {
                    "repository": str,        # "owner/repo" format
                    "branch": str,            # Branch name
                    "folder_location": str,   # Normalized folder path
                    "files": dict,            # Per-file results (see below)
                    "message": str (optional) # Present if no files found
                }

                Each file in "files" dict has one of these structures:

                SUCCESS:
                {
                    "status": "success",
                    "content": str,     # Decoded UTF-8 text
                    "size": int,        # Bytes
                    "sha": str          # Git blob SHA
                }

                BINARY/NON-UTF8:
                {
                    "status": "binary_or_non_utf8",
                    "message": str,
                    "size": int,
                    "sha": str
                }

                NOT FOUND:
                {
                    "status": "not_found",
                    "message": str
                }

                ERROR:
                {
                    "status": "error",
                    "message": str
                }

                On error, returns a string error message instead of dict.

        Raises:
            Does not raise exceptions directly; all errors are caught and returned
            as formatted error strings to ensure CrewAI agents receive actionable
            error messages.

        Error Handling:
            - Network errors: Captured with response status/text
            - API errors: HTTP status codes translated to messages
            - Decode errors: Binary files flagged with special status
            - Missing resources: 404s return descriptive error messages

        Performance Considerations:
            - Uses recursive tree API to minimize requests (1 call for entire tree)
            - Downloads files individually (unavoidable with Contents API)
            - Large folders may hit rate limits or take significant time
            - Consider pagination for repositories with >1000 files

        Example Success:
            >>> tool = GithubReader()
            >>> result = tool._run("src", "my-repo", "main")
            >>> print(result["files"]["src/app.py"]["content"])
            'import os\\nfrom flask import Flask...'

        Example Error:
            >>> result = tool._run("nonexistent", "my-repo", "main")
            >>> print(result)
            "Error reading scripts: Folder 'nonexistent' not found in branch 'main'."
        """
        try:
            # ═══════════════════════════════════════════════════════════════════
            # PHASE 1: INPUT VALIDATION
            # ═══════════════════════════════════════════════════════════════════

            # Validate that folder_location is a non-empty string
            # Pydantic ensures it's a string, but it could be empty or whitespace-only
            if not isinstance(folder_location, str) or not folder_location.strip():
                return "Error reading scripts: 'folder_location' must be a non-empty string."

            # Normalize folder_location by removing leading/trailing whitespace and slashes
            # This ensures consistent path matching regardless of user input format
            # Examples: " src/ " → "src", "/docs/api/" → "docs/api"
            folder_location = folder_location.strip().strip("/")

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 2: AUTHENTICATION AND REPOSITORY OWNER RESOLUTION
            # ═══════════════════════════════════════════════════════════════════

            # Token retrieved from AWS Secrets Manager at import time
            token = GITHUB_TOKEN

            # Fetch the repository owner's username using the token
            # This is necessary because we only have the repo name, not the full "owner/repo"
            repo_owner = _fetch_github_repo_owner(token)

            # Construct standard headers for all subsequent GitHub API requests
            # Authorization: Bearer token for authentication
            # Accept: Ensures we get GitHub API v3 response format
            # Content-Type: JSON format for request/response bodies
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github+json",
                "Content-Type": "application/json",
            }

            # Construct the base API URL for this repository
            # Format: https://api.github.com/repos/{owner}/{repo}
            # All subsequent API calls will use this as a prefix
            base_url = f"https://api.github.com/repos/{repo_owner}/{repo}"

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 3: REPOSITORY EXISTENCE VERIFICATION
            # ═══════════════════════════════════════════════════════════════════

            # Verify that the repository exists and is accessible with this token
            # GET /repos/{owner}/{repo} returns repo metadata if accessible
            repo_check = requests.get(base_url, headers=headers)

            # Check for 404 Not Found specifically (repo doesn't exist or is inaccessible)
            if repo_check.status_code == 404:
                return f"Error: Repository '{repo_owner}/{repo}' not found."

            # Raise exception for any other error status (403 Forbidden, 500 Server Error, etc.)
            repo_check.raise_for_status()

            # Initialize dictionary to store all file contents
            # Key: file path relative to repo root
            # Value: dict with status, content, size, sha, and/or error messages
            file_contents = {}

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 4: FOLDER EXISTENCE VERIFICATION
            # ═══════════════════════════════════════════════════════════════════

            # URL-encode the folder path to handle special characters
            # safe="/" preserves forward slashes (path separators)
            # Example: "project k/docs" → "project%20k/docs"
            encoded_folder = quote(folder_location, safe="/")

            # Construct API URL to check if folder exists
            # GET /repos/{owner}/{repo}/contents/{path} returns folder contents
            folder_api_url = f"{base_url}/contents/{encoded_folder}"

            # Query the folder with branch specification
            # ?ref={branch} parameter ensures we're checking the correct branch
            folder_response = requests.get(folder_api_url, headers=headers, params={"ref": branch})

            # If folder doesn't exist in this branch, return early with error message
            if folder_response.status_code == 404:
                return (
                    f"Error reading scripts: Folder '{folder_location}' not found "
                    f"in branch '{branch}'."
                )

            # Raise exception for other errors (permissions, API issues, etc.)
            folder_response.raise_for_status()

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 5: BRANCH AND TREE SHA RESOLUTION
            # ═══════════════════════════════════════════════════════════════════

            # To efficiently get all files recursively, we use the Git Tree API
            # First, we need the "tree SHA" for the branch's current commit

            # Construct API URL for branch details
            # GET /repos/{owner}/{repo}/branches/{branch} returns branch metadata
            # quote(branch, safe='') encodes the entire branch name (including slashes)
            branch_api_url = f"{base_url}/branches/{quote(branch, safe='')}"

            # Fetch branch metadata
            branch_response = requests.get(branch_api_url, headers=headers)
            branch_response.raise_for_status()
            branch_data = branch_response.json()

            # Navigate the nested JSON structure to extract the tree SHA
            # Path: response → commit → commit → tree → sha
            # This SHA represents the root tree object of the branch's HEAD commit
            # Tree objects in Git contain references to all files and subdirectories
            tree_sha = branch_data.get("commit", {}).get("commit", {}).get("tree", {}).get("sha")

            # If we couldn't extract the tree SHA, the response structure is unexpected
            if not tree_sha:
                return "Error reading scripts: Unable to resolve tree SHA for branch."

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 6: RECURSIVE TREE RETRIEVAL
            # ═══════════════════════════════════════════════════════════════════

            # Now use the Git Tree API to get ALL files in the repository recursively
            # This is much more efficient than navigating folder-by-folder via Contents API
            # GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1
            tree_url = f"{base_url}/git/trees/{tree_sha}"

            # The ?recursive=1 parameter is crucial: it returns entire tree in one response
            # Without it, we'd only get the top-level directory
            tree_response = requests.get(tree_url, headers=headers, params={"recursive": "1"})
            tree_response.raise_for_status()
            tree_data = tree_response.json()

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 7: FILE FILTERING
            # ═══════════════════════════════════════════════════════════════════

            # Construct the path prefix to filter files under our target folder
            # Example: if folder_location is "src", prefix is "src/"
            # This ensures we only match "src/app.py", not "source/app.py"
            prefix = f"{folder_location}/"

            # Filter the tree to only include files (blobs) under our target folder
            # tree_data["tree"] is a list of tree items, each with:
            #   - path: file/folder path relative to repo root
            #   - type: "blob" (file), "tree" (directory), or "commit" (submodule)
            #   - sha: Git object SHA
            #   - size: file size in bytes (for blobs)
            target_files = [
                item
                for item in tree_data.get("tree", [])
                # Only include files (blobs), not directories (trees) or submodules (commits)
                if item.get("type") == "blob" and item.get("path", "").startswith(prefix)
            ]

            # If no files found under the target folder, return early with informational message
            if not target_files:
                return {
                    "repository": f"{repo_owner}/{repo}",
                    "branch": branch,
                    "folder_location": folder_location,
                    "files": {},
                    "message": f"No files found under folder '{folder_location}'.",
                }

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 8: FILE CONTENT RETRIEVAL AND DECODING
            # ═══════════════════════════════════════════════════════════════════

            # Iterate through each file and download its content
            # This is the most time-consuming phase as it makes one API call per file
            for item in target_files:
                # Extract the file path from the tree item
                file_path = item.get("path")

                # Skip if path is missing (shouldn't happen, but defensive programming)
                if not file_path:
                    continue

                # URL-encode the file path to handle spaces and special characters
                # Example: "docs/API Reference.md" → "docs/API%20Reference.md"
                encoded_path = quote(file_path, safe="/")

                # Construct the Contents API URL for this specific file
                # GET /repos/{owner}/{repo}/contents/{path}?ref={branch}
                api_url = f"{base_url}/contents/{encoded_path}"

                # Fetch the file metadata and content
                # ?ref={branch} ensures we get content from the correct branch
                response = requests.get(api_url, headers=headers, params={"ref": branch})

                # Handle case where file was in tree but is now missing (race condition)
                # This can happen if the file was deleted between tree fetch and content fetch
                if response.status_code == 404:
                    file_contents[file_path] = {
                        "status": "not_found",
                        "message": f"File '{file_path}' not found in branch '{branch}'.",
                    }
                    continue

                # Raise exception for other HTTP errors
                response.raise_for_status()

                # Parse the JSON response
                data = response.json()

                # GitHub Contents API returns files with:
                #   - type: "file" for regular files
                #   - content: base64-encoded file content
                #   - size: file size in bytes
                #   - sha: Git blob SHA
                if data.get("type") == "file" and "content" in data:
                    try:
                        # GitHub API returns file content as base64-encoded string
                        # Decode base64, then decode the resulting bytes as UTF-8 text
                        decoded_content = base64.b64decode(data["content"]).decode("utf-8")

                        # Store successfully decoded file content
                        file_contents[file_path] = {
                            "status": "success",
                            "content": decoded_content,  # Actual file text
                            "size": data.get("size"),    # File size in bytes
                            "sha": data.get("sha"),      # Git blob SHA (for version tracking)
                        }

                    except UnicodeDecodeError:
                        # File is binary (image, PDF, compiled code, etc.) or uses non-UTF-8 encoding
                        # Cannot represent as text, so return metadata only with special status
                        file_contents[file_path] = {
                            "status": "binary_or_non_utf8",
                            "message": "File is not UTF-8 text; content not decoded.",
                            "size": data.get("size"),
                            "sha": data.get("sha"),
                        }

                    except Exception as e:
                        # Catch any other decoding errors (corrupted base64, etc.)
                        file_contents[file_path] = {
                            "status": "error",
                            "message": f"Failed to decode file content: {str(e)}",
                        }

                else:
                    # Unexpected response type (e.g., symlink, submodule)
                    # GitHub Contents API can return other types besides "file"
                    file_contents[file_path] = {
                        "status": "error",
                        "message": f"Unsupported type: {data.get('type')}",
                    }

            # ═══════════════════════════════════════════════════════════════════
            # PHASE 9: RESULT AGGREGATION AND RETURN
            # ═══════════════════════════════════════════════════════════════════

            # Return structured result dictionary with all file contents
            return {
                "repository": f"{repo_owner}/{repo}",  # Full repository identifier
                "branch": branch,                       # Branch that was read
                "folder_location": folder_location,     # Normalized folder path
                "files": file_contents,                 # Dictionary of all file results
            }

        except requests.exceptions.RequestException as e:
            # Handle all HTTP/network-related errors from the requests library
            # This includes: ConnectionError, Timeout, HTTPError, etc.

            # Initialize empty response text
            response_text = ""

            # If the exception has an attached response object, include its details
            # This provides debugging information about what GitHub returned
            if getattr(e, "response", None) is not None:
                response_text = f" | GitHub response: {e.response.status_code} {e.response.text}"

            # Return formatted error message combining exception and response details
            return f"Error reading scripts: {str(e)}{response_text}"

        except Exception as e:
            # Catch-all for any other unexpected errors (JSON parsing, type errors, etc.)
            # This ensures the tool always returns a string message, never raises
            return f"Error reading scripts: {str(e)}"
