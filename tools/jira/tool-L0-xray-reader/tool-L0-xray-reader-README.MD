# tool-L0-xray-reader

## 1. Summary

You give the tool one or more Jira issue keys. It fetches each Jira issue, retrieves Xray Test data according to the Jira issue type, and recursively walks child work items through Jira's `parent` relationship up to the configured depth. Each issue node contains Jira metadata, the Xray retrieval result, and any discovered child issue nodes.

For Jira issue type `Test`, the tool performs an exact Xray Test lookup. For `Story` and `Requirement`, it retrieves Tests linked through Xray's `requirementTests()` coverage function. Other issue types receive `UNSUPPORTED_ISSUE_TYPE`; the tool does not infer a relationship. A single `key` input returns one JSON object. A `keys` input, top-level list, or comma-separated string returns a JSON array.

**Key points** (details in [Section 6](#6-nuances)):

- `inputJSON` accepts a dictionary, list, JSON string, comma-separated string, single key, or supported issue object; input shape determines whether the result is an object or array ([6.1](#61-input-shape-and-output-shape)).
- Child traversal defaults to five levels. `maxDepth: 0` and `null` use the default; `includeChildren: false` disables traversal ([6.2](#62-child-traversal-controls)).
- Xray lookup is selected from the Jira issue type: exact lookup for `Test`, coverage lookup for `Story` and `Requirement`, and an explicit unsupported status for other types ([6.3](#63-xray-retrieval-by-jira-issue-type)).
- Root Jira failures and Xray failures are represented in the result; child-search failures are treated as leaf nodes ([6.4](#64-result-fields-and-failure-handling)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`inputJSON`**

```json
{
  "keys": [
    "E2ESFI-45",
    "E2ESFI-46",
    "E2ESFI-47"
  ],
  "maxDepth": 2,
  "includeChildren": true
}
```

The same parameter also accepts a single-key object:

```json
{
  "key": "E2ESFI-45"
}
```

### 2.2 Calling the tool in an agent

The agent supplies `inputJSON` on each call. The issue key or keys, `maxDepth`, and `includeChildren` are workflow values. Jira and Xray credentials and service endpoints are loaded or selected by the tool; the agent does not pass credentials, tokens, or base URLs.

```python
inputJSON = {
    "keys": {{jira_issue_keys}},
    "maxDepth": {{max_depth}},
    "includeChildren": {{include_children}}
}
```

For a single issue:

```python
inputJSON = {
    "key": {{jira_issue_key}},
    "maxDepth": {{max_depth}},
    "includeChildren": {{include_children}}
}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputJSON` | Any | ✓ | The only tool argument. Accepts a dictionary containing `key` or `keys`, a list of Jira keys or supported issue objects, a JSON string, a comma-separated Jira-key string, or a single Jira-key string. A dictionary may also contain `maxDepth` and `includeChildren`. If both `keys` and `key` are present and `keys` is not `null`, `keys` takes precedence. A string in `keys` is treated as one key. A single-key input returns one issue object; `keys`, list, and comma-separated inputs return an array. |

The dictionary properties below are values inside `inputJSON`; they are not separate CrewAI tool arguments.

| `inputJSON` property | Python type | Required | Default and accepted values |
|----------------------|-------------|----------|-----------------------------|
| `key` | `str` |  | One Jira issue key. Used when `keys` is absent or `null`. |
| `keys` | `str`, `list`, or `dict` |  | One Jira issue key or a list of keys/issue objects. Takes precedence over `key` when not `null`. A string is treated as one key. |
| `maxDepth` | `int`-convertible value |  | Default `5`. Omitted, `null`, or `0` means `5`. Negative values and booleans are rejected; other values are converted with `int()`. |
| `includeChildren` | Any value |  | Default `true`. Converted using Python `bool()` truthiness. Use the JSON boolean `false` to disable child traversal; the string `"false"` is truthy and enables traversal. |

Jira keys are trimmed and uppercased. The key validator uses the ASCII pattern `[A-Z][A-Z0-9_]*-[0-9]+` and rejects keys longer than 255 characters before Jira/Xray requests. Structured issue objects in `keys` may provide one of these fields: `key`, `jira_issue_id`, `jira_key`, `issue_key`, `issue_id`, or nested `jira_issue.key`.

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| Jira API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Used as the password in Jira HTTP Basic Authentication. |
| Jira account identifier | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Used as the username in Jira HTTP Basic Authentication. |
| Jira base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `base_url` or `jira_base_url` | `base_url` takes precedence. Whitespace and trailing `/` characters are removed. If neither `http://` nor `https://` is present, `https://` is added. |
| Xray client ID | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `xray_client_id` | Sent to the Xray authentication endpoint. |
| Xray client secret | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `xray_client_secret` | Sent to the Xray authentication endpoint. |
| Xray base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `xray_base_url`; otherwise `DEFAULT_XRAY_BASE_URL` | Whitespace and trailing `/` characters are removed. The selected URL must begin with `http://` or `https://`. |
| Secrets Manager secret identifier | Production file constant `SECRET_NAME` | Identifies the secret read by the tool. Do not pass it through `inputJSON`. |
| AWS region | Production file constant `AWS_REGION` | Selects the AWS Secrets Manager region. |
| Default traversal depth | Production file constant `DEFAULT_MAX_DEPTH` | Default is `5`; `maxDepth` values of omitted, `null`, or `0` use this value. |
| Page size | Production file constant `PAGE_SIZE` | Default is `100` for Jira child search and Xray GraphQL pagination. |
| Request timeout | Production file constant `REQUEST_TIMEOUT_SECONDS` | Default read timeout is `30` seconds. Requests use `(5, REQUEST_TIMEOUT_SECONDS)` for connect/read timeout. |
| Setup-required values | Production file | No `SETUP-REQUIRED:` markers are present in the production file. |

The AWS workload identity attached to the pod must permit `secretsmanager:GetSecretValue` for the secret named in `SECRET_NAME`.

Before deploying to another environment, configure the secret and review `SECRET_NAME`, `AWS_REGION`, `DEFAULT_XRAY_BASE_URL`, `DEFAULT_MAX_DEPTH`, `PAGE_SIZE`, and `REQUEST_TIMEOUT_SECONDS` in `xray_jira_reader_multi_v2.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `json` | `stdlib` | Parsing JSON input and secret content; serializing tool output and GraphQL errors. |
| `re` | `stdlib` | Jira issue-key pattern validation. |
| `typing` | `stdlib` | Type annotations for dictionaries, lists, optional values, tuples, and the CrewAI schema type. |
| `requests` | `requests` | Jira REST and Xray Cloud HTTP requests. |
| `pydantic` | `pydantic` | Defining the `inputJSON` argument schema with `BaseModel` and `Field`. |
| `crewai.tools` | `crewai` | `BaseTool` base class. |
| `boto3` | `boto3` | Creating the AWS Secrets Manager client. Imported inside credential loading. |
| `botocore.exceptions` | `botocore` | Handling AWS Secrets Manager `ClientError`. Imported inside credential loading. |

---

## 6. Nuances

### 6.1 Input shape and output shape

A dictionary with `key` returns one JSON object. A dictionary with `keys`, a top-level list, or a comma-separated string returns a JSON array, including when the array contains only one key. If both `key` and `keys` are present and `keys` is not `null`, `keys` takes precedence. A string supplied as the `keys` value is treated as one key; it is not split on commas. A JSON string is parsed first. Structured issue objects are accepted when they contain `key`, `jira_issue_id`, `jira_key`, `issue_key`, `issue_id`, or nested `jira_issue.key`. **Do:** pass `keys` as a list when downstream processing expects an array, and pass `key` when the downstream contract expects one object.

### 6.2 Child traversal controls

The requested root issue is depth `0`. The tool expands children while the current depth is less than `maxDepth`; the default therefore traverses five child levels. `maxDepth` values of `0`, `null`, and omitted all use the default depth `5`; `0` does not disable traversal. A visited-key set prevents an issue from being expanded more than once within one root tree. `includeChildren` is evaluated with Python truthiness, so the string `"false"` is truthy. **Do:** use the JSON boolean `false` to return only the requested root issue(s), and use a small positive `maxDepth` for large hierarchies.

### 6.3 Xray retrieval by Jira issue type

For Jira issue type `Test`, the tool queries Xray `getTests` with exact-key JQL (`key = "<KEY>"`). For `Story` and `Requirement`, it queries `getTests` with `issue in requirementTests("<KEY>")`. Other issue types are not mapped to an inferred relationship. They receive `UNSUPPORTED_ISSUE_TYPE`, with a message identifying the unsupported type and listing `Test, Story, Requirement`. The same retrieval logic is applied to each child node. **Do:** treat `UNSUPPORTED_ISSUE_TYPE` as a deliberate skip, not as proof that the Jira issue is missing or that the complete tool invocation failed.

### 6.4 Result fields and failure handling

Each successful issue node returns `issue_id`, `title`, `status`, `description`, `labels`, `assignee`, `due_date`, `reporter`, `issue_type`, `child_work_item_ids`, `xray_retrieval`, and `children`. The Xray retrieval object contains `retrieval_status`, `retrieval_method`, `total_test_cases`, and `test_cases`; a `message` is included for unsupported issue types and Xray retrieval errors. Xray Test records are preserved from the GraphQL response, including `issueId`, `testType`, selected Jira fields, and ordered `steps` (`id`, `action`, `data`, `result`). Jira ADF descriptions are flattened to plain text. A root Jira fetch failure is returned in that root's result position as an object with `issue_id`, `error`, and `detail`; other requested roots continue. Xray failures are attached to the affected node. Child-search failures are silently treated as no children, so an empty `children` array does not prove that no children exist. **Do:** inspect each root's `error`, each node's `xray_retrieval.retrieval_status`, and the `message` field where present; do not interpret an empty child list as proof that child discovery succeeded.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `boto3.client("secretsmanager").get_secret_value(SecretId=SECRET_NAME)` (once per tool invocation) | Read Jira and Xray credentials from the secret named in `SECRET_NAME`. |
| 2 | `POST {xray_base_url}/api/v2/authenticate` (once per tool invocation) | Authenticate to Xray using `xray_client_id` and `xray_client_secret`; reuse the returned token for all issue nodes in the invocation. |
| 3 | `GET {jira_base_url}/rest/api/3/issue/{key}` (per requested root issue) | Fetch the Jira issue with `fields=*all` using Jira HTTP Basic Authentication. |
| 4 | `POST {xray_base_url}/api/v2/graphql` (per supported issue node and page) | Run Xray GraphQL `getTests` using exact Test JQL or `requirementTests()` coverage JQL; paginate with `start` and `limit` variables. |
| 5 | `POST {jira_base_url}/rest/api/3/search/jql` (per expanded issue and page) | Search direct children using `parent = "<KEY>" ORDER BY created ASC`, with `maxResults` `100` and `fields: ["*all"]`; continue with `nextPageToken`. |

The call order for each root is Jira issue fetch, Xray retrieval for that node, then child search if traversal is enabled. The same Xray retrieval and child-search sequence is repeated recursively for child nodes.

### 7.2 Returns

**Success — one issue**

```json
{
  "issue_id": "<JIRA-KEY>",
  "title": "<Jira summary>",
  "status": "<status name>",
  "description": "<plain text or null>",
  "labels": ["<label>"],
  "assignee": "<display name or null>",
  "due_date": "<date or null>",
  "reporter": "<display name or null>",
  "issue_type": "<Jira issue type>",
  "child_work_item_ids": ["<child JIRA-KEY>"],
  "xray_retrieval": {
    "retrieval_status": "SUCCESS | NO_TESTS_FOUND | UNSUPPORTED_ISSUE_TYPE | PERMISSION_ERROR | FAILED",
    "retrieval_method": "exact_test_lookup | requirement_coverage_lookup | not_completed",
    "total_test_cases": 0,
    "test_cases": [],
    "message": "<included for unsupported issue types or Xray retrieval errors>"
  },
  "children": []
}
```

For `keys`, a top-level list, or comma-separated input, the output is an array of issue objects and/or per-root error objects. A root Jira fetch failure is represented as:

```json
{
  "issue_id": "<JIRA-KEY>",
  "error": "HTTP <status>",
  "detail": "<Jira response detail>"
}
```

An unexpected error while processing a root is represented as:

```json
{
  "issue_id": "<JIRA-KEY>",
  "error": "RETRIEVAL_ERROR",
  "detail": "<exception detail>"
}
```

**Error strings and error forms**

The following are the literal error messages or message templates built by the production code. Dynamic values are shown in braces.

| Error | When it occurs |
|-------|----------------|
| `Provide 'key' or 'keys' in inputJSON.` | Empty string input. |
| `Fatal error: provide 'key' (string) or 'keys' (list).` | Dictionary contains neither a usable `key` nor `keys`; the outer handler prefixes this with `Fatal error: ` as well. |
| `inputJSON must be a dict, list, JSON string, CSV string, or Jira key.` | Input cannot be normalized as a supported outer type. |
| `'key' must be a Jira key string; 'keys' must be a string, a list of strings, or a list of Jira issue objects.` | The `key`/`keys` value has an unsupported type. |
| `Invalid issue item at index {index}: expected a Jira key string or an object containing one of {candidate_fields}.` | A dictionary item in the issue list contains none of the recognized Jira-key fields. |
| `Invalid issue item at index {index}: expected a Jira key string or Jira issue object; received {type_name}.` | A list item is not a supported string, dictionary, or object with a recognized key attribute. |
| `Invalid Jira issue key '{raw_key}' at index {index}. Expected format such as E2ESFI-14.` | A normalized list key does not match the Jira key pattern. |
| `Provide at least one Jira issue key.` | The normalized key list is empty. |
| `'maxDepth' must be a non-negative integer.` | `maxDepth` is `True`, cannot be converted to an integer, or is negative. `False` is treated as `0` and therefore selects the default depth. |
| `{field_name} must be a string.` | A value passed to the strict Jira key validator is not a string. |
| `Invalid {field_name}. Expected a key such as E2ESFI-14; quotes, whitespace within the key, JQL operators and special characters are not allowed.` | A key fails strict validation or exceeds 255 characters. |
| `AWS secret must contain a JSON object.` | Secrets Manager returns a secret that does not parse to a dictionary. |
| `AWS secret is missing required keys: {comma-separated missing credential names}` | One or more required credential values are absent. |
| `xray_base_url must start with http:// or https://.` | The selected Xray base URL has no accepted scheme. |
| `Unable to read AWS Secrets Manager secret '{self.SECRET_NAME}': {exc}` | AWS Secrets Manager raises `ClientError`. |
| `Credential loading failed: {exc}` | Another exception occurs during credential loading. |
| `Xray authentication failed (HTTP {status_code}): {response_text}` | Xray authentication returns a non-200 status. The response text is truncated to 1,500 characters. |
| `Xray authentication returned an empty token.` | Xray authentication returns an empty token. |
| `Jira returned a non-JSON issue response.` | Jira issue response cannot be parsed as JSON. |
| `Jira issue response did not contain fields.` | Jira issue response is not an object containing a `fields` dictionary. |
| `Xray GraphQL permission failure (HTTP {status_code}): {detail}` | Xray GraphQL returns HTTP 401 or 403. |
| `Xray GraphQL request failed (HTTP {status_code}): {detail}` | Xray GraphQL returns another non-200 status. |
| `Xray returned non-JSON response: {detail}` | Xray GraphQL response cannot be parsed as JSON. |
| `Xray GraphQL response was not a JSON object.` | Parsed Xray response is not a dictionary. |
| `Xray GraphQL returned errors: {JSON errors}` | Xray GraphQL response contains an `errors` field. |
| `Unexpected Xray GraphQL response: {JSON body}` | Response does not contain a dictionary at `data.getTests`. The serialized body is truncated to 2,000 characters. |
| `Xray GraphQL 'results' was not a list.` | `getTests.results` has an unexpected type. |
| `Jira issue type '{issue_type or 'Unknown'}' is not a supported Xray retrieval root. Supported types: Test, Story, Requirement.` | Jira issue type is not supported for Xray retrieval; node status is `UNSUPPORTED_ISSUE_TYPE`. |
| `Fatal error: {exc}` | An exception escapes the per-root handling, such as input normalization, credential loading, or Xray authentication. |

For a non-200 Jira issue fetch, the returned root error uses `HTTP {status_code}` and `detail` contains the response body (up to 2,000 characters), or `No response detail supplied.` when no response detail is available. A root-level unexpected exception is returned with `error: "RETRIEVAL_ERROR"` and the exception text in `detail`. Child-search HTTP, request, and JSON failures return an empty child list and do not add an error field.

### 7.3 Known limitations

- Read-only. The tool does not create, update, transition, execute, delete, or link Jira/Xray issues.
- Only Jira issue types `Test`, `Story`, and `Requirement` have Xray retrieval behavior. Other types receive `UNSUPPORTED_ISSUE_TYPE`.
- Child discovery follows Jira's `parent` relationship only. Other issue links are not traversed.
- Child-search failures are silently treated as leaf nodes; no child-search error is added to the output.
- Jira issue descriptions are flattened to plain text. The original ADF structure and formatting are not returned.
- The tool returns the Jira fields and Xray GraphQL fields selected in the production code; there is no input option to request additional fields.
- The tool does not deduplicate repeated requested Jira keys or records with identical titles or test steps.
- There is no hard maximum for the number of requested issue keys or `maxDepth`; the default traversal depth is `5`.

### 7.4 Security & resilience

**Security**

- Jira and Xray credentials are loaded at runtime from AWS Secrets Manager using the AWS identity available to the pod. The agent does not supply credentials in `inputJSON`.
- The AWS workload identity must have `secretsmanager:GetSecretValue` permission for the secret named in `SECRET_NAME`.
- Jira keys are trimmed, uppercased, and validated against an ASCII-only full-match pattern. The strict validator rejects keys longer than 255 characters.
- JQL values are built from validated Jira keys and wrapped as quoted JQL string literals. The accepted key grammar excludes quotes, backslashes, whitespace within keys, JQL operators, and special characters.
- Jira base URL values are normalized to include an HTTP(S) scheme. Xray base URL values are rejected unless they begin with `http://` or `https://`.
- Credentials and the Xray bearer token are used in request authentication/headers and are not included in the normal result payload. Error details can include remote response text; the Secrets Manager `ClientError` message is also included in the credential-loading error. **Do:** restrict the pod's IAM permissions and outbound network access, and ensure error details are access-controlled and redacted before being written to shared logs.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | All `requests` calls use `timeout=(5, REQUEST_TIMEOUT_SECONDS)`; the configured read timeout is `30` seconds. | Keep explicit connect/read timeouts and tune them to measured Jira/Xray latency. |
| Retry | None. Jira root failures are isolated per root; Xray failures are attached to the node; child-search failures are silently treated as no children. | Add bounded retries with backoff for transient 429 and 5xx responses. Preserve explicit child-search failure visibility rather than converting every failure to an empty list. |
| Concurrency | Root issues, child nodes, and pagination are processed sequentially. One Xray token is reused per invocation. | If throughput requires it, introduce bounded concurrency while retaining per-root failure isolation and respecting Jira/Xray rate limits. |
| Input validation | The tool validates supported input shapes, extracts recognized issue-key fields, normalizes keys, validates Jira key syntax, and converts `maxDepth` to an integer while rejecting `True` and negative values; `False` compares equal to `0` and selects the default depth. `includeChildren` uses Python truthiness. | Add configurable upper bounds for the number of keys and traversal depth when inputs can come from untrusted callers. |
| Pagination | Jira child search uses `nextPageToken`; Xray GraphQL uses offset pagination with `start` and `limit`. Both page sizes are `100`. | Retain pagination and add safeguards/telemetry for unusually large result sets. |

The production file is `xray_jira_reader_multi_v2.py`.
