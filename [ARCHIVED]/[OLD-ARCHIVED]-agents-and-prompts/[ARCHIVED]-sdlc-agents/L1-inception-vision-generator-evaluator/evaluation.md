# Evaluation — L1-inception-vision-generator-evaluator

## Quality Gates

- [ ] All findings have category + description + fix_applied
- [ ] Score per dimension is 0.0–1.0
- [ ] Overall verdict is pass (all scores ≥ threshold) or fail
- [ ] If fixes applied, corrected artifact re-uploaded
- [ ] No hallucinated fixes (only corrects what's genuinely wrong)

## Scores

| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Accuracy | 0.90 | Findings are genuine issues, not false positives |
| Fix quality | 0.85 | Fixes resolve the issue without introducing new problems |
| Completeness | 0.90 | All rubric dimensions evaluated |

## Reflection Checklist

- [ ] Every finding traces to a specific rubric criterion
- [ ] Fixes don't invent content not grounded in domain KB
- [ ] Pass/fail verdict matches scores (not contradictory)
- [ ] Re-uploaded artifact is the corrected version, not original
