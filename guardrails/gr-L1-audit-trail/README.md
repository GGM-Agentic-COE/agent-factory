# gr-L1-audit-trail

**Layer:** L1 Enterprise (applies to ALL agents, cannot be overridden)  
**Triggers on:** post_execution (output rail)  
**On fail:** Block output (missing fields) or Warn (persistence failure)  
**Implementation:** Pure Colang — no Python actions required

## What does it do?

This guardrail ensures every agent execution leaves a traceable, compliant audit record. It operates in two phases:

1. **Validates completeness** — Before output is delivered, the LLM checks that all traceability fields exist in the agent's response: who ran (agent_id, version), what happened (execution_id, output type), where input came from (source, parameters), and which schema version was used. If any field is missing, output is **blocked** — it never reaches the user or downstream agent.

2. **Persists a structured audit record** — After validation passes, a Python action extracts the traceability fields, masks any PII in input parameters (emails → [EMAIL], phones → [PHONE], etc.), and writes a structured JSON record to the configured audit store. If persistence fails, output is still delivered but an operational alert is raised.

The result: every agent execution can be traced end-to-end — from who triggered it, through what was produced, to where the output went. This is essential for regulatory compliance, incident investigation, and operational monitoring.

## How It Works

Uses NeMo Guardrails' built-in `self_check_output` mechanism. The LLM evaluates the output against the `prompts.yml` criteria — no custom Python code needed.

```
Agent generates output
        ↓
┌─────────────────────────────────────────┐
│  check audit trail completeness         │
│                                         │
│  LLM evaluates (via prompts.yml):       │
│  ✓ agent_id present (L[0-4]-*-agent)?   │
│  ✓ execution_id present (exec-*)?       │
│  ✓ agent_version present (x.y.z)?       │
│  ✓ input_summary.source valid enum?     │
│  ✓ input_summary.parameters non-empty?  │
│  ✓ output.type valid enum?              │
│  ✓ output.schema_version present?       │
│                                         │
│  ANY missing → BLOCK output             │
└─────────────────────────────────────────┘
        ↓ (all present)
┌─────────────────────────────────────────┐
│  log audit record                       │
│                                         │
│  LLM extracts and formats:              │
│  AUDIT | agent_id=X | exec_id=Y | ...   │
│  PII in parameters is masked            │
│                                         │
│  Captured in NeMo conversation log      │
└─────────────────────────────────────────┘
        ↓
Output delivered
```

## Fields Validated

| Field | Format | Fail Action |
|-------|--------|-------------|
| `agent_id` | `L[0-4]-*-agent` | Block |
| `execution_id` | `exec-*` | Block |
| `agent_version` | `x.y.z` (semver) | Block |
| `input_summary.source` | `agent_output` / `direct_input` / `file_upload` | Block |
| `input_summary.parameters` | Non-empty object | Block |
| `output.type` | Valid enum (story, epic, test_case, code, etc.) | Block |
| `output.schema_version` | Non-empty string | Block |

## File Structure

```
gr-L1-audit-trail/
├── config.yml          # Rail configuration (2 output flows)
├── prompts.yml         # LLM prompts for validation + audit summary
├── gr-L1-audit-trail.co  # LLM-only Colang flow (uses self_check_input/output)
├── L1-audit-trail.co  # Python-hybrid Colang flow (calls actions.py)
├── actions.py          # Python actions (persistence + PII masking)
├── spec.yaml           # Guardrail specification
└── README.md           # This file
```

## Usage

### 1. Include in your agent's guardrails config

```yaml
rails:
  output:
    flows:
      - check audit trail completeness
      - log audit record
```

### 2. Load the configuration

```python
from nemoguardrails import LLMRails, RailsConfig

config = RailsConfig.from_path("./gr-L1-audit-trail")
rails = LLMRails(config)
```

### 3. Place last in the output rail chain

The audit trail should run **after** all other output validations:

```yaml
rails:
  output:
    flows:
      - check output schema           # First: structure valid?
      - check output pii              # Second: safe?
      - check output hallucination    # Third: grounded?
      - check audit trail completeness # Last: log it
      - log audit record
```

This ensures only valid, safe output gets an audit record.

## Audit Summary Format

The LLM produces a one-line audit summary captured in NeMo's conversation log:

```
AUDIT | agent_id=L1-inception-template-agent | exec_id=exec-abc123 | version=1.0.0 | source=direct_input | type=fact | items=1 | status=success
```

PII in parameters is masked:
```
AUDIT | ... | params={email: [EMAIL], topic: "honeybees"} | ...
```

## Production Persistence

For production audit stores beyond NeMo's conversation log, add a Python action file (`actions.py`) that persists to:
- **AWS:** DynamoDB, S3, CloudWatch Logs
- **Azure:** Cosmos DB, Blob Storage  
- **GCP:** BigQuery, Cloud Logging

See `guardrail.py` for a standalone Python implementation that can be used with non-NeMo runtimes.

## Testing

### Option 1: Prompt-Based Testing (LLM Judgement Only)

Tests whether the LLM can correctly identify valid/invalid audit trail fields when given the prompt. This validates the **LLM's judgement accuracy** — not the guardrail flow itself. Useful for prompt tuning and evaluating if the LLM reliably returns "yes"/"no".

**Valid output (expected: "yes"):**

