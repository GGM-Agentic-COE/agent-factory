# L1-planning-backlog-prioritizer

## Purpose

Feature decomposition and dependency mapping tell you *what* needs to be built and *what depends on what* — but not *what order to build it in*. This agent closes that gap: it scores each decomposed feature with WSJF or RICE at feature granularity, weights the ranking by how much delivering a feature unblocks downstream work, and produces a single sequenced backlog the planning team can act on directly.

## What does it do?

Accepts:
- A decomposed feature set (id, name, description)
- A dependency graph between those feature ids (blocks / blocked_by)
- Business-value scoring inputs (WSJF or RICE fields) supplied by the Product Lead

Produces:
- Per-feature priority score, rank, and dependency-unblocking score (structured items)
- A rendered `prioritized-backlog.md` document with the full ranked table and rationale
- A gap list for any feature that couldn't be scored due to missing inputs

## How does it work?

1. Ingest features, dependency graph, and value-scoring inputs; reject unknown feature id references.
2. Compute a WSJF or RICE priority_score per feature from the Product Lead's value inputs. Features missing inputs are never guessed — they're reported as gaps.
3. Walk the dependency graph to compute a dependency_unblocking_score per feature.
4. Blend the two: a feature that unblocks several others moves up the ranking even at a mid-range standalone value score, with the adjustment documented.
5. Optionally cross-check feature ids against an adjacent Jira backlog for duplicates.
6. Assign sequential ranks and render `prioritized-backlog.md`.
7. Run a basic self-check (completeness, ID validity, no dependency-order contradictions) before delivery.

## Input

- **Source:** agent output (features.json, dependency-graph.json) + direct input or file upload (value-scoring inputs)
- **Required:** `features` — feature list from L1-design-feature-decomposer
- **Required:** `dependency_graph` — dependency-graph.json from L1-design-dependency-mapper
- **Required:** `value_scoring_inputs` — RICE/WSJF fields per feature from the Product Lead
- **Optional:** `scoring_method` — WSJF (default) or RICE
- **Optional:** `adjacent_backlog_check` — cross-check against Jira via tool-L1-jira-fetch-issue

## Output

- **Type:** `prioritized_backlog`
- **Items:** `prioritized_features[]` (rank, scores, dependency links, distilled summary, citation) and `gaps[]` (unscored features)
- **Artifact:** `prioritized-backlog.md` — the full ranked table and per-feature rationale
- **Metadata:** confidence and citation on every scored feature
- **Summary:** plain-text execution_summary covering counts, rank adjustments, KBs/guardrails/tools used, and gaps

## Composition

```
agents/L1-planning-backlog-prioritizer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json
│   ├── output-01-happy-path.json
│   ├── input-02-edge-case.json
│   └── output-02-edge-case.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json
    ├── golden-01-happy-path.json
    ├── input-golden-02-edge-case.json
    └── golden-02-edge-case.json

prompts/L1-planning-backlog-prioritizer/
└── instructions.md
```
