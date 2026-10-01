# L1-vision-statement-generator-evaluator

## Purpose

This is the last automated checkpoint before a human (the Product Lead)
reads `vision.md`. If a serious regulatory finding was dropped anywhere in
the pipeline, this is the last place it can still be caught before it
reaches a person who will reasonably assume nothing was silently lost. This
agent's entire job is verifying that reconciliation is real, not just
claimed in the generator's own execution_summary.

## What does it do?

Accepts the original input (the upstream item sets plus viability_score) and
draft output from `L1-vision-statement-generator`, and produces:
- A reconciliation coverage check: every Amber/Red regulatory constraint_id
  must appear in at least one `open_risks` entry's `related_ids` — checked
  by set membership, not by trusting a count
- A groundedness check: the Amber/Red set rebuilt from
  `regulatory-feasibility.md` itself, so a constraint dropped *before*
  `regulatory_posture` is caught rather than scored as full coverage
- An executive-summary integrity check: every sentence checked individually
  against the sections below it
- A viability_score consistency check across `regulatory-feasibility.md`,
  `original_input`, `items` and `vision.md` — plus a narrative check that a
  capped score is matched by an executive summary naming the constraint that
  caused the cap
- Fixes for mechanically-recoverable gaps (built from the constraint's own
  mitigation_summary); escalation for anything requiring new judgment

## How does it work?

1. Ingests the generator's original input and draft output
2. Reads `vision.md`, `regulatory-feasibility.md`, `idea-brief.json` and
   (optionally) `market-analysis.md` in a single blob-storage call. The brief
   is **JSON**, parsed by key path
3. Reads `L1-vision-statement-generator/evaluation.md` from GitHub with
   `tool-L1-github-reader-using-app` as the scoring source of truth, plus this
   evaluator's `examples/` folder for shape — repo, branch and folders all from
   the request. An unreadable rubric fails with `REFERENCE_UNAVAILABLE` rather
   than scoring against a remembered bar; corrections go back to blob storage
4. Computes the coverage-gap set (Amber/Red constraint_ids minus covered ids)
5. Checks each executive_summary sentence for grounding elsewhere in the document
6. Checks viability_score wasn't silently altered — against
   `regulatory-feasibility.md` as the authoritative source. It is **never
   re-derived here**: that already happened in
   `L1-vision-regulatory-feasibility-checker-evaluator`, and a discrepancy at
   this point is a finding to report, not arithmetic to redo
7. Fixes what's mechanically recoverable and writes changes back into
   `vision.md`; escalates anything requiring new analysis rather than
   inventing content

## Input

- **Source:** agent_output from `L1-vision-statement-generator`
- **Required:** `original_input`, `generator_output`

## Output

- **Type:** `vision_statement` — the generator's own type. This agent
  re-emits the corrected result with the evaluation attached under
  `items.evaluation`, not a separate evaluation-only shape
- **Items:** the generator's full item sections, plus `evaluation` carrying
  `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `reconciliation_check`, `final_decision` — see `output_schema.json`
- **Artifacts:** `vision.md` — re-saved if corrected, otherwise referenced at
  its original location
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
