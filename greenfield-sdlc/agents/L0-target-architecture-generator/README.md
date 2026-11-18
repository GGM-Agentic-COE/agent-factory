# L0-target-architecture-generator

## Purpose

A PRD says what the product must do. The binding principles say what the
enterprise will and will not permit. Neither says how the system is divided
or who owns each fact. This agent produces the target architecture that
bridges them: the last functional statement and the first technical one.
Solution architecture, high-level designs and interface specifications are
written against it and cite its keys, and conformance is assessed against it
at every release. Every boundary is tested by reason-for-change: do these
things change for the same reason, on the same clock, under the same
approval? Effort is never the test.

## What does it do?

Produces `{product_name}-target-architecture.md` (document ID
`{document_code}-ARC-001`) in S3, filling `kb-L0-target-architecture-template`
section by section:
- **Drivers** (`DRV-NN`, Section 2), with actors, external systems
  (unselected ones marked "to be selected" with an `OI-NN`), and a Mermaid
  system-context diagram
- **Principle positions** (Section 3): one row per binding principle,
  verdict unchanged, recorded deviations as `DEV-NN`
- **Decomposition** (Sections 4–6): bounded contexts (core, supporting or
  generic) grouped by reason-for-change (PAT-01), each PRD entity owned by
  exactly one context (PAT-06), experience components with no business rules
  (PAT-11), a single identity authority (PAT-13), and a Mermaid domain view
- **Context map** (Section 5): every interaction is a request (`R-NN`, with
  DEV cover, budget and failure mode) or an event (with a consistency
  bound), plus read models with owner and freshness. Mermaid uses solid
  arrows for requests and dashed arrows for events
- **Components and invariants** (Section 7): `APP-2` with one service per
  context, and `APP-3` with `INV-NN` rules in *shall* form
- **Constraints** (`CON-N`, Section 8): the standing set plus any
  product-specific constraints a PRD obligation demands
- **Demands and quality attributes** (Section 9): `REQ-DAT`, `REQ-INT`,
  `REQ-PLT` and `QA-NN`. Targets come only from the PRD or a KB standard,
  otherwise **Requires validation** with an `OI-NN`
- **Security** (`SEC-N`, Section 10): at least one control per viewpoint
- **Decisions and governance** (Section 11): append-only `ADR-NNN`, change
  control and conformance states
- **Position and open items** (Section 12), plus **Appendix B** (change
  register) when a baseline was supplied

The document selects no technology and names no product, vendor, protocol or
platform; that is `{document_code}-ARC-002`. The output JSON carries only
meta points (keys, names, counts, cross-references, summaries of 150
characters or fewer) and the S3 location.

## How does it work?

1. Inherits `workflow_execution_id` from the binding-principles evaluator and
   generates a fresh `execution_id`
2. Reads the evaluated binding principles from S3 via `tool-L0-s3-files-reader`
   first, then the PRD and KBs from Confluence and the template from GitHub
3. Returns INSUFFICIENT_CONTEXT if the PRD has no keyed FRs, the binding
   principles have no `principles[]`, or the product names don't match
4. Builds a PRD index by meaning and cites every PRD item as `prd:<key>`, so
   PRD keys are never confused with this document's own keys
5. Fills Sections 2–12 per the processing rules: principles mapped, never
   changed; budgets split across synchronous requests (PAT-17) and never
   above the PRD figure; the stricter of PRD and KB applied for
   classification and retention, with an `OI-NN`; availability tier stated
   explicitly per ES4
6. With `existing_target_architecture`, carries unchanged text verbatim, never
   reuses or renumbers keys, marks withdrawn items, adds an ADR per
   structural change, and records every difference in Appendix B
7. Runs a mechanical self-check: all template sections and callouts
   present in the exact blockquote form, every entity owned once, every FR
   traced, every `R-NN` complete, every cited key defined, numbering
   sequential, and summaries not holding document text
8. Writes the markdown to `<workflow_execution_id>/{product_name}-target-architecture.md`
   via `tool-L0-s3-writer` and records the confirmed location

## Input

- **Source:** agent_output from `L0-binding-principles-generator-evaluator`
  (`workflow_execution_id`). The binding principles are read from S3
- **Required:** `workflow_execution_id`: inherited; names the S3 folder
- **Required:** `prd-confluence-page-id` and the three KB page IDs
  (`architecture-patterns-`, `enterprise-architecture-`,
  `enterprise-security-confluence-page-id`)
- **Required:** `target-architecture-template-github-folder-location`,
  `agent-github-repo-name`, `agent-github-repo-branch`: where the template
  lives
- **Optional:** `existing_target_architecture`: the baseline, which turns
  the run into an update with Appendix B
- **Optional:** `reviewer_notes`, `architecture_notes` (external systems,
  reviewer roles, decisions, known open items), `epics_and_features`
  (coverage check only)

## Output

- **Type:** `target-architecture`
- **Items:** `document_id`, `document_version`, `document_status`,
  `drivers[]`, `principle_positions[]`, `deviations[]`,
  `bounded_contexts[]`, `experience_components[]`, `platform_components[]`,
  `relationships[]`, `invariants[]`, `constraints[]`, `demands[]`,
  `quality_attributes[]`, `security_controls[]`, `decisions[]`,
  `open_items[]`, `feature_coverage`, `change_register[]`
- **Artifacts:** `{product_name}-target-architecture.md`, format
  `markdown`, `storage.provider: s3`, location `<bucket>/<key>`. The
  location is null when the write failed
- **Metadata:** `confidence` and `reasoning` on drivers and bounded contexts
- **Summary:** counts per key family, the boundary most likely to be
  challenged, budgets marked "Requires validation", verdicts the
  architecture could not honour, the change register size, the S3 location
  or tool error, KBs, tools, gaps

## Composition

```
agents/L0-target-architecture-generator/
├── spec.yaml
└── README.md

prompts/L0-target-architecture-generator/
└── instructions.md
```

Upstream: `L0-binding-principles-generator-evaluator` (evaluated binding
principles in S3) and the PRD in Confluence.
Downstream: `L0-target-architecture-generator-evaluator`, which reads the
document from the same S3 folder.
