# tool-L1-github-writer-using-app

## What does it do?

Creates a new branch from a source branch in a GitHub repository and commits one or more files to it in a single operation, authenticating as a **GitHub App installation** rather than a Personal Access Token. Functionally identical to `tool-L1-github-writer-using-PAT` — same input schema, same commit flow, same idempotent-branch behaviour — but the credential model differs: the tool signs a JWT with the App's private key, exchanges it for a short-lived installation access token, and uses that token for all write operations. The repository owner is derived from the App installation itself, so there's no hardcoded `repo_owner` to maintain.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `app_id` | **AWS Secrets Manager** — secret `aava-secret-manager-github-app-credentials`, key `app_id` | Numeric GitHub App ID. Only one of `app_id` / `client_id` is required. |
| `client_id` | **AWS Secrets Manager** — same secret, key `client_id` | The App's Client ID (`Iv23li...`). Takes precedence over `app_id` when both are set. |
| `private_key` | **AWS Secrets Manager** — same secret, key `private_key` | RSA private key (PEM) used to sign the App's JWT. Never appears in the code. Shared with `tool-L1-github-reader-using-app`. |

> Every value that must be reviewed before deploying this tool to a new environment or client — `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-github-writer-secrets-manager-using-app.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-github-writer-secrets-manager-using-app.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-github-app-credentials"
secrets = reader._run()
APP_ID = secrets.get("app_id")
CLIENT_ID = secrets.get("client_id")
PRIVATE_KEY = secrets.get("private_key")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity. Unlike the PAT-based writer, there is no `repo_owner` to configure — it's resolved automatically from the App installation.

> `tool-L1-github-writer-using-app.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the credentials as placeholder values in code.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| files | array of objects | ✓ | — | List of file descriptors (see formats below) |
| repo_name | string | ✓ | — | Repository name, either bare (`"scib_demo"`) or fully qualified (`"my-org/scib_demo"`) |
| new_branch | string | ✓ | — | Name of the branch to create and commit to (e.g. `"feature/auto-update"`) |
| source_branch | string | | `"main"` | Branch to use as the base when creating `new_branch` |

### File Descriptor Formats

**Flat format:**
```json
{"filename": "docs/api.txt", "code": "API documentation content"}
```

**Nested format** (folder + filename):
```json
{"src/utils": {"filename": "helpers.py", "code": "def add(a, b):\n    return a + b\n"}}
```

Both formats can be mixed in the same `files` list.

## Returns

| Field | Type | Description |
|-------|------|-------------|
| status | string | `"success"` or `"failure"` |
| branch | string | Name of the newly created or updated branch |
| source_branch | string | Branch used as the base |
| updated_files | array[string] | Resolved file paths that were committed |
| message | string | Human-readable summary (e.g. `"Created 'feature/x' from 'main' and committed 3 file(s)."`) |
| url | string | GitHub URL to browse the new branch |

On failure:
```json
{"status": "failure", "message": "<exception message>"}
```

## Standalone tool calling

 Example JSON structure to paste in AAVA, under 'files' variable:
```json
[
  {
    "filename": "docs/summary.md",
    "code": "# Summary\nSprint complete."
  },
  {
    "src": {
      "filename": "main.py",
      "code": "print('hello')\n"
    }
  }
]
```

python code to run locally on IDE, if needed:
```python
from tool_L1_github_writer_secrets_manager_using_app import GithubCommitterTool

tool = GithubCommitterTool()
result = tool._run(
    files=[
        {"filename": "docs/summary.md", "code": "# Summary\nSprint complete."},
        {"src": {"filename": "main.py", "code": "print('hello')\n"}}
    ],
    repo_name="my-repo",
    new_branch="feature/sprint-42-output",
    source_branch="main"
)
print(result["status"])   # "success"
print(result["url"])      # "https://github.com/your-github-org/my-repo/tree/feature/sprint-42-output"
```

## Calling tool in agent

`repo_name`, `new_branch`, and `source_branch` are usually known to the orchestrator ahead of time; `files` is typically the content the agent itself just produced, passed VERBATIM rather than typed by an end user:

```
files = [{"filename": "<<generated-file-name>>", "code": "the full file content that was produced, VERBATIM"}]
repo_name = {{repo_name}}
new_branch = {{new_branch}}
source_branch = main
```

## GitHub API Workflow

| Step | API Call | Purpose |
|------|----------|---------|
| 0 | `GET /app/installations` + `POST /app/installations/{id}/access_tokens` (JWT auth) | Resolve owner and get installation token — cached after first run |
| 1 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Get HEAD SHA of source branch |
| 2 | `POST /repos/{owner}/{repo}/git/refs` | Create new branch (HTTP 422 = already exists → skip to step 2b) |
| 2b | `GET /repos/{owner}/{repo}/git/ref/heads/{new_branch}` | Get current HEAD SHA of existing branch |
| 3 | `POST /repos/{owner}/{repo}/git/trees` | Create tree object with all file contents |
| 4 | `POST /repos/{owner}/{repo}/git/commits` | Create commit pointing to new tree |
| 5 | `PATCH /repos/{owner}/{repo}/git/refs/heads/{new_branch}` | Update branch reference to new commit |

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| App has no installations / repo not visible / ambiguous repo name | Owner resolution failure | Caught and returned as `{"status": "failure", "message": "..."}` before any write is attempted |
| HTTP 403 Forbidden | The App's "Contents" repository permission is Read-only instead of Read and write | Returned failure message includes an explicit HINT about this — the single most common App write failure |
| Branch already exists | HTTP 422 on step 2 | Detected gracefully; commit stacked on existing branch HEAD |
| Network timeout | No response within 30 s | Caught; returned as failure dict |
| Malformed file descriptor | Missing `filename` key | Defaults to `"script.py"` for filename; empty string for code |

## Security Notes

- `app_id`, `client_id`, and `private_key` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- The App must have **Repository permissions → Contents: Read and write**. After changing this permission, each installation must accept it again before writes will succeed.
- JWTs are cached and re-signed at most once per ~8 minutes; installation tokens are cached and re-minted at most once per ~55 minutes.
- The commit message includes a UTC timestamp; no PII is included.
- All file content is passed directly as strings to the GitHub API — ensure content does not contain secrets before committing.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request (requests library default) |
| JWT cache | Re-signs at most once per ~8 minutes |
| Installation token cache | Re-mints at most once per ~55 minutes |
| Idempotency | Existing branch detected via HTTP 422; commit safely stacked on top |
| Diagnostics | 403 responses include a specific hint pointing at the App's Contents permission |
