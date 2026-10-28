# tool-L0-sfi-jira-epics-uploader

## 1. Summary

You give the tool one JSON payload with a Jira project key and an ordered list of issues (typically Epics followed by their child Stories), where each issue can also carry Jira custom fields. It creates each issue in Jira in order, converts each description into Jira's rich-text format, links each child to its parent, turns references to earlier issues into clickable links, and sends any `customfield_<id>` values to Jira as given. It returns one result line per issue with the new Jira key, or the reason it failed.

**Key points** (details in [Section 6](#6-nuances)):

- Custom fields are passed through unchanged. Their IDs and value shapes must match your Jira site exactly ([6.1](#61-custom-fields-are-passed-through-as-given)).
- Order matters. A child can only use a parent's logical ID (e.g. `EP-01`) if that parent appears earlier in the same `issues` list ([6.2](#62-parents-must-come-before-children)).
- A failed issue does not stop the run, and running the same payload twice creates duplicates ([6.5](#65-partial-failures-and-re-runs)).
- Compared with `tool-L0-jira-epics-uploader`, this tool adds custom fields, always uses the secret's credentials, and returns no URL line ([6.7](#67-how-this-tool-differs-from-tool-l0-jira-epics-uploader)).

---

## 2. How to use

### 2.1 Calling the tool in aava

*These are sample values. Enter actual values to run tool in AAVA*

**`inputJSON`**
```
{
  "projectKey": "PROJ",
  "issueType": "Epic",
  "issues": [
    {
      "summary": "EP-01: Platform Foundation",
      "issueType": "Epic",
      "label": ["EP-01"],
      "customfield_10244": {"value": "Functional"},
      "description": {
        "description": "Technical foundation for the customer portal.",
        "scope_in": ["User registration", "Consent capture flow"]
      }
    },
    {
      "summary": "F-01.1: User Registration",
      "issueType": "Story",
      "label": ["F-01.1"],
      "parentKey": "EP-01",
      "customfield_10244": {"value": "Functional"},
      "description": {
        "description": "Allow new users to register. Relates to EP-01.",
        "requirements_covered": ["FR-12", "NFR-03"]
      }
    }
  ]
}
```

The custom field ID and value above are examples. Use the IDs your Jira site defines. The optional `baseUrl` key is left out, so the URL from the secret is used.

### 2.2 Calling the tool in an agent

The agent builds `inputJSON` on every call. `projectKey` is usually fixed for the environment; `issues` (including any custom fields) comes from the upstream payload. Credentials always come from the secret.

```
inputJSON = {
  "projectKey": "{{jira_project_key}}",
  "issueType": "Epic",
  "issues": {{converted_issue_list_with_custom_fields}}
}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputJSON` | Dict[str, Any] | ✓ | Payload dictionary. Keys: `projectKey` (str, required; missing or empty returns a fatal error), `issueType` (str, optional, default `"Epic"`; used for issues without their own type), `issues` (list, required, must be non-empty; see below), `baseUrl` (str, optional; overrides the secret's Jira URL). Each item in `issues` accepts: `summary` (str, default `"<no summary>"`), `description` (str or dict, default empty), `issueType` (str), `label` or `labels` (str or list of str; the first label is the issue's logical ID; spaces become `_`), `parentKey` (str; a logical ID from earlier in the list or a real Jira key), and any number of `customfield_<digits>` keys (any JSON value, sent to Jira unchanged; `null` values are skipped). Other keys are ignored, including `userEmail` and `apiToken`. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| Jira base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `base_url` | e.g. `https://<your-domain>.atlassian.net`. Can be overridden by `baseUrl` in the input. |
| Jira account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Atlassian account used for Basic auth. Cannot be overridden. |
| Jira API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Cannot be overridden; no environment variable fallback. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the secret's name. The pod's IAM role needs `secretsmanager:GetSecretValue` on it. |
| AWS region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the secret's region. |
| `ISSUE_TYPE_MAP` | Code — module configuration | `SETUP-REQUIRED:` defaults to `{}` (types sent unchanged). Map payload types to the types your project offers, e.g. `{"Epic": "Task", "Story": "Task"}`. |
| `DEFAULT_ISSUE_TYPE` | Code — module configuration | Defaults to `"Epic"`. Used when neither the payload nor the issue sets `issueType`. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-sfi-jira-epics-uploader.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `re` | stdlib | Logical-ID and custom field key matching, heading formatting |
| `json` | stdlib | Parsing the secret and stringifying description values |
| `requests` | `requests` | Jira REST calls and Basic auth (`requests.auth.HTTPBasicAuth`) |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |

---

## 6. Nuances

### 6.1 Custom fields are passed through as given
Any key on an issue that matches `customfield_<digits>` is added to the Jira fields unchanged; keys with a `null` value are skipped. The tool does not look up field IDs, check that a field is on the project's create screen, or convert values. Select fields usually need `{"value": "<option>"}`, and a wrong shape or an unknown ID makes Jira reject the whole issue with HTTP 400. **Do:** confirm each custom field's ID and value format for your Jira site and include every field your project requires on create.

### 6.2 Parents must come before children
Issues are created one at a time, in list order. When an issue is created, its first label (e.g. `EP-01`) is mapped to the new Jira key. A later issue's `parentKey` is looked up in that map; if it is not found, the value is sent to Jira unchanged as a real key. A child listed before its parent therefore sends `EP-01` as the parent key and Jira rejects it. **Do:** list every Epic before its Stories, and give each parent its logical ID as the first label.

### 6.3 Cross-references become links only to earlier issues
In descriptions, text matching `EP-<n>`, `F-<n>`, `FR-<n>` or `NFR-<n>` (with optional `.n` parts, e.g. `F-01.2`) is replaced by the Jira key and a link to `<base_url>/browse/<KEY>` if that logical ID was created earlier in the same call. Otherwise the text is left as it is. **Do:** order issues so that referenced items come first, and expect forward references to stay as plain text.

### 6.4 Description formatting is limited
A string description supports lines starting with `- ` (bullets), `**bold**` and `*italic*`. All other lines become plain paragraphs; headings, numbered lists, tables and code blocks are not converted. A dict description becomes one bold heading per key (`scope_in` becomes "Scope in"), with list values as bullets and nested dict values as `key: value` bullets. **Do:** pass descriptions as a dict of short sections or as simple bullet text.

### 6.5 Partial failures and re-runs
If Jira rejects an issue, a `Failed:` line is added and the next issue is still attempted. Children of a failed parent will then fail too (see 6.2). An unexpected error (e.g. an item in `issues` that is not a dict) stops the run and returns only `Fatal error: ...`, even if earlier issues were already created. The tool does not check for existing issues, so running the same payload twice creates duplicates. **Do:** check every line for `Failed:`, and before re-running, remove the issues that were already created from the payload.

### 6.6 Issue type names must exist in the project
If the project's issue-type scheme does not include the type sent (e.g. `Epic` or `Story`), Jira returns a 400 error that reads like a missing project or permission problem. **Do:** confirm the project's issue types and set `ISSUE_TYPE_MAP` in code when they differ from the payload's types.

### 6.7 How this tool differs from tool-L0-jira-epics-uploader
Both tools share the same payload format, ordering, linking and description logic. This tool adds per-issue `customfield_<id>` pass-through. It always authenticates with the secret's `id` and `api_key`; `userEmail` and `apiToken` in the input are ignored and there is no `JIRA_API_TOKEN` environment fallback. Its success line has no `url:` line, so you get only the key. `baseUrl` can still be overridden, and the secret's credentials are then sent to that URL. **Do:** use this tool when your project requires custom fields on create; use `tool-L0-jira-epics-uploader` when you need the browse URL in the output and no custom fields.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at module import) | Read the Jira base URL, email and API token |
| 2 | `POST {base_url}/rest/api/3/issue` (once per issue, in order) | Create each issue with project, summary, type, labels, ADF description, optional parent and custom fields |

### 7.2 Returns

**Success**
```
<IssueType> created: <KEY>  (<summary>)
<IssueType> created: <KEY>  (<summary>)
```

**Error**
```
Failed: <summary> -> HTTP <status_code> | Detail: <Jira response body>
Failed: <summary> -> <exception> | Detail: <response body or "No response received">
Fatal error: <detail>
```

Per-issue `Failed:` lines appear among the success lines. A `Fatal error:` string replaces the whole output.

| Error | Cause | Fix |
|-------|-------|-----|
| `Fatal error: no projectKey provided and JIRA_PROJECT_KEY is empty.` | `projectKey` missing or empty in `inputJSON` | Pass `projectKey` (there is no project key fallback in code) |
| `Fatal error: 'issues' must be a non-empty list.` | `issues` missing, empty or not a list | Pass at least one issue in a list |
| `Fatal error: <exception>` | Unexpected error, e.g. an `issues` item is not a dict | Fix the payload shape; check Jira for issues already created |
| `Failed: <summary> -> HTTP 400 \| Detail: ...` | Invalid or missing custom field, unknown issue type, or unresolved parent key | Read the detail; check custom fields (6.1), issue order (6.2) and `ISSUE_TYPE_MAP` (6.6) |
| `Failed: <summary> -> HTTP 401 \| Detail: ...` | Wrong email or API token | Check keys `id` and `api_key` in the secret |
| `Failed: <summary> -> HTTP 403 \| Detail: ...` | Account cannot create issues in the project | Grant "Create issues" permission in the project |
| `Failed: <summary> -> <exception> \| Detail: No response received` | Network error reaching Jira | Check `base_url` and network access from the pod |
| `RuntimeError: Error retrieving secret: ...` / `RuntimeError: Unexpected error: ...` | Secret missing, access denied or not valid JSON (raised at import; the tool does not load) | Check `SECRET_NAME`, region and the pod's IAM role |

### 7.3 Known limitations

- Create only. It cannot update, transition, link (other than parent) or delete issues.
- Only custom fields named `customfield_<digits>` are passed through. Other standard fields such as assignee, priority, components, fix versions or due dates are not sent.
- No duplicate check or idempotency; every call creates new issues.
- No browse URL in the output; only the issue key is returned.
- Logical-ID linking only recognises the `EP-`, `F-`, `FR-` and `NFR-` prefixes.
- No dry-run option in the tool input. The Python helper `create_issues(payload, dry_run=True)` builds payloads without calling Jira, for local testing only.

### 7.4 Security & resilience

**Security**
- Credentials are read from AWS Secrets Manager via Pod Identity when the module is imported, and used for Basic auth. They are not logged or returned, and cannot be supplied in the input.
- `baseUrl` in the input overrides the secret's URL, and the secret's email and token are sent to that host. Do not let untrusted input set `baseUrl`.
- Failure lines include Jira's raw response body.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | None; `requests.post` has no timeout and can hang | Pass `timeout=30` to `requests.post` |
| Retry | None; a failed issue is reported and skipped | Retry on 429 and 5xx with exponential backoff, honouring `Retry-After` |
| Concurrency | Issues are created one at a time, in order (required for parent resolution) | Keep sequential; split very large payloads across calls |
| Input validation | Only `projectKey` presence and a non-empty `issues` list are checked; custom field keys are matched by name but values, item shape and parent order are not checked | Validate each issue and its custom fields before the first POST |
