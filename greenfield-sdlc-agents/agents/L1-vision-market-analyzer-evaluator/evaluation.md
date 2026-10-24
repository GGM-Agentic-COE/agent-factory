# Evaluation — L1-vision-market-analyzer-evaluator

This covers THIS evaluator's own meta-quality — not L1-vision-market-analyzer's
rubric (loaded at runtime from `../L1-vision-market-analyzer/evaluation.md`).

## Quality Gates
- [ ] Citation check was exhaustive (100% of competitor_matrix, market_sizing tam/sam/som, industry_trends, customer_insights, and pricing_benchmarks entries), not sampled
- [ ] No fabricated citation was added to "fix" an uncited claim — that path always escalates
- [ ] Every SWOT finding checks the reasoning field's specificity, not just its presence
- [ ] Every market_sizing, industry_trends, customer_insights, and pricing_benchmarks finding checks the reasoning field's specificity, same treatment as SWOT/competitor_matrix
- [ ] A legitimate data_sufficiency: "insufficient" verdict is evaluated for honesty, not treated as an automatic defect — including a per-dimension "thin" note, not just an overall status

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output |
| Hallucination | ≤ 0.05 | No fix introduces an unverified citation or fact |
| Consistency | 0.90 | overall_score and pass agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding's detail names the specific entry/id it's about |

## Reflection Checklist
- [ ] Every competitor entry actually checked, not assumed fine because the count looked right
- [ ] escalate_to_hitl used for any uncited or fabricated-looking claim, never patched over
- [ ] fixes_applied preserves everything that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
