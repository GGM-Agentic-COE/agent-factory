# Evaluation — L1-inception-task-generator

## Quality Gates
- [ ] Every input feature appears as one or more tasks, or as a gap — never silently dropped
- [ ] task_id is unique and sequential within its parent feature (T-{epic}.{feature_seq}.{task_seq})
- [ ] No task's effort_hours exceeds max_task_effort_hours
- [ ] Every task has a citation (source_reference + source_location)
- [ ] artifacts[0].storage.location keyed by workflow_execution_id, not execution_id
- [ ] No summary/*_summary field contains the full artifact task description

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every task traces to a specific feature/acceptance-criteria source |
| Hallucination | <= 0.10 | No invented scope beyond what the feature/criteria imply |
| Consistency | 0.90 | Dependency links (blocks/blocked_by) are mutually consistent, no orphan references |
| Relevance | 0.85 | Tasks are directly assignable/sprint-ready |
| Reasoning quality | 0.80 | Task type and split decisions explained in summary |
| Citation completeness | 0.95 | Every task cites source |

## Reflection Checklist
- [ ] All features present as tasks or gaps; task_id pattern and sequencing correct
- [ ] No placeholder text; no description silently copied into an item summary
- [ ] No task_type forced onto a feature that doesn't need it
- [ ] Gaps reported (not guessed) for any feature too vague to decompose

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
