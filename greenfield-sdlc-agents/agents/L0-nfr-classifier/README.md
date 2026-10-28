# L0-nfr-classifier

## Purpose

A plausible-sounding NFR number with no source becomes a fake commitment
once it reaches the PRD. This agent classifies the non-functional boundary
conditions for every evaluated functional requirement so that each one is
either grounded in a real, citable source or honestly marked TBD. It also
closes TBDs that an enterprise group policy already answers, so open
questions aren't raised for things that are already decided.

## What does it do?

Accepts the evaluated requirement set from
`L0-requirements-elicitor-evaluator` and the vision document's regulatory
feasibility analysis, and produces:
- **nfr_classifications[]** — one entry per FR, same ids and order as the
  evaluated requirements:
  - `id`, `title`
  - `boundary_conditions[]` — only the genuinely applicable categories out of
    Performance, Security, Scalability, Availability, Compliance, Usability;
    each with a `boundary_condition` (an explicit number/rule, or the literal
    "TBD — needs stakeholder input"), a `rationale`, and a `source`
    (requirements, vision.md, regulatory-feasibility.md,
    kb-L0-enterprise-security, or "—" for TBD)
  - `confidence` and `reasoning` ("No NFR categories apply" when the list is
    empty — the FR's entry is never omitted)

It writes nothing to any store. The JSON output is the artifact of record;
there is no nfr-spec.md document.

## How does it work?

1. Inherits `workflow_execution_id` from the evaluated requirements and
   generates a fresh `execution_id`
2. Validates the precondition: a successful, non-empty requirement set is
   required, otherwise INSUFFICIENT_CONTEXT. A missing regulatory
   feasibility analysis is not fatal — Compliance conditions become TBD
3. Reads the vision document via `tool-L0-confluence-reader` and retrieves
   `kb-L0-nfr-classification-taxonomy` from GitHub
4. For each FR, asks each of the six taxonomy questions against its
   statement and keeps only the categories that genuinely apply
5. For each applicable category, looks for a number/rule in this order: the
   FR's statement, vision.md, regulatory-feasibility.md, then
   kb-L0-enterprise-security (ES3/ES4)
6. Writes the grounded value with its citation, or "TBD — needs stakeholder
   input" if no source answers it
7. Runs a mechanical self-check (one entry per FR, every non-TBD cited, every
   TBD checked against regulatory feasibility and enterprise security first)
   and emits the JSON. Judging whether a TBD was actually resolvable is left
   to `L0-nfr-classifier-evaluator`

## Input

- **Source:** agent_output from `L0-requirements-elicitor-evaluator`; vision
  document from Confluence
- **Required:** `requirements_output` — the evaluated requirement set
- **Required:** `confluence_vision_page_id` — Confluence page_id of the
  vision document
- **Required:** `github-nfr-classifier-kb-folder-location`,
  `github-nfr-classifier-kb-repo-name`, `github-nfr-classifier-kb-branch` —
  where `kb-L0-nfr-classification-taxonomy` lives
- **Optional:** `regulatory_feasibility_output` — if absent or failed,
  Compliance conditions are marked TBD

## Output

- **Type:** `nfr_classification`
- **Items:** `nfr_classifications[]`
- **Metadata:** every entry carries `confidence` and `reasoning`; every
  boundary condition carries a `source`
- **Summary:** FRs classified, category and TBD counts, which TBDs were
  resolved via enterprise security or regulatory feasibility, self-check
  changes, KBs consulted, guardrails, gaps flagged

## Composition

```
agents/L0-nfr-classifier/
├── L0-nfr-classifier-prompt.md
├── spec.yaml
└── README.md
```

Upstream: `L0-requirements-elicitor-evaluator`.
Downstream: `L0-nfr-classifier-evaluator`.
