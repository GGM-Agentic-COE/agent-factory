# Evaluation — L1-planning-feature-cycle-mapper

## Quality Gates
- [ ] Output validates against output_schema.json
- [ ] No feature appears twice; no unplanned or left-out feature appears anywhere in items
- [ ] Every feature starts in a cycle strictly later than the end_cycle_id of each of its dependencies
- [ ] Summed effort per cycle (whole features + stories) never exceeds cycle_capacity_effort
- [ ] No work assigned to C-00; cycle_number always matches cycle_id
- [ ] No feature with epic_not_ready, effort above two cycles' capacity, or a left-out dependency is assigned; Story A never appears without Story B
- [ ] Every feature with effort above cycle capacity has is_split true and exactly Story A + Story B (efforts sum to the feature), B in a later cycle than A
- [ ] Every feature that fits one cycle has is_split false, stories [] and end_cycle_id = cycle_id
- [ ] Story numbers are sequential across the PI (US-001, US-002 …) with no restarts or duplicates
- [ ] summary_table has one row per feature_assignment, values identical to the assignments, and a correct total row

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every assignment traces to the backlog and pi_cycles |
| Hallucination | ≤ 0.10 | No invented effort values, dependencies, MVP scope or story scope |
| Consistency | 0.90 | Assignments, stories, summary_table and execution_summary agree |
| Relevance | 0.85 | Each feature's cycle and stories are clear enough to commit |
| Reasoning quality | 0.80 | Each summary says why the feature landed in its cycle(s) |
| Citation completeness | 0.95 | Every assignment cites its backlog row |

## Reflection Checklist
- [ ] Rank order respected; nothing pulled forward to fill spare capacity
- [ ] Unknown dependency IDs and features larger than two cycles raise a gap
- [ ] Gaps carry a concrete question for the RTE or Product Lead
- [ ] summary fields ≤ 150 characters
- [ ] No placeholder text; IDs (US-, GAP-) sequential

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
