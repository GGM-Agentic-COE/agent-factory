---
name: workflow-creator
description: Standard structure, patterns, and conventions for creating workflows in the Agent Factory. Use this whenever asked to create a workflow — apply this exact structure, naming, step composition, and quality gate patterns.
trigger: When the user asks to create a workflow, orchestrate agents, chain agents together, or asks about workflow structure and standards.
---

# Workflow Creator Skill

## Naming Convention

```
L{layer}-WF-{phase}-{outcome}
```

- `L1` = Enterprise (generic workflow, works for any domain)
- `L2` = Domain/LOB (domain-specific, extends L1)
- `L3` = Project/Initiative (project-specific, extends L2)
- `L4` = Squad/Local (team-specific, extends L3)
- `WF` = workflow marker (always present)
- `{phase}` = SDLC phase: inception | design | construction | testing | deployment
- `{outcome}` = kebab-case description of the workflow's end result

**Reference:** See `01-agent-development-naming-standard.html` for the full naming guide.

Patterns per layer:
- L1: `L1-WF-{phase}-{outcome}`
- L2: `L2-{domain}-WF-{phase}-{outcome}`
- L3: `L3-{project}-WF-{phase}-{outcome}`
- L4: `L4-{squad}-WF-{phase}-{outcome}`

Examples:
- `L1-WF-inception-feature-decomposition`
- `L1-WF-inception-requirements-to-stories`
- `L2-payments-WF-inception-feature-decomposition`
- `L3-kyc-WF-design-api-spec-generation`
- `L4-squad-alpha-WF-inception-feature-decomposition`

## Core Principles

| Principle | Standard |
|-----------|----------|
| Quality gates | Between every agent handoff. Rubric-based scoring. Min 7/10 to proceed. |
| HITL points | Explicit. On quality gate failure → Jira subtask for human review. |
| Idempotent | Safe to re-run. Check-before-create. No duplicate Jira issues. |
| Error handling | Per step: retry (max 2, exponential), fallback, or escalate to HITL. |
| Layer composition | Workflows at level N use agents at level N or lower. Tools typically L1. |

## Folder Structure

```
workflows/{workflow-name}/
├── spec.yaml              # Workflow specification (steps, gates, error handling)
├── README.md              # What it does, step diagram, HITL points
└── tests/
    ├── test-happy-path.json       # Expected flow through all steps
    └── test-gate-failure.json     # Expected behaviour on quality gate failure
```

## spec.yaml Template

```yaml
spec_version: "1.0"
artifact_type: workflow
metadata:
  name: {workflow-name}
  version: "1.0.0"
  layer: L{n}
  phase: {phase}
  owner: {owner}
  created: {date}

purpose:
  description: "{What this workflow achieves end-to-end}"
  trigger: "{What initiates this workflow — manual, event, upstream workflow}"
  outcome: "{What is produced when workflow completes successfully}"

steps:
  - step: 1
    name: {step-name}
    agent: {agent-name}
    tool: {tool-name}           # optional — only if step uses a tool
    input: "{what this step receives}"
    output: "{what this step produces}"
    quality_gate:
      ref: qg-L{n}-{gate-name}
      min_score: 7.0
      on_fail: escalate_to_hitl
    error_handling:
      retry: {max: 2, backoff: exponential}
      on_exhausted: escalate_to_hitl

  - step: 2
    name: {step-name}
    agent: {agent-name}
    input: "{output from step 1}"
    output: "{what this step produces}"
    quality_gate:
      ref: qg-L{n}-{gate-name}
      min_score: 7.0
      on_fail: retry_once_then_escalate

hitl_points:
  - after_step: {n}
    condition: "quality_gate_failure"
    action: "Create Jira subtask for human review"
    resume: "Re-run from failed step after human approval"

composition:
  agents_used:
    - {agent-1}: "L{n} — {purpose}"
    - {agent-2}: "L{n} — {purpose}"
  tools_used:
    - {tool-1}: "L1 — {purpose}"
  quality_gates:
    - {qg-1}: "L{n} — {what it checks}"
  guardrails_inherited:
    - "All guardrails from constituent agents apply"

idempotency:
  strategy: "{check-before-create | idempotency-key | skip-if-exists}"
  description: "{How re-runs are handled safely}"
```

