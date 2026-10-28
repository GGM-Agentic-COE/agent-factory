# Evaluation — L0-planning-impact-assessor

## Quality Gates
- [ ] prd_output.status != success → status failed, INSUFFICIENT_CONTEXT, no artifact
- [ ] Every FR-NNN in prd_output appears in components_identified AND in some node's source_requirement
- [ ] Every service_catalog entry named in Capability check (closest match stated even when not a match)
- [ ] Every CMDB CI has exactly one node (impacted → component/existing; not impacted → existing-ci, no edges)
- [ ] Catalog + CMDB both empty → "no parent enterprise" stated; KB-mandatory infra (IdP, API Gateway, observability, secrets manager) added as external-dependency nodes
- [ ] CMDB/KB mismatches and stale/contaminated exports flagged, never reconciled
- [ ] Edge direction uniform: blocks dep→component, depends-on prerequisite→dependent, integrates-with producer→consumer
- [ ] cycle_check reproduced by independent DFS; FAIL → critical_path.nodes = [], no edge dropped
- [ ] critical_path reproduced by longest-path over blocks/depends-on only; all ties reported
- [ ] Mermaid is 1:1 with nodes[]/edges[] (ids, counts, directions, quoted labels, classDefs, %% comments)
- [ ] ids kebab-case and unique; no invented FR/CI/SVC ids
- [ ] executive_summary ≤ 20 words; rationale_summary ≤ 15 words; full text only in artifacts[0].content
- [ ] Executive Summary in artifact introduces no claim absent from sections below it

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every component, CI row, dependency traces to PRD/catalog/CMDB/KB |
| Hallucination | ≤ 0.10 | No invented ids, systems or integrations |
| Consistency | 0.90 | Items ↔ artifact ↔ mermaid agree; counts match |
| Relevance | 0.85 | Graph usable as topological-sort input downstream |
| Reasoning quality | 0.80 | Blast radius and exclusions explained |
| Citation completeness | 0.95 | Every row cites FR-NNN / CI / SVC id |

## Reflection Checklist
- [ ] All template sections present, no {placeholder} left
- [ ] No summary field contains full artifact text
- [ ] Node ids unique, kebab-case; FR coverage complete
- [ ] artifacts[0].content is the complete final markdown

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
