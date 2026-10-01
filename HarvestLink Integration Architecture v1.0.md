# HarvestLink Marketplace — Integration Architecture

## 1. Document Control

**Document:** Integration Architecture  
**Project:** HarvestLink Marketplace  
**Version:** 1.0  
**Lifecycle Stage:** Cycle 0  
**Status:** Approved  
**Owner:** Integration Architect  
**Canonical Location:** `/architecture/integration-architecture.md`  
**Parent:** `foundational-solution-architecture.md`

---

## 2. Purpose and Scope

This document defines the canonical rules by which HarvestLink bounded contexts, applications and external systems exchange information.

It satisfies the integration demands defined by the Foundational Solution Architecture.

This document defines:

- permitted integration styles
- synchronous vs asynchronous rules
- contract ownership
- API conventions
- event/topic conventions
- versioning
- cross-context flow governance
- degraded-mode requirements
- resilience expectations
- integration observability

Individual endpoint payloads belong in service OpenAPI specifications.

---

## 3. Inputs

- HarvestLink PRD and NFRs
- Binding architecture principles
- Foundational bounded-context/component map
- `CON-*` constraints
- `REQ-INT-*` demands
- Data Architecture
- Dependency graph
- Initial epics/features

---

# INT-1 — Integration Principles

## INT-1.1 Contract-Mediated Integration Only

All cross-context interactions require a governed interface.

Permitted:

```text
API
Event
Approved read model
```

Prohibited:

```text
direct cross-context database access
shared mutable tables
unmanaged point-to-point file exchange
```

---

## INT-1.2 Async Is the Default for Cross-Context Propagation

If a downstream result is not required to complete the caller's immediate transaction:

```text
prefer asynchronous event
```

Example:

```text
Orders
   │
   │ order placed
   ▼
Kafka
   │
   ▼
Billing
```

---

## INT-1.3 Synchronous Calls Require Justification

A synchronous cross-context dependency is permitted when:

```text
the caller requires the result
to continue the current user transaction
```

and it must define:

- latency budget
- timeout
- degraded-mode behavior
- ownership
- contract version

Example:

```text
Orders
   │
   │ "Is this listing currently available?"
   ▼
Catalogue
```

Checkout cannot safely proceed without the availability decision.

---

# INT-2 — Approved Integration Styles

| Style | Use | Example |
|---|---|---|
| REST/HTTP | Immediate response required | Orders → Catalogue |
| Domain event | Downstream processing can be decoupled | Orders → Billing |
| Domain event | Notification/side effect | Billing → Notifications |

Database integration is not an approved style.

---

# INT-3 — Contract and Topic Rules

## INT-3.1 Event Naming

Canonical pattern:

```text
{context}.{entity}.{event}
```

Examples:

```text
catalogue.listing.published

orders.order.placed

billing.payout.scheduled
```

---

## INT-3.2 Event Versioning

Every event contract has an explicit version.

Example:

```text
orders.order.placed
version 1.0.0
```

Breaking changes require controlled migration.

---

## INT-3.3 API Versioning

Public/service APIs use explicit versioning.

Example:

```text
/v1/listings

/v1/orders
```

---

# INT-4 — Canonical Cross-Context Flow Register

## INT-4.1 Checkout Listing Validation

### Purpose

Orders must confirm listing availability before creating an order.

### Flow

```text
Buyer SPA
    │
    ▼
Orders Service
    │
    │ synchronous request
    ▼
Catalogue Service
    │
    ▼
Listing availability result
    │
    ▼
Orders Service
```

### Owner of Contract

Catalogue.

### Why Synchronous

Orders requires the answer before completing checkout.

### Required Design Values

```text
Latency budget: defined by REQ-INT/NFR
Timeout: defined before implementation
Degraded mode: reject/defer checkout rather than use unknown availability
```

---

## INT-4.2 Order Placed → Billing

### Purpose

Trigger downstream financial processing without coupling the order transaction to Billing availability.

### Flow

```text
Orders
   │
   │ orders.order.placed
   ▼
Kafka
   │
   ▼
Billing
   │
   ├── create Transaction
   ├── calculate Fee
   └── initiate Payout lifecycle
```

### Producer

Orders

### Consumer

Billing

### Ownership

Orders owns the event contract.

Billing owns Transaction, Fee and Payout.

---

## INT-4.3 Payout Scheduled → Notifications

```text
Billing
   │
   │ billing.payout.scheduled
   ▼
Kafka
   │
   ▼
Notifications
```

