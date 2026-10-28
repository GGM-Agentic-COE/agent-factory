# L1-design-hld-generator-agent

## Purpose

Generates a High-Level Design (HLD) from epics and stories — the architectural blueprint that bridges requirements and code. Defines system architecture, components, APIs, data models, integrations, and deployment topology so development teams can implement without ambiguity.

## What does it do?

Takes structured epics (with features) and optionally stories, and produces:
- **System overview** — architecture style, technology stack summary
- **Components** — services, databases, caches, queues, gateways (each tracing to features)
- **API contracts** — endpoints with method, path, request/response schemas, auth
- **Data model** — entities with fields, types, constraints, relationships, store technology
- **Integrations** — external systems, patterns (REST/event/webhook), direction
- **Deployment topology** — container strategy, scaling, infrastructure
- **Architecture Decision Records (ADRs)** — key decisions with rationale and alternatives
- **Cross-cutting concerns** — authentication, logging, monitoring, error handling

## How does it work?

1. Ingests epics with features (and optionally stories for richer detail)
2. Validates input has at least one epic
3. Designs component architecture per epic (what services are needed)
4. Defines API contracts at service boundaries
5. Designs data model (entities, stores, relationships)
6. Maps external integrations
7. Defines deployment topology
8. Documents architecture decisions as ADRs
9. Verifies all choices against enterprise architecture KB
10. Reflects, fixes EA violations, delivers final

## Input

- **Source:** agent_output (from epics/stories generators) or direct_input
- **Required:** `epics` (array) — epics with features
- **Optional:** `stories` (array), `target_epic` (string — HLD for one epic only)
- **Knowledge bases:** kb-L1-enterprise-architecture, kb-L1-golang-api-standards, kb-L1-microservices-architecture

## Output

- **Type:** `hld`
- **Structure:** `items` object with: system_overview, components[], apis[], data_model, integrations[], deployment, architecture_decisions[], cross_cutting
- **IDs:** CMP-XX (components), API-XX (endpoints), DS-XX (data stores), INT-XX (integrations), ADR-XX (decisions)
- **Summary:** Plain-text execution_summary

## Composition

```
L1-design-hld-generator/
├── spec.yaml                 # Agent specification
├── evaluation.md             # Quality rubric and reflection checklist
├── output_schema.json        # JSON Schema for output validation
├── README.md                 # This file
├── examples/                 # Input/output pairs
└── golden/v1.0.0/            # Benchmark responses

prompts/L1-design-hld-generator-agent/
└── instructions.md           # Agent prompt
```
