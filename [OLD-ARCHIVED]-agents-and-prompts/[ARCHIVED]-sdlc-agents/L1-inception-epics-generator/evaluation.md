# Evaluation Criteria — L1-inception-epics-generator-agent

## Quality Gates (must pass)

| Criterion | Threshold | Method |
|-----------|-----------|--------|
| All FRs covered | 100% of input FRs in at least one feature's implements[] | Automated: set comparison |
| No orphan requirements | Zero FRs unassigned | Automated: count unassigned |
| Epic size 2-8 features | No violations | Automated: count per epic |
| IDs sequential | EPIC-01, EPIC-02... / FEAT-01-01, FEAT-01-02... | Automated: pattern check |
| No duplicate IDs | All IDs unique | Automated: uniqueness check |
| Priorities assigned | Every epic has a MoSCoW priority | Automated: field check |
| Features have implements[] | No empty implements | Automated: field check |
| Dependencies valid | All depends_on reference existing EPIC IDs | Automated: reference check |

## Evaluation Scores (LLM-as-Judge)

| Evaluator | Threshold | Direction |
|-----------|-----------|-----------|
| Faithfulness | ≥ 0.90 | Every feature traces to FRs in input |
| Hallucination | ≤ 0.10 | No invented features beyond input requirements |
| Consistency | ≥ 0.90 | Epics don't overlap or contradict |
| Relevance | ≥ 0.85 | Groupings are logical and deliverable |
| Reasoning quality | ≥ 0.80 | Grouping and priority decisions explained |
| Citation completeness | ≥ 0.95 | Every feature cites FR IDs |

## Epic Quality Rubric

| Dimension | Score 9-10 | Score 7-8 | Score 5-6 | Score < 5 |
|-----------|-----------|-----------|-----------|-----------|
| Grouping | Logical capability clusters, high cohesion | Mostly cohesive, one misplaced feature | Several features in wrong epic | Random grouping |
| Coverage | 100% FR coverage, NFRs assigned | All FRs covered, NFRs partially | Some FRs missing | Major gaps |
| Sizing | All epics 3-8 features, right for 2-4 cycles | Most right-sized, one edge case | Several too large or too small | Epics undeliverable |
| Dependencies | Minimal, enable parallel delivery | Correct but serial where parallel possible | Unnecessary dependencies | Circular or missing |
| Traceability | Full FR → feature → epic chain | Mostly complete, minor gaps | Several broken links | No traceability |

## Reflection Checklist

The agent must self-verify before delivering:

- [ ] Every FR from input appears in at least one feature's implements[]
- [ ] NFRs are assigned as cross-cutting to relevant epics
- [ ] Constraints mapped to affected epics
- [ ] Assumptions mapped as risks
- [ ] No epic has only 1 feature (merge or decompose further)
- [ ] Dependencies are minimised — can any epics run in parallel?
- [ ] Epic priorities reflect the highest-priority FR they contain
- [ ] Execution summary includes coverage count and dependency chain

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
