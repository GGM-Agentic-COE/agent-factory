# L0-testing-strategy-evaluator

## Purpose
Independently evaluate and safely correct the Programme Increment Test Strategy (`test-strategy.md`) produced by `L0-testing-strategy-architect` against freshly fetched architecture documents, optional PRD, the GitHub evaluation rubric (`evaluation.md`), and the GitHub document template before publishing the final evaluated document to Confluence.

## What does it do?
- **Accepts:** `generator_output` from `L0-testing-strategy-architect` plus `test-strategy.md` read from blob storage under `<workflow_execution_id>`.
- **Fetches independently:** Target Architecture document, Solution Architecture document, and optional PRD from Confluence; `evaluation.md` rubric and Test Strategy document template from GitHub.
- **Evaluates & corrects:** Runs gates `G1`–`G10` in order per `evaluation.md`, re-derives version parity, ID traceability, obligations, thresholds, pack governance, and `PEND-*` coverage, fixes mechanically-recoverable gaps, and escalates ambiguous findings.
- **Publishes:** Unconditionally writes the evaluated `test-strategy.md` verbatim (with applied fixes) to Confluence.

## How does it work?
1. Validates `generator_output` and inherits `workflow_execution_id` (`wf-<uuid>`), generating a fresh `execution_id` (`exec-<uuid>`).
2. Fetches Target Architecture document, Solution Architecture document, optional PRD (Confluence), `evaluation.md` rubric and document template (GitHub), and `test-strategy.md` (blob storage).
3. Verifies mandatory declaration sections (`APP-2`, `DAT-1`, `DAT-3`), Target approval, `satisfies_from` version parity, and `input_summary` consistency.
4. Evaluates gates `G1`–`G10` across all 12 sections + `Appendix A` against `evaluation.md`, scoring 9 dimensions (`0.0–1.0`) and `overall_score` (`0.0–10.0`).
5. Applies permitted mechanical fixes per `evaluation.md`, writes the final `test-strategy.md` to Confluence (`title = 'Test Strategy: ' + <project_name>`, `space_key = {{confluence-test-strategy-space-key}}`), records the literal `confluence_page_url`, and returns `AgentOutput`.

## Input
- **Source:** `generator_output` from `L0-testing-strategy-architect` + `test-strategy.md` from blob storage + Confluence (Target Architecture document, Solution Architecture document, optional PRD) + GitHub (`evaluation.md` rubric and Test Strategy template).
- **Required runtime parameters:**
  - `{{confluence-target-architecture-page-id}}` — Confluence page ID of the Target Architecture document
  - `{{confluence-solution-architecture-pageid}}` — Confluence page ID of the Solution Architecture document
  - `{{confluence-test-strategy-space-key}}` — Confluence space key for publishing the evaluated Test Strategy
  - `{{github-test-strategy-evaluation-folder-location}}` — GitHub folder location of `evaluation.md`
  - `{{github-test-strategy-evaluation-repo}}` — GitHub repository containing `evaluation.md`
  - `{{github-test-strategy-evaluation-branch}}` — GitHub branch containing `evaluation.md`
  - `{{github-test-strategy-template-folder-location}}` — GitHub folder location of the Test Strategy template
  - `{{github-test-strategy-template-repo}}` — GitHub repository containing the template
  - `{{github-test-strategy-template-branch}}` — GitHub branch containing the template
- **Optional runtime parameters:**
  - `{{confluence-prd-page_id}}` — Confluence page ID of the PRD

## Output
- **Type:** `evaluation_result` (`schema_version = 1.0`)
- **Items:** 9 component `scores` (`0.0–1.0`), `overall_score` (`0.0–10.0`), `gates_passed`, `gates_failed`, `findings` (`FND-xx`), `fixes_applied` (`FIX-xx`), `final_decision` (`approved | fixed_and_approved | escalate_to_hitl`), and `confluence_page_url` (literal return from Confluence writer or `null`).
- **Summary:** Concise `execution_summary` (max 30 words) covering `overall_score`, `final_decision`, gates failed, fix count, and Confluence write outcome.

## Composition
```text
agents/L0-testing-strategy-achitect-evaluator/
├── spec.yaml
└── README.md
prompts/L0-testing-strategy-evaluator/
└── instructions.md
```
