<!--
kb-L0-target-architecture-template · content · target-architecture-template.md
Layer: L0 (enterprise-wide, cross-phase — NOT domain-specific).
The literal document template L0-target-architecture-generator fills to
produce {product_name}-target-architecture.md. Headings, callouts, tables
and the *shall* voice are kept exactly; every {placeholder} is replaced;
table rows repeat as needed. Appendix B is emitted only when a baseline
document was supplied. Rules for filling each section live in the agent
prompt, not here. Illustrative structure derived from the HarvestLink
reference target architecture (HL-ARC-001).
-->

# Target Architecture Document Template

Fill as `{product_name}-target-architecture.md`. Keep headings, callouts, tables and the *shall* voice exactly; replace every `{placeholder}`; repeat table rows as needed.

# {product_name} Target Architecture
**{product_name} · Enterprise Architecture** · Status: **Draft**
*Domain decomposition, ownership boundaries, cross-viewpoint constraints, and the demands every realisation of {product_name} must satisfy*
## 1. Purpose and Scope
> **PURPOSE**
>
> {What this document sets out: how the system is divided into bounded contexts, which context is the system of record for each entity, which rules bind every design decision, and what the domain requires of the data, integration and platform architectures. State that it is technology-free and that technology belongs to {document_code}-ARC-002.}

