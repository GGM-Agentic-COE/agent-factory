# Evaluation — L1-inception-vision-brief-extractor

## Quality Gates

- [ ] Brief ≤ 3,000 tokens (~2,400 words)
- [ ] All feature areas from input have ≥1 capability bullet
- [ ] All user types from input captured
- [ ] All numeric targets/thresholds preserved verbatim
- [ ] All regulatory references preserved (PSD2, GDPR, FCA, etc.)
- [ ] All integration systems captured
- [ ] MVP boundary (in/out) included
- [ ] No invented content (only what's stated or strongly implied)
- [ ] No IDs, priorities, or reasoning assigned (downstream job)

## Scores (≥ threshold to pass)

| Dimension | ≥ | Checks |
|-----------|---|--------|
| Completeness | 0.90 | All extractable facts from input captured |
| Faithfulness | 0.95 | Every bullet traces to input content |
| Conciseness | 0.85 | No elaboration beyond reconstruction needs |

## Reflection Checklist

- [ ] Compare section count: input feature areas vs brief capabilities
- [ ] Compare user count: input user types vs brief users
- [ ] Spot-check: 3 random numeric values from input appear in brief
- [ ] Brief fits within token budget
