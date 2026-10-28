# gr-L2-payments-compliance

**Layer:** L2  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail validates that agents working in the payments domain produce output that correctly references regulations and uses domain terminology accurately. It prevents agents from citing non-existent regulations, misrepresenting PSD2/SCA requirements, or using incorrect payments terminology.

**What it checks:**
- **Regulatory accuracy:** Are PSD2, SCA, PCI-DSS references correct and real (not hallucinated)?
- **SCA completeness:** Do payment-related stories include Strong Customer Authentication requirements where applicable?
- **Terminology correctness:** Are domain terms (SEPA, BACS, FPS, beneficiary, remitter) used correctly per the payments KB?
- **No phantom regulations:** Are there any cited standards or regulations that don't actually exist?
- **Completeness:** Are mandatory regulatory linkages present where required?

**Scope:** Only applies to agents in the payments domain (L2-payments-* agents).


## How It Works

```
Payments agent generates output
        ↓
┌─────────────────────────────────────────┐
│  COMPLIANCE CHECK (self_check_output)   │
│                                         │
│  LLM validates against payments rules:  │
│  • Cited regulations real? → ✓/✗        │
│  • SCA included where needed? → ✓/✗     │
│  • Domain terms correct? → ✓/✗          │
│  • No phantom regulations? → ✓/✗        │
│  • Regulatory linkage complete? → ✓/✗   │
│                                         │
│  Any failure → BLOCK + escalate         │
│  All correct → deliver output           │
└─────────────────────────────────────────┘
        ↓
Compliant output delivered
```


## File Structure

```
gr-L2-payments-compliance/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L2-payments-compliance.co  # LLM-only Colang flow (uses self_check_input/output)
├── payments_compliance.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L2-payments-compliance.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`payments_compliance.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"content": {"regulatory_linkage": "PSD2 Article 97 - SCA"}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"content": {"regulatory_linkage": "PSD5 Article 999"}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Correct PSD2 reference | None | "yes" |
| Non-existent regulation (PSD5) | regulatory_linkage: "PSD5" | "no" |
| Missing SCA for payment story | Payment story without SCA in AC | "no" |
| Incorrect terminology | "SEPA" spelled as "SEPPA" | "no" |
| Complete compliant output | PSD2 + SCA + correct terms | "yes" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L2-payments-compliance")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"content": {"regulatory_linkage": "PS..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"content": {"regulatory_linkage": "PS..."}]
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
