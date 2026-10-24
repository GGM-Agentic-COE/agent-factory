# gr-L1-vision-statement-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-vision-statement-generator-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-vision-statement-generator-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-statement-generator-evaluator` is the last automated checkpoint
before a human (the Product Lead) reads `vision.md`. This guardrail fires
at that point but validates a different thing: the **resultant**
`L1-vision-statement-generator` output — its own `items`, with the
evaluator's `fixes_applied` resolved in — is what actually reaches that
approval gate. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-statement-generator/output_schema.json` (not the evaluator's
   own output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-vision-statement-generator/evaluation.md`'s
   rubric — above all, the reconciliation-coverage BLOCKER (every
   regulatory constraint covered by `open_risks`), roadmap phase 1
   addressing the worst risk, executive_summary introducing no new claim,
   and the received `viability_score` reported honestly.

This is NOT a check on the evaluator's own scores/findings/final_decision
— it independently re-derives the ONE thing this evaluator exists to
guarantee (nothing regulatory was silently dropped), directly against the
content a human is about to read.

**Why it matters:** nothing downstream of this evaluator catches a dropped
regulatory finding — a human will, and by then it's not "automated"
anymore. `regulatory_posture.constraint_summaries` and `open_risks` are
both fields on this SAME output — the coverage check is entirely
self-contained, no upstream lookup required, which makes an uncovered
constraint slipping through this gate especially avoidable.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | reconciliation-coverage-complete | Rubric adherence | block | critical |
| 4 | roadmap-phase1-addresses-worst-risk | Rubric adherence | flag | high |
| 5 | executive-summary-no-new-claims | Rubric adherence | flag | high |
| 6 | no-publishing-tool-invoked | Rubric adherence | flag | medium |
| 7 | viability-score-honest | Rubric adherence | block | critical |

## How It Works

```
L1-vision-statement-generator-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  VISION-STATEMENT QUALITY GATE (post_execution, fires on evaluator) │
│                                                                      │
│  Reconstruct RESULTANT content: statement items with                │
│  fixes_applied[].before→after resolved in                            │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: all 9 required sections present, lengths/types valid?  │
│  2. NSM-NN / OR-NN ids sequential; roadmap phases 1..N sequential?  │
│  3. Every constraint_id ∈ union(open_risks.related_ids)? (BLOCKER)  │
│  4. Roadmap phase 1 resolves a Red-traced open risk, if one exists? │
│  6. execution_summary shows no Confluence tool invocation?          │
│  7. execution_summary reports the actual received viability_score? │
│  (7 additionally cross-checks against original_input)               │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  5. executive_summary introduces no claim absent elsewhere?          │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant vision.md content reaches the Product Lead approval gate
```

## File Structure

```
gr-L1-vision-statement-quality-gate/
├── config.yml                                # Rail configuration
├── prompts.yml                               # LLM evaluation prompt (7 checks)
├── gr-L1-vision-statement-quality-gate.co     # LLM-only Colang flow
├── vision_statement_quality_gate.co           # Python-hybrid Colang flow (calls actions.py)
├── actions.py                                 # Deterministic Python (schema, coverage BLOCKER, roadmap ordering, viability_score)
├── spec.yaml                                  # Guardrail specification
└── README.md                                  # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-vision-statement-quality-gate.co`): all 7 checks via `self_check_output`.
- **Python-hybrid** (`vision_statement_quality_gate.co`): the 6 deterministic checks (1, 2, 3, 4, 6, 7) reconstruct the resultant content and validate it directly in `actions.py` (7 additionally needs `original_input` for the received `viability_score`); the LLM handles the 1 genuinely semantic check (5).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — the one Amber/Red constraint (CON-02) is covered by OR-01, and roadmap phase 1 resolves it:

```json
{
  "regulatory_posture": {"overall_status": "Amber", "constraint_summaries": [{"constraint_id": "CON-02", "status": "Amber", "mitigation_summary": "Structural mitigation in place"}]},
  "open_risks": [{"id": "OR-01", "description_summary": "Compliance workflow design gap", "source": "regulatory", "related_ids": ["CON-02"]}],
  "roadmap": [{"phase_number": 1, "title": "Compliance workflow", "description_summary": "Close CON-02's gap first", "resolves_risk": "OR-01"}]
}
```

**Invalid resultant output (expected: "no")** — CON-02 exists in `constraint_summaries` but no `open_risks` entry references it:

```json
{
  "regulatory_posture": {"overall_status": "Amber", "constraint_summaries": [{"constraint_id": "CON-02", "status": "Amber", "mitigation_summary": "..."}]},
  "open_risks": [{"id": "OR-01", "description_summary": "A market-only concern", "source": "market", "related_ids": ["WK-01"]}],
  "roadmap": [{"phase_number": 1, "title": "...", "description_summary": "...", "resolves_risk": "OR-01"}]
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully-reconciled resultant content | None | "yes" |
| Coverage gap | CON-02 present but no open_risks references it | "no" |
| Roadmap misordered | Red-traced risk exists, but phase 1 resolves a different risk | "no" |
| Executive summary over-claims | A number/claim absent from any other section | "no" |
| Confluence invoked | execution_summary states a page was created | "no" |
| viability_score misreported | original_input has 6.2, execution_summary omits it or states 7.8 | "no" |
| ID gap | OR-01 then OR-03, no OR-02 | "no" |

## Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-vision-statement-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean, fully-reconciled resultant content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Fully-reconciled resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<coverage gap JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Coverage gap blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_vision_statement_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "executive_summary": {"summary": "x" * 30, "confidence": 0.9, "reasoning": "y" * 25},
    "problem_statement": {"summary": "a" * 20, "confidence": 0.9, "reasoning": "b" * 15},
    "target_users": {"summary": "c" * 20, "confidence": 0.9, "reasoning": "d" * 15},
    "value_proposition": {"summary": "e" * 20, "confidence": 0.9, "reasoning": "f" * 15},
    "market_context": {"summary": "g" * 20, "confidence": 0.9, "reasoning": "h" * 25},
    "regulatory_posture": {"overall_status": "Amber", "constraint_summaries": [{"constraint_id": "CON-02", "status": "Amber", "mitigation_summary": "m"}]},
    "north_star_metrics": [{"id": "NSM-01", "metric": "m", "target": "t", "confidence": 0.9, "reasoning": "r" * 25}],
    "roadmap": [{"phase_number": 1, "title": "t", "description_summary": "d"}],
    "open_risks": [{"id": "OR-01", "description_summary": "a market-only concern", "source": "market", "related_ids": ["WK-01"]}],  # CON-02 never covered
}, "execution_summary": "viability_score: 7.4"}})

result = await check_vision_statement_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # CON-02 coverage gap caught
```
