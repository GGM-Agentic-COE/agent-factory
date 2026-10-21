import json
import threading
import time
from typing import Any, Dict, Tuple, Type
from urllib.parse import quote

import boto3
import jwt  # PyJWT -- install with the [crypto] extra for RS256 support
import requests
from botocore.exceptions import ClientError
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# ═════════════════════════════════════════════════════════════════════════════
#  CREDENTIALS -- unchanged from the committer tool
# ═════════════════════════════════════════════════════════════════════════════

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
    SECRET_NAME: str = "aava/aava-github-app-dev-secret-asm"

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

# ═════════════════════════════════════════════════════════════════════════════

# JWT lifetime. GitHub rejects `exp` more than 600s in the future. We also
# backdate `iat` by 60s (see _generate_app_jwt) to absorb clock skew.
# With the 60s backdating, exp - iat = 540s, which stays strictly under 600.
JWT_TTL_SECONDS = 480

# Re-sign the JWT this many seconds before it expires.
JWT_REFRESH_MARGIN = 60

# Refresh the installation token this many seconds before its stated expiry.
TOKEN_REFRESH_MARGIN = 300  # 5 minutes

REQUEST_TIMEOUT = 30


def _load_private_key() -> str:
    """
    Return the App's RSA private key as a PEM string.

    Both PKCS#1 and PKCS#8 are accepted -- PyJWT handles either.

    Raises:
        RuntimeError: If no key is configured.
    """
    if PRIVATE_KEY:
        key = PRIVATE_KEY
        # Docker/K8s/CI env vars routinely carry the PEM with two-character
        # backslash-n sequences instead of real newlines. Normalise it here.
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

_jwt_cache: Dict[str, Any] = {"token": None, "expires_at": 0.0}
_jwt_lock = threading.Lock()


def _generate_app_jwt() -> str:
    """
    Return a JWT authenticating as the GitHub App itself, signing only when
    the cached one is missing or near expiry.
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

        # PyJWT 1.x returned bytes; 2.x returns str. Normalise.
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
    """Headers for repo-level endpoints."""
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


# ─────────────────────────────────────────────────────────────────────────────
# INSTALLATION TOKEN MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

_token_cache: Dict[int, Tuple[str, float]] = {}   # installation_id -> (token, expires_at)
_cache_lock = threading.Lock()


def _list_installations() -> list:
    """GET /app/installations (JWT auth)."""
    resp = requests.get(
        f"{GITHUB_API}/app/installations",
        headers=_jwt_headers(),
        params={"per_page": 100},
        timeout=REQUEST_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()


def _get_installation_token(installation_id: int) -> str:
    """POST /app/installations/{id}/access_tokens (JWT auth), with caching."""
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
    with _cache_lock:
        _token_cache[installation_id] = (token, time.time() + 3600)
    return token


_owner_cache: Dict[str, Tuple[str, int]] = {}   # repo (lowercased) -> (owner, installation_id)
_owner_lock = threading.Lock()


def _resolve_owner_and_token(repo: str) -> Tuple[str, str, str]:
    """
    Determine the owner of `repo` and return (owner, repo_name, token).

    Accepts a bare repo name ("scib_demo") or "owner/repo".
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


# ═════════════════════════════════════════════════════════════════════════════
#  PULL REQUEST TOOL -- new
# ═════════════════════════════════════════════════════════════════════════════

def _branch_path(branch: str) -> str:
    """URL-encode a branch name for use in a path, keeping '/' (feature/x)."""
    return quote(branch, safe="/")


def _github_error_message(resp: requests.Response) -> str:
    """
    Extract GitHub's human-readable reason from an error response.

    422s in particular carry the real cause in `errors[]`, e.g.
    "A pull request already exists for owner:branch." or
    "No commits between main and feature/x".
    """
    try:
        data = resp.json()
    except ValueError:
        return resp.text

    message = data.get("message", "") if isinstance(data, dict) else str(data)
    details = []
    for err in (data.get("errors") or []) if isinstance(data, dict) else []:
        if isinstance(err, dict):
            details.append(
                err.get("message")
                or f"{err.get('resource', '')} {err.get('field', '')} {err.get('code', '')}".strip()
            )
        else:
            details.append(str(err))
    return f"{message} ({'; '.join(details)})" if details else message


