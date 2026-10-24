# gr-L1-market-analysis-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-vision-market-analyzer-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-vision-market-analyzer-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-market-analyzer-evaluator` scores `L1-vision-market-analyzer`'s
draft output against `L1-vision-market-analyzer/evaluation.md` — with an
exhaustive citation check as its primary job — and fixes what it can. This
guardrail fires at that point but validates a different thing: the
**resultant** `L1-vision-market-analyzer` output — its own `items` across
all five dimensions (`competitor_matrix`, `market_sizing`,
`industry_trends`, `customer_insights`, `pricing_benchmarks`, `swot`), with
the evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-vision-statement-generator`. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-market-analyzer/output_schema.json` (not the evaluator's own
   output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-vision-market-analyzer/evaluation.md`'s
   Quality Gates (100% citation coverage across every citation-bearing
   field above all else, sequential IDs per category, SWOT items naming a
   specific entry, no fabricated sizing/trend/insight/pricing figures, an
   honest per-dimension data-sufficiency verdict)?

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's a check on whether evaluation, having concluded, actually produced
schema-valid, citation-complete content ready for the next pipeline step.

**Why it matters:** the evaluator's entire reason for existing is to catch
a missing citation the generator's own self-check overlooked. If the
evaluator reports `fixed_and_approved` but a competitor entry (or a
market-sizing, industry-trend, customer-insight, or pricing-benchmark
entry) is still missing its `retrieved_date`, or a fix left a citation's
`source_reference` empty, the exact gap this evaluator exists to close
would reach `L1-vision-statement-generator` anyway. This gate is
independent of the evaluator's own self-report.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | citation-completeness-100pct | Rubric adherence | block | critical |
| 4 | swot-reasoning-specific | Rubric adherence | flag | high |
| 5 | no-fabricated-figures | Rubric adherence | block | critical |
| 6 | data-sufficiency-honest | Rubric adherence | flag | medium |

## How It Works

```
L1-vision-market-analyzer-evaluator concludes (scores, fixes, final_decision)
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  MARKET-ANALYSIS QUALITY GATE (post_execution, fires on evaluator)  │
│                                                                      │
│  Reconstruct RESULTANT content: L1-vision-market-analyzer's items   │
│  with fixes_applied[].before→after resolved in                      │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: full-text fields/confidence/reasoning present across    │
│     competitor_matrix, market_sizing (tam/sam/som), industry_trends,│
│     customer_insights, pricing_benchmarks, swot?                    │
│  2. CM-NN / TR-NN / CI-NN / PB-NN / ST/WK/OP/TH-NN ids sequential,   │
│     no gaps/duplicates?                                             │
│  3. EVERY competitor_matrix, market_sizing.{tam,sam,som},            │
│     industry_trends, customer_insights, and pricing_benchmarks      │
│     entry has BOTH source_reference AND retrieved_date?             │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  4. SWOT reasoning names a specific competitor/trend/insight/fact?   │
│  5. No fabricated sizing/trend/insight/pricing figure?                │
│  6. data_sufficiency rationale genuinely honest per dimension,        │
│     not padded?                                                      │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant market-analysis content flows to L1-vision-statement-generator
```

## File Structure

```
gr-L1-market-analysis-quality-gate/
├── config.yml                                # Rail configuration
├── prompts.yml                               # LLM evaluation prompt (6 checks)
├── gr-L1-market-analysis-quality-gate.co     # LLM-only Colang flow
├── market_analysis_quality_gate.co           # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                # Deterministic Python (schema, ID sequencing, citation completeness — all 5 dimensions)
├── spec.yaml                                 # Guardrail specification
└── README.md                                 # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-market-analysis-quality-gate.co`): all 6 checks via `self_check_output`.
- **Python-hybrid** (`market_analysis_quality_gate.co`): the deterministic checks (1, 2, 3) reconstruct the resultant content and validate it directly in `actions.py` across all five dimensions; the LLM handles the 3 genuinely semantic checks (4, 5, 6).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — every citation-bearing entry across all five dimensions cited, sequential ids:

```json
{
  "competitor_matrix": [
    {"id": "CM-01", "name": "Wholesaler A", "positioning": "Volume-focused, low differentiation", "strengths": "Scale, existing distribution", "weaknesses": "No compliance documentation service", "citation": {"source_reference": "kb-L2-domain-market", "retrieved_date": "2026-07-15"}, "confidence": 0.85, "reasoning": "Named category example in the KB, cross-checked against search"}
  ],
  "market_sizing": {
    "tam": {"value": "£30-35bn", "basis": "UK foodservice/wholesale distribution market, annual revenue", "confidence": 0.6, "reasoning": "Illustrative KB figure, not independently re-verified", "citation": {"source_reference": "kb-L2-domain-market#market-sizing", "retrieved_date": "2026-07-15"}},
    "sam": {"value": "£2-4bn", "basis": "Independent/regional producer + HORECA buyer addressable spend", "confidence": 0.55, "reasoning": "Illustrative KB figure scoped to the target segment", "citation": {"source_reference": "kb-L2-domain-market#market-sizing", "retrieved_date": "2026-07-15"}},
    "som": {"value": "£5-15m", "basis": "Year 1-2 achievable revenue for a compliance-enabled entrant", "confidence": 0.5, "reasoning": "Illustrative KB figure, low confidence given no primary research yet", "citation": {"source_reference": "kb-L2-domain-market#market-sizing", "retrieved_date": "2026-07-15"}}
  },
  "industry_trends": [
    {"id": "TR-01", "statement": "Rising consumer demand for traceability/provenance data", "direction": "growing", "confidence": 0.7, "reasoning": "Directly named in the KB's Industry Trends section", "citation": {"source_reference": "kb-L2-domain-market#industry-trends", "retrieved_date": "2026-07-15"}}
  ],
  "customer_insights": [
    {"id": "CI-01", "insight": "Producers cite compliance paperwork as their top onboarding friction", "segment": "producer-side", "confidence": 0.65, "reasoning": "Directly named in the KB's Customer Insights section", "citation": {"source_reference": "kb-L2-domain-market#customer-insights", "retrieved_date": "2026-07-15"}}
  ],
  "pricing_benchmarks": [
    {"id": "PB-01", "subject": "market norm", "price_point": "2-5% commission per transaction", "model": "commission", "confidence": 0.6, "reasoning": "Directly named in the KB's Cost Structure Norms section", "citation": {"source_reference": "kb-L2-domain-market#cost-structure-norms", "retrieved_date": "2026-07-15"}}
  ],
  "swot": {
    "strengths": [{"id": "ST-01", "statement": "Compliance-first positioning vs CM-01's volume focus", "confidence": 0.8, "reasoning": "Derived directly from CM-01's weakness"}],
    "weaknesses": [], "opportunities": [], "threats": []
  },
  "data_sufficiency": {"status": "sufficient", "rationale": "3 competitor categories reviewed via KB + search; market_sizing, industry_trends, customer_insights, and pricing_benchmarks all grounded in kb-L2-domain-market"}
}
```

**Invalid resultant output (expected: "no")** — CM-01 is missing `retrieved_date`, an incomplete citation even after evaluation concluded (other dimensions omitted here for brevity, but a real check requires all five present):

```json
{
  "competitor_matrix": [
    {"id": "CM-01", "name": "Wholesaler A", "positioning": "...", "strengths": "...", "weaknesses": "...", "citation": {"source_reference": "kb-L2-domain-market"}, "confidence": 0.85, "reasoning": "..."}
  ],
  "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
  "data_sufficiency": {"status": "sufficient", "rationale": "..."}
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully-cited resultant content across all 5 dimensions | None | "yes" |
| Missing retrieved_date | CM-01.citation has source_reference only | "no" |
| Missing source_reference | CM-02.citation has retrieved_date only | "no" |
| ID gap | CM-01 then CM-03, no CM-02 | "no" |
| Missing full-text field | `strengths` empty/absent | "no" |
| Generic SWOT reasoning | `detail` = "competitive pressure exists" with no id | "no" |
| Padded "sufficient" verdict | data_sufficiency honesty questionable given thin matrix | "no" |
| market_sizing missing citation | `tam` populated but no `citation` | "no" |
| industry_trends ID gap | TR-01 then TR-03, no TR-02 | "no" |
| customer_insights invalid segment/missing field | `insight` empty/absent | "no" |
| pricing_benchmarks invalid model | `model` = "flat_fee" (not in enum) | "no" |
| Fabricated sizing figure | `som.value` present but no real citation behind it | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-market-analysis-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean, fully-cited resultant content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Fully-cited resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<content missing a retrieved_date>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Incomplete citation blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_market_analysis_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "competitor_matrix": [{
        "id": "CM-01", "name": "Wholesaler A",
        "positioning": "p", "strengths": "s", "weaknesses": "w",
        "citation": {"source_reference": "kb-L2-domain-market"},  # missing retrieved_date
        "confidence": 0.85, "reasoning": "r" * 25,
    }],
    "market_sizing": {
        "tam": {"value": "£30bn", "basis": "b", "confidence": 0.6, "reasoning": "r" * 25, "citation": {"source_reference": "kb", "retrieved_date": "2026-07-15"}},
        "sam": {"value": "£3bn", "basis": "b", "confidence": 0.6, "reasoning": "r" * 25, "citation": {"source_reference": "kb", "retrieved_date": "2026-07-15"}},
        "som": {"value": "£10m", "basis": "b", "confidence": 0.5, "reasoning": "r" * 25, "citation": {"source_reference": "kb", "retrieved_date": "2026-07-15"}},
    },
    "industry_trends": [],
    "customer_insights": [],
    "pricing_benchmarks": [],
    "swot": {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []},
    "data_sufficiency": {"status": "sufficient", "rationale": "x"},
}}})

result = await check_market_analysis_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # CM-01's missing retrieved_date caught, even with every other dimension otherwise clean
```
