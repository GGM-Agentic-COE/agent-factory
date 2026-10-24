# Evaluation — L1-vision-market-analyzer

## Quality Gates
- [ ] All required fields present: competitor_matrix, swot (all 4 quadrants), market_sizing (tam/sam/som), industry_trends, customer_insights, pricing_benchmarks, data_sufficiency
- [ ] Every competitor_matrix entry has a non-empty citation with source_reference + retrieved_date
- [ ] Every market_sizing.{tam,sam,som} entry has a non-empty citation, even when reasoning flags a data gap
- [ ] Every industry_trends, customer_insights, and pricing_benchmarks entry has a non-empty citation with source_reference + retrieved_date
- [ ] Every SWOT item's reasoning names a specific competitor id or idea-brief fact
- [ ] data_sufficiency.status is "insufficient" (not fabricated coverage) when KB + search both returned thin results, and its rationale names which of the 5 dimensions were thin
- [ ] No sizing figure, trend, insight, or price point is fabricated — a genuine gap is an explicit low-confidence entry with reasoning stating the gap, or an empty array, never an invented plausible-sounding number
- [ ] IDs sequential per category (CM-01...; ST/WK/OP/TH-01...; TR-01...; CI-01...; PB-01...), no gaps or duplicates

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every competitor/sizing/trend/insight/pricing claim traces to a KB or search citation |
| Hallucination | ≤ 0.10 | No invented competitors, sizing figures, trends, insights, or price points |
| Consistency | 0.90 | SWOT doesn't contradict the competitor matrix, trends, or insights it's derived from |
| Relevance | 0.85 | Competitors, trends, insights, and pricing benchmarks reviewed are realistic for the stated target users |
| Reasoning quality | 0.80 | SWOT and other reasoning fields explain derivation, not just restate the statement |
| Citation completeness | 0.95 | 100% of competitor_matrix, market_sizing, industry_trends, customer_insights, and pricing_benchmarks entries cite a source — this is a BLOCKER, not just scored |

## Reflection Checklist
- [ ] No competitor, market_sizing, industry_trends, customer_insights, or pricing_benchmarks entry lacks a citation
- [ ] No SWOT item is generic filler unconnected to a specific competitor/fact
- [ ] data_sufficiency rationale is honest, not padded to look thorough, and names which dimensions were thin

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
