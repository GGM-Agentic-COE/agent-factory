# L1-inception-workflow-summariser

## Purpose

Synthesises the execution summaries of all agents in a workflow into a single, plain-English narrative that stakeholders can read to understand what happened, what was produced, and what resources were used.

## What does it do?

- Accepts the AgentOutput array from all prior agents in the same workflow
- Produces a structured summary covering:
  - **Request & Intent** — what triggered the workflow and what was the goal
  - **Execution Flow** — ordered list of agents that ran and what each did
  - **Artifacts & Content** — what was generated or modified (documents, stories, epics, etc.)
  - **Resources Used** — consolidated list of knowledge bases, guardrails, and tools across all agents
  - **Outcome** — final status, what was delivered, any gaps or failures

## How does it work?

1. Receive the array of AgentOutput objects from the workflow orchestrator
2. Validate at least 1 agent output is present
3. Identify workflow intent from the first agent's input and content type
4. Walk through each agent in execution order extracting: what it did, what it produced, what resources it used, its status
5. Consolidate duplicate KB/guardrail/tool references
6. Synthesise into the 5-section narrative structure
7. Reflect against evaluation.md checklist
8. Deliver final summary

## Input

- **Source:** agent_output (array of AgentOutput objects)
- **Required:** `agent_outputs` — array of complete AgentOutput JSON from all prior workflow agents
- **Optional:** `workflow_name` — human-readable name for the workflow

## Output

- **Type:** `workflow_summary`
- **Items:** request_and_intent, execution_flow[], artifacts_and_content[], resources_used{}, outcome, metadata (confidence + reasoning)
- **Summary:** Plain-text bullet points covering agent count, workflow status, key deliverables, resources used

## Composition

```
agents/L1-inception-workflow-summariser/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-inception-pipeline.json
│   └── output-01-inception-pipeline.json
└── golden/v1.0.0/
    ├── input-golden-01-full-pipeline.json
    ├── golden-01-full-pipeline.json
    ├── input-golden-02-partial-failure.json
    ├── golden-02-partial-failure.json
    ├── input-golden-03-insufficient-context.json
    └── golden-03-insufficient-context.json

prompts/L1-inception-workflow-summariser/
└── instructions.md
```

## Downstream

- Stakeholder dashboards and notifications
- Audit trail and compliance reporting
- Workflow execution history
