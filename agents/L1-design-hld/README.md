# L1-design-hld

## v2.0.0 — single-document input

This version supersedes the original four-structured-input design. Instead of requiring `L1-inception-requirements-elicitor`, `L1-inception-nfr-classifier`, `L1-design-dependency-mapper`, and `L1-design-api-spec-generator` to have already run, this agent now takes **one Requirements.md document** — a PRD, requirements spec, or impact assessment — and does its own extraction of FRs, NFR-relevant language, dependencies, and integration signals.

## Purpose

A single requirements document is rarely structured the way four separate upstream agents would have produced it — functional requirements might be tagged `FR-{seq}` or might just be prose; NFRs are almost always prose (an "SLA Impact" paragraph, a "Regulatory Boundaries" section) rather than a tagged list; dependencies might come from a CMDB-style impact table or a mermaid diagram embedded in the doc. This agent reads all of that itself and produces the same High-Level Design output as before: components grouped by cohesion, every NFR mapped to an approach, integrations and data flows derived from what the document actually says — with full traceability back to specific headings/rows/ids in the source document.

## What does it do?

Accepts:
- `requirements_document` — the full text of Requirements.md

Produces:
- A component list, grouped by cohesion, each typed and traced to the requirements/NFRs it satisfies (structured items)
- An integration list (protocol-classified — explicitly stated where the document names one, otherwise inferred and flagged as an assumption) and a data-flow list (PII-flagged)
- An NFR-to-design mapping — which component(s) and mechanism address each NFR-relevant statement found in the document
- A rendered `hld.md` with C4 Context and Container diagrams (Mermaid), full component/NFR rationale, and a Gaps section
- A gap list for any requirement or NFR-relevant statement that couldn't be mapped — including genuine contradictions found within the source document itself (see golden-01, where the HarvestLink assessment states two different availability targets for the same FR)

## How does it work?

1. Ingest `requirements_document` via the INPUT PROTOCOL (direct input / file upload / attached reader tool — never RAG/semantic search, since this is a raw document, not a KB artifact).
2. Extract FRs (explicit `FR-{seq}` tags if present, else assigned sequentially from distinct capability statements) and NFR-relevant statements (assigned `NFR-{seq}`, classified by category, confidence reduced for statements with no measurable target).
3. Group requirements into components by shared data/responsibility — a well-formed HLD has fewer components than requirements, not a 1:1 mapping.
4. Map each NFR to the component(s) and architectural approach that address it; anything with no plausible component, no measurable target, or a genuine contradiction in the source becomes a gap instead of a guess.
5. Derive integrations from any named existing-system/dependency signal in the document; classify protocol from an explicitly named endpoint when one exists, otherwise infer it and say so in the integration's summary.
6. Derive data flows for anything moving customer/user data, flagging PII based on the data description and any compliance-related NFR language.
7. Render the C4 diagrams and `hld.md`.
8. Run a basic self-check (completeness, ID validity in document order, no ungrounded components) plus a conformance check against `kb-L1-enterprise-architecture` before delivery.

## Input

- **Source:** direct input, file upload (`.md`/`.txt`), or an attached blob-storage reader tool (retrieval only, never semantic search)
- **Required:** `requirements_document` — full text of Requirements.md
- **Optional:** `system_name` — used in C4 diagram titles; inferred from the document title if omitted

## Output

- **Type:** `high_level_design`
- **Items:** `components[]`, `integrations[]`, `data_flows[]`, `nfr_mappings[]`, `gaps[]`
- **Artifact:** `hld.md` — C4 Context/Container diagrams, component/NFR detail, full rationale
- **Metadata:** confidence and citation (always `Requirements.md` + a specific heading/row/id) on every item
- **Summary:** plain-text execution_summary covering counts, grouping/NFR decisions, inferred-vs-stated protocol calls, KB/guardrails used, and gaps

## Composition

```
agents/L1-design-hld/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-happy-path.json       # synthetic notification-system Requirements.md
│   ├── output-01-happy-path.json
│   ├── input-02-edge-case.json        # one requirement + one NFR with no integration/target detail
│   └── output-02-edge-case.json
└── golden/v1.0.0/
    ├── input-golden-01-happy-path.json   # the REAL HarvestLink impact assessment, verbatim
    ├── golden-01-happy-path.json         # 12 components, 21 integrations, includes a caught source-document contradiction
    ├── input-golden-02-edge-case.json    # a placeholder doc with no identifiable requirements
    └── golden-02-edge-case.json          # INSUFFICIENT_CONTEXT / rejected

prompts/L1-design-hld/
└── instructions.md
```

## Note on prompt length

`instructions.md` is ~167 lines, over the skill's 150-line guideline by more than the usual small S4 template-embedding allowance. This reflects genuinely new extraction logic (document-order id assignment, tagged-vs-untagged FR/NFR handling, inferred-vs-stated protocol flagging) on top of the embedded hld.md template, not padding — trimmed once already; further cuts would lose real instruction content.

## Knowledge base

References `kb-L1-enterprise-architecture` (not yet created in this workspace) for component-type taxonomy, integration-pattern standards, and diagramming/naming conventions — attached at runtime, not duplicated in the prompt. Same open item as before — let me know if you'd like this KB built out.
