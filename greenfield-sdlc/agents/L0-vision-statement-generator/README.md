# L0-vision-statement-generator

## Purpose

Three separate analyses (idea, market, regulatory) aren't a decision — the
Product Lead needs one document with a north-star metric and roadmap
outline to approve or reject. This agent is also the last automated
checkpoint before a human reads the output: if a serious regulatory finding
gets dropped between the regulatory-feasibility-checker and this document,
it's this agent's reconciliation logic that would have caught it.

## What does it do?

Accepts the full outputs of `L0-idea-intake` (as `idea-brief.json`)
and `L0-regulatory-feasibility-checker` — plus `L0-vision-market-analyzer`
where it ran — and the viability score, and produces one reconciled vision
statement:
- Problem, target users, and value proposition carried forward without drift
- Market context condensed to the single most decision-relevant insight
- Regulatory posture with every Amber/Red constraint's mitigation summarized
- North-star metrics and a phase-level roadmap
- **Open risks** — every Amber/Red regulatory constraint MUST appear here,
  tied to a roadmap dependency; this is the concrete test of reconciliation,
  not just summarization
- A Section 2 Summary (vision, summary, principles, feasibility position), written last, that introduces no new claims

The document layout is **not embedded in the prompt**. It is
`vision-template.md`, read from GitHub with `tool-L0-github-reader-using-app`
(`template_repo` / `template_branch` / `vision_statement_template_folder` —
in this deployment `agentic-sdlc-knowledge-bases`, `main`,
`0. planning/vision-statement-generator/template`). Changing the layout
means editing that file, not the prompt. Since 2026-11-26 the layout follows
the DairyShield Product Vision (DS-VIS-001): Document Control and Approvals
tables, twelve numbered sections (vision and summary, problem, users,
capabilities, scope, market, regulatory posture, success measures, roadmap,
risks, decisions) and a glossary.

It saves the vision document to **S3** as `vision.md`, with
`tool-L0-s3-writer`, in this workflow run's folder — the one the
regulatory feasibility checker created, `<product name>/<workflow_execution_id>`,
taken from the checker evaluator's `artifacts[0].storage.folder`. It reads
`idea-brief.json` (and any `market-analysis.md`) from the brief's original
folder, `storage.source_folder`. It has no folder input and calls no
Confluence tool. The flow is:

```
S3: <source folder>/idea-brief.json ──► checker ──► S3: <product>/<new wf id>/regulatory-feasibility.md   (brief stays in the source folder)
GitHub: vision-template.md ──► generator ──► S3: <product>/<new wf id>/vision.md ──► evaluator (evaluate + fix) ──► Confluence: <Product Name>-vision
```

The document is a Draft: the Status row reads "Draft — pending Product Lead
sign-off".

**Product Name.** The user fills the `{{product_name}}` placeholder; that value
is used verbatim in the H1 and the Document Control Product row, and becomes the
Confluence title when the evaluator publishes. If no
name is supplied, the agent proposes one from the idea brief and labels it
"(proposed by agent — … confirm or replace)" in the Document Control table's Product row.

## How does it work?

1. Ingests the upstream item sets plus viability_score, and reads
   `idea-brief.json`, `regulatory-feasibility.md` and (optionally)
   `market-analysis.md` in a single S3 call. The brief is **JSON**,
   parsed by key path, not scanned as markdown
1a. Resolves the Product Name — the user's verbatim, or a proposed one, labelled as proposed
1b. Reads `vision-template.md` from GitHub (one call); unreadable → `REFERENCE_UNAVAILABLE`
2. Carries problem/users/value-proposition forward verbatim in substance
3. Condenses market SWOT into one paragraph — or, when no market analysis
   ran, writes Market Context as "Not assessed" rather than inferring one
4. Carries regulatory overall_status forward and summarizes every Amber/Red
   constraint's mitigation
5. Builds north-star metrics and a roadmap, with phase 1 required to address
   the single most severe open risk
6. Builds open_risks — cross-checks that every Amber/Red regulatory
   constraint produced exactly one entry here
7. Writes Section 2's Summary and Bottom line last, as a pure condensation
8. Reports viability_score exactly as received; does not compute, re-derive,
   round, or adjust it, and does not decide what follows (that's the
   workflow's `qg-L0-viability-score` gate, not this agent)
9. Saves the filled template to S3 as `vision.md` with
   `tool-L0-s3-writer` (one call, one retry on failure). If the write still
   fails, the whole document goes in the JSON artifact's `content` instead,
   so the evaluator can still read it

## Where the viability score comes from

`L0-regulatory-feasibility-checker` derives it, and its evaluator
re-derives it from the final constraints. It reaches this agent two ways
that must agree exactly: as the `viability_score` input parameter, and in
`regulatory-feasibility.md`'s Document Control table and Viability Score section. A
disagreement between the two is `INPUT_MALFORMED` — never resolved here by
picking one or averaging them.

There is no `viability-assessment.md` and no `L0-vision-viability-scorer`.
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
- **Optional:** `product_name` — proposed by the agent when absent

## Output

- **Type:** `vision_statement`
- **Items:** `product_name`, `executive_summary`, `problem_statement`, `target_users`,
  `value_proposition`, `market_context`, `regulatory_posture`,
  `north_star_metrics[]`, `roadmap[]`, `open_risks[]` — see `output_schema.json`
- **Artifacts:** `vision.md` in S3 — storage carries bucket, key, folder, size_bytes and uploaded_at copied from the S3 writer's reply, plus `write_mode` (saved / failed / not_saved)
- **Metadata:** every item carries `confidence` and `reasoning`; carried-forward
  items are checked against their upstream source for drift instead of citation
- **Summary:** metric/roadmap/risk counts, reconciliation decisions,
  viability_score and gate status, guardrail results

## Composition

```
agents/L0-vision-statement-generator/
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

prompts/L0-vision-statement-generator/
└── instructions.md
```