> **KEY ARCHITECTURAL ASSUMPTION**
>
> {The regulatory or business fronts that must not be blurred, and why each is kept inside a context that owns it outright.}
### What this document covers
#### In scope
- {Business drivers and principles, including recorded deviations} · {Domain decomposition} · {Components, aggregates and invariants} · {Constraints and demands with budgets} · {Required security controls and change governance}
#### Not attempted here
- {Technology selection, in {document_code}-ARC-002} · {Physical data design} · {Interface specifications} · {Component design and delivery planning}
> **READING THIS DOCUMENT**
>
> {One line per section stating what it holds.} Statements using *shall* are normative; every normative item carries a stable key and is cross-referenced by it.
---
## Document Control and Contents
| Attribute | Value |
|---|---|
| **Document ID** | {document_code}-ARC-001 · version {n.n} |
| **Document type** | Target architecture (normative) |
| **Owner and approver** | Enterprise Architect |
| **Change control** | Amended only through an approved Architecture Decision Record (Section 11) |
| **Realised by** | {document_code}-ARC-002 {product_name} Solution Architecture |
| **Governing principles** | {principle ids} (Section 3) |
| **Decision records** | ADR-001 to ADR-{NNN} (Section 11) |
| **Classification** | Internal |
| **Baseline** | {previous version, or "None"} |
### Approvals
| Role | Responsibility | Signature | Date |
|---|---|---|---|
| **Enterprise Architect** | Owner and approver |   |   |
| {reviewer roles from architecture_notes; default Solution Architect, Platform Lead, and the business owner of the regulated obligations} | {responsibility} |   |   |
### Contents
{Linked list of sections 1 to 12, Appendix A, and Appendix B when present}
---
## 2. Business Context and Drivers
*What {product_name} does, who depends on it, and the obligations that shape its architecture*
> **THE BUSINESS**
>
> {One paragraph in the PRD's own terms.}
### System context
```mermaid
{flowchart TB: people, the system as one box, external systems; labelled edges; dashed edges for systems not yet selected}
```
***FIGURE 1** · {product_name} as a single software system, with the people who use it and the external systems it depends on.*
| Actor or system | Role | Primary interest in {product_name} |
|---|---|---|
| **{actor}** | {Customer / Seller / Internal operator / External regulator / External system} | {interest; cite REQ or OI key where relevant} |
### Business drivers
| Key | Driver | Architectural consequence |
|---|---|---|
| **DRV-{NN}** | {driver} | {consequence, citing PRD locator} |
> **WHY THIS SECTION MATTERS**
>
> {Which boundaries trace to which drivers; which drivers are regulatory and what the architecture therefore favours.}
---
## 3. Architecture Principles
*The enterprise principles that bind {product_name}, and how this architecture stands against each*
> **HOW PRINCIPLES APPLY**
>
> {Count of principles; decomposition-shaping ones applied here, technology-selecting ones in {document_code}-ARC-002; a departure is permitted only as a recorded deviation under CON-{n}; an unrecorded deviation is a defect.}
| Principle | Statement | Position | Where it is applied |
|---|---|---|---|
| **{id}** | {statement} | **{Satisfied / Recorded deviation / Applied in {document_code}-ARC-002 / At risk / Not applicable}** | {keys in this document, ADRs, or DEV-NN / OI-NN} |
### Recorded deviation
| Key | Deviation record |
|---|---|
| **DEV-{NN}** | **Principle:** {id}, {statement}.<br>**Scope:** {named flows, and no others}.<br>**Rationale:** {from binding_principles}.<br>**Approved by:** {approver or Pending}. |
> **WHAT THIS MEANS IN PRACTICE**
>
> {The deviation is bounded, not general; what a new request of the same kind needs.}
---
## 4. Domain Decomposition
*{N} bounded contexts, each the single owner of its entities* · Keys: `APP-1`
> **ARCHITECTURE POSITION**
>
> {Decomposition in one paragraph, citing ADRs, CON-{n} for system of record and CON-{n} for deployability; the reason-for-change test.}
| Bounded context | Subdomain | Purpose | Owns | Publishes |
|---|---|---|---|---|
| **{context}** | {Core / Supporting / Generic} | {purpose} | {entities} | {events, or "None; queried by other contexts"} |
{Definitions of core, supporting and generic.}
### Business capability map
```mermaid
{flowchart: capabilities grouped by owning context; from epics_and_features when supplied, else from Section 6 capabilities}
```
***FIGURE 2** · Business capabilities grouped by the bounded context that owns them.*
### Domain view
```mermaid
{flowchart TB: people → experience components → bounded contexts → external systems; labelled edges; class per subdomain type}
```
***FIGURE 3** · How people reach each bounded context through the experience components. Interactions between contexts are in Section 5. The view is technology-free; each context is realised by the single component named in `APP-2`.*
---
## 5. Context Map and Interaction Model
*How the bounded contexts depend on each other, by which pattern, and within which budget* · Keys: `APP-1`
> **THE INTERACTION RULE**
>
> {Default is an event; a request only when needed inside a user's action and a stale answer would be visible or disputable; every request is named and covered by DEV-NN; a request protecting a regulatory invariant fails closed, one that improves a display degrades.}
```mermaid
{flowchart TB of contexts; solid arrows "R-NN · what · failure mode · budget" for requests; dashed arrows "R-NN · event · bound" for events}
```
***FIGURE 4** · Context map. Solid arrow: a request, from the asking context to the answering one. Dashed arrow: an event, from publisher to consumer. {Note any read models listed but omitted from the figure.}*
| Key | Asking or consuming | Answering or publishing | Relationship | Interaction and consistency | Governs |
|---|---|---|---|---|---|
| **R-{NN}** | {context} | {context} | {DDD relationship type} | {Request at {moment} · fail-closed/degrades · current / Event: {name} · eventual, within {bound} / Registered analytical read model · {freshness}} | {INV, CON, REQ keys} |
### Rules that hold across every relationship
- {Value owned elsewhere obtained through the published contract (CON keys)} · {No direct reads except registered snapshot and read model} · {Identity upstream of every context} · {Which context is downstream of which, and the outage consequence}
> **WHAT THIS MAP SHOWS**
>
> {Which path carries fail-closed requests and why; what is event-driven and can be delayed.}
---
## 6. Bounded Context Definitions
*Purpose, capabilities, boundary and rationale for each context* · Keys: `APP-1`
#### {Context}
*{Subdomain} · owns {entities}*
**Purpose.** {one sentence}
**Capabilities.** {list; each traces to prd:<requirement keys>}
**Boundary.** {what it explicitly does not own and who does}
**Rationale.** {reason-for-change argument}
{repeat per context}
> **THE BOUNDARY MOST LIKELY TO BE CHALLENGED**
>
> {Which merge would work and why it is rejected: different reasons, regulators or approval paths. Effort is never the test; reason-for-change is.}
---
## 7. Components, Aggregates and Invariants
*Which component realises each context, and the rules every realisation must enforce* · Keys: `APP-2` · `APP-3`
### APP-2 · Component map and responsibility allocation
{Each context is realised by exactly one service; experience components hold no business rule not enforced by a service; platform components own no entities.}
| Component | Kind | Context | Responsible for | Explicitly not responsible for |
|---|---|---|---|---|
| **{name}** | {Service / Experience / Platform} | {context or —} | {responsibilities} | {non-responsibilities} |
### APP-3 · Aggregates and invariants
| Key | Aggregate (context) | Invariant | Why it exists |
|---|---|---|---|
| **INV-{NN}** | {aggregate} ({context}) | {rule in shall form} | {DRV key or PRD locator} |
> **WHY INVARIANTS SIT IN THIS DOCUMENT**
>
> {Invariants enforced in more than one viewpoint are stated once here, above the viewpoints.}
---
## 8. Cross-Viewpoint Constraints
*Rules that bind the data, integration and platform architectures alike* · Keys: `CON`
> **HOW CONSTRAINTS APPLY**
>
> {Binding on every realisation; each section of {document_code}-ARC-002 shows how it honours them; conformance assessed at every release.}
| Key | Constraint | Rationale |
|---|---|---|
| **CON-{N}** | {constraint} | {principle, driver or ADR} |
> **THE DISTINCTION THAT MATTERS MOST**
>
> {Snapshot versus replicated attribute, and why registration is mandatory.}
---
## 9. Demands on Data, Integration and Platform
*What the decomposition requires of each viewpoint, each stated with its budget* · Keys: `REQ` · `QA`
> **HOW DEMANDS ARE MET**
>
> {What versus how; the satisfying section of {document_code}-ARC-002 cites the demand by key; an unsatisfied demand is "not yet built".}
### Data
| Key | Demand | Driven by |
|---|---|---|
| **REQ-DAT-{NN}** | {demand incl. classification and retention} | {CON / INV / DRV} |
### Integration
| Key | Demand | Budget |
|---|---|---|
| **REQ-INT-{NN}** | {demand} | {p95 budget inside which operation budget, or "Eventual" with bound, or —} |
### Platform
| Key | Demand | Driven by |
|---|---|---|
| **REQ-PLT-{NN}** | {demand} | {CON / REQ / DRV} |
### Quality attributes
| Key | Attribute | Target | Measured at |
|---|---|---|---|
| **QA-{NN}** | {attribute} | {target from PRD, or **Requires validation** (`OI-NN`)} | {where measured} |
> **BUDGETS ARE SPLIT, NOT GROWN**
>
> {How each user-facing budget is allocated across its synchronous dependencies.}
---
## 10. Required Security Controls
*The controls every realisation shall implement, by viewpoint* · Keys: `SEC`
> **SECURITY AS A CROSS-CUTTING REQUIREMENT**
>
> {Security places requirements on every viewpoint; the implemented control is recorded in {document_code}-ARC-002 under the same key.}
| Key | Viewpoint | Required control | Principle or driver |
|---|---|---|---|
| **SEC-{N}** | {Application / Data / Integration / Platform} | {control} | {principle id, DRV or ES key} |
> **INTERFACE DESIGN THAT LEAKS NOTHING**
>
> {Contracts shall not reveal the existence of resources the caller does not own.}
---
## 11. Architecture Decisions and Governance
*The decisions this target rests on, and how it is changed and assured*
### Decision record
| ADR | Decision | Sections it governs |
|---|---|---|
| **ADR-{NNN}** | {decision} | {keys} |
### Change control
#### Changes that amend this document
- {list} · Each requires an ADR approved by the Enterprise Architect; major version step for a context or constraint change, minor otherwise.
#### Changes that do not
- {list} · Approved by the Solution Architect, with the Platform Lead where platform capability is affected.
### Assurance and deviation handling
- **Conformance.** {Conformant / Not yet built / Deviating at each release.}
- **Deviations.** {Never legitimised by an ADR; logged in the deviation register with key, owner and removal date.}
- **Records.** {ADRs are append-only.}
---
## 12. Architectural Position and Open Items
#### Architectural positions
- **Position {n}:** {one line}
#### What design still must answer
- **OI-{NN}** {open item, citing the key it affects}
> **BOTTOM-LINE POSITION**
>
> {What the hardest problems are, what the architecture optimises for, and what cost it accepts.}
| Question | Architecture answer |
|---|---|
| **{question a reader asks}** | {answer citing keys} |
---
## Appendix A. Glossary
| Term | Meaning in {product_name} |
|---|---|
| **{term}** | {meaning, citing key where relevant} |
---
## Appendix B. Change Register (for review)
*Only when a baseline document was supplied. One row per difference from the baseline; this register is the complete record of what changed.*
| Key | Change type | Before | After | Rationale | Review status |
|---|---|---|---|---|---|
| **{key}** | {added / amended / withdrawn} | {baseline text, or —} | {new text, or —} | {prd:<key>, principle id or reviewer note that caused it} | pending-human-review |
