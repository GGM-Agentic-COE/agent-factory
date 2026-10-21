# tool-L0-jira-reader

## 1. Executive summary

You give the tool one or more Jira issue keys. It fetches each issue and then walks down its child work items (children, their children, and so on) up to a set depth. It returns one clean JSON tree per key with title, status, plain-text description, labels, assignee, due date, reporter and the nested children.

**Key points** (details in [Section 6](#6-nuances)):

- `inputJSON` accepts several shapes: a dict, a list of keys, a JSON string, a comma-separated string or a single key. One `key` returns an object; `keys` returns an array ([6.1](#61-input-shape-decides-output-shape)).
- Children are walked up to `maxDepth` levels (default 5). `maxDepth: 0` does not mean "no children"; use `includeChildren: false` ([6.2](#62-depth-and-the-includechildren-switch)).
- Descriptions come back as plain text, and only a fixed set of fields is returned ([6.3](#63-descriptions-are-plain-text-and-fields-are-fixed)).
- A child lookup that fails is silently treated as "no children" ([6.4](#64-failures-are-reported-per-issue-or-hidden)).

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

**`inputJSON`**
```
{"key": "PROJ-101", "maxDepth": 2, "includeChildren": true}
```

`baseUrl`, `userEmail` and `apiToken` are omitted from the example. Leave them out so the values from AWS Secrets Manager are used.

### 2.2 Calling the tool in an agent

The issue key or keys change on every call. `maxDepth` and `includeChildren` are usually fixed for the workflow. The Jira site and credentials come from AWS Secrets Manager, so the agent passes none of them.

```
inputJSON = {"keys": {{issue_keys}}, "maxDepth": 3, "includeChildren": true}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputJSON` | Dict[str, Any] | ✓ | Request payload with the keys below. Before validation a list becomes `{"keys": [...]}`, a JSON string is parsed, a comma-separated string becomes `keys`, and any other string becomes `key`. |
| `inputJSON.key` | str |  | One Jira issue key, e.g. `PROJ-101`. Required when `keys` is not given. |
| `inputJSON.keys` | List[str] |  | Several issue keys, e.g. `["PROJ-101", "PROJ-110"]`. Takes precedence over `key`. A plain string is treated as one key. |
| `inputJSON.maxDepth` | int |  | Levels of children to walk below each requested issue. Default `5`. `0`, `null` or omitted all mean `5`. |
| `inputJSON.includeChildren` | bool |  | Default `true`. `false` returns only the requested issues with empty `children`. Any truthy value (including the string `"false"`) counts as `true`. |
| `inputJSON.baseUrl` | str |  | Jira site URL, e.g. `https://<your-domain>.atlassian.net`. Overrides `base_url` from the secret. A trailing `/` is removed. |
| `inputJSON.userEmail` | str |  | Atlassian account email. Overrides `id` from the secret. |
| `inputJSON.apiToken` | str |  | Atlassian API token. Overrides `api_key` from the secret. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| Jira base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `base_url` | Site root, e.g. `https://<your-domain>.atlassian.net`. Used when `baseUrl` is not passed. |
| Jira account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Basic-auth user. Used when `userEmail` is not passed. |
| Jira API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Basic-auth password. Used when `apiToken` is not passed. If both are empty, the `JIRA_API_TOKEN` environment variable is used. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with your secret's name. The secret must be a JSON object. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| AWS credentials | Pod Identity (IAM role on the pod) | No AWS keys in code. The role needs `secretsmanager:GetSecretValue` on the secret. |
| `DEFAULT_MAX_DEPTH` | Code — module constant | Defaults to `5`. Depth used when `maxDepth` is not given. |
| `PAGE_SIZE` | Code — module constant | Defaults to `100`. Children fetched per search page. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-jira-reader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `os` | stdlib | `JIRA_API_TOKEN` environment fallback |
| `json` | stdlib | Parsing the secret and string input; building the output |
| `requests` | `requests` | Jira REST calls |
| `requests.auth` | `requests` | `HTTPBasicAuth` |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`, `field_validator`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` |

---

## 6. Nuances

### 6.1 Input shape decides output shape
If you pass a single `key` (or a bare key string), the result is one JSON object. If you pass `keys`, a list or a comma-separated string, the result is a JSON array, even for one key. If both `key` and `keys` are present, `keys` wins. **Do:** always pass `keys` as a list when the agent parses the output, so the shape is always an array.

### 6.2 Depth and the includeChildren switch
The requested issue is depth 0 and children are fetched while depth is below `maxDepth`, so the default walks five levels down. `maxDepth` of `0` is treated as "not set" and becomes `5`. An issue already visited in the current tree is not expanded again. **Do:** use `includeChildren: false` to get only the requested issues, and keep `maxDepth` small (1 to 3) for epics with many descendants, because every node adds a search call and output size.

### 6.3 Descriptions are plain text and fields are fixed
Jira's rich-text description (ADF) is flattened to plain text. Paragraphs, headings, bullet lists (`- `), numbered lists (`1. `) and line breaks are kept; bold, links, tables, mentions and other formatting are reduced to their text or dropped. Each node returns only `issue_id`, `title`, `status`, `description`, `labels`, `assignee`, `due_date`, `reporter`, `child_work_item_ids` and `children`. **Do:** use another tool if you need comments, attachments, priority or custom fields.

### 6.4 Failures are reported per issue, or hidden
If a requested issue cannot be fetched, its place in the output is `{"issue_id": "<key>", "error": "HTTP <status>", "detail": "<Jira response>"}` and the other keys are still returned. If a child search fails (permissions, bad key), that issue is shown with no children and no error. **Do:** check each item for an `error` field, and do not treat an empty `children` list as proof that an issue has no children.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (once, at module import) | Read `base_url`, `id` and `api_key` |
| 2 | `GET {base_url}/rest/api/3/issue/{key}?fields=*all` (per requested key) | Fetch the root issue |
| 3 | `POST {base_url}/rest/api/3/search/jql` with `parent = "<key>" ORDER BY created ASC`, `maxResults` 100, paged by `nextPageToken` (per expanded node) | Fetch child issues, recursively up to `maxDepth` |

### 7.2 Returns

**Success**
```
{
  "issue_id": "<KEY>",
  "title": "<summary>",
  "status": "<status name>",
  "description": "<plain text>",
  "labels": ["<label>", ...],
  "assignee": "<display name> | null",
  "due_date": "<YYYY-MM-DD> | null",
  "reporter": "<display name> | null",
  "child_work_item_ids": ["<child KEY>", ...],
  "children": [ { <same shape> }, ... ]
}
```
With `keys`, the output is an array of these objects. A root issue that failed appears as:
```
{"issue_id": "<key>", "error": "HTTP <status>", "detail": "<Jira response body>"}
```

**Error**
```
Fatal error: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Fatal error: provide 'key' (string) or 'keys' (list).` | Neither `key` nor `keys` was supplied | Pass at least one issue key |
| `Fatal error (network): <detail>` | Connection or DNS failure reaching Jira | Check `base_url` and network access from the pod |
| `Fatal error: <detail>` | Any other exception, e.g. a non-numeric `maxDepth` | Check the input values |
| `"error": "HTTP 401"` / `"HTTP 403"` | Wrong email or token, or no permission on the issue | Check `id` and `api_key` in the secret and the account's project access |
| `"error": "HTTP 404"` | Issue key does not exist or is not visible | Check the key and its project |
| `RuntimeError: Error retrieving secret: <detail>` / `RuntimeError: Unexpected error: <detail>` | Secret could not be read when the module was imported; the tool does not load | Check `SECRET_NAME`, the region, the Pod Identity association and `secretsmanager:GetSecretValue` |

### 7.3 Known limitations

- Read-only. It cannot create, update, transition or delete issues.
- Walks parent-child links only. Issue links (blocks, relates to) and sub-task relationships outside the `parent` field are not followed.
- Returns a fixed set of fields. No option to request comments, attachments, priority, components or custom fields.
- No JQL search parameter. Issues are selected by key only.
- Descriptions are returned as plain text only; the original rich formatting is not available.

### 7.4 Security & resilience

**Security**
- Jira credentials are read from AWS Secrets Manager through Pod Identity; none are stored in code. They are read once when the module is imported.
- `baseUrl`, `userEmail` and `apiToken` in the input override the secret. If `baseUrl` is overridden without the other two, the stored credentials are sent to that URL.
- The tool prints `GET <key> -> <status>` to stdout for each requested issue. Credentials are not printed. Error details include the raw Jira response body.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | None; `requests` calls have no timeout | Pass `timeout=(5, 30)` to every `requests` call |
| Retry | None; a failed child search is treated as a leaf | Retry 429 and 5xx with backoff, honouring `Retry-After` |
| Concurrency | Issues and children are fetched one at a time | Use a bounded thread pool per tree level for large hierarchies |
| Input validation | Input is coerced to a dict; key format, `maxDepth` range and `baseUrl` host are not checked | Validate key format, cap `maxDepth`, and restrict `baseUrl` to your Jira site |
