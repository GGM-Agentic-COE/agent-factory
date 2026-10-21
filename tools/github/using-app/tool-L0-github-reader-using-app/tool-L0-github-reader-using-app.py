import base64
import os
import threading
import time
from typing import Any, Dict, Optional, Tuple, Type
from urllib.parse import quote

import jwt  # PyJWT -- install with the [crypto] extra for RS256 support
import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


import json
import boto3
from botocore.exceptions import ClientError


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
    SECRET_NAME: str = "<name-of-secret-in-aws-secrets-manager>"

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

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

GITHUB_API = "https://api.github.com"

# ═════════════════════════════════════════════════════════════════════════════
#  GITHUB APP CREDENTIALS (from AWS Secrets Manager)
# ═════════════════════════════════════════════════════════════════════════════
#
# Only ONE of APP_ID / CLIENT_ID is needed -- both work as the JWT issuer, and
# CLIENT_ID takes precedence when both are set.
#
# The client SECRET is deliberately absent. It is only used for OAuth
# user-authorization, which this tool does not do.

# App ID -- the numeric id from Settings -> Developer settings -> GitHub Apps
APP_ID = secrets.get("app_id")                       # from AWS Secrets Manager

# Client ID -- the "Iv23li..." string on the same page. GitHub's currently
# recommended issuer value.
CLIENT_ID = secrets.get("client_id")                 # from AWS Secrets Manager

# Private key (PEM), either PKCS#1 ("BEGIN RSA PRIVATE KEY") or PKCS#8
# ("BEGIN PRIVATE KEY") -- both are accepted.
PRIVATE_KEY = secrets.get("private_key")             # from AWS Secrets Manager

# ⚠️  A leaked App private key is strictly worse than a leaked PAT: it cannot
#     be scoped down after the fact, and it grants access to every account
#     that installed the App. Keeping it in Secrets Manager rather than in
#     code is what prevents that.


# ═════════════════════════════════════════════════════════════════════════════

# JWT lifetime. GitHub rejects `exp` more than 600s in the future. We also
# backdate `iat` by 60s (see _generate_app_jwt) to absorb the case where this
# host's clock runs AHEAD of GitHub's -- an `iat` in GitHub's future is
# rejected outright, and clock drift is the most common cause of a spurious
# 401 "'Expiration' claim ('exp') must be a numeric value representing the
# future time".
#
# 480 is deliberate, not arbitrary: with the 60s backdating, exp - iat = 540s,
# which stays strictly under 600 on either reading of the cap (exp measured
# against GitHub's clock, or exp - iat as total lifetime). At 540 here,
# exp - iat would be exactly 600 and sit right on the boundary.
JWT_TTL_SECONDS = 480

# Re-sign the JWT this many seconds before it expires.
JWT_REFRESH_MARGIN = 60

# Refresh the installation token this many seconds before its stated expiry,
# so a long file loop can't have the token die mid-run.
TOKEN_REFRESH_MARGIN = 300  # 5 minutes

REQUEST_TIMEOUT = 30


def _load_private_key() -> str:
    """
    Return the App's RSA private key as a PEM string.

    The key is read from the `private_key` field of the secret.
    Both PKCS#1 ("BEGIN RSA PRIVATE KEY", what GitHub's download gives you)
    and PKCS#8 ("BEGIN PRIVATE KEY", what `openssl pkcs8 -topk8` produces)
    are accepted -- PyJWT handles either.

    Returns:
        str: PEM-encoded private key.

    Raises:
        RuntimeError: If no key is configured.
    """
    if PRIVATE_KEY:
        key = PRIVATE_KEY
        # Docker/K8s/CI env vars routinely carry the PEM with two-character
        # backslash-n sequences instead of real newlines. PEM parsing fails
        # cryptically on that, so normalise it here.
        if "\\n" in key and "\n" not in key:
            key = key.replace("\\n", "\n")
        return key


    raise RuntimeError(
        "No App private key configured. Set PRIVATE_KEY or PRIVATE_KEY_PATH "
        "at the top of this file, or the GITHUB_APP_PRIVATE_KEY / "
        "GITHUB_APP_PRIVATE_KEY_PATH environment variables."
    )



# ─────────────────────────────────────────────────────────────────────────────
# JWT CACHE
# ─────────────────────────────────────────────────────────────────────────────
#
# Without this, every /app/* request re-signs. The discovery path alone makes
# 3-4 such calls per run. Cached, a whole run costs one signature.

_jwt_cache: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_jwt_lock = threading.Lock()


