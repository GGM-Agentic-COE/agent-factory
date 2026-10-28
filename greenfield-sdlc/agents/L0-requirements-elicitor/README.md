# L0-requirements-elicitor

## Purpose

An approved vision is a direction, not something a team can build or test
against. This agent is the first step of Phase 1: it turns the approved
vision document into a set of functional requirements that are each
Singular, Traceable, and Unambiguous. It refuses to run unless the vision
carries a recorded Product Lead approval, so nothing downstream is built on
an unapproved vision.

## What does it do?

Accepts the approved vision document (read from Confluence) and produces:
- **functional_requirements[]** — one object per atomic, testable capability:
  - `id` (FR-001, FR-002...), `title`, and the `statement` carried verbatim
  - `citation` to the exact vision.md section the FR came from
  - 2-3 `acceptance_criteria` derived directly from the statement
  - `depends_on` (another FR-id or "None"), `priority` (High / Medium / Low)
  - `notes` when the FR came from splitting a compound clause
  - `confidence` and `reasoning`
- **compound_splits[]** — every vision.md clause that bundled two or more
  independently testable capabilities, with the FR-ids it was split into

It writes nothing to any store. The JSON output is the artifact of record;
there is no requirements.md document.

## How does it work?

1. Generates a new `workflow_execution_id` (it is the first agent in the
   Phase 1 run) and a fresh `execution_id`
2. Reads the vision document via `tool-L0-confluence-reader` using the
   supplied page_id
3. Validates the precondition: if the vision did not succeed or has no
   approval comment, returns INSUFFICIENT_CONTEXT and stops
4. Reads the vision section by section (Problem, Target Users, Value
   Proposition, Regulatory Posture, Roadmap Outline, North-Star Metrics) and
   extracts one FR per testable capability
5. Splits any compound clause into separate FRs and records the split in
   `compound_splits[]`
6. Cites every FR to the vision.md section it came from
7. Retrieves `kb-L0-requirements-quality-standard` from GitHub and runs a
   mechanical self-check only: no unqualified vague terms, no remaining
   compound clauses, sequential IDs, every FR cited
8. Emits the JSON and a plain-text execution summary. Deeper checks
   (coverage, testability, consistency) are left to
   `L0-requirements-elicitor-evaluator`

## Input

- **Source:** direct input (runtime parameters); the vision document is read
  from Confluence
- **Required:** `confluence_vision_page_id` — Confluence page_id of the
  approved vision document
- **Required:** `github-requirements-elicitor-kb-folder-location`,
  `github-requirements-elicitor-kb-repo-name`,
  `github-requirements-elicitor-kb-branch` — where
  `kb-L0-requirements-quality-standard` lives in GitHub

## Output

- **Type:** `requirements`
- **Items:** `functional_requirements[]`, `compound_splits[]`
- **Metadata:** every FR carries `citation`, `confidence` and `reasoning`
- **Summary:** FR count and splits made, which clauses were split and why,
  self-check changes, KB consulted, guardrails, tools invoked, gaps flagged

## Composition

```
agents/L0-requirements-elicitor/
├── L0-requirements-elicitor-prompt.md
├── spec.yaml
└── README.md
```

Upstream: Phase 0 human approval gate (approved vision in Confluence).
Downstream: `L0-requirements-elicitor-evaluator`.
