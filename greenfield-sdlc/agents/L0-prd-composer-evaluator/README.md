# L0-prd-composer-evaluator

## Purpose

The PRD is the single source of truth that `L0-impact-assessor` and
`L0-dependency-mapper` read from Confluence, so a requirement
dropped or attached to the wrong FR during composition propagates into every
plan built on it. This agent is the independent check (S6) on the
composition, and the only agent permitted to publish the PRD. Nothing is
published until it approves.

## What does it do?

Accepts `L0-prd-composer`'s output (held in memory, including the full PRD
markdown) and its original input, and produces:
- The **corrected PRD items** in exactly the composer's structure, with every
  fix already applied
- An **evaluation block**:
  - `scores` — faithfulness, hallucination, consistency, relevance,
    reasoning quality, citation completeness
  - `overall_score` (0-10) and `pass`
  - `findings[]` — pass/fail per gate, each naming the FR-id, category or
    constraint involved
  - `fixes_applied[]` — before/after and the reasoning for every change
  - `final_decision` — approved, fixed_and_approved, or escalate_to_hitl
- The **published PRD** — the corrected `{product_name}-prd.md` uploaded to
  Confluence, referenced in `artifacts[0].storage` (location null when not
  published)

## How does it work?

1. Inherits `workflow_execution_id` from the composer's output and generates
   a fresh `execution_id`
2. Retrieves the composer's evaluation file from GitHub
3. Approves a legitimate INSUFFICIENT_CONTEXT as-is (no upload). If the
   composer reported success but the PRD markdown is missing, records a fail
   and escalates rather than rebuilding it from condensed items
4. **Zero-drop FRs:** every evaluated FR-id is present with its statement
   unchanged
5. **Zero-drop NFRs:** every boundary condition appears under the same FR it
   belongs to — dropped or misattached both fail
6. **Citation:** every assumption/constraint/risk names real FR-ids or
   "program-level" and maps to the vision or a specific FR
7. **Table structure:** Assumptions/Constraints/Risks are the templated
   tables with sequential ASSUM-/CON-/RISK- IDs matching the items'
   `short_title` prefixes
8. **Success-metrics absence** and **compound splits carried verbatim**
9. Fixes grounded gaps in both the JSON and the PRD markdown so they stay
   consistent; escalates anything needing new scope judgment
10. On approved or fixed_and_approved, publishes the corrected PRD via
    `tool-L0-confluence-writer`; never publishes on escalate_to_hitl

## Input

- **Source:** agent_output from `L0-prd-composer`, held in memory
- **Required:** `original_input` — the composer's input (`requirements_output`,
  `nfr_spec_output`)
- **Required:** `generator_output` — the composer's JSON output including
  `artifacts[0].content`
- **Required:** `github-prd-evaluator-folder-location`,
  `github-prd-evaluator-repo-name`, `github-prd-evaluator-branch` — where the
  composer's evaluation file lives
- **Required:** `prd-upload-confluence-location` — Confluence space_key (or
  folder) to publish to

## Output

- **Type:** `prd` (same structure as the composer) plus `evaluation`
- **Items:** corrected `executive_summary`, `compound_splits[]`,
  `assumptions[]`, `constraints[]`, `risks[]`, `requirements[]`,
  `open_questions[]`
- **Evaluation:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision`
- **Artifacts:** `{product_name}-prd.md` with `storage.provider: confluence`
  and the page location, or null when not published
- **Summary:** overall score and decision, zero-drop results, citation /
  table-structure / success-metrics findings, what was modified, whether the
  PRD was uploaded (and where, or why not), KBs, guardrails, gaps flagged

## Composition

```
agents/L0-prd-composer-evaluator/
├── L0-prd-composer-evaluator-prompt.md
├── evaluation.md
├── spec.yaml
└── README.md
```

Upstream: `L0-prd-composer`.
Downstream: `L0-impact-assessor`, `L0-dependency-mapper`
(read the published PRD from Confluence).
