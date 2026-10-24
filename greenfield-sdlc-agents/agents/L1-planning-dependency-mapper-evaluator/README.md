# L1-planning-dependency-mapper-evaluator

## Purpose

`L1-planning-dependency-mapper`'s own self-check runs a DFS and a
longest-path computation, but it is still the same agent grading its own
homework. The single most important thing this evaluator does is
independently RE-COMPUTE `cycle_check` and `critical_path` from the raw
`nodes`/`edges` — it never trusts the generator's own declared
`cycle_check.status` or `critical_path.nodes` at face value, because a
schema-valid graph with a reversed edge or an unverified cycle claim would
pass every structural check and still be wrong (exactly the bug
`phase-1/README.md` documents an earlier worked-example revision shipping
with).

## What does it do?

Scores the mapper's draft output against
`L1-planning-dependency-mapper/evaluation.md`. Re-derives:
- **Cycle check** — its own DFS traversal over every node/edge, comparing
  the result against the generator's declared `cycle_check.status`
- **Critical path** — its own longest-path walk over `depends-on`/`blocks`
  edges only, comparing the result against the generator's declared
  `critical_path.nodes`, including whether a genuine tie was reported
  honestly or missed
- **Edge direction** — spot-checks `from`/`to` against
  impact-assessment.md's own stated prerequisite language for every edge

Fixes what's mechanically fixable (a reversed edge, a missed tie);
escalates a genuinely unresolvable cycle rather than dropping an edge to
force acyclicity.

## How does it work?

1. Loads `L1-planning-dependency-mapper/evaluation.md` as source of truth
2. Re-runs DFS cycle detection independently over the raw node/edge list
3. Re-runs longest-path computation independently over the blocking
   (`depends-on`/`blocks`) edge subset
4. Compares both results against the generator's declared
   `cycle_check`/`critical_path` — any mismatch is at least a fail finding
5. Spot-checks a sample of edges' direction against
   impact-assessment.md's own stated prerequisite language
6. Fixes mechanically-recoverable issues (e.g. one reversed edge); escalates
   a genuine, confirmed cycle instead of forcing acyclicity
7. If a fix changes graph content (a node, an edge, the cycle_check or
   critical_path fields), corrects dependency-graph.json too and overwrites
   it at the SAME s3 location — same artifact id, not a new one, so every
   downstream consumer already referencing
   `generator_output.content.artifacts[0]` picks up the correction for
   free. A fix confined to items-only bookkeeping needs no document edit
8. `final_decision` per the standard rule

## Input

- **Source:** agent_output (`L1-planning-dependency-mapper`'s original
  input + draft output)

## Output

- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision` — shared shape across all Phase 0/1
  evaluators, see `output_schema.json`
- **Summary:** overall_score, pass/fail, final_decision, the independently
  re-derived cycle_check/critical_path result specifically, what was
  fixed and re-saved, knowledge bases consulted, gaps flagged

## Composition

```
agents/L1-planning-dependency-mapper-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-critical-path-fix.json
│   ├── output-01-critical-path-fix.json
│   ├── input-02-legitimate-cycle-escalation.json
│   └── output-02-legitimate-cycle-escalation.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-edge-direction-bug.json
    └── golden-02-edge-direction-bug.json

prompts/L1-planning-dependency-mapper-evaluator/
└── instructions.md
```
