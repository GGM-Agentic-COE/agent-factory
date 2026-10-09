# Evaluation — L1-planning-backlog-prioritizer-evaluator

This is this agent's OWN meta-quality bar: is ITS auditing correct? It is
never a restatement of L1-planning-backlog-prioritizer/evaluation.md — that
file is the scoring source of truth this agent applies, referenced via
`context.knowledge_bases`, not duplicated here.

## Quality Gates
- [ ] Every feature in generator_output has exactly one verification_result — none skipped, none duplicated
- [ ] recomputed_priority_score and recomputed_dependency_unblocking_score are independently derived (traceable to features/value_scoring_inputs/dependency_graph), never copied from generator_output
- [ ] Every "blocker" severity traces to an actual dependency violation or a >0.01 score mismatch — never a stylistic disagreement
- [ ] final_decision is never "fixed_and_approved" while a document_updated=true fix's field still holds pre-fix text in the re-uploaded artifact
- [ ] If artifacts[] is present, its id and storage.location exactly match the generator's — never a new artifact for a re-upload
- [ ] duplicate_flag_verified is present only when independently re-checked via tool-L1-jira-fetch-issue, never copied from the generator's flag

## Scores (>= threshold to pass — evaluators held to a higher bar than generators)
| Check | >= | What it verifies |
|-------|---|-------------------|
| Finding accuracy | 0.95 | Findings match an independent re-derivation, not a false positive/negative |
| Fix correctness | 0.95 | Every corrected_value is the actually-correct recomputed value |
| Document consistency | 1.00 | No case where items and the re-uploaded artifact disagree on a fixed field |
| Verdict soundness | 0.90 | final_decision logically follows from fixes_applied and severities found |
| Independence | 0.95 | No score/flag reported without a traceable independent recomputation |

## Reflection Checklist
- [ ] One verification_result per generator feature, no gaps
- [ ] final_decision consistent with fixes_applied and document state
- [ ] No summary contains full fix reasoning instead of a distillation (that belongs in the paired fixes_applied entry)
- [ ] Every "major"/"blocker" finding has a corresponding fixes_applied entry, unless final_decision is "rejected"

## Reflection Process
1. Independently re-derive → 2. Compare to generator claims → 3. Fix items + document together → 4. Check all gates above → 5. Deliver final only
