# L1-planning-dependency-mapper

## Purpose

`L1-planning-backlog-prioritizer` needs a topological-sort-ready graph, and
Phase 4's `L1-design-hld` needs to know the real build-order constraints
between components — not a hand-wave. A dependency graph that is merely
schema-valid can still be wrong: an earlier revision of this project's own
worked example shipped with a reversed edge that passed JSON Schema
validation but produced a nonsensical critical path (see
`phase-1/README.md`). This agent exists to run the actual graph traversal
— DFS cycle detection, longest blocking-path computation — not just
assemble the shape and assert the answer.

## What does it do?

Accepts `impact-assessment.md` and `prd.md` (both full upstream
`agent_output`) and produces `dependency-graph.json`:
- **Nodes** — one per component (from impact-assessment.md's Components
  Identified table, tracing back to its FR-NNN) and one per external
  dependency (from its External Dependencies list)
- **Edges** — uniform prerequisite → dependent direction, regardless of
  whether the edge is `depends-on` (component-to-component), `blocks`
  (external-dependency-to-component), or `integrates-with` (non-blocking
  peer integration)
- **cycle_check** — the result of an actual depth-first-search traversal,
  never asserted
- **critical_path** — the result of an actual longest-path computation
  over `depends-on`/`blocks` edges only (`integrates-with` excluded, since
  it is non-blocking by definition), including honest reporting of a
  genuine tie rather than an arbitrary tie-break

It never invents a node impact-assessment.md doesn't name, never drops an
FR from coverage, and never silently "fixes" a detected cycle by removing
the offending edge — a cycle escalates (`status: failed`) instead.

## How does it work?

1. Validates both upstream outputs are `status: success` — fails fast
   (`INSUFFICIENT_CONTEXT`) if either is missing or itself failed
2. Builds one node per component in impact-assessment.md's Components
   Identified table (type `component`, `source_requirement` from its
   FR-NNN(s)) and one node per entry in External Dependencies (type
   `external-dependency`, no `source_requirement`)
3. Builds edges from impact-assessment.md's own stated prerequisite
   relationships (blast-radius/blocking language) and prd.md's
   component-to-component technical dependencies — always
   prerequisite → dependent, for every edge type
4. Runs an explicit DFS cycle check over the full node/edge set — recursion-
   stack back-edge detection, not a visual scan
5. Runs an explicit longest-path computation over `depends-on`/`blocks`
   edges only, reporting every chain that ties for maximum length
6. Self-checks mechanically: every FR-NNN in prd.md covered by some node,
   every impact-assessment.md component/external-dependency has a node, no
   duplicate node ids
7. Saves the filled `dependency-graph.json` to blob storage; items carry
   the identical content — see `output_schema.json`'s own note on why this
   agent departs from the framework's usual items/artifact condensation
   pattern (a graph has no narrative to condense away from)

## Input

- **Source:** agent_output (`impact-assessment.md` from
  `L1-planning-impact-assessor`, `prd.md` from
  `L1-requirements-prd-composer`)
- **Required:** `impact_assessment_output`, `prd_output` — both full
  upstream `agent_output`, both `status: success`

## Output

- **Type:** `dependency_graph`
- **Items:** `product_name`, `source_artifacts`, `nodes[]`, `edges[]`,
  `cycle_check`, `critical_path` — see `output_schema.json`. Unlike every
  other agent in this framework, items carry the SAME content as the
  artifact, not a condensed meta-point version — there is no narrative to
  separate from a summary
- **Artifacts:** `dependency-graph.json` — the same content, saved to s3
  for `L1-planning-backlog-prioritizer` and Phase 4's `L1-design-hld` to
  retrieve directly
- **Metadata:** no per-node/per-edge confidence or reasoning field, by
  design — `cycle_check` and `critical_path` are this agent's
  confidence-equivalent, earned by actually running the algorithm
- **Summary:** node/edge counts, cycle-check result, critical-path result
  (including any tie), what reflection found, knowledge bases consulted,
  guardrails evaluated, gaps flagged

## Composition

```
agents/L1-planning-dependency-mapper/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-insufficient.json
│   └── output-02-insufficient.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-cycle-detected.json
    └── golden-02-cycle-detected.json

prompts/L1-planning-dependency-mapper/
└── instructions.md
```
