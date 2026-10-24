# Evaluation — L1-requirements-nfr-classifier-evaluator

This covers THIS evaluator's own meta-quality — not L1-requirements-nfr-
classifier's rubric (that lives in `../L1-requirements-nfr-classifier/
evaluation.md` and `kb-L1-nfr-classification-taxonomy`, loaded at runtime,
not duplicated here).

## Quality Gates
- [ ] Every APPLICABLE category was independently re-derived per FR (by
      asking the taxonomy's own question against the FR's statement), not
      accepted because the generator's category list "looks about right"
- [ ] Every finding cites a specific taxonomy category or a specific gate
      from the generator's evaluation.md, not a vague impression
- [ ] Every TBD was independently re-checked against vision.md's Regulatory
      Posture section and kb-L1-enterprise-security before being accepted as
      genuinely open
- [ ] No fix invents a number/rule not actually present in a real source
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is
      approved as-is, never "fixed" into fabricated classifications

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output |
| Hallucination | <= 0.05 | No fix introduces a number/rule not grounded in a real source |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific FR-id and category |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific re-check
- [ ] escalate_to_hitl used only when genuinely unfixable — e.g. a real
      coverage gap needing new stakeholder input, not a shortcut
- [ ] Any fix that changes boundary-condition content actually lands in
      items, not just in this evaluator's own findings/fixes_applied text —
      items are the sole, authoritative record

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
