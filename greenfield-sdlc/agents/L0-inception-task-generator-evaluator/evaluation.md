# Evaluation — L1-inception-task-generator-evaluator

This is this agent's OWN meta-quality bar: is ITS auditing correct? It is
never a restatement of L1-inception-task-generator/evaluation.md — that file
(and kb-L1-task-decomposition-best-practices) are the sources of truth this
agent applies, referenced via `context.knowledge_bases`, not duplicated here.

## Quality Gates
- [ ] Every task in generator_output has exactly one verification_result — none skipped, none duplicated
- [ ] Every feature in the original features input has exactly one feature_coverage entry — none skipped
- [ ] task_type_justified, effort_within_ceiling, and dependency_correct are independently derived from features/acceptance_criteria/the KB, never copied from generator_output
- [ ] Every "blocker" severity traces to an actual ceiling violation, unjustified scope, or dropped feature — never a stylistic disagreement
- [ ] final_decision is never "fixed_and_approved" while a document_updated=true fix's field still holds pre-fix text in the re-uploaded artifact
- [ ] If artifacts[] is present, its id and storage.location exactly match the generator's — never a new artifact for a re-upload
- [ ] duplicate_flag_verified is present only when independently re-checked via tool-L1-jira-fetch-issue, never copied from the generator's flag

## Scores (>= threshold to pass — evaluators held to a higher bar than generators)
| Check | >= | What it verifies |
|-------|---|-------------------|
| Finding accuracy | 0.95 | Findings match an independent re-derivation, not a false positive/negative |
| Fix correctness | 0.95 | Every corrected_value is genuinely correct, including any id renumbering from an inserted task |
| Coverage completeness | 1.00 | No feature silently missing from both verification_results' task references and feature_coverage |
| Document consistency | 1.00 | No case where items and the re-uploaded artifact disagree on a fixed field |
| Verdict soundness | 0.90 | final_decision logically follows from fixes_applied and severities found |
| Independence | 0.95 | No judgment reported without a traceable independent re-derivation |

## Reflection Checklist
- [ ] One verification_result per generator task, one feature_coverage entry per input feature, no gaps
- [ ] final_decision consistent with fixes_applied and document state
- [ ] No summary contains full fix reasoning instead of a distillation (that belongs in the paired fixes_applied entry)
- [ ] Every "major"/"blocker" finding has a corresponding fixes_applied entry, unless final_decision is "rejected"

## Reflection Process
1. Independently re-judge each task and re-check feature coverage → 2. Compare to generator claims → 3. Fix items + document together → 4. Check all gates above → 5. Deliver final only
