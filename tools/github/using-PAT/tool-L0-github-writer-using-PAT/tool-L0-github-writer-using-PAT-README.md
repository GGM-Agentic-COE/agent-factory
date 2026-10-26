# tool-L0-github-writer-using-PAT

## 1. Summary

You give the tool a list of files (path and content), a repository name, a new branch name and, optionally, a source branch. It authenticates to GitHub with a Personal Access Token (PAT) held in AWS Secrets Manager, creates the new branch from the source branch, and commits all the files to it in a single commit. It returns a dictionary with the status, the committed paths and a link to the branch.

**Key points** (details in [Section 6](#6-nuances)):

- The repository owner is fixed in code (`repo_owner`). You pass only the repository name ([6.1](#61-the-owner-is-fixed-in-code)).
- If the new branch already exists, the tool does not fail. It commits on top of that branch and ignores `source_branch` ([6.2](#62-an-existing-branch-is-reused)).
- Files at the same path are overwritten without warning ([6.3](#63-files-are-overwritten-not-merged)).
- `files` accepts two item shapes, flat and nested by folder ([6.4](#64-two-file-formats-are-accepted)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`files`**
```
[
  {"filename": "docs/api.md", "code": "# API\n\nGenerated documentation.\n"},
  {"src/utils": {"filename": "helpers.py", "code": "def add(a, b):\n    return a + b\n"}}
]
```

**`repo_name`**
```
my-repo
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

`files`, `repo_name` and `new_branch` change per call. `source_branch` is usually fixed to the repository's default branch and can be left out when that is `main`. The owner and token are fixed for the environment.

```
files = {{list of {"filename": <path>, "code": <content>} produced by the agent}}
repo_name = {{repo_name}}
new_branch = {{branch_name}}
source_branch = main
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `files` | List[dict] | ✓ | Files to commit. Each item is either flat `{"filename": "<path>", "code": "<content>"}` or nested `{"<folder>": {"filename": "<name>", "code": "<content>"}}`. A missing `filename` defaults to `script.py`; a missing `code` defaults to an empty file. Leading `/` is stripped from paths. |
| `repo_name` | str | ✓ | Repository name without the owner prefix, e.g. `my-repo`. The owner is `repo_owner` in code. |
| `new_branch` | str | ✓ | Branch to create and commit to, e.g. `feature/auto-update`. If it already exists, the commit is added on top of it. |
| `source_branch` | str |  | Branch to copy when creating `new_branch`. Default `main`. Ignored when `new_branch` already exists. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| `github_token` | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `github_token` | GitHub Personal Access Token. Needs write access to repository contents (`repo` scope, or a fine-grained token with Contents: read and write). Read once when the module is imported. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Set it to the secret that holds `github_token`. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` hardcoded to `us-east-1`. Change it if the secret lives in another region. |
| `repo_owner` | Code — module level | `SETUP-REQUIRED:` placeholder `<your-github-org>`. Set it to the GitHub organisation or username that owns the target repositories. |
| AWS credentials | Pod Identity (IAM role on the pod) | No AWS keys in code. The pod's role needs `secretsmanager:GetSecretValue` on the secret. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-github-writer-secrets-manager-using-PAT.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `datetime` | stdlib | Timestamp in the commit message |
| `typing` | stdlib | Type hints |
| `requests` | `requests` | GitHub REST API calls |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `json` | stdlib | Parsing the secret string |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling for the secret read |

---

## 6. Nuances

### 6.1 The owner is fixed in code
Every call writes to `https://github.com/<repo_owner>/<repo_name>`, where `repo_owner` is set in code. Passing `owner/repo` as `repo_name` produces a wrong URL and a 404. **Do:** pass only the repository name, and set `repo_owner` for the environment before deploying.

### 6.2 An existing branch is reused
The tool first tries to create `new_branch` from the head of `source_branch`. If GitHub answers 422 (the branch already exists), the tool reads the existing branch's head and commits on top of it instead. `source_branch` is then not used, but the success message still says "Created '<new_branch>' from '<source_branch>'". **Do:** use a unique branch name per run when you need a clean branch off `source_branch`.

### 6.3 Files are overwritten, not merged
All files go into one new tree based on the branch's current head. A file at the same path is replaced with the new content; files not listed are left as they are. Files cannot be deleted. Every file is written with mode `100644` (regular, non-executable). **Do:** send the complete final content of each file, not a patch.

### 6.4 Two file formats are accepted
An item with a `filename` key is treated as flat, and `filename` is the full path. An item with no `filename` and exactly one key whose value is a dict with `filename` is treated as nested: the key is the folder and the path becomes `<folder>/<filename>`. Any other shape falls back to `script.py` with empty content, so two malformed items write to the same file. **Do:** always include `filename` and `code` in every item.

### 6.5 One fixed commit message
The commit message is always `Automation Update: <YYYY-MM-DD HH:MM:SS>`, using the pod's local clock. There is no parameter to change it or the author. **Do:** describe the change in the branch name or in the pull request that follows.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at import) | Read `github_token` from the secret named in `SECRET_NAME` |
| 2 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Get the source branch's head SHA |
| 3 | `POST /repos/{owner}/{repo}/git/refs` | Create `new_branch` at that SHA |
| 3a | `GET /repos/{owner}/{repo}/git/ref/heads/{new_branch}` (only on 422) | Get the existing branch's head SHA |
| 4 | `POST /repos/{owner}/{repo}/git/trees` | Create a tree with all files, based on the branch head |
| 5 | `POST /repos/{owner}/{repo}/git/commits` | Create the commit with the branch head as parent |
| 6 | `PATCH /repos/{owner}/{repo}/git/refs/heads/{new_branch}` | Move `new_branch` to the new commit |

### 7.2 Returns

**Success**
```
{
  "status": "success",
  "branch": "<new_branch>",
  "source_branch": "<source_branch>",
  "updated_files": ["<path>", ...],
  "message": "Created '<new_branch>' from '<source_branch>' and committed <n> file(s).",
  "url": "https://github.com/<repo_owner>/<repo_name>/tree/<new_branch>"
}
```

**Error**
```
{"status": "failure", "message": "<exception text>"}
```

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Client Error: Unauthorized for url: ...` | Token invalid, expired or revoked | Rotate the token in the secret |
| `403 Client Error: Forbidden for url: ...` | Token lacks write scope, branch protection, or rate limit | Check token scopes, branch rules and rate limit |
| `404 Client Error: Not Found for url: .../git/ref/heads/<source_branch>` | Repository, owner or `source_branch` does not exist, or the token cannot see it | Check `repo_owner`, `repo_name` and `source_branch` |
| `422 Client Error: Unprocessable Entity for url: ...` | GitHub rejected the tree, commit or ref update, e.g. an invalid path | Check file paths and branch name |
| `<connection error text>` | Network failure | Retry; check connectivity to `api.github.com` |
| `RuntimeError: Error retrieving secret: ...` / `RuntimeError: Unexpected error: ...` | Secret could not be read at import time; the tool does not load | Check `SECRET_NAME`, the region and the pod role's `secretsmanager:GetSecretValue` permission |

### 7.3 Known limitations

- Cannot delete or rename files, or change file modes; every file is written as `100644`.
- Cannot open a pull request; it only creates or updates a branch.
- No owner parameter; all writes go to `repo_owner` set in code.
- No commit message or author parameter.
- Text content only; there is no way to send binary or base64 content.
- All files go into a single commit; there is no per-file commit option.

### 7.4 Security & resilience

**Security**
- The PAT is read from AWS Secrets Manager using the pod's IAM role and kept in memory only. It is not returned, logged or stored in code.
- The tool can write to any repository and branch under `repo_owner` that the token can push to. Use a token scoped to the target repositories and protect important branches.
- Error messages include the GitHub request URL, which shows the owner and repository name.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | None on any GitHub call | Add `timeout=` to every `requests` call |
| Retry | None; any failure returns `status: failure` | Retry 429 and 5xx with exponential backoff, honouring `Retry-After` |
| Concurrency | Not handled; if another push moves the branch between steps, the final ref update fails as a non-fast-forward | Retry the whole sequence from step 2 on a 422 from the ref update |
| Input validation | Only Pydantic type checks; paths, branch names and item shape are not validated | Reject items without `filename`, and empty `repo_name` or `new_branch` |
