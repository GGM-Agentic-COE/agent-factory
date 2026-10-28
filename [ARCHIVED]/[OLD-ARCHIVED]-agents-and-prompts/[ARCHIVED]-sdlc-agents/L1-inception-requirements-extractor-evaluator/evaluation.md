# Evaluation — L1-inception-requirements-extractor-evaluator

## Quality Gates

- [ ] All findings have category + description + fix_applied (or unfixable_reason)
- [ ] Score per dimension is 0.0–1.0
- [ ] Scores are post-fix (reflect corrected document state)
- [ ] Verdict is pass (all ≥ threshold) or fail
- [ ] If fixes applied, corrected PRD re-uploaded
- [ ] No hallucinated fixes (only corrects genuine issues)
- [ ] Faithfulness check uses original input as ground truth

## Scores

| Dimension | ≥ | Checks |
|-----------|---|--------|
| Accuracy | 0.90 | Findings are genuine issues, not false positives |
| Fix quality | 0.85 | Fixes resolve issue without introducing new problems |
| Completeness | 0.90 | All rubric dimensions evaluated, all inline gates checked |

## Reflection Checklist

- [ ] Every finding traces to a specific rubric criterion from KB or inline gates
- [ ] Fixes don't invent requirements not in original input
- [ ] Pass/fail verdict matches post-fix scores (not contradictory)
- [ ] Re-uploaded artifact is the corrected version, not original
- [ ] Unfixable items have clear reason why fix is impossible