Notifications is a consumer and does not become owner of Payout.

---

# INT-5 — Initial Contract Register

| Contract | Owner | Consumer | Style | Version | Initial State |
|---|---|---|---|---|---|
| Listing API | Catalogue | Producer SPA / Buyer SPA | REST | v1 | Planned |
| Listing availability | Catalogue | Orders | REST | v1 | Planned |
| Order API | Orders | Buyer SPA | REST | v1 | Planned |
| `catalogue.listing.published` | Catalogue | TBD | Event | 1.0.0 | Planned |
| `orders.order.placed` | Orders | Billing | Event | 1.0.0 | Planned |
| `billing.payout.scheduled` | Billing | Notifications | Event | 1.0.0 | Planned |

`Planned` means the architecture recognizes the contract but the producing feature has not necessarily been implemented.

---

# INT-6 — Reliability and Failure Policy

## Synchronous Integrations

Every synchronous dependency shall define:

```text
latency budget
timeout
retry policy
circuit-breaker policy if applicable
degraded mode
```

Example:

```text
Orders → Catalogue failure

Orders must not assume:
"listing probably exists"

The degraded behaviour is explicitly defined.
```

---

## Asynchronous Integrations

Each consumer shall define:

```text
duplicate handling
idempotency
retry strategy
dead-letter/recovery path
event replay policy
```

Example:

```text
orders.order.placed
delivered twice
       ↓
Billing must not create two Transactions
for the same business event.
```

---

# INT-7 — Identity and Trust Boundaries

Identity is upstream of HarvestLink services.

Conceptually:

```text
User
  │
  ▼
Identity
  │
  │ authenticated identity
  ▼
Client / Service Request
```

At every trust boundary:

- caller identity must be established
- authorization is applied
- correlation information is preserved

Exact identity technology belongs to the Platform/Identity design.

---

# INT-8 — Integration Observability

Every integration must be observable through:

```text
correlation ID
trace ID
contract/version identification
latency metrics
failure metrics
event consumer lag
retry/dead-letter metrics
```

Platform Architecture provides the implementation capability.

Integration Architecture defines the requirement.

---

# INT-9 — Contract Change Policy

## Compatible Change

Example:

```text
Add optional field:
producer_display_name
```

May evolve within the compatible contract policy.

## Breaking Change

Example:

```text
rename listing_id → product_listing_id
and remove listing_id
```

Must use an expand-and-contract approach.

Conceptually:

```text
Provider supports old + new
          ↓
Consumers migrate
          ↓
Old field deprecated
          ↓
Old contract removed later
```

A provider release must not unexpectedly break existing consumers.

---

# INT-10 — Traceability to Principles

| Principle | Integration Decision |
|---|---|
| Governed reusable interfaces | INT-1 |
| Async by default | INT-1.2 |
| Sync only with explicit need | INT-1.3 |
| No cross-context direct persistence | INT-1.1 |
| Versioned contracts | INT-3 / INT-9 |
| Security designed in | INT-7 |

---

# INT-11 — Conformance Checks

## INT-C1 — Every Cross-Context Edge Has a Contract

```text
For every interaction in the component graph:

API contract exists
OR
event contract exists
```

## INT-C2 — No Cross-Context DB Grants

```text
count(cross_context_database_grants) == 0
```

## INT-C3 — Synchronous Calls Are Budgeted

```text
For every synchronous cross-context edge:

latency budget exists
AND
degraded mode exists
```

---

# INT-12 — Pending Decisions

| Decision | Status | Trigger |
|---|---|---|
| Event schema registry product | PENDING | Independent consumers require schema-governance capability |
| Exact API gateway product/configuration | PENDING | Platform realization |
| Final Orders→Catalogue latency value | PENDING | Checkout NFR finalized |

---

# INT-13 — Feature Delta Model

Cycle 1 may produce:

```json
{
  "target_document":
    "architecture/integration-architecture.md",

  "from_version": "1.0",

  "changes": [
    {
      "type": "additive",
      "section": "INT-5",
      "content":
        "Activate Catalogue listing contracts"
    },
    {
      "type": "additive",
      "section": "INT-5",
      "content":
        "Register catalogue.listing.published v1.0.0"
    }
  ],

  "structural": false,
  "adr_required": false
}
```

After implementation and verification:

```text
Integration Architecture
v1.0 → v1.1
```

---

## Version History

| Version | Change |
|---|---|
| 1.0 | Initial HarvestLink Cycle 0 integration rules and contract register |