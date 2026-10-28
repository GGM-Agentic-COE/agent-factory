# L0-inception-feature-decomposer-evaluator

## Purpose
Independently evaluate and safely correct Features against their evaluator-approved parent Epics.

## What does it do?
- Accepts: Feature Decomposer AgentOutput and approved Epic Evaluator AgentOutput from the same workflow.
- Produces `feature_evaluation` in the standard AgentOutput envelope.
- Preserves workflow lineage and exact source traceability.
- Performs independent gate evaluation and safe correction.

## How does it work?
1. Validates mandatory inputs and workflow identifiers.
2. Loads the configured standards and knowledge bases.
3. Processes only grounded source content.
4. Validates IDs, required fields, and traceability.
5. Returns the final structured AgentOutput and execution summary.

## Input
- **Source:** Feature Decomposer AgentOutput and approved Epic Evaluator AgentOutput from the same workflow.
- **Required:** Valid source content and required workflow parameters.
- **Optional:** Alternate source supported by the prompt precedence rules.

## Output
- **Type:** `feature_evaluation`
- **Items:** `features` plus `gaps`.
- **Metadata:** Confidence, concise reasoning, and exact citation for primary items.
- **Summary:** Item counts, decisions, self-check outcome, KBs, guardrails, tools, and gaps.

## Composition
```text
agents/L0-inception-feature-decomposer-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-insufficient-context.json
│   └── output-02-insufficient-context.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json
    ├── golden-01-happy-path.json
    ├── input-golden-02-failure.json
    └── golden-02-failure.json
prompts/L0-inception-feature-decomposer-evaluator/
└── instructions.md
```
