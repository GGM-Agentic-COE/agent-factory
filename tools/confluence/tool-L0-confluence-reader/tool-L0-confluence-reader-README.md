# tool-L0-confluence-reader

## 1. Executive summary

You give the tool the numeric ID of a Confluence page. It fetches the page through the Confluence REST API, converts the body from Confluence storage format (XHTML) to Markdown, and returns the page title as a `#` heading followed by the Markdown body.

**Key points** (details in [Section 6](#6-nuances)):

- Output is always Markdown. There is no parameter to choose the format and no way to get the raw XHTML ([6.1](#61-output-is-always-markdown)).
- Code inside Confluence code macros, images and other macro content is not returned ([6.2](#62-what-the-markdown-conversion-keeps-and-drops)).
- Long pages are cut at 80,000 characters ([6.3](#63-long-pages-are-truncated)).
- The Confluence site and credentials come from the secret, so you pass only the page ID ([6.4](#64-pass-the-page-id-only)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`page_id`**
```
425985
```

### 2.2 Calling the tool in an agent

`page_id` changes on every call. The Confluence site address, account email and API token are read from the secret, so the agent passes none of them.

```
page_id = {{confluence_page_id}}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `page_id` | str | ✓ | The numeric ID of the Confluence page, e.g. `425985`. It is the number in the page URL after `/pages/`. Passed as-is into the request path; not validated. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Confluence API token. Sent as the HTTP Basic Auth password. |
| Account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Email of the Atlassian account that owns the token. Sent as the HTTP Basic Auth user name. |
| Confluence base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `confluence_base_url` | Address the REST path is appended to, e.g. `https://<your-domain>.atlassian.net/wiki`. A trailing `/` is removed. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the name of your secret. The pod's IAM role needs `secretsmanager:GetSecretValue` on it. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| Secret key names | Code — module level | `SETUP-REQUIRED:` the keys `api_key`, `id` and `confluence_base_url` must match the keys in the secret JSON. |
| `max_chars` | Code — `ConfluencePageReader` | Defaults to `80_000`. Markdown longer than this is truncated. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-confluence-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `os` | stdlib | Imported; not used |
| `re` | stdlib | Pattern matching during Markdown conversion |
| `json` | stdlib | Parsing the secret string |
| `html.parser` | stdlib | `HTMLParser`, base of the storage-format-to-Markdown converter |
| `typing` | stdlib | Type hints |
| `requests` | `requests` | Confluence REST API call |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |

---

## 6. Nuances

### 6.1 Output is always Markdown
The tool requests the page body in storage format (`expand=body.storage`) and always converts it to Markdown before returning it. You do not need to ask for Markdown, and there is no parameter to switch it off. The output starts with `# <page title>`, followed by the converted body. **Do:** treat the result as Markdown; if you need the exact XHTML (for example to edit and write the page back), this tool cannot provide it.

### 6.2 What the Markdown conversion keeps and drops
The converter handles these elements:

- Headings `h1`–`h6` become `#`–`######`.
- Paragraphs, `div` and `blockquote` become blank-line-separated text. Block quotes are not marked with `>`.
- Line breaks become Markdown hard breaks.
- Bulleted and numbered lists both become `- ` bullets. Nested lists are indented two spaces per level.
- Tables become pipe tables. The first row is the header if it contains `th` cells; otherwise an empty header row is added. Whitespace inside cells is collapsed to single spaces.
- Links (`<a href>`) become `[text](url)`.
- Bold, italic and inline code become `**`, `*` and backticks.
- `<pre>` blocks become fenced code blocks. If the block already contains Markdown (a code fence, a pipe-table line or a `#` heading line), it is passed through unchanged instead.
- A macro's `title` parameter (for example an expand or code macro title) becomes a `### <title>` heading, and the macro's rich-text body is kept.

The converter drops these:

- Every other macro parameter, such as a code macro's language.
- Script and style content.
- CDATA bodies. This includes the code inside Confluence code macros and the text of internal page links.
- Images and attachments.

**Do:** if the page keeps important content in code macros, internal links or images, check the original page as well. Do not rely on the Markdown alone.

### 6.3 Long pages are truncated
If the converted Markdown is longer than 80,000 characters, only the first 80,000 are returned, followed by `_[Truncated.]_`. **Do:** check for `_[Truncated.]_` at the end of the output, and split very large pages into child pages if the full text is needed.

### 6.4 Pass the page ID only
The Confluence site, email and token are read from the secret when the tool module is loaded. `page_id` is placed straight into the request path, so a page URL, title or space key in its place gives an HTTP error. **Do:** pass only the numeric ID, e.g. `425985`.

### 6.5 Empty pages return a short placeholder
If the page body is empty, the tool returns the title, the word `url` joined directly to the configured base URL, and a note that the page is empty. It does not return an error. **Do:** check for `has an empty body.` before using the result.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (once, when the module is loaded) | Read the API token, email and base URL |
| 2 | `GET {base_url}/rest/api/content/{page_id}?expand=body.storage` | Fetch the page title and storage-format body |
| 3 | Local conversion (no API call) | Convert storage-format XHTML to Markdown |

### 7.2 Returns

**Success**
```
# <page title>
 
 <page body as Markdown>
```

When the Markdown is longer than 80,000 characters, it ends with:
```
_[Truncated.]_
```

When the page body is empty:
```
# <page title>

url<base_url>

_(Page <page_id> has an empty body.)_
```

**Error**
```
Error reading Confluence page: <requests exception>
Error converting page to Markdown: <ExceptionType>: <detail>
```

When the module is loaded, the secret read can raise:
```
RuntimeError: Error retrieving secret: <detail>
RuntimeError: Unexpected error: <detail>
RuntimeError: Secret '<SECRET_NAME>' is missing keys: [<names>]
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Error reading Confluence page: 401 Client Error` | Token rejected, or the email does not match the token | Check `api_key` and `id` in the secret |
| `Error reading Confluence page: 403 Client Error` | The account cannot view the page | Grant the account view permission on the space or page |
| `Error reading Confluence page: 404 Client Error` | Page ID does not exist, is not numeric, or is not visible to the account | Check `page_id` and permissions |
| `Error reading Confluence page: <connection or timeout error>` | Base URL unreachable or no response within 30 seconds | Check `confluence_base_url` and network access from the pod |
| `Error converting page to Markdown: …` | The storage-format body could not be parsed | Read the page in Confluence directly |
| `RuntimeError: Error retrieving secret: …` | Secret missing, wrong region, or the pod role lacks `secretsmanager:GetSecretValue` | Check `SECRET_NAME`, the region and the Pod Identity association |
| `RuntimeError: Secret '…' is missing keys: […]` | The secret does not contain one of the three keys. The message uses the internal names `api_key`, `user_email` and `base_url`; these correspond to the secret keys `api_key`, `id` and `confluence_base_url` | Add the missing key to the secret |

### 7.3 Known limitations

- Read-only. It cannot create, edit or delete pages.
- One page per call. It does not read child pages, comments, labels, attachments or version history.
- Pages are found by ID only. There is no lookup by title, space or URL.
- Output is Markdown only. There is no option for raw storage XHTML, plain text or HTML.
- The conversion drops code-macro code, internal link text, images and macro parameters other than `title` (see [6.2](#62-what-the-markdown-conversion-keeps-and-drops)).
- No parameter to change the 80,000-character limit.

### 7.4 Security & resilience

**Security**
- The email and API token are read from AWS Secrets Manager through Pod Identity and sent only as HTTP Basic Auth. They are not returned or logged.
- Error strings include the raw `requests` exception text, which can contain the request URL and page ID.
- The empty-page message includes the configured Confluence base URL.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | 30 seconds on the page request. No explicit timeout on the Secrets Manager call. | Keep 30 seconds. Add a `botocore` config with timeouts for the secret read. |
| Retry | None. One attempt, and any failure is returned. The secret is read once when the module loads and is not reloaded. | Retry on timeout, 429 and 5xx with exponential backoff. Reload the secret on a 401 so rotated tokens are picked up. |
| Concurrency | One request per call; no shared state between calls | No change needed |
| Input validation | `page_id` is not checked. Secret keys are checked for presence when the module loads. | Reject a non-numeric `page_id` before calling the API |
