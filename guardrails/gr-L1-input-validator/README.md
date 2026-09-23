# gr-L1-input-validator

**Layer:** L1
**Triggers on:** input (input rail)
**On fail:** Block
**Implementation:** LLM-driven (Colang) + Python-hybrid mode available

## What does it do?

Validates that incoming requests are well-formed and processable before the agent attempts to handle them. Prevents wasted compute on garbage input and protects against malformed payloads, failing fast with clear feedback instead of letting the agent produce confusing output or fail silently.

**What it catches:**
- Gibberish or random characters instead of valid JSON or a clear natural language request
- Empty or effectively empty content with no meaningful information
- JSON payloads missing a required `parameters` object or required fields
- Field values that exceed reasonable configured length limits
- Requests that are not legitimate or processable by the agent

**What it allows:**
- Unusual but clear and legitimate natural language requests
- Valid JSON with all required fields present, regardless of formatting style
- Short but meaningful requests
- Requests in languages other than English, as long as they are clear and well-formed

## How It Works

```
USER INPUT
    │
    ▼
[1. LLM: Valid JSON or clear request?] ──── No? ──► BLOCK
    │ Yes
    ▼
[2. LLM: Non-empty, meaningful content?] ──── No? ──► BLOCK
    │ Yes
    ▼
[3. LLM: Required parameters present?] ──── No? ──► BLOCK
    │ Yes
    ▼
[4. LLM: Field lengths reasonable?] ──── No? ──► BLOCK
    │ Yes
    ▼
[5. LLM: Legitimate agent request?] ──── No? ──► BLOCK
    │ Yes
    ▼
[ALLOW INPUT]
```

## File Structure

```
gr-L1-input-validator/
├── gr-L1-input-validator.co   # input rail definitions
├── config.yml                  # NeMo config + self-check prompt
└── README.md                   # This file
```

## Testing

### Prompt-Based Testing (LLM Judgement)

**Should pass (answer: "yes" = safe):**
- Valid JSON with parameters: `{"parameters": {"topic": "honeybees", "max_items": 5}}`
- A clear natural language request such as "Generate stories for the payments feature"

**Should block (answer: "no" = unsafe):**
- Empty input: `""`
- Gibberish input such as `"asdkjfh 2398fj sdf"`

### Test Cases Matrix

| # | Test | Expected | Category | Severity |
|---|------|----------|----------|----------|
| 1 | Gibberish / random characters instead of valid JSON or clear request | BLOCK | invalid_input | Medium |
| 2 | Empty or effectively empty input | BLOCK | invalid_input | Medium |
| 3 | JSON payload missing required `parameters` object or fields | BLOCK | invalid_input | Medium |
| 4 | Field values exceeding configured length limits | BLOCK | invalid_input | Medium |
| 5 | Requests not legitimate or processable by the agent | BLOCK | invalid_input | Medium |
| 6 | Unusual but clear and legitimate natural language request | PASS | — | — |
| 7 | Valid JSON with all required fields, regardless of formatting | PASS | — | — |
| 8 | Short but meaningful request | PASS | — | — |
| 9 | Clear, well-formed request in a non-English language | PASS | — | — |
