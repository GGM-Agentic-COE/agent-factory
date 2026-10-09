# L1-inception-task-generator

## Purpose

A prioritized or decomposed feature is still too coarse to hand to an engineer — it needs to become concrete, estimable, assignable work units. This agent takes each feature and breaks it into typed tasks (frontend, backend, QA, infra, data, design, devops, documentation), each sized under an effort ceiling and linked by dependency where one task's output gates another.

## What does it do?

Accepts:
- A feature set (id, name, description)
- Optional per-feature acceptance criteria for sharper scoping
- An optional effort ceiling and set of task types to consider

Produces:
- A task list, each tied to its parent feature, typed, estimated, and dependency-linked (structured items)
- A rendered `task-breakdown.md` document with the full per-task detail and rationale
- A gap list for any feature too vague to decompose

## How does it work?

1. Ingest features and (if available) acceptance criteria; reject unknown feature id references.
2. For each feature, infer which task types are genuinely needed — never force a full spread of every type onto every feature.
3. Draft tasks, estimate effort_hours, and split any task that would exceed max_task_effort_hours.
4. Derive task-level dependencies (e.g. QA blocked by implementation; frontend blocked by the backend contract it consumes; cross-feature links inherited from the feature dependency graph, when supplied).
5. Optionally cross-check task titles against an adjacent Jira backlog for duplicates.
6. Render task-breakdown.md.
7. Run a basic self-check (completeness, ID validity, effort-ceiling compliance) before delivery.

## Input

- **Source:** agent output (features.json) + optional agent output or direct input (acceptance criteria)
- **Required:** `features` — feature list from L1-design-feature-decomposer
- **Optional:** `acceptance_criteria` — from L1-design-story-generator, sharpens task scoping
- **Optional:** `task_types` — which categories to consider (default: frontend, backend, qa, infra, data, design)
- **Optional:** `max_task_effort_hours` — split ceiling (default: 16)
- **Optional:** `adjacent_backlog_check` — cross-check against Jira via tool-L1-jira-fetch-issue

## Output

- **Type:** `task_breakdown`
- **Items:** `tasks[]` (id, feature_id, type, effort, dependency links, distilled summary, citation) and `gaps[]` (undecomposable features)
- **Artifact:** `task-breakdown.md` — the full per-feature task table and rationale
- **Metadata:** confidence and citation on every task
- **Summary:** plain-text execution_summary covering counts, split/scoping decisions, KBs/guardrails/tools used, and gaps

## Composition

```
agents/L1-inception-task-generator/
├── spec.yaml
├── evaluation.md
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

prompts/L1-inception-task-generator/
└── instructions.md
```
