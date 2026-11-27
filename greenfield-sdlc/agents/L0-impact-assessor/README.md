# L0-impact-assessor

## Purpose
Combines Impact Assessment and Dependency Graph construction into one execution. Grounds every PRD functional requirement against the enterprise estate via freshly-fetched source data; its components and external dependencies become the node set of a dependency graph whose cycle check and critical path are proven by traversal. A wrong finding here becomes a wrong build sequence downstream.

## What does it do?
- **Accepts:** PRD and target architecture from Confluence (two separate reader calls); document template from GitHub.
- **Produces:**
  - `items.impact_assessment` — impact level, ≤20-word summary, FR→component map, counts, flags
  - `items.dependency_graph` — nodes, edges, DFS `cycle_check`, longest-path `critical_path` (all ties)
  - `artifacts[0]` — `<product_name>-impact-assessment.md` uploaded to S3 under `<workflow_execution_id>/`
  - `execution_summary` — plain-text bullets
- **Does not** write to Confluence — the paired evaluator owns that step.

## How does it work?
1. Generate a fresh `workflow_execution_id` (wf-\<uuid\>) — this is the run identifier for all downstream agents.
2. Fetch PRD from Confluence (`{{confluence-prd-page-id}}`).
3. Fetch target architecture from Confluence (`{{confluence-target-architecture-page-id}}`).
4. Fetch document template from GitHub (`{{github-impact-assessor-template}}`).
5. Capability check (every service) + technical impact check (every CI); flag CMDB/KB mismatches.
6. Map every FR to a component with blast radius; list external dependencies.
7. Write Executive Summary last, from findings only.
8. Build nodes (`component` / `external-dependency` / `existing-ci`) and directed edges.
9. DFS cycle check → PASS/FAIL; on PASS longest-path over blocks/depends-on, report all ties.
10. Self-check coverage; render mermaid 1:1 from computed graph.
11. Populate the fetched template, append mermaid under `## Dependency Graph`, upload to S3.

## Input
- **Source:** Confluence (PRD + target architecture), GitHub (document template)
- **Runtime variables:**
  - `{{confluence-prd-page-id}}` — PRD page
  - `{{confluence-target-architecture-page-id}}` — target architecture page
  - `{{github-impact-assessor-template}}` — template folder location
  - `{{github-repo-name}}` — GitHub repo
  - `{{github-branch-name}}` — GitHub branch

## Output
- **Type:** `impact_assesment` (wire spelling retained)
- **Items:** `impact_assessment` + `dependency_graph`
- **Artifact:** `<product_name>-impact-assessment.md` in S3 at `<workflow_execution_id>/<product_name>-impact-assessment.md`
- **IDs:** fresh `workflow_execution_id` (wf-\<uuid\>); fresh `execution_id` (exec-\<uuid\>)

## Workflow position
```
Confluence (PRD, target arch) ──┐
GitHub (template)               ├──▶  L0-impact-assessor  ──▶  S3  ──▶  L0-impact-assessor-evaluator
```

## Composition
```
agents/L0-impact-assessor/
├── spec.yaml
└── README.md
prompts/L0-impact-assessor/
└── instructions.md
```
