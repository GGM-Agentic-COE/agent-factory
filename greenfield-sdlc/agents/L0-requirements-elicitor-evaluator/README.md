# L0-requirements-elicitor-evaluator

## Purpose

The elicitor's own self-check only confirms each requirement is Singular and
Unambiguous. This agent is the independent check (S6) for the rest: are the
requirements Complete against the vision, Verifiable by a tester, and
Consistent with each other? Its corrected output, not the raw elicitor
output, is what `L0-nfr-classifier` and `L0-prd-composer` build on.

## What does it do?

Accepts `L0-requirements-elicitor`'s output plus the original vision input
and produces:
- The **corrected requirement set** — `functional_requirements[]` and
  `compound_splits[]` in exactly the elicitor's structure, with every fix
  already applied
- An **evaluation block**:
  - `scores` — faithfulness, hallucination, consistency, relevance,
    reasoning quality, citation completeness
  - `overall_score` (0-10) and `pass`
  - `findings[]` — pass/fail per gate, each citing an ISO/IEC/IEEE 29148
    characteristic
  - `fixes_applied[]` — before/after and the reasoning for every change
  - `final_decision` — approved, fixed_and_approved, or escalate_to_hitl

It writes nothing to GitHub or blob storage. All corrections live in the
JSON output.

## How does it work?

1. Inherits `workflow_execution_id` from the elicitor's output and generates
   a fresh `execution_id`
2. Retrieves the elicitor's evaluation file and
   `kb-L0-requirements-quality-standard` from GitHub
3. Approves a legitimate INSUFFICIENT_CONTEXT (status: failed) as-is —
   never fabricates requirements to "fix" an honest refusal
4. **Complete:** builds the set of vision.md sections/clauses and the set
   covered by FR citations; any uncovered section is a gap
5. **Verifiable:** checks a tester could write one pass/fail test from each
   statement alone
6. **Consistent:** compares FRs touching the same entity/state for
   contradictions or terminology mismatches
7. **Singular/Unambiguous:** spot-checks the elicitor's mechanical
   self-check rather than re-running it
8. Fixes grounded gaps in the JSON (e.g. adds an FR from a vision.md clause
   the elicitor missed); escalates anything needing new scope judgment
9. Emits the corrected JSON, the evaluation block, and a plain-text
   execution summary

## Input

- **Source:** agent_output from `L0-requirements-elicitor`
- **Required:** `original_input` — the elicitor's input, including the
  vision output used for the coverage check
- **Required:** `generator_output` — the elicitor's JSON output
- **Required:** `github-requirements-evaluator-folder-location`,
  `github-requirements-evaluator-repo-name`,
  `github-requirements-evaluator-branch` — where the elicitor's evaluation
  file lives
- **Required:** `github-requirements-elicitor-kb-folder-location`,
  `github-requirements-elicitor-kb-repo-name`,
  `github-requirements-elicitor-kb-branch` — where
  `kb-L0-requirements-quality-standard` lives

## Output

- **Type:** `requirements` (same structure as the elicitor) plus `evaluation`
- **Items:** corrected `functional_requirements[]`, `compound_splits[]`
- **Evaluation:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision`
- **Summary:** overall score and decision, coverage-check result,
  verifiable/consistent findings, what was modified and why, KBs consulted,
  guardrails, gaps flagged

## Composition

```
agents/L0-requirements-elicitor-evaluator/
├── L0-requirements-elicitor-evaluator-prompt.md
├── evaluation.md
├── spec.yaml
└── README.md
```

Upstream: `L0-requirements-elicitor`.
Downstream: `L0-nfr-classifier`, `L0-prd-composer`.
