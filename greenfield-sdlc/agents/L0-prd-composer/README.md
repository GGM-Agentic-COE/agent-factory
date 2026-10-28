# L0-prd-composer

## Purpose

Evaluated requirements and an evaluated NFR set sitting in two separate JSON
outputs aren't something a team can review, approve, or plan from. This
agent composes them into one Product Requirements Document, the Phase 1
artifact that the planning agents read as their single source of truth. Its
job is to compose, not analyse: no requirement or boundary condition may be
dropped, re-classified, or re-derived along the way.

## What does it do?

Accepts the evaluated outputs of `L0-requirements-elicitor-evaluator` and
`L0-nfr-classifier-evaluator` and produces `{product_name}-prd.md`, with:
- A **Legend** naming the three sources (requirements, NFRs,
  `{product_name}-vision.md`) and the approval fields left for a human
- An **Executive Summary**, written last, introducing nothing new
- **Out of Scope** — capabilities the vision implies or defers that have no FR
- A **Traceability Matrix** — FR, Priority, MVP, NFR categories, TBD count
- **Compound Requirements Split**, carried forward verbatim
- **Assumptions** (ASSUM-NNN), **Constraints** (CON-NNN) and **Risks**
  (RISK-NNN) as ID-tagged tables, each traced to FR(s) or "program-level"
- **Requirements** — every FR's statement and citation verbatim, an MVP
  tag, and its full NFR table
- **Open Questions** — every TBD boundary condition, plus any coverage gap
  found reading FRs and NFRs side by side
- A **Glossary** of recurring domain-specific terms

The full PRD goes in `artifacts[0].content`. Items carry `requirements[]` and
`compound_splits[]` in full, and condensed (<=150 char) summaries for the
executive summary, assumptions, constraints, risks, and open questions. It
adds no success metrics and writes nothing to Confluence or any other store.

## How does it work?

1. Inherits `workflow_execution_id` from upstream and generates a fresh
   `execution_id`
2. Validates both upstream outputs succeeded, otherwise returns
   INSUFFICIENT_CONTEXT
3. Retrieves the human-supplied `product_name` (noting in the JSON, not the
   PRD, if the vision document isn't titled `{product_name}-vision.md`) and
   the optional vision Confluence link ("link NA" if empty)
4. Carries every FR's statement, citation, and NFR table forward verbatim, in
   the same order — an FR with no NFRs gets an explicit "No NFR categories
   apply"
5. Tags MVP status per FR from the vision roadmap/value proposition (Priority
   as a secondary signal); NFR rows inherit their FR's tag unless the source
   frames them as later-phase
6. Builds the Assumptions/Constraints/Risks tables from the vision's
   regulatory posture and open risks, adding a new row only when a specific
   FR reveals one
7. Builds Out of Scope, the Glossary, Open Questions, and the Traceability
   Matrix, then writes the Executive Summary last
8. Runs a mechanical self-check (FR count matches, no NFR row dropped, every
   tag and ID present, nothing truncated) and passes the PRD in memory to
   `L0-prd-composer-evaluator`

## Input

- **Source:** agent_output from `L0-requirements-elicitor-evaluator` and
  `L0-nfr-classifier-evaluator`
- **Required:** `requirements_output` — the evaluated requirement set
- **Required:** `nfr_spec_output` — the evaluated NFR set
- **Required:** `product_name` — human-supplied product name used to name the
  PRD and every vision reference
- **Optional:** `OPTIONAL_vision_doc_confluence_link` — Confluence link to the
  vision document; "link NA" if empty

## Output

- **Type:** `prd`
- **Items:** `executive_summary`, `compound_splits[]`, `assumptions[]`,
  `constraints[]`, `risks[]`, `requirements[]` (with `nfrs[]`),
  `open_questions[]`
- **Artifacts:** `{product_name}-prd.md`, held in memory in
  `artifacts[0].content` (not published)
- **Metadata:** items carry `confidence` and `reasoning`;
  assumption/constraint/risk `short_title`s carry their table ID prefix
- **Summary:** plain-text execution summary of what was composed

## Composition

```
agents/L0-prd-composer/
├── L0-prd-composer-prompt.md
├── spec.yaml
└── README.md
```

Upstream: `L0-requirements-elicitor-evaluator`, `L0-nfr-classifier-evaluator`.
Downstream: `L0-prd-composer-evaluator` (receives the PRD in memory and is
the only agent that publishes it).
