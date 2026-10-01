# L1-vision-statement-generator

## Purpose

Three separate analyses (idea, market, regulatory) aren't a decision — the
Product Lead needs one document with a north-star metric and roadmap
outline to approve or reject. This agent is also the last automated
checkpoint before a human reads the output: if a serious regulatory finding
gets dropped between the regulatory-feasibility-checker and this document,
it's this agent's reconciliation logic that would have caught it.

## What does it do?

Accepts the full outputs of `L1-vision-idea-intake` (as `idea-brief.json`)
and `L1-vision-regulatory-feasibility-checker` — plus `L1-vision-market-analyzer`
where it ran — and the viability score, and produces one reconciled vision
statement:
- Problem, target users, and value proposition carried forward without drift
- Market context condensed to the single most decision-relevant insight
- Regulatory posture with every Amber/Red constraint's mitigation summarized
- North-star metrics and a phase-level roadmap
- **Open risks** — every Amber/Red regulatory constraint MUST appear here,
  tied to a roadmap dependency; this is the concrete test of reconciliation,
  not just summarization
- An executive summary, written last, that introduces no new claims

It produces the `vision.md` artifact only. It does **not** publish it —
that's a separate Utility agent (`L1-confluence-publisher`), per the
Core/Utility split: this agent's logic must not break if the client swaps
Confluence for Notion.

## How does it work?

1. Ingests the upstream item sets plus viability_score, and reads
   `idea-brief.json`, `regulatory-feasibility.md` and (optionally)
   `market-analysis.md` in a single blob-storage call. The brief is **JSON**,
   parsed by key path, not scanned as markdown
1a. Reads its `examples/` folder from GitHub with `tool-L1-github-reader-using-app`
   (`reference_repo`, `reference_branch`, `examples_folder` — all from the request).
   Shape guidance only: an example's numbers are never a source, and an unavailable
   folder is tolerated. The repository is read-only — `vision.md` goes to blob storage
2. Carries problem/users/value-proposition forward verbatim in substance
3. Condenses market SWOT into one paragraph — or, when no market analysis
   ran, writes Market Context as "Not assessed" rather than inferring one
4. Carries regulatory overall_status forward and summarizes every Amber/Red
   constraint's mitigation
5. Builds north-star metrics and a roadmap, with phase 1 required to address
   the single most severe open risk
6. Builds open_risks — cross-checks that every Amber/Red regulatory
   constraint produced exactly one entry here
7. Writes the executive summary last, as a pure condensation
8. Reports viability_score exactly as received; does not compute, re-derive,
   round, or adjust it, and does not decide whether to publish (that's the
   workflow's `qg-L1-viability-score` gate, not this agent)

## Where the viability score comes from

`L1-vision-regulatory-feasibility-checker` derives it, and its evaluator
re-derives it from the final constraints. It reaches this agent two ways
that must agree exactly: as the `viability_score` input parameter, and in
`regulatory-feasibility.md`'s header table and Viability Score section. A
disagreement between the two is `INPUT_MALFORMED` — never resolved here by
picking one or averaging them.

There is no `viability-assessment.md` and no `L1-vision-viability-scorer`.
If either turns up in the folder, it is a stale artifact of an earlier
pipeline version and is ignored.

## Input

- **Source:** agent_output from the upstream Phase 0 generators
- **Required:** `idea_brief_items` (from `idea-brief.json`),
  `regulatory_feasibility_items`, `viability_score`
- **Optional:** `market_analysis_items` — the market analyzer may not have
  run. Its absence is never a failure: Market Context reads "Not assessed",
  `market_context` is emitted with confidence 0 and `traced_to` "none", and
  no market-sourced open risks are carried

## Output

- **Type:** `vision_statement`
- **Items:** `executive_summary`, `problem_statement`, `target_users`,
  `value_proposition`, `market_context`, `regulatory_posture`,
  `north_star_metrics[]`, `roadmap[]`, `open_risks[]` — see `output_schema.json`
- **Artifacts:** `vision.md`
- **Metadata:** every item carries `confidence` and `reasoning`; carried-forward
  items are checked against their upstream source for drift instead of citation
- **Summary:** metric/roadmap/risk counts, reconciliation decisions,
  viability_score and gate status, guardrail results

## Composition

```
agents/L1-vision-statement-generator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-missing-upstream.json
│   └── output-02-missing-upstream.json
└── golden/v1.0.0/
    ├── input-golden-01-harvestlink.json
    ├── golden-01-harvestlink.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-vision-statement-generator/
└── instructions.md
```
