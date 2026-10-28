# Evaluation — L1-planning-impact-assessor

## Quality Gates
- [ ] Capability check genuinely run against service_catalog, not skipped — names the closest candidate service even when it is not a duplicate, never "no similar service found" with nothing checked against
- [ ] Every CMDB CI relevant to a proposed component is checked and cross-referenced against kb-L1-enterprise-architecture's narrative — a mismatch between what the CMDB shows and what the KB claims is flagged as a finding, never silently resolved by picking one source
- [ ] Every FR in prd.md is mapped to a component with a stated blast-radius rationale (Low/Medium/High per the prompt's embedded classification guide) — no FR silently unmapped
- [ ] external_dependencies includes anything newly surfaced by the capability/technical-touch checks above (e.g. an identity-provider gap), not just what vision/PRD already named
- [ ] A genuinely empty service_catalog/cmdb_export (no parent enterprise) is stated explicitly as such, never confused with an unchecked or skipped catalog/CMDB

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to a real prd.md requirement, service_catalog entry, or CMDB CI |
| Hallucination | ≤ 0.10 | No invented service, CI, or dependency absent from the input sources |
| Consistency | 0.90 | existing_system_impact agrees with kb-L1-enterprise-architecture; no two components contradict on the same requirement |
| Relevance | 0.85 | Output is usable as-is by L1-planning-dependency-mapper and L1-planning-backlog-prioritizer |
| Reasoning quality | 0.80 | Every rationale/how_or_why_not explains the decision, not just restates the finding |
| Citation completeness | N/A | This agent grounds against prd.md/service_catalog/cmdb_export/KB directly, not a citation object — ci_id/matched_service_id/requirement_id substitute for citation |

## Reflection Checklist
- [ ] Every service in service_catalog.services[] was genuinely checked, not assumed clear
- [ ] Every CI in cmdb_export relevant to a proposed component was genuinely checked, not skipped as "probably not relevant"
- [ ] No CMDB/KB disagreement was silently reconciled instead of flagged
- [ ] "No existing internal systems affected" is never conflated with "no external dependencies" — both sections are independently populated

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
