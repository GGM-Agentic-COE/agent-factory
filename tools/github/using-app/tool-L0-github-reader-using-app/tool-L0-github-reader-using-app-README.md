# tool-L1-github-reader-using-app

## What does it do?

Recursively reads and returns the decoded text contents of all files under a specified folder in a GitHub repository branch, authenticating as a **GitHub App installation** rather than a Personal Access Token. Functionally identical to `tool-L1-github-reader-using-PAT` — same input schema, same output shape, same error semantics — but the credential model differs: the tool signs a JWT with the App's private key, exchanges it for a short-lived installation access token, and uses that token for all repository calls. The repository owner is derived from the App installation itself rather than from a `GET /user` call, since an installation has no associated human user.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `app_id` | **AWS Secrets Manager** — secret `aava-secret-manager-github-app-credentials`, key `app_id` | Numeric GitHub App ID. Only one of `app_id` / `client_id` is required. |
| `client_id` | **AWS Secrets Manager** — same secret, key `client_id` | The App's Client ID (`Iv23li...`). Takes precedence over `app_id` when both are set. |
| `private_key` | **AWS Secrets Manager** — same secret, key `private_key` | RSA private key (PEM) used to sign the App's JWT. Never appears in the code. Shared with `tool-L1-github-writer-using-app`. |

> Every value that must be reviewed before deploying this tool to a new environment or client — `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-github-reader-secrets-manager-using-app.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-github-reader-secrets-manager-using-app.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-github-app-credentials"
secrets = reader._run()
APP_ID = secrets.get("app_id")
CLIENT_ID = secrets.get("client_id")
PRIVATE_KEY = secrets.get("private_key")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-github-reader-using-app.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the credentials as placeholder values in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| folder_location | string | ✓ | Repository folder path to read recursively (e.g. `"src"` or `"project_k/lld"`). Leading/trailing whitespace and slashes are stripped automatically. |
| repo | string | ✓ | Repository name, either bare (`"scib_demo"`) or fully qualified (`"my-org/scib_demo"`). A bare name is resolved automatically via the App's installations. |
| branch | string | ✓ | Exact branch name to read from (e.g. `"main"`, `"feature/SCRUM-11691"`) |

## Returns

On success, a dictionary with the following structure:

| Field | Type | Description |
|-------|------|-------------|
| repository | string | Full repository identifier in `owner/repo` format |
| branch | string | Branch that was read |
| folder_location | string | Normalised folder path (leading/trailing slashes removed) |
| files | object | Per-file results keyed by file path (see below) |
| message | string (optional) | Present when the folder exists but contains no files, or when GitHub truncated a very large tree |

Each entry in `files` has one of these shapes:

**Success:**
```json
{
  "status": "success",
  "content": "<decoded UTF-8 text>",
  "size": 1234,
  "sha": "abc123..."
}
```

**Binary / non-UTF-8:**
```json
{
  "status": "binary_or_non_utf8",
  "message": "File is not UTF-8 text; content not decoded.",
  "size": 5678,
  "sha": "def456..."
}
```

**Not found** (race condition — file deleted between tree and content fetch):
```json
{"status": "not_found", "message": "File '<path>' not found in branch '<branch>'."}
```

**Error:**
```json
{"status": "error", "message": "<description>"}
```

On any unhandled error, returns a plain **error string** (not a dict).

## Standalone tool calling

```python
from tool_L1_github_reader_secrets_manager_using_app import GithubAppReader

tool = GithubAppReader()
result = tool._run(
    folder_location="src/components",
    repo="my-repo",
    branch="main"
)
print(result["repository"])   # "your-github-org/my-repo"
print(result["files"]["src/components/app.py"]["content"])  # decoded file text
```

## Calling tool in agent

All three parameters typically come from the request itself — the repository and branch are usually known ahead of time by the orchestrator/agent rather than typed by an end user, but can be exposed as user input where relevant:

```
folder_location = {{folder_location}}
repo = {{repo}}
branch = {{branch}}
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Empty `folder_location` | Blank or whitespace-only string | Returns error string: `'folder_location' must be a non-empty string` |
| App has no installations | The App isn't installed on any account | Returns `"Error reading scripts: This GitHub App has no installations..."` |
| Repo not visible to any installation | Repo name doesn't match, or installation lacks repository access | Returns `"Error reading scripts: Repository '<repo>' is not accessible to any installation..."` |
| Repo name ambiguous across accounts | Same repo name exists under multiple installed accounts | Returns `"Error reading scripts: Repository name '<repo>' is ambiguous..."`; pass `"owner/repo"` to disambiguate |
| Repository not found | 404 from GitHub | Returns `"Error: Repository '<owner>/<repo>' not found."` |
| Folder not found | Folder path absent in branch | Returns `"Error reading scripts: Folder '<path>' not found in branch '<branch>'."` |
| Tree SHA missing | Unexpected branch API response shape | Returns `"Error reading scripts: Unable to resolve tree SHA for branch."` |
| Tree truncated | Repository has an extremely large tree (~100k+ entries or 7 MB+) | Result still returned, with a `message` warning that the file list may be incomplete |
| Binary / decode error | Non-UTF-8 file content | Entry set to `{"status": "binary_or_non_utf8", ...}` |
| Network / HTTP error | Timeout, 429, 5xx | Returns `"Error reading scripts: <exception> | GitHub response: <status> <text>"` |

## GitHub API Endpoints Used

| Order | Endpoint | Purpose |
|-------|----------|---------|
| 1 | `GET /app/installations` (JWT auth) | List accounts the App is installed on — cached after first run |
| 2 | `POST /app/installations/{id}/access_tokens` (JWT auth) | Exchange JWT for an installation token — re-minted at most once per ~55 min |
| 2b | `GET /repos/{owner}/{repo}/installation` (JWT auth) | Only used when `repo` is passed as `"owner/repo"` |
| 3 | `GET /installation/repositories` (installation token) | Only used when the App has more than one installation, to find which account owns the repo |
| 4 | `GET /repos/{owner}/{repo}` | Verify repository exists |
| 5 | `GET /repos/{owner}/{repo}/contents/{folder}?ref={branch}` | Verify folder exists in branch |
| 6 | `GET /repos/{owner}/{repo}/branches/{branch}` | Fetch root tree SHA |
| 7 | `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` | Retrieve full recursive file list |
| 8 | `GET /repos/{owner}/{repo}/contents/{file}?ref={branch}` | Download each file's content (one call per file) |

There is no `GET /user` call — an installation token has no associated human, so the owner is derived from the installation's own account.

## Security Notes

- `app_id`, `client_id`, and `private_key` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- The App must have **Repository permissions → Contents: Read-only** (Metadata: Read-only is added implicitly by GitHub). Without it, every file fetch returns 404 — indistinguishable from a missing file.
- JWTs are cached and re-signed at most once per ~8 minutes; installation tokens are cached and re-minted at most once per ~55 minutes — a single run performs at most one signature regardless of how many files it reads.
- Rate limit: 5,000 requests/hour per installation, scaling up to 15,000 for larger organisations — and it does not consume any individual's personal PAT quota.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| JWT cache | Re-signs at most once per ~8 minutes |
| Installation token cache | Re-mints at most once per ~55 minutes |
| Binary files | Gracefully flagged, never cause failure |
| Race conditions | Mid-run file deletions handled with `not_found` status |
| Large repositories | Truncated trees surfaced via a `message` warning rather than silently returning a partial result |
