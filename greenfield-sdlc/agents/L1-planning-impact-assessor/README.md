# L1-planning-impact-assessor

## Purpose

Phase 2 planning (dependency mapping, backlog prioritization) needs to know
what a new product duplicates, touches, or newly depends on before effort is
committed. HarvestLink is built WITHIN an already-established enterprise
(Thornbury Foods Group), not in isolation — this agent's job is to make that
check real and explicit rather than a rubber-stamped "no existing systems
affected," which would only be true for a product with genuinely no parent
enterprise at all.

## What does it do?

Accepts an approved `prd.md` (from `L1-requirements-prd-composer`) plus the
enterprise's own service-catalog and CMDB exports, and runs three checks in
sequence, none skipped:
- A **capability check** (service catalog, service grain) — does an existing
  service already provide a similar capability, avoiding a duplicate build?
- A **technical touch check** (CMDB, configuration-item grain) — for every
  relevant existing CI, is it touched, and how, or explicitly not, and why?
- A **cross-reference** of both against `kb-L1-enterprise-architecture`'s
  narrative — if the KB and the CMDB/catalog disagree, that mismatch is
  itself a finding, never silently resolved by picking one source.

It then maps every requirement to a component with a blast-radius
classification, and lists every external dependency — including anything
newly surfaced by the checks above (e.g. an identity-provider gap invisible
at vision/requirements stage).

## How does it work?

1. Validates `prd_output.status == "success"` — fails fast
   (`INSUFFICIENT_CONTEXT`) otherwise
2. Checks every service in `service_catalog.services[]` against the PRD's
   proposed capabilities; names the closest candidate even when it is not a
   duplicate, and states specifically why it isn't
3. Checks every CI in `cmdb_export.configuration_items[]` relevant to a
   proposed component, states explicitly whether it's touched and how, or
   why not, and cross-references `kb-L1-enterprise-architecture`'s
   integration-relevance narrative for the same CI
4. Maps every FR in `prd.md` to a new or existing component, classified
   Low/Medium/High blast radius per the guide embedded in the prompt (S4)
5. Lists external dependencies, including any newly surfaced by step 3
6. Self-checks mechanically: every catalog service and every relevant CI
   genuinely checked, every FR mapped, no CMDB/KB mismatch silently
   resolved — the full rubric (independent re-derivation of both checks) is
   delegated to `L1-planning-impact-assessor-evaluator` downstream, per S6
7. Saves the filled `impact-assessment.md` template to blob storage; items
   carry the same facts in full, not condensed — this agent's facts are
   already short, atomic statements, same principle as
   `L1-requirements-elicitor`

## Input

- **Source:** agent_output (`prd.md` from `L1-requirements-prd-composer`)
  plus two External data exports (not a KB, not agent_output)
- **Required:** `prd_output` — the PRD composer's full output, status must
  be `success`; `service_catalog` — service-catalog export (service grain);
  `cmdb_export` — CMDB export (configuration-item grain). An empty catalog/
  CMDB is valid ONLY for a product with genuinely no parent enterprise.

## Output

- **Type:** `impact_assessment`
- **Items:** `capability_check`, `existing_system_impact[]`, `components[]`,
  `external_dependencies[]` — see `output_schema.json`. Like
  `L1-requirements-elicitor`, facts are carried in FULL in items, not
  condensed — they're already short, atomic statements
- **Artifacts:** `impact-assessment.md` — the human-readable document
- **Metadata:** every item carries a `rationale`/`how_or_why_not` explaining
  the decision; `ci_id`/`matched_service_id`/`requirement_id` are this
  agent's citation equivalent, since it grounds against `prd.md`,
  `service_catalog`, and `cmdb_export` directly, not a knowledge base
- **Summary:** checks run, mismatches found, blast-radius decisions,
  knowledge bases consulted, guardrails evaluated, tools invoked, gaps
  flagged

## Composition

```
agents/L1-planning-impact-assessor/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-typical.json
│   ├── output-01-typical.json
│   ├── input-02-no-parent-enterprise.json
│   └── output-02-no-parent-enterprise.json
└── golden/v1.0.0/
    ├── input-golden-01-thornbury.json
    ├── golden-01-thornbury.json
    ├── input-golden-02-insufficient.json
    └── golden-02-insufficient.json

prompts/L1-planning-impact-assessor/
└── instructions.md
```
