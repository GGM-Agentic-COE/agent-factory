# L1-vision-statement-generator

## Purpose

Three separate analyses (idea, market, regulatory) aren't a decision — the
Product Lead needs one document with a north-star metric and roadmap
outline to approve or reject. This agent is also the last automated
checkpoint before a human reads the output: if a serious regulatory finding
gets dropped between the regulatory-feasibility-checker and this document,
it's this agent's reconciliation logic that would have caught it.

## What does it do?

Accepts the full outputs of `L1-vision-idea-intake`, `L1-vision-market-analyzer`,
and `L1-vision-regulatory-feasibility-checker`, plus a viability score, and
produces one reconciled vision statement:
- Problem, target users, and value proposition carried forward without drift
- Market context condensed to the single most decision-relevant insight
- Regulatory posture with every Amber/Red constraint's mitigation summarized
- North-star metrics and a phase-level roadmap
- **Open risks** — every Amber/Red regulatory constraint MUST appear here,
  tied to a roadmap dependency; this is the concrete test of reconciliation,
  not just summarization
- An executive summary, written last, that introduces no new claims

It produces the `vision.md` artifact only. It does **not** publish it —
that's a separate Utility agent (`L1-confluence-publisher`), per the
Core/Utility split: this agent's logic must not break if the client swaps
Confluence for Notion.

## How does it work?

1. Ingests all three upstream agents' full item sets, plus viability_score
2. Carries problem/users/value-proposition forward verbatim in substance
3. Condenses market SWOT into one paragraph
4. Carries regulatory overall_status forward and summarizes every Amber/Red
   constraint's mitigation
5. Builds north-star metrics and a roadmap, with phase 1 required to address
   the single most severe open risk
6. Builds open_risks — cross-checks that every Amber/Red regulatory
   constraint produced exactly one entry here
7. Writes the executive summary last, as a pure condensation
8. Reports viability_score honestly; does not decide whether to publish
   (that's the workflow's `qg-L1-viability-score` gate, not this agent)

## Input

- **Source:** agent_output from all three upstream Phase 0 generators
- **Required:** `idea_brief_items`, `market_analysis_items`,
  `regulatory_feasibility_items`, `viability_score`

## Output

- **Type:** `vision_statement`
- **Items:** `executive_summary`, `problem_statement`, `target_users`,
  `value_proposition`, `market_context`, `regulatory_posture`,
  `north_star_metrics[]`, `roadmap[]`, `open_risks[]` — see `output_schema.json`
- **Artifacts:** `vision.md`
- **Metadata:** every item carries `confidence` and `reasoning`; carried-forward
  items are checked against their upstream source for drift instead of citation
- **Summary:** metric/roadmap/risk counts, reconciliation decisions,
  viability_score and gate status, guardrail results

## Composition

```
agents/L1-vision-statement-generator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-missing-upstream.json
│   └── output-02-missing-upstream.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-vision-statement-generator/
└── instructions.md
```
