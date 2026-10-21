# tool-L1-confluence-reader

## What does it do?

Reads the title and full body of a Confluence page via the Confluence REST API v1. Authentication uses HTTP Basic Auth (email + API token). The body is returned in **Confluence storage format**, which is a proprietary XHTML dialect — not plain text, not Markdown. Agents consuming this output must be prepared to handle or strip XHTML tags.

---

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `api_key` | **AWS Secrets Manager** — secret `aava-secret-manager-confluence-credentials`, key `api_key` | Atlassian API token. Never appears in the code. Shared with `tool-L1-confluence-page-writer`. |
| `user_email` | **AWS Secrets Manager** — same secret, key `user_email` | Atlassian account email used for HTTP Basic Auth. |
| `page_id`, `base_url` | Supplied by the caller at call time | Not credentials — passed as parameters on every call (see Parameters below). |

> Every value that must be reviewed before deploying this tool to a new environment or client — `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-confluence-reader-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-confluence-reader-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-confluence-credentials"
secrets = reader._run()
api_key = secrets.get("api_key")
user_email = secrets.get("user_email")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-confluence-reader.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is not used in production and still has the API token as a placeholder value in code.

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | string | ✓ | Numeric ID of the Confluence page (e.g. `"425985"`). Find it in the page URL: `.../pages/425985/Page+Title` |
| `base_url` | string | ✓ | Base URL of the Confluence instance **including `/wiki`** (e.g. `"https://your-domain.atlassian.net/wiki"`) |

---

## Returns

On success, a single formatted string:

```
Title: <page title>
Content: <body in Confluence storage format (XHTML)>
```

On error:

```
Error reading Confluence page: <requests exception message>
```

### ⚠️ Output Format — Confluence Storage Format (XHTML)

The `Content` field is **raw Confluence storage format**, not plain text or Markdown. This is a proprietary XHTML dialect used internally by Confluence. Examples of what you will see:

```xml
<p>This is a paragraph.</p>
<h2>Section Heading</h2>
<ul><li>Bullet point</li></ul>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>This is an info panel.</p></ac:rich-text-body>
</ac:structured-macro>
<ri:page ri:content-title="Another Page" />
```

**Agents and downstream consumers must either:**
- Parse/strip XHTML tags if they need plain text, or
- Treat the string as markup to be passed directly to another Confluence write call

---

## Standalone tool calling

```python
from tool_L1_confluence_reader_secrets_manager import ConfluencePageReader

tool = ConfluencePageReader()
result = tool._run(
    page_id="425985",
    base_url="https://mycompany.atlassian.net/wiki"
)
```

## Calling tool in agent

`page_id` is the value that changes per request; `base_url` is specific to your Confluence instance and should usually be told to the agent as a fixed value rather than asked of the end user:

```
page_id = {{page_id}}
base_url = https://your-domain.atlassian.net/wiki
```

---

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| `401 Unauthorized` | Invalid or expired API token | `RequestException` caught; returns `"Error reading Confluence page: 401 Client Error..."` |
| `403 Forbidden` | Authenticated user lacks page-read permission | Same as above |
| `404 Not Found` | `page_id` does not exist | Returns `"Error reading Confluence page: 404 Client Error..."` |
| `429 Rate Limited` | Too many API requests | Returns error string; no automatic retry in current implementation |
| Network timeout | Confluence instance unreachable | Caught by `RequestException`; returns error string |
| Connection error | DNS failure, firewall | Caught by `RequestException`; returns error string |

---

## API Endpoint Used

```
GET {base_url}/rest/api/content/{page_id}?expand=body.storage
```

Authentication: HTTP Basic Auth (`user_email:api_key`)

---

## Known Issues & Nuances

### 1. Argument Swap Guard (silent behaviour)
The tool contains this guard:
```python
if base_url.isdigit() or page_id.startswith("http"):
    page_id, base_url = base_url, page_id
```
If the calling agent passes the arguments in the wrong order — `page_id="https://..."` or `base_url="425985"` — the tool **silently swaps them and continues** rather than failing fast. While this improves robustness against agent confusion, it can **mask incorrect invocations** and make bugs harder to diagnose.

### 2. Output is XHTML, not plain text
The `Content` field contains raw Confluence storage format. Agents expecting natural-language text will receive XML markup. An HTML/XML parser or stripping step is needed if plain text is required.

### 3. No HTTP timeout configured
There is no `timeout=` argument on the `requests.get()` call. On a slow or unresponsive Confluence instance the request can **hang indefinitely**, blocking the agent's execution thread. A 30 s timeout should be added.

### 4. Only `body.storage` is fetched
The `expand=body.storage` query parameter means only the page body is returned. **Not included**: labels, attachments, comments, page version, space info, child pages, or ancestors. A separate API call is required for any of these.

### 5. No input validation
`page_id` is not validated to be numeric before the API call. A non-numeric `page_id` will cause a `404` or malformed URL.

---

## Security Notes

- `api_key` and `user_email` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- Credentials are passed via HTTP Basic Auth over HTTPS — never logged by the tool.

## Resilience

| Concern | Current state | Recommendation |
|---------|--------------|----------------|
| Timeout | ❌ None configured | Add `timeout=30` to `requests.get()` |
| Retry | ❌ No retry logic | Add retry with exponential backoff for 429/5xx |
| Input validation | ❌ No `page_id` format check | Validate `page_id` is numeric before calling |
| Error detail | ⚠️ Exception message only | Consider including HTTP status code in error string |
