# L1-vision-market-analyzer-evaluator

## Purpose

`gr-L1-citation-verifier` is a BLOCKER guardrail for `L1-vision-market-analyzer`
— a competitor claim without a citation is exactly the kind of thing a
generator's own basic self-check might miss under time pressure. This
evaluator's job is to check every single competitor entry, not a sample, and
to never fabricate a citation just to make a check pass.

## What does it do?

Accepts the original input and draft output from `L1-vision-market-analyzer`
and produces:
- Independent scores across the rubric's scoring dimensions
- An exhaustive citation-completeness check (100% of competitor_matrix,
  market_sizing tam/sam/som, industry_trends, customer_insights, and
  pricing_benchmarks entries)
- SWOT-item and other findings checking that reasoning names a real
  competitor, trend, insight, or fact — not generic filler
- Fixes for mechanically-correctable issues; escalation for anything requiring
  a real, unavailable citation

## How does it work?

1. Ingests the generator's original input and draft output
2. Loads `L1-vision-market-analyzer/evaluation.md` as the scoring source of truth
3. Checks every competitor_matrix, market_sizing (tam/sam/som),
   industry_trends, customer_insights, and pricing_benchmarks entry's
   citation — exhaustively, across all five dimensions
4. Checks every SWOT item's (and other dimensions') reasoning for real traceability
5. Fixes what's mechanically correctable; escalates uncited/fabricated claims
   rather than inventing a citation to cover them
6. Evaluates a legitimate "insufficient" data_sufficiency verdict for honesty,
   including whether the rationale names which dimensions were thin, not as
   an automatic defect

## Input

- **Source:** agent_output from `L1-vision-market-analyzer`
- **Required:** `original_input`, `generator_output`

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`, `fixes_applied[]`,
  `final_decision` — see `output_schema.json`
- **Summary:** overall score, citation-completeness result, findings, fixes,
  guardrail results

## Composition

```
agents/L1-vision-market-analyzer-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-vague-swot-reasoning.json
│   ├── output-01-vague-swot-reasoning.json
│   ├── input-02-uncited-competitor.json
│   └── output-02-uncited-competitor.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-uncited.json
    └── golden-02-uncited.json

prompts/L1-vision-market-analyzer-evaluator/
└── instructions.md
```
