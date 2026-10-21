<<<<<<<< HEAD:tools/confluence/tool-L1-confluence-writer/tool-L1-confluence-writer-README.md
# tool-L1-confluence-writer
========
# tool-L1-confluence-page-writer
>>>>>>>> main:tools/api-secrets-exposed/tool-L1-confluence-page-writer/tool-L1-confluence-page-writer-README.md

## What does it do?

Creates a new Confluence page, or **appends content to an existing page** if a page with the same title already exists in the target space. The tool first searches the space for a page matching the title exactly. If found, it fetches the existing body, concatenates the new content onto it, and PUTs the full updated body back. If not found, it POSTs a new page. Content must be provided in **Confluence storage format (XHTML)** — the same format returned by the reader tool.

---

## Secrets & Configuration

| Value | Where it lives | Notes |
|-------|-----------------|-------|
| `api_key` | **AWS Secrets Manager** — secret `aava-secret-manager-confluence-credentials`, key `api_key` | Atlassian API token. Never appears in the code. Shared with `tool-L1-confluence-reader`. |
| `user_email` | **AWS Secrets Manager** — same secret, key `user_email` | Atlassian account email used for HTTP Basic Auth. |
| `title`, `content`, `space_key`, `base_url` | Supplied by the caller at call time | Not credentials — passed as parameters on every call (see Parameters below). |

> Every value that must be reviewed before deploying this tool to a new environment or client — `SECRET_NAME` and `region_name` on the `AWSSecretReaderPodIdentity` class — is tagged `SETUP-REQUIRED:` directly in `tool-L1-confluence-writer-secrets-manager.py`. Search the file for that tag to find them all in one pass.

The production tool (`tool-L1-confluence-writer-secrets-manager.py`) retrieves its credentials at import time:

```python
reader = AWSSecretReaderPodIdentity()   # SECRET_NAME = "aava-secret-manager-confluence-credentials"
secrets = reader._run()
api_key = secrets.get("api_key")
user_email = secrets.get("user_email")
```

`AWSSecretReaderPodIdentity` calls `boto3.client("secretsmanager", region_name="us-east-1").get_secret_value(...)` — no credential is stored in this file; access is granted via the runtime's pod identity.

> `tool-L1-confluence-writer.py` (without the `-secrets-manager` suffix) is kept in this folder only for local debugging. It is **not used in production** — note that this particular debug copy still contains a live-looking Atlassian API token hardcoded in it rather than a placeholder, so treat it as sensitive and do not commit further copies of it.

---

## Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | string | ✓ | Title of the page to create or append to. **Exact-match, case-sensitive** against existing pages in the space. |
| `content` | string | ✓ | Body content in **Confluence storage format (XHTML)**. See below for format details and examples. Plain text or Markdown will be stored literally and render incorrectly. |
| `space_key` | string | ✓ | Key of the target Confluence space. For team spaces: alphanumeric (e.g. `"ENG"`). For personal spaces: a hashed key (e.g. `"~7120208dde8969e5854fbfbe0185df21567c33"`). |
| `base_url` | string | ✓ | Base URL of the Confluence instance **including `/wiki`** (e.g. `"https://your-domain.atlassian.net/wiki"`). |

---

## ⚠️ Input Format — Confluence Storage Format (XHTML)

The `content` parameter **must** be valid Confluence storage format. This is a proprietary XHTML dialect. Passing plain text or Markdown will cause it to be stored literally — it will appear as raw markup in the Confluence page.

### Supported tags

| Purpose | Tags |
|---------|------|
| Paragraphs | `<p>text</p>` |
| Headings | `<h1>` through `<h6>` |
| Bullet list | `<ul><li>item</li></ul>` |
| Numbered list | `<ol><li>item</li></ol>` |
| Table | `<table><tr><th>Head</th></tr><tr><td>Cell</td></tr></table>` |
| Bold / italic | `<strong>bold</strong>`, `<em>italic</em>` |
| Code block | `<ac:structured-macro ac:name="code"><ac:plain-text-body><![CDATA[code here]]></ac:plain-text-body></ac:structured-macro>` |
| Info panel | `<ac:structured-macro ac:name="info"><ac:rich-text-body><p>text</p></ac:rich-text-body></ac:structured-macro>` |
| Cross-page link | `<ac:link><ri:page ri:content-title="Page Name"/></ac:link>` |

### Example valid content string

```xml
<h2>Sprint 42 Summary</h2>
<p>Velocity: <strong>34 points</strong>.</p>
<ul>
  <li>Feature A shipped</li>
  <li>Bug B resolved</li>
</ul>
<ac:structured-macro ac:name="info">
  <ac:rich-text-body><p>Retrospective scheduled for Friday.</p></ac:rich-text-body>
</ac:structured-macro>
```

---

## Returns

### On successful append (page already existed)

```
Content appended to existing page.
confluence_page_id: 425985
base_url: https://mycompany.atlassian.net/wiki
space_key: ENG

Page Title: Sprint 42 Notes
Version: 4
URL: https://mycompany.atlassian.net/wiki/spaces/ENG/pages/425985/Sprint+42+Notes
```

### On successful create (new page)

```
Page created successfully.
confluence_page_id: 425986
base_url: https://mycompany.atlassian.net/wiki
space_key: ENG

Page Title: Sprint 42 Notes
Version: 1
URL: https://mycompany.atlassian.net/wiki/spaces/ENG/pages/425986/Sprint+42+Notes
```

