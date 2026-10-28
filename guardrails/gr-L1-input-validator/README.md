# gr-L1-input-validator

**Layer:** L1  
**Triggers on:** input  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail validates that incoming requests are well-formed and processable before the agent attempts to handle them. It prevents wasted compute on garbage input and protects against malformed payloads.

**What it checks:**
- Is the input valid JSON or a clear natural language request (not gibberish)?
- Does it contain meaningful content (not empty, not random characters)?
- If JSON format is expected: does it have a `parameters` object with required fields?
- Are field values of reasonable length (not exceeding configured limits)?
- Is it a legitimate request the agent can handle?

**Why it matters:** Without input validation, the agent might spend tokens processing nonsense, produce confusing error outputs, or fail silently. This guardrail fails fast and gives clear feedback.


## How It Works

```
User sends input
        ↓
┌─────────────────────────────────────────┐
│  INPUT VALIDATION (self_check_input)    │
│                                         │
│  LLM evaluates:                         │
│  • Valid JSON or clear request? → ✓/✗   │
│  • Non-empty, meaningful? → ✓/✗         │
│  • Required parameters present? → ✓/✗   │
│  • Field lengths reasonable? → ✓/✗      │
│  • Legitimate agent request? → ✓/✗      │
│                                         │
│  Any ✗ → REJECT with clear message      │
│  All ✓ → pass to agent                  │
└─────────────────────────────────────────┘
        ↓
Agent processes validated input
```


## File Structure

```
gr-L1-input-validator/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L1-input-validator.co  # LLM-only Colang flow (uses self_check_input/output)
├── L1_input_validator.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-input-validator.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L1_input_validator.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
{"parameters": {"topic": "honeybees", "max_items": 5}}
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```

```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Valid JSON with parameters | None | "yes" |
| Empty input | "" | "no" |
| Gibberish | "asdkjfh 2398fj sdf" | "no" |
| JSON without parameters | {"data": "test"} | "no" |
| Natural language request | "Generate stories for payments feature" | "yes" |
| Extremely long input (>5000 chars) | "a" * 6000 | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-input-validator")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"parameters": {"topic": "honeybees", "max_items": 5}}..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "..."}]
)
assert "blocked" in response["content"].lower()
print("✅ Invalid input blocked by flow")
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
