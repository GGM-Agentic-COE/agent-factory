<<<<<<<< HEAD:tools/github/using-PAT/tool-L1-github-writer-using-PAT/tool-L1-github-writer-using-PAT-README.md
# tool-L1-github-writer-using-PAT
========
# tool-L1-github-writer
>>>>>>>> main:tools/api-secrets-exposed/tool-L1-github-writer/tool-L1-github-writer-README.md

## What does it do?

Creates a new branch from a source branch in a GitHub repository and commits one or more files to it in a single operation. The tool handles both flat and nested file descriptor formats, builds a Git tree object containing all the files, creates a commit, and updates the branch reference atomically. If the target branch already exists, the commit is stacked on top of its current HEAD — the tool is idempotent on the branch name.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `github_token` (GitHub PAT) | **AWS Secrets Manager** — secret `aava-secret-manager-github-credentials`, key `github_token` | Never appears in the code. Shared with `tool-L1-github-reader-using-PAT`. |
| `repo_owner` | Set directly in code | Not a secret — the GitHub org/user that owns the target repos. See "SETUP-REQUIRED" comment at the top of the tool file. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-github-writer-secrets-manager-using-PAT.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-github-writer-secrets-manager-using-PAT.py`) retrieves its token at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-github-credentials"
secrets = reader._run()
github_token = secrets.get("github_token")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no token is stored in this file; access is granted via the runtime's pod identity. `repo_owner` is a plain configuration value (not a credential), so it stays hardcoded in the file rather than in Secrets Manager — update it if your GitHub org/username changes.

> `tool-L1-github-writer-using-PAT.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the token as a placeholder value in code.

## Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| files | array of objects | ✓ | — | List of file descriptors (see formats below) |
| repo_name | string | ✓ | — | Repository name without owner prefix (e.g. `"SCIB-Inception"`) |
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

```python
from tool_L1_github_writer_secrets_manager_using_PAT import GithubCommitterTool

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
| 1 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Get HEAD SHA of source branch |
| 2 | `POST /repos/{owner}/{repo}/git/refs` | Create new branch (HTTP 422 = already exists → skip to step 2b) |
| 2b | `GET /repos/{owner}/{repo}/git/ref/heads/{new_branch}` | Get current HEAD SHA of existing branch |
| 3 | `POST /repos/{owner}/{repo}/git/trees` | Create tree object with all file contents |
| 4 | `POST /repos/{owner}/{repo}/git/commits` | Create commit pointing to new tree |
| 5 | `PATCH /repos/{owner}/{repo}/git/refs/heads/{new_branch}` | Update branch reference to new commit |

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| HTTP 4xx/5xx | API error on any step | `raise_for_status()` raises; caught by outer `except`; returned as `{"status": "failure", "message": "..."}` |
| Branch already exists | HTTP 422 on step 2 | Detected gracefully; commit stacked on existing branch HEAD |
| Invalid token | 401 Unauthorized | Caught; returned as failure dict |
| Network timeout | No response within 30 s | Caught; returned as failure dict |
| Malformed file descriptor | Missing `filename` key | Defaults to `"script.py"` for filename; empty string for code |

## Security Notes

- `github_token` is retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- `repo_owner` is not a credential; it's fixed per deployment in code (see Secrets & Configuration above).
- The commit message includes a UTC timestamp; no PII is included.
- All file content is passed directly as strings to the GitHub API — ensure content does not contain secrets before committing.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request (requests library default) |
| Retry | Max 2 retries with exponential backoff on transient errors (429, 502, 503, timeout) |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Idempotency | Existing branch detected via HTTP 422; commit safely stacked on top |
