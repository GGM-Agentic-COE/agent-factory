# tool-L0-github-writer-using-app

## 1. Executive summary

You give the tool a list of files (path and text content), a repository, a new branch name and optionally a source branch. It signs in as a GitHub App installation, creates the new branch from the source branch (or reuses it if it already exists) and commits all the files to it in a single commit. It returns a dictionary with the status, the committed paths and a link to the branch.

**Key points** (details in [Section 6](#6-nuances)):

- `files` must be a list. Each item is either `{"filename", "code"}` or `{"<folder>": {"filename", "code"}}`; a dict keyed by file name is not accepted ([6.1](#61-the-files-list-accepts-two-item-shapes)).
- If `new_branch` already exists, the tool does not fail. It commits on top of that branch's current head ([6.2](#62-an-existing-branch-is-reused)).
- Files at the same path are overwritten without warning. The tool never deletes files ([6.3](#63-existing-files-are-overwritten)).
- A 403 almost always means the App's **Contents** permission is Read-only ([6.5](#65-write-access-needs-the-contents-read-and-write-permission)).

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

**`files`**

option 1:

```
[
  {
    "filename": "folder/subfolder1/markdownfile.md",
    "code": "# this is a sample markdown file"
  },

  {
    "filename" : "folder/subfolder2/samplecode.py",
    "code": "print('hello')"
  }
]
```

option 2:
```

```

[
  {"filename": "docs/api.md", "code": "# API\n\nGenerated documentation."},
  {"src": {"filename": "main.py", "code": "print('hello')\n"}}
]
```

**`repo_name`**
```
my-project-repo
```

**`new_branch`**
```
feature/auto-update
```

**`source_branch`**
```
main
```

### 2.2 Calling the tool in an agent

`files` is usually the content the agent has just produced, passed verbatim. `new_branch` normally changes per run. `repo_name` and `source_branch` are usually fixed for the workflow. The GitHub App credentials come from AWS Secrets Manager and the owner is derived from the App installation, so the agent passes neither.

```
files = [{"filename": "{{file_path}}", "code": "{{full_file_content}}"}]
repo_name = {{repo_name}}            # or {{owner}}/{{repo_name}} to skip owner discovery
new_branch = {{new_branch}}
source_branch = main
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | List[dict] | ✓ | Files to commit. Each item is either flat `{"filename": "<path>", "code": "<content>"}` or nested `{"<folder>": {"filename": "<name>", "code": "<content>"}}` (committed to `<folder>/<name>`). Both shapes can be mixed. Missing `filename` defaults to `script.py`; missing `code` defaults to an empty file. |
| `repo_name` | str | ✓ | Repository name, e.g. `my-project-repo`. A fully qualified `owner/repo` is also accepted and skips owner discovery. |
| `new_branch` | str | ✓ | Branch to create and commit to, e.g. `feature/auto-update`. Reused if it already exists. |
| `source_branch` | str | | Branch to copy when creating `new_branch`. Default `main`. It is always looked up and must exist, but its content is not used if `new_branch` already exists. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `app_id` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `app_id` | Numeric GitHub App ID. Used as the JWT issuer only when `client_id` is absent. One of `app_id` / `client_id` is required. |
| `client_id` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `client_id` | GitHub App Client ID. Takes precedence over `app_id` as the JWT issuer. |
| `private_key` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `private_key` | The App's RSA private key in PEM form (PKCS#1 or PKCS#8). Literal `\n` sequences are converted to real newlines. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of the secret holding the keys above. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` hardcoded to `us-east-1`. Set it to the region the secret lives in. |
| AWS credentials | Pod Identity (IAM role on the pod) | The role needs `secretsmanager:GetSecretValue` on the secret. |
| GitHub App installation | GitHub — App settings | The App must be installed on the account that owns the repository, with access to that repository and the **Contents: Read and write** repository permission. |
| Commit message | Code — `GithubCommitterTool._run` | Fixed to `Automation Update: <YYYY-MM-DD HH:MM:SS>` (server local time). |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-github-writer-using-app.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `datetime` | stdlib | Commit message timestamp |
| `os` | stdlib | Imported; not used |
| `threading` | stdlib | Locks around the JWT, token and owner caches |
| `time` | stdlib | JWT timestamps and cache expiry |
| `typing` | stdlib | Type hints |
| `base64` | stdlib | Imported; not used |
| `json` | stdlib | Parsing the secret string |
| `jwt` | `PyJWT[crypto]` | Signing the RS256 App JWT |
| `requests` | `requests` | GitHub REST API calls |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 The files list accepts two item shapes
`files` must be a JSON list. Each item is either flat, `{"filename": "docs/api.md", "code": "..."}`, where `filename` is the full path in the repository, or nested, `{"docs": {"filename": "api.md", "code": "..."}}`, which commits to `docs/api.md`. An item is treated as nested only when it has exactly one key and that key's value contains `filename`; any other item without `filename` is committed as `script.py` with its `code` (or empty content). A single dict keyed by file name instead of a list is rejected. Leading `/` is removed from `filename`, and surrounding `/` from the folder. **Do:** pass a list and give every item an explicit `filename`.

### 6.2 An existing branch is reused
The tool first tries to create `new_branch` from the head of `source_branch`. If GitHub answers 422 (normally "already exists"), it reads the existing branch's head and commits on top of it, so `source_branch` is ignored and earlier commits on that branch are kept. **Do:** use a unique branch name per run when you need a clean branch from `source_branch`.

### 6.3 Existing files are overwritten
All files go into one new tree based on the branch's current tree. A file at the same path is replaced; other files are left as they are. Nothing is ever deleted. **Do:** read the target paths first if overwriting existing content is not wanted.

### 6.4 The owner comes from the App installation
There is no owner parameter. With a bare repo name and one installation, the owner is that installation's account. With several installations, the tool searches each installation's repositories for the name and fails if it exists under more than one account. **Do:** pass `owner/repo` when the App is installed on several accounts.

### 6.5 Write access needs the Contents: Read and write permission
A 403 response gets a `HINT` appended pointing at the App's **Contents** permission being Read-only. After changing the permission, each installation must accept it before writes work. **Do:** set **Contents: Read and write** on the App and have the installation owner approve the change.

### 6.6 Text content only, with a fixed commit message
Content is committed as a regular text file (mode `100644`). The commit message is always `Automation Update: <timestamp>`. The `message` in the result counts the items in `files`, not distinct paths. **Do:** pass text only, and use another tool if you need binary files, a custom commit message or a pull request.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at import) | Load `app_id` / `client_id` and `private_key` |
| 2a | `GET /repos/{owner}/{repo}/installation` (JWT) | Only when `repo_name` is `owner/repo`: find the installation |
| 2b | `GET /app/installations` (JWT) | Bare repo name, not cached: list the App's installations |
| 3 | `POST /app/installations/{id}/access_tokens` (JWT) | Mint an installation token (cached ~55 min) |
| 3a | `GET /installation/repositories` (paginated) | Only with more than one installation: find which account holds the repo |
| 4 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Get the source branch's head SHA |
| 5 | `POST /repos/{owner}/{repo}/git/refs` | Create `new_branch` at that SHA |
| 5a | `GET /repos/{owner}/{repo}/git/ref/heads/{new_branch}` | Only on 422: get the existing branch's head SHA |
| 6 | `POST /repos/{owner}/{repo}/git/trees` | Create a tree with the files on top of the branch's tree |
| 7 | `POST /repos/{owner}/{repo}/git/commits` | Create the commit |
| 8 | `PATCH /repos/{owner}/{repo}/git/refs/heads/{new_branch}` | Move the branch to the new commit |

### 7.2 Returns

**Success**
```
{
  "status": "success",
  "branch": "<new_branch>",
  "source_branch": "<source_branch>",
  "updated_files": ["<path>", ...],
  "message": "Created '<new_branch>' from '<source_branch>' and committed <n> file(s).",
  "url": "https://github.com/<owner>/<repo>/tree/<new_branch>"
}
```

**Error**
```
{"status": "failure", "message": "<detail>"}
```

| Error | Cause | Fix |
|-------|-------|-----|
| `This App has no installation with access to '<owner>/<repo>'. ...` | `owner/repo` given but the App is not installed there | Install the App on that account and grant it the repository |
| `This GitHub App has no installations. ...` | The App is not installed anywhere | Install the App on the target account |
| `Installation response missing account login or id; ...` | Unexpected installation data from GitHub | Check the App installation in GitHub |
| `Repository '<repo>' is not accessible to any installation of this App. ...` | Wrong repo name, or the installation's repository access excludes it | Check the name, or add the repo under Install App -> Configure -> Repository access |
| `Repository name '<repo>' is ambiguous -- ...` | Same name under several installed accounts | Pass `owner/repo` |
| `No App private key configured. ...` | `private_key` missing from the secret | Add `private_key` to the secret |
| `Set CLIENT_ID or APP_ID ...` | Both `client_id` and `app_id` missing from the secret | Add one of them to the secret |
| `<HTTP error> \| GitHub response: 404 <body>` | Source branch or repository not found | Check `source_branch` and `repo_name` |
| `<HTTP error> \| GitHub response: 403 <body> \| HINT: this is almost always the App's Repository permission 'Contents' being Read-only ...` | The App lacks write access | Set **Contents: Read and write** and have the installation accept it |
| `<HTTP error> \| GitHub response: <status> <body>` | Any other HTTP error (e.g. 401 bad JWT, 422 invalid path) | Read GitHub's status and body in the message |
| `<exception text>` | Network error or malformed `files` item | Check connectivity and the `files` shape |
| `Error retrieving secret: ...` / `Unexpected error: ...` (raised at import) | The secret could not be read or is not a JSON object | Check `SECRET_NAME`, the region, and the pod's IAM role |

### 7.3 Known limitations

- Cannot delete or rename files; it only adds or overwrites.
- Cannot open a pull request; it only creates or updates a branch.
- No parameter for the commit message, author or file mode.
- Text content only; binary files cannot be committed.
- Always commits to a separate branch; there is no option to fail if `new_branch` already exists.

### 7.4 Security & resilience

**Security**
- The App ID / Client ID and private key are read from AWS Secrets Manager at import using the pod's IAM role. Nothing is stored in code.
- The JWT and installation token are held only in memory and are never returned or printed.
- Error messages include GitHub's raw response body and may show owner, repository or account names.
- An App private key grants access to every account that installed the App. Keep it only in Secrets Manager and rotate it if exposed.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 seconds on the App authentication and owner lookup calls; none on the branch, tree, commit and ref calls | Pass `timeout=REQUEST_TIMEOUT` on every write-flow request |
| Retry | None; any HTTP error ends the run | Retry 429/5xx with backoff, honouring `Retry-After` |
| Concurrency | Token, JWT and owner caches are thread-safe; two runs writing to the same branch at once can conflict on the final ref update | Use a unique branch per run |
| Input validation | Pydantic type checks only; paths, empty lists and duplicate paths are not checked, and a 422 on branch creation is always treated as "already exists" | Reject empty `files`, validate paths, and check the 422 body before reusing a branch |
