# Evaluation — L1-planning-dependency-mapper

## Quality Gates
- [ ] `cycle_check` was produced by an ACTUAL depth-first-search traversal
      (recursion-stack back-edge detection) over every node/edge — never
      asserted PASS because the graph "looks" acyclic
- [ ] `critical_path` was produced by an ACTUAL longest-path computation over
      `depends-on`/`blocks` edges only (`integrates-with` excluded, non-blocking
      by definition) — never asserted from eyeballing the longest-looking chain
- [ ] A genuine TIE in longest-path length is reported honestly as a tie,
      naming every chain that shares the maximum length — never arbitrarily
      resolved to a single "winner" to make the output look simpler
- [ ] Edge direction is UNIFORM: `from` is always upstream/prerequisite, `to`
      is always downstream/dependent, for every edge regardless of `type`
      (`depends-on`, `blocks`, `integrates-with` all follow the same rule)
- [ ] Every FR-NNN in prd.md appears in at least one node's `source_requirement`
      — checked by set membership against prd.md's full FR list, not by
      counting nodes and assuming coverage
- [ ] Every component and external dependency named in impact-assessment.md
      has a corresponding node — no silent drop
- [ ] Node ids are kebab-case (`^[a-z0-9-]+$`), unique, no duplicates
- [ ] If `cycle_check.status` is FAIL, overall AgentOutput `status` is
      `"failed"` (escalate) — a cyclic graph is never silently "fixed" by
      dropping the offending edge and reporting success

## Scores (≥ threshold to pass)
| Evaluator | ≥ | Checks |
|-----------|---|--------|
| Faithfulness | 0.90 | Every node/edge traces to a real impact-assessment.md component or external dependency |
| Hallucination | ≤ 0.10 | No node, edge, or FR coverage invented beyond impact-assessment.md / prd.md |
| Consistency | 0.90 | `cycle_check` and `critical_path` are consistent with the actual edge set — no orphaned claim |
| Relevance | 0.85 | Output is directly usable as topological-sort input by backlog-prioritizer |
| Reasoning quality | 0.80 | `critical_path.rationale` states the actual path length and any tie, not just a list of ids |
| Citation completeness | N/A | This agent grounds against impact-assessment.md/prd.md directly, not a KB — `source_requirement` and node `label` substitute for citation |

## Reflection Checklist
- [ ] DFS cycle check was actually run (traced node-by-node), not eyeballed
- [ ] Longest-path computation was actually run edge-by-edge over the
      blocking subset, not eyeballed
- [ ] No summary/rationale field silently contains less information than the
      graph itself would show — the graph fields (nodes/edges/cycle_check/
      critical_path) ARE the meta-points here, per output_schema.json's own
      note on why this agent departs from the usual condensation pattern

## Reflection Process
1. Generate → 2. Check all items above → 3. Fix silently → 4. Deliver final only
