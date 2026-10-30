# L1-architecture-hld-designer

## Purpose

Architecture for a module is usually written as separate views — a PRD, a platform view, a data view and an integration view — and none of them says plainly what is *real right now* versus what is mocked, simplified or still only designed. This agent merges those four inputs into a single High-Level Design (`hld.md`) where every section carries the **target enterprise architecture** and the **current build reality** side by side, and a consolidated Gap Register is the single source of truth for what is not yet real.

## What does it do?

It accepts:
- `prd.md` — features (F-XX.X), roles, user flows, NFRs, MVP/cycle scope
- `platform-architecture.md` — runtime, ingress, deployment, auth, observability
- `data-architecture.md` — datastores, entity lifecycle, caching, encryption
- `integration-architecture.md` — external systems, connectors, events

It produces:
- **`hld.md`** (the artifact, published to Confluence) with the fixed structure:
  header · §0 Revision note · §1 System Component Diagram · §2 Data Flow Diagrams · §3 State Machine · §4 Deployment View (target + MVP) · §5 Security View (flow, encryption boundaries, authorization matrix) · §6 Observability · §7 NFR Compliance Summary · §8 Gap Register.
  All diagrams are plain ASCII in code blocks — no Mermaid, readable anywhere.
- **Meta-point items** for downstream reconciliation: components with realization state, flows, state machine, deployment, security/authz rules, observability signals, NFR status, binding-principle checks, gaps, open questions.

## How does it work?

1. Validates that all four documents are present and substantive; otherwise returns `INSUFFICIENT_CONTEXT` without publishing.
2. **Phase 1:** extracts the relevant EA-xx references from `kb-L1-enterprise-architecture` and every ABP-xx principle from `kb-L1-architectural-binding-principles`.
3. **Phase 2:** derives scope, components (with `real | mocked | simplified | deferred | absent | unconfirmed`), flows, lifecycle, deployment, security, observability and NFR status.
4. Checks every binding principle; deviations become gaps.
5. Records any conflict between inputs as an open question (PRD governs business rules; EA KB governs technology).
6. Fills the embedded HLD template and publishes it with `tool-L1-confluence-create-page` under a page keyed by `workflow_execution_id`.
7. Runs a light mechanical self-check (sections, placeholders, IDs, summaries) and appends a plain-text execution summary.

## Input

- **Source:** agent output, direct input, or file upload (`.md`, `.txt`)
- **Required:** `prd`, `platform_architecture`, `data_architecture`, `integration_architecture` — full document text
- **Optional:** `document_version` (default `1.0.0`), `previous_hld` (drives §0), `confluence_space_key` (default `ARCH`), `confluence_parent_page_id`

## Output

- **Type:** `hld`
- **Items:** `document_header`, `components`, `data_flows`, `state_machine`, `deployment`, `security`, `observability`, `nfr_compliance`, `binding_principle_checks`, `gaps`, `open_questions` — summaries capped by `maxLength`; IDs, enums, citations and cross-references kept complete
- **Artifacts:** one `hld.md` document, `storage.provider: "confluence"`, location `confluence://{space}/{workflow_execution_id}/hld.md`
- **Metadata:** confidence + reasoning on every item; citation on components, flows, NFRs, principle checks, gaps
- **Summary:** counts, key decisions, reflection fixes, KBs used, guardrails, tool outcome, flagged issues

## Design notes

- **Name vs. naming standard.** The standard pattern is `L1-{phase}-{function}` with phase ∈ inception | design | construction | testing | deployment. The requested name `L1-architecture-hld-designer` is kept as specified; `metadata.phase` is set to `design`. The standard-conformant name would be `L1-design-hld-designer`.
- **Write tool on a Core agent.** The standard places write/publish tools on a separate Utility agent. `tool-L1-confluence-create-page` is attached here as requested and used only as the artifact save step (Key Pattern 19). To align with the Core/Utility split later, move it to a `L1-…-confluence-publisher` utility and switch `storage.provider` to `s3`.
- **Guardrails.** None were specified; the mandatory set for content generators with tool access was applied.
- **Prompt length.** `instructions.md` is ~170 lines (budget 150) because the HLD template is embedded literally (S4) with no template KB; flagged rather than cut.

## Composition

```
agents/L1-architecture-hld-designer/
├── spec.yaml
├── evaluation.md
├── output_schema.json
├── README.md
├── examples/
│   ├── input-01-reporting-service.json
│   ├── output-01-reporting-service.json
│   ├── input-02-missing-prd.json
│   └── output-02-missing-prd.json
└── golden/v1.0.0/
    ├── input-golden-01-clinicflow-appointments.json
    ├── golden-01-clinicflow-appointments.json
    ├── golden-01-clinicflow-appointments-hld.md
    ├── input-golden-02-incomplete-architecture.json
    └── golden-02-incomplete-architecture.json

prompts/L1-architecture-hld-designer/
└── instructions.md
```