### On error

```
Error writing to Confluence page: <exception message>
Details: <HTTP response body from Confluence>
```

---

## Standalone tool calling

```python
from tool_L1_confluence_writer_secrets_manager import ConfluencePageCreator

tool = ConfluencePageCreator()

# Create a new page
result = tool._run(
    title="Sprint 42 Notes",
    content="<h2>Goals</h2><p>Complete auth module.</p>",
    space_key="ENG",
    base_url="https://mycompany.atlassian.net/wiki"
)

# Run again with the same title -> appends to the existing page instead
result = tool._run(
    title="Sprint 42 Notes",
    content="<h2>Outcomes</h2><p>Auth module shipped.</p>",
    space_key="ENG",
    base_url="https://mycompany.atlassian.net/wiki"
)
```

## Calling tool in agent

`title` and `content` are what changes per call; `space_key` and `base_url` are usually specific to your Confluence instance and should be told to the agent as fixed values:

```
title = {{page_title}}
content = the full Confluence-storage-format (XHTML) body to write, VERBATIM
space_key = ENG
base_url = https://your-domain.atlassian.net/wiki
```

---

## API Workflow

| Step | API Call | Purpose |
|------|----------|---------|
| 1 | `GET {base}/rest/api/content?spaceKey=...&title=...&expand=body.storage,version` | Search for existing page by exact title |
| 2a | `PUT {base}/rest/api/content/{page_id}` | Update (append) if page found — must include `version.number = current + 1` |
| 2b | `POST {base}/rest/api/content` | Create new page if not found |

---

## Error Handling

| Error | Cause | Behaviour |
|-------|-------|-----------|
| `401 Unauthorized` | Invalid or expired API token | `RequestException` caught; returns error string with HTTP detail |
| `403 Forbidden` | User lacks write permission to the space | Same as above |
| `404 Not Found` | `space_key` or `page_id` invalid | Returns error string with HTTP detail |
| `400 Bad Request` | Malformed XHTML content or invalid JSON payload | Returns error string with Confluence's error body in `Details:` |
| `409 Conflict` | Version mismatch (optimistic lock failure) | Returns error string — see concurrency caveat below |
| `429 Rate Limited` | Too many API requests | Returns error string; no automatic retry |
| Network / timeout | Confluence instance unreachable | Caught by `RequestException`; returns error string |

---

## Known Issues & Nuances

### 1. Append is a full read-modify-write (not an atomic append)
Confluence has no "append" endpoint. The tool:
1. Reads the existing page body (XHTML)
2. Concatenates `<p></p>` + new content onto the end
3. PUTs the entire combined body back

This means the **whole page is rewritten on every append**. If the existing page has complex macros or structured content, there is a small risk of subtle rendering changes.

### 2. Version bumping is mandatory — 409 Conflict on stale version
Confluence uses **optimistic locking**. Every PUT must supply `version.number` as exactly `current_version + 1`. The tool reads the current version from the search response and increments it. If the version has changed between the search and the PUT (e.g. a manual edit in the browser), the PUT will **fail with HTTP 409 Conflict**.

### 3. Concurrency hazard — parallel runs will conflict
Because the flow is read → increment version → write, **two agents running against the same page title simultaneously** will both read the same current version. One PUT will succeed; the other will fail with 409. Never run two instances of this tool targeting the same page in parallel.

### 4. Title matching is exact and case-sensitive
The search uses `title=<exact string>`. `"Sprint Notes"` and `"sprint notes"` are treated as **different pages**. Confluence itself is not case-sensitive for page titles, but the REST API search parameter is used with `=` exact match here — ensure the calling agent always passes the canonical casing.

### 5. Content is not validated before submission
The tool sends whatever string is in `content` directly to the Confluence API. **Malformed XHTML** (unclosed tags, invalid attribute values, illegal characters) may:
- Cause a `400 Bad Request` from Confluence
- Be silently accepted but render incorrectly in the page editor
- Strip certain unsupported tags without warning

### 6. Append separator is a single empty paragraph
The separator between the existing body and the new content is `<p></p>` (an empty paragraph). This produces a small visual gap. If you need a horizontal rule or a labelled section, include it explicitly in the `content` parameter.

### 7. No HTTP timeout on any request
None of the three `requests` calls (`GET`, `PUT`, `POST`) have a `timeout=` argument. All three can hang indefinitely.

---

## Security Notes

- `api_key` and `user_email` are retrieved from AWS Secrets Manager at import time — never hardcoded, never logged.
- Credentials are passed via HTTP Basic Auth over HTTPS — never logged by the tool.
- The HTTP response body from Confluence (which may contain internal error detail) is included in the error return string on failure.

## Resilience

| Concern | Current state | Recommendation |
|---------|--------------|----------------|
| Timeout | ❌ None on GET / PUT / POST | Add `timeout=30` to all three calls |
| Retry | ❌ No retry logic | Add retry with backoff for 429/5xx; **do NOT retry 409** (version conflict needs re-read) |
| Concurrency | ❌ Race condition on same-title pages | Serialize writes to the same page; or re-read version before PUT |
| Content validation | ❌ No XHTML validation | Validate content is well-formed XML before submitting |
| 409 handling | ❌ Returned as error string | Consider re-reading the page and retrying once on 409 |
