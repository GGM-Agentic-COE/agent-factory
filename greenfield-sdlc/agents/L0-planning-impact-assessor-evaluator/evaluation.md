# Evaluation — L0-impact-assessor-evaluator
Meta-quality of THIS evaluator's findings and fixes. The generator's rubric
(../L0-impact-assessor/evaluation.md) is the scoring source of truth — not restated here.

## Quality Gates
- [ ] Generator rubric fetched (github) and KB re-fetched (confluence) — tool outcomes recorded
- [ ] Every finding cites a specific id (ci_id, service_id, FR-id, node id, edge from→to)
- [ ] Capability + technical-impact checks re-derived from FRESH exports, not generator's copy
- [ ] Own DFS result and own longest-path result (with all ties) stated explicitly in findings
- [ ] Mermaid finding states node count, edge count, directions, shapes, styles, annotations
- [ ] Every fix has reasoning traced to source data; no invented data; no edge dropped for acyclicity
- [ ] Ambiguous direction / stale-export validity → escalate_to_hitl, never forced pass
- [ ] Document fixes applied to artifact-001 content AND JSON items before final_decision
- [ ] Unchanged document written byte-for-byte (content == generator artifacts[0].content)
- [ ] Confluence writer invoked unconditionally; storage.location == literal tool return (omitted if write failed)
- [ ] fixed_and_approved only when corrected content persisted
- [ ] Missing generator_output → INSUFFICIENT_CONTEXT; legitimate generator INSUFFICIENT_CONTEXT → approved as-is
- [ ] workflow_execution_id inherited from generator_output; new execution_id

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings match independently re-derived source truth |
| Hallucination | ≤ 0.05 | No invented CI/SVC/FR/edge in findings or fixes |
| Consistency | 0.95 | Items, findings, artifact, mermaid agree post-fix |
| Relevance | 0.90 | Findings actionable for backlog prioritiser / HITL |
| Reasoning quality | 0.90 | Every fix and escalation explained |
| Citation completeness | 0.95 | Every finding cites an id |

## Reflection Checklist
- [ ] No pass reported without showing re-derived result
- [ ] fixes_applied[].finding_id all resolve to a fail finding
- [ ] overall_score consistent with scores and pass flag (pass ⇔ overall_score ≥ 8.0 and no open fail)
- [ ] No storage.location constructed by the agent

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
