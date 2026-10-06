# Evaluation — L1-vision-regulatory-feasibility-checker

## Checks
- [ ] All required fields present: constraints (≥1), overall_status, categories_not_applicable, viability, open_items
- [ ] Every constraint has a citation naming a specific regulation/section — no generic citations
- [ ] **BLOCKER — Jurisdiction:** the brief's `target_geography` and the jurisdiction each KB declares in its `#jurisdiction` section were compared before any assessment began, and every citation belongs to the resolved jurisdiction. An out-of-jurisdiction instrument is a fabricated citation in effect, not a near-miss — it reads as complete and well-sourced while binding nothing, and it passes both an existence check and a plausibility check. A geography the KBs do not cover is a `JURISDICTION_MISMATCH` failure, never a translated assessment
- [ ] No false equivalence: a local regime named correctly but reasoned through the mechanics of the better-known foreign regime it resembles is the same defect as a wrong citation
- [ ] Where a regime binds at sub-national as well as national level (licensing, labour, workplace safety, weights and measures, local trading permissions), that layer is a constraint or an open_item — not silently folded into the national answer
- [ ] Every Amber/Red constraint has a non-null mitigation OR requires_legal_review: true — schema-enforced, must not be bypassed
- [ ] overall_status.rationale references the specific constraint(s) driving the verdict, not a vague summary
- [ ] Every applicable category in `kb-L1-regulatory-frameworks-index#coverage-categories` is either a constraint or a categories_not_applicable entry — a silently absent category is a coverage failure, not a shorter output. That KB section is the single source for both the sweep and its audit; neither agent keeps its own copy
- [ ] IDs sequential (CON-01...; OI-01...; VC-01, VC-02), no gaps or duplicates
- [ ] **BLOCKER:** no Red constraint present in reasoning/analysis is missing from the final constraints list — cross-check against KB coverage
- [ ] **BLOCKER — Viability derivation:** weighted_score equals (regulatory_posture × 0.60) + (idea_clarity × 0.40) to one decimal; every qualifying cap appears in caps_applied; final_score is the LOWEST of weighted_score and every cap; recommendation agrees with final_score against the threshold of 7
- [ ] The score in regulatory-feasibility.md's header table, its Viability Score section, and items.viability.viability_score are the same number

## Scores (minimum per dimension)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every constraint traces to a real KB/lookup citation (higher bar than other agents — compliance risk) |
| Hallucination | ≤ 0.05 | No invented regulations (tighter than the 0.10 default — a fabricated citation here is worse than most other agents' hallucinations) |
| Consistency | 0.90 | overall_status is justified by, not contradicted by, the individual constraints; viability_score is justified by, not contradicted by, overall_status and the caps |
| Relevance | 0.85 | Constraints assessed are the ones actually applicable to the stated activity/geography |
| Reasoning quality | 0.85 | Every mitigation is concrete and actionable, not generic ("comply with regulations"); every viability component names what it was traced to |
| Citation completeness | 1.00 | 100% required — this is the one agent where citation completeness is a hard requirement, not a soft score |

## Reflection Checklist
- [ ] No Red constraint downgraded to Amber to avoid writing a mitigation, or to avoid firing the red_constraint cap
- [ ] requires_legal_review used only where no precedented mitigation exists — check it isn't a default escape hatch, and note it caps the score at 6.5 when used
- [ ] overall_status logic (worst-item vs. one-level-better-if-all-mitigated) is explicitly justified, not asserted
- [ ] The regulatory scenario patterns that applied (not-yet-in-force rules, transition relief, thresholds, extraterritorial reach, third-party permissions, pre-approval regimes, ongoing duties, overlapping regulators) are handled per the prompt's Edge Cases Section D, not flattened into a single generic constraint. These stay in the prompt, not the KB — they are behaviours, not facts
- [ ] idea_clarity is scored from idea-brief.json's own content, never from how well this assessment was written
- [ ] A below-threshold score is reported exactly as derived — not rounded up, not softened, no cap dropped to lift it above 7

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
