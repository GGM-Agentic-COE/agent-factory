# gr-L4-reasoning-validator

**Layer:** L4  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail ensures the agent explains its thinking — that every output item includes a substantive reasoning field explaining WHY that output was generated, not just WHAT was generated.

**What it validates:**
- Every item has a non-empty `metadata.reasoning` field
- Reasoning is at least 20 characters long (not a token placeholder)
- Reasoning is substantive — not just restating the title or content
- Reasoning explains the decision logic (references input data, KB sections, or decision criteria)
- Reasoning demonstrates the agent's thought process

**Why it matters:** Reasoning is what makes agent output auditable. If a story gets a "Confidential" sensitivity tag, the reasoning should explain why ("handles IBAN data per PSD2 classification"). Without reasoning, humans can't verify if the agent's decisions are correct.

**Scope:** L4 (Squad level) — teams can configure stricter reasoning requirements for their specific needs.


## How It Works

```
Agent generates output with reasoning
        ↓
┌─────────────────────────────────────────┐
│  REASONING CHECK (self_check_output)    │
│                                         │
│  For each item:                         │
│  • reasoning field exists? → ✓/✗        │
│  • Length ≥ 20 chars? → ✓/✗             │
│  • Not just restating title? → ✓/✗      │
│  • Explains WHY (not just WHAT)? → ✓/✗  │
│  • References input/KB/logic? → ✓/✗     │
│                                         │
│  Missing/shallow → FLAG + retry         │
│  Substantive → deliver output           │
└─────────────────────────────────────────┘
        ↓
Well-reasoned output delivered
```


## File Structure

```
gr-L4-reasoning-validator/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L4-reasoning-validator.co  # LLM-only Colang flow (uses self_check_input/output)
├── reasoning_validator.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L4-reasoning-validator.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`reasoning_validator.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"title": "SEPA Story", "metadata": {"reasoning": "Generated based on PSD2 Article 97 SCA requirements from kb-L2-payments, applied to retail SEPA transfer scenario"}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"title": "SEPA Story", "metadata": {"reasoning": ""}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Substantive reasoning | None | "yes" |
| Empty reasoning | reasoning: "" | "no" |
| Too short (<20 chars) | reasoning: "because" | "no" |
| Just restates title | reasoning: "SEPA Story" | "no" |
| References KB | reasoning mentions kb-L2-payments | "yes" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L4-reasoning-validator")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"title": "SEPA Story", "metadata": {"..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"title": "SEPA Story", "metadata": {"..."}]
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
