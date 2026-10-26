# tool-L0-github-reader-using-PAT

## 1. Summary

You give the tool a folder path, a repository name and a branch. It authenticates to GitHub with a Personal Access Token (PAT) held in AWS Secrets Manager, finds every file under that folder (including sub-folders) and downloads each one. It returns a dictionary with the decoded text of every file, keyed by file path, plus a per-file status.

**Key points** (details in [Section 6](#6-nuances)):

- The repository owner is always the user who owns the token. You pass only the repo name, and organisation-owned repositories cannot be reached ([6.1](#61-the-owner-is-the-tokens-user)).
- The read is recursive. Every file in every sub-folder of `folder_location` is downloaded, one API call per file ([6.2](#62-the-read-is-recursive-and-costs-one-call-per-file)).
- Binary and non-UTF-8 files are listed but their content is not returned ([6.3](#63-binary-files-return-metadata-only)).
- Errors come back as a plain string, not a dictionary ([6.4](#64-errors-are-strings-successes-are-dictionaries)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`folder_location`**
```
docs/design
```

**`repo`**
```
my-repo
```

**`branch`**
```
main
```

### 2.2 Calling the tool in an agent

All three parameters can change per call. The owner, the token and the Secrets Manager region are fixed for the environment, so the agent never passes them.

```
folder_location = {{folder_location}}
repo = {{repo_name}}
branch = {{branch_name}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `folder_location` | str | ✓ | Folder path inside the repository to read recursively, e.g. `docs` or `project/docs`. Must not be empty. Surrounding whitespace and leading or trailing `/` are stripped. |
| `repo` | str | ✓ | Repository name without the owner prefix, e.g. `my-repo` (not `owner/my-repo`). The owner is the login of the token's user. |
| `branch` | str | ✓ | Exact branch name to read from, e.g. `main` or `feature/new-login`. Case-sensitive. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `github_token` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `github_token` | GitHub Personal Access Token. Needs read access to repository contents (`repo` scope for private repos, or a fine-grained token with Contents: read). Read once when the module is imported. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Set it to the secret that holds `github_token`. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` hardcoded to `us-east-1`. Change it if the secret lives in another region. |
| AWS credentials | Pod Identity (IAM role on the pod) | No AWS keys in code. The pod's role needs `secretsmanager:GetSecretValue` on the secret. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-github-reader-secrets-manager-using-PAT.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `requests` | `requests` | GitHub REST API calls |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `urllib.parse` | stdlib | URL-encoding folder, file and branch paths (`quote`) |
| `base64` | stdlib | Decoding file content returned by the Contents API |
| `json` | stdlib | Parsing the secret string |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling for the secret read |

---

## 6. Nuances

### 6.1 The owner is the token's user
The tool calls `GET /user` and uses the returned login as the repository owner, so it always reads `<token-user>/<repo>`. A repository owned by an organisation, or by a different user who shared it with the token's user, returns `Error: Repository '<owner>/<repo>' not found.` **Do:** pass only the repository name, and make sure the PAT belongs to the account that owns the repository.

### 6.2 The read is recursive and costs one call per file
Every file (blob) whose path starts with `<folder_location>/` is downloaded, including files in nested sub-folders. Each file is a separate Contents API call, so a large folder uses a large share of GitHub's rate limit and can take a long time. Submodules and folder entries are skipped. **Do:** point the tool at the narrowest folder you need.

### 6.3 Binary files return metadata only
Each file is base64-decoded and then decoded as UTF-8. Files that are not valid UTF-8 (images, PDFs, archives) get `status: "binary_or_non_utf8"` with size and SHA but no `content`. Other per-file problems get `status: "not_found"` or `status: "error"`. One bad file does not stop the others. **Do:** check each file's `status` before using `content`.

### 6.4 Errors are strings, successes are dictionaries
On success the tool returns a dictionary. On any failure (empty folder path, repository or folder not found, HTTP error, network error) it returns a single string starting with `Error reading scripts:` or `Error: Repository`. A folder that exists but has no files returns a dictionary with an empty `files` and a `message`. **Do:** check whether the result is a string before reading `files`.

### 6.5 The whole repository cannot be read
`folder_location` must be non-empty, and the path match is `<folder_location>/`, so there is no value that selects the repository root. **Do:** call the tool once per top-level folder you need.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at import) | Read `github_token` from the secret named in `SECRET_NAME` |
| 2 | `GET https://api.github.com/user` | Resolve the token user's login, used as the owner |
| 3 | `GET /repos/{owner}/{repo}` | Check the repository exists and is accessible |
| 4 | `GET /repos/{owner}/{repo}/contents/{folder_location}?ref={branch}` | Check the folder exists on the branch |
| 5 | `GET /repos/{owner}/{repo}/branches/{branch}` | Get the branch head's tree SHA |
| 6 | `GET /repos/{owner}/{repo}/git/trees/{tree_sha}?recursive=1` | List every file in the branch |
| 7 | `GET /repos/{owner}/{repo}/contents/{path}?ref={branch}` (per file) | Download and decode each file under the folder |

### 7.2 Returns

**Success**
```
{
  "repository": "<owner>/<repo>",
  "branch": "<branch>",
  "folder_location": "<normalised folder>",
  "files": {
    "<path>": {"status": "success", "content": "<text>", "size": <bytes>, "sha": "<blob sha>"},
    "<path>": {"status": "binary_or_non_utf8", "message": "File is not UTF-8 text; content not decoded.", "size": <bytes>, "sha": "<blob sha>"},
    "<path>": {"status": "not_found", "message": "File '<path>' not found in branch '<branch>'."},
    "<path>": {"status": "error", "message": "Failed to decode file content: <detail>" | "Unsupported type: <type>"}
  }
}
```

When the folder exists but contains no files, `files` is `{}` and a `"message": "No files found under folder '<folder>'."` key is added.

**Error**
```
Error reading scripts: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Error reading scripts: 'folder_location' must be a non-empty string.` | `folder_location` is empty or whitespace | Pass a folder path |
| `Error: Repository '<owner>/<repo>' not found.` | Repo name wrong, repo not owned by the token user, or token cannot see it | Check the name and the token's owner and scopes |
| `Error reading scripts: Folder '<folder>' not found in branch '<branch>'.` | Folder path or branch is wrong (404 on the folder) | Check the path, branch and their case |
| `Error reading scripts: Unable to resolve tree SHA for branch.` | Branch response did not contain a tree SHA | Check the branch name |
| `Error reading scripts: <exception> \| GitHub response: <status> <body>` | GitHub returned an HTTP error, e.g. 401 bad token, 403 rate limit or scope, 404 branch not found | Act on the status code: rotate the token, wait for the rate limit, or fix the branch name |
| `Error reading scripts: <exception>` | Network failure or other unexpected error | Retry; check connectivity to `api.github.com` |
| `RuntimeError: Error retrieving secret: ...` / `RuntimeError: Unexpected error: ...` | Secret could not be read at import time; the tool does not load | Check `SECRET_NAME`, the region and the pod role's `secretsmanager:GetSecretValue` permission |

### 7.3 Known limitations

- Read-only. It cannot create, change or delete files.
- No owner parameter. Only repositories owned by the token's user can be read.
- Cannot read a single file or the repository root; it reads one folder recursively.
- Branch names only. Tags and commit SHAs are not accepted, because the branch endpoint is used to resolve the tree.
- No filter by file type or name, and no file size limit or recursion depth option.
- Text only. Binary files are not decoded or extracted.
- Very large repositories may return a truncated tree from GitHub; the tool does not detect this.

### 7.4 Security & resilience

**Security**
- The PAT is read from AWS Secrets Manager using the pod's IAM role and kept in memory only. It is not returned, logged or stored in code.
- On HTTP errors, the raw GitHub response body is appended to the error string.
- The token's scopes define what the tool can see. Use a read-only, least-privilege token.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 s on `GET /user` only; all other GitHub calls have no timeout | Add `timeout=` to every `requests` call |
| Retry | None | Retry 429 and 5xx with exponential backoff, honouring `Retry-After` |
| Concurrency | Files are downloaded one at a time | Use a bounded thread pool, within GitHub rate limits |
| Input validation | `folder_location` must be non-empty; `repo` and `branch` are not validated beyond URL-encoding | Reject empty `repo` and `branch` with a clear message |
