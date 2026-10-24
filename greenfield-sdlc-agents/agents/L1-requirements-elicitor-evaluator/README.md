# L1-requirements-elicitor-evaluator

## Purpose

`L1-requirements-elicitor`'s own self-check only covers the mechanical
characteristics (Singular, Unambiguous's vague-term scan). The
interpretive characteristics — Complete (does every vision.md item have a
covering FR?), Verifiable (can each FR actually be tested?), Consistent (do
any two FRs contradict?), Feasible/Correct (judgment calls) — need an
independent pass, not the generator grading its own homework.

## What does it do?

Scores the elicitor's draft output against
`L1-requirements-elicitor/evaluation.md`, sourced from
`kb-L1-requirements-quality-standard` for the full ISO/IEC/IEEE 29148
rubric. Fixes what's mechanically fixable (a missing trace that's
obviously findable, an ID gap); escalates what needs new judgment (a
genuine coverage gap, a contradiction between two FRs).

## How does it work?

1. Loads `L1-requirements-elicitor/evaluation.md` as source of truth
2. Re-derives Complete's coverage check independently: builds the set of
   vision.md sections/clauses, the set of sections actually covered by an
   FR's `traces_to`, and checks by set membership — never assumes coverage
   because the FR count "looks about right"
3. Re-checks Verifiable for every FR: could a tester write one pass/fail
   test directly from the statement?
4. Cross-checks every pair of FRs for Consistent — contradiction or
   terminology mismatch
5. Fixes mechanically-recoverable gaps; escalates genuine judgment calls
6. `final_decision` per the standard rule

## Input

- **Source:** agent_output (`L1-requirements-elicitor`'s original input +
  draft output)

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision` — shared shape across all Phase 0/1
  evaluators, see `output_schema.json`
- **Summary:** overall_score, pass/fail, findings breakdown, what was
  fixed, knowledge bases consulted, gaps flagged

## Composition

```
agents/L1-requirements-elicitor-evaluator/
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

prompts/L1-requirements-elicitor-evaluator/
└── instructions.md
```
