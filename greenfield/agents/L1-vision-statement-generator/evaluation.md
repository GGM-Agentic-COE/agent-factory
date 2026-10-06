# Evaluation — L1-vision-statement-generator

## Checks
- [ ] All required fields present (see output_schema.json's top-level required list)
- [ ] **BLOCKER — Reconciliation:** every constraint_id in regulatory_posture.constraint_summaries appears in at least one open_risks entry's related_ids — coverage, not 1:1 count; grouping related Amber items into one combined risk is fine, a constraint_id appearing in NO entry is not
- [ ] problem_statement/target_users/value_proposition do not contradict idea-brief.json (the upstream source of record)
- [ ] roadmap phase 1 addresses the single most severe open risk
- [ ] executive_summary introduces no claim absent from the sections below it
- [ ] viability_score in items and in vision.md matches regulatory-feasibility.md and the input parameter exactly — carried, never recomputed, re-derived, rounded, or averaged
- [ ] Where the score was capped upstream by a Red or legal-review constraint, that constraint is covered in open_risks and named as the biggest open risk in the executive summary — the number and the narrative describe the same situation
- [ ] Product Name: the H1 and the Product Name row carry the same name. A name the agent proposed is labelled as proposed in the Product Name row — a proposed name presented as the user's is a fail
- [ ] vision.md was saved to blob storage in the request's folder_name, and the artifact's storage.location was built from the write tool's message. No Confluence tool was called by the generator — publishing is the evaluator's step, after evaluation. Nothing was written to GitHub

## Scores (minimum per dimension)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every carried-forward item matches its upstream source |
| Hallucination | ≤ 0.10 | No claim introduced that isn't grounded in an upstream input — and no market picture inferred when no market analysis was available |
| Consistency | 0.95 | Reconciliation check (above) passes fully — this is the highest consistency bar of any Phase 0 agent, since a dropped risk here reaches a human decision-maker |
| Relevance | 0.85 | Roadmap and metrics are usable as-is for Phase 1 planning |
| Reasoning quality | 0.80 | Every north_star_metric and roadmap phase explains its derivation |
| Citation completeness | N/A | This agent synthesizes upstream agent outputs, not KB/external sources — reconciliation check substitutes for citation |

**Sources of record:** `idea-brief.json` for problem/users/value (JSON, read by
key path), `regulatory-feasibility.md` for the constraint list *and* the
viability score, `market-analysis.md` for market context where it exists.
There is no `viability-assessment.md` and no viability scorer agent — a
reference to either is a stale artifact of an earlier pipeline version.

## Reflection Checklist
- [ ] Zero regulatory Amber/Red items missing from open_risks
- [ ] executive_summary written last, after all other sections finalized
- [ ] viability_score reported honestly even if low — not omitted or softened

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
