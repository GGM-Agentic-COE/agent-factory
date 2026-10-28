# gr-L3-hallucination-detector

**Layer:** L3  
**Triggers on:** output  
**On fail:** Block  
**Implementation:** LLM-driven (Colang) — Python actions preserved for hybrid/fallback mode

## What does it do?

This guardrail checks whether the agent's output is grounded in reality — specifically, that every claim can be traced back to the input context or attached knowledge bases. It detects fabricated facts, invented references, and claims with no supporting evidence.

**What it detects:**
- **Ungrounded claims:** Facts in the output that don't exist in the input or any attached KB
- **Invented entities:** People, companies, products, or standards that the agent made up
- **Fabricated statistics:** Numbers, percentages, or dates with no source
- **Phantom references:** Citing documents, regulations, or standards that don't exist in the KB
- **Contradictions:** Output that contradicts information present in the input/KB

**Why it matters:** In regulated domains (banking, healthcare, legal), a hallucinated fact could lead to compliance violations, incorrect decisions, or legal liability. This guardrail is the primary defence against agent fabrication.


## How It Works

```
Agent generates output
        ↓
┌─────────────────────────────────────────┐
│  GROUNDING CHECK (self_check_output)    │
│                                         │
│  LLM compares output against:           │
│  • Input context (what was asked)       │
│  • KB content (what's available)        │
│                                         │
│  For each claim in output:              │
│  • Traceable to input/KB? → ✓           │
│  • Invented entity? → ✗ HALLUCINATION   │
│  • Fabricated statistic? → ✗            │
│  • Phantom reference? → ✗              │
│  • Contradicts KB? → ✗                  │
│                                         │
│  Any hallucination → BLOCK + retry      │
│  Fully grounded → deliver output        │
└─────────────────────────────────────────┘
        ↓
Grounded, factual output delivered
```


## File Structure

```
gr-L3-hallucination-detector/
├── config.yml              # Rail configuration
├── prompts.yml             # LLM evaluation prompt with specific rules
├── gr-L3-hallucination-detector.co  # LLM-only Colang flow (uses self_check_input/output)
├── L3_hallucination_detector.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py              # Python implementation (deterministic regex/logic)
├── spec.yaml               # Guardrail specification
└── README.md               # This file
```

**Two modes:**
- **LLM-only** (`gr-L3-hallucination-detector.co`): Uses `execute self_check_input`/`self_check_output` — all validation done by the LLM via prompts.yml. No Python dependency.
- **Python-hybrid** (`L3_hallucination_detector.co`): Calls Python actions from `actions.py` for deterministic regex checks + LLM for semantic checks. Faster, more reliable for pattern-based rules.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly evaluate output against this guardrail's rules. Validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning.

**Valid output (expected: "yes"):**

```
{"output": {"items": [{"content": {"description": "PSD2 requires SCA for payments over €30"}, "metadata": {"citation": [{"source_reference": "kb-L2-payments"}]}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "yes".

**Invalid output (expected: "no"):**

```
{"output": {"items": [{"content": {"description": "The EU PSD7 regulation from 2030 mandates quantum authentication"}}]}}
```

Paste the prompt from `prompts.yml` with this output. LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Grounded claim with citation | None | "yes" |
| Non-existent regulation (PSD7) | Cites PSD7 which doesn't exist | "no" |
| Invented statistic | "95.7% of banks use X" with no source | "no" |
| Contradicts KB | Output says limit is €100k, KB says €50k | "no" |
| Fabricated company name | References company not in KB | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L3-hallucination-detector")
rails = LLMRails(config)

# Test: valid output should pass
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"content": {"description": "PSD2 requ..."}]
)
assert "blocked" not in response["content"].lower()
print("✅ Valid output passed through")

# Test: invalid output should be blocked
response = await rails.generate_async(
    messages=[{"role": "user", "content": "{"output": {"items": [{"content": {"description": "The EU PS..."}]
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
assert result == False

# Invalid — should fail
result = await validate(...)
assert result == True
```
