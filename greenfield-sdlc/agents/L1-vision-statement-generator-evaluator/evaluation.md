# Evaluation — L1-vision-statement-generator-evaluator

This covers THIS evaluator's own meta-quality — not the generator's rubric
(loaded at runtime from `../L1-vision-statement-generator/evaluation.md`).

## Quality Gates
- [ ] Coverage check was done by set membership (constraint_id ∈ union of open_risks.related_ids), not by count comparison
- [ ] Every executive_summary sentence was checked individually against the sections below it, not judged as a whole
- [ ] viability_score was checked against what the generator actually received, not assumed correct
- [ ] Any fix to close a coverage gap was built from the constraint's own mitigation_summary, never invented from nothing

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately reflect the actual document structure |
| Hallucination | ≤ 0.05 | No fix introduces a risk/roadmap claim not grounded in upstream inputs |
| Consistency | 0.97 | Reconciliation coverage check passes fully — highest bar of any Phase 0 evaluator, since this is the last automated checkpoint before a human reads the result |
| Reasoning quality | 0.9 | Every coverage-gap finding names the specific missing constraint_id |

## Reflection Checklist
- [ ] Zero regulatory constraint_ids missing from open_risks coverage
- [ ] No unsupported claim left in executive_summary
- [ ] viability_score reporting matches what was actually received, not silently changed

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
