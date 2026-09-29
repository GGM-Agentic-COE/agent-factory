# L1-Testing-Strategy-Composer — Design Document

## 1. Goal

Build an agentic composer that ingests project artifacts — business requirements (Jira Epics, Stories, Acceptance Criteria), High-Level Design (HLD), Low-Level Design (LLD), and supporting context — and produces a **fully populated Test Strategy document**. The output conforms to the `L1-testing-strategy-template.md`, is published to a Confluence page, and serves as the primary input for the downstream Test Plan, Test Scenarios, and Test Cases pipeline.

---

## 2. Pipeline Context

The L1-Testing-Strategy-Composer is the **first agent** in a three-stage test authoring pipeline:

```
┌──────────────────────────────────┐
│  L1-Testing-Strategy-Composer    │  ◄── THIS AGENT
│  (Produces: Test Strategy)       │
└──────────────┬───────────────────┘
               │
               ▼
┌──────────────────────────────────┐
│  L1-Testing-Plan-Composer        │
│  (Produces: Test Plan)           │
└──────────────┬───────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
┌──────────────┐ ┌──────────────┐
│ L1-Test-     │ │ L1-Test-     │
│ Scenario-    │ │ Case-Writer  │
│ Writer       │ │              │
└──────────────┘ └──────────────┘
```

**Upstream sources:** User input, Jira API, upstream design agents (HLD/LLD generators), impact assessment agent.  
**Downstream consumer:** L1-Testing-Plan-Composer (consumes the full strategy document + structured metadata).

---

## 3. Input Specification

Inputs are grouped into three tiers based on their impact on output quality.

### 3.1 Required Inputs

The agent **must halt** with `INSUFFICIENT_CONTEXT` if any of these are missing.

| # | Input Name | Format | Description |
|---|-----------|--------|-------------|
| 1 | **Project / Epic Context** | Text | Project name, business goals, release timeline, key stakeholders. |
| 2 | **Jira Epics & Stories** | JSON / Structured Markdown | Epic keys, story summaries, acceptance criteria (ACs), priority, labels. Minimum: 1 epic with ≥1 story. |
| 3 | **HLD (High-Level Design)** | Markdown / PDF | Architectural overview, component/microservice list, service boundaries, integration points, external dependencies, tech stack summary. |
| 4 | **LLD (Low-Level Design)** | Markdown / PDF | Database schemas, API contracts, message queue configs, caching strategies, service-level implementation details. |

### 3.2 Recommended Inputs

Sections that depend on these will be populated with `[TO BE CONFIRMED]` markers if absent.

| # | Input Name | Format | Description |
|---|-----------|--------|-------------|
| 5 | **Impact Assessment** | Markdown | Component blast radii, dependency graph, integration landscape, data model impact. |
| 6 | **Environment Inventory** | JSON / Text | Available environments (Dev, QA, UAT, Pre-Prod), infra constraints, access details. |
| 7 | **CI/CD Pipeline Configuration** | YAML / Text | Build tool, pipeline stages, deployment strategy, existing test hooks. |

### 3.3 Optional Inputs

Standard defaults are applied if absent.

| # | Input Name | Format | Description |
|---|-----------|--------|-------------|
| 8 | **Non-Functional Requirements** | Text | Performance targets (SLAs, latency), security requirements, accessibility standards. |
| 9 | **Existing Test Automation Inventory** | Text | Current frameworks, coverage %, reusable test suites. |
| 10 | **Org-level Defect Policy** | Text | Standard severity/priority matrix, SLA for bug-fix turnaround, defect tracking tool. |
| 11 | **Risk Register** | Text / JSON | Pre-identified business and technical risks with likelihood/impact ratings. |
| 12 | **Confluence Target Config** | JSON | `{ space_key, parent_page_id, page_title, publish_as_draft }` |

---

## 4. Processing Pipeline

### Phase 1 — Input Validation

| Step | Action | Detail |
|------|--------|--------|
| 1 | **Validate required inputs** | Check all 4 required inputs are present and parseable. Halt if any are missing. |
| 2 | **Parse & normalise formats** | Convert all inputs into a normalised internal representation. |
| 3 | **Extract structured data from HLD/LLD** | Pull out component lists, API endpoints, database technologies, integration points, and dependency chains. |

