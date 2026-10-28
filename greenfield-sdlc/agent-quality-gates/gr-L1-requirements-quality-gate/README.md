# gr-L1-requirements-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-elicitor-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-requirements-elicitor-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-elicitor-evaluator` scores `L1-requirements-elicitor`'s
draft requirements against ISO/IEC/IEEE 29148 (via
`L1-requirements-elicitor/evaluation.md` and
`kb-L1-requirements-quality-standard`) and fixes what it can. This
guardrail fires at that point but validates a different thing: the
**resultant** `L1-requirements-elicitor` output — its own `items`, with the
evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-requirements-nfr-classifier` and `L1-requirements-prd-composer`. This
gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-requirements-elicitor/output_schema.json` (not the evaluator's own
   output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy ISO/IEC/IEEE 29148's characteristics:
   sequential/gap-free IDs, integral compound-split references, no
   unqualified vague term, and (semantically) genuine singularity,
   testability, and consistency?

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's an independent re-derivation of requirement quality, run against
what actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a claim,
not a guarantee. If a "fix" added a requirement whose `split_into`
reference doesn't actually exist, or left a vague, unqualified term in a
statement, that's exactly the defect this gate exists to catch —
independent of what the evaluator's own bookkeeping says.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | compound-split-integrity | Rubric adherence | block | high |
| 4 | unambiguous-vague-term-scan | Rubric adherence | block | critical |
| 5 | singular-compound-clause-check | Rubric adherence | flag | high |
| 6 | verifiable-testability-check | Rubric adherence | flag | high |
| 7 | consistent-no-contradiction | Rubric adherence | flag | medium |

## How It Works

```
L1-requirements-elicitor-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  REQUIREMENTS QUALITY GATE (post_execution, fires on evaluator)    │
│                                                                      │
│  Reconstruct RESULTANT content: functional_requirements/            │
│  compound_splits with fixes_applied[].before→after resolved in      │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: id/title/statement/traces_to/confidence/reasoning?       │
│  2. FR-NNN ids sequential, no gaps/duplicates?                      │
│  3. Every compound_splits.split_into id actually exists?            │
│  4. No unqualified vague term (fast/secure/appropriate/...) found?  │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  5. Any FR genuinely joins two independently-testable capabilities?  │
│  6. Could a tester write one pass/fail test from each statement?     │
│  7. Do any two FRs contradict or use inconsistent terminology?       │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant requirements content flows to nfr-classifier / prd-composer
```

## File Structure

```
gr-L1-requirements-quality-gate/
├── config.yml                              # Rail configuration
├── prompts.yml                             # LLM evaluation prompt (7 checks)
├── gr-L1-requirements-quality-gate.co      # LLM-only Colang flow
├── requirements_quality_gate.co            # Python-hybrid Colang flow (calls actions.py)
├── actions.py                              # Deterministic Python (schema, ID sequencing, split integrity, vague-term scan)
├── spec.yaml                               # Guardrail specification
└── README.md                               # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-requirements-quality-gate.co`): all 7 checks via `self_check_output`.
- **Python-hybrid** (`requirements_quality_gate.co`): the 4 deterministic checks (1-4) reconstruct the resultant content and validate it directly in `actions.py`; the LLM handles the 3 genuinely semantic checks (5, 6, 7) — "and" appearing in a statement is not by itself proof of a compound clause (a compound subject like "producer and distributor sign-off" on one testable outcome is not the same defect as two independently testable behaviours joined together), so Singular is judgment, not a regex match.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")**:

```json
{
  "functional_requirements": [
    { "id": "FR-001", "title": "Digital claim submission", "statement": "The system shall allow an employee to submit an expense claim digitally.", "traces_to": "vision.md § Value Proposition", "confidence": 0.93, "reasoning": "Directly restates the value proposition's digital-submission capability." }
  ],
  "compound_splits": []
}
```

**Invalid resultant output (expected: "no")** — an unqualified vague term and an ID gap:

```json
{
  "functional_requirements": [
    { "id": "FR-001", "title": "...", "statement": "The system shall respond fast to buyer searches.", "traces_to": "vision.md § Value Proposition", "confidence": 0.8, "reasoning": "r" },
    { "id": "FR-003", "title": "...", "statement": "The system shall record a completeness score.", "traces_to": "vision.md § North-Star Metric(s)", "confidence": 0.8, "reasoning": "r" }
  ],
  "compound_splits": []
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean resultant content | None | "yes" |
| Unqualified vague term | "shall respond fast" with no number | "no" |
| Qualified term (should pass) | "shall respond within 200ms" | "yes" |
| ID gap | FR-001 then FR-003, no FR-002 | "no" |
| Broken split reference | compound_splits references FR-099, not present | "no" |
| Split with only 1 id | split_into: ["FR-001"] | "no" |
| Missing traces_to | An FR with no traces_to field | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-requirements-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant requirements JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Clean resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<vague-term JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Unqualified vague term blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_requirements_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "functional_requirements": [
        {"id": "FR-001", "title": "t", "statement": "The system shall respond fast to buyer searches.", "traces_to": "vision.md § X", "confidence": 0.8, "reasoning": "r" * 25},
    ],
    "compound_splits": [],
}}})

result = await check_requirements_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # unqualified "fast" caught
```