def _generate_app_jwt() -> str:
    """
    Return a JWT authenticating as the GitHub App itself, signing only when
    the cached one is missing or near expiry.

    The `iss` claim may be the Client ID or the numeric App ID; GitHub accepts
    either and now recommends the Client ID, so that wins when both are set.

    Returns:
        str: RS256-signed JWT, valid for at least JWT_REFRESH_MARGIN seconds.

    Raises:
        RuntimeError: If no issuer identifier is configured.
    """
    with _jwt_lock:
        cached = _jwt_cache["token"]
        if cached and _jwt_cache["expires_at"] - JWT_REFRESH_MARGIN > time.time():
            return cached

        issuer = CLIENT_ID or APP_ID
        if not issuer:
            raise RuntimeError(
                "Set CLIENT_ID or APP_ID at the top of this file (or the "
                "GITHUB_APP_CLIENT_ID / GITHUB_APP_ID environment variables) "
                "to identify the App."
            )

        now = int(time.time())
        payload = {
            "iat": now - 60,               # backdated to absorb clock skew
            "exp": now + JWT_TTL_SECONDS,
            "iss": issuer,
        }
        token = jwt.encode(payload, _load_private_key(), algorithm="RS256")

        # PyJWT 1.x returned bytes; 2.x returns str. Normalise so the f-string
        # in _jwt_headers can't produce a literal "b'eyJ...'" Authorization
        # header, which fails with an opaque 401.
        if isinstance(token, bytes):
            token = token.decode("ascii")

        _jwt_cache["token"] = token
        _jwt_cache["expires_at"] = now + JWT_TTL_SECONDS
        return token


