# tool-L0-jira-epics-uploader

## 1. Executive summary

You give the tool one JSON payload with a Jira project key and an ordered list of issues (typically Epics followed by their child Stories). It creates each issue in Jira in order, converts each description into Jira's rich-text format, links each child to its parent, and turns references to earlier issues into clickable links. It returns one result line per issue with the new Jira key and its browse URL, or the reason it failed.

**Key points** (details in [Section 6](#6-nuances)):

- Order matters. A child can only use a parent's logical ID (e.g. `EP-01`) if that parent appears earlier in the same `issues` list ([6.1](#61-parents-must-come-before-children)).
- A failed issue does not stop the run, and running the same payload twice creates duplicates ([6.4](#64-partial-failures-and-re-runs)).
- The Jira URL, email and API token can be overridden from the input. The sibling `tool-L0-sfi-jira-epics-uploader` does not allow this, but adds custom field support ([6.6](#66-credential-overrides-in-the-input) and [6.7](#67-how-this-tool-differs-from-tool-l0-sfi-jira-epics-uploader)).

---

## 2. How to use

### 2.1 Calling the tool in aava

Enter these values and click **Execute**.

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
      "description": {
        "description": "Technical foundation for the customer portal.",
        "scope_in": ["User registration", "Consent capture flow"],
        "scope_out": ["Reporting (see EP-02)"]
      }
    },
    {
      "summary": "F-01.1: User Registration",
      "issueType": "Story",
      "label": ["F-01.1"],
      "parentKey": "EP-01",
      "description": {
        "description": "Allow new users to register. Relates to EP-01.",
        "requirements_covered": ["FR-12", "NFR-03"]
      }
    }
  ]
}
```

The optional `baseUrl`, `userEmail` and `apiToken` keys are left out of this example. Without them, the values from the secret are used.

### 2.2 Calling the tool in an agent

The agent builds `inputJSON` on every call. `projectKey` is usually fixed for the environment; `issues` comes from the upstream payload. Credentials come from the secret, so the agent should not pass `baseUrl`, `userEmail` or `apiToken`.

```
inputJSON = {
  "projectKey": "{{jira_project_key}}",
  "issueType": "Epic",
  "issues": {{converted_issue_list}}
}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputJSON` | Dict[str, Any] | ✓ | Payload dictionary. Keys: `projectKey` (str, required; missing or empty returns a fatal error), `issueType` (str, optional, default `"Epic"`; used for issues without their own type), `issues` (list, required, must be non-empty; see below), `baseUrl` (str, optional; overrides the secret's Jira URL), `userEmail` (str, optional; overrides the secret's email), `apiToken` (str, optional; overrides the secret's token). Each item in `issues` accepts: `summary` (str, default `"<no summary>"`), `description` (str or dict, default empty), `issueType` (str), `label` or `labels` (str or list of str; the first label is the issue's logical ID; spaces become `_`), `parentKey` (str; a logical ID from earlier in the list or a real Jira key). |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| Jira base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `base_url` | e.g. `https://<your-domain>.atlassian.net`. Can be overridden by `baseUrl` in the input. |
| Jira account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Atlassian account used for Basic auth. Can be overridden by `userEmail` in the input. |
| Jira API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Can be overridden by `apiToken` in the input. If both are empty, the `JIRA_API_TOKEN` environment variable is used. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with the secret's name. The pod's IAM role needs `secretsmanager:GetSecretValue` on it. |
| AWS region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the secret's region. |
| `ISSUE_TYPE_MAP` | Code — module configuration | `SETUP-REQUIRED:` defaults to `{}` (types sent unchanged). Map payload types to the types your project offers, e.g. `{"Epic": "Task", "Story": "Task"}`. |
| `DEFAULT_ISSUE_TYPE` | Code — module configuration | Defaults to `"Epic"`. Used when neither the payload nor the issue sets `issueType`. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-jira-epics-uploader-epics.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `os` | stdlib | `JIRA_API_TOKEN` environment variable fallback |
| `re` | stdlib | Logical-ID matching and heading formatting |
| `json` | stdlib | Parsing the secret and stringifying description values |
| `requests` | `requests` | Jira REST calls and Basic auth (`requests.auth.HTTPBasicAuth`) |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` handling |

---

## 6. Nuances

### 6.1 Parents must come before children
Issues are created one at a time, in list order. When an issue is created, its first label (e.g. `EP-01`) is mapped to the new Jira key. A later issue's `parentKey` is looked up in that map; if it is not found, the value is sent to Jira unchanged as a real key. A child listed before its parent therefore sends `EP-01` as the parent key and Jira rejects it. **Do:** list every Epic before its Stories, and give each parent its logical ID as the first label.

### 6.2 Cross-references become links only to earlier issues
In descriptions, text matching `EP-<n>`, `F-<n>`, `FR-<n>` or `NFR-<n>` (with optional `.n` parts, e.g. `F-01.2`) is replaced by the Jira key and a link to `<base_url>/browse/<KEY>` if that logical ID was created earlier in the same call. Otherwise the text is left as it is. **Do:** order issues so that referenced items come first, and expect forward references to stay as plain text.

### 6.3 Description formatting is limited
A string description supports lines starting with `- ` (bullets), `**bold**` and `*italic*`. All other lines become plain paragraphs; headings, numbered lists, tables and code blocks are not converted. A dict description becomes one bold heading per key (`scope_in` becomes "Scope in"), with list values as bullets and nested dict values as `key: value` bullets. **Do:** pass descriptions as a dict of short sections or as simple bullet text.

### 6.4 Partial failures and re-runs
If Jira rejects an issue, a `Failed:` line is added and the next issue is still attempted. Children of a failed parent will then fail too (see 6.1). An unexpected error (e.g. an item in `issues` that is not a dict) stops the run and returns only `Fatal error: ...`, even if earlier issues were already created. The tool does not check for existing issues, so running the same payload twice creates duplicates. **Do:** check every line for `Failed:`, and before re-running, remove the issues that were already created from the payload.

### 6.5 Issue type names must exist in the project
If the project's issue-type scheme does not include the type sent (e.g. `Epic` or `Story`), Jira returns a 400 error that reads like a missing project or permission problem. **Do:** confirm the project's issue types and set `ISSUE_TYPE_MAP` in code when they differ from the payload's types.

### 6.6 Credential overrides in the input
`baseUrl`, `userEmail` and `apiToken` in `inputJSON` take priority over the secret. This allows one deployment to target another Jira site, but any token passed this way is visible in the tool input and agent traces. **Do:** leave these keys out in normal use so the secret's values apply.

### 6.7 How this tool differs from tool-L0-sfi-jira-epics-uploader
Both tools share the same payload format, ordering, linking and description logic. This tool also accepts `userEmail` and `apiToken` overrides, falls back to the `JIRA_API_TOKEN` environment variable, and adds a `url:` line after each created issue. `tool-L0-sfi-jira-epics-uploader` always uses the secret's email and token, returns no `url:` line, and passes per-issue `customfield_<id>` values through to Jira, which this tool ignores. **Do:** use the sibling tool when your Jira project requires custom fields on create.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (at module import) | Read the Jira base URL, email and API token |
| 2 | `POST {base_url}/rest/api/3/issue` (once per issue, in order) | Create each issue with project, summary, type, labels, ADF description and optional parent |

### 7.2 Returns

**Success**
```
<IssueType> created: <KEY>  (<summary>)
url: <base_url>/browse/<KEY>
<IssueType> created: <KEY>  (<summary>)
url: <base_url>/browse/<KEY>
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
| `Failed: <summary> -> HTTP 400 \| Detail: ...` | Invalid field, unknown issue type, or unresolved parent key | Read the detail; check issue order (6.1) and `ISSUE_TYPE_MAP` (6.5) |
| `Failed: <summary> -> HTTP 401 \| Detail: ...` | Wrong email or API token | Check keys `id` and `api_key` in the secret |
| `Failed: <summary> -> HTTP 403 \| Detail: ...` | Account cannot create issues in the project | Grant "Create issues" permission in the project |
| `Failed: <summary> -> <exception> \| Detail: No response received` | Network error reaching Jira | Check `base_url` and network access from the pod |
| `RuntimeError: Error retrieving secret: ...` / `RuntimeError: Unexpected error: ...` | Secret missing, access denied or not valid JSON (raised at import; the tool does not load) | Check `SECRET_NAME`, region and the pod's IAM role |

### 7.3 Known limitations

- Create only. It cannot update, transition, link (other than parent) or delete issues.
- No custom fields, assignee, priority, components, fix versions or due dates. Only project, summary, type, labels, description and parent are sent.
- No duplicate check or idempotency; every call creates new issues.
- Logical-ID linking only recognises the `EP-`, `F-`, `FR-` and `NFR-` prefixes.
- No dry-run option in the tool input. The Python helper `create_issues(payload, dry_run=True)` builds payloads without calling Jira, for local testing only.

### 7.4 Security & resilience

**Security**
- Credentials are read from AWS Secrets Manager via Pod Identity when the module is imported, and used for Basic auth. They are not logged or returned.
- `baseUrl`, `userEmail` and `apiToken` in the input override the secret, so credentials passed this way appear in tool inputs and traces.
- Failure lines include Jira's raw response body.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | None; `requests.post` has no timeout and can hang | Pass `timeout=30` to `requests.post` |
| Retry | None; a failed issue is reported and skipped | Retry on 429 and 5xx with exponential backoff, honouring `Retry-After` |
| Concurrency | Issues are created one at a time, in order (required for parent resolution) | Keep sequential; split very large payloads across calls |
| Input validation | Only `projectKey` presence and a non-empty `issues` list are checked; item shape, types and parent order are not | Validate each issue (dict, summary present, parent defined earlier) before the first POST |
