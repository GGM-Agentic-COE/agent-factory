# gr-L3-agent-rate-limit

**Layer:** L3  
**Triggers on:** input  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail limits how many tool calls and downstream agent invocations an agent can make in a single execution. It prevents runaway agents from making hundreds of API calls or spawning unbounded sub-agent chains.

**What it enforces:**
- **Max tool calls:** Agent cannot exceed configured maximum tool invocations per execution (e.g., 50 calls)
- **Max agent calls:** Orchestrator agents cannot invoke more downstream agents than configured
- **Cooldown:** Enforces minimum interval between repeated calls to the same tool (prevents hammering)

**Why it matters:** Without rate limits, a malfunctioning agent could make thousands of Jira API calls in seconds, hit external rate limits, run up costs, or create a denial-of-service condition.


## How It Works

```
Agent attempts tool/agent call
        ↓
┌─────────────────────────────────────────┐
│  RATE LIMIT (self_check_input)          │
│                                         │
│  LLM evaluates counters:               │
│  • tool_call_count > max? → BLOCK       │
│  • agent_call_count > max? → BLOCK      │
│  • Cooldown elapsed? → ✓/THROTTLE       │
│                                         │
│  Exceeded → BLOCK + throttle            │
│  Within limits → permit call            │
└─────────────────────────────────────────┘
        ↓
Call proceeds within budget
```


## File Structure

```
gr-L3-agent-rate-limit/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-agent-rate-limit.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_agent_rate_limit.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-agent-rate-limit.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_agent_rate_limit.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
Tool call count: 5, max: 50
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```
Tool call count: 55, max: 50
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Within limits | 5/50 calls | "yes" |
| At limit | 50/50 calls | "no" |
| Over limit | 55/50 calls | "no" |
| Agent calls exceeded | agent_calls: 12, max: 10 | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-agent-rate-limit")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Tool call count: 5, max: 50..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Tool call count: 55, max: 50..."}]
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
