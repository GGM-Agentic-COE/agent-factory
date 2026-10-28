# gr-L1-idea-intake-quality-gate

**Layer:** L1
**Triggers on:** post_execution (output rail) — fires when `L1-vision-idea-intake-evaluator` concludes
**On fail:** Retry once, then escalate to HITL
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid mode
**Applies to:** `L1-vision-idea-intake-evaluator` only (`configured_agents`)

## What does it do?

`L1-vision-idea-intake-evaluator` scores `L1-vision-idea-intake`'s draft
output against `L1-vision-idea-intake/evaluation.md` and fixes what it can.
This guardrail fires at that point (post-evaluation) but validates a
different thing entirely: the **resultant** `L1-vision-idea-intake` output
— its own `items`, with the evaluator's `fixes_applied` resolved in — is
what actually flows to `L1-vision-market-analyzer` and
`L1-vision-regulatory-feasibility-checker`. This gate checks THAT content:

1. **Output schema validation** — does the resultant content conform to
   `L1-vision-idea-intake/output_schema.json` (not the evaluator's own
   output shape)?
2. **Capability checklist / rubric adherence** — does the resultant
   content actually satisfy `L1-vision-idea-intake/evaluation.md`'s
   Quality Gates and Reflection Checklist (sequential IDs, correctly
   labeled stated/suggested metrics, grounded `traced_to`, no
   placeholder text, honest INSUFFICIENT_CONTEXT handling)?

This is NOT a check on the evaluator's own scores/findings/final_decision
— it's a check on whether evaluation, having concluded, actually produced
schema-valid, rubric-compliant content ready for the next pipeline step.

**Why it matters:** an evaluator can claim `fixed_and_approved` while an
ID gap is left unresolved, a required field is missing, or a `traced_to`
is weakened to something no longer grounded. This gate is independent of
the evaluator's own self-report — it re-derives compliance from the
actual resultant content.

### Rules

| # | Rule | Category | Action | Severity |
|---|------|----------|--------|----------|
| 1 | schema-compliance | Schema | block | critical |
| 2 | ids-sequential-no-gaps | Rubric adherence | block | high |
| 3 | insufficient-context-integrity | Rubric adherence | block | critical |
| 4 | traced-to-grounded | Rubric adherence | flag | high |
| 5 | success-metric-status-correct | Rubric adherence | flag | high |
| 6 | no-placeholder-or-vague-filler | Rubric adherence | flag | medium |

## How It Works

```
L1-vision-idea-intake-evaluator concludes (scores, fixes, final_decision)
        ↓
┌────────────────────────────────────────────────────────────────────┐
│  IDEA-INTAKE QUALITY GATE (post_execution, fires on evaluator)      │
│                                                                      │
│  Reconstruct RESULTANT content: L1-vision-idea-intake's items with  │
│  fixes_applied[].before→after resolved in                           │
│                                                                      │
│  DETERMINISTIC (actions.py):                                        │
│  1. Schema: statement/confidence/reasoning/traced_to present + valid? │
│  2. TU-NN/SM-NN/OQ-NN ids sequential, no gaps/duplicates?           │
│  3. If status=failed: items empty + INSUFFICIENT_CONTEXT stated?    │
│  6. No placeholder/filler text found (best-effort backstop)?        │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  SEMANTIC (self_check_output, LLM):                                  │
│  4. traced_to genuinely grounded in idea_brief_text?                 │
│  5. stated vs. suggested correctly labeled?                          │
│                                                                      │
│  Any ✗ → BLOCK, retry once, then escalate_to_hitl                    │
│                                                                      │
│  All ✓ → gate passes                                                 │
└────────────────────────────────────────────────────────────────────┘
        ↓
Resultant idea-brief content flows to L1-vision-market-analyzer /
L1-vision-regulatory-feasibility-checker
```

## File Structure

```
gr-L1-idea-intake-quality-gate/
├── config.yml                              # Rail configuration
├── prompts.yml                             # LLM evaluation prompt (6 checks)
├── gr-L1-idea-intake-quality-gate.co       # LLM-only Colang flow (uses self_check_output)
├── idea_intake_quality_gate.co             # Python-hybrid Colang flow (calls actions.py)
├── actions.py                              # Deterministic Python (schema, ID sequencing, INSUFFICIENT_CONTEXT integrity, placeholder scan)
├── spec.yaml                               # Guardrail specification
└── README.md                               # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-idea-intake-quality-gate.co`): all 6 checks via `self_check_output`.
- **Python-hybrid** (`idea_intake_quality_gate.co`): the 4 deterministic checks (1, 2, 3, 6) reconstruct the resultant content and validate it directly in `actions.py`; the LLM handles the 2 genuinely semantic checks (4, 5).

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

