# L0-jira-epic-formatter-and-uploader

## Purpose

This utility agent is the controlled hand-off between approved inception outputs and Jira. It accepts evaluator-approved Epic and Feature AgentOutputs, validates that they belong to the same workflow execution, converts the approved content into one flat Jira upload payload, invokes the Jira uploader exactly once, and returns a reconciled upload-status AgentOutput. It does not return, log, or persist the internal Jira payload.

## What does it do?

The agent:

- Accepts approved outputs from `L0-epics-creator-evaluator` and `L0-feature-decomposer-evaluator`.
- Verifies both upstream outputs succeeded, passed evaluation, and have a final decision of `approved` or `fixed_and_approved`.
- Requires both inputs to contain the same `workflow_execution_id` and inherits that ID unchanged.
- Uses only evaluator-approved `content.items.epics` and `content.items.features` as its working sets.
- Validates required fields, duplicate logical IDs, parent-child relationships, source references, project alignment, pillars, acceptance criteria, requirements, dependencies, risks, and MVP classification.
- Drops only records covered by explicit drop rules and reports those drops separately.
- Builds all Epic issues first and all Feature issues second so logical parent IDs can be resolved in one upload pass.
- Produces string or string-array description values and leaves Jira/ADF formatting to the upload tool.
- Invokes `tool-L1-sfi-jira-epics-uploader-secrets-manager` once with the complete validated payload.
- Parses every success, failure, and fatal response line.
- Reconciles expected, created, failed, dropped, and unreconciled issue counts.
- Returns `success`, `partial_success`, or `failed` in a standard `jira_upload_status` response.

## How does it work?

1. Read the Epic evaluator output, Feature evaluator output, and optional Jira runtime parameters.
2. Validate upstream status, evaluation approval, and final decisions.
3. Confirm both upstream outputs share the same `workflow_execution_id`.
4. Extract the approved Epic and Feature collections only.
5. Validate required fields and remove explicitly droppable duplicates or invalid parent references.
6. Determine the Jira project key from the runtime override or the common approved Epic project.
7. Format all retained Epic issues followed by all retained Feature issues.
8. Validate the complete internal payload before any Jira call.
9. Invoke the Jira upload tool exactly once without retrying.
10. Parse the tool response and reconcile each result with a submitted issue.
11. Return only the final upload-status AgentOutput and plain-text execution summary.

## Input

- **Source:** `agent_output`
- **Required:** `epic_evaluator_output` — Approved AgentOutput from `L0-epics-creator-evaluator`.
- **Required:** `feature_evaluator_output` — Approved AgentOutput from `L0-feature-decomposer-evaluator`.
- **Optional:** `projectKey` — Explicit Jira project-key override. It must be supplied or grounded in the retained Epic set.
- **Optional:** `site` — Jira site parameter required by the upload tool when applicable.
- **Optional:** `base_url` — Jira base URL used only to construct the returned project URL.
- **Direct input:** Not accepted.
- **File upload:** Not accepted.

## Output

- **Type:** `jira_upload_status`
- **Status:** `success`, `partial_success`, or `failed`
- **Items:** Agent status, tool-call result, Jira project information, reconciled issue counts, created issues, failed issues, dropped records, and response-reconciliation details.
- **Metadata:** Agent/version IDs, a fresh `execution_id`, the inherited `workflow_execution_id`, source agent IDs, and input counts.
- **Summary:** Plain-text bullets covering the tool outcome, expected/created/failed/dropped counts, validation outcomes, project URL and returned keys, guardrails, tool invocation, failures, and gaps.
- **Excluded:** Internal Jira payload, full Epic/Feature content, artifacts, persistence metadata, evaluator findings, and private reasoning.

## Key Behaviour and Failure Handling

- Jira is not invoked if upstream approval fails, workflow IDs differ, no valid Epic remains, project grounding fails, or a blocking validation error remains.
- Valid Epics may be uploaded without Features when no valid Feature remains.
- The upload tool is called once at most. The agent never retries.
- `partial_success` is used only when at least one issue is created and at least one submitted issue fails or is unreconciled without a fatal call-level error.
- A fatal tool response, zero created issues, or a skipped tool call results in `failed`.
- Missing tool results are reported as unreconciled; they are never fabricated.

## Composition

```text
agents/L0-jira-epic-formatter-and-uploader/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-success.json
│   ├── output-01-success.json
│   ├── input-02-upstream-rejection.json
│   └── output-02-upstream-rejection.json
└── golden/v1.0.0/
    ├── input-golden-01-success.json
    ├── golden-01-success.json
    ├── input-golden-02-failure.json
    └── golden-02-failure.json

prompts/L0-jira-epic-formatter-and-uploader/
└── instructions.md
```

## Upstream and Downstream

- **Upstream:** `L0-epics-creator-evaluator`, `L0-feature-decomposer-evaluator`
- **Downstream:** Workflow orchestrator and audit logging consume the status AgentOutput; Jira receives the created Epic and Feature issues through the uploader tool.
