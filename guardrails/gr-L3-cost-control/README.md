# gr-L3-cost-control

**Layer:** L3  
**Triggers on:** input  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail enforces budget caps on agent execution — preventing runaway costs from unbounded token usage or excessive invocations.

**What it enforces:**
- **Token budget:** Total tokens (input + output combined) must not exceed `max_token_budget` configured in the agent spec
- **Invocation cap:** Agent cannot exceed maximum invocations per time window (prevents cost spikes)
- **Early warning:** Flags executions that reach 80% of budget (allows graceful completion)

**Why it matters:** LLM API calls cost money. A single agent in a loop could consume thousands of dollars in minutes. This guardrail kills execution before budget is exceeded, protecting against both bugs and adversarial token-stuffing attacks.


## How It Works

```
Agent execution in progress
        ↓
┌─────────────────────────────────────────┐
│  COST CHECK (self_check_input)          │
│                                         │
│  Evaluate budget status:                │
│  • total_tokens > max_budget? → KILL    │
│  • invocations > max? → KILL            │
│  • At 80% budget? → WARN (continue)     │
│                                         │
│  Exceeded → terminate execution         │
│  Warning → log + continue               │
│  Within budget → proceed                │
└─────────────────────────────────────────┘
        ↓
Execution continues within budget
```


## File Structure

```
gr-L3-cost-control/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-cost-control.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_cost_control.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-cost-control.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_cost_control.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
Tokens used: 3000, budget: 8000
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```
Tokens used: 9500, budget: 8000
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Within budget | 3000/8000 tokens | "yes" |
| At 80% (warning) | 6500/8000 tokens | "warn" |
| Over budget | 9500/8000 tokens | "no" |
| Invocations exceeded | invocations: 15, max: 10 | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-cost-control")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Tokens used: 3000, budget: 8000..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Tokens used: 9500, budget: 8000..."}]
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