```
You are an audit trail validator.

Agent output: {"agent_id": "L1-inception-template-agent", "agent_version": "1.0.0", "execution_id": "exec-abc123", "input_summary": {"source": "direct_input", "source_agent_id": null, "parameters": {"topic": "honeybees"}}, "output": {"type": "fact", "schema_version": "1.0", "items": [{"id": "item-001", "title": "Bee Dance", "content": {"description": "A unique fact is: bees waggle dance"}, "metadata": {"confidence": 0.95, "reasoning": "Well established fact from entomology research", "citation": [{"source_reference": "general-knowledge", "source_location": "biology", "start_index": 0, "end_index": 0}], "trajectory": [{"step": 1, "action": "reason", "tool": null, "detail": "identified fact"}]}}]}}

Check if ALL of these audit trail fields are present and non-empty:
1. agent_id (format: L[0-4]-*-agent)
2. execution_id (format: exec-*)
3. agent_version (format: x.y.z)
4. input_summary.source (one of: agent_output, direct_input, file_upload)
5. input_summary.parameters (non-empty object)
6. output.type (one of: story, epic, test_case, code, design, document, decision, api_spec, config, report, fact)
7. output.schema_version (non-empty string)

Answer "yes" if ALL fields are present and valid. Answer "no" if ANY field is missing or invalid.
```

**Invalid output (expected: "no"):**

```
You are an audit trail validator.

Agent output: {"agent_version": "1.0.0", "execution_id": "exec-abc123", "input_summary": {"parameters": {"topic": "honeybees"}}, "output": {"type": "fact", "items": []}}

Check if ALL of these audit trail fields are present and non-empty:
1. agent_id (format: L[0-4]-*-agent)
2. execution_id (format: exec-*)
3. agent_version (format: x.y.z)
4. input_summary.source (one of: agent_output, direct_input, file_upload)
5. input_summary.parameters (non-empty object)
6. output.type (one of: story, epic, test_case, code, design, document, decision, api_spec, config, report, fact)
7. output.schema_version (non-empty string)

Answer "yes" if ALL fields are present and valid. Answer "no" if ANY field is missing or invalid.
```

Missing: `agent_id`, `input_summary.source`, `output.schema_version` → LLM should answer "no".

### Test Cases Matrix

| Test | Mutation | Expected |
|------|----------|----------|
| Valid complete output | None | "yes" |
| Missing agent_id | Remove agent_id | "no" |
| Missing source | Remove input_summary.source | "no" |
| Invalid source enum | source = "webhook" | "no" |
| Empty parameters | parameters = {} | "no" |
| Missing schema_version | Remove output.schema_version | "no" |
| Invalid agent_id format | agent_id = "my-agent" | "no" |
| Missing execution_id | Remove execution_id | "no" |
| Missing agent_version | Remove agent_version | "no" |
| Invalid output.type | type = "unknown" | "no" |

### Option 2: End-to-End Flow Testing (NeMo Guardrails SDK)

Tests the actual Colang flow as it would execute at runtime — the full pipeline: `check audit trail completeness` → `self_check_output` → LLM evaluates → flow blocks or passes. This is how the guardrail behaves when an agent runs in production.

```python
from nemoguardrails import LLMRails, RailsConfig

# Load the guardrail config
config = RailsConfig.from_path("./gr-L1-audit-trail")
rails = LLMRails(config)

# Test 1: Valid output — flow should PASS (output delivered)
valid_output = '{"agent_id": "L1-inception-template-agent", "agent_version": "1.0.0", "execution_id": "exec-abc123", "input_summary": {"source": "direct_input", "source_agent_id": null, "parameters": {"topic": "honeybees"}}, "output": {"type": "fact", "schema_version": "1.0", "items": [{"id": "item-001", "title": "Bee Dance", "content": {"description": "A unique fact"}, "metadata": {"confidence": 0.95, "reasoning": "Entomology research", "citation": [{"source_reference": "general-knowledge", "source_location": "biology", "start_index": 0, "end_index": 0}], "trajectory": [{"step": 1, "action": "reason", "tool": null, "detail": "identified"}]}}]}}'

response = await rails.generate_async(
    messages=[{"role": "user", "content": "generate a fact about bees"}],
    options={"output": valid_output}
)
assert "Output blocked" not in response["content"]
print("✅ Test 1: Valid output passed through the flow")

# Test 2: Invalid output — flow should BLOCK
invalid_output = '{"agent_version": "1.0.0", "execution_id": "exec-abc123", "input_summary": {"parameters": {"topic": "bees"}}, "output": {"type": "fact", "items": []}}'

response = await rails.generate_async(
    messages=[{"role": "user", "content": "generate a fact about bees"}],
    options={"output": invalid_output}
)
assert "Output blocked" in response["content"]
print("✅ Test 2: Invalid output blocked by flow")
```

### Option 3: Python Unit Testing (standalone guardrail.py)

```python
from guardrail import L1AuditTrailGuardrail

guardrail = L1AuditTrailGuardrail()

valid = {
    "agent_id": "L1-inception-template-agent",
    "agent_version": "1.0.0",
    "execution_id": "exec-abc123",
    "input_summary": {"source": "direct_input", "source_agent_id": None, "parameters": {"topic": "honeybees"}},
    "output": {"type": "fact", "schema_version": "1.0", "items": []}
}

assert guardrail.evaluate(valid)["passed"] == True

invalid = {**valid}
del invalid["agent_id"]
assert guardrail.evaluate(invalid)["passed"] == False
```
