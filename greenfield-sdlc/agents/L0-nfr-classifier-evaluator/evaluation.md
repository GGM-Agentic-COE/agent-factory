# Evaluation — L1-requirements-nfr-classifier-evaluator

This covers THIS evaluator's own meta-quality — not L1-requirements-nfr-
classifier's rubric (that lives in `../L1-requirements-nfr-classifier/
evaluation.md` and `kb-L1-nfr-classification-taxonomy`, loaded at runtime,
not duplicated here).

## Quality Gates

### Category Coverage (→ Reasoning quality, Faithfulness)
- [ ] Every one of the 6 taxonomy categories (Performance, Security,
      Scalability, Availability, Compliance, Usability) was tested against
      each FR's statement — not just the categories the generator already
      listed as applicable. A category the generator omitted is only a
      valid omission if re-asking the taxonomy's own question against the
      FR statement genuinely yields "not applicable."
- [ ] Every APPLICABLE category was independently re-derived per FR (by
      asking the taxonomy's own question against the FR's statement), not
      accepted because the generator's category list "looks about right."
- [ ] FR-id set in nfr-spec.md matches FR-id set in requirements.md exactly
      (no missing FR, no invented FR, same order) — checked by set
      membership, not by row count.

### Grounding & Citation (→ Faithfulness, Hallucination)
- [ ] Every finding cites a specific taxonomy category AND a specific gate
      from the generator's evaluation.md — never a vague impression.
- [ ] Every non-TBD boundary condition's cited Source is dereferenced and
      the number/rule is confirmed to appear in that source verbatim (or as
      a direct logical consequence of it) — not merely "plausible."
- [ ] Every Compliance-category boundary condition traces only to
      regulatory-feasibility.md or kb-L1-enterprise-security, never to an
      unsupported inference from the FR statement alone.

### TBD Verification (→ Faithfulness, Consistency)
- [ ] Every TBD was independently re-checked against regulatory-feasibility.md
      and kb-L1-enterprise-security before being accepted as genuinely open.
- [ ] The Coverage Summary's TBD count (if present) matches an actual count
      of "TBD — needs stakeholder input" rows, not an estimate.

### Fabrication Prevention (→ Hallucination)
- [ ] No fix invents a number/rule not actually present in a real source.
- [ ] No fix silently reclassifies a category's applicability without
      documenting the taxonomy question that changed the answer.

### Status Handling (→ Consistency)
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is
      approved as-is, never "fixed" into fabricated classifications.
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
- [ ] Any fix that changes content also present in nfr-spec.md was pushed
      back to the SAME s3 location — never left to diverge from items

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
