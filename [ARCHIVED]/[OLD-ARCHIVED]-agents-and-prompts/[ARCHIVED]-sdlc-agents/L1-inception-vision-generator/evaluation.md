# Evaluation — L1-inception-vision-generator

## Quality Gates

- [ ] All 5 sections present (Executive Summary, Business Context, Full Scope Vision, MVP Scope, Risks & Dependencies)
- [ ] Executive Summary ≤ 5 sentences
- [ ] Feature Areas ≥ 4 with description + capabilities + user value
- [ ] MVP features ≥ 5 with priority + rationale
- [ ] Out-of-scope ≥ 3 with deferral reason
- [ ] User Journeys ≥ 2 with numbered steps + outcomes
- [ ] Risks ≥ 4 with likelihood + impact + mitigation
- [ ] Success metrics are numeric and measurable (no "improve" / "enhance")
- [ ] No placeholder text (`{{...}}` or `<!-- -->`)
- [ ] Artifact uploaded (blob storage 200 response)

## Scores (≥ threshold to pass)

| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every claim traces to domain KB or input |
| Hallucination | ≤ 0.10 | No invented data/stats/regulations |
| Domain grounding | 0.90 | Features, users, constraints from KB |
| Specificity | 0.85 | Concrete metrics, named entities, no buzzwords |
| Consistency | 0.90 | No contradictions across sections |
| Completeness | 0.85 | All subsections populated |

## Reflection Checklist

Before delivering, verify:

- [ ] Problem Statement is specific and quantifiable
- [ ] Business Drivers cite domain KB context
- [ ] Target Users ≥ 3 with domain-relevant roles
- [ ] Feature Areas are domain-specific business capabilities (not "user management")
- [ ] Integration Points reference real systems from domain
- [ ] User Journeys ≥ 2 with numbered steps + outcomes
- [ ] MVP is strict subset of Full Scope Vision
- [ ] Constraints/Assumptions state "Risk if wrong"
- [ ] Risks have Likelihood + Impact + Mitigation
- [ ] Open Questions ≥ 3 for requirements analysis
- [ ] No vague language ("world-class", "seamless", "intuitive", "cutting-edge")
- [ ] No technology/architecture decisions (belongs in HLD)
- [ ] Document is complete and actionable — not a template with gaps

## Reflection Process

1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
