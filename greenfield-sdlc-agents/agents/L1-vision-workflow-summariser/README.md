# L1-vision-workflow-summariser

## Purpose

Provides a single-point-of-truth for what happened in a Phase 0 workflow
run — which agent ran, whether it passed clean, needed a fix, or was
escalated — without anyone having to reconstruct the story by reading 8
separate agent logs. Runs once, at the very end of
`L1-WF-vision-idea-to-statement`.

## What does it do?

Accepts the outputs of all 4 generator+evaluator pairs from this workflow
run and produces:
- `intent` — one sentence on what this run was for
- `execution_flow` — one entry per step, in order, with its real outcome
- `outcome` — final_status (ready_for_human_approval / escalated / failed),
  the viability_score received, the open-risk count, and (if escalated) the
  specific finding that triggered it

It is strictly read-only: it transforms no artifact and re-scores nothing —
that's already done by the evaluators.

## How does it work?

1. Ingests all 8 step outputs from this workflow run, in order
2. Verifies workflow_execution_id is consistent across all of them
3. Builds execution_flow directly from each step's own status/final_decision
4. Derives outcome.final_status from the worst individual step outcome
5. If escalated, quotes the escalating step's actual finding rather than
   paraphrasing it into something vaguer

## Input

- **Source:** agent_output from all 8 prior Phase 0 steps
- **Required:** `all_step_outputs` — ordered list of every step's AgentOutput envelope

## Output

- **Type:** `workflow_summary`
- **Items:** `intent`, `execution_flow[]`, `outcome` — see `output_schema.json`
- **Summary:** step count and outcome breakdown, final_status and why,
  guardrail results

## Composition

```
agents/L1-vision-workflow-summariser/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-clean-run.json
│   ├── output-01-clean-run.json
│   ├── input-02-escalated-run.json
│   └── output-02-escalated-run.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-empty.json
    └── golden-02-empty.json

prompts/L1-vision-workflow-summariser/
└── instructions.md
```
