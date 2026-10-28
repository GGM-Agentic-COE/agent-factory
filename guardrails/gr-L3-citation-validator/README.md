# gr-L3-citation-validator

**Layer:** L3  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail ensures every claim in the agent's output is backed by a citation — a reference to the knowledge base or source that supports it. Without citations, there's no way to verify if the agent's output is grounded or hallucinated.

**What it validates:**
- Every item in `output.items` has a non-empty `metadata.citation` array
- Each citation has a non-empty `source_reference` (KB name or source ID)
- The cited sources appear to be real (not fabricated KB names)
- At least 1 citation per item (minimum bar)

**Why it matters:** Citations create the traceability chain from output back to source. If an agent claims "PSD2 requires SCA for payments over €30", the citation points to exactly where in the KB that rule exists. Without citations, claims are unverifiable.


## How It Works

```
Agent generates output with items
        ↓
┌─────────────────────────────────────────┐
│  CITATION CHECK (self_check_output)     │
│                                         │
│  For each item in output.items:         │
│  • citation array non-empty? → ✓/✗      │
│  • source_reference non-empty? → ✓/✗    │
│  • source looks real (not fake)? → ✓/✗  │
│  • At least 1 citation? → ✓/✗           │
│                                         │
│  Any item missing citations → BLOCK     │
│  All cited → deliver output             │
└─────────────────────────────────────────┘
        ↓
Fully-cited output delivered
```


## File Structure

```
gr-L3-citation-validator/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-citation-validator.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_citation_validator.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-citation-validator.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_citation_validator.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"metadata": {"citation": [{"source_reference": "kb-L2-payments", "source_location": "section-3", "start_index": 0, "end_index": 100}]}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"metadata": {"citation": []}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Item with valid citation | None | "yes" |
| Item with empty citation array | citation: [] | "no" |
| Citation missing source_reference | source_reference: "" | "no" |
| Multiple items, one missing citation | Item 2 has no citation | "no" |
| Fabricated KB name | source_reference: "kb-fake-nonexistent" | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-citation-validator")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"metadata": {"citation": [{"source_re..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"metadata": {"citation": []}}]}}..."}]
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
