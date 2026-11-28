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
`L0-nfr-classifier-evaluator` and fills the fixed template
`kb-L0-prd-template` (read from GitHub) to produce `{product_name}-prd.md`, with:
- **Purpose and Scope**, and **Document Control** naming the three sources
  (requirements, NFRs, `{product_name}-vision.md`) and the approval fields left
  for a human
- **Product Overview** (goals G-NN, capabilities CAP-NN), **Users and Roles**
  with a permissions matrix, and **Key User Journeys**
- **Release Plan and Scope**: each FR tagged to a release from the vision
  roadmap, plus Out of Scope
- **Functional Requirements**: every FR's statement, citation and acceptance
  criteria verbatim, and the compound-requirements split
- **Non-Functional Requirements**: every boundary condition verbatim as an
  NFR-NN row, and every TBD as an NQ-NN target to be set
- **Data and Integration**: business entities and personal-data inventory
- **Regulatory and Compliance Mapping** (CON-NN) and **Success Metrics**
  (NSM-NN, LI-NN), carried from the vision only
- **Assumptions** (AS-NN), **Dependencies** (DP-NN) and **Risks** (OR-NN),
  each traced to FR(s) or "program-level"
- **Open Questions** (OQ-NN), including coverage gaps found reading FRs and
  NFRs side by side
- **Traceability Matrix** and **Glossary**

The full PRD goes in `artifacts[0].content`. Items carry `requirements[]` and
`compound_splits[]` in full, and condensed (<=150 char) summaries for the
product summary, assumptions, constraints, risks, and open questions. It
invents nothing and writes nothing to Confluence or any other store.

## How does it work?

1. Inherits `workflow_execution_id` from upstream and generates a fresh
   `execution_id`
2. Validates both upstream outputs succeeded, otherwise returns
   INSUFFICIENT_CONTEXT
3. Retrieves the human-supplied `product_name` (noting in the JSON, not the
   PRD, if the vision document isn't titled `{product_name}-vision.md`) and
   the optional vision Confluence link ("link NA" if empty)
4. Reads `kb-L0-prd-template` from GitHub with the GitHub reader tool
5. Carries every FR and NFR boundary condition forward verbatim, in the same
   order; TBD conditions become NQ rows
6. Tags each FR's release from the vision roadmap/value proposition (Priority
   as a secondary signal); NFR rows inherit their FR's release unless the
   source frames them as later-phase
7. Builds the context, compliance, metrics, assumption, dependency and risk
   sections from the vision, adding a row only when a specific FR reveals one
8. Builds Open Questions, the Traceability Matrix and Glossary, then writes the
   product summary last
9. Runs a mechanical self-check (FR count matches, no NFR row dropped, every
   tag and key present, nothing truncated) and passes the PRD in memory to
   `L0-prd-composer-evaluator`

## Input

- **Source:** agent_output from `L0-requirements-elicitor-evaluator` and
  `L0-nfr-classifier-evaluator`
- **Required:** `requirements_output` — the evaluated requirement set
- **Required:** `nfr_spec_output` — the evaluated NFR set
- **Required:** `product_name` — human-supplied product name used to name the
  PRD and every vision reference
- **Required:** `prd-template-github-folder-location`, `agent-github-repo-name`,
  `agent-github-repo-branch` — where the GitHub reader finds `kb-L0-prd-template`
- **Optional:** `OPTIONAL_vision_doc_confluence_link` — Confluence link to the
  vision document; "link NA" if empty

## Output

- **Type:** `prd`
- **Items:** `executive_summary`, `compound_splits[]`, `assumptions[]`,
  `constraints[]`, `risks[]`, `requirements[]` (with `release` and `nfrs[]`),
  `open_questions[]`
- **Artifacts:** `{product_name}-prd.md`, held in memory in
  `artifacts[0].content` (not published)
- **Metadata:** items carry `confidence` and `reasoning`;
  assumption/constraint/risk `short_title`s carry their table key prefix
  (`AS-`, `CON-`, `OR-`)
- **Summary:** plain-text execution summary of what was composed

## Composition

```
prompts/L0-prd-composer/instructions.md
agents/L0-prd-composer/
├── spec.yaml
└── README.md
greenfield-sdlc-kbs/kb-L0-prd-template/content/prd-template.md
```

Upstream: `L0-requirements-elicitor-evaluator`, `L0-nfr-classifier-evaluator`.
Downstream: `L0-prd-composer-evaluator` (receives the PRD in memory and is
the only agent that publishes it).
