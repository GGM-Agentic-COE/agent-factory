# Evaluation — L1-planning-impact-assessor-evaluator

This covers THIS evaluator's own meta-quality — not L1-planning-impact-
assessor's rubric (that lives in
`../L1-planning-impact-assessor/evaluation.md` and `kb-L1-enterprise-
architecture`, loaded at runtime, not duplicated here).

## Quality Gates
- [ ] The capability check was independently re-derived against
      service_catalog directly, not accepted because the generator's
      matched_service_id/is_duplicate "looks reasonable"
- [ ] The technical-touch check was independently re-derived against
      cmdb_export AND kb-L1-enterprise-architecture for every relevant CI —
      a CI the generator marked touched/not-touched is re-checked against
      both sources, not trusted from the generator's own row
- [ ] Every finding cites a specific ci_id, service_id, or FR-id, not a
      vague impression
- [ ] No fix invents a service, CI, or dependency not actually present in
      service_catalog/cmdb_export/kb-L1-enterprise-architecture
- [ ] A legitimate INSUFFICIENT_CONTEXT (status: failed) generator output
      is approved as-is, never "fixed" into a fabricated assessment

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output and source data |
| Hallucination | ≤ 0.05 | No fix introduces a service/CI/dependency not grounded in the actual exports or KB |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific ci_id/service_id/FR-id and which check it concerns |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("looks fine") without a specific re-derived check
- [ ] escalate_to_hitl used only when genuinely unfixable (e.g. the KB itself is ambiguous), not overused as a shortcut
- [ ] fixes_applied preserves everything that was already correct
- [ ] Any fix touching a fact also stated in impact-assessment.md was pushed back to the SAME s3 location — never left to diverge

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
