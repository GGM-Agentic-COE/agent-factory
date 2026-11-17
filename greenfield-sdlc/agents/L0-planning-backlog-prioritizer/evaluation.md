# Evaluation — L1-planning-backlog-prioritizer

## Quality Gates
- [ ] Every input feature appears exactly once in prioritized_features or gaps
- [ ] rank is sequential 1..N, no duplicates or gaps in the sequence
- [ ] priority_score, dependency_unblocking_score present and traceable to source data
- [ ] Every value_score and dependency_unblocking_score has a citation (source_reference + source_location)
- [ ] artifacts[0].storage.location keyed by workflow_execution_id, not execution_id
- [ ] No summary/*_summary field contains the full artifact rationale text

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every score traces to a specific input field |
| Hallucination | <= 0.10 | No invented value-scoring or dependency data |
| Consistency | 0.90 | Rank order matches dependency graph unless a trade-off is documented |
| Relevance | 0.85 | Backlog is directly usable for sprint planning |
| Reasoning quality | 0.80 | Rank adjustments explained in feature summary |
| Citation completeness | 0.95 | value_score and dependency_unblocking_score cite source |

## Reflection Checklist
- [ ] All features present, ranked, IDs match features.json pattern F-{epic}.{seq}
- [ ] No placeholder text; no rationale silently copied into an item summary
- [ ] No rank contradicts a blocks/blocked_by edge without a documented trade-off note
- [ ] Gaps reported (not guessed) for any feature missing value-scoring inputs

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
