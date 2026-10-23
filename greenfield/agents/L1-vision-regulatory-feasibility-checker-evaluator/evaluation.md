# Evaluation — L1-vision-regulatory-feasibility-checker-evaluator

This covers THIS evaluator's own meta-quality — not the generator's rubric
(loaded at runtime from `../L1-vision-regulatory-feasibility-checker/evaluation.md`).

## Checks
- [ ] Every constraint's severity label was checked against its own rationale, not accepted at face value
- [ ] Any overall_status "discount" claim was independently validated (every Amber/Red item genuinely has a non-legal-review mitigation) before being approved
- [ ] No mitigation was invented to rescue a Red constraint from escalation
- [ ] The jurisdiction was RESOLVED from the brief's `target_geography` and the KBs' own `#jurisdiction` declarations, not assumed — `groundedness_check.brief_target_geography` and `kb_declared_jurisdiction` record both
- [ ] Every citation was checked for JURISDICTION, not only for existence and plausibility — `out_of_jurisdiction_citations` reflects what was found, and each produced a fail finding. A real regulation of the wrong country passes both an existence check and a plausibility check; only the jurisdiction check catches it
- [ ] False equivalence was checked: a local regime named correctly but argued through a foreign analogue's mechanics is a finding, not a stylistic quibble
- [ ] A KB-grounded assessment produced against a geography the KBs do not declare was escalated, not repaired field-by-field — there is nothing to fix when every citation names law that does not bind
- [ ] The category coverage sweep was re-run against `kb-L1-regulatory-frameworks-index#coverage-categories` — the same list the generator walked, never a list authored here. `groundedness_check.uncovered_categories` reflects what was actually found, and a non-empty result produced a finding
- [ ] No finding was raised against a category absent from `#coverage-categories`, however sensible that category seemed
- [ ] **BLOCKER — Viability re-derivation:** `viability_check` records a score derived from the FINAL post-fix constraints, not copied from the generator. `caps_expected` matches what those constraints actually trigger, `rederived_score` is the lowest of the weighted score and every expected cap, and `items.viability` carries that derivation
- [ ] `items.viability` is present and complete on every final_decision, including `escalate_to_hitl`
- [ ] Where a fix changed a severity, the score moved with it — a corrected constraint whose cap was never applied is a defect in this evaluator, not only in the generator
- [ ] A legitimate INSUFFICIENT_CONTEXT failure is evaluated, not "fixed"

## Scores (minimum per dimension)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.97 | Findings accurately re-derive severity from each constraint's own rationale; the viability derivation follows the constraints rather than the reported number |
| Hallucination | ≤ 0.03 | No invented mitigation, no invented citation validation, no invented component score |
| Consistency | 0.95 | overall_status conclusion matches what the individual constraints actually support, and viability_score matches both |
| Reasoning quality | 0.9 | Every severity-mismatch finding explains specifically why the label doesn't fit the rationale |

## Reflection Checklist
- [ ] Checked every constraint, not just the ones already flagged by the generator's own reasoning field
- [ ] Escalated every unmitigated Red — zero exceptions, zero "close enough"
- [ ] Verified the discount rule's precondition (ALL Amber/Red items mitigated) rather than assuming it from the stated rationale alone
- [ ] Re-derived viability arithmetic independently rather than re-checking the generator's stated sum
- [ ] Never adjusted a component score to move the final score toward a wanted side of the threshold of 7
- [ ] A viability correction was written into BOTH regulatory-feasibility.md's header table and its Viability Score section, not one of the two

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
