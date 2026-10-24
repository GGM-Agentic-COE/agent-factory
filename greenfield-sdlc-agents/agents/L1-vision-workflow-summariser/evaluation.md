# Evaluation — L1-vision-workflow-summariser

## Quality Gates
- [ ] execution_flow contains exactly one entry per step actually provided, in the order they ran
- [ ] Every outcome value is taken directly from that step's own status/final_decision — not re-derived or softened
- [ ] outcome.final_status correctly reflects the worst individual step (any escalation → escalated; any unrecovered failure → failed)
- [ ] workflow_execution_id consistency across all 8 steps is checked, not assumed

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every execution_flow entry matches the actual step output it summarizes |
| Hallucination | ≤ 0.05 | No step outcome invented or guessed |
| Consistency | 0.95 | outcome.final_status logic matches the individual steps' worst outcome |
| Reasoning quality | 0.75 | intent and escalation_reason (if any) are specific, not generic |

## Reflection Checklist
- [ ] No step silently omitted, especially a failed or escalated one
- [ ] escalation_reason quotes the actual finding, not a paraphrase that loses specificity
- [ ] This agent did not attempt to re-score or override any evaluator's decision

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
