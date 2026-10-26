# tool-L0-jira-writer

## 1. Executive summary

You give the tool a Jira project key and a list of issues, each with a summary and a description. It creates the issues one by one, converting each description into Jira's rich-text format and turning logical IDs such as `E1` into links to issues created earlier in the same call. It returns one line per issue with the new Jira key or the failure reason.

**Key points** (details in [Section 6](#6-nuances)):

- `projectKey` has no default. Without it every issue fails ([6.1](#61-projectkey-must-always-be-passed)).
- Issues are created in list order. `label[0]` is a logical ID that later descriptions can reference as a link; `parentKey` must be a real Jira key ([6.2](#62-order-logical-ids-and-parents)).
- Descriptions support only `- ` bullets, `**bold**` and `*italic*` ([6.3](#63-description-formatting)).
- A missing `summary` or `description` stops the whole run and hides results for issues already created; nothing is rolled back ([6.4](#64-partial-failure-and-re-runs)).

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
      "summary": "Customer onboarding portal",
      "description": "Build the self-service onboarding flow.\n- Sign-up form\n- **Email verification**",
      "label": ["E1"]
    },
    {
      "summary": "Onboarding analytics",
      "description": "Track funnel drop-off for E1.",
      "label": ["E2"]
    },
    {
      "summary": "Design sign-up form",
      "description": "Wireframes and validation rules.",
      "issueType": "Story",
      "parentKey": "PROJ-100"
    }
  ]
}
```

`baseUrl` and `userEmail` are omitted from the example. Leave them out so the values from AWS Secrets Manager are used.

### 2.2 Calling the tool in an agent

`issues` changes on every call and is usually content the agent has just drafted. `projectKey` and the default `issueType` are normally fixed for the workflow. The Jira site and credentials come from AWS Secrets Manager.

```
inputJSON = {
  "projectKey": "{{project_key}}",
  "issueType": "Epic",
  "issues": {{issues_drafted_by_agent}}
}
```

---

## 3. Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `inputJSON` | Dict[str, Any] | ✓ | Request payload with the keys below. Must be a dict; strings are not parsed. |
| `inputJSON.projectKey` | str | ✓ | Jira project key, e.g. `PROJ`. Not enforced by the schema, but there is no fallback; without it Jira rejects every issue. |
| `inputJSON.issueType` | str |  | Default issue type for every issue, e.g. `Epic`, `Story`, `Task`. Default `Epic`. Must exist in the project. |
| `inputJSON.issues` | List[Dict] |  | Issues to create, in order. Default `[]` (nothing is created and an empty string is returned). |
| `inputJSON.issues[].summary` | str | ✓ | Issue title. |
| `inputJSON.issues[].description` | str or Dict | ✓ | Text with `- ` bullets, `**bold**`, `*italic*`; or a dict rendered as headed sections (see [6.3](#63-description-formatting)). |
| `inputJSON.issues[].issueType` | str |  | Overrides the default issue type for this issue. |
| `inputJSON.issues[].label` | List[str] |  | Jira labels for the issue (no spaces). `label[0]` is also the logical ID, e.g. `E1`, used for cross-links. Default `[]`. |
| `inputJSON.issues[].parentKey` | str |  | Real Jira key of the parent issue, e.g. `PROJ-100`. |
| `inputJSON.baseUrl` | str |  | Jira site URL, e.g. `https://<your-domain>.atlassian.net`. Overrides `base_url` from the secret. A trailing `/` is removed. |
| `inputJSON.userEmail` | str |  | Atlassian account email. Overrides `id` from the secret. |

---

## 4. Secrets & configuration

| Value | Source | Notes |
|-------|--------|-------|
| Jira base URL | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `base_url` | Site root, e.g. `https://<your-domain>.atlassian.net`. Used when `baseUrl` is not passed. Also used to build `/browse/<KEY>` links. |
| Jira account email | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `id` | Basic-auth user. Used when `userEmail` is not passed. |
| Jira API token | AWS Secrets Manager — the secret named in `SECRET_NAME`, key `api_key` | Basic-auth password. If empty, the `JIRA_API_TOKEN` environment variable is used. It cannot be passed in the input. |
| `SECRET_NAME` | Code — `AWSSecretReaderPodIdentity` | `SETUP-REQUIRED:` placeholder `<name-of-secret-in-aws-secrets-manager>`. Replace it with your secret's name. The secret must be a JSON object. |
| Secrets Manager region | Code — `AWSSecretReaderPodIdentity._run` | `SETUP-REQUIRED:` defaults to `us-east-1`. Set it to the region the secret lives in. |
| AWS credentials | Pod Identity (IAM role on the pod) | No AWS keys in code. The role needs `secretsmanager:GetSecretValue` on the secret. |
| `DEFAULT_ISSUE_TYPE` | Code — module constant | Defaults to `Epic`. Used when neither the payload nor the issue sets `issueType`. |

Before deploying to a new environment, review every value tagged `SETUP-REQUIRED:` in `tool-L0-jira-writer.py`.

---

## 5. Import modules required

| Module | Package | Used for |
|--------|---------|----------|
| `os` | stdlib | `JIRA_API_TOKEN` environment fallback |
| `re` | stdlib | Heading formatting and logical-ID matching |
| `json` | stdlib | Parsing the secret |
| `requests` | `requests` | Jira REST calls |
| `requests.auth` | `requests` | `HTTPBasicAuth` |
| `typing` | stdlib | Type hints |
| `pydantic` | `pydantic` | Input schema (`BaseModel`, `Field`) |
| `crewai.tools` | `crewai` | `BaseTool` base class |
| `boto3` | `boto3` | Secrets Manager client |
| `botocore.exceptions` | `botocore` | `ClientError` |

---

## 6. Nuances

### 6.1 projectKey must always be passed
The project key is taken only from `inputJSON.projectKey`. If it is missing, the request is still sent with no project key and Jira rejects each issue with an HTTP 400 `Failed:` line. **Do:** always include `projectKey`, and make sure `issueType` names a type that exists in that project.

### 6.2 Order, logical IDs and parents
Issues are created strictly in list order. When an issue is created, its `label[0]` (e.g. `E1`) is mapped to the new Jira key. In descriptions of later issues, any text matching `E<number>` (optionally `.<part>`, e.g. `E1.2`) that is in that map becomes a link to `<base_url>/browse/<KEY>`; unknown IDs stay as plain text. The match is made anywhere in the text, including inside words. `parentKey` is not resolved through this map. **Do:** put referenced issues before the issues that mention them, use `E`-style IDs as `label[0]` only when you want linking, and pass parents as real keys that already exist.

### 6.3 Description formatting
A string description is split into lines. Lines starting with `- ` become a bullet list; every other non-empty line becomes its own paragraph; blank lines are dropped. Inside a line, `**text**` is bold and `*text*` is italic. Headings, numbered lists, links, tables and code blocks are not converted and appear as literal text. A dict description becomes one section per key: the key is turned into a bold heading (`acceptanceCriteria` becomes "Acceptance criteria"), list values become bullets and nested dicts become `key: value` lines. **Do:** send plain lines with `- ` bullets and bold or italic only, and avoid stray `*` characters, which can turn following text italic.

### 6.4 Partial failure and re-runs
If Jira rejects an issue or the request fails, that issue gets a `Failed:` line and the tool continues with the next one. If an issue is missing `summary` or `description`, the tool stops and returns only `Fatal error: '<field>'`; issues created before that point still exist in Jira but their keys are not returned. The tool does not check for existing issues, so re-running a payload creates duplicates. **Do:** validate every issue has `summary` and `description` before calling, and check Jira for already-created issues before retrying.

---

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|------|----------|---------|
| 1 | `secretsmanager:GetSecretValue` (once, at module import) | Read `base_url`, `id` and `api_key` |
| 2 | `POST {base_url}/rest/api/3/issue` (once per issue, in order) | Create the issue with project, summary, issue type, labels, ADF description and optional parent |

### 7.2 Returns

**Success**
```
<issueType> created: <KEY>
<issueType> created: <KEY>
Failed: <summary> → HTTP <status> | Detail: <Jira response body>
```
One line per issue, in input order. An empty `issues` list returns an empty string.

**Error**
```
Failed: <summary> → <exception> | Detail: <Jira response body | No response received>
Fatal error: <detail>
```

| Error | Cause | Fix |
|-------|-------|-----|
| `Failed: <summary> → HTTP 400 \| Detail: ...` | Missing or wrong `projectKey`, unknown issue type, label with spaces, invalid `parentKey` or a parent/child type mismatch | Read the Jira detail and correct the payload |
| `Failed: <summary> → HTTP 401 \| Detail: ...` | Wrong email or API token | Check `id` and `api_key` in the secret |
| `Failed: <summary> → HTTP 403 \| Detail: ...` | Account lacks create permission in the project | Grant "Create issues" in the project |
| `Failed: <summary> → <exception> \| Detail: No response received` | Network or DNS failure reaching Jira | Check `base_url` and network access from the pod |
| `Fatal error: 'summary'` / `Fatal error: 'description'` | An issue is missing that field; the run stops | Add the field to every issue |
| `Fatal error: <detail>` | Any other exception, e.g. `issues` is not a list of dicts | Check the payload shape |
| `RuntimeError: Error retrieving secret: <detail>` / `RuntimeError: Unexpected error: <detail>` | Secret could not be read when the module was imported; the tool does not load | Check `SECRET_NAME`, the region, the Pod Identity association and `secretsmanager:GetSecretValue` |

### 7.3 Known limitations

- Create-only. It cannot update, transition, comment on or delete issues.
- Sets only project, summary, issue type, labels, description and parent. No priority, assignee, components, due date, fix version or custom fields.
- One project per call.
- `parentKey` cannot reference a logical ID from the same call; it must be an existing Jira key.
- The API token cannot be supplied in the input.
- Description conversion covers paragraphs, `- ` bullets, bold and italic only.

### 7.4 Security & resilience

**Security**
- Jira credentials are read from AWS Secrets Manager through Pod Identity; none are stored in code. They are read once when the module is imported.
- `baseUrl` and `userEmail` in the input override the secret. If `baseUrl` is overridden, the stored API token is sent to that URL.
- The tool prints the HTTP status and full Jira response body to stdout for every create call. Credentials are not printed. Failure lines include the raw Jira response body.

**Resilience**

| Concern | Current state | Recommendation |
|---------|---------------|----------------|
| Timeout | None; `requests.post` has no timeout | Pass `timeout=(5, 30)` to every `requests` call |
| Retry | None; each issue is attempted once | Retry 429 and 5xx with backoff, honouring `Retry-After`, and guard against duplicates |
| Concurrency | Issues are created one at a time, which preserves ordering for logical-ID links | Keep sequential creation; use Jira's bulk create endpoint for large batches |
| Input validation | Only checks that `inputJSON` is a dict; missing `summary`/`description` aborts the run; `baseUrl` host is not checked | Validate every issue and `projectKey` before the first call, and restrict `baseUrl` to your Jira site |
