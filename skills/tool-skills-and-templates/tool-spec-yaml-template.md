## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: tool
metadata:
  name: tool-L{n}-{platform}-{action}
  version: "1.0.0"
  layer: L{n}
  owner: agentic-ai-coe

purpose:
  description: "{What this tool does in one sentence}"
  platform: {platform}
  operation: {action}

interface:
  parameters:
    {param_1}: {type: string, required: true, description: "{what}"}
    {param_2}: {type: string, required: true, pattern: "{regex}"}
    {param_3}: {type: array, items: {type: string}, default: []}

  returns:
    type: ToolResult
    fields:
      success: boolean
      data: {field_1: type, field_2: type}
      error: {type: string, nullable: true}

credentials:
  source: secrets-sdk
  path: "{platform}"
  fields_used: [base_url, api_token]

identity:
  tool_id: "tool-{name}-001"
  role: tool-executor

  invocable_by:
    roles: [content-generator, orchestrator]
    agents: [{allowed-agent-1}]

  permissions:
    operation: read|write|delete
    platform: {platform}
    scope: "org-level|project-level|resource-level"

  credential_scoping:
    method: org-from-context
    vault_path_template: "/secrets/{org_id}/{platform}"

resilience:
  timeout_seconds: 30
  retry: {max: 2, backoff: exponential, retry_on: [timeout, 429, 502, 503]}
  circuit_breaker: {failure_threshold: 5, reset_seconds: 60}

security:
  input_validation: "All parameters validated before API call"
  output_sanitization: "Raw API errors never exposed; mapped to ToolResult.error"
  logging: "Input logged (PII masked); output summary logged; credentials never logged"
```