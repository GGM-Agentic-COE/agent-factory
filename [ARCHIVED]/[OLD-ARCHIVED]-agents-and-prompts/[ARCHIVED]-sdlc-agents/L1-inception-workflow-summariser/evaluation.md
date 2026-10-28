# Evaluation — L1-inception-workflow-summariser

## Quality Gates
- [ ] All input agents mentioned in execution_flow (100%)
- [ ] No invented data (0 claims not traceable to input)
- [ ] No raw JSON in output
- [ ] Workflow outcome matches agent statuses
- [ ] No duplicate resource entries

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every claim traces to an agent's execution_summary |
| Hallucination | ≤ 0.05 | No invented counts, artifacts, or statuses |
| Completeness | 0.95 | All agents, artifacts covered |
| Clarity | 0.85 | Non-technical reader can understand |
| Consistency | 0.90 | No contradictions between sections |

## Reflection Checklist
- [ ] Every agent in input array mentioned in execution_flow
- [ ] request_and_intent reflects actual workflow trigger
- [ ] Artifact names/locations match what agents produced
- [ ] Failed agents highlighted in outcome
- [ ] No raw JSON fragments
- [ ] Summary is concise (≤ 10 bullets)

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
