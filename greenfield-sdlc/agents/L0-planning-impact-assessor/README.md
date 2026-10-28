# L0-impact-assessor

## Purpose
Combines Impact Assessment and Dependency Graph construction into one execution. The assessment grounds every PRD functional requirement against the real enterprise estate (service catalog, CMDB, architecture KB); its components and external dependencies become the node set of a dependency graph whose cycle check and critical path are proven by traversal. A wrong finding here becomes a wrong build sequence downstream, so both are produced from the same in-memory findings.

## What does it do?
- **Accepts:** `prd_output` (from L0-requirements-prd-composer), `service_catalog`, `cmdb_export`; reads `kb-L1-architecture-principles` from Confluence (page_id 524091393).
- **Produces:**
  - `items.impact_assessment` — meta points: impact level, ≤20-word summary, FR→component map, counts, flags
  - `items.dependency_graph` — nodes, edges, DFS `cycle_check`, longest-path `critical_path` (all ties)
  - `artifacts[0]` — full `<Product name>-impact-assessment.md` inlined in `content` (incl. mermaid)
  - `execution_summary` — plain-text bullets
- **Does not** persist to blob storage — the paired evaluator owns persistence.

## How does it work?
1. Validate input (`prd_output.status`, empty estate, export freshness/contamination).
2. Fetch KB via `tool-L1-confluence-fetch-page`.
3. Capability check (every service) + technical impact check (every CI), flag KB/CMDB mismatches.
4. Map every FR to a component with blast radius; list external dependencies (+ KB-mandatory infra if no parent enterprise).
5. Write Executive Summary last, from findings only.
6. Build nodes (component / external-dependency / existing-ci) and directed edges.
7. DFS cycle check → PASS/FAIL; on PASS longest-path over blocks/depends-on, report ties.
8. Self-check coverage; render mermaid 1:1; inline the document as artifact.

## Input
- **Source:** agent_output (prd_output) + direct_input/file_upload (catalog, CMDB)
- **Required:** `prd_output` — PRD AgentOutput; `service_catalog` — services[]; `cmdb_export` — configuration_items[], relationships[], export_metadata
- **Optional:** `run_date` — staleness reference; `kb_page_id` — default 524091393

## Output
- **Type:** `impact_assesment`
- **Items:** impact_assessment + dependency_graph (meta points only)
- **Metadata:** agent_id, version, execution_id, workflow_execution_id (inherited from prd_output)
- **Summary:** assessment counts, graph counts/cycle/critical path, KB mode, tools, artifact, gaps

## Composition
```
agents/L0-impact-assessor/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-merchant-refunds.json
│   ├── output-01-merchant-refunds.json
│   ├── input-02-no-parent-enterprise.json
│   └── output-02-no-parent-enterprise.json
└── golden/v1.0.0/
    ├── input-golden-01-claims-intake.json
    ├── golden-01-claims-intake.json
    ├── input-golden-02-prd-failed.json
    └── golden-02-prd-failed.json
prompts/L0-impact-assessor/
└── instructions.md
```
