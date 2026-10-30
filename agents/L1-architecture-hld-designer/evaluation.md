# Evaluation — L1-architecture-hld-designer

## Quality Gates
- [ ] hld.md has the header block (version, baseline, feature coverage, stack, correlation ID = workflow_execution_id) and §0–§8, or §3 omitted with a stated reason
- [ ] Every component, deployment row, encryption boundary and observability signal states BOTH target and MVP reality
- [ ] Every mocked / simplified / deferred / absent / unconfirmed item, every `not_met` NFR and every `deviation_recorded` principle maps to a GAP-xx in §8
- [ ] Every GAP-xx has an EA/ABP reference and an owner (or "Unassigned" + an open question)
- [ ] Every PRD NFR appears in §7; every ABP-xx from the KB appears in binding_principle_checks
- [ ] Diagrams are ASCII in code blocks — no Mermaid
- [ ] Input conflicts recorded as OQ-xx, never resolved silently
- [ ] hld.md published via tool-L1-confluence-create-page under `{workflow_execution_id}/`; artifacts[0].storage matches
- [ ] Output validates against output_schema.json; all gap_ids / participant_ids resolve

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every item traces to input docs or KB refs |
| Hallucination | ≤ 0.10 | No invented components, endpoints, owners, numbers, EA/ABP refs |
| Consistency | 0.90 | Items ↔ hld.md agree; realization ↔ gaps ↔ NFR status agree |
| Relevance | 0.85 | A reviewer can tell what is real today without opening other files |
| Reasoning quality | 0.80 | Realization, NFR status and principle outcomes are justified |
| Citation completeness | 0.95 | Components, flows, NFRs, principle checks, gaps cite source |

## Reflection Checklist
- [ ] No claim merges target and reality ("uses PostgreSQL" when MVP is SQLite)
- [ ] No NFR marked `met` without a stated mechanism or test
- [ ] Designed-not-built features shown as "(not built)" in §3/§8, not omitted
- [ ] Authorization matrix rows = endpoints × roles actually stated in inputs
- [ ] No summary field contains full hld.md prose
- [ ] IDs sequential: CMP, FLW, AZ, NFR, BPC, GAP, OQ

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
