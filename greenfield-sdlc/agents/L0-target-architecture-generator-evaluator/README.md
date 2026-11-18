# L0-target-architecture-generator-evaluator

## Purpose

The target architecture is the last functional statement and the first
technical one. Solution architecture, high-level designs and interface
specifications are written against it and cite its keys. A dangling key, an
entity with two owners, a budget nobody gave or a quietly altered verdict
becomes a defect in every document that follows. This agent is the
independent check (S6) on `L0-target-architecture-generator`. It re-derives
rather than re-reads: it rebuilds the entity-ownership set, the key index and
the budget sources from the inputs, then compares them with the document. It
fixes what can be recovered mechanically, escalates what needs architectural
judgment, and always publishes the document so a human can approve or reject
it where it is published.

## What does it do?

Reads `{product_name}-target-architecture.md` and
`{product_name}-binding-principles.json` from S3 and produces:
- **Items:** `document_id`, `document_version`, `document_status`, `counts`
  per key family, `entity_ownership[]`, `unsourced_budgets_resolved[]`,
  `open_items_added[]`
- **An evaluation block**:
  - `scores`: faithfulness, hallucination, consistency, relevance,
    reasoning quality, citation completeness
  - `overall_score` and `pass`
  - `findings[]`: pass/fail per gate, each naming the document key or
    section and the rule involved
  - `fixes_applied[]`: patches with `key`, before/after excerpts (150
    characters or fewer) and reasoning
  - `final_decision`: `approved`, `fixed_and_approved` or
    `escalate_to_hitl`
- **The published document**: the corrected markdown, status **Draft**,
  published verbatim to Confluence with no banner or verdict added. The
  verdict and findings live only in this agent's output

## How does it work?

1. Inherits `workflow_execution_id` from the generator's output and
   generates a fresh `execution_id`
2. Reads both documents from S3 in one `tool-L0-s3-files-reader` call (exact
   paths, never lists the folder), the PRD and KBs from Confluence, and the
   template and its own `evaluation.md` from GitHub
3. Returns INSUFFICIENT_CONTEXT if the document is empty or isn't a filled
   template, or the binding principles have no `principles[]`
4. **Template conformance:** checks every section, heading, callout, table
   and column, and the exact callout blockquote form (`> **TITLE**`, a bare
   `>` line, then `> ` body lines)
5. **Key integrity:** rebuilds the defined-key and cited-key sets and checks
   for dangling citations, duplicates, numbering gaps and renumbering
6. **Entity ownership:** each PRD entity is owned by exactly one context
   (PAT-06)
7. **Requirement coverage:** every FR is cited by a capability, every
   `prd:` citation exists and supports its statement, and every conditional
   requirement has an `OI-NN`
8. **Principle positions:** Section 3 matches the input verdicts, and each
   `DEV-NN` copies its input deviation
9. **Context map:** each `R-NN` has a DEV cover, a sourced budget and a
   failure mode; each event has a consistency bound; each read model has an
   owner and freshness. Arrow styles must match the kind, with no
   unregistered cross-context reads (RULE-02)
10. **Budgets:** every numeric target traces to the PRD or a KB standard,
    otherwise it becomes "Requires validation" with an `OI-NN`. PAT-17
    budget splits must not exceed the PRD figure. Classification, retention
    and tier are checked against ES2–ES4
11. **Mandatory content** (standing `CON`, `SEC` per viewpoint, one service
    per context, complete `INV`, one `ADR` per structural decision) and
    **technology neutrality** (including Mermaid figures and tables)
12. **Baseline fidelity** (when supplied): unchanged text is verbatim and
    every difference has one Appendix B row
13. Applies every fix to the in-memory document and `items` together,
    scores, and decides `final_decision`
14. Always publishes the corrected document via `tool-L0-confluence-writer`
    to the configured space, titled `{product_name}-target-architecture`,
    whatever the decision. Only a failed read leaves nothing to publish

## Input

- **Source:** agent_output from `L0-target-architecture-generator`
  (`workflow_execution_id`). Both documents come from S3
- **Required:** `workflow_execution_id`: inherited; names the S3 folder
- **Required:** `prd-confluence-page-id` and the three KB page IDs
  (`architecture-patterns-`, `enterprise-architecture-`,
  `enterprise-security-confluence-page-id`)
- **Required:** `target-architecture-template-github-folder-location`,
  `target-architecture-eval-github-folder-loc`, `agent-github-repo-name`,
  `agent-github-repo-branch`: where the template and evaluation file live
- **Required:** `target-architecture-confluence-upload-space-key`: the
  Confluence space to publish to
- **Optional:** `existing_target_architecture` (baseline),
  `reviewer_notes`, `architecture_notes`, `epics_and_features`

## Output

- **Type:** `target-architecture-evaluation`
- **Items:** `document_id`, `document_version`, `document_status`,
  `counts`, `entity_ownership[]`, `unsourced_budgets_resolved[]`,
  `open_items_added[]`
- **Evaluation:** `scores`, `overall_score`, `pass`, `findings[]`,
  `fixes_applied[]`, `final_decision`
- **Artifacts:** `{product_name}-target-architecture.md`,
  `storage.provider: confluence`, with `item_id` and `web_url` as returned
  by the tool (null when the write failed) and `source_blob` set to the S3
  path read
- **Summary:** score and decision; results for template conformance, key
  integrity, entity ownership and requirement coverage; findings on
  principle positions, budget sources and technology neutrality; baseline
  fidelity; what was patched; the published page or tool error; what the
  reviewer must decide; KBs, tools and guardrails; gaps

## Composition

```
agents/L0-target-architecture-generator-evaluator/
├── evaluation.md
├── spec.yaml
└── README.md

prompts/L0-target-architecture-generator-evaluator/
└── instructions.md
```

Upstream: `L0-target-architecture-generator`.
Downstream: human approval of the published Confluence page, then solution
architecture (`{document_code}-ARC-002`), HLDs and interface specifications,
which cite its keys.
