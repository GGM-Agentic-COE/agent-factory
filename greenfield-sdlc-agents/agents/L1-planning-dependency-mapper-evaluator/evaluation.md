# Evaluation — L1-planning-dependency-mapper-evaluator

This covers THIS evaluator's own meta-quality — not L1-planning-dependency-mapper's
rubric (that lives in `../L1-planning-dependency-mapper/evaluation.md`,
loaded at runtime, not duplicated here).

## Quality Gates
- [ ] `cycle_check` was independently RE-COMPUTED via this evaluator's own
      DFS over the raw node/edge list — never accepted because the
      generator's `cycle_check.status` says PASS
- [ ] `critical_path` was independently RE-COMPUTED via this evaluator's
      own longest-path walk over `depends-on`/`blocks` edges — never
      accepted because the generator's `critical_path.nodes` looks
      plausible
- [ ] Edge direction was checked node-by-node against impact-assessment.md's
      own stated prerequisite language — a reversed edge (schema-valid,
      semantically wrong) is exactly the class of bug this evaluator exists
      to catch
- [ ] A fix that changes graph content is pushed back into the SAME
      dependency-graph.json at the SAME s3 location — never left corrected
      in items only while the saved file still holds the pre-fix graph
- [ ] A legitimate cycle escalation (generator status: failed,
      cycle_check.status: FAIL) is approved as-is when the cycle is
      genuinely confirmed by this evaluator's own re-derivation — never
      "fixed" by dropping an edge to force acyclicity

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.95 | Findings accurately describe the actual generator output |
| Hallucination | ≤ 0.05 | No fix introduces a node/edge not grounded in impact-assessment.md/prd.md |
| Consistency | 0.90 | overall_score and pass boolean agree with the individual dimension scores |
| Reasoning quality | 0.85 | Every finding names the specific node/edge id and the exact traversal step that produced it |

## Reflection Checklist
- [ ] No finding is a rubber stamp ("cycle check looks right") without
      showing the actual re-derived DFS/longest-path result
- [ ] escalate_to_hitl used only for a genuinely unresolvable cycle, not
      overused as a shortcut for an edge that's merely awkward
- [ ] fixes_applied preserves every node/edge that was already correct

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
