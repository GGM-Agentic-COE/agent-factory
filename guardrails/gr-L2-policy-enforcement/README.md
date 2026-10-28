# gr-L2-policy-enforcement

**Layer:** L2  
**Triggers on:** input + output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail enforces domain boundaries — ensuring agents only respond to requests within their designated scope and don't produce output outside their domain.

**On input:** If a payments agent receives a request about HR policies or weather forecasts, it's blocked with an OUT_OF_SCOPE response before the agent wastes tokens on an irrelevant task.

**On output:** Even if the agent processes a valid request, if its response drifts into topics outside its domain (e.g., a payments agent giving legal advice), the output is blocked.

**What it enforces:**
- Agent stays within its declared domain scope (defined in agent spec)
- Off-topic requests get explicit OUT_OF_SCOPE refusal
- Output doesn't stray into domains the agent isn't qualified for
- Domain-specific business policies are respected

**Why it matters:** Without topic adherence, agents become unpredictable — giving answers outside their expertise where they're more likely to hallucinate.


## How It Works

```
User sends request
        ↓
┌─────────────────────────────────────────┐
│  INPUT POLICY (self_check_input)        │
│                                         │
│  LLM compares request against agent's   │
│  declared scope:                        │
│  • On-topic for this agent? → ✓/✗       │
│  • Within domain boundaries? → ✓/✗      │
│                                         │
│  Off-topic → OUT_OF_SCOPE response      │
│  On-topic → pass to agent               │
└─────────────────────────────────────────┘
        ↓
Agent generates output
        ↓
┌─────────────────────────────────────────┐
│  OUTPUT POLICY (self_check_output)      │
│                                         │
│  LLM checks output stays in scope:      │
│  • Relevant to original request? → ✓/✗  │
│  • Avoids out-of-domain info? → ✓/✗     │
│  • Complies with business policies? ✓/✗ │
│                                         │
│  Drift detected → BLOCK                 │
│  On-scope → deliver                     │
└─────────────────────────────────────────┘
        ↓
Scoped output delivered
```


## File Structure

```
gr-L2-policy-enforcement/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L2-policy-enforcement.co  # LLM-only Colang flow (uses self_check_input/output)
├── policy_enforcement.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L2-policy-enforcement.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`policy_enforcement.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
Generate user stories for the payments initiation feature
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```
What is the weather forecast for tomorrow in London?
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| On-topic request | None | "yes" |
| Completely off-topic | "weather forecast" | "no" |
| Adjacent but out of scope | "give me legal advice on PSD2 liability" | "no" |
| On-topic with extra context | "payments stories with SEPA focus" | "yes" |
| Attempting to use agent for chat | "tell me a joke" | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L2-policy-enforcement")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Generate user stories for the payments initiation feature..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "What is the weather forecast for tomorrow in London?..."}]
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
