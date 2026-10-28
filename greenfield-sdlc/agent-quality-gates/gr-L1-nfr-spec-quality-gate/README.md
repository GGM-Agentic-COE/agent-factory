# gr-L1-nfr-spec-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-nfr-classifier-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-requirements-nfr-classifier-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-nfr-classifier-evaluator` independently re-checks
`L1-requirements-nfr-classifier`'s draft NFR classifications against
`kb-L1-nfr-classification-taxonomy` and the real grounding sources
(`requirements.md`, `vision.md` — including its Regulatory Posture section,
`kb-L1-enterprise-security`), and fixes what it can. This guardrail fires
at that point but validates a different thing: the **resultant**
`L1-requirements-nfr-classifier` output — its own `items`, with the
evaluator's `fixes_applied` resolved in — is what actually flows to
`L1-requirements-prd-composer`. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-requirements-nfr-classifier/output_schema.json` (not the
   evaluator's own output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-requirements-nfr-classifier/evaluation.md`'s
   Quality Gates: exactly one entry per FR with matching ids/order, at
   least one genuinely-applicable category per FR (or an explicit "No NFR
   categories apply"), every non-TBD boundary condition citing a real
   source, every TBD genuinely ungrounded, `source == "—"` iff the literal
   TBD phrase is used, and ids matching `requirements.md` exactly.

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's an independent re-derivation of NFR classification quality, run
against what actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a claim,
not a guarantee. If a "fix" left a boundary condition with a plausible-
sounding number and no matching citation, corrected a citation's section
but forgot to also correct its own TBD/source pairing, or resolved one
FR's coverage gap while silently dropping another FR's entry, that's
exactly the defect this gate exists to catch — independent of what the
evaluator's own bookkeeping says.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | tbd-source-consistency | Rubric adherence | block | critical |
| 4 | citation-form-validity | Rubric adherence | block | high |
| 5 | category-coverage-or-explicit-none | Rubric adherence | flag | high |
| 6 | fabrication-plausibility-check | Rubric adherence | flag | high |
| 7 | no-premature-tbd | Rubric adherence | flag | medium |

## How It Works

```
L1-requirements-nfr-classifier-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  NFR-SPEC QUALITY GATE (post_execution, fires on evaluator)        │
│                                                                      │
│  Reconstruct RESULTANT content: nfr_classifications with            │
│  fixes_applied[].before→after resolved in                           │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: id/title/boundary_conditions/confidence/reasoning?       │
│     Empty boundary_conditions always paired with "No NFR categories  │
│     apply" reasoning?                                                │
│  2. FR-NNN ids sequential, no gaps/duplicates/invented ids?          │
│  3. source == "—" iff boundary_condition ends in the TBD phrase?     │
│  4. Every non-TBD source matches a recognized citation form?         │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  5. Any FR silently skip an obviously-applicable category?           │
│  6. Any boundary condition's figure look fabricated vs its citation? │
│  7. Any TBD left open when a grounded value was clearly available?   │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant nfr-spec content flows to L1-requirements-prd-composer
```

## File Structure

```
gr-L1-nfr-spec-quality-gate/
├── config.yml                              # Rail configuration
├── prompts.yml                             # LLM evaluation prompt (7 checks)
├── gr-L1-nfr-spec-quality-gate.co          # LLM-only Colang flow
├── nfr_spec_quality_gate.co                # Python-hybrid Colang flow (calls actions.py)
├── actions.py                              # Deterministic Python (schema, ID sequencing, TBD/source consistency, citation-form validity)
├── spec.yaml                               # Guardrail specification
└── README.md                               # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-nfr-spec-quality-gate.co`): all 7 checks via `self_check_output`.
- **Python-hybrid** (`nfr_spec_quality_gate.co`): the 4 deterministic checks (1-4) reconstruct the resultant content and validate it directly in `actions.py`; the LLM handles the 3 genuinely semantic checks (5, 6, 7) — whether a category was genuinely applicable, whether a cited figure is plausible, and whether a TBD was actually resolvable are judgment calls, not regex matches.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")**:

```json
{
  "nfr_classifications": [
    {
      "id": "FR-001",
      "title": "Digital claim submission",
      "boundary_conditions": [
        { "category": "Security", "boundary_condition": "Claim submission must be tied to an authenticated employee identity — no anonymous submissions", "source": "requirements.md § FR-001" },
        { "category": "Performance", "boundary_condition": "Claim submission response time — TBD — needs stakeholder input", "source": "—" }
      ],
      "confidence": 0.88,
      "reasoning": "Security follows directly from the statement's own authenticated-employee terms; no response-time figure is stated anywhere, so Performance is marked TBD rather than guessed."
    }
  ]
}
```

**Invalid resultant output (expected: "no")** — a TBD/source mismatch and an ID gap:

```json
{
  "nfr_classifications": [
    { "id": "FR-001", "title": "...", "boundary_conditions": [ { "category": "Performance", "boundary_condition": "Response time — TBD — needs stakeholder input", "source": "requirements.md § FR-001" } ], "confidence": 0.8, "reasoning": "r" * 25 },
    { "id": "FR-003", "title": "...", "boundary_conditions": [], "confidence": 0.8, "reasoning": "No NFR categories apply." }
  ]
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean resultant content | None | "yes" |
| TBD/source mismatch | boundary_condition ends in TBD phrase but source is a citation, not "—" | "no" |
| Non-TBD with bare "—" source | Grounded boundary_condition but source is "—" | "no" |
| ID gap | FR-001 then FR-003, no FR-002 | "no" |
| Invalid citation form | source = "internal knowledge" | "no" |
| Empty boundary_conditions, no explicit reasoning | boundary_conditions: [], reasoning doesn't say "No NFR categories apply" | "no" |
| Silently-skipped category | FR statement clearly implies Security but no Security category appears | "no" |
| Fabricated-looking figure | A cited requirements.md § FR-NNN source that plainly doesn't state the figure claimed | "no" |
| Premature TBD | TBD used even though the same FR's own statement (or a sibling entry's kb-L1-enterprise-security citation) already grounds it | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-nfr-spec-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant nfr_classifications JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Clean resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<TBD/source mismatch JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ TBD/source mismatch blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_nfr_spec_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "nfr_classifications": [
        {"id": "FR-001", "title": "t", "boundary_conditions": [
            {"category": "Performance", "boundary_condition": "Response time under 200ms — TBD — needs stakeholder input", "source": "requirements.md § FR-001"}
        ], "confidence": 0.8, "reasoning": "r" * 25},
    ],
}}})

result = await check_nfr_spec_quality_gate(output="{}", generator_output=generator_output)
assert result == True  # TBD boundary_condition with a non-"—" source caught
```
