# gr-L1-output-schema-validator

**Layer:** L1
**Triggers on:** output (output rail)
**On fail:** Block
**Implementation:** LLM-driven (Colang) + Python-hybrid mode available

## What does it do?

Ensures every agent output strictly conforms to the AgentOutput contract — the standard JSON structure all agents must produce. This is critical for workflow composability: if one agent's output doesn't match the schema, a downstream agent can't consume it and the workflow chain breaks.

**What it catches:**
- Missing root fields: agent_id, agent_version, execution_id, input_summary, or output
- input_summary missing a valid source enum or a non-empty parameters object
- output section missing a valid type enum or a schema_version
- Items missing id, title, content, or metadata
- Metadata missing confidence (0-1), reasoning (20+ chars), citation array, or trajectory array
- Null values present in any required field

**What it allows:**
- Outputs with an empty items array and no metadata, since this is a valid "no results" response
- Optional fields explicitly set to null when they are not required, e.g. source_agent_id
- Minor formatting or ordering differences that don't affect field presence

## How It Works

```
AGENT OUTPUT
    │
    ▼
[LLM: Schema validation (6-point check)] ──── Invalid? ──► BLOCK
    │ Valid
    ▼
[DELIVER OUTPUT]
```

## File Structure

```
gr-L1-output-schema-validator/
├── gr-L1-output-schema-validator.co   # output rail definitions
├── config.yml                          # NeMo config + self-check prompt
└── README.md                           # This file
```

## Testing

### Prompt-Based Testing (LLM Judgement)

**Should pass (answer: "yes" = safe):**
- A complete output with all root fields present, a valid input_summary, and items carrying full metadata
- An output with an empty items array and no metadata (a valid "no results" response)

**Should block (answer: "no" = unsafe):**
- An output missing the agent_id root field
- An output whose items are missing required metadata, such as reasoning or citation

### Test Cases Matrix

| # | Test | Expected | Category | Severity |
|---|------|----------|----------|----------|
| 1 | Missing a root field (agent_id, agent_version, execution_id, input_summary, or output) | BLOCK | schema_validation | High |
| 2 | input_summary missing a valid source enum or non-empty parameters object | BLOCK | schema_validation | High |
| 3 | output section missing a valid type enum or schema_version | BLOCK | schema_validation | High |
| 4 | Item missing id, title, content, or metadata | BLOCK | schema_validation | High |
| 5 | Metadata missing confidence, reasoning, citation, or trajectory | BLOCK | schema_validation | High |
| 6 | Null value present in a required field | BLOCK | schema_validation | High |
| 7 | Empty items array with no metadata (valid "no results" response) | PASS | — | — |
| 8 | Optional field explicitly set to null when not required | PASS | — | — |
| 9 | Minor formatting or ordering differences with all fields present | PASS | — | — |
