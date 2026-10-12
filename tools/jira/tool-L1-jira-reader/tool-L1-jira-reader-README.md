# tool-L1-jira-reader

## What does it do?

Fetches one or more Jira issues with their complete nested child hierarchy, returning a clean fixed-schema JSON string. For each issue key, the tool retrieves all fields via the Jira REST API, then recursively fetches child work items (using JQL `parent = "<key>"`) up to a configurable depth. Atlassian Document Format (ADF) descriptions are automatically converted to plain text. The output schema is uniform across all levels of the hierarchy.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `base_url` | **AWS Secrets Manager** — secret `aava-secret-manager-jira-credentials`, key `base_url` | Jira instance base URL. Shared with `tool-L1-jira-writer` and `tool-L1-jira-epics-uploader`. |
| `user_email` | **AWS Secrets Manager** — same secret, key `user_email` | Atlassian account email used for HTTP Basic Auth. |
| `api_token` | **AWS Secrets Manager** — same secret, key `api_token` | Jira API token. Never appears in the code. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-jira-reader-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-jira-reader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-jira-credentials"
secrets = reader._run()
JIRA_BASE_URL = secrets.get("base_url")
JIRA_USER_EMAIL = secrets.get("user_email")
JIRA_API_TOKEN = secrets.get("api_token")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity. All three values can still be overridden per-call via `inputJSON` (see Parameters below) if a caller needs to target a different Jira instance.

> `tool-L1-jira-reader.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the credentials as placeholder values in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inputJSON | object | ✓ | Input payload (see structure below). Also accepts a bare key string, comma-separated keys string, or JSON-encoded string — all coerced to a dict automatically. |

### `inputJSON` structure

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| key | string | ✓ (or `keys`) | — | Single Jira issue key (e.g. `"GGMDEMOS-101"`) |
| keys | array[string] | ✓ (or `key`) | — | Multiple Jira issue keys |
| maxDepth | integer | | `5` | Maximum levels of child hierarchy to traverse |
| includeChildren | boolean | | `true` | Whether to fetch child issues at all |
| userEmail | string | | From Secrets Manager | Atlassian account email; overrides the Secrets Manager value for this call |
| apiToken | string | | From Secrets Manager | Jira API token; overrides the Secrets Manager value for this call |
| baseUrl | string | | From Secrets Manager | Jira instance base URL; overrides the Secrets Manager value for this call |

### Input coercion

The `inputJSON` field validator accepts these additional forms:

| Input type | Coerced to |
|-----------|------------|
| `"GGMDEMOS-101"` (bare string) | `{"key": "GGMDEMOS-101"}` |
| `"GGMDEMOS-101, GGMDEMOS-102"` (comma-separated) | `{"keys": ["GGMDEMOS-101", "GGMDEMOS-102"]}` |
| `'["GGMDEMOS-101"]'` (JSON array string) | `{"keys": ["GGMDEMOS-101"]}` |
| `["GGMDEMOS-101"]` (Python list) | `{"keys": ["GGMDEMOS-101"]}` |

## Returns

JSON-encoded string. For a single key, returns a single object. For multiple keys, returns a JSON array.

Each node in the hierarchy has this fixed schema:

| Field | Type | Description |
|-------|------|-------------|
| issue_id | string | Jira issue key (e.g. `"GGMDEMOS-101"`) |
| title | string | Issue summary |
| status | string | Workflow status name (e.g. `"To Do"`, `"In Progress"`) |
| description | string | ADF description converted to plain text |
| labels | array[string] | Issue labels |
| assignee | string \| null | Display name of assignee |
| due_date | string \| null | Due date in `YYYY-MM-DD` format |
| reporter | string \| null | Display name of reporter |
| child_work_item_ids | array[string] | Direct child issue keys |
| children | array[object] | Recursively fetched child nodes (same schema) |

On HTTP error for a specific key, that node has: `{"issue_id": "<key>", "error": "HTTP <code>", "detail": "<response text>"}`.

On fatal error: returns a plain `"Fatal error: ..."` or `"Fatal error (network): ..."` string.

## Standalone tool calling

```python
from tool_L1_jira_reader_secrets_manager import JiraIssueTreeFetcher

tool = JiraIssueTreeFetcher()

# Single issue
result = tool._run({"key": "GGMDEMOS-101"})

# Multiple issues
result = tool._run({"keys": ["GGMDEMOS-101", "GGMDEMOS-110"], "maxDepth": 2})

# Bare string (auto-coerced)
result = tool._run("GGMDEMOS-101")
```

## Calling tool in agent

Tell the agent which Jira issue key(s) to fetch — everything else has a sensible default from Secrets Manager / code:

```
inputJSON = {"key": "{{jira_issue_key}}"}
```

Or for multiple keys:

```
inputJSON = {"keys": [{{jira_issue_keys}}]}
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Missing `key` and `keys` | Neither provided in payload | Returns `"Fatal error: provide 'key' (string) or 'keys' (list)."` |
| Issue HTTP error | 404, 401, 403 from Jira | Node set to `{"issue_id": ..., "error": "HTTP N", "detail": "..."}` |
| Children fetch error | JQL search fails | Children treated as empty list; tree traversal continues |
| Network / timeout | Connection failure or timeout | Returns `"Fatal error (network): ..."` |
| Unexpected exception | JSON parsing, type error | Returns `"Fatal error: ..."` |

## Security Notes

- `base_url`, `user_email`, and `api_token` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- Credentials can still be overridden per-call via `inputJSON.userEmail`, `inputJSON.apiToken`, and `inputJSON.baseUrl`.
- The API token is used via `HTTPBasicAuth` — never logged.
- `PAGE_SIZE = 100` children are fetched per paginated request; all pages are retrieved before building the tree.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Cycle prevention | `_visited` set tracks already-traversed keys; prevents infinite loops in cyclic hierarchies |
| Pagination | Children fetched in pages of 100 using `nextPageToken` until `isLast = true` |
