# Evaluation Criteria — L1-design-hld-generator-agent

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All epics have components | 100% coverage | Automated: every epic_id in at least one component's implements_features |
| APIs have request/response schemas | No empty schemas | Automated: field check |
| Data model entities have fields | No empty fields array | Automated: field check |
| Technology choices in EA KB | 100% | LLM: verify against enterprise architecture KB |
| No orphan components | Every component traces to a feature | Automated: implements_features non-empty |
| ADRs present | ≥1 ADR | Automated: count |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every component traces to input features |
| Hallucination | ≤ 0.10 | No invented features or technologies |
| Consistency | ≥ 0.90 | Components don't contradict each other |
| EA Compliance | ≥ 0.95 | All technology choices match EA KB |
| Completeness | ≥ 0.85 | All features have architectural representation |

## Reflection Checklist

- [ ] Every feature from input appears in at least one component's implements_features
- [ ] Technology choices match enterprise architecture KB exactly
- [ ] API contracts are specific (method, path, schemas — not just descriptions)
- [ ] Data model includes field types and constraints (not just entity names)
- [ ] Integrations map to features that need external systems
- [ ] No component exists without a feature justification
- [ ] Cross-cutting concerns addressed (auth, logging, monitoring, errors)
- [ ] At least one ADR documents a significant architectural decision
- [ ] Deployment topology is realistic (not over-provisioned)

## Reflection Process (mandatory)

1. **Generate** initial HLD
2. **Log** `[REFLECTING] Checking against evaluation criteria and EA KB`
3. **Check** every item in Reflection Checklist
4. **Verify** all technology choices against enterprise architecture KB
5. **Identify** gaps or EA violations
6. **Fix** silently
7. **Deliver** final output only

Reflection findings appear in execution_summary.
