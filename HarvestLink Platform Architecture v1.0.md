# HarvestLink Marketplace — Platform Architecture

## 1. Document Control

**Document:** Platform Architecture  
**Project:** HarvestLink Marketplace  
**Version:** 1.0  
**Lifecycle Stage:** Cycle 0  
**Status:** Approved  
**Owner:** Platform Architect  
**Canonical Location:** `/architecture/platform-architecture.md`  
**Parent:** `foundational-solution-architecture.md`

---

## 2. Purpose and Scope

This document defines the platform capabilities on which HarvestLink runs.

It translates Foundational Architecture platform demands into concrete technology and operational capabilities.

Unlike the Foundational Solution Architecture, this document may name technologies and managed services.

It defines:

- compute/runtime
- relational persistence capability
- event infrastructure
- object storage
- networking
- environments
- deployment
- security capabilities
- observability
- scalability and resilience
- the platform capability register used by future Impact Assessments

Detailed Terraform resource definitions remain in the platform repository.

---

## 3. Inputs

- PRD and NFRs
- Regulatory posture
- Binding architecture principles
- Foundational Solution Architecture
- `REQ-PLT-*`
- `CON-*`
- Data Architecture
- Integration Architecture
- Initial roadmap/features
- Enterprise approved-technology catalogue

---

## 4. Principles Applied

### PRIN-04 — Capability-Aligned Deployability

Each bounded context must be independently deployable.

### PRIN-06 — Security and Privacy Designed In

Platform capabilities must support:

- encrypted storage
- attributable access
- identity/trust boundaries
- secret isolation

### PRIN-07 — Prefer Strategically Approved Platforms and Managed Services

Technology choices must first use approved enterprise capabilities where they satisfy the required architecture demand.

A product in `contain` or `retire` lifecycle status may not be selected without an exception.

---

# PLT-1 — Runtime Architecture

## Backend Workloads

Technology:

```text
Spring Boot
```

Deployment:

```text
AWS ECS
```

Initial workload mapping:

```text
Catalogue Service
Orders Service
Billing Service
Identity Service
Notifications Service
```

Each service is independently deployable.

---

## Front-End Workloads

Technology:

```text
React SPA
```

Applications:

```text
Buyer SPA

Producer SPA
```

Hosting/CDN realization is supplied by the approved platform service selected for static web delivery.

---

# PLT-2 — High-Level Platform Topology

```text
                    Users
                      │
             ┌────────┴────────┐
             ▼                 ▼
         Buyer SPA        Producer SPA
             │                 │
             └────────┬────────┘
                      ▼
              Application/API Layer
                      │
       ┌──────────────┼──────────────┐
       ▼              ▼              ▼
   Catalogue         Orders        Billing
       │              │              │
       ▼              ▼              ▼
   PostgreSQL      PostgreSQL      PostgreSQL

               Async workloads
                      │
                      ▼
                    Kafka
                      │
             ┌────────┴────────┐
             ▼                 ▼
          Billing        Notifications


Identity
   └── upstream authentication / identity capability
```

---

# PLT-3 — Persistence Platform

## Relational Capability

Technology:

```text
PostgreSQL
```

Capability status:

```text
AVAILABLE
```

Architecture realization:

```text
Catalogue → own PostgreSQL schema

Orders → own PostgreSQL schema

Billing → own PostgreSQL schema

Identity → own PostgreSQL schema
```

Platform provisioning does not create cross-context data ownership.

---

## Access Boundary

Credentials/grants must enforce:

```text
Catalogue credential
→ Catalogue persistence only

Orders credential
→ Orders persistence only

Billing credential
→ Billing persistence only
```

The platform shall prevent normal application credentials from reading another context's schema directly.

---

# PLT-4 — Messaging Platform

Technology:

```text
Kafka
```

Capability status:

```text
AVAILABLE
```

Purpose:

```text
domain/event-driven integration
```

Integration Architecture owns:

- topic naming
- contract rules
- producer/consumer semantics

Platform Architecture owns:

- Kafka runtime
- availability
- networking
- authentication
- capacity
- monitoring

---

# PLT-5 — Object Storage

Capability:

```text
Object Storage
```

HarvestLink use case:

```text
Listing images
```

Capability status:

```text
AVAILABLE
```

The application retains metadata/reference while the platform stores binary objects.

---

# PLT-6 — Capability Register

This register is checked by every later feature Impact Assessment.

| Capability | Realization | Status | Consumer/Reason |
|---|---|---|---|
| HTTP service hosting | AWS ECS | AVAILABLE | Backend services |
| Relational persistence | PostgreSQL | AVAILABLE | Domain persistence |
| Event bus | Kafka | AVAILABLE | Async integrations |
| Object storage | Approved object store | AVAILABLE | Listing images |
| Identity capability | Identity context/platform integration | AVAILABLE/Planned | All authenticated flows |
| Scheduled jobs | Not selected | NOT PRESENT | No current requirement |
| Search index | Not selected | NOT PRESENT | No Cycle 0 requirement |
| Analytical store | Not selected | NOT PRESENT | DAT-4 is pending |

`AVAILABLE` means technically provisioned and consumable.

It does not mean merely "we know which product we might use."

---

# PLT-7 — Capability Gap Rule

For every committed feature:

```text
Feature Requirement
        │
        ▼
Required Platform Capability
        │
        ▼
Check PLT-6
```

