# L1-inception-task-generator-evaluator

## Purpose

The generator's own self-check is a light, mechanical pass — complete? no placeholders? IDs valid? It never re-derives whether a task type was actually justified, whether an oversized task should have been split differently, or whether a feature quietly fell through the cracks. This agent is the paired evaluator (S6 pattern): it takes the SAME source data the generator received and independently re-judges every task's type, effort, and dependencies, confirms every feature is covered, and fixes what's wrong — in both the structured items and the `task-breakdown.md` document itself when the document is wrong.

## What does it do?

Accepts:
- `generator_output` — the full AgentOutput from L1-inception-task-generator
- The same `features`, `acceptance_criteria`, and `max_task_effort_hours` the generator was given

Produces:
- `verification_results[]` — one independently-rejudged entry per task, checking task_type_justified, effort_within_ceiling, and dependency_correct against source data and the KB
- `feature_coverage[]` — one entry per input feature, catching any feature silently missing from both tasks and gaps
- `fixes_applied[]` — any correction made, and whether it also required correcting the document (including inserting a new task and renumbering ids, for a missed split)
- `guardrail_rechecks[]` — independent re-verification of the generator's own guardrail claims (never trusted at face value)
- `verdict` — `approved` / `fixed_and_approved` / `rejected`, with faithfulness/hallucination/consistency/citation scores
- A re-uploaded `task-breakdown.md` at the SAME artifact id and location, only if a fix touched the document

## How does it work?

1. Retrieve the generator's items AND the full document from `generator_output.content.artifacts[0].storage.location` — items' distilled summaries aren't enough for full-content scoring.
2. Independently apply `kb-L1-task-decomposition-best-practices`' selection rule, split-ceiling procedure, and dependency-inference patterns to each task — never read the generator's type/effort/dependency choices as ground truth.
3. Check every input feature has at least one task, or a gap that holds up against the KB's "when a feature can't be decomposed" criteria — a feature with neither is always a blocker.
4. Re-verify any duplicate_flag via an independent `tool-L1-jira-fetch-issue` call, not by trusting the generator's stored flag.
5. Re-run each guardrail the generator claims to have passed, independently.
6. For every mismatch or omission, record a fix — including inserting a missed split's second task and renumbering later task ids in the same feature. If the mismatched field also appears in the document, correct it there too and re-upload to the same location/id.
7. Compute the verdict and report it — `rejected` only when a blocker-severity issue can't be confidently fixed (e.g. contradictory source data).

## Input

- **Source:** agent output (`generator_output`) + direct input (the generator's original `features`, `acceptance_criteria`, `max_task_effort_hours`)
- **Required:** `generator_output`, `features` — recomputation is impossible without the original source data, not just the generator's claims
- **Optional:** `acceptance_criteria`, `max_task_effort_hours`, `adjacent_backlog_check` — re-verify duplicate_flag claims via Jira

## Output

- **Type:** `task_breakdown_evaluation`
- **Items:** `verification_results[]`, `feature_coverage[]`, `fixes_applied[]`, `guardrail_rechecks[]`
- **Verdict:** `final_decision` plus faithfulness/hallucination/consistency/citation scores
- **Artifact:** re-uploaded `task-breakdown.md` (same id/location as the generator's), only if a fix touched the document
- **Summary:** plain-text execution_summary covering what was verified, findings, guardrail rechecks, tools invoked, and the final verdict

## Composition

```
agents/L1-inception-task-generator-evaluator/
├── spec.yaml
├── evaluation.md          # this agent's OWN meta-quality bar — NOT the generator's rubric
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-edge-case.json
│   └── output-02-edge-case.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json
    ├── golden-01-happy-path.json
    ├── input-golden-02-edge-case.json
    └── golden-02-edge-case.json

prompts/L1-inception-task-generator-evaluator/
└── instructions.md
```

Wired against: `agents/L1-inception-task-generator/evaluation.md` (referenced as `context.knowledge_bases[0].ref`, the quality rubric this agent applies — never duplicated into its own prompt) and `kb-L1-task-decomposition-best-practices` (the same taxonomy/split/dependency rules the generator uses, re-applied independently).
