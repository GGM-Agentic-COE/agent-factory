# gr-L1-output-schema-validator

**Layer:** L1  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail ensures every agent output strictly conforms to the AgentOutput contract — the standard JSON structure all agents must produce. This is critical for workflow composability: if Agent A's output doesn't match the schema, Agent B downstream can't consume it.

**What it validates:**
- **Root fields:** agent_id, agent_version, execution_id, input_summary, output — all present
- **Input summary:** has source (valid enum) and parameters (non-empty object)
- **Output section:** has type (valid enum like "story", "fact", "code") and schema_version
- **Items (if present):** each has id, title, content, metadata
- **Metadata (if items):** has confidence (0-1), reasoning (20+ chars), citation (array), trajectory (array)
- **No null required fields** anywhere in the structure

**Why it matters:** The AgentOutput schema is the contract that enables agents to be composed into workflows. If one agent produces non-conformant output, the entire workflow chain breaks.


## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────────┐
│  SCHEMA CHECK (self_check_output)       │
│                                         │
│  LLM validates structure:               │
│                                         │
│  Root:                                  │
│  ├── agent_id ✓                         │
│  ├── agent_version ✓                    │
│  ├── execution_id ✓                     │
│  ├── input_summary                      │
│  │   ├── source (valid enum) ✓          │
│  │   └── parameters (non-empty) ✓       │
│  └── output                             │
│      ├── type (valid enum) ✓            │
│      ├── schema_version ✓               │
│      └── items[]                        │
│          ├── id, title, content ✓       │
│          └── metadata                   │
│              ├── confidence (0-1) ✓     │
│              ├── reasoning (20+) ✓      │
│              ├── citation [] ✓          │
│              └── trajectory [] ✓        │
│                                         │
│  Any missing → BLOCK + retry            │
│  All valid → deliver output             │
└─────────────────────────────────────────┘
        ↓
Output delivered to downstream
```


## File Structure

```
gr-L1-output-schema-validator/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L1-output-schema-validator.co  # LLM-only Colang flow (uses self_check_input/output)
├── output_schema_validator.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L1-output-schema-validator.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`output_schema_validator.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"agent_id": "L1-inception-template-agent", "agent_version": "1.0.0", "execution_id": "exec-abc123", "input_summary": {"source": "direct_input", "source_agent_id": null, "parameters": {"topic": "bees"}}, "output": {"type": "fact", "schema_version": "1.0", "items": [{"id": "item-001", "title": "Bee fact", "content": {"desc": "bees dance"}, "metadata": {"confidence": 0.9, "reasoning": "well known biological fact", "citation": [{"source_reference": "general-knowledge", "source_location": "bio", "start_index": 0, "end_index": 0}], "trajectory": [{"step": 1, "action": "reason", "tool": null, "detail": "identified"}]}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"agent_version": "1.0.0", "output": {"items": []}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Complete valid schema | None | "yes" |
| Missing agent_id | Remove agent_id | "no" |
| Missing input_summary | Remove input_summary | "no" |
| Missing output.type | Remove output.type | "no" |
| Missing metadata.reasoning | Remove reasoning from items | "no" |
| Missing citation array | Remove citation from metadata | "no" |
| Empty items (failure case) | items: [], no metadata | "yes" (valid failure) |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-output-schema-validator")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"agent_id": "L1-inception-template-agent", "agent_version":..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"agent_version": "1.0.0", "output": {"items": []}}..."}]
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
