# L1-vision-regulatory-feasibility-checker-evaluator

## Purpose

This is the highest-stakes evaluator in Phase 0. A false negative here — a
Red constraint that slips through unmitigated, or gets quietly relabeled
Amber to avoid writing a mitigation — is a compliance risk that reaches a
human decision-maker looking already handled. This agent's entire job is to
re-derive severity independently rather than trust the generator's own
classification at face value.

## What does it do?

Accepts the original input and draft output from
`L1-vision-regulatory-feasibility-checker` and produces:
- Independent scores across 5 dimensions
- A severity-mismatch check: does each constraint's rationale actually
  support its stated Green/Amber/Red label?
- Validation of any overall_status "discount" claim — confirming every
  Amber/Red item genuinely has a non-legal-review mitigation before
  accepting a one-level-better verdict
- Fixes for mechanically-correctable issues; escalation for any
  genuinely-unmitigated Red constraint, with zero exceptions

## How does it work?

1. Ingests the generator's original input and draft output
2. Loads `L1-vision-regulatory-feasibility-checker/evaluation.md` as the
   scoring source of truth, plus `kb-L1-regulatory-frameworks-index` to
   independently sanity-check citations
3. Checks every constraint's citation, mitigation/legal-review status, and
   whether its severity label actually matches its rationale
4. Validates any claimed overall_status discount against its precondition
5. Fixes mechanical issues; escalates anything requiring a mitigation this
   evaluator can't independently justify from the KB

## Input

- **Source:** agent_output from `L1-vision-regulatory-feasibility-checker`
- **Required:** `original_input`, `generator_output`

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `final_decision` — see `output_schema.json`
- **Summary:** overall score, severity-mismatch findings, discount validation
  result, guardrail results

## Composition

```
agents/L1-vision-regulatory-feasibility-checker-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-mislabeled-severity.json
│   ├── output-01-mislabeled-severity.json
│   ├── input-02-invalid-discount.json
│   └── output-02-invalid-discount.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-unmitigated-red.json
    └── golden-02-unmitigated-red.json

prompts/L1-vision-regulatory-feasibility-checker-evaluator/
└── instructions.md
```
