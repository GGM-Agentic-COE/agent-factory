# gr-L3-confidence-gate

**Layer:** L3  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail uses the agent's self-reported confidence score to decide whether output should be delivered automatically, sent for human review, or blocked entirely.

**Three outcomes based on confidence:**
- **≥ 0.7:** Output delivered normally (agent is confident)
- **0.5 – 0.7:** Output escalated to Human-in-the-Loop review (borderline confidence)
- **< 0.5:** Output blocked entirely (agent is too uncertain to be useful)

**What it checks:**
- Every item has a `metadata.confidence` score between 0.0 and 1.0
- No items below the block threshold (0.5)
- Items below escalation threshold (0.7) flagged for HITL
- Confidence appears calibrated (not blindly 1.0 for uncertain claims)

**Why it matters:** An agent outputting stories with 0.3 confidence is essentially guessing. Rather than deliver unreliable output, this guardrail routes it to a human who can verify or reject it.


## How It Works

```
Agent generates output with confidence scores
        ↓
┌─────────────────────────────────────────┐
│  CONFIDENCE GATE (self_check_output)    │
│                                         │
│  For each item:                         │
│  • confidence ≥ 0.7 → PASS ✅           │
│  • confidence 0.5-0.7 → ESCALATE ⚠️    │
│  • confidence < 0.5 → BLOCK ❌          │
│  • confidence missing → BLOCK ❌        │
│                                         │
│  Any item < 0.5 → block entire output   │
│  Any item 0.5-0.7 → escalate to HITL   │
│  All ≥ 0.7 → deliver normally           │
└─────────────────────────────────────────┘
        ↓
Output routed appropriately
```


## File Structure

```
gr-L3-confidence-gate/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-confidence-gate.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_confidence_gate.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-confidence-gate.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_confidence_gate.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"metadata": {"confidence": 0.92}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"metadata": {"confidence": 0.3}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| High confidence (0.92) | None | "yes" |
| Borderline (0.65) | confidence: 0.65 | "escalate" |
| Too low (0.3) | confidence: 0.3 | "block" |
| Missing confidence | No confidence field | "block" |
| Multiple items, one low | Items at 0.9, 0.4, 0.8 | "block" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-confidence-gate")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"metadata": {"confidence": 0.92}}]}}..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"metadata": {"confidence": 0.3}}]}}..."}]
)
assert "blocked" in response["content"].lower()
print("✅ Invalid output blocked by flow")
```

### Option 3: Python Unit Testing (standalone actions.py)

Tests the deterministic Python implementation directly (hybrid mode):

```python
from actions import *

# Valid — should pass
result = await validate(...)
assert result == True

# Invalid — should fail
result = await validate(...)
assert result == False
```
