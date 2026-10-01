# tool-L1-jira-writer

## What does it do?

Creates one or more Jira issues from a structured JSON payload, converting their descriptions into Atlassian Document Format (ADF). Descriptions can be provided as plain strings or as structured dictionaries (key → string or list of strings), which are normalised to markdown-ish text then converted to ADF paragraphs and bullet lists. Cross-references matching the pattern `E\d+` (e.g. `E1`, `E1.2`) are auto-linked to already-created issues using a running `id_map`. Issues are created sequentially so earlier issues can be referenced as parents by later ones via their `parentKey` field.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `base_url` | **AWS Secrets Manager** — secret `aava-secret-manager-jira-credentials`, key `base_url` | Jira instance base URL. Shared with `tool-L1-jira-reader` and `tool-L1-jira-epics-uploader`. |
| `user_email` | **AWS Secrets Manager** — same secret, key `user_email` | Atlassian account email used for HTTP Basic Auth. |
| `api_token` | **AWS Secrets Manager** — same secret, key `api_token` | Jira API token. Never appears in the code. |
| `JIRA_PROJECT_KEY` | Set directly in code | Not a secret — the default Jira project this tool operates against. See "SETUP-REQUIRED" comment at the top of the tool file. |

> Every value that must be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-jira-writer-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-jira-writer-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-jira-credentials"
secrets = reader._run()
JIRA_BASE_URL = secrets.get("base_url")
JIRA_USER_EMAIL = secrets.get("user_email")
JIRA_API_TOKEN = secrets.get("api_token")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity. All three values can still be overridden per-call via `inputJSON` (see Parameters below) if a caller needs to target a different Jira instance.

> `tool-L1-jira-writer.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the credentials as placeholder values in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inputJSON | object | ✓ | Top-level payload (see structure below) |

### `inputJSON` structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| projectKey | string | | Jira project key (e.g. `"GGMDEMOS"`). Falls back to the in-code `JIRA_PROJECT_KEY`. |
| issueType | string | | Default issue type (e.g. `"Task"`, `"Epic"`). Falls back to `"Epic"`. |
| userEmail | string | | Atlassian account email; overrides the Secrets Manager value for this call. |
| apiToken | string | | Jira API token; overrides the Secrets Manager value for this call. |
| baseUrl | string | | Jira instance base URL; overrides the Secrets Manager value for this call. |
| issues | array | ✓ | List of issue objects (see below) |

### Each issue object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| summary | string | ✓ | Issue title |
| description | string \| object | ✓ | Plain text or dict of `{heading: value}` pairs |
| issueType | string | | Overrides the default `issueType` for this issue |
| label | array[string] | | Labels to apply; `label[0]` is used as the logical ID for cross-linking |
| parentKey | string | | Real Jira key of the parent issue |

## Returns

| Value | Description |
|-------|-------------|
| `"<IssueType> created: <KEY>. jira_issue_link = <url>"` | One line per successfully created issue |
| `"Failed: <summary> → HTTP <code> \| Detail: <text>"` | One line per failed issue |
| `"Fatal error: <message>"` | Returned when the entire run aborts (e.g. unexpected exception) |

The return value is a newline-joined string of all per-issue results.

## Standalone tool calling

```python
from tool_L1_jira_writer_secrets_manager import JiraIssueCreator

tool = JiraIssueCreator()
result = tool._run(
{
  "projectKey": "GGMDEMOS",
  "issueType": "Task",
  "issues": [
    {
      "summary": "Tool connectivity test",
      "description": "If this issue appears in Jira, the tool works.",
      "label": []
    }
  ]
}


)
```

## Calling tool in agent

`projectKey` is usually fixed per deployment; `issues` is typically the content the agent itself just drafted:

```
inputJSON = {
  "projectKey": "MYPROJ",
  "issues": [
    {"summary": "{{issue_summary}}", "description": "the issue description the agent drafted, VERBATIM"}
  ]
}
```

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| Timeout | API didn't respond in 30 s | `RequestException` caught per-issue; appended as `"Failed: ..."` line |
| 401 Unauthorized | Invalid credentials | `not response.ok` branch; appended as `"Failed: ... → HTTP 401"` |
| 400 Bad Request | Invalid issue type or project key | `not response.ok` branch; Jira error detail included |
| 404 Not Found | Project key or parent key not found | `not response.ok` branch; detail included |
| Per-issue exception | Any unexpected error for one issue | `RequestException` caught; other issues continue processing |
| Fatal exception | Unrecoverable error (e.g. JSON parsing) | Entire `_run` returns `"Fatal error: ..."` |

## Security Notes

- `base_url`, `user_email`, and `api_token` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- Credentials can still be overridden per-call via `inputJSON.userEmail`, `inputJSON.apiToken`, and `inputJSON.baseUrl`.
- The API token is used via HTTP Basic Auth (`HTTPBasicAuth`) — never logged.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Partial failure | Per-issue errors are isolated; other issues in the batch continue |
| Cross-linking | `id_map` built incrementally — earlier issues' keys available for later issues |
