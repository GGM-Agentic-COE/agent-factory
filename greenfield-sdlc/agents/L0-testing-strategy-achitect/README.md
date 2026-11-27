# L0-testing-strategy-architect

## Purpose
Establish the Programme Increment (PI) architecture-level testing strategy (`test-strategy.md`) from the Target Architecture and Solution Architecture documents (and optional PRD), defining testing rules, tiers, gates, environments, data policy, and regression pack governance without inventing thresholds or using a roadmap.

## What does it do?
- **Accepts:** Target Architecture document and Solution Architecture document from Confluence, optional PRD from Confluence, and the Test Strategy document template from GitHub.
- **Produces:** `AgentOutput` (`content.type = test_strategy`, `schema_version = 1.0`) referencing `test-strategy.md` stored in blob storage under `<workflow_execution_id>`.
- **Preserves traceability:** Links every derived policy (`traced_to`), open pending decision (`PEND-*`), and numeric budget/boolean control back to authoritative declaration IDs, marking absent/unbudgeted items explicitly as `[TO BE CONFIRMED]` / `Blocked`.
- **Performs validation & self-check:** Checks mandatory sections (`APP-2`, `DAT-1`, `DAT-3`), Target approval, and Solution `satisfies_from` version parity before generating the 12-section strategy + Appendix A.

## How does it work?
1. Retrieves Target Architecture document, Solution Architecture document, optional PRD (Confluence), and Test Strategy document template (GitHub).
2. Validates document inventories, blocking status, mandatory sections (`APP-2`, `DAT-1`, `DAT-3`), Target `approved` status, and `satisfies_from` version match.
3. Generates a fresh `workflow_execution_id` (`wf-<uuid>`) (or inherits when chained) and a fresh `execution_id` (`exec-<uuid>`).
4. Maps declaration IDs (`INT-D*`, `QA-*`, `FLOW-*`), derives the 4 testing tiers (`feature`, `contract`, `integration`, `regression+NFR`) with gate-model cadences (`G1`–`G4`), derives environment topology (`§6`) and fixture/data policy (`§7`), applies fixed QE pack governance values (`§8`, `§10`), and classifies budgeted vs. unbudgeted NFRs (`§5`, `§9`).
5. Populates the GitHub-retrieved template (`§1`–`§12` + `Appendix A`), writes `test-strategy.md` to blob storage, and returns metadata and storage artifact details in `AgentOutput`.

## Input
- **Source:** Confluence (Target Architecture document, Solution Architecture document, optional PRD) and GitHub (Test Strategy document template).
- **Required runtime parameters:**
  - `{{confluence-target-architecture-page-id}}` — Confluence page ID of the Target Architecture document
  - `{{confluence-solution-architecture-pageid}}` — Confluence page ID of the Solution Architecture document
  - `{{github-test-strategy-template-folder-location}}` — GitHub folder location of the Test Strategy template
  - `{{github-test-strategy-template-repo}}` — GitHub repository containing the template
  - `{{github-test-strategy-template-branch}}` — GitHub branch containing the template
- **Optional runtime parameters:**
  - `{{confluence-prd-page_id}}` — Confluence page ID of the PRD

## Output
- **Type:** `test_strategy`
- **Artifact:** `test-strategy.md` written to blob storage (`folder_name = <workflow_execution_id>`), returned in `content.artifact` (never inline in JSON).
- **Metadata:** `input_summary` (`project_name`, `prd_provided`, `target_architecture`, `solution_architecture`), `pending_decisions_open` (`PEND-nn`), and `workflow_execution_id` / `execution_id`.
- **Summary:** Concise `execution_summary` (max 30 words) covering tiers defined, obligations count, open `PEND-*` count, `gate_ready`, tool outcomes, and critical gaps.

## Composition
```text
agents/L0-testing-strategy-achitect/
├── spec.yaml
└── README.md
prompts/L0-testing-strategy-architect/
└── instructions.md
```
