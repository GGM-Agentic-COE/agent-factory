# gr-L1-prd-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-requirements-prd-composer-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-requirements-prd-composer-evaluator` only (`configured_agents`)

## What does it do?

`L1-requirements-prd-composer-evaluator` scores `L1-requirements-prd-composer`'s
draft `prd.md` composition against `L1-requirements-prd-composer/evaluation.md`
and fixes what it can. This guardrail fires at that point but validates a
different thing: the **resultant** `L1-requirements-prd-composer` output — its
own `items`, with the evaluator's `fixes_applied` resolved in — is what
actually flows to `L1-planning-impact-assessor` and
`L1-planning-dependency-mapper`. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-requirements-prd-composer/output_schema.json` (not the evaluator's
   own output shape)?
2. **Capability checklist / rubric adherence** — does the resultant content
   actually satisfy `L1-requirements-prd-composer/evaluation.md`'s Quality
   Gates: zero-drop composition of every FR from `requirements.md` and every
   NFR boundary condition from `nfr-spec.md`, verbatim `compound_splits`
   carry-forward, every Assumption/Constraint/Risk tagged to an FR or
   "program-level" and genuinely traceable, success metrics genuinely
   absent, and a complete `open_questions` TBD rollup?

This is NOT a check on the evaluator's own scores/findings/final_decision —
it's an independent re-derivation of composition fidelity, run against what
actually ships downstream.

**Why it matters:** an evaluator reporting `fixed_and_approved` is a claim,
not a guarantee. `L1-requirements-prd-composer` composes (does not
re-derive) two already-approved upstream documents — a "fix" that quietly
dropped an FR's NFR boundary condition, left a risk untagged, or let a
success-metrics-looking field slip through despite the template's explicit
exclusion would all still report as "fixed". This gate is the independent
re-derivation that catches that, checked directly against
`original_input.requirements_output` and `original_input.nfr_spec_output` —
the same upstream content the composer itself received.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | zero-drop-requirements | Rubric adherence | block | critical |
| 3 | zero-drop-nfrs | Rubric adherence | block | critical |
| 4 | compound-splits-carried-forward | Rubric adherence | block | high |
| 5 | assumption-constraint-risk-tagged | Rubric adherence | block | critical |
| 6 | no-success-metrics-field | Rubric adherence | block | high |
| 7 | open-questions-completeness | Rubric adherence | block | high |
| 8 | assumption-constraint-risk-traceability | Rubric adherence | flag | high |
| 9 | executive-summary-no-new-claims | Rubric adherence | flag | medium |

## How It Works

```
L1-requirements-prd-composer-evaluator concludes
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  PRD QUALITY GATE (post_execution, fires on evaluator)             │
│                                                                      │
│  Reconstruct RESULTANT content: executive_summary/requirements/     │
│  assumptions/constraints/risks/open_questions/compound_splits with  │
│  fixes_applied[].before→after resolved in                           │
│                                                                      │
│  DETERMINISTIC (actions.py, cross-checked against original_input's  │
│  requirements_output and nfr_spec_output):                          │
│  1. Schema: all required fields/lengths/patterns valid?             │
│  2. FR id SET in requirements[] == FR id SET in requirements.md,    │
│     each statement carried verbatim?                                │
│  3. Every FR's nfrs[] (category, boundary_condition) SET == the     │
│     matching nfr-spec.md FR's boundary_conditions SET?               │
│  4. compound_splits[] == requirements.md's compound_splits[]?       │
│  5. Every assumption/constraint/risk's underlies_or_affects names    │
│     real FR ids or "program-level" — never untagged?                │
│  6. No key anywhere looks like a smuggled metrics field?             │
│  7. Every TBD (nfr-spec.md source == "—") has a matching             │
│     open_questions "tbd" entry (same fr_id/category)?                │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  8. Every assumption/constraint/risk genuinely traceable to          │
│     vision.md or a specific FR — not invented?                       │
│  9. executive_summary introduces no claim absent elsewhere?          │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant PRD content flows to impact-assessor / dependency-mapper
```

## File Structure

```
gr-L1-prd-quality-gate/
├── config.yml                        # Rail configuration
├── prompts.yml                       # LLM evaluation prompt (9 checks)
├── gr-L1-prd-quality-gate.co         # LLM-only Colang flow
├── prd_quality_gate.co               # Python-hybrid Colang flow (calls actions.py)
├── actions.py                        # Deterministic Python (schema, zero-drop FR/NFR, split carry-forward, tagging, metrics scan, TBD rollup)
├── spec.yaml                         # Guardrail specification
└── README.md                         # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-prd-quality-gate.co`): all 9 checks via `self_check_output`.
- **Python-hybrid** (`prd_quality_gate.co`): the 7 deterministic checks (1-7)
  reconstruct the resultant content and validate it directly in
  `actions.py` — checks 2, 3, 4, and 7 additionally need `original_input`
  (which carries `requirements_output` and `nfr_spec_output`, both
  `L1-requirements-prd-composer-evaluator`'s own required input parameters)
  to compare against; the LLM handles the 2 genuinely semantic checks
  (8, 9) — whether a claim is actually "absent" elsewhere or a risk is
  genuinely traceable is judgment, not a regex match.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")** — every FR/NFR from upstream is
present verbatim, assumptions are tagged, no metrics field, no TBD dropped:

```json
{
  "executive_summary": {"summary": "Composes 1 FR with its NFR table; no open TBDs.", "confidence": 0.9, "reasoning": "Restates counts already present below."},
  "compound_splits": [],
  "assumptions": [{"short_title": "Single tenant", "summary": "Assumes single-tenant deployment.", "underlies_or_affects": ["FR-001"], "confidence": 0.85, "reasoning": "Carried forward from vision.md's Regulatory Posture."}],
  "constraints": [],
  "risks": [],
  "requirements": [{"id": "FR-001", "title": "Digital claim submission", "statement": "The system shall allow an employee to submit an expense claim digitally.", "traces_to": "vision.md § Value Proposition", "nfrs": [{"category": "Security", "boundary_condition": "All submissions encrypted in transit (TLS 1.2+)", "source": "kb-L1-enterprise-security § ES3"}], "confidence": 0.93, "reasoning": "Composed verbatim from requirements.md and nfr-spec.md."}],
  "open_questions": []
}
```

**Invalid resultant output (expected: "no")** — FR-001's NFR boundary
condition was dropped and a stray metrics field was smuggled in:

```json
{
  "executive_summary": {"summary": "...", "confidence": 0.9, "reasoning": "r" * 25},
  "compound_splits": [],
  "assumptions": [],
  "constraints": [],
  "risks": [],
  "requirements": [{"id": "FR-001", "title": "...", "statement": "The system shall allow an employee to submit an expense claim digitally.", "traces_to": "vision.md § Value Proposition", "nfrs": [], "confidence": 0.93, "reasoning": "r" * 25, "success_metric_target": "95% submission rate"}],
  "open_questions": []
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean resultant content | None | "yes" |
| Dropped FR | requirements.md has FR-001/FR-002, resultant only has FR-001 | "no" |
| Invented FR | resultant adds FR-099 not in requirements.md | "no" |
| Paraphrased statement | FR-001 statement text altered from requirements.md's | "no" |
| Dropped NFR boundary condition | nfr-spec.md's FR-001 has a Security row, resultant nfrs[] is empty | "no" |
| Compound split altered | compound_splits differs from requirements.md's own | "no" |
| Untagged assumption | underlies_or_affects missing / empty array | "no" |
| Smuggled metrics field | A key containing "metric"/"kpi"/"target" appears in items | "no" |
| Dropped TBD | nfr-spec.md has a TBD boundary condition, no matching open_questions "tbd" entry | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-prd-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant PRD JSON>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Clean resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<dropped-FR JSON>"}]
)
assert "blocked" in response["content"].lower()
print("✅ Dropped FR blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_prd_quality_gate

original_input = json.dumps({
    "requirements_output": {"status": "success", "content": {"items": {
        "functional_requirements": [{"id": "FR-001", "title": "t", "statement": "The system shall allow an employee to submit an expense claim digitally.", "traces_to": "vision.md § X", "confidence": 0.9, "reasoning": "r" * 25}],
        "compound_splits": [],
    }}},
    "nfr_spec_output": {"status": "success", "content": {"items": {
        "nfr_classifications": [{"id": "FR-001", "title": "t", "boundary_conditions": [{"category": "Security", "boundary_condition": "All submissions encrypted in transit (TLS 1.2+)", "source": "kb-L1-enterprise-security § ES3"}], "confidence": 0.9, "reasoning": "r" * 25}],
    }}},
})

generator_output = json.dumps({"status": "success", "content": {"items": {
    "executive_summary": {"summary": "s", "confidence": 0.9, "reasoning": "r" * 25},
    "compound_splits": [],
    "assumptions": [], "constraints": [], "risks": [],
    "requirements": [{"id": "FR-001", "title": "t", "statement": "The system shall allow an employee to submit an expense claim digitally.", "traces_to": "vision.md § X", "nfrs": [], "confidence": 0.9, "reasoning": "r" * 25}],  # NFR dropped!
    "open_questions": [],
}}})

result = await check_prd_quality_gate(output="{}", generator_output=generator_output, original_input=original_input)
assert result == True  # dropped NFR boundary condition caught
```
