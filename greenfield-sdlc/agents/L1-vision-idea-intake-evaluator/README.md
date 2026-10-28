# L1-vision-idea-intake-evaluator

## Purpose

Letting a generator grade its own homework defeats the point of a quality
gate. This agent is the independent, different-prompt check the
Generator→Evaluator pattern (S6) requires — it scores
`L1-vision-idea-intake`'s output against a fixed rubric, fixes what's
genuinely fixable, and escalates what isn't, rather than trusting the
generator's own self-assessment.

## What does it do?

Accepts the original input and draft output from `L1-vision-idea-intake` and
produces:
- Independent scores across 5 dimensions (faithfulness, hallucination,
  consistency, relevance, reasoning quality)
- Per-gate findings (pass/fail with a specific reason) against the
  generator's `evaluation.md`
- Fixes for mechanically-correctable issues (e.g. a mislabeled metric
  status), applied directly rather than triggering a full re-generation
- A final decision: approved, fixed_and_approved, or escalate_to_hitl

## How does it work?

1. Ingests the generator's original input and draft output
2. Loads `L1-vision-idea-intake/evaluation.md` as the scoring source of
   truth — does not duplicate its rubric in this agent's own prompt
3. Scores each dimension and records a finding per quality gate/checklist item
4. Applies fixes for anything mechanically correctable, recording before/after
5. Escalates to HITL rather than forcing a passing score on something
   genuinely deficient
6. Approves a legitimate INSUFFICIENT_CONTEXT failure as-is — an honest
   failure is not something to "fix"

## Input

- **Source:** agent_output from `L1-vision-idea-intake`
- **Required:** `original_input`, `generator_output`

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `final_decision` — see `output_schema.json`
- **Summary:** overall score, pass/fail, findings breakdown, fixes applied,
  guardrail results

## Composition

```
agents/L1-vision-idea-intake-evaluator/
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
    ├── input-golden-02-unfixable.json
    └── golden-02-unfixable.json

prompts/L1-vision-idea-intake-evaluator/
└── instructions.md
```