def _jwt_headers() -> Dict[str, str]:
    """Headers for App-level (JWT) endpoints: /app/*."""
    return {
        "Authorization": f"Bearer {_generate_app_jwt()}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def _token_headers(token: str) -> Dict[str, str]:
    """Headers for repo-level (installation token) endpoints."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# ─────────────────────────────────────────────────────────────────────────────
# INSTALLATION TOKEN MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
#
# An installation token lives 1 hour. Minting one per _run() is wasteful and
# noisy in the App's audit log, so we cache per installation ID. The lock
# matters because CrewAI may run tools concurrently across agents.

_token_cache: Dict[int, Tuple[str, float]] = {}   # installation_id -> (token, expires_at)
_cache_lock = threading.Lock()


def _list_installations() -> list:
    """
    List every account that has installed this App.

    Returns:
        list[dict]: Installation objects, each with `id` and
                    `account.login` (the owner name).

    API: GET /app/installations  (JWT auth)
    """
    resp = requests.get(
        f"{GITHUB_API}/app/installations",
        headers=_jwt_headers(),
        params={"per_page": 100},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _get_installation_token(installation_id: int) -> str:
    """
    Exchange the App JWT for an installation access token, with caching.

    Args:
        installation_id (int): Target installation.

    Returns:
        str: `ghs_...` token usable exactly like a PAT.

    API: POST /app/installations/{id}/access_tokens  (JWT auth)
    """
    with _cache_lock:
        cached = _token_cache.get(installation_id)
        if cached and cached[1] - TOKEN_REFRESH_MARGIN > time.time():
            return cached[0]

    resp = requests.post(
        f"{GITHUB_API}/app/installations/{installation_id}/access_tokens",
        headers=_jwt_headers(),
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()

    token = data["token"]
    # `expires_at` is ISO-8601 Zulu, e.g. "2026-07-27T12:34:56Z". Rather than
    # parse it, trust GitHub's documented 1-hour lifetime from now.
    with _cache_lock:
        _token_cache[installation_id] = (token, time.time() + 3600)
    return token


# Resolved owners are stable for the life of the process, so cache them and
# skip resolution entirely on subsequent runs.
_owner_cache: Dict[str, Tuple[str, int]] = {}   # repo (lowercased) -> (owner, installation_id)
_owner_lock = threading.Lock()


def _resolve_owner_and_token(repo: str) -> Tuple[str, str, str]:
    """
    Determine the owner of `repo` and return (owner, repo_name, token).

    An App installation has no authenticated human user, so the owner
    comes from the installation instead of a GET /user call.

    The key property that makes this work without a caller-supplied owner:
    an installation is scoped to exactly ONE account, and every repository it
    can access belongs to that account. Therefore
    `installation.account.login` IS the owner.

    Resolution:
      * "owner/repo" passed explicitly -- honoured directly, one API call.
      * 1 installation (the overwhelmingly common case) -- the owner is that
        installation's account login. One API call, no repo-list scan.
      * N installations -- scan each installation's accessible repositories
        for a name match. Ambiguity across accounts is reported rather than
        silently guessed.

    Args:
        repo (str): Repository name, either bare ("<your-repo-name>") or fully
                    qualified ("<your-github-org>/<your-repo-name>").

    Returns:
        tuple[str, str, str]: (owner_login, repo_name, installation_token)

    Raises:
        RuntimeError: If the App has no installations, or no installation can
                      see a repo by that name, or the name is ambiguous.
    """
    repo = repo.strip().strip("/")

    # ── Explicit "owner/repo" -- skip discovery entirely ────────────────────
    if "/" in repo:
        owner, _, repo_name = repo.partition("/")
        resp = requests.get(
            f"{GITHUB_API}/repos/{owner}/{repo_name}/installation",
            headers=_jwt_headers(),
            timeout=REQUEST_TIMEOUT,
        )
        if resp.status_code == 404:
            raise RuntimeError(
                f"This App has no installation with access to "
                f"'{owner}/{repo_name}'. Install it on '{owner}' and grant "
                f"access to that repository."
            )
        resp.raise_for_status()
        installation_id = resp.json()["id"]
        return owner, repo_name, _get_installation_token(installation_id)

    key = repo.lower()

    with _owner_lock:
        cached = _owner_cache.get(key)
    if cached:
        owner, installation_id = cached
        return owner, repo, _get_installation_token(installation_id)

    installations = _list_installations()
    if not installations:
        raise RuntimeError(
            "This GitHub App has no installations. Install it on the target "
            "account first: Settings -> Developer settings -> GitHub Apps -> "
            "Install App."
        )

    # ── Single installation: the account login is definitionally the owner ──
    if len(installations) == 1:
        inst = installations[0]
        owner = (inst.get("account") or {}).get("login")
        installation_id = inst.get("id")
        if not owner or not installation_id:
            raise RuntimeError(
                "Installation response missing account login or id; cannot "
                "determine repository owner."
            )
        with _owner_lock:
            _owner_cache[key] = (owner, installation_id)
        return owner, repo, _get_installation_token(installation_id)

    # ── Multiple installations: find which account holds this repo name ─────
    matches = []   # list of (owner, installation_id)

    for inst in installations:
        installation_id = inst.get("id")
        account_login = (inst.get("account") or {}).get("login")
        if not installation_id:
            continue

        token = _get_installation_token(installation_id)

        # An installation may be granted only a subset of its account's repos,
        # so we ask what it can actually see rather than assuming.
        page = 1
        while True:
            resp = requests.get(
                f"{GITHUB_API}/installation/repositories",
                headers=_token_headers(token),
                params={"per_page": 100, "page": page},
                timeout=REQUEST_TIMEOUT,
            )
            resp.raise_for_status()
            repos = resp.json().get("repositories", [])
            if not repos:
                break

            for r in repos:
                if r.get("name", "").lower() == key:
                    # full_name is "owner/repo" -- authoritative owner casing.
                    owner = r.get("full_name", "/").split("/")[0] or account_login
                    matches.append((owner, installation_id))

            if len(repos) < 100:
                break
            page += 1

    if not matches:
        accounts = ", ".join(
            (i.get("account") or {}).get("login", "?") for i in installations
        )
        raise RuntimeError(
            f"Repository '{repo}' is not accessible to any installation of "
            f"this App. Installed on: {accounts}. Either the repo name is "
            f"wrong, or the installation's repository access does not include "
            f"it (Install App -> Configure -> Repository access)."
        )

    if len(matches) > 1:
        owners = ", ".join(owner for owner, _ in matches)
        raise RuntimeError(
            f"Repository name '{repo}' is ambiguous -- it exists under "
            f"multiple accounts this App is installed on: {owners}. "
            f"Disambiguate by passing the full 'owner/repo' as the repo "
            f"argument."
        )

    owner, installation_id = matches[0]
    with _owner_lock:
        _owner_cache[key] = (owner, installation_id)
    return owner, repo, _get_installation_token(installation_id)


# ─────────────────────────────────────────────────────────────────────────────
# TOOL SCHEMA
# ─────────────────────────────────────────────────────────────────────────────


class GithubAppReaderSchema(BaseModel):
    """
    Input schema. Three fields, no owner: the owner is derived from the
    App installation.
    """

    folder_location: str = Field(
        ...,
        description=(
            "Repository folder path to read recursively. Specify the exact "
            "folder path within the repository that you want to read all files "
            "from. Example: 'lld' for root level folder or 'project_k/lld' for "
            "nested folder structure."
        ),
    )
    repo: str = Field(
        ...,
        description=(
            "Repository name without owner prefix. This should be the exact "
            "name of the GitHub repository you want to access. Example: "
            "'my-project-repo'. A fully qualified "
            "'owner/repo' is also accepted but is not required."
        ),
    )
    branch: str = Field(
        ...,
        description=(
            "Branch name to read files from. Specify the exact branch name "
            "where the files are located. Example: 'main', 'develop', or "
            "'feature/my-feature'."
        ),
    )


class GithubAppReader(BaseTool):
    """
    CrewAI tool for recursively reading all files from a GitHub repository
    folder, authenticating as a **GitHub App installation**.

    API endpoints used:
        App-level (JWT) -- owner/token resolution, cached after first run:
            GET  /app/installations                    (always)
            POST /app/installations/{id}/access_tokens  (once per ~55 min)
            GET  /repos/{owner}/{repo}/installation    (only if "owner/repo" given)
        Installation-level (ghs_ token):
            GET  /installation/repositories            (only if >1 installation)
            GET  /repos/{owner}/{repo}
            GET  /repos/{owner}/{repo}/contents/{folder}?ref={branch}
            GET  /repos/{owner}/{repo}/branches/{branch}
            GET  /repos/{owner}/{repo}/git/trees/{sha}?recursive=1
            GET  /repos/{owner}/{repo}/contents/{file}?ref={branch}  (per file)

        There is no GET /user call. An installation token has no associated
        human, so the owner comes from the installation's own account.

    Rate limits:
        5,000 requests/hour per installation, scaling to 15,000 for larger
        organisations — generally more headroom than a PAT, and it does not
        consume any human's personal quota.
    """

    name: str = "GitHub App Reader"
    description: str = (
        "Tool to read all files from a folder in a GitHub repository using "
        "GitHub App installation credentials. Accepts folder location, repo, "
        "and branch, and returns file contents recursively."
    )
    args_schema: Type[BaseModel] = GithubAppReaderSchema

    def _run(self, folder_location: str, repo: str, branch: str) -> Any:
        """
        Execute the read. See module docstring for the auth flow.

        Returns:
            dict | str: On success, {repository, branch, folder_location, files}
                        where each `files` entry carries status "success",
                        "binary_or_non_utf8", "not_found", or "error".
                        On failure, a descriptive error string.
        """
        try:
            # ═══════════════════════════════════════════════════════════════
            # PHASE 1: INPUT VALIDATION
            # ═══════════════════════════════════════════════════════════════
            if not isinstance(folder_location, str) or not folder_location.strip():
                return "Error reading scripts: 'folder_location' must be a non-empty string."

            folder_location = folder_location.strip().strip("/")

            # ═══════════════════════════════════════════════════════════════
            # PHASE 2: APP AUTHENTICATION + OWNER RESOLUTION
            # ═══════════════════════════════════════════════════════════════
            try:
                repo_owner, repo, token = _resolve_owner_and_token(repo)
            except RuntimeError as exc:
                return f"Error reading scripts: {exc}"

            headers = _token_headers(token)
            base_url = f"{GITHUB_API}/repos/{repo_owner}/{repo}"

            # ═══════════════════════════════════════════════════════════════
            # PHASE 3: REPOSITORY EXISTENCE VERIFICATION
            # ═══════════════════════════════════════════════════════════════
            repo_check = requests.get(base_url, headers=headers, timeout=REQUEST_TIMEOUT)
            if repo_check.status_code == 404:
                return f"Error: Repository '{repo_owner}/{repo}' not found."
            repo_check.raise_for_status()

            file_contents: Dict[str, Any] = {}

            # ═══════════════════════════════════════════════════════════════
            # PHASE 4: FOLDER EXISTENCE VERIFICATION
            # ═══════════════════════════════════════════════════════════════
            encoded_folder = quote(folder_location, safe="/")
            folder_api_url = f"{base_url}/contents/{encoded_folder}"

            folder_response = requests.get(
                folder_api_url,
                headers=headers,
                params={"ref": branch},
                timeout=REQUEST_TIMEOUT,
            )
            if folder_response.status_code == 404:
                return (
                    f"Error reading scripts: Folder '{folder_location}' not found "
                    f"in branch '{branch}'."
                )
            folder_response.raise_for_status()

            # ═══════════════════════════════════════════════════════════════
            # PHASE 5: BRANCH AND TREE SHA RESOLUTION
            # ═══════════════════════════════════════════════════════════════
            branch_api_url = f"{base_url}/branches/{quote(branch, safe='')}"
            branch_response = requests.get(
                branch_api_url, headers=headers, timeout=REQUEST_TIMEOUT
            )
            branch_response.raise_for_status()
            branch_data = branch_response.json()

            tree_sha = (
                branch_data.get("commit", {})
                .get("commit", {})
                .get("tree", {})
                .get("sha")
            )
            if not tree_sha:
                return "Error reading scripts: Unable to resolve tree SHA for branch."

            # ═══════════════════════════════════════════════════════════════
            # PHASE 6: RECURSIVE TREE RETRIEVAL
            # ═══════════════════════════════════════════════════════════════
            tree_url = f"{base_url}/git/trees/{tree_sha}"
            tree_response = requests.get(
                tree_url,
                headers=headers,
                params={"recursive": "1"},
                timeout=REQUEST_TIMEOUT,
            )
            tree_response.raise_for_status()
            tree_data = tree_response.json()

            # GitHub silently truncates trees above ~100k entries or 7 MB.
            # Worth surfacing rather than returning a quietly partial result.
            truncated = bool(tree_data.get("truncated"))

            # ═══════════════════════════════════════════════════════════════
            # PHASE 7: FILE FILTERING
            # ═══════════════════════════════════════════════════════════════
            prefix = f"{folder_location}/"
            target_files = [
                item
                for item in tree_data.get("tree", [])
                if item.get("type") == "blob"
                and item.get("path", "").startswith(prefix)
            ]

            if not target_files:
                return {
                    "repository": f"{repo_owner}/{repo}",
                    "branch": branch,
                    "folder_location": folder_location,
                    "files": {},
                    "message": f"No files found under folder '{folder_location}'.",
                }

            # ═══════════════════════════════════════════════════════════════
            # PHASE 8: FILE CONTENT RETRIEVAL AND DECODING
            # ═══════════════════════════════════════════════════════════════
            for item in target_files:
                file_path = item.get("path")
                if not file_path:
                    continue

                encoded_path = quote(file_path, safe="/")
                api_url = f"{base_url}/contents/{encoded_path}"

                response = requests.get(
                    api_url,
                    headers=headers,
                    params={"ref": branch},
                    timeout=REQUEST_TIMEOUT,
                )

                if response.status_code == 404:
                    file_contents[file_path] = {
                        "status": "not_found",
                        "message": f"File '{file_path}' not found in branch '{branch}'.",
                    }
                    continue

                response.raise_for_status()
                data = response.json()

                if data.get("type") == "file" and "content" in data:
                    try:
                        decoded_content = base64.b64decode(data["content"]).decode("utf-8")
                        file_contents[file_path] = {
                            "status": "success",
                            "content": decoded_content,
                            "size": data.get("size"),
                            "sha": data.get("sha"),
                        }
                    except UnicodeDecodeError:
                        file_contents[file_path] = {
                            "status": "binary_or_non_utf8",
                            "message": "File is not UTF-8 text; content not decoded.",
                            "size": data.get("size"),
                            "sha": data.get("sha"),
                        }
                    except Exception as e:
                        file_contents[file_path] = {
                            "status": "error",
                            "message": f"Failed to decode file content: {str(e)}",
                        }
                else:
                    file_contents[file_path] = {
                        "status": "error",
                        "message": f"Unsupported type: {data.get('type')}",
                    }

            # ═══════════════════════════════════════════════════════════════
            # PHASE 9: RESULT AGGREGATION AND RETURN
            # ═══════════════════════════════════════════════════════════════
            result: Dict[str, Any] = {
                "repository": f"{repo_owner}/{repo}",
                "branch": branch,
                "folder_location": folder_location,
                "files": file_contents,
            }
            if truncated:
                result["message"] = (
                    "Warning: GitHub truncated the repository tree; the file "
                    "list may be incomplete."
                )
            return result

        except requests.exceptions.RequestException as e:
            response_text = ""
            if getattr(e, "response", None) is not None:
                response_text = (
                    f" | GitHub response: {e.response.status_code} {e.response.text}"
                )
            return f"Error reading scripts: {str(e)}{response_text}"

        except Exception as e:
            return f"Error reading scripts: {str(e)}"


if __name__ == "__main__":
    # Smoke test (credentials come from the secret named in SECRET_NAME):
    #   python tool-L0-github-reader-using-app.py
    tool = GithubAppReader()
    out = tool._run(folder_location="src", repo="<your-repo-name>", branch="main")
    if isinstance(out, str):
        print(out)
    else:
        print(out["repository"], out["branch"], f"{len(out['files'])} files")
        for path, meta in out["files"].items():
            print(f"  [{meta['status']}] {path}")