class GithubPullRequestSchema(BaseModel):
    """Input schema for GithubPullRequestTool."""

    repo_name: str = Field(
        ...,
        description="The name of the repository, bare or fully qualified. "
                    "Example: 'SCIB-Inception' or 'my-org/SCIB-Inception'.",
    )
    source_branch: str = Field(
        ...,
        description="The branch that contains the changes (the PR 'head'). "
                    "Example: 'feature/auto-update'.",
    )
    pull_request_title: str = Field(
        ...,
        description="The pull request title / message, provided at runtime. "
                    "Example: 'Add automated API documentation updates'.",
    )
    destination_branch: str = Field(
        default="main",
        description="The branch the changes should be merged into (the PR "
                    "'base'). Defaults to 'main'.",
    )


class GithubPullRequestTool(BaseTool):
    """
    Opens a pull request from a source branch into a destination branch,
    authenticating as a GitHub App installation.

    Owner and token resolution are shared with the committer and reader tools.

    Behaviour:
      * Both branches are verified to exist before anything is created.
      * If an OPEN pull request already exists for the same source ->
        destination pair, it is returned instead of erroring (idempotent).
      * If the source branch has no commits that the destination lacks, no
        PR is created and a clear failure message is returned.

    API endpoints used:
        App-level (JWT) -- owner/token resolution, cached after first run:
            GET  /app/installations
            POST /app/installations/{id}/access_tokens
        Installation-level (ghs_ token):
            GET  /repos/{owner}/{repo}/git/ref/heads/{branch}     (x2)
            GET  /repos/{owner}/{repo}/pulls?head=...&base=...
            GET  /repos/{owner}/{repo}/compare/{base}...{head}
            POST /repos/{owner}/{repo}/pulls

    Required App permissions:
        Contents:       Read
        Pull requests:  Read and write
    """

    name: str = "Github Pull Request Creator"
    description: str = (
        "Creates a pull request in a GitHub repository from a source branch "
        "into a destination branch, using the pull request title supplied at "
        "runtime. Returns the PR number and URL. If an open "
        "PR already exists for the same branches, returns that one instead."
    )
    args_schema: Type[BaseModel] = GithubPullRequestSchema

    def _run(
        self,
        repo_name: str,
        source_branch: str,
        pull_request_title: str,
        destination_branch: str = "main",
    ) -> Any:
        try:
            source_branch = (source_branch or "").strip()
            destination_branch = (destination_branch or "").strip()
            pr_title = (pull_request_title or "").strip()

            if not source_branch or not destination_branch:
                return {
                    "status": "failure",
                    "message": "Both source_branch and destination_branch are required.",
                }
            if not pr_title:
                return {
                    "status": "failure",
                    "message": "A non-empty pull request title is required.",
                }
            if source_branch == destination_branch:
                return {
                    "status": "failure",
                    "message": f"Source and destination branch are the same ('{source_branch}').",
                }

            # ═══════════════════════════════════════════════════════════════
            # 0. APP AUTHENTICATION + OWNER RESOLUTION (shared logic)
            # ═══════════════════════════════════════════════════════════════
            try:
                repo_owner, repo_name, token = _resolve_owner_and_token(repo_name)
            except RuntimeError as exc:
                return {"status": "failure", "message": str(exc)}

            headers = _token_headers(token)
            base_api = f"{GITHUB_API}/repos/{repo_owner}/{repo_name}"
            full_name = f"{repo_owner}/{repo_name}"

            # 1. Verify both branches exist, so the agent gets a precise
            #    message instead of GitHub's generic 422 "Validation Failed".
            for label, branch in (("Source", source_branch), ("Destination", destination_branch)):
                resp = requests.get(
                    f"{base_api}/git/ref/heads/{_branch_path(branch)}",
                    headers=headers,
                    timeout=REQUEST_TIMEOUT,
                )
                # A 404, or a list of partial matches, both mean "no such branch".
                if resp.status_code == 404 or (resp.ok and not isinstance(resp.json(), dict)):
                    return {
                        "status": "failure",
                        "message": f"{label} branch '{branch}' does not exist in '{full_name}'.",
                    }
                resp.raise_for_status()

            # 2. Idempotency: return an already-open PR for the same pair.
            existing_resp = requests.get(
                f"{base_api}/pulls",
                headers=headers,
                params={
                    "state": "open",
                    "head": f"{repo_owner}:{source_branch}",
                    "base": destination_branch,
                    "per_page": 1,
                },
                timeout=REQUEST_TIMEOUT,
            )
            existing_resp.raise_for_status()
            existing_prs = existing_resp.json()
            if existing_prs:
                pr = existing_prs[0]
                return {
                    "status": "success",
                    "already_existed": True,
                    "pull_request_number": pr.get("number"),
                    "pull_request_title": pr.get("title"),
                    "source_branch": source_branch,
                    "destination_branch": destination_branch,
                    "message": (
                        f"An open pull request #{pr.get('number')} already exists "
                        f"from '{source_branch}' into '{destination_branch}'."
                    ),
                    "url": pr.get("html_url"),
                }

            # 3. Make sure there is actually something to merge.
            compare_resp = requests.get(
                f"{base_api}/compare/{_branch_path(destination_branch)}...{_branch_path(source_branch)}",
                headers=headers,
                timeout=REQUEST_TIMEOUT,
            )
            compare_resp.raise_for_status()
            compare = compare_resp.json()
            ahead_by = compare.get("ahead_by", 0)
            if ahead_by == 0:
                return {
                    "status": "failure",
                    "message": (
                        f"No commits to merge: '{source_branch}' has no changes "
                        f"that '{destination_branch}' does not already contain."
                    ),
                }

            # 4. Create the pull request.
            create_resp = requests.post(
                f"{base_api}/pulls",
                headers=headers,
                json={
                    "title": pr_title,
                    "head": source_branch,
                    "base": destination_branch,
                },
                timeout=REQUEST_TIMEOUT,
            )
            if create_resp.status_code == 422:
                # Covers races (PR opened between step 2 and now) and other
                # validation errors GitHub reports.
                return {
                    "status": "failure",
                    "message": f"GitHub rejected the pull request: {_github_error_message(create_resp)}",
                }
            create_resp.raise_for_status()
            pr = create_resp.json()

            return {
                "status": "success",
                "already_existed": False,
                "pull_request_number": pr.get("number"),
                "pull_request_title": pr.get("title"),
                "source_branch": source_branch,
                "destination_branch": destination_branch,
                "commits": ahead_by,
                "files_changed": len(compare.get("files", []) or []),
                "message": (
                    f"Opened pull request #{pr.get('number')} from "
                    f"'{source_branch}' into '{destination_branch}' in '{full_name}'."
                ),
                "url": pr.get("html_url"),
            }

        except requests.exceptions.HTTPError as e:
            detail = ""
            response = getattr(e, "response", None)
            if response is not None:
                detail = f" | GitHub response: {response.status_code} {_github_error_message(response)}"
                if response.status_code == 403:
                    detail += (
                        " | HINT: this is almost always the App lacking the "
                        "Repository permission 'Pull requests: Read and write'. "
                        "After adding it, each installation must accept the new "
                        "permission, and tokens minted before that (cached up to "
                        "1 hour in this process) still carry the old permissions."
                    )
                elif response.status_code == 404:
                    detail += (
                        " | HINT: GitHub returns 404 instead of 403 when an App "
                        "lacks permission on a private repository. Check that the "
                        "installation can access this repo and has the 'Contents' "
                        "and 'Pull requests' permissions."
                    )
            return {"status": "failure", "message": f"{str(e)}{detail}"}

        except Exception as e:
            return {"status": "failure", "message": str(e)}
 