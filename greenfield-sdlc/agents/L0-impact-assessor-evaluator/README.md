# L0-impact-assessor-evaluator

## Purpose
Sole quality gate between `L0-impact-assessor` and `L0-backlog-prioritizer`. Independently re-derives every impact finding and every graph result (DFS cycle check, longest-path critical path, mermaid 1:1) from freshly-fetched source data, fixes what the data mechanically supports, escalates what it doesn't, and publishes the final evaluated document to Confluence.

## What does it do?
- **Accepts:** `generator_output` (inline JSON from `L0-impact-assessor`); `<product_name>-impact-assessment.md` from S3.
- **Fetches independently:** PRD and target architecture from Confluence; evaluation rubric (`evaluation.md`) from GitHub.
- **Produces:**
  - `items.scores`, `overall_score`, `pass`
  - `items.findings[]` — one per gate, each citing an id and showing re-derived results
  - `items.fixes_applied[]` — before/after with reasoning
  - `items.final_decision` — `approved | fixed_and_approved | escalate_to_hitl`
  - `artifacts[0]` — evaluated `<product_name>-impact-assessment.md` with `storage.confluence_page_id` and `blob_storage_location`
  - `execution_summary` — plain-text bullets incl. the Confluence page id

## How does it work?
1. Inherit `workflow_execution_id` from `generator_output.workflow_execution_id` (never create a new one).
2. Generate a fresh `execution_id` (exec-\<uuid\>) for this agent run.
3. Fetch PRD from Confluence (`{{confluence-prd-page-id}}`).
4. Fetch target architecture from Confluence (`{{confluence-target-architecture-page-id}}`).
5. Read `<product_name>-impact-assessment.md` from S3 using inherited `<workflow_execution_id>`.
6. Fetch evaluation rubric from GitHub (`{{github-impact-assessor-evaluation}}`).
7. Re-run capability check and technical impact check; flag freshness/contamination.
8. Verify FR coverage, grounding, node-id uniqueness.
9. Re-run DFS cycle check; on PASS, longest-path with all ties; check edge directions.
10. Verify mermaid (counts, directions, shapes, styles, annotations) and distillation limits.
11. Fix mechanically-recoverable gaps; escalate ambiguity.
12. Write the evaluated document to Confluence unconditionally; record the returned `confluence_page_id`.

## Input
- **Source:** Inline `generator_output` from L0-impact-assessor + S3 (assessment doc) + Confluence (PRD, target arch) + GitHub (rubric)
- **Runtime variables:**
  - `{{confluence-prd-page-id}}` — PRD page
  - `{{confluence-target-architecture-page-id}}` — target architecture page
  - `{{confluence-impact-assessment-space-key}}` — Confluence space for the writer
  - `{{github-impact-assessor-evaluation}}` — evaluation rubric folder
  - `{{github-repo-name}}` — GitHub repo
  - `{{github-branch-name}}` — GitHub branch

## Output
- **Type:** `evaluation_result`
- **Items:** `scores`, `overall_score`, `pass`, `findings`, `fixes_applied`, `final_decision`
- **Artifact:** `<product_name>-impact-assessment.md` with `blob_storage_location` (S3) and `confluence_page_id` (from Confluence writer return)
- **IDs:** inherited `workflow_execution_id`; fresh `execution_id` (exec-\<uuid\>)

## Workflow position
```
S3 (<workflow_execution_id>/) ──┐
Confluence (PRD, target arch)   ├──▶  L0-impact-assessor-evaluator  ──▶  Confluence (evaluated doc)
GitHub (evaluation rubric)     ──┘
```

## Composition
```
agents/L0-impact-assessor-evaluator/
├── spec.yaml
└── README.md
prompts/L0-impact-assessor-evaluator/
└── instructions.md
```
