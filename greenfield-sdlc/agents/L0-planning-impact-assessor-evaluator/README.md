# L0-impact-assessor-evaluator

## Purpose
Sole quality gate between `L0-impact-assessor` and `L0-backlog-prioritizer`. The generator only runs a light self-check; this agent independently re-derives every impact finding and every graph result (DFS cycle check, longest-path critical path, mermaid 1:1) from freshly-fetched source data, fixes what the data mechanically supports, escalates what it doesn't, and is the only agent that persists the final impact-assessment document.

## What does it do?
- **Accepts:** `generator_output` + `original_input` from the impact assessor; fresh `service_catalog` and `cmdb_export`.
- **Fetches:** generator rubric `evaluation.md` (GitHub), `kb-L1-architecture-principles` (Confluence page 524091393).
- **Produces:**
  - `items.scores`, `overall_score`, `pass`
  - `items.findings[]` — one per gate, each citing an id and showing re-derived results
  - `items.fixes_applied[]` — before/after with reasoning
  - `items.final_decision` — approved | fixed_and_approved | escalate_to_hitl
  - `artifacts[0]` — evaluated `<product>-impact-assessment.md` with `storage.location` = literal Confluence URL
  - `execution_summary` — plain-text bullets incl. the persisted URL

## How does it work?
1. Validate input (missing generator_output → INSUFFICIENT_CONTEXT; legitimate upstream failure → approve as-is).
2. Fetch rubric and KB.
3. Re-run capability check (fresh catalog) and technical impact check (fresh CMDB relationships + KB); flag freshness/contamination.
4. Check FR coverage, grounding and node-id uniqueness.
5. Re-run DFS cycle check; if PASS, longest-path with all ties; check edge directions against prerequisite language.
6. Verify mermaid (counts, directions, shapes, styles, annotations) and distillation limits.
7. Fix mechanically-recoverable gaps in JSON items and the document; escalate ambiguity.
8. Decide; write the evaluated document to Confluence unconditionally; record the returned URL.

## Input
- **Source:** agent_output
- **Required:** `generator_output`, `original_input`, `service_catalog`, `cmdb_export`
- **Optional:** `space_key` — Confluence space (blank in instructions; set at deployment)

## Output
- **Type:** `evaluation_result`
- **Items:** scores, overall_score, pass, findings, fixes_applied, final_decision
- **Metadata:** agent_id, version, new execution_id, inherited workflow_execution_id
- **Summary:** decision, re-derivation results, mismatches, mermaid check, KBs, tools, guardrails, gaps, Confluence URL

## Composition
```
agents/L0-impact-assessor-evaluator/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-clean-approved.json            output-01-clean-approved.json
│   ├── input-02-cmdb-mismatch-fixed.json       output-02-cmdb-mismatch-fixed.json
│   ├── input-03-ambiguous-cycle-hitl.json      output-03-ambiguous-cycle-hitl.json
│   └── input-04-stale-export-hitl.json         output-04-stale-export-hitl.json
└── golden/v1.0.0/
    ├── input-golden-01-fixable-cycle.json      golden-01-fixable-cycle.json
    └── input-golden-02-missing-generator-output.json  golden-02-missing-generator-output.json
prompts/L0-impact-assessor-evaluator/
└── instructions.md
```
> Example inputs carry a `_test_harness_tool_returns` block simulating tool responses (KB excerpt, rubric fetch, Confluence URL) so outputs are reproducible. It is not part of the runtime contract.
