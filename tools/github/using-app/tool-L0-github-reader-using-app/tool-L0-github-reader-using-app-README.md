# tool-L0-github-reader-using-app

## 1. Executive summary

You give the tool a repository, a branch and a folder path. It signs in as a GitHub App installation, finds every file under that folder (including sub-folders) on that branch, and downloads each one. It returns a dictionary keyed by file path with each file's decoded text, size, blob SHA and a per-file status.

**Key points** (details in [Section 6](#6-nuances)):

- You do not pass an owner. A bare repo name is resolved through the App's installations; pass `owner/repo` when the same name exists under more than one account ([6.1](#61-the-owner-comes-from-the-app-installation)).
- The success result is a dictionary, but every failure is a plain string. Check the type before reading `files` ([6.2](#62-success-is-a-dict-failure-is-a-string)).
- Each file carries its own `status`. Binary files, missing files and unsupported entries are flagged per file and do not stop the read ([6.3](#63-check-each-files-status)).
- A wrong branch name is reported as "Folder ... not found in branch ..." ([6.4](#64-a-wrong-branch-looks-like-a-missing-folder)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_location`**
```
project_k/lld
```

**`repo`**
```
my-project-repo
```

**`branch`**
```
main
```

### 2.2 Calling the tool in an agent

All three parameters can change per call. The GitHub App credentials come from AWS Secrets Manager and the owner is derived from the App installation, so the agent passes neither.

```
folder_location = {{folder_location}}
repo = {{repo_name}}            # or {{owner}}/{{repo_name}} to skip owner discovery
branch = {{branch}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_location` | str | ✓ | Folder inside the repository to read recursively, e.g. `lld` or `project_k/lld`. Must be non-empty. Surrounding whitespace and leading/trailing `/` are stripped. |
| `repo` | str | ✓ | Repository name, e.g. `my-project-repo`. A fully qualified `owner/repo` is also accepted and skips owner discovery. Surrounding whitespace and `/` are stripped. |
| `branch` | str | ✓ | Exact branch name to read from, e.g. `main`, `develop` or `feature/my-feature`. |

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
| GitHub App installation | GitHub — App settings | The App must be installed on the account that owns the repository, with access to that repository and the **Contents: Read** repository permission. |
| `REQUEST_TIMEOUT` | Code | `30` seconds per GitHub request. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-github-reader-using-app.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `base64` | stdlib | Decoding file content returned by GitHub |
| `os` | stdlib | Imported; not used |
| `threading` | stdlib | Locks around the JWT, token and owner caches |
| `time` | stdlib | JWT timestamps and cache expiry |
| `typing` | stdlib | Type hints |
| `urllib.parse` | stdlib | URL-encoding folder, file and branch paths |
| `json` | stdlib | Parsing the secret string |
| `jwt` | `PyJWT[crypto]` | Signing the RS256 App JWT |
| `requests` | `requests` | GitHub REST API calls |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 The owner comes from the App installation
There is no owner parameter. With a bare repo name and one installation, the owner is that installation's account. With several installations, the tool searches each installation's accessible repositories for the name and fails if it is found under more than one account. The resolved owner is cached for the life of the process. **Do:** pass `owner/repo` when the App is installed on several accounts or when the name may be ambiguous.

### 6.2 Success is a dict, failure is a string
A successful read returns a dictionary with `repository`, `branch`, `folder_location` and `files`. Every failure (bad input, App not installed, repo or folder not found, HTTP or network error) returns a single string starting with `Error reading scripts:` or `Error:`. **Do:** check whether the result is a string before reading `files`.

### 6.3 Check each file's status
Each entry in `files` has a `status`: `success` (with `content`), `binary_or_non_utf8` (content not decoded), `not_found`, or `error` (decode failure, or an entry GitHub does not return as a regular file). One bad file does not stop the others. **Do:** use only entries with `status` `success`, and treat the others as missing content.

### 6.4 A wrong branch looks like a missing folder
The folder is checked on the given branch before the branch itself is looked up, so a misspelt branch returns `Error reading scripts: Folder '<folder>' not found in branch '<branch>'.` **Do:** confirm the branch name as well as the folder path when you see this error.

### 6.5 The read is recursive and unfiltered
Every file whose path starts with `<folder_location>/` is downloaded, one request per file, in tree order. If the folder exists but holds no files, `files` is `{}` and `message` says `No files found under folder '<folder>'.` For very large repositories GitHub may truncate the tree, and `message` then carries a warning that the list may be incomplete. **Do:** point the tool at the narrowest folder you need, and check `message` when completeness matters.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at import) | Load `app_id` / `client_id` and `private_key` |
| 2a | `GET /repos/{owner}/{repo}/installation` (JWT) | Only when `repo` is `owner/repo`: find the installation |
| 2b | `GET /app/installations` (JWT) | Bare repo name, not cached: list the App's installations |
| 3 | `POST /app/installations/{id}/access_tokens` (JWT) | Mint an installation token (cached ~55 min) |
| 3a | `GET /installation/repositories` (paginated) | Only with more than one installation: find which account holds the repo |
| 4 | `GET /repos/{owner}/{repo}` | Confirm the repository exists |
| 5 | `GET /repos/{owner}/{repo}/contents/{folder}?ref={branch}` | Confirm the folder exists on the branch |
| 6 | `GET /repos/{owner}/{repo}/branches/{branch}` | Get the branch's tree SHA |
| 7 | `GET /repos/{owner}/{repo}/git/trees/{sha}?recursive=1` | List every file in the repository |
| 8 | `GET /repos/{owner}/{repo}/contents/{file}?ref={branch}` (per file) | Download and decode each file under the folder |

### 7.2 Returns

**Success**
```
{
  "repository": "<owner>/<repo>",
  "branch": "<branch>",
  "folder_location": "<folder>",
  "files": {
    "<path>": {"status": "success", "content": "<text>", "size": <bytes>, "sha": "<blob sha>"},
    "<path>": {"status": "binary_or_non_utf8", "message": "File is not UTF-8 text; content not decoded.", "size": <bytes>, "sha": "<blob sha>"},
    "<path>": {"status": "not_found", "message": "File '<path>' not found in branch '<branch>'."},
    "<path>": {"status": "error", "message": "Failed to decode file content: <error>" | "Unsupported type: <type>"}
  },
  "message": "No files found under folder '<folder>'." | "Warning: GitHub truncated the repository tree; the file list may be incomplete."   (only when applicable)
}
```

**Error**
```
Error reading scripts: <detail>
Error: Repository '<owner>/<repo>' not found.
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Error reading scripts: 'folder_location' must be a non-empty string.` | Empty or blank `folder_location` | Pass a folder path |
| `Error reading scripts: This App has no installation with access to '<owner>/<repo>'. ...` | `owner/repo` given but the App is not installed there | Install the App on that account and grant it the repository |
| `Error reading scripts: This GitHub App has no installations. ...` | The App is not installed anywhere | Install the App on the target account |
| `Error reading scripts: Installation response missing account login or id; ...` | Unexpected installation data from GitHub | Check the App installation in GitHub |
| `Error reading scripts: Repository '<repo>' is not accessible to any installation of this App. ...` | Wrong repo name, or the installation's repository access excludes it | Check the name, or add the repo under Install App -> Configure -> Repository access |
| `Error reading scripts: Repository name '<repo>' is ambiguous -- ...` | Same name under several installed accounts | Pass `owner/repo` |
| `Error reading scripts: No App private key configured. ...` | `private_key` missing from the secret | Add `private_key` to the secret |
| `Error reading scripts: Set CLIENT_ID or APP_ID ...` | Both `client_id` and `app_id` missing from the secret | Add one of them to the secret |
| `Error: Repository '<owner>/<repo>' not found.` | Repository check returned 404 | Check the repo name and the installation's access |
| `Error reading scripts: Folder '<folder>' not found in branch '<branch>'.` | Folder or branch does not exist | Check both the folder path and the branch name |
| `Error reading scripts: Unable to resolve tree SHA for branch.` | Branch response had no tree SHA | Check the branch in GitHub |
| `Error reading scripts: <error> \| GitHub response: <status> <body>` | Any other HTTP or network error (e.g. 401 bad JWT, 403 missing permission, rate limit) | Read GitHub's status and body in the message |
| `Error retrieving secret: ...` / `Unexpected error: ...` (raised at import) | The secret could not be read or is not a JSON object | Check `SECRET_NAME`, the region, and the pod's IAM role |

### 7.3 Known limitations

- Read-only. It cannot create, change or delete files.
- No owner parameter; the owner is always derived from the App installation.
- No filter by file type or name pattern, and no option to stop recursion into sub-folders.
- Text only. Binary files are flagged, not returned.
- Only regular files are decoded. Entries GitHub does not return as a file (for example some symlinks) are reported as `Unsupported type: <type>`, and submodules are skipped.
- Files larger than 1 MB are not returned inline by GitHub's contents API, so they may come back with empty `content`. The tool has no fallback for large files.
- Reads branches only. The ref is resolved through the branches endpoint, so tags and commit SHAs are not supported.

### 7.4 Security & resilience

**Security**
- The App ID / Client ID and private key are read from AWS Secrets Manager at import using the pod's IAM role. Nothing is stored in code.
- The JWT and installation token are held only in memory and are never returned or printed.
- Error strings include GitHub's raw response body and may show owner, repository or account names.
- An App private key grants access to every account that installed the App. Keep it only in Secrets Manager and rotate it if exposed.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 seconds per GitHub request (`REQUEST_TIMEOUT`); the Secrets Manager call uses boto3 defaults | Keep; add an overall time budget for very large folders |
| Retry | None; any non-404 HTTP error ends the run | Retry 429/5xx with backoff, honouring `Retry-After` |
| Concurrency | Files are downloaded one at a time; token, JWT and owner caches are thread-safe | Use a bounded thread pool for large folders |
| Input validation | Only `folder_location` is checked for non-empty; `repo` and `branch` are not validated | Reject empty `repo` and `branch` with a clear message |