**Valid resultant output (expected: "yes")**:

```json
{
  "problem_statement": {"statement": "Expense claims stall in approvals with no visibility.", "confidence": 0.95, "reasoning": "Directly restates the stated problem.", "traced_to": "it goes through 2-3 manager approvals..."},
  "target_users": [{"id": "TU-01", "statement": "Employees submitting claims", "confidence": 0.9, "reasoning": "Explicitly named.", "traced_to": "Employees don't know where their claim is stuck"}],
  "value_proposition": {"statement": "Digital claims, single dashboard, clean export.", "confidence": 0.95, "reasoning": "Near-verbatim restatement.", "traced_to": "a small internal tool where employees submit claims digitally..."},
  "candidate_success_metrics": [{"id": "SM-01", "metric": "Reduction in submission-to-payment time", "status": "suggested", "confidence": 0.7, "reasoning": "No baseline given, inferred metric."}],
  "open_questions": [{"id": "OQ-01", "question": "What specific reduction is the target?", "reasoning": "Input gives no target magnitude."}]
}
```

**Invalid resultant output (expected: "no")** — an ID gap (TU-01 then TU-03, no TU-02) and a metric mislabeled "stated" with no explicit basis in the input:

```json
{
  "problem_statement": {"statement": "...", "confidence": 0.95, "reasoning": "...", "traced_to": "..."},
  "target_users": [
    {"id": "TU-01", "statement": "Employees submitting claims", "confidence": 0.9, "reasoning": "...", "traced_to": "..."},
    {"id": "TU-03", "statement": "Finance staff", "confidence": 0.9, "reasoning": "...", "traced_to": "..."}
  ],
  "value_proposition": {"statement": "...", "confidence": 0.95, "reasoning": "...", "traced_to": "..."},
  "candidate_success_metrics": [{"id": "SM-01", "metric": "50% reduction in submission time", "status": "stated", "confidence": 0.95, "reasoning": "..."}],
  "open_questions": []
}
```

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Clean, fully compliant resultant content | None | "yes" |
| ID gap | TU-02 missing between TU-01 and TU-03 | "no" |
| Duplicate ID | Two entries both SM-01 | "no" |
| Missing traced_to | `value_proposition.traced_to` absent | "no" |
| Mislabeled metric | A number with no input basis marked "stated" | "no" |
| Placeholder text | `target_users[].statement` = "TBD" | "no" |
| Legitimate INSUFFICIENT_CONTEXT | status=failed, items empty, summary states it | "yes" |
| Fabricated failure content | status=failed but items non-empty | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-idea-intake-quality-gate")
rails = LLMRails(config)

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<clean resultant idea-brief content>"}]
)
assert "blocked" not in response["content"].lower()
print("✅ Compliant resultant content passed")

response = await rails.generate_async(
    messages=[{"role": "assistant", "content": "<content with an ID gap>"}]
)
assert "blocked" in response["content"].lower()
print("✅ ID gap blocked")
```

### Option 3: Python Unit Testing (standalone actions.py)

```python
from actions import check_idea_intake_quality_gate

generator_output = json.dumps({"status": "success", "content": {"items": {
    "problem_statement": {"statement": "x" * 30, "confidence": 0.9, "reasoning": "y" * 25, "traced_to": "z"},
    "target_users": [
        {"id": "TU-01", "statement": "a", "confidence": 0.9, "reasoning": "b" * 25, "traced_to": "c"},
        {"id": "TU-03", "statement": "d", "confidence": 0.9, "reasoning": "e" * 25, "traced_to": "f"},
    ],
    "value_proposition": {"statement": "g" * 20, "confidence": 0.9, "reasoning": "h" * 25, "traced_to": "i"},
    "candidate_success_metrics": [{"id": "SM-01", "metric": "m", "status": "stated", "confidence": 0.9, "reasoning": "n" * 25}],
    "open_questions": [{"id": "OQ-01", "question": "q", "reasoning": "r" * 15}],
}}})

# Should detect the TU-02 gap
result = await check_idea_intake_quality_gate(output="{}", generator_output=generator_output)
assert result == True
```
