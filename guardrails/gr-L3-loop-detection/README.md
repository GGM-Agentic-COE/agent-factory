# gr-L3-loop-detection

**Layer:** L3  
**Triggers on:** input  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail detects and kills runaway agent execution — infinite loops, stuck processes, and recursion spirals that would otherwise run forever (consuming tokens and time).

**What it detects:**
- **Infinite loops:** Same action repeated more than N times (default: 50 iterations)
- **Timeout:** Execution exceeding configured time limit (default: 300 seconds)
- **Excessive recursion:** Agent calling itself or creating circular call chains deeper than configured depth (default: 10 levels)

**Why it matters:** An agent stuck in a retry loop (e.g., repeatedly failing a quality gate and retrying) could run indefinitely. Without loop detection, a single stuck agent could block an entire workflow, consume unbounded tokens, and drive costs up.


## How It Works

```
Agent execution running
        ↓ (checked on every iteration)
┌─────────────────────────────────────────┐
│  LOOP CHECK (self_check_input)          │
│                                         │
│  Check execution state:                 │
│  • iteration_count > 50? → KILL         │
│  • elapsed_seconds > 300? → KILL        │
│  • recursion_depth > 10? → KILL         │
│                                         │
│  Any limit hit → terminate immediately  │
│  Within limits → continue execution     │
└─────────────────────────────────────────┘
        ↓
Execution continues (or killed)
```


## File Structure

```
gr-L3-loop-detection/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-loop-detection.co  # LLM-only Colang flow (uses self_check_input/output)
├── loop_detection.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-loop-detection.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`loop_detection.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
Iteration: 5, elapsed: 30s, recursion: 2
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```
Iteration: 55, elapsed: 350s, recursion: 12
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Within all limits | iter:5, time:30s, depth:2 | "yes" |
| Iterations exceeded | iter:55, max:50 | "kill" |
| Timeout exceeded | elapsed:350s, timeout:300s | "kill" |
| Recursion too deep | depth:12, max:10 | "kill" |
| At limit (boundary) | iter:50, time:300s, depth:10 | "yes" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-loop-detection")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Iteration: 5, elapsed: 30s, recursion: 2..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Iteration: 55, elapsed: 350s, recursion: 12..."}]
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
assert result == False

# Invalid — should fail
result = await validate(...)
assert result == True
```
