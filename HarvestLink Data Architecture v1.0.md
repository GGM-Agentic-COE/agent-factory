# HarvestLink Marketplace — Data Architecture

## 1. Document Control

**Document:** Data Architecture  
**Project:** HarvestLink Marketplace  
**Version:** 1.0  
**Lifecycle Stage:** Cycle 0  
**Status:** Approved  
**Owner:** Data Architect  
**Canonical Location:** `/architecture/data-architecture.md`  
**Parent:** `foundational-solution-architecture.md`

---

## 2. Purpose and Scope

This document defines the canonical data architecture for HarvestLink Marketplace.

It translates the data-related constraints and demands established by the Foundational Solution Architecture and binding enterprise principles into concrete data decisions.

It defines:

- authoritative ownership of business entities
- systems of record
- cross-context data-access rules
- event-data envelope rules
- data classification
- retention and residency requirements
- operational and analytical data planes
- controlled replication/read-model rules
- deferred data decisions and their triggers

Physical table definitions, indexes, ORM classes and SQL implementation details are outside this document and belong in service HLD/LLD.

---

## 3. Inputs

### Product Inputs

- HarvestLink PRD
- Functional requirements
- NFR classifications
- Regulatory posture:
  - GDPR for Producer and Buyer data
  - PSD2-related payment requirements
  - financial/tax evidence requirements

### Architecture Inputs

- Binding architecture principles
- Foundational Solution Architecture
- Bounded-context model
- Entity ownership model
- `CON-*` cross-viewpoint constraints
- `REQ-DAT-*` demands

### Planning Inputs

- Impact assessment
- Dependency graph
- Initial epics/features
- Roadmap

---

## 4. Principles Applied

### PRIN-02 — One Accountable Owner and One Authoritative Source Per Data Domain

HarvestLink shall maintain exactly one authoritative owner for every critical domain entity.

No bounded context may become a second writer for an entity owned elsewhere.

### PRIN-03 — Governed Integration Only

A service requiring data owned by another context shall consume that data through an approved API, event or governed read model.

Direct cross-context table access is prohibited.

### PRIN-06 — Security and Privacy Designed In

Every PII, financial or regulated-evidence entity shall have classification, retention and residency rules before it is persisted.

---

# DAT-1 — Domain Entity and System-of-Record Architecture

## DAT-1.1 Bounded Context Ownership

| Entity | Owning Context | Authoritative System of Record | Classification |
|---|---|---|---|
| Product | Catalogue | Catalogue persistence | Internal |
| Listing | Catalogue | Catalogue persistence | Internal |
| Category | Catalogue | Catalogue persistence | Internal |
| Order | Orders | Orders persistence | Confidential |
| OrderLine | Orders | Orders persistence | Confidential |
| OrderStatus | Orders | Orders persistence | Internal |
| Transaction | Billing | Billing persistence | Financial |
| Fee | Billing | Billing persistence | Financial / Regulated Evidence |
| Payout | Billing | Billing persistence | Financial |
| Producer | Identity | Identity persistence | PII |
| Buyer | Identity | Identity persistence | PII |
| Session | Identity | Identity persistence | Security-sensitive |

Notifications owns no core domain entities.

---

## DAT-1.2 System-of-Record Rules

### DAT-1.a — Exactly One Writer

Every entity has exactly one authoritative owning context.

Examples:

```text
Listing
    Owner: Catalogue

Order
    Owner: Orders

Fee
    Owner: Billing
```

Orders may reference a Listing but may not become another writer of Listing.

---

### DAT-1.b — No Cross-Context Direct Database Access

The following is prohibited:

```text
Orders Service
       │
       ▼
Catalogue PostgreSQL tables
```

The permitted pattern is:

```text
Orders Service
       │
       │ governed contract
       ▼
Catalogue Service
       │
       ▼
Catalogue persistence
```

---

## DAT-1.3 Logical Domain Relationships

```text
Producer
   │
   └── creates
          ▼
       Listing
          │
          └── describes
                 ▼
              Product


Buyer
   │
   └── places
          ▼
        Order
          │
          ├── OrderLine
          └── OrderStatus


Order
   │
   │ business event
   ▼
Transaction
   │
   ├── Fee
   └── Payout
```

These relationships describe business meaning.

They do not imply database foreign keys across bounded contexts.

---

## DAT-1.4 Cross-Context Reference Policy

A non-owning context may normally retain:

```text
entity identifier
```

Example:

```text
OrderLine.listing_id
```

Orders may retain `listing_id`, but Catalogue remains the owner of Listing.

Replicated attributes require an explicit registered read model and staleness rule.

---

# DAT-2 — Event Data Architecture

## DAT-2.1 Canonical Event Envelope

All domain events use a standard envelope.

```json
{
  "event_id": "uuid",
  "event_type": "catalogue.listing.published",
  "event_version": "1.0.0",
  "occurred_at": "ISO-8601 timestamp",
  "producer_context": "Catalogue",
  "correlation_id": "uuid",
  "payload": {}
}
```

The envelope is independent of the business-specific payload.

---

## DAT-2.2 Initial Event Register

At Cycle 0 the register establishes known architectural events.

| Event | Owner | Purpose | Version |
|---|---|---|---|
| `catalogue.listing.published` | Catalogue | Listing lifecycle notification | Planned |
| `orders.order.placed` | Orders | Inform downstream financial processing | Planned |
| `billing.payout.scheduled` | Billing | Inform notification capability | Planned |