### Phase 2 — Analysis & Synthesis

| Step | Action | Detail |
|------|--------|--------|
| 4 | **Requirements analysis** | Extract every acceptance criterion from Jira stories. Classify each AC by testability (UI / API / Unit / Manual). Rank features by business criticality. |
| 5 | **Architecture analysis** | From HLD: components, service boundaries, integration points, external dependencies. From LLD: database tech, API specs, queues, caching. Determine how architecture dictates testing approach. Enrich with impact assessment if provided. |
| 6 | **Scope derivation** | Define in-scope modules, APIs, and user journeys. Define out-of-scope areas with justifications. |
| 7 | **Risk synthesis** | Aggregate risks from requirements, architecture, impact assessment, and risk register. Assign likelihood/impact ratings and produce mitigation plans. |

### Phase 3 — Composition

| Step | Action | Detail |
|------|--------|--------|
| 8 | **Populate template sections** | Fill each of the 10 template sections with project-specific content. Mark sections `[TO BE CONFIRMED]` where input was insufficient. |
| 9 | **Cross-reference consistency** | Verify components in §3 appear in §4 scope; testing types in §5 align with risks in §9; tooling in §7 matches tech stack in §3. |

### Phase 4 — Output & Publish

| Step | Action | Detail |
|------|--------|--------|
| 10 | **Self-evaluate** | Validate all 10 sections are populated. Assess overall confidence score based on input coverage. |
| 11 | **Format for Confluence** | Render as Confluence-compatible markdown with proper heading hierarchy and tables. |
| 12 | **Publish** | Push to Confluence. Return structured output with page URL and metadata. |

---

## 5. Output Specification

The agent produces two outputs:

### 5.1 Test Strategy Document (Confluence Page)

The document follows the exact structure of the `L1-testing-strategy-template.md`:

```
# Test Strategy: <Project/Epic Name>

## 1. Executive Summary & Objective
   - Purpose
   - Context

## 2. Business Requirements & Features
   - Target Epics & Stories
   - Acceptance Criteria Mapping
   - Business Criticality

## 3. System Architecture Context (HLD & LLD Integration)
   - Architectural Overview (HLD)
   - Technical Details (LLD)
   - Testing Impact

## 4. Scope of Testing
   - In-Scope Areas
   - Out-of-Scope Areas

## 5. Testing Approach & Methodologies
   - Testing Levels (Unit, Integration, System/E2E)
   - Testing Types (Functional, Performance, Security, etc.)
   - Shift-Left Integration

## 6. Test Environment & Infrastructure Strategy
   - Environment Architecture
   - Mocking & Stubbing
   - Test Data Management

## 7. Automation Strategy
   - Automation Layers (Testing Pyramid)
   - Tooling Selection
   - CI/CD Integration

## 8. Defect Management & Metrics
   - Defect Lifecycle
   - Severity/Priority Definitions

## 9. Risks & Mitigations
   - Business Risks
   - Architectural Risks
   - Mitigation Plans

## 10. Quality Gates (Entry & Exit Criteria)
   - Entry Criteria
   - Exit Criteria
```

**Rules for populating the template:**
- Every `[placeholder]` is replaced with concrete, project-specific content
- Sections with insufficient input are marked: `> [TO BE CONFIRMED] — This section requires additional input: <what is missing>`
- Every claim traces back to a specific input (epic key, HLD section, LLD detail, or risk)
- No generic boilerplate — every section must reflect this specific project

### 5.2 Structured Agent Output (JSON)

