# L1-requirements-prd-composer-evaluator

## Purpose

`L1-requirements-prd-composer`'s own self-check only covers mechanical
carry-forward (FR count, obviously-empty NFR tables). Whether every FR
genuinely kept its full statement, whether every nfr-spec.md boundary
condition landed on the RIGHT FR (not just landed somewhere), whether every
Assumption/Constraint/Risk is actually traceable rather than plausible-
sounding, and whether success metrics genuinely stayed out — these need an
independent pass, not the generator grading its own homework.

## What does it do?

Scores the composer's draft output against
`L1-requirements-prd-composer/evaluation.md`. Independently re-derives
zero-drop composition: builds the set of FR-ids from `requirements_output`
and checks every one appears in `generator_output`'s `requirements[]`;
builds the set of boundary conditions per FR from `nfr_spec_output` and
checks each one appears in that SAME FR's `nfrs[]`, not just somewhere in
the document. Re-checks every Assumption/Constraint/Risk against
`vision_output`'s regulatory_posture/open_risks or a specific FR. Fixes
what's mechanically recoverable; escalates genuine judgment calls.

## How does it work?

1. Loads `L1-requirements-prd-composer/evaluation.md` as source of truth
2. Retrieves `prd.md` from s3 via
   `generator_output.content.artifacts[0].storage.location` — items carry
   full FR/NFR text already, but Assumptions/Constraints/Risks and the
   Executive Summary are condensed in items, so the full prose lives only
   in the document
3. Re-derives the zero-drop FR check by set membership against
   `original_input.requirements_output`
4. Re-derives the zero-drop NFR check per-FR, per-category against
   `original_input.nfr_spec_output` — a boundary condition attached to the
   wrong FR is caught here, not just a missing one
5. Cross-checks every Assumption/Constraint/Risk against
   `original_input.vision_output`'s regulatory_posture/open_risks, or a
   specific FR if tagged as a requirement-level refinement
6. Confirms no success-metrics field or claim was smuggled into items or
   the retrieved `prd.md`
7. Fixes mechanically-recoverable gaps; if a fix touches content also in
   `prd.md` (an FR's NFR row, an assumption's text), corrects the document
   too and overwrites it at the SAME s3 location
8. `final_decision` per the standard rule

## Input

- **Source:** agent_output (`L1-requirements-prd-composer`'s original input
  + draft output)

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision` — shared shape across all Phase 0/1
  evaluators, see `output_schema.json`
- **Summary:** overall_score, pass/fail, zero-drop check results, what was
  fixed, knowledge bases consulted, gaps flagged

## Composition

```
agents/L1-requirements-prd-composer-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-minor-fix.json
│   ├── output-01-minor-fix.json
│   ├── input-02-legitimate-failure.json
│   └── output-02-legitimate-failure.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-coverage-gap.json
    └── golden-02-coverage-gap.json

prompts/L1-requirements-prd-composer-evaluator/
└── instructions.md
```