A planned event becomes active only when the corresponding feature is implemented.

---

## DAT-2.3 Event Ownership

The producing context owns the business meaning of its event.

Example:

```text
orders.order.placed
```

is owned by Orders.

Billing may consume the event but does not become owner of Order.

---

# DAT-3 — Classification, Retention and Residency

## DAT-3.1 Classification Model

| Classification | Meaning |
|---|---|
| Public | Safe for public disclosure |
| Internal | Internal operational information |
| Confidential | Sensitive business/user information |
| PII | Personally identifiable information |
| Financial | Financially sensitive information |
| Regulated Evidence | Must be preserved for audit/compliance |

---

## DAT-3.2 Data Classification Register

| Entity | Classification | Retention | Residency |
|---|---|---|---|
| Product | Internal | Business lifecycle | Approved operating region |
| Listing | Internal | Business lifecycle | Approved operating region |
| Order | Confidential | Policy-defined | Approved operating region |
| Fee | Financial / Regulated Evidence | 10 years | Approved financial-data region |
| Transaction | Financial | Policy-defined | Approved financial-data region |
| Payout | Financial | Policy-defined | Approved financial-data region |
| Producer | PII | GDPR policy | Approved PII region |
| Buyer | PII | GDPR policy | Approved PII region |

Where exact retention is not yet supplied by the regulatory requirement, the value remains `PENDING`, not guessed.

---

## DAT-3.3 Encryption Requirement

All PII and Financial data requires:

```text
encryption at rest
+
encryption in transit
+
attributable access
```

The data architecture states the requirement.

Platform Architecture determines the technical realization.

---

# DAT-4 — Data Planes

## DAT-4.1 Operational Data Plane

**Decision:** REQUIRED

The operational plane supports interactive business transactions.

### Technology

```text
PostgreSQL
```

### Ownership Model

```text
Catalogue → Catalogue schema

Orders → Orders schema

Billing → Billing schema

Identity → Identity schema
```

A schema is platform infrastructure; domain ownership remains with its bounded context.

---

## DAT-4.2 Object Data

Listing image binaries are not stored as relational database blobs.

Object-storage capability is used.

Catalogue retains the business metadata/reference.

Example:

```text
Listing
   │
   ├── image_id
   └── image_uri/reference

Object Store
   └── image bytes
```

---

## DAT-4.3 Analytical Plane

**Status:** PENDING

HarvestLink does not create an analytical platform during Cycle 0 merely because one may eventually be useful.

### Decision Trigger

The analytical-plane decision must be reopened when the first requirement requires any of:

```text
1. Aggregation over more than one month

2. A query joining authoritative data
   across two or more bounded contexts

3. A non-interactive analytical read SLA
```

Until one of these conditions occurs:

```text
Analytical Store = NOT PRESENT
```

---

# DAT-5 — Consistency Model

## Inside One Context

Transactional operations may use strong database consistency.

Example:

```text
Create Order
   │
   ├── Order
   ├── OrderLines
   └── initial OrderStatus
```

These belong to the Orders transaction boundary.

---

## Across Contexts

Distributed database transactions are not permitted as the default integration mechanism.

Example:

```text
Orders
   │
   │ orders.order.placed
   ▼
Billing
```

Billing processing may therefore become eventually consistent with Orders.

---

# DAT-6 — Read Models and Replication Register

| Read Model | Source Owner | Consumer | Staleness Budget | Status |
|---|---|---|---|---|
| None at Cycle 0 | — | — | — | — |

Any future replicated attribute must be entered here before use.

---

# DAT-7 — Data Architecture Demand Traceability

| FSA Demand / Principle | Data Architecture Satisfaction |
|---|---|
| One system of record per entity | DAT-1 ownership register |
| No cross-context table access | DAT-1.b |
| Financial retention | DAT-3 retention register |
| PII protection | DAT-3 classification/security |
| Event data governance | DAT-2 |
| Operational/analytical separation | DAT-4 |

---

# DAT-8 — Pending Decisions

| ID | Decision | Status | Trigger |
|---|---|---|---|
| DAT-PEND-01 | Analytical platform | PENDING | DAT-4 trigger |
| DAT-PEND-02 | Exact Order retention | PENDING | Legal retention requirement approved |
| DAT-PEND-03 | Exact Transaction retention | PENDING | Finance/compliance policy approved |

A pending decision must always have a trigger.

---

# DAT-9 — Conformance Checks

### DAT-C1 — One Writer Per Entity

```text
For every critical entity:
count(authoritative_writers) == 1
```

### DAT-C2 — No Unregistered Replication

```text
For every attribute copied from another context:
registered_read_model exists
```

### DAT-C3 — Protected Data Has Governance

```text
For every PII / Financial / Regulated entity:
classification exists
AND retention exists
AND residency exists
```

---

# DAT-10 — Change Model

Feature cycles do not rewrite this document.

They create:

```text
data-architecture.delta.json
```

Example from Producer Listing:

```json
{
  "target_document": "architecture/data-architecture.md",
  "from_version": "1.0",
  "changes": [
    {
      "type": "additive",
      "section": "DAT-2",
      "content": "Activate catalogue.listing.published v1.0.0"
    }
  ],
  "version_bump": "minor",
  "structural": false,
  "adr_required": false
}
```

After the feature is implemented, verified and merged:

```text
Data Architecture
v1.0 → v1.1
```

---

## Version History

| Version | Change |
|---|---|
| 1.0 | Initial Cycle 0 HarvestLink Data Architecture |