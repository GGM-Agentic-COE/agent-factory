# Evaluation Criteria — L1-inception-stories-generator-agent

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All features decomposed | 100% coverage | Automated: count features in input vs features with stories |
| Story points ≤ 5 | No violations | Automated: check every story |
| AC count 3-5 per story | No violations | Automated: count per story |
| Given/When/Then format | 100% AC | Automated: regex check |
| Dependencies acyclic | No cycles | Automated: graph traversal |
| No intra-feature Tier 1 deps | Foundation independent within feature | Automated: dependency check |
| Title format | "As a / I want / So that" | Automated: regex check |
| All stories have implements[] | No empty | Automated: field check |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every story traces to a feature/FR |
| Hallucination | ≤ 0.10 | No invented capabilities beyond input |
| Consistency | ≥ 0.90 | Stories don't contradict each other |
| Relevance | ≥ 0.85 | Stories are implementable, not vague |
| Reasoning quality | ≥ 0.80 | Tier/points/sequence decisions explained |
| Citation completeness | ≥ 0.95 | Every story cites feature_id and FR |

## Story Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Decomposition | Feature fully decomposed, right-sized stories | Most stories right-sized, one may be too large | Some stories too large or too small | Stories don't decompose the feature |
| Sequencing | Perfect tier ordering, team can implement in sequence | Mostly correct, one minor ordering issue | Several sequencing issues | No logical order |
| AC quality | All testable, Given/When/Then, specific outcomes | Most testable, minor vagueness | Several vague AC | AC untestable |
| Dependencies | Acyclic, minimal, enable parallel work | Correct but could be more parallel | Some unnecessary deps | Circular or missing deps |
| Completeness | All FRs + NFRs addressed | FRs covered, NFRs partially | Some FRs missing | Major gaps |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] Every feature has ≥ 2 stories
- [ ] Tier 1 stories exist for every feature (setup/foundation)
- [ ] No story exceeds 5 points
- [ ] Dependencies allow a team to start immediately (Tier 1 has no intra-feature deps)
- [ ] NFRs from epic are reflected in at least one story (usually Tier 3)
- [ ] Acceptance criteria are specific enough for a developer to implement and QA to test
- [ ] Execution summary includes recommended cycle sequence

## Reflection Process (mandatory)

The agent MUST perform reflection before delivering output:

1. **Generate** initial output following processing rules
2. **Log** `[REFLECTING] Checking output against evaluation criteria`
3. **Check** every item in the Reflection Checklist above
4. **Identify** gaps, errors, inconsistencies, or missed items
5. **Log** each finding: `[REFLECTING] Found: <description>`
6. **Fix** each issue — amend the output silently
7. **Log** each resolution: `[REFLECTING] Resolved: <what was fixed>`
8. **Deliver** only the final corrected output

The reflection findings and resolutions should appear in the execution_summary 
(what reflection found and changed) but the interim output must never be shown.
