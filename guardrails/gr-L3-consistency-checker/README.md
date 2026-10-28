# gr-L3-consistency-checker

**Layer:** L3  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail detects internal contradictions in multi-item output. When an agent produces multiple items (e.g., 5 user stories, 10 test cases), this guardrail checks they don't contradict each other.

**What it detects:**
- **Duplicate IDs:** Two items with the same `id` field (breaks downstream processing)
- **Conflicting claims:** Item 1 says "payment limit is €50k" but Item 3 says "payment limit is €100k"
- **Enum conflicts:** Same field given different enum values for the same entity across items
- **Entity inconsistency:** Same entity referenced with different names/formats (e.g., "SEPA" vs "sepa" vs "S.E.P.A.")

**When it applies:** Only triggers for outputs with more than one item. Single-item outputs skip this check.

**Why it matters:** Contradictory output confuses downstream agents and humans. If stories contradict each other, test cases generated from them will be wrong.


## How It Works

```
Agent generates multi-item output
        ↓
┌─────────────────────────────────────────┐
│  CONSISTENCY CHECK (self_check_output)  │
│                                         │
│  Skip if items.length ≤ 1              │
│                                         │
│  Cross-item analysis:                   │
│  • Duplicate IDs? → BLOCK              │
│  • Contradicting claims? → FLAG         │
│  • Conflicting enums? → FLAG            │
│  • Entity name inconsistency? → FLAG    │
│                                         │
│  Duplicates → BLOCK                     │
│  Contradictions → escalate to HITL      │
│  Consistent → deliver output            │
└─────────────────────────────────────────┘
        ↓
Internally consistent output delivered
```


## File Structure

```
gr-L3-consistency-checker/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-consistency-checker.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_consistency_checker.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-consistency-checker.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_consistency_checker.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"id": "item-001", "title": "Story A"}, {"id": "item-002", "title": "Story B"}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"id": "item-001", "title": "Story A"}, {"id": "item-001", "title": "Story B"}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Unique IDs, consistent | None | "yes" |
| Duplicate IDs | Two items with id: item-001 | "no" |
| Contradicting claims | Item 1: limit €50k, Item 2: limit €100k | "no" |
| Single item (skip check) | Only one item | "yes" |
| Entity inconsistency | "SEPA" vs "sepa" vs "S.E.P.A." | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-consistency-checker")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"id": "item-001", "title": "Story A"}..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"id": "item-001", "title": "Story A"}..."}]
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
