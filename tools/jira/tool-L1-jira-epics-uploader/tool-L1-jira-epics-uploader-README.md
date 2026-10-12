# tool-L1-jira-epics-uploader

## What does it do?

Creates Jira Epics and child Stories (or any issue types) from a structured payload produced by the `L1-inception-jira-payload-converter-agent`. Descriptions are converted to Atlassian Document Format (ADF) with support for bold text, italic text, bullet lists, and automatic cross-reference hyperlinks. Parent links are resolved in a single pass using a logical ID map — e.g. `parentKey: "EP-01"` is replaced by the real Jira key once `EP-01` has been created. A `dry_run` mode builds and validates all payloads without posting to Jira. ADF is sanitised to remove empty nodes before every POST.

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `base_url` | **AWS Secrets Manager** — secret `aava-secret-manager-jira-credentials`, key `base_url` | Jira instance base URL. Shared with `tool-L1-jira-reader` and `tool-L1-jira-writer`. |
| `user_email` | **AWS Secrets Manager** — same secret, key `user_email` | Atlassian account email used for HTTP Basic Auth. |
| `api_token` | **AWS Secrets Manager** — same secret, key `api_token` | Jira API token. Never appears in the code. |
| `ISSUE_TYPE_MAP` | Set directly in code | Not a secret — optional remap of issue types (e.g. if your project doesn't offer "Epic"/"Story"). |

> Every value that *must* be reviewed before deploying this tool to a new environment or client — including `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class. Search the file for that tag to find them all in one pass. (`ISSUE_TYPE_MAP` above is optional, not required, so it is intentionally left untagged.)

The production tool (`tool-L1-jira-epics-uploader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-jira-credentials"
secrets = reader._run()
JIRA_BASE_URL = secrets.get("base_url")
JIRA_USER_EMAIL = secrets.get("user_email")
JIRA_API_TOKEN = secrets.get("api_token")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity. All three values can still be overridden per-call via `inputJSON` (see Parameters below) if a caller needs to target a different Jira instance.

> `tool-L1-jira-epics-uploader-epics.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the credentials as placeholder values in code.

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| inputJSON | object | ✓ | Top-level payload (see structure below) |

### `inputJSON` structure

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| projectKey | string | | Jira project key (e.g. `"GGMDEMOS"`)|
| issueType | string | | Default issue type. Falls back to `"Epic"`. Per-issue `issueType` overrides this. |
| userEmail | string | | Atlassian account email; overrides the Secrets Manager value for this call. |
| apiToken | string | | Jira API token; overrides the Secrets Manager value for this call. |
| baseUrl | string | | Jira instance base URL; overrides the Secrets Manager value for this call. |
| issues | array | ✓ | Ordered list of issue objects — **epics must appear before their child features** so `parentKey` can be resolved in a single pass. |

### Each issue object

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| summary | string | ✓ | Issue title |
| description | string \| object | | Plain text, or `{heading: str/list[str]/dict}` normalised to markdown then converted to ADF |
| issueType | string | | Overrides the batch default for this issue |
| label | array[string] | | Labels to apply; `label[0]` is the **logical ID** (e.g. `"EP-01"`, `"F-01.1"`) used for cross-linking and parent resolution |
| parentKey | string | | Logical ID (e.g. `"EP-01"`) **or** a real Jira key — resolved to the actual key via `id_map` before posting |

> **Ordering rule:** Because `parentKey` is resolved in a single linear pass, parent issues (Epics) must be listed before their children (Stories/Features) in the `issues` array.

## Returns

| Value | Description |
|-------|-------------|
| `"[DRY RUN] <IssueType> '<summary>' -> <fake-key> (parent=<key>)"` | One line per issue in dry-run mode |
| `"<IssueType> created: <KEY>  (<summary>)"` | One line per successfully created issue |
| `"Failed: <summary> -> HTTP <code> \| Detail: <text>"` | One line per failed issue |
| `"Fatal error: <message>"` | Entire run aborted |

## Standalone tool calling

```python
from tool_L1_jira_epics_uploader_secrets_manager import JiraIssueCreator, create_issues

payload = 

{
    "projectKey": "MYPROJ",
    "issueType": "Epic",
    "issues": [
        {
            "summary": "EP-01: Platform Foundation",
            "issueType": "Epic",
            "label": ["EP-01", "S1"],
            "parentKey": null,
            "description": {
                "description": "Technical foundation for the Credit Coach agent.",
                "scope_in": ["Envoy agent registration", "Consent capture flow"],
                "scope_out": ["Score retrieval (see EP-02)"]
            }
        },
        {
            "summary": "F-01.1: Envoy Agent Registration",
            "issueType": "Story",
            "label": ["F-01.1"],
            "parentKey": "EP-01",   
            "description": "Register Credit Coach as a specialist agent. Relates to EP-01."
        }
    ]
}

# Dry run (no Jira calls)
print(create_issues(payload, dry_run=True))

# Live run
print(create_issues(payload))
```

## Calling tool in agent

`issues` is typically the payload produced by the upstream Jira-payload-converter agent, passed through VERBATIM rather than typed by an end user:

```
inputJSON = the full { "projectKey": ..., "issues": [...] } payload produced by the converter agent, VERBATIM
```

## ADF Conversion Rules

| Input markup | ADF output |
|-------------|-----------|
| `**bold text**` | `{"type": "text", "text": "bold text", "marks": [{"type": "strong"}]}` |
| `*italic text*` | `{"type": "text", "text": "italic text", "marks": [{"type": "em"}]}` |
| `- list item` | `bulletList > listItem > paragraph` |
| `EP-01`, `F-01.1`, etc. in `id_map` | Hyperlink to `{base_url}/browse/{MYPROJ-42}` |
| Dict description | Each key becomes a `**Heading**` paragraph; list values become bullet lists |

ADF is sanitised after conversion — empty text nodes, empty paragraphs, and empty containers are removed. A document with no content gets a single space paragraph so Jira always receives valid ADF.

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| No `projectKey` | Neither in payload nor in config | Returns `"Fatal error: no projectKey provided..."` |
| Empty or non-list `issues` | Malformed payload | Returns `"Fatal error: 'issues' must be a non-empty list."` |
| HTTP error per issue | 400 Bad Request, 401, 404, etc. | Appended as `"Failed: ..."` line; other issues continue |
| `parentKey` not yet resolved | Parent issue not in `id_map` | `parentKey` treated as a real Jira key (passed through as-is) |
| Network / timeout | Connection failure | Per-issue `RequestException` caught; appended as `"Failed: ..."` |
| Fatal exception | Unexpected error | Returns `"Fatal error: ..."` |

## ISSUE_TYPE_MAP

If your Jira project uses non-standard issue type names, populate `ISSUE_TYPE_MAP` at the top of the file:

```python
ISSUE_TYPE_MAP = {"Epic": "Task", "Story": "Task"}
```

This remaps the payload's types before posting, avoiding misleading 400 errors.

## Security Notes

- `base_url`, `user_email`, and `api_token` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- Credentials can still be overridden per-call via `inputJSON`.
- The API token is used via `HTTPBasicAuth` — never logged.

## Resilience

| Concern | Configuration |
|---------|--------------|
| Timeout | 30 s per HTTP request |
| Retry | Max 2 retries with exponential backoff on transient errors |
| Circuit breaker | 5 consecutive failures → open for 60 s |
| Dry-run mode | `dry_run=True` builds and validates all payloads without any Jira API calls |
| Partial failure | Per-issue errors are isolated; the batch continues for remaining issues |
| Cross-linking | `id_map` built incrementally — earlier issues' real keys are available for later cross-links |
