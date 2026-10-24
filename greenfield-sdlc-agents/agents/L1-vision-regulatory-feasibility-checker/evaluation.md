# Evaluation — L1-vision-regulatory-feasibility-checker

## Quality Gates
- [ ] All required fields present: constraints (≥1), overall_status, open_items
- [ ] Every constraint has a citation naming a specific regulation/section — no generic citations
- [ ] Every Amber/Red constraint has a non-null mitigation OR requires_legal_review: true — schema-enforced, must not be bypassed
- [ ] overall_status.rationale references the specific constraint(s) driving the verdict, not a vague summary
- [ ] IDs sequential (CON-01...; OI-01...), no gaps or duplicates
- [ ] **BLOCKER:** no Red constraint present in reasoning/analysis is missing from the final constraints list — cross-check against KB coverage

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Every constraint traces to a real KB/lookup citation (higher bar than other agents — compliance risk) |
| Hallucination | ≤ 0.05 | No invented regulations (tighter than the 0.10 default — a fabricated citation here is worse than most other agents' hallucinations) |
| Consistency | 0.90 | overall_status is justified by, not contradicted by, the individual constraints |
| Relevance | 0.85 | Constraints assessed are the ones actually applicable to the stated activity/geography |
| Reasoning quality | 0.85 | Every mitigation is concrete and actionable, not generic ("comply with regulations") |
| Citation completeness | 1.00 | 100% required — this is the one agent where citation completeness is a hard gate, not a soft score |

## Reflection Checklist
- [ ] No Red constraint downgraded to Amber to avoid writing a mitigation
- [ ] requires_legal_review used only where no precedented mitigation exists — check it isn't a default escape hatch
- [ ] overall_status logic (worst-item vs. one-level-better-if-all-mitigated) is explicitly justified, not asserted

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
