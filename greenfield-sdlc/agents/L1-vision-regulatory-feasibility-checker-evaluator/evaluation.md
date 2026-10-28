# Evaluation — L1-vision-regulatory-feasibility-checker-evaluator

This covers THIS evaluator's own meta-quality — not the generator's rubric
(loaded at runtime from `../L1-vision-regulatory-feasibility-checker/evaluation.md`).

## Quality Gates
- [ ] Every constraint's severity label was checked against its own rationale, not accepted at face value
- [ ] Any overall_status "discount" claim was independently validated (every Amber/Red item genuinely has a non-legal-review mitigation) before being approved
- [ ] No mitigation was invented to rescue a Red constraint from escalation
- [ ] A legitimate INSUFFICIENT_CONTEXT failure is evaluated, not "fixed"

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.97 | Findings accurately re-derive severity from each constraint's own rationale |
| Hallucination | ≤ 0.03 | No invented mitigation, no invented citation validation |
| Consistency | 0.95 | overall_status conclusion matches what the individual constraints actually support |
| Reasoning quality | 0.9 | Every severity-mismatch finding explains specifically why the label doesn't fit the rationale |

## Reflection Checklist
- [ ] Checked every constraint, not just the ones already flagged by the generator's own reasoning field
- [ ] Escalated every unmitigated Red — zero exceptions, zero "close enough"
- [ ] Verified the discount rule's precondition (ALL Amber/Red items mitigated) rather than assuming it from the stated rationale alone

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
