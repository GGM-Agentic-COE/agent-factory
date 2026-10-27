# Evaluation — L0-inception-feature-decomposer-evaluator

## Quality Gates
- [ ] Required AgentOutput and item fields are present.
- [ ] Input-source and workflow-ID rules are satisfied.
- [ ] Every primary item is grounded and traceable.
- [ ] IDs, enums, counts, and inherited values are valid.
- [ ] No prohibited implementation detail or fabricated content appears.
- [ ] Failure and escalation behavior follows the prompt.

## Scores (threshold to pass)
| Evaluator | Threshold | Checks |
|---|---:|---|
| Faithfulness | >= 0.90 | Every item traces to input |
| Hallucination | <= 0.10 | No invented content |
| Consistency | >= 0.90 | No contradictions |
| Relevance | >= 0.85 | Output fits downstream use |
| Reasoning quality | >= 0.80 | Decisions are concise and grounded |
| Citation completeness | >= 0.95 | Primary items cite exact source |

Minimum aggregate quality score: 8.0/10.

## Reflection Checklist
- [ ] No required field is missing.
- [ ] No placeholder or vague value remains.
- [ ] IDs are sequential, unique, and correctly formatted.
- [ ] execution_summary accurately states production and validation outcomes.

## Reflection Process
Generate → check all items above → fix mechanical defects silently → deliver final only.
