# tool-L0-confluence-writer

## 1. Executive summary

You give the tool a page title, the body content in Markdown, and where to write it (a space key or a folder). It converts the Markdown to Confluence storage format, then either creates a new page or, if a page with that title already exists in the space, appends the content to the bottom of it. It returns a short confirmation with the page ID, space key, title and new version number.

**Key points** (details in [Section 6](#6-nuances)):

- Write the content in Markdown. It is converted automatically, and storage-format XHTML is also accepted unchanged ([6.1](#61-content-is-markdown-converted-automatically)).
- An existing page with the same title is appended to, never overwritten ([6.2](#62-same-title-means-append-not-overwrite)).
- `space_key` also accepts a folder ID or `SPACEKEY/folderID` to write inside a folder ([6.3](#63-choosing-where-the-page-goes)).
- If the move into a folder fails, the tool still reports success. The output contains no page URL ([6.4](#64-a-failed-folder-move-is-not-reported)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`title`**
```
Sprint 42 Release Notes
```

**`content`**
````
## Summary
Release **42** ships the new export feature.

| Item | Owner |
|------|-------|
| Export API | Platform team |

- Fixed login timeout
- Updated dependencies

```python
print("hello")
```
````

**`space_key`**
```
ENG/123456789
```

### 2.2 Calling the tool in an agent

`title` and `content` change on every call. `space_key` is usually fixed for a workflow (a space or a folder) but can be passed per call. The Confluence site and credentials come from the secret.

```
title = {{page_title}}
content = {{markdown_body}}
space_key = {{space_key_or_SPACEKEY/folderID}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `title` | str | ✓ | Title of the page. If a page with this exact title exists in the target space, the content is appended to it. Otherwise a new page is created. |
| `content` | str | ✓ | Body content in Markdown: headings, paragraphs, bulleted and numbered lists (one nested level), pipe tables, fenced code blocks, horizontal rules, links, `**bold**`, `*italic*` and inline code. Converted to Confluence storage format automatically. Content that starts with `<p>`, `<h1>`–`<h6>`, `<table>`, `<ul>`, `<ol>`, `<div>` or `<pre>` is treated as storage-format XHTML and passed through unchanged. |
| `space_key` | str | ✓ | Where to write. A space key (e.g. `ENG`) writes at the root of the space. `SPACEKEY/folderID` (e.g. `ENG/123456789`) writes inside that folder. A digits-only folder ID (e.g. `123456789`) is looked up to find its space. A digits-only value that matches no content is used as a numeric space key. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Confluence API token, sent as the HTTP Basic Auth password. Needs the scopes `write:confluence-content`, `read:confluence-content.all` and `read:confluence-space.summary`, plus permission to add pages in the space. |
| Account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Email of the Atlassian account that owns the token. Sent as the HTTP Basic Auth user name. |
| Confluence base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `confluence_base_url` | Address the REST paths are appended to. For scoped API tokens, use the `https://api.atlassian.com/ex/confluence/<cloudId>/wiki` form. A trailing `/` is removed. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of your secret. The pod's IAM role needs `secretsmanager:GetSecretValue` on it. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| Secret key names | Code — module level | `SETUP-REQUIRED:` the keys `api_key`, `id` and `confluence_base_url` must match the keys in the secret JSON. |
| `_TIMEOUT` | Code — module level | Defaults to `30` seconds for every Confluence request. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-confluence-writer.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `os` | stdlib | Imported; not used |
| `re` | stdlib | Markdown parsing and target resolution |
| `json` | stdlib | Parsing the secret string |
| `typing` | stdlib | Type hints |
| `requests` | `requests` | Confluence REST API calls |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 Content is Markdown, converted automatically
The tool converts Markdown in `content` to Confluence storage format before writing. Supported elements:

- Headings `#`–`######`.
- Paragraphs. Consecutive lines are joined into one paragraph.
- Bulleted (`-`, `*`, `+`) and numbered (`1.` or `1)`) lists. Indented items become one level of bulleted sub-items.
- Pipe tables. The first row is the header and the separator row is dropped.
- Fenced code blocks using ```` ``` ```` or `~~~`. These become Confluence code macros, with syntax highlighting for known languages such as python, java, javascript, typescript, bash, sql, json, yaml, xml, go and csharp. Unknown languages get a code macro with no language.
- Horizontal rules (`---`, `***`, `___`).
- Inline elements: `[text](url)` links, `**bold**`, `*italic*`, inline code and backslash escapes.

A whole body wrapped in a ```` ```markdown ```` or ```` ```md ```` fence is unwrapped first. If content starts with a storage-format tag (`<p>`, `<h1>`–`<h6>`, `<table>`, `<ul>`, `<ol>`, `<div>`, `<pre>`), it is passed through unchanged. **Do:** send plain Markdown. Do not mix in HTML tags, because inside Markdown they are escaped and appear as literal text.

### 6.2 Same title means append, not overwrite
Before writing, the tool searches the target space for a page with exactly that title. If it finds one, it adds an empty paragraph and then the new content after the existing body, and saves the page as the next version. The existing content is never replaced or deleted. **Do:** use a unique title (for example, include a date) when you want a new page, and reuse the title only when you intend to add to the page.

### 6.3 Choosing where the page goes
`space_key` decides the location:

| Value | Result |
|-------|--------|
| `ENG` | Root of space `ENG` |
| `ENG/123456789` | Inside folder `123456789` in space `ENG`. No lookup is made. |
| `123456789` | The tool looks up the ID (by content ID, then a CQL `id=` search) to find its space, then writes inside that folder. If nothing matches, the value is used as a numeric space key. |

The title search covers the whole space, not just the folder. An existing page with the same title elsewhere in the space is appended to where it is, and is not moved. **Do:** use `SPACEKEY/folderID` when you know both values, because it skips the lookup.

### 6.4 A failed folder move is not reported
A new page is first created at the root of the space and then moved into the folder. If the move fails (for example, because of a missing permission or a wrong folder ID), the page stays at the space root. The tool still returns `Page created successfully.` with the `folder_id` line, and it returns no page URL. **Do:** after writing to a folder for the first time, confirm in Confluence that the page landed in the folder.

### 6.5 Parallel writes to the same page can conflict
Each append reads the current version and saves version + 1. Two calls appending to the same title at the same time can collide, and one fails with HTTP 409. **Do:** run appends to the same page one after another.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (once, when the module is loaded) | Read the API token, email and base URL |
| 2 | Local conversion (no API call) | Convert Markdown to storage format |
| 3 | `GET {base_url}/rest/api/content/{id}?expand=space` (digits-only `space_key` only) | Find the space of a folder ID |
| 4 | `GET {base_url}/rest/api/content/search?cql=id={id}&expand=space` (only if step 3 finds no space) | Fallback lookup of the folder's space |
| 5 | `GET {base_url}/rest/api/content?spaceKey=…&title=…&expand=body.storage,version` | Check whether the page exists and read its body and version |
| 6a | `PUT {base_url}/rest/api/content/{page_id}` (page exists) | Save existing body + new content as version + 1 |
| 6b | `POST {base_url}/rest/api/content` (page does not exist) | Create the page at the space root |
| 7 | `PUT {base_url}/rest/api/content/{new_id}/move/append/{folder_id}` (new page with a folder only) | Move the new page into the folder |

### 7.2 Returns

**Success**

Appended to an existing page:
```
Content appended to existing page.
confluence_page_id: <page_id>
space_key: <space_key>
folder_id: <folder_id>        (only when a folder was resolved)

Page Title: <title>
Version: <new_version>
```

New page created:
```
Page created successfully.
confluence_page_id: <page_id> 
 space_key: <space_key>
folder_id: <folder_id>        (only when a folder was resolved)

Page Title: <title>
Version: 1 
```

**Error**
```
Error writing to Confluence page: <requests exception>
Details: <HTTP response body>
Hint: <shown for 401 and 403 only>
```
```
Error in Confluence Page Creator: <ExceptionType>: <detail>
```

When the module is loaded, the secret read can raise:
```
RuntimeError: Error retrieving secret: <detail>
RuntimeError: Unexpected error: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `401 Client Error` + `Hint: 401 means the token was rejected…` | Wrong email or token, or `confluence_base_url` is not the `api.atlassian.com/ex/confluence/<cloudId>/wiki` address required for scoped tokens | Check `id`, `api_key` and `confluence_base_url` in the secret |
| `403 Client Error` + `Hint: 403 means a missing scope or Confluence permission…` | Token lacks `write:confluence-content`, `read:confluence-content.all` or `read:confluence-space.summary`, or the account cannot add pages in the space | Add the scopes and space permission |
| `404 Client Error` | Space key does not exist or is not visible to the account | Check `space_key` |
| `409 Client Error` | Another update to the same page happened between read and write | Retry the call, and avoid parallel appends to one page |
| `400 Client Error` | Confluence rejected the body (for example, malformed XHTML passed through) | Send Markdown, or fix the XHTML |
| `Error in Confluence Page Creator: AttributeError: …` | A secret key is missing, so the base URL is empty | Add `api_key`, `id` and `confluence_base_url` to the secret |
| `RuntimeError: Error retrieving secret: …` | Secret missing, wrong region, or the pod role lacks `secretsmanager:GetSecretValue` | Check `SECRET_NAME`, the region and the Pod Identity association |

### 7.3 Known limitations

- Cannot overwrite, replace or delete page content. It only creates pages or appends to them.
- Appends only to the bottom of a page. There is no way to insert at a position or under a heading.
- No parent-page option. Pages go to a space root or into a folder only.
- Does not return the page URL.
- Markdown support is limited to the elements in [6.1](#61-content-is-markdown-converted-automatically). Images, `_underscore_` italics, strikethrough, block-quote styling, task lists and lists nested more than one level are not converted.
- Cannot attach files, add labels or set page properties.
- An existing page found by title is not moved into the requested folder.

### 7.4 Security & resilience

**Security**
- The email and API token are read from AWS Secrets Manager through Pod Identity and sent only as HTTP Basic Auth. They are not returned or logged.
- On failure, the error string includes the raw exception text and the HTTP response body from Confluence, which can contain URLs, IDs and space details.
- Text in Markdown content is HTML-escaped. Storage-format content is passed through without validation.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 seconds on each Confluence request (up to five per call). No explicit timeout on the Secrets Manager call. | Keep 30 seconds per request. Add a `botocore` config with timeouts for the secret read. |
| Retry | None. Any failure is returned. The secret is read once when the module loads and is not reloaded. | Retry on timeout, 429 and 5xx with backoff. On 409, re-read the version and retry the append once. |
| Concurrency | Read-modify-write with optimistic locking. Parallel appends to one page can fail with 409. | Serialise writes per page title |
| Input validation | `title` and `space_key` are not validated. The secret keys are not checked for presence. A failed folder move is not reported. | Check the secret keys at load time, include the move warning and page URL in the output, and reject empty titles |
