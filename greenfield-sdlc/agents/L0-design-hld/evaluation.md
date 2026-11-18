# Evaluation — L1-design-hld

## Quality Gates
- [ ] Every requirement (FR-*) and NFR (NFR-*) found in Requirements.md appears in at least one item's traceability array, or in gaps — never silently dropped
- [ ] Every component traces to >=1 requirement or NFR (satisfies_requirement_ids or satisfies_nfr_ids non-empty)
- [ ] Every integration has a protocol; from/to component ids resolve to real entries in components[]
- [ ] Every data_flow's contains_pii is set deliberately (not defaulted false without checking)
- [ ] artifacts[0].storage.location keyed by workflow_execution_id, not execution_id
- [ ] No summary/*_summary field contains the full artifact rationale text

## Scores (>= threshold to pass)
| Evaluator | >= | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every component/integration/data-flow/NFR-mapping traces to text actually present in Requirements.md, not general knowledge of similar systems |
| Hallucination | <= 0.10 | No invented components, integrations, or NFR approaches |
| Consistency | 0.90 | Component groupings and integration directions match the document's own dependency/integration language |
| EA adherence | 0.90 | Component types and integration patterns conform to kb-L1-enterprise-architecture |
| Reasoning quality | 0.80 | Component/NFR-mapping summaries explain the grouping/approach |
| Citation completeness | 0.95 | Every item cites Requirements.md plus a specific heading/table-row/FR-NFR id — never just the document name |

## Reflection Checklist
- [ ] All requirements/NFRs present as items or gaps; ids well-formed (C-NN, INT-NN, DF-NN, FR-NN..NNNN, NFR-NN..NNNN) and assigned in document order
- [ ] No placeholder text; no rationale silently copied into an item summary
- [ ] No component invented without requirement/NFR grounding; no inferred integration protocol presented as if explicitly stated in the source
- [ ] Design checked against kb-L1-enterprise-architecture's conventions
- [ ] Gaps reported (not guessed) for any unmappable requirement/NFR

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
