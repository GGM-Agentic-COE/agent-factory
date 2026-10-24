# L1-vision-market-analyzer

## Purpose

No idea should reach a funding decision without knowing who else is already
solving this problem. This agent makes that check mandatory, grounded, and
consistent — instead of an ad hoc "someone should Google this" step that
gets skipped under time pressure.

## What does it do?

Accepts the problem statement and target users from `L1-vision-idea-intake`
and produces a market analysis across five dimensions:
- **Competitive intelligence** — a competitor matrix (name, positioning,
  strengths, weaknesses), every row citing a real source
- **Market sizing** — a TAM/SAM/SOM-style estimate for the relevant market
  segment, every figure citing a real source or honestly flagging the gap
- **Industry trends** — first-class, citable trend items (direction:
  growing/declining/stable/emerging), not just implicit SWOT context
- **Customer insights** — buyer-/producer-side needs, pain points, and
  behaviors from a market-research lens (distinct from idea-intake's
  `target_users`, which identifies WHO they are, not WHAT they need)
- **Pricing benchmarks** — what comparable products/competitors charge and
  the pricing model (commission, subscription, listing fee, etc.)

Plus a SWOT synthesis drawing on all four dimensions above, and an honest
data-sufficiency verdict — if coverage is genuinely thin for any dimension,
it says so rather than padding to look complete.

## How does it work?

1. Ingests `problem_statement` and `target_users` from the upstream agent's output
2. Queries `kb-L2-domain-market` for relevant distribution-channel,
   player-category, market-sizing, industry-trends, customer-insights, and
   cost-structure/pricing facts
3. Issues `tool-L1-web-search-competitor-scan` queries for anything more
   current than the KB's last review, across all five dimensions
4. Builds the competitor matrix, market sizing (tam/sam/som), industry
   trends, customer insights, and pricing benchmarks — every entry cited,
   no exceptions; a genuine gap is an explicit low-confidence entry or an
   empty array, never a fabricated figure
5. Derives SWOT items, each pointing back to a specific competitor, trend,
   insight, or fact
6. Assesses data sufficiency honestly, noting which dimensions were thin;
   self-checks citation completeness before returning (full scoring
   delegated to `L1-vision-market-analyzer-evaluator`, per S6)

## Input

- **Source:** agent_output from `L1-vision-idea-intake`
- **Required:** `problem_statement`, `target_users[]`
- **Optional:** `known_competitor_list` — candidates the requester already has in mind

## Output

- **Type:** `market_analysis`
- **Items:** `competitor_matrix[]`, `market_sizing` (tam/sam/som),
  `industry_trends[]`, `customer_insights[]`, `pricing_benchmarks[]`,
  `swot` (strengths/weaknesses/opportunities/threats), `data_sufficiency`
  — see `output_schema.json`; items carry the full analysis directly, there
  is no separate document produced
- **Metadata:** competitor/sizing/trend/insight/pricing entries all carry
  `citation` (source + retrieved_date) — this is a BLOCKER guardrail
  (`gr-L1-citation-verifier`), not advisory; SWOT items carry `reasoning`
  pointing to their origin
- **Summary:** competitor/sizing/trend/insight/pricing/SWOT counts, search
  queries run, KB content used, guardrail results, data-sufficiency verdict

## Composition

```
agents/L1-vision-market-analyzer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-internal-tool.json
│   ├── output-01-internal-tool.json
│   ├── input-02-thin-coverage.json
│   └── output-02-thin-coverage.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-thin-coverage.json
    └── golden-02-thin-coverage.json

prompts/L1-vision-market-analyzer/
└── instructions.md
```
