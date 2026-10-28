# L1-vision-statement-generator-evaluator

## Purpose

This is the last automated checkpoint before a human (the Product Lead)
reads `vision.md`. If a serious regulatory finding was dropped anywhere in
the pipeline, this is the last place it can still be caught before it
reaches a person who will reasonably assume nothing was silently lost. This
agent's entire job is verifying that reconciliation is real, not just
claimed in the generator's own execution_summary.

## What does it do?

Accepts the original input (all three upstream item sets plus
viability_score) and draft output from `L1-vision-statement-generator`, and
produces:
- A reconciliation coverage check: every Amber/Red regulatory constraint_id
  must appear in at least one `open_risks` entry's `related_ids` — checked
  by set membership, not by trusting a count
- An executive-summary integrity check: every sentence checked individually
  against the sections below it
- A viability_score consistency check against what the generator actually received
- Fixes for mechanically-recoverable gaps (built from the constraint's own
  mitigation_summary); escalation for anything requiring new judgment

## How does it work?

1. Ingests the generator's original input and draft output
2. Loads `L1-vision-statement-generator/evaluation.md` as the scoring source of truth
3. Computes the coverage-gap set (Amber/Red constraint_ids minus covered ids)
4. Checks each executive_summary sentence for grounding elsewhere in the document
5. Checks viability_score wasn't silently altered
6. Fixes what's mechanically recoverable; escalates anything requiring new
   analysis rather than inventing content

## Input

- **Source:** agent_output from `L1-vision-statement-generator`
- **Required:** `original_input`, `generator_output`

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `final_decision` — see `output_schema.json`
- **Summary:** overall score, coverage-gap result, executive-summary
  integrity result, viability_score consistency, guardrail results

## Composition

```
agents/L1-vision-statement-generator-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-coverage-gap.json
│   ├── output-01-coverage-gap.json
│   ├── input-02-unsupported-summary-claim.json
│   └── output-02-unsupported-summary-claim.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-fabricated-risk.json
    └── golden-02-fabricated-risk.json

prompts/L1-vision-statement-generator-evaluator/
└── instructions.md
```
