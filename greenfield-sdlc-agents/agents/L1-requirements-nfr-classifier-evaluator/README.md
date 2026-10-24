# L1-requirements-nfr-classifier-evaluator

## Purpose

`L1-requirements-nfr-classifier`'s own self-check only covers mechanical
consistency (non-TBD conditions have a source, TBD conditions have source
"—", ids match requirements.md). Whether every genuinely-applicable category
was actually checked per FR, whether a cited source really supports the
number/rule it's attached to, and — critically — whether a TBD the
generator left open was actually resolvable from vision.md's Regulatory
Posture section or kb-L1-enterprise-security and simply missed, all need an
independent pass, not the generator grading its own homework.

## What does it do?

Scores the classifier's draft output against
`L1-requirements-nfr-classifier/evaluation.md`, sourced from
`kb-L1-nfr-classification-taxonomy` for the full six-category method. Fixes
what's mechanically recoverable (a TBD that a real, checkable source
actually already answers); escalates what needs new judgment (a genuine
coverage gap with no grounding to build from).

## How does it work?

1. Loads `L1-requirements-nfr-classifier/evaluation.md` as source of truth
2. Cross-references every `nfr_classifications` entry against
   `original_input` — items already carry every boundary condition in
   full, so there is no separate document to retrieve
3. Re-derives category coverage independently: for every FR, asks
   kb-L1-nfr-classification-taxonomy's own question per category against
   the FR's statement, and checks by set membership against what the
   generator actually classified — a genuinely-applicable category the
   generator skipped is a gap, not a rounding error
4. Re-checks every non-TBD boundary condition's source actually supports the
   number/rule attached to it
5. For every TBD, independently re-checks vision.md's Regulatory Posture
   section and kb-L1-enterprise-security — a TBD that either source actually
   answers is a fixable finding, not an acceptable gap
6. Fixes mechanically-recoverable gaps by writing the grounded value and
   citation directly into items; escalates genuine judgment calls
7. `final_decision` per the standard rule

## Input

- **Source:** agent_output (`L1-requirements-nfr-classifier`'s original
  input + draft output)

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision` — shared shape across all Phase 0/1
  evaluators, see `output_schema.json`
- **Summary:** overall_score, pass/fail, findings breakdown, what was
  fixed, knowledge bases consulted, gaps flagged

## Composition

```
agents/L1-requirements-nfr-classifier-evaluator/
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
    ├── input-golden-02-missed-grounding.json
    └── golden-02-missed-grounding.json

prompts/L1-requirements-nfr-classifier-evaluator/
└── instructions.md
```
