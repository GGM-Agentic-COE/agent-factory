# gr-L2-tool-permissions

**Layer:** L2  
**Triggers on:** input  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail enforces least-privilege access to tools. Each agent has an explicit list of tools it's allowed to use (`tools_allowed`) and tools it must never touch (`tools_denied`). This guardrail intercepts tool calls and blocks any that aren't on the allowed list.

**What it enforces:**
- Agent can only invoke tools in its `tools_allowed` list from the agent spec
- Agent is explicitly blocked from tools in its `tools_denied` list
- Tool calls must be within the agent's organisational scope (`org_scope`)

**Why it matters:** An agent with access to `jira-delete-issue` could accidentally (or through injection) delete production tickets. By restricting each agent to only the tools it needs, blast radius is minimised.

**Example:** A story-generator agent is allowed `L1-jira-fetch-issue` (read) but denied `L1-jira-delete-issue` (destructive).


## How It Works

```
Agent attempts to call a tool
        ↓
┌─────────────────────────────────────────┐
│  PERMISSION CHECK (self_check_input)    │
│                                         │
│  LLM evaluates:                         │
│  • Tool in tools_allowed? → ✓/✗         │
│  • Tool in tools_denied? → ✗ always     │
│  • Within org_scope? → ✓/✗              │
│                                         │
│  Not permitted → BLOCK tool call        │
│  Permitted → execute tool               │
└─────────────────────────────────────────┘
        ↓
Tool executes with least-privilege
```


## File Structure

```
gr-L2-tool-permissions/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L2-tool-permissions.co  # LLM-only Colang flow (uses self_check_input/output)
├── tool_permissions.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L2-tool-permissions.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`tool_permissions.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate input against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid input (expected: "yes"):**

```
Call L1-jira-fetch-issue to get epic details
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "yes".

**Invalid input (expected: "no"):**

```
Call L1-jira-delete-issue to remove ticket PROJ-100
```

Paste the prompt from `prompts.yml` with this input. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Allowed tool call | L1-jira-fetch-issue | "yes" |
| Denied tool call | L1-jira-delete-issue | "no" |
| Tool not in any list | L1-slack-send-message | "no" |
| Out of org scope | Tool from different org | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_input` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L2-tool-permissions")
rails = LLMRails(config)

# Test: valid input should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Call L1-jira-fetch-issue to get epic details..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid input passed through")

# Test: invalid input should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "Call L1-jira-delete-issue to remove ticket PROJ-100..."}]
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
