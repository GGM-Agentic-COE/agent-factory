# Evaluation — L1-vision-idea-intake-evaluator

This covers THIS evaluator's own meta-quality — not L1-vision-idea-intake's
rubric (that lives in `../L1-vision-idea-intake/evaluation.md` and is loaded
at runtime, not duplicated here).

## Quality Gates
- [ ] Every finding cites a specific gate/checklist item from the generator's evaluation.md, not a vague impression
- [ ] Every score in `scores` is independently justified, not copied from the generator's own confidence fields
- [ ] Every fix in `fixes_applied` has a genuinely correct `after` value — not just a plausible-looking edit
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is approved as-is, never "fixed" into a fabricated success

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output |
| Hallucination | ≤ 0.05 | No fix introduces content not grounded in the original input |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's `detail` explains why, not just pass/fail |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific check
- [ ] escalate_to_hitl used when genuinely unfixable, not overused as a shortcut
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
