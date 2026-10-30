# Evaluation — L1-planning-feature-cycle-mapper-evaluator

Meta-quality only: are this evaluator's findings genuine, its fixes correct and its decision sound.
The rubric for the mapper itself lives in ../L1-planning-feature-cycle-mapper/evaluation.md and is not repeated here.

## Quality Gates
- [ ] Output validates against output_schema.json
- [ ] Plan was re-derived from generator_input, not copied from generator_output
- [ ] Every finding is reproducible: its expected value matches the re-derived plan or a named gate
- [ ] No defect covered by the mapper rubric is missed (seeded-defect goldens catch 100%)
- [ ] One quality_gates entry per gate in the mapper's evaluation.md, in the same order
- [ ] corrected_output (when present) validates against the mapper's output_schema.json and passes every mapper gate
- [ ] corrected_output equals the re-derived plan; values without findings are untouched
- [ ] final_decision follows the decision rules; approved has zero findings; rejected has a gap with the action needed
- [ ] No plan invented when the mapper's input was insufficient

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Finding precision | 0.95 | Findings that are genuine defects |
| Finding recall | 0.95 | Real defects that were found |
| Fix correctness | 0.95 | Fixes that produce the re-derived value |
| Decision accuracy | 1.00 | Decision matches findings and post-fix scores |
| Severity calibration | 0.85 | Severity matches the prompt's blocker/major/minor rules |
| Citation completeness | 0.95 | Findings cite location and rule |

## Reflection Checklist
- [ ] Each finding has concrete expected and actual values
- [ ] Before and after scores both reported; after equals before when nothing was fixed
- [ ] summary_table in corrected_output re-rendered from corrected assignments
- [ ] No reliance on the mapper's execution_summary or self-check claims
- [ ] IDs (FND-, QG-, GAP-) sequential; no placeholder text

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