```json
{
  "agent_id": "L1-testing-strategy-composer",
  "agent_version": "1.0.0",
  "execution_id": "exec-<uuid>",
  "input_summary": {
    "source": "agent_output | direct_input",
    "source_agent_id": "<upstream-agent-id> | null",
    "parameters": {
      "project_name": "<name>",
      "epic_keys": ["EPIC-1", "EPIC-2"],
      "hld_provided": true,
      "lld_provided": true,
      "impact_assessment_provided": true,
      "environment_inventory_provided": false,
      "nfr_provided": false
    }
  },
  "output": {
    "type": "test_strategy",
    "schema_version": "1.0",
    "items": [
      {
        "id": "item-001",
        "title": "Test Strategy — <Project Name>",
        "content": {
          "document_markdown": "<full test strategy document>",
          "confluence_page_url": "<url if published>",
          "confluence_page_id": "<page id if published>"
        },
        "tags": ["test-strategy", "<project-key>"],
        "metadata": {
          "confidence": 0.85,
          "sections_confirmed": ["S1", "S2", "S3", "S4", "S5"],
          "sections_to_be_confirmed": ["S6", "S7"],
          "input_coverage": {
            "required": "4/4",
            "recommended": "1/3",
            "optional": "0/4"
          },
          "trajectory": [
            {"step": 1, "action": "validate", "detail": "Validated 4/4 required inputs"},
            {"step": 2, "action": "analyse", "detail": "Extracted 23 ACs from 8 stories"},
            {"step": 3, "action": "compose", "detail": "Populated 10/10 template sections"},
            {"step": 4, "action": "publish", "detail": "Published to Confluence"}
          ]
        }
      }
    ]
  }
}
```

---

## 6. Section-to-Input Traceability Matrix

This matrix shows which inputs feed each template section, and what happens when an input is missing.

| Template Section | Required Input(s) | Recommended Input(s) | Optional Input(s) | Fallback if Missing |
|-----------------|-------------------|----------------------|-------------------|-------------------|
| §1 Executive Summary | Project Context | — | — | **Cannot proceed** — required |
| §2 Business Requirements | Jira Epics & Stories | — | — | **Cannot proceed** — required |
| §3 Architecture Context | HLD, LLD | Impact Assessment | — | **Cannot proceed** without HLD/LLD; Impact Assessment enriches Testing Impact sub-section |
| §4 Scope of Testing | Jira Epics & Stories, HLD | Impact Assessment | — | Derive from requirements + HLD only; miss out-of-scope justifications from impact assessment |
| §5 Testing Approach | HLD, LLD | — | NFRs | Infer testing types from architecture; mark NFR-driven types (Performance, Security, Accessibility) as `[TO BE CONFIRMED]` |
| §6 Environment Strategy | — | Environment Inventory | — | Produce generic recommendation, mark entire section `[TO BE CONFIRMED]` |
| §7 Automation Strategy | LLD (tech stack) | CI/CD Config | Existing Automation Inventory | Recommend tooling based on tech stack; mark CI/CD integration as `[TO BE CONFIRMED]` |
| §8 Defect Management | — | — | Org-level Defect Policy | Apply standard severity/priority definitions |
| §9 Risks & Mitigations | HLD, LLD | Impact Assessment | Risk Register | Derive risks from architecture only; miss blast-radius analysis and pre-identified risks |
| §10 Quality Gates | Jira Epics & Stories | — | — | Apply standard entry/exit criteria tailored to the project |

---

## 7. Downstream Contract

The Test Strategy output serves as the **primary input** for the L1-Testing-Plan-Composer:

| Strategy Section | Used by Plan Composer For |
|-----------------|--------------------------|
| §2 Business Requirements | Test plan scope and feature-level breakdowns |
| §3 Architecture Context | Integration test plans and environment needs |
| §4 Scope of Testing | Filtering what gets planned vs excluded |
| §5 Testing Approach | Structuring the plan by testing level and type |
| §7 Automation Strategy | Assigning manual vs automated execution |
| §9 Risks & Mitigations | Prioritising high-risk areas for deeper coverage |
| §10 Quality Gates | Milestones and checkpoints in the plan |
| `metadata.sections_to_be_confirmed` | Gaps the plan must account for or escalate |

---

## 7. Open Questions

| # | Question | Impact |
|---|---------|--------|
| 1 | **Confluence publishing method** — REST API (XHTML) or markdown converter? | Affects output markup syntax. |
| 2 | **Confluence space & parent page** — Auto-resolve from project key, or supplied as input? | Affects whether Input #12 is required or optional. |
| 3 | **Approval workflow** — Publish as draft or directly as published page? | Affects publish step behaviour. |
| 4 | **Versioning** — New page version or sibling page on re-run? | Affects idempotency. |
| 5 | **Organisational defaults** — Org-wide defaults for Defect Lifecycle, Severity, Quality Gates? | Determines whether Input #10 should be promoted to recommended. |
| 6 | **Knowledge Base access** — Access to org-level KBs for auto-filling §6 and §7? | Determines if agent can populate environment/automation sections without explicit input. |
