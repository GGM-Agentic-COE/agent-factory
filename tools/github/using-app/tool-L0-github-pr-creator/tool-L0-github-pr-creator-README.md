# tool-L0-github-pr-creator

## 1. Executive summary

You give the tool a repository, a source branch, a pull request title and optionally a destination branch. It signs in as a GitHub App installation, checks that both branches exist and that the source branch has commits the destination lacks, and opens a pull request from the source into the destination. It returns a dictionary with the status, the pull request number and its link, or the already-open pull request if one exists for the same branches.

**Key points** (details in [Section 6](#6-nuances)):

- If an open pull request already exists from `source_branch` into `destination_branch`, it is returned with `already_existed: true` instead of creating a new one ([6.1](#61-an-open-pull-request-for-the-same-branches-is-reused)).
- The tool refuses to open an empty pull request: `source_branch` must have commits that `destination_branch` does not ([6.2](#62-the-source-branch-must-be-ahead-of-the-destination)).
- Only the title is set; there is no body, draft flag, reviewer or label option ([6.4](#64-title-only)).
- The App needs **Pull requests: Read and write** and **Contents: Read**. A 403 or 404 usually means one of these is missing ([6.5](#65-required-github-app-permissions)).

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

**`repo_name`**
```
my-project-repo
```

**`source_branch`**
```
feature/auto-update
```

**`pull_request_title`**
```
Add automated API documentation updates
```

**`destination_branch`**
```
main
```

### 2.2 Calling the tool in an agent

`source_branch` and `pull_request_title` normally change per run; the source branch is usually the one a previous step committed to, and the title summarises that change. `repo_name` and `destination_branch` are usually fixed for the workflow. The GitHub App credentials come from AWS Secrets Manager and the owner is derived from the App installation, so the agent passes neither.

```
repo_name = {{repo_name}}                  # or {{owner}}/{{repo_name}} to skip owner discovery
source_branch = {{branch_with_changes}}
pull_request_title = {{short_summary_of_the_change}}
destination_branch = main
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `repo_name` | str | ✓ | Repository name, e.g. `my-project-repo`. A fully qualified `owner/repo` is also accepted and skips owner discovery. |
| `source_branch` | str | ✓ | Branch that contains the changes (the pull request head), e.g. `feature/auto-update`. Must exist in the same repository. Surrounding whitespace is stripped. |
| `pull_request_title` | str | ✓ | Pull request title, e.g. `Add automated API documentation updates`. Surrounding whitespace is stripped; an empty title is rejected. |
| `destination_branch` | str | | Branch to merge into (the pull request base). Default `main`. Must exist and differ from `source_branch`. |

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
| GitHub App installation | GitHub — App settings | The App must be installed on the account that owns the repository, with access to that repository and the repository permissions **Pull requests: Read and write** (list and create pull requests) and **Contents: Read** (branch refs and compare). |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-github-pr-creator.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `json` | stdlib | Parsing the secret string |
| `threading` | stdlib | Locks around the JWT, token and owner caches |
| `time` | stdlib | JWT timestamps and cache expiry |
| `typing` | stdlib | Type hints |
| `urllib.parse` | stdlib | URL-encoding branch names in API paths |
| `boto3` | `boto3` | Secrets Manager client |
| `jwt` | `PyJWT[crypto]` | Signing the RS256 App JWT |
| `requests` | `requests` | GitHub REST API calls |
| `botocore.exceptions` | `botocore` | `ClientError` handling |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |

---

## 6. Nuances

### 6.1 An open pull request for the same branches is reused
Before creating anything, the tool looks for an open pull request from `<owner>:<source_branch>` into `destination_branch`. If one exists, it returns that pull request with `already_existed: true`, its existing title (the `pull_request_title` you passed is not applied) and no `commits` or `files_changed` fields. Closed or merged pull requests are ignored, so a new one is opened. **Do:** check `already_existed` in the result, and edit the existing pull request in GitHub if its title must change.

### 6.2 The source branch must be ahead of the destination
The tool compares `destination_branch...source_branch` and fails with `No commits to merge: ...` when the source has no commits the destination lacks. This check runs after the existing-pull-request check, so an already-open pull request is still returned. **Do:** commit the changes to `source_branch` (for example with tool-L0-github-writer-using-app) before calling this tool.

### 6.3 Both branches must exist in the same repository
Each branch is looked up in the target repository first, and a missing one fails with `<Source|Destination> branch '<branch>' does not exist in '<owner>/<repo>'.` The pull request head is always a branch of that repository; branches from forks are not supported. Branch names with `/` (e.g. `feature/x`) work. **Do:** pass branch names exactly as they appear in the repository, without an `owner:` prefix.

### 6.4 Title only
The pull request is created with `title`, `head` and `base` only. It has no description, is never a draft, and has no reviewers, assignees or labels. **Do:** put the key information in `pull_request_title`, and add a description or reviewers in GitHub or with another tool if needed.

### 6.5 Required GitHub App permissions
From the calls it makes, the App needs the repository permissions **Pull requests: Read and write** (list open pull requests, create a pull request) and **Contents: Read** (read branch refs, compare branches). A 403 gets a `HINT` about the Pull requests permission. GitHub returns 404 instead of 403 on a private repository the App cannot see, so a 404 gets a `HINT` about repository access and both permissions. After changing permissions, each installation must accept them, and installation tokens already cached by the running process (up to about 55 minutes) keep the old permissions. **Do:** set both permissions on the App, have the installation owner approve them, and restart the process if a permission was just added.

### 6.6 The owner comes from the App installation
There is no owner parameter. With a bare repo name and one installation, the owner is that installation's account. With several installations, the tool searches each installation's repositories for the name and fails if it exists under more than one account. **Do:** pass `owner/repo` when the App is installed on several accounts.

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
| 4 | `GET /repos/{owner}/{repo}/git/ref/heads/{source_branch}` | Check the source branch exists |
| 5 | `GET /repos/{owner}/{repo}/git/ref/heads/{destination_branch}` | Check the destination branch exists |
| 6 | `GET /repos/{owner}/{repo}/pulls?state=open&head={owner}:{source_branch}&base={destination_branch}` | Find an already-open pull request for the same pair |
| 7 | `GET /repos/{owner}/{repo}/compare/{destination_branch}...{source_branch}` | Only if none is open: count commits and files to merge |
| 8 | `POST /repos/{owner}/{repo}/pulls` | Only if the source is ahead: create the pull request |

### 7.2 Returns

**Success**
```
{
  "status": "success",
  "already_existed": false,
  "pull_request_number": 42,
  "pull_request_title": "<pull_request_title>",
  "source_branch": "<source_branch>",
  "destination_branch": "<destination_branch>",
  "commits": <commits source is ahead by>,
  "files_changed": <files in the compare response>,
  "message": "Opened pull request #42 from '<source_branch>' into '<destination_branch>' in '<owner>/<repo>'.",
  "url": "https://github.com/<owner>/<repo>/pull/42"
}
```

When an open pull request already exists:
```
{
  "status": "success",
  "already_existed": true,
  "pull_request_number": 42,
  "pull_request_title": "<existing title>",
  "source_branch": "<source_branch>",
  "destination_branch": "<destination_branch>",
  "message": "An open pull request #42 already exists from '<source_branch>' into '<destination_branch>'.",
  "url": "https://github.com/<owner>/<repo>/pull/42"
}
```

**Error**
```
{"status": "failure", "message": "<detail>"}
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Both source_branch and destination_branch are required.` | A branch is empty or whitespace | Pass both branch names |
| `A non-empty pull request title is required.` | Title is empty or whitespace | Pass a title |
| `Source and destination branch are the same ('<branch>').` | `source_branch` equals `destination_branch` | Use different branches |
| `This App has no installation with access to '<owner>/<repo>'. ...` | `owner/repo` given but the App is not installed there | Install the App on that account and grant it the repository |
| `This GitHub App has no installations. ...` | The App is not installed anywhere | Install the App on the target account |
| `Installation response missing account login or id; ...` | Unexpected installation data from GitHub | Check the App installation in GitHub |
| `Repository '<repo>' is not accessible to any installation of this App. ...` | Wrong repo name, or the installation's repository access excludes it | Check the name, or add the repo under Install App -> Configure -> Repository access |
| `Repository name '<repo>' is ambiguous -- ...` | Same name under several installed accounts | Pass `owner/repo` |
| `No App private key configured. ...` | `private_key` missing from the secret | Add `private_key` to the secret |
| `Set CLIENT_ID or APP_ID ...` | Both `client_id` and `app_id` missing from the secret | Add one of them to the secret |
| `Source branch '<branch>' does not exist in '<owner>/<repo>'.` | Source branch not found | Check the name or create the branch first |
| `Destination branch '<branch>' does not exist in '<owner>/<repo>'.` | Destination branch not found | Check `destination_branch` |
| `No commits to merge: '<source>' has no changes that '<destination>' does not already contain.` | Source is not ahead of destination | Commit changes to the source branch first |
| `GitHub rejected the pull request: <message> (<details>)` | GitHub returned 422 on creation, e.g. a pull request opened at the same moment by another run | Read GitHub's reason in the message; call again to get the existing pull request |
| `<HTTP error> \| GitHub response: 403 <message> \| HINT: this is almost always the App lacking the Repository permission 'Pull requests: Read and write'. ...` | The App lacks write access to pull requests | Set **Pull requests: Read and write** and have the installation accept it |
| `<HTTP error> \| GitHub response: 404 <message> \| HINT: GitHub returns 404 instead of 403 when an App lacks permission on a private repository. ...` | The installation cannot see the repository, or lacks Contents / Pull requests permission | Check repository access and both permissions |
| `<HTTP error> \| GitHub response: <status> <message>` | Any other HTTP error (e.g. 401 bad JWT) | Read GitHub's status and message |
| `<exception text>` | Network error or other unexpected failure | Check connectivity and inputs |
| `Error retrieving secret: ...` / `Unexpected error: ...` (raised at import) | The secret could not be read or is not a JSON object | Check `SECRET_NAME`, the region, and the pod's IAM role |

### 7.3 Known limitations

- Cannot create, update or merge branches, or commit files; both branches must already exist.
- Cannot open a pull request from a fork; the head is always a branch in the target repository.
- No parameter for a description, draft status, reviewers, assignees or labels.
- Cannot update, close or merge an existing pull request; an open one is returned as is.
- Does not open a pull request when the source branch has no new commits.

### 7.4 Security & resilience

**Security**
- The App ID / Client ID and private key are read from AWS Secrets Manager at import using the pod's IAM role. Nothing is stored in code.
- The JWT and installation token are held only in memory and are never returned or printed.
- Error messages include GitHub's error message and may show owner, repository, branch or account names.
- An App private key grants access to every account that installed the App. Keep it only in Secrets Manager and rotate it if exposed.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 seconds on every GitHub request; none set on the Secrets Manager call | Keep; add a boto3 timeout config if import hangs are a concern |
| Retry | None; any HTTP error ends the run | Retry 429/5xx with backoff, honouring `Retry-After` |
| Concurrency | Token, JWT and owner caches are thread-safe; two runs for the same branch pair can race, and the loser gets a 422 `GitHub rejected the pull request` | Call again after a 422 to receive the existing pull request |
| Input validation | Pydantic type checks; empty branches or title and identical branches are rejected; both branches must exist and the source must be ahead before creation | Also validate branch names against GitHub's ref rules and limit title length |
