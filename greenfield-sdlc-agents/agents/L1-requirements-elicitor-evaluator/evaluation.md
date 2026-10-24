# Evaluation — L1-requirements-elicitor-evaluator

This covers THIS evaluator's own meta-quality — not L1-requirements-elicitor's
rubric (that lives in `../L1-requirements-elicitor/evaluation.md` and
`kb-L1-requirements-quality-standard`, loaded at runtime, not duplicated here).

## Quality Gates
- [ ] The Complete coverage check was done by set membership (every vision.md
      section → ≥1 FR), not by counting FRs and assuming enough exist
- [ ] Every finding cites a specific ISO/IEC/IEEE 29148 characteristic or a
      specific gate from the elicitor's evaluation.md, not a vague impression
- [ ] No fix invents a new FR to close a coverage gap without grounding it
      in an actual vision.md clause the elicitor missed
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is
      approved as-is, never "fixed" into fabricated requirements

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output |
| Hallucination | ≤ 0.05 | No fix introduces a capability not grounded in vision.md |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific FR-id and characteristic |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific check
- [ ] escalate_to_hitl used when genuinely unfixable, not overused as a shortcut
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