If:

```text
AVAILABLE
```

then:

```text
PLT viewpoint = NONE
```

provided no configuration/topology change is needed.

If:

```text
NOT PRESENT
```

then:

```text
PLT DELTA REQUIRED
```

---

## Example — Cycle 1 Producer Listing

Feature needs:

```text
HTTP hosting
PostgreSQL
Object storage
```

PLT-6 says:

```text
HTTP             AVAILABLE
PostgreSQL       AVAILABLE
Object storage   AVAILABLE
```

Therefore:

```text
PLT = NONE
```

No new platform capability is needed.

---

## Example — Cycle 2 Buyer Search

Feature needs:

```text
category browse
full-text search
```

Capability check:

```text
PostgreSQL
AVAILABLE

Search Index
NOT PRESENT
```

Therefore:

```text
Platform delta required
```

The selected approved implementation may then be:

```text
Elasticsearch / approved managed search capability
```

After provisioning and successful delivery:

```text
PLT-6

Search Index
NOT PRESENT → AVAILABLE
```

---

# PLT-8 — Network Architecture

High-level principles:

```text
Public ingress
      │
      ▼
Application endpoints
      │
      ▼
Private application network
      │
      ├── PostgreSQL
      ├── Kafka
      └── Object storage/private service access
```

Internal data and messaging capabilities must not be unnecessarily exposed publicly.

---

# PLT-9 — Identity, Secrets and Access

Each independently deployable component receives its own workload identity.

Example:

```text
Catalogue Service
    own workload identity
    own database credential

Orders Service
    own workload identity
    own database credential
```

Shared application credentials across bounded contexts are prohibited.

Secrets must be rotatable without requiring unrelated consumers to be redeployed.

---

# PLT-10 — Encryption

Platform capabilities must provide:

```text
TLS / encryption in transit

encryption at rest

managed key/secret capability

auditable access
```

especially for:

```text
PII
Financial
Regulated Evidence
```

---

# PLT-11 — CI/CD Architecture

```text
Source
   │
   ▼
Build
   │
   ▼
Unit / Security Validation
   │
   ▼
Artifact
   │
   ▼
Deploy
   │
   ▼
Runtime
   │
   ▼
Observe
```

Infrastructure is defined through IaC.

A feature cannot require manual infrastructure creation as its normal delivery mechanism.

---

# PLT-12 — Observability Platform

Standard capabilities:

```text
centralized logs
metrics
tracing
alerts
dashboards
Kafka monitoring
database monitoring
ECS/runtime monitoring
```

All workloads must propagate correlation identifiers defined by Integration Architecture.

---

# PLT-13 — Environment Strategy

Initial environments:

| Environment | Purpose |
|---|---|
| Development | Developer/integration work |
| Test | Automated feature/integration validation |
| UAT | Business acceptance |
| Production | Live workload |

Environment differences should be configuration/capacity differences rather than different architecture patterns.

---

# PLT-14 — Resilience

Architecture must define, where driven by NFRs:

```text
availability target

recovery time objective

recovery point objective

backup

multi-zone deployment

scaling policy
```

Values not provided by NFRs remain `PENDING`, rather than being invented.

---

# PLT-15 — Technology Lifecycle Compliance

For every technology selected:

```text
lifecycle_status != contain
AND
lifecycle_status != retire
```

unless an approved exception exists.

This check applies to future platform deltas as well.

---

# PLT-16 — Platform Conformance Checks

## PLT-C1 — Isolation

```text
cross_context_db_grants == 0
```

## PLT-C2 — Technology Lifecycle

```text
For every platform technology:
lifecycle status is approved
OR exception exists
```

## PLT-C3 — Deployability

```text
Each bounded context:
has at least one independently deployable component
```

## PLT-C4 — Classified Data Protection

```text
PII / Financial storage:
encryption capability enabled
```

---

# PLT-17 — Pending Decisions

| Decision | Status | Trigger |
|---|---|---|
| Search capability | NOT PRESENT | First full-text/indexed-search feature |
| Scheduled-job runtime | NOT PRESENT | First scheduled/batch requirement |
| Analytical platform | PENDING | DAT-4 analytical trigger |
| Exact capacity sizing | PENDING | Production-volume NFR |

---

# PLT-18 — Platform Delta Example

Cycle 2 buyer search:

```json
{
  "target_document":
    "architecture/platform-architecture.md",

  "from_version":
    "1.0",

  "changes": [
    {
      "type": "additive",
      "section": "PLT-6",
      "content":
        "Provision Search Index capability"
    },
    {
      "type": "extending",
      "section": "PLT-6",
      "content":
        "Search Index status: NOT PRESENT → AVAILABLE"
    }
  ],

  "version_bump": "minor",
  "structural": false,
  "adr_required": false
}
```

The corresponding platform repository contains the actual IaC/provisioning implementation.

The architecture document records the architectural capability and state.

---

# PLT-19 — Cycle 0 Exit Proof

Platform readiness is proven rather than scored subjectively.

A trivial service must demonstrate:

```text
build
   ✓

deploy
   ✓

run
   ✓

be observable
   ✓

emit event
   ✓

consume event
   ✓
```

Only after this succeeds is the platform considered ready for feature delivery.

---

## Version History

| Version | Change |
|---|---|
| 1.0 | Initial HarvestLink Cycle 0 Platform Architecture |