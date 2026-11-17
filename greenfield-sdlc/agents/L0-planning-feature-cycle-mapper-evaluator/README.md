# L1-planning-feature-cycle-mapper-evaluator

## Purpose

Paired evaluator for `L1-planning-feature-cycle-mapper`. The mapper only runs a light self-check; this agent does the deep check. It re-derives the cycle plan independently from the mapper's own input, scores the mapper's output against the mapper's `evaluation.md`, fixes what can be fixed, and decides whether the plan can go to `L1-planning-story-decomposer`. It never trusts the mapper's execution summary or self-check claims.

## What does it do?

It accepts:
- `generator_output` — the mapper's AgentOutput (feature assignments, gaps, summary table)
- `generator_input` — the exact input the mapper received (prioritized backlog, `pi_cycles`, capacity, MVP scope)

It produces `cycle_plan_evaluation.json` with:
- **Final decision**: `approved`, `fixed_and_approved` or `rejected`
- **Overall score** (0–10) and **six metric scores** before and after fixes, against the mapper's thresholds
- **Quality gates**: one entry per gate in the mapper's `evaluation.md` — pass, fail_fixed or fail_unfixed
- **Findings**: severity, category, JSON location, expected vs actual value, whether and how it was fixed, citation
- **Corrected output**: the full corrected mapper output, only when the decision is `fixed_and_approved`
- **Gaps**: the action needed when the plan is rejected or the evaluation can't run

## How does it work?

1. Validates inputs; fails with INSUFFICIENT_CONTEXT if `generator_output` or `generator_input` is missing.
2. Validates the mapper output against the mapper's `output_schema.json`.
3. Re-derives the plan from `generator_input` using the mapper's rules: exclusions, rank-order placement, capacity, Story A / Story B splits, story numbering.
4. Compares the output with the re-derived plan field by field, and checks every mapper quality gate.
5. Raises findings (blocker / major / minor) with concrete expected and actual values.
6. Fixes every fixable finding by applying the re-derived value and re-rendering the summary table; re-checks the corrected output once.
7. Scores before and after, then decides:
   - **approved** — zero findings
   - **fixed_and_approved** — all findings fixed and every gate and threshold passes after fixing
   - **rejected** — a finding cannot be fixed (plan invented from insufficient input, mapper failed on valid input) or a threshold is still missed

## Input

- **Source:** agent output (`L1-planning-feature-cycle-mapper`), direct input, or file upload (.json)
- **Required:** `generator_output` — mapper AgentOutput (schema_version 3.x)
- **Required:** `generator_input` — the exact input given to the mapper
- **Optional:** `max_fix_rounds` — fix-and-recheck rounds before rejecting (default 1)

## Output

- **Type:** `cycle_plan_evaluation`
- **Items:** `evaluated`, `final_decision`, `overall_score`, `scores`, `quality_gates`, `findings`, `corrected_output`, `gaps`
- **Metadata:** confidence and citation on every finding
- **Summary:** decision, findings by severity, gates, KBs, guardrails, gaps

Example finding (golden 01):

```json
{
  "finding_id": "FND-01", "severity": "blocker", "category": "capacity",
  "location": "content.items.feature_assignments[5].cycle_id",
  "summary": "F-03.6 placed in C-05 beside F-03.4: 6 + 5 = 11 exceeds capacity 8.",
  "expected": "C-06 (cycle_number 6, end_cycle_id C-06)", "actual": "C-05 (cycle_number 5, end_cycle_id C-05)",
  "fix_applied": true, "fix_summary": "Moved F-03.6 to C-06, updated cycle numbers and summary to the re-derived placement.",
  "confidence": 0.98,
  "citation": { "source_reference": "L1-planning-feature-cycle-mapper/evaluation.md", "source_location": "QG-04 effort per cycle ≤ capacity" }
}
```

## Examples and golden set

| Case | Mapper output | Decision |
|---|---|---|
| examples/01 | Correct KYC plan | approved, 9.7, 0 findings |
| examples/02 | generator_input missing | status failed, INSUFFICIENT_CONTEXT |
| golden/01 | Payouts plan with 4 seeded defects (over-capacity cycle, wrong Story B effort, wrong cycle_number, missing table row) | fixed_and_approved, 9.7 after fixes |
| golden/02 | Plan invented from an assumed 8-cycle PI (pi_cycles missing) | rejected, 4.2, 2 blockers |

## Composition

```
agents/L1-planning-feature-cycle-mapper-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-clean-kyc-plan.json
│   ├── output-01-clean-kyc-plan.json
│   ├── input-02-missing-generator-input.json
│   └── output-02-missing-generator-input.json
└── golden/v1.0.0/
    ├── input-golden-01-payouts-seeded-defects.json
    ├── golden-01-payouts-seeded-defects.json
    ├── input-golden-02-invented-plan.json
    └── golden-02-invented-plan.json

prompts/L1-planning-feature-cycle-mapper-evaluator/
└── instructions.md
```
