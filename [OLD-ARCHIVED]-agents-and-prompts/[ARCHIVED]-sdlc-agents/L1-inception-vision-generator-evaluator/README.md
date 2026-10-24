# L1-inception-vision-generator-evaluator

## Purpose

Post-generation validator for vision documents. Evaluates output from L1-inception-vision-generator against the quality rubric, fixes issues found, and re-uploads the corrected artifact. Implements S6 (Evaluation at Validation) to reduce token load on the generator agent.

## What does it do?

- Receives the vision document markdown + generator's AgentOutput
- Evaluates against all quality dimensions (faithfulness, hallucination, domain grounding, specificity, consistency, completeness)
- Identifies findings with specific category and description
- Applies fixes silently to the document
- Re-uploads corrected artifact to the same blob location
- Returns pass/fail verdict with scores

## Input

- **Source:** agent_output from L1-inception-vision-generator
- **Required:** vision_document (markdown content), generator_output (AgentOutput JSON)

## Output

- **Type:** vision_document_evaluation
- **Items:** verdict (pass/fail), scores (6 dimensions), findings (array), artifact (corrected location + status)

## Composition

```
agents/L1-inception-vision-generator-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
└── examples/
    ├── input-01-pass.json
    └── output-01-pass.json

prompts/L1-inception-vision-generator-evaluator/
└── instructions-concise.md
```
