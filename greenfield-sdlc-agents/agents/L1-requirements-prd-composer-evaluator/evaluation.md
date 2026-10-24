# Evaluation — L1-requirements-prd-composer-evaluator

This covers THIS evaluator's own meta-quality — not L1-requirements-prd-composer's
rubric (that lives in `../L1-requirements-prd-composer/evaluation.md`, loaded
at runtime, not duplicated here).

## Quality Gates
- [ ] The zero-drop FR check was done by set membership (every requirements.md
      FR-id → present in prd.md's requirements[]), not by counting and
      assuming enough exist
- [ ] The zero-drop NFR check was done per-FR, per-category (every nfr-spec.md
      boundary condition → present in the SAME FR's nfrs[] in prd.md), not by
      a total-row-count comparison that could mask a swap between FRs
- [ ] Every Assumption/Constraint/Risk finding cites the specific vision.md
      constraint_id/open_risk id or FR-NNN it should trace to, not a vague
      impression
- [ ] Success-metrics absence was actually checked (no metrics field/section
      in items or the retrieved prd.md), not assumed from the schema's own
      omission of a metrics field
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output is
      approved as-is, never "fixed" into fabricated requirements

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output and the retrieved prd.md |
| Hallucination | ≤ 0.05 | No fix introduces an FR, NFR, assumption, constraint, or risk not grounded in requirements.md/nfr-spec.md/vision.md |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific FR-id/category/constraint-id involved |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific check
- [ ] escalate_to_hitl used when genuinely unfixable, not overused as a shortcut
- [ ] Every fix that touched prd.md content was actually pushed back to the
      SAME s3 location — final_decision never claims fixed_and_approved while
      the document still holds the pre-fix text
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
