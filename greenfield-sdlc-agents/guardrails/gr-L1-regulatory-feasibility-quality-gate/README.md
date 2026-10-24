# gr-L1-regulatory-feasibility-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-vision-regulatory-feasibility-checker-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-vision-regulatory-feasibility-checker-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-regulatory-feasibility-checker-evaluator` re-derives constraint
severity independently and fixes what it can — a false negative here (an
unmitigated Red constraint slipping through) is a compliance risk, not a
quality nuance. This guardrail fires at that point but validates a
different thing: the **resultant** `L1-vision-regulatory-feasibility-checker`
output — its own `items`, with the evaluator's `fixes_applied` resolved in
— is what actually flows to `L1-vision-statement-generator`. This gate
checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-regulatory-feasibility-checker/output_schema.json` (not the
   evaluator's own output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-vision-regulatory-feasibility-checker/evaluation.md`'s
   rubric — above all, the zero-tolerance rule that every Amber/Red
   constraint carries a real mitigation or an explicit legal-review flag,
   re-checked directly on the resultant content, independent of whatever
   the evaluator claims it fixed.

This is NOT a check on the evaluator's own scores/findings/final_decision
— it is an independent re-derivation of the ONE rule this whole pipeline
step exists to enforce, run against what actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a claim,
not a guarantee. If a "fix" left `mitigation` null on a Red
constraint with `requires_legal_review: false`, or a citation still reads
"applicable regulations" instead of a named section, that is exactly the
false negative this evaluator exists to prevent — reaching
`L1-vision-statement-generator` regardless of what the evaluator's own
bookkeeping says.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | amber-red-mitigation-or-legal-review | Rubric adherence | block | critical |
| 3 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 4 | citation-specificity | Rubric adherence | block | critical |
| 5 | overall-status-rationale-specific | Rubric adherence | flag | high |
| 6 | no-downgraded-severity | Rubric adherence | flag | high |
| 7 | legal-review-not-default-escape | Rubric adherence | flag | medium |

## How It Works

```
L1-vision-regulatory-feasibility-checker-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  REGULATORY-FEASIBILITY QUALITY GATE (post_execution, fires on eval)│
│                                                                      │
│  Reconstruct RESULTANT content: constraints/overall_status/          │
│  open_items with fixes_applied[].before→after resolved in            │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: rationale/mitigation full-text fields present, citation shape, enums? │
│  2. Every Amber/Red: mitigation OR requires_legal_review?    │
│     (re-checked on the RESULTANT content — zero tolerance)          │
│  3. CON-NN / OI-NN ids sequential, no gaps/duplicates?               │
│  4. citation.regulation is a specific section, not a generic phrase?│
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  5. overall_status.rationale names the driving constraint?   │
│  6. severity actually matches what the rationale describes?          │
│  7. requires_legal_review not overused as a blanket escape?          │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant regulatory-feasibility content flows to L1-vision-statement-generator
```

## File Structure

```
gr-L1-regulatory-feasibility-quality-gate/
├── config.yml                                     # Rail configuration
├── prompts.yml                                    # LLM evaluation prompt (7 checks)
├── gr-L1-regulatory-feasibility-quality-gate.co    # LLM-only Colang flow
├── regulatory_feasibility_quality_gate.co          # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                      # Deterministic Python (schema, zero-tolerance mitigation rule, citation specificity)
├── spec.yaml                                       # Guardrail specification
└── README.md                                       # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-regulatory-feasibility-quality-gate.co`): all 7 checks via `self_check_output`.
- **Python-hybrid** (`regulatory_feasibility_quality_gate.co`): the 4 deterministic checks (1-4) — including the zero-tolerance mitigation rule — reconstruct the resultant content and validate it directly in `actions.py`; the LLM handles the 3 genuinely semantic checks (5, 6, 7).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — Red constraint properly mitigated, specific citation:

```json
{
  "constraints": [
    {"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "kb-L2-domain-regulatory", "regulation": "Food Safety Act 1990, s.19"}, "rationale": "Registration required before trading; not yet structured for it", "mitigation": "Register with local authority 28 days before trading start", "requires_legal_review": false, "confidence": 0.9, "reasoning": "Directly required for any food business"}
  ],
  "overall_status": {"status": "Amber", "rationale": "CON-01 (Red) has a precedented mitigation, discounted one level per the stated rule"},
  "open_items": []
}
```

**Invalid resultant output (expected: "no")** — same Red constraint, but mitigation is null and requires_legal_review is false, even after evaluation concluded:

```json
{
  "constraints": [
    {"id": "CON-01", "name": "Food business registration", "status": "Red", "citation": {"source_reference": "kb-L2-domain-regulatory", "regulation": "Food Safety Act 1990, s.19"}, "rationale": "Registration required before trading; not yet structured for it", "mitigation": null, "requires_legal_review": false, "confidence": 0.9, "reasoning": "..."}
  ],
  "overall_status": {"status": "Red", "rationale": "..."},
  "open_items": []
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully-mitigated resultant content | None | "yes" |
| Unmitigated Amber/Red | mitigation=null, requires_legal_review=false | "no" |
| Generic citation | regulation = "applicable regulations" | "no" |
| ID gap | CON-01 then CON-03, no CON-02 | "no" |
| Missing full-text field | `rationale` empty/absent | "no" |
| Vague overall_status rationale | "some constraints need attention" | "no" |
| Downgraded severity | rationale describes a hard blocker, status="Green" | "no" |
| requires_legal_review overused | every single Amber/Red constraint flagged for legal review | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-regulatory-feasibility-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean, fully-mitigated resultant content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Fully-mitigated resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<unmitigated Red constraint JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Unmitigated Red constraint blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_regulatory_feasibility_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "constraints": [{
        "id": "CON-01", "name": "Food business registration", "status": "Red",
        "citation": {"source_reference": "kb-L2-domain-regulatory", "regulation": "Food Safety Act 1990, s.19"},
        "rationale": "r" * 30, "mitigation": None, "requires_legal_review": False,
        "confidence": 0.9, "reasoning": "s" * 25,
    }],
    "overall_status": {"status": "Red", "rationale": "t" * 20},
    "open_items": [],
}}})

result = await check_regulatory_feasibility_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # unmitigated Red caught, zero tolerance
```
