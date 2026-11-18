# tool-L0-jira-linked-issue-writer

## 1. Summary

You give the tool a Jira project key, an issue type, a source issue key (SourceIssueId) and a list of issues, each with a summary and a description. It creates the issues one by one, converting each description into Jira's rich-text format, then links every created issue to its SourceIssueId with an issue link (default Relates), so it appears under **Related issues** on that source issue. It returns one line per issue with the new Jira key and link status, or the failure reason.
**Key points** (details in [Section 6](#6-nuances)):
- issueType and SourceIssueId are not hard-coded. Each must be supplied in the payload, at the top level or per issue; an issue without either is skipped ([6.2](#62-issuetype-and-sourceissueid-must-be-supplied)).
- Issues are linked, not parented. No parent field is sent, so any issue type can be related to any source issue, e.g. a Task to a Feature ([6.3](#63-linking-to-the-source-issue)).
- The payload must be passed as inputJSON itself; an extra inputJSON wrapper returns an empty string ([6.7](#67-payload-shape)).
- A missing summary or description stops the whole run and hides results for issues already created; nothing is rolled back ([6.6](#66-partial-failure-and-re-runs)).

## 2. How to use

### 2.1 Calling the tool in aava

_These are sample values. Enter actual values to run tool in AAVA_
**inputJSON**
```json
{
  "projectKey": "PROJ",
  "issueType": "Task",
  "SourceIssueId": "PROJ-12",
  "linkType": "Relates",
  "issues": [
    {
      "summary": "[TS-001] Verify server-side limit enforcement",
      "description": {
        "Pre-condition": "Producer limit is configured",
        "Test Data": "Transaction value above the configured limit",
        "Navigable Path": "Submit a transaction",
        "Expected Result": "Transaction is rejected"
      },
      "label": ["ai-generated", "L2-Service", "PROJ-12-AC-01-TS-001"]
    },
    {
      "summary": "[TS-001] Verify limit change is audited",
      "description": "Admin updates the producer limit.\n- **Expected:** change is logged with user and timestamp",
      "issueType": "Task",
      "SourceIssueId": "PROJ-15",
      "label": ["ai-generated", "L2-Service", "PROJ-15-AC-01-TS-001"]
    }
  ]
}
```
baseUrl and userEmail are omitted from the example. Leave them out so the values from AWS Secrets Manager are used. linkType can also be omitted; it defaults to Relates.

### 2.2 Calling the tool in an agent

issues changes on every call and is usually content the agent has just evaluated or drafted. projectKey and issueType are normally fixed for the workflow run. SourceIssueId is set per issue when one call covers several source issues, or once at the top level when all issues relate to the same one. The Jira site and credentials come from AWS Secrets Manager.
```
inputJSON = {
  "projectKey": "{{project_key}}",
  "issueType": "{{issue_type}}",
  "issues": {{issues_with_SourceIssueId}}
}
```

## 3. Parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| inputJSON | Dict\[str, Any\] | ✓ | Request payload with the keys below. Must be a dict; strings are not parsed. |
| inputJSON.projectKey | str | ✓ | Jira project key, e.g. PROJ. Not enforced by the schema, but there is no fallback; without it Jira rejects every issue. |
| inputJSON.issueType | str | ✓\* | Issue type name for every issue, e.g. Task or a custom type such as Test Scenario. No default. Must exist in the project. \*Required unless every issue sets its own issueType. |
| inputJSON.SourceIssueId | str | ✓\* | Real Jira key of the issue every created issue is linked to, e.g. PROJ-12. No default. Case-sensitive key name. \*Required unless every issue sets its own SourceIssueId. |
| inputJSON.linkType | str |  | Name of the Jira issue link type used for the link. Default Relates. Must exist on the Jira site. |
| inputJSON.issues | List\[Dict\] |  | Issues to create, in order. Default \[\] (nothing is created and an empty string is returned). |
| inputJSON.issues\[\].summary | str | ✓ | Issue title. |
| inputJSON.issues\[\].description | str or Dict | ✓ | Text with -  bullets, \*\*bold\*\*, \*italic\*; or a dict rendered as headed sections (see [6.5](#65-description-formatting)). |
| inputJSON.issues\[\].issueType | str |  | Overrides the top-level issueType for this issue. |
| inputJSON.issues\[\].SourceIssueId | str |  | Overrides the top-level SourceIssueId for this issue. |
| inputJSON.issues\[\].label | List\[str\] |  | Jira labels for the issue (no spaces). label\[0\] is also the logical ID used for cross-links (see [6.4](#64-order-and-logical-ids)). Default \[\]. |
| inputJSON.baseUrl | str |  | Jira site URL, e.g. https://\<your-domain\>.atlassian.net. Overrides base\_url from the secret. A trailing / is removed. |
| inputJSON.userEmail | str |  | Atlassian account email. Overrides id from the secret. |

## 4. Secrets & configuration

| Value | Source | Notes |
|---|---|---|
| Jira base URL | AWS Secrets Manager — the secret named in SECRET\_NAME, key base\_url | Site root, e.g. https://\<your-domain\>.atlassian.net. Used when baseUrl is not passed. Also used to build /browse/\<KEY\> links. |
| Jira account email | AWS Secrets Manager — the secret named in SECRET\_NAME, key id | Basic-auth user. Used when userEmail is not passed. |
| Jira API token | AWS Secrets Manager — the secret named in SECRET\_NAME, key api\_key | Basic-auth password. If empty, the JIRA\_API\_TOKEN environment variable is used. It cannot be passed in the input. |
| SECRET\_NAME | Code — AWSSecretReaderPodIdentity | SETUP-REQUIRED: must match the name of the secret in your AWS Secrets Manager. The secret must be a JSON object. |
| Secrets Manager region | Code — AWSSecretReaderPodIdentity.\_run | SETUP-REQUIRED: set to us-east-2 in code. Change it to the region the secret lives in. |
| AWS credentials | Pod Identity (IAM role on the pod) | No AWS keys in code. The role needs secretsmanager:GetSecretValue on the secret. |
| DEFAULT\_LINK\_TYPE | Code — module constant | Defaults to Relates. Used when the payload does not set linkType. |

Before deploying to a new environment, review every value tagged SETUP-REQUIRED: in tool-L0-jira-linked-issue-writer.py.

## 5. Import modules required

| Module | Package | Used for |
|---|---|---|
| os | stdlib | JIRA\_API\_TOKEN environment fallback |
| re | stdlib | Heading formatting and logical-ID matching |
| json | stdlib | Parsing the secret |
| requests | requests | Jira REST calls |
| requests.auth | requests | HTTPBasicAuth |
| typing | stdlib | Type hints |
| pydantic | pydantic | Input schema (BaseModel, Field) |
| crewai.tools | crewai | BaseTool base class |
| boto3 | boto3 | Secrets Manager client |
| botocore.exceptions | botocore | ClientError |

## 6. Nuances

### 6.1 projectKey must always be passed

The project key is taken only from inputJSON.projectKey. If it is missing, the request is still sent with no project key and Jira rejects each issue with an HTTP 400 Failed: line. All issues in one call go to the same project. **Do:** always include projectKey, and make one call per project.

### 6.2 issueType and SourceIssueId must be supplied

Neither value is hard-coded. For each issue, the tool uses the issue's own issueType and SourceIssueId, falling back to the top-level values. If either is still missing, no create call is made; the issue gets Failed: \<summary\> → no issueType supplied in payload (or no SourceIssueId supplied in payload) and the tool continues with the next issue. The key names are case-sensitive: sourceIssueId or featureKey are not read. Any issue type the project allows works, including custom types, as long as it is not a sub-task type and needs no required fields beyond project, summary, issue type, labels and description. **Do:** set both at the top level for a uniform batch, override per issue only when needed, and copy the issue type name exactly as it appears in the project.

### 6.3 Linking to the source issue

The tool never sends a parent field. After an issue is created, it calls the issue link API with the new issue as inwardIssue and SourceIssueId as outwardIssue, using linkType (default Relates). With Relates the link reads the same from both sides, so the issue appears under **Related issues** on the source issue. If the link call is rejected, the issue still exists in Jira and the line reads \<issueType\> created: \<KEY\> \| Link to \<SourceIssueId\> failed → HTTP \<status\> \| Detail: .... If the link call raises a network exception, the line starts with Failed: even though the issue was created. **Do:** pass SourceIssueId as a real, existing key, confirm the link type name exists on your site, and link any unlinked issues manually rather than re-running.

### 6.4 Order and logical IDs

Issues are created strictly in list order. When an issue is created, its label\[0\] is mapped to the new Jira key. In descriptions of later issues, any text matching E\<number\> (optionally .\<part\>, e.g. E1.2) that is in that map becomes a link to \<base\_url\>/browse/\<KEY\>; unknown matches stay as plain text. Only E-style IDs are matched, so labels such as ai-generated or TS-001 never create links. SourceIssueId is not resolved through this map. **Do:** use an E-style ID as label\[0\] only when later descriptions should link to that issue, and always pass SourceIssueId as a real key.

### 6.5 Description formatting

A string description is split into lines. Lines starting with -  become a bullet list; every other non-empty line becomes its own paragraph; blank lines are dropped. Inside a line, \*\*text\*\* is bold and \*text\* is italic. Headings, numbered lists, links, tables and code blocks are not converted and appear as literal text. A dict description becomes one section per key: the key is turned into a bold heading with only its first letter capitalised (Expected Result becomes "Expected result", expectedResult becomes "Expected result"), list values become bullets and nested dicts become key: value lines. **Do:** send plain lines with -  bullets and bold or italic only, and avoid stray \* characters, which can turn following text italic.

### 6.6 Partial failure and re-runs

If Jira rejects an issue or the request fails, that issue gets a Failed: line and the tool continues with the next one. If an issue that has issueType and SourceIssueId is missing summary or description, the tool stops and returns only Fatal error: '\<field\>'; issues created before that point still exist in Jira but their keys are not returned. The tool does not check for existing issues or links, so re-running a payload creates duplicates. **Do:** validate every issue has summary and description before calling, and check Jira for already-created issues, e.g. by label, before retrying.

### 6.7 Payload shape

The tool reads projectKey, issueType, SourceIssueId and issues directly from inputJSON. If the payload is wrapped again, e.g. {"inputJSON": {...}}, the tool finds no issues and returns an empty string with no error. **Do:** pass the payload object itself as inputJSON.

## 7. Appendix

### 7.1 API workflow

| Step | API call | Purpose |
|---|---|---|
| 1 | secretsmanager:GetSecretValue (once, at module import) | Read base\_url, id and api\_key |
| 2 | POST {base\_url}/rest/api/3/issue (once per issue, in order) | Create the issue with project, summary, issue type, labels and ADF description |
| 3 | POST {base\_url}/rest/api/3/issueLink (once per successfully created issue) | Link the new issue to SourceIssueId using linkType |

### 7.2 Returns

**Success**
```
<issueType> created: <KEY> | Linked to <SourceIssueId> (<linkType>)
<issueType> created: <KEY> | Link to <SourceIssueId> failed → HTTP <status> | Detail: <Jira response body>
Failed: <summary> → HTTP <status> | Detail: <Jira response body>
Failed: <summary> → no issueType supplied in payload
Failed: <summary> → no SourceIssueId supplied in payload
```
One line per issue, in input order. An empty issues list returns an empty string.
**Error**
```
Failed: <summary> → <exception> | Detail: <Jira response body | No response received>
Fatal error: <detail>
```

| Error | Cause | Fix |
|---|---|---|
| Failed: \<summary\> → no issueType supplied in payload | Neither the issue nor the payload sets issueType | Add issueType at the top level or on the issue |
| Failed: \<summary\> → no SourceIssueId supplied in payload | Neither the issue nor the payload sets SourceIssueId, or the key is spelled differently | Add SourceIssueId, spelled exactly, at the top level or on the issue |
| Failed: \<summary\> → HTTP 400 \| Detail: ... | Missing or wrong projectKey, issue type not in the project, sub-task type, required custom fields, Description or Labels not on the create screen, or a label with spaces | Read the Jira detail and correct the payload or the project's issue type configuration |
| Failed: \<summary\> → HTTP 401 \| Detail: ... | Wrong email or API token | Check id and api\_key in the secret |
| Failed: \<summary\> → HTTP 403 \| Detail: ... | Account lacks create permission in the project | Grant "Create issues" in the project |
| \<issueType\> created: \<KEY\> \| Link to \<SourceIssueId\> failed → HTTP 400 / 404 \| Detail: ... | Unknown linkType, or SourceIssueId does not exist or is not visible | Check the link type name and the source key; link the issue manually |
| \<issueType\> created: \<KEY\> \| Link to \<SourceIssueId\> failed → HTTP 403 \| Detail: ... | Account lacks "Link issues" permission | Grant "Link issues" in the project |
| Failed: \<summary\> → \<exception\> \| Detail: No response received | Network or DNS failure reaching Jira | Check base\_url and network access from the pod |
| Fatal error: 'summary' / Fatal error: 'description' | An issue is missing that field; the run stops | Add the field to every issue |
| Fatal error: \<detail\> | Any other exception, e.g. issues is not a list of dicts | Check the payload shape |
| Empty string | issues is empty or missing, often because the payload was wrapped in an extra inputJSON key | Pass the payload object itself as inputJSON |
| RuntimeError: Error retrieving secret: \<detail\> / RuntimeError: Unexpected error: \<detail\> | Secret could not be read when the module was imported; the tool does not load | Check SECRET\_NAME, the region, the Pod Identity association and secretsmanager:GetSecretValue |

### 7.3 Known limitations
- Create-and-link only. It cannot update, transition, comment on, unlink or delete issues.
- Sets only project, summary, issue type, labels and description, plus one issue link. No parent, priority, assignee, components, due date, fix version or custom fields.
- Cannot create sub-task issue types, because no parent is sent.
- One project per call.
- Each issue links to exactly one source issue; SourceIssueId cannot reference a logical ID from the same call.
- If the link fails, the created issue is not rolled back.
- The API token cannot be supplied in the input.
- Description conversion covers paragraphs, -  bullets, bold and italic only.

### 7.4 Security & resilience

**Security**
- Jira credentials are read from AWS Secrets Manager through Pod Identity; none are stored in code. They are read once when the module is imported.
- baseUrl and userEmail in the input override the secret. If baseUrl is overridden, the stored API token is sent to that URL.
- The tool prints the HTTP status and full Jira response body to stdout for every create and link call. Credentials are not printed. Failure lines include the raw Jira response body.

**Resilience**

| Concern | Current state | Recommendation |
|---|---|---|
| Timeout | None; requests.post has no timeout | Pass timeout=(5, 30) to every requests call |
| Retry | None; each create and link call is attempted once | Retry 429 and 5xx with backoff, honouring Retry-After, and guard against duplicates |
| Concurrency | Issues are created and linked one at a time, which preserves order and logical-ID links | Keep sequential creation; use Jira's bulk create endpoint for large batches |
| Input validation | Only checks that inputJSON is a dict and that issueType and SourceIssueId resolve per issue; missing summary/description aborts the run; SourceIssueId existence and baseUrl host are not checked | Validate every issue, projectKey and SourceIssueId before the first call, and restrict baseUrl to your Jira site |