## Layer Composition Rules

Workflows at level N can use:
- **Agents** at level N or lower (L4 workflow can use L1, L2, L3, L4 agents)
- **Tools** typically at L1 (shared tools), L2+ only for domain-specific systems
- **Quality gates** from any level (L1 foundation gates + domain/project-specific gates)

```yaml
# Example: L4 workflow composing agents from multiple layers
L4-squad-alpha-WF-inception-feature-decomposition:
  steps:
    - agent: L1-jira-orchestrator            # L1 shared tool agent
      tool:  tool-L1-jira-fetch-issue        # L1 shared tool

    - agent: L4-squad-alpha-feature-decomposer  # L4 squad agent
      quality_gate: qg-L2-payments-feature-check  # L2 domain gate

    - agent: L4-squad-alpha-story-generator     # L4 squad agent
      quality_gate: qg-L1-story-quality         # L1 foundation gate

    - agent: L1-jira-orchestrator            # L1 shared tool agent
      tool:  tool-L1-jira-create-issue       # L1 shared tool
```

## Quality Gate Pattern

Quality gates sit between steps and enforce minimum quality:

```yaml
quality_gates:
  qg-L1-story-quality:
    evaluators:
      - faithfulness: "≥ 0.90"
      - completeness: "≥ 0.85"
      - format_compliance: "≥ 0.95"
    min_composite: 7.0
    on_fail: escalate_to_hitl

  qg-L2-payments-feature-check:
    evaluators:
      - domain_alignment: "≥ 0.90"
      - regulatory_coverage: "≥ 0.95"
    min_composite: 8.0
    on_fail: retry_once_then_escalate
```

## Error Handling Strategy

| Error Type | Strategy | Max Retries | Escalation |
|-----------|----------|-------------|------------|
| Agent timeout | Retry with backoff | 2 | HITL |
| Quality gate failure | Retry once (re-generate) | 1 | HITL |
| Tool API error (transient) | Retry with backoff | 2 | Block workflow |
| Tool API error (auth) | No retry | 0 | Alert ops + block |
| Agent hallucination detected | Re-generate with stricter prompt | 1 | HITL |

## HITL Integration

When a workflow step fails quality gates:

1. **Create Jira subtask** under the parent epic/story
2. **Attach** the failed output + quality gate scores
3. **Assign** to the relevant reviewer (domain champion for L2 gates, squad lead for L4)
4. **Pause** workflow at that step
5. **Resume** from the failed step after human approval (not from scratch)

## README.md Template

```markdown
# {workflow-name}

## Purpose

{What this workflow achieves end-to-end in one paragraph}

## Flow Diagram

```
[Trigger] → [Step 1: Agent A] → QG → [Step 2: Agent B] → QG → [Step 3: Tool] → [Output]
                                  ↓ fail                    ↓ fail
                              [HITL Review]             [HITL Review]
```

## Steps

| # | Agent/Tool | Input | Output | Quality Gate |
|---|-----------|-------|--------|--------------|
| 1 | {agent} | {input} | {output} | {gate} |
| 2 | {agent} | {output from 1} | {output} | {gate} |

## HITL Points

- After step {n}: Triggered when {condition}. Human reviews {what}.

## Idempotency

{How re-runs are handled safely}

## Error Handling

{Per-step error handling summary}
```

## Checklist Before Publishing

- [ ] Name follows `L{N}-{scope}-WF-{phase}-{outcome}` convention
- [ ] All agents at correct layer (workflow level N uses agents ≤ N)
- [ ] Tools at L1 unless domain-specific system
- [ ] Quality gates between every agent handoff
- [ ] HITL points defined for gate failures
- [ ] Error handling per step (retry + escalation)
- [ ] Idempotent (safe to re-run)
- [ ] Versioned (semver)
- [ ] README includes flow diagram
- [ ] Tests cover happy path and gate failure scenarios
