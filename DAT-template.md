# Data Architecture — Document Template

## 0. How to use this template

The Data Architecture is the **canonical data viewpoint (DAT-\*)** for one product. It answers, once and before any epic is cut, the four questions that every feature cycle would otherwise answer differently by accident: *who owns each entity*, *how is it classified, retained and located*, *what is the shape of an event*, and *which data planes exist*. It is produced at Cycle 0 (Phase 2.25) from the approved Foundational Solution Architecture, is gated by the Enterprise Architect alongside its two sibling viewpoints, and thereafter moves only by a `data-architecture.delta.json` emitted from a feature cycle.

It was previously triggered from the LLD. That made the data model a *consequence* of how someone happened to design their classes — an inverted dependency in a DDD regime. The foundational invocation exists to put the ownership register in front of the code, not behind it.

It owns exactly four things and deliberately nothing else:

1. **Ownership** — DAT-1: exactly one writing context per entity, and the system of record that holds it.
2. **Governance of the data itself** — DAT-3: classification, retention and residency, the three together, because that triple is what `PRIN-06-C1` checks.
3. **The event data standard** — DAT-2: the envelope every domain event carries, and the register of events the architecture already knows about.
4. **Planes, consistency and replication** — DAT-4 to DAT-6: which planes exist, where consistency is strong and where it is eventual, and every read model that copies someone else's attribute.

**The one-line tests for what belongs here.** Apply them to every sentence before it is written:

| Question | If yes… |
| --- | --- |
| Is it a `CREATE TABLE`, a column type, an index, a migration or an ORM class? | It is **never** in this document. That is service HLD/LLD, one phase later. |
| Does it say which bounded context may *write* an entity? | It is **only** in this document (DAT-1). |
| Is it a retention period, a residency region or a staleness budget with no cited source? | It is not a value. It is `PENDING` with a DAT-PEND trigger. |
| Does it choose the compute, the managed service or the cluster that *runs* a store? | It is Platform (PLT-3). State the capability the data needs; the realisation is theirs. |
| Does it name a topic, a contract version or an endpoint path? | It is Integration (INT-3). This document owns the envelope and the business meaning of the payload, not the transport. |
| Does it record what is deployed today, in which version, owned by which squad? | It is baseline payload. Never here — see Appendix A for the brownfield exception. |

**Section-ID spine.** `DAT-1` … `DAT-10`, the conformance checks `DAT-Cn`, and the deferrals `DAT-PEND-nn` are stable identifiers shared with the application baseline and the conformance checker. Headings may be reworded; IDs must never be renumbered or reused.

**Entity and context names are not yours to change.** They match the FSA's APP-1 and APP-3 exactly — never renamed, never renumbered, never invented. A name that differs from the FSA silently breaks every downstream key.

**Template conventions used below.**

- Text in `[square brackets]` is a placeholder the authoring agent replaces.
- Lines beginning *Example:* are illustrative content drawn from the HarvestLink producer/buyer marketplace (Catalogue, Orders, Billing, Identity, Notifications). Delete them in a real document.
- Text diagrams are plain ASCII in fenced `text` blocks — readable in a terminal, a diff and a PR review.
- **A value is either traceable or `PENDING`. There is no third category.** "Six years is typical for financial records" is an invention with a citation-shaped wrapper.
- Mode-specific guidance is marked **[GF]** greenfield, **[BF]** brownfield retrofit, or **[BOTH]**.

## 1. Document control

Every field is required. Version follows semantic versioning where a **major** bump means a normative change (an ownership move, a classification change, a new plane), a **minor** bump means a clarification or a restoration that changes no rule, and a **patch** is editorial.

| Field | Value | Notes |
| --- | --- | --- |
| Document | Data Architecture | Fixed |
| Document id | `dat-[system-slug]` | *Example:* `dat-harvestlink` |
| Canonical path | `/architecture/data-architecture.md` | Same path in every project; agents key on it |
| Project / product | `[name]` | *Example:* HarvestLink Marketplace |
| Version | `[MAJOR.MINOR.PATCH]` | *Example:* `1.0` at Cycle 0 |
| Lifecycle stage | `Cycle 0` / `Cycle [n] delta` | Cycle 0 is the foundational invocation |
| Status | `DRAFT` / `IN REVIEW` / `APPROVED` / `SUPERSEDED` | Only `APPROVED` is normative |
| Mode | `GREENFIELD-CREATE` / `BROWNFIELD-RETROFIT` / `BROWNFIELD-DELTA` | Drives Appendix A |
| Owner | Data Architect | Accountable human role |
| Authoring agent | `[agent id @ version]` | *Example:* `L1-design-data-architect@1.0.0` |
| Parent document | `foundational-solution-architecture.md @ [version]` | The exact version read |
| Approval gate | Enterprise Architect (with Platform Lead at Cycle 0 exit) | Recorded in the version history |
| Regulatory regimes in scope | `[list]` | Copied from the PRD's Regulatory Posture. *Example:* UK GDPR; HMRC/Companies Act business-record retention; food-safety registration validity |
| Downstream consumers | integration-architect · platform-architect · arch-baseline-generator · env-provisioner · synthetic-data-generator · gr-L1-architecture-conformance | Change the section spine and each of these breaks |

### 1.1 Version history

| Version | Date | Change type | Summary | Delta / ADR | Approver |
| --- | --- | --- | --- | --- | --- |
| `[1.0]` | `[date]` | Created | Initial Cycle 0 `[product]` Data Architecture | — | `[EA name]` |
| *Example:* 1.1 | 2026-05-02 | Normative (minor) | DAT-PEND-02 fired — REQ-31 (dispute handling) supplied an order-record obligation, so Order retention resolved from `PENDING` to 6 years (ES3) | `data-architecture.delta.json` c3 | J. Okafor |
| *Example:* 2.0 | 2026-09-14 | Structural (major) | FSA OPEN-02 fired: tax rates moved out of Billing into a new Tax context; Fee's owner and residency unchanged | ADR-011 + `data-architecture.delta.json` c7 | J. Okafor |

---

## 2. Purpose and Scope

### 2.1 Purpose statement

`[One paragraph, written for the Enterprise Architect, stating what this document decides for this product and why those decisions cannot wait for a feature cycle. Readable without the PRD.]`

*Example:* This document fixes data ownership, classification and plane decisions for HarvestLink before the first epic is cut. Two decisions carry most of the weight. **Fee is owned by Billing alone**: REQ-07 requires the figure shown at confirmation to be the figure charged, so a copy of it in Orders would be a mis-selling risk rather than a caching convenience — the read stays synchronous (INT-4.2). **FoodSafetyRegistration is owned by Identity alone**: REQ-12 requires a producer's registration to be valid at the point of sale, so Catalogue must ask rather than remember (INT-4.3). Both are decisions the first cycle that needs an answer would otherwise make in an afternoon, in whichever direction is cheapest that afternoon. Ownership settled here costs a conversation; ownership discovered in Cycle 3 costs a migration and a dispute.

### 2.2 What this document owns

| Section IDs | Owns | Downstream reader |
| --- | --- | --- |
| DAT-1 | Entity ownership and system-of-record rules | integration-architect, platform-architect, LLD agents, synthetic-data-generator |
| DAT-2 | Canonical event envelope and event register | integration-architect (INT-3 naming, kinds and versioning build on this) |
| DAT-3 | Classification, retention, residency, encryption *requirement* | platform-architect (PLT-10 realisation), security review, env-provisioner |
| DAT-4 | Operational, object and analytical planes; lineage | platform-architect (PLT-3, PLT-5), impact-assessor |
| DAT-5 / DAT-6 | Consistency boundaries; read model and replication register | integration-architect, test scenario writers |
| DAT-7 | Traceability from REQ-DAT-\*, CON-\* and principles to the answer | gr-L1-architecture-conformance |
| DAT-8 / DAT-9 | Pending decisions with triggers; evaluable conformance checks | impact-assessor (fires triggers), conformance checker |

### 2.3 What this document must never contain

- Physical schema of any kind: `CREATE TABLE`, column types, indexes, constraints, migrations, ORM classes, SQL.
- Runtime topology, instance sizing, backup jobs, cluster configuration — that is PLT-3 and PLT-14.
- Topic names, contract versions, endpoint paths, retry policy — that is INT-3 and INT-6.
- Team names, service names or database names as *owners*. Ownership is assigned to a bounded context, never to a team, a service or a store.
- A retention period, residency region or staleness budget that no cited source supports.
- Deployed versions, owning squads, CMDB identifiers — baseline payload.

### 2.4 Position in the lifecycle

```mermaid
flowchart LR
  FSA[Foundational Solution Architecture<br/>APP-1 · APP-3 · CON-* · REQ-DAT-*] --> DAT[Data Architecture]
  PRD[PRD + regulatory posture] --> DAT
  BP[binding-principles.json] -.optional.-> DAT
  DAT --> INT[Integration Architecture]
  DAT --> PLT[Platform Architecture]
  DAT --> BL[Application baseline v0.1]
  INT --> BL
  PLT --> BL
  BL --> C1[Cycle 1 — first feature]
```

Data runs first among the three viewpoints because Integration needs the ownership register to know who may publish what, and Platform needs the classification register to know what must be encrypted and isolated. **[BF]** In brownfield this document is normally *read*, not written; it is authored when a running system has no canonical data viewpoint (retrofit) or when a delta moves it.

---

## 3. Inputs and provenance

Every decision below must trace to an input listed here, at the version actually read this run. List only what was read — an input table naming a document the agent never opened is worse than no table.

### 3.1 Product inputs [BOTH]

| Input | Artifact and version read | What was taken from it | Mandatory |
| --- | --- | --- | --- |
| Product requirements | `prd.md @ [version]` | Data-bearing functional scope; the nouns of the domain | Yes |
| Regulatory posture | `prd.md § Regulatory Posture` / `vision.md @ [version]` | Regimes in scope — without these, classification is guesswork wearing a table | Yes |
| NFR classification | `nfr_classifications.json @ [version]` | Per-requirement retention, availability and classification constraints | Where produced |

### 3.2 Architecture inputs [BOTH]

| Input | Artifact and version read | What was taken from it | Mandatory |
| --- | --- | --- | --- |
| Foundational architecture | `foundational-solution-architecture.md @ [version]` | APP-1 contexts; **APP-3 aggregates, entities and invariants**; every CON-\* binding DAT; every REQ-DAT-\*; SEC-\* controls touching data; § 4 PRIN rows | Yes — **blocking** |
| Binding principles resolution | `binding-principles.json @ [version]` | Applicability, binding level, resolved scope, `program_guardrail`, `conformance_checks`, and the `fsa_hooks` whose `binds_viewpoints` contains `DAT` | Optional — see 3.3 |

**Blocking input rule.** An FSA with no APP-3 aggregate model is `INSUFFICIENT_CONTEXT`, not a document to be written around: without an entity set there is nothing to assign ownership over, and ownership is this document's whole reason to exist. Derive nothing.

### 3.3 Knowledge bases consulted [BOTH]

| Knowledge base | Layer | Attached | What this document takes from it |
| --- | --- | --- | --- |
| `kb-L1-enterprise-architecture` | L1 enterprise | Yes | EA2/EA3 estate and integration boundaries (which legacy stores may be read, which must never be written back); EA4 "new services own their datastore, no shared database"; EA10 governance triggers; BP0–BP14 binding-principle catalogue and the BP11 resolution-file contract |
| `kb-L1-enterprise-security` | L1 enterprise | Yes | ES2 classification classes; ES3 retention and erasure; ES9 residency (an approved operating region, never a cloud region id); ES10 encryption, key management and attributable access |
| `kb-L1-nfr-classification-taxonomy` | L1 enterprise | Indirect | Read through `nfr_classifications.json`; the taxonomy the retention and availability classes came from |
| `kb-L2-domain-regulatory` / `kb-L1-regulatory-frameworks-index` | L2 domain / L1 index | Indirect | Read through the PRD's regulatory posture; the source of any retention obligation cited in DAT-3.2 |
| `kb-L2-[domain]` | L2 domain — **swappable** | Where deployed | Domain meaning of an entity: which records are *evidence* rather than application state, and therefore append-only |
| `kb-L3-[project]-application-baseline` | L3 project | **[BF]** only | The as-built entity set and de facto writers — evidence for Appendix A, never transcribed as intent |

**BP11 resolution rule.** When `binding-principles.json` is present, validate it *before* use against its own `validation_rules` (status `APPROVED`; today within `valid_until`; 5–15 principles; every principle has at least one non-placeholder conformance check; every `APPLIES`/`PARTIAL` principle has at least one hook; every `catalogue.abstraction_check == PASS`; every `TRANSITIONAL` exception has `due`, `exit_plan` and `remediation_owner`). A file that fails validation is **unusable input** — which is not the same as the product being non-conformant. Say which, and fall back. When the file is absent, fall back to the FSA § 4 PRIN rows and **record here that you did so**. Do not apply the whole catalogue as if every principle were MANDATORY; do not skip § 4 as if none were.

### 3.4 Demand coverage pre-check

Every REQ-DAT-\* and every CON-\* whose binding viewpoints include DAT is listed here on intake, so an unanswered demand is visible before DAT-7 is written rather than after.

| Demand / constraint | Source | Budget or rule stated in the FSA | Answered in |
| --- | --- | --- | --- |
| `[REQ-DAT-01]` | `[FSA § REQ-DAT]` | `[budget]` | `[DAT-n.n]` |
| *Example:* REQ-DAT-03 | FSA § REQ-DAT | Fee records immutable and retrievable for 10 years (REQ-07, tax audit) | DAT-3.2 retention + residency; DAT-9 (DAT-C3) |
| *Example:* REQ-DAT-07 | FSA § REQ-DAT | Registration status authoritative at point of sale — not cached (REQ-12) | DAT-1.1 (Identity sole owner); DAT-6 (deliberately no read model); DAT-9 (DAT-C2) |
| *Example:* CON-2 | FSA § CON | No context reads another context's store directly | DAT-1.b; enforced at PLT-3 Access Boundary; DAT-9 (DAT-C1) |

---

## 4. Principles Applied

One subsection per principle that binds DAT. State what the principle requires **of this product**, quoting the `program_guardrail` where the resolution supplies one — a principle restated in catalogue language has not been applied to anything.

| ID | Principle | Applicability | Binding level | Where it lands | Source |
| --- | --- | --- | --- | --- | --- |
| `[PRIN-nn]` | `[name]` | APPLIES / PARTIAL / NOT_APPLICABLE | MANDATORY / DIRECTIONAL / ADVISORY | `[DAT section ids]` | `binding-principles.json` / FSA § 4 |
| *Example:* PRIN-02 | One accountable owner and one authoritative source per data domain | APPLIES | MANDATORY | DAT-1.1 (13 entities, 4 owning contexts, Notifications owning none); DAT-1.2; DAT-6 (empty by decision, not by omission) | binding-principles.json |
| *Example:* PRIN-06 | Security and privacy are designed in | APPLIES | MANDATORY | DAT-3.2 (every PII / Financial / Regulated-Evidence row carries the ES2 · ES3 · ES9 triple); DAT-3.3; DAT-4.4 | binding-principles.json |
| *Example:* PRIN-03 | Integrate through governed, reusable interfaces | PARTIAL — the data-access half only; the contract half binds INT | MANDATORY | DAT-1.b; DAT-6 | binding-principles.json |
| *Example:* PRIN-01 | Business outcome before technology choice | APPLIES | DIRECTIONAL | DAT-4.3 (analytical plane NOT PRESENT with three triggers); DAT-8 (PRIN-01-C1) | FSA § 4 |
| *Example:* PRIN-07 | Prefer strategically approved platforms and managed services | APPLIES | MANDATORY | DAT-4.1 — the operational store is named here and checked against the approved catalogue and its lifecycle status | binding-principles.json |

### 4.[n] PRIN-[nn] — `[name]`

`[What this principle requires of this product, in this product's vocabulary. Quote the program_guardrail. Name the conformance check id it contributes — e.g. PRIN-02-C1 — and the DAT-Cn that carries it in DAT-9.]`

*Example — PRIN-02:* Every entity in the HarvestLink domain model has exactly one writing context. Guardrail as resolved for this product: *"No HarvestLink component writes an entity owned by another bounded context; a second writer is a boundary defect in APP-1, not a data-access convenience."* The two places it bit during authoring: Orders wanted to write `Listing.stock_on_hand` at order time (resolved — a Catalogue operation invoked through a contract, not an Orders write), and the reporting component wanted to write a denormalised `producer_status` (resolved — it reads through a contract, and would need a DAT-6 read model if it kept the value). Contributes `PRIN-02-C1` (BLOCKING), carried here as DAT-C1.

### 4.[n+1] Declared deviations and standing exceptions

A deviation from a **DIRECTIONAL** principle is a `DEV-xx` row here. A deviation from a **MANDATORY** principle is not a DEV row at all — it needs an approved `EXC-xx` in the resolution file, and this table only references it. Exceptions already approved in `binding-principles.json` are recorded as known drift: never re-litigated, never silently "fixed".

| ID | Principle | Where | Why | Compensating control | Review trigger / exit |
| --- | --- | --- | --- | --- | --- |
| `[DEV-01 / EXC-…]` | `[PRIN-nn]` | `[DAT section]` | `[reason]` | `[control]` | `[condition or exit date]` |
| *Example:* EXC-PRIN-02-001 (TRANSITIONAL) | PRIN-02 (MANDATORY — so an exception, never a DEV row) | DAT-6 | Group wholesale reporting reads the Producer store directly during the pilot; SMDS and HarvestLink producer records are not reconciled (EA8), and the reporting team has no contract to read | Read-only grant scoped to three columns; no write path; quarterly review; the grant is named in PLT-3 so PLT-C1 reports it rather than missing it | Exit 2026-12-31 — on the earlier of the reporting feed moving to the outbound aggregate path (EA3) or the exit date. Owner: Core IT |

---

# DAT-1 — Domain Entity and System-of-Record Architecture

## DAT-1.1 Bounded Context Ownership

One row per entity in the FSA's APP-3 aggregate model. **Every entity, exactly once.** Cross-check both directions before publishing: every APP-3 entity has a row here, and every row names a context that exists in APP-1. A context that owns no core domain entity is named explicitly below the table — a context missing from this section reads as an omission, not as a decision.

| Entity | Owning Context | Authoritative System of Record | Classification |
| --- | --- | --- | --- |
| `[Entity]` | `[APP-1 context name]` | `[owning context's persistence]` | `[DAT-3.1 class]` |
| *Example:* Listing | Catalogue | Catalogue persistence | Internal |
| *Example:* ListingImage | Catalogue | Catalogue persistence (metadata) + object store (binary, DAT-4.2) | Internal |
| *Example:* Order | Orders | Orders persistence | Confidential |
| *Example:* OrderLine | Orders | Orders persistence | Confidential |
| *Example:* Fee | Billing | Billing persistence | Financial / Regulated Evidence |
| *Example:* Payout | Billing | Billing persistence | Financial |
| *Example:* Producer | Identity | Identity persistence | PII |
| *Example:* FoodSafetyRegistration | Identity | Identity persistence | Regulated Evidence |

*Example:* Notifications owns no core domain entities — it is stateless and consumes events. It is listed here rather than omitted, because a context missing from this table is indistinguishable from one the agent forgot.

*Example — an ownership decision that was not obvious.* `FoodSafetyRegistration` was argued for Catalogue, since Catalogue is what blocks publication when a registration lapses. It went to Identity: the invariant the entity protects is *this party is who they claim to be and is permitted to trade*, which is Identity's, and the registration's validity is consumed by Billing and Orders too. Catalogue enforcing a rule is not Catalogue owning the fact.

**Where two contexts both appear to need write access**, that is a boundary problem in APP-1, not a data problem to be solved by allowing two writers. Record it as an open question against the FSA and assign the entity to the context whose invariant it protects.

## DAT-1.2 System-of-Record Rules

### DAT-1.a — Exactly One Writer

`[The rule, then a worked example listing two or three real entities and their owners, then the specific cross-context case this forbids for this product.]`

```text
[Entity]
    Owner: [Context]

[Entity]
    Owner: [Context]
```

*Example:*

```text
Listing
    Owner: Catalogue                 written by Catalogue only

Fee
    Owner: Billing                   written by Billing only; immutable once written

FoodSafetyRegistration
    Owner: Identity                  written by Identity only
```

*Example — the case this forbids for HarvestLink:* Orders may reference a Listing but may not become a second writer of it. A stock decrement at order time is a Catalogue operation invoked through a contract (INT-4.1), not an Orders write. The same rule is why Orders does not write `Fee`: it asks Billing for the figure at confirmation (INT-4.2) and stores the identifier of the fee record, not the amount.

### DAT-1.b — No Cross-Context Direct Database Access

`[The prohibited shape and the permitted shape, both as ASCII text diagrams.]`

```text
PROHIBITED
  [Context A] ──► [Context B store]        direct read or write

PERMITTED
  [Context A] ──► [contract owned by B] ──► [Context B] ──► [Context B store]
```

This is the data half of `PRIN-03-C2` (BLOCKING). The platform enforces it at the credential boundary (PLT-3 Access Boundary); this document states the rule the platform enforces.

## DAT-1.3 Logical Domain Relationships

`[A text diagram of business relationships between entities.]`

```text
[Entity A] ──has──► [Entity B]
[Entity C] ──references──► [Entity A]
```

*Example:*

```text
Producer ──publishes──► Listing ──has──► ListingImage
Buyer    ──places────► Order   ──has──► OrderLine ──references──► Listing
Order    ──results in─► Transaction ──has──► Fee
Producer ──holds─────► FoodSafetyRegistration

        │ context boundary crossed by:
        └── OrderLine → Listing        (Orders → Catalogue)
        └── Transaction → Order        (Billing → Orders)
        └── Listing → FoodSafetyReg.   (Catalogue → Identity)
```

Each of those three boundary-crossing lines is a *business* relationship and a *contract* obligation — they reappear as INT-4.1, INT-4.4 and INT-4.3. None of them is a foreign key.

These describe **business meaning only**. They do not imply foreign keys, and a relationship that crosses a bounded-context boundary never implies one.

## DAT-1.4 Cross-Context Reference Policy

A non-owning context may normally retain:

```text
entity identifier
```

*Example:* `OrderLine.listing_id` — Orders retains the identifier; Catalogue remains the owner of Listing. Orders does **not** retain `listing_title` or `listing_price`: the moment it does, it holds a value that can go stale without Catalogue knowing, and it owes a DAT-6 read model with a staleness budget.

*Example — the near-miss worth recording.* Orders asked to keep `fee_amount` on OrderLine so the confirmation screen would not need a call. Refused: REQ-07 requires the figure displayed to be the figure charged, and a cached fee is precisely the mis-selling risk the requirement exists to prevent. Had it been permitted, the honest staleness budget would have been zero — which is another way of writing "synchronous", and so it stayed synchronous (INT-4.2).

Any attribute beyond the identifier is a **replication**, and a replication requires a registered read model in DAT-6 with a named staleness budget. An unregistered copied attribute is the failure mode `PRIN-02-C2` exists to catch.

---

# DAT-2 — Event Data Architecture

## DAT-2.1 Canonical Event Envelope

All domain events carry a standard envelope, independent of the business payload.

```json
{
  "event_id": "uuid",
  "event_type": "[context].[entity].[event]",
  "event_version": "1.0.0",
  "occurred_at": "ISO-8601 timestamp",
  "producer_context": "[APP-1 context]",
  "correlation_id": "uuid",
  "payload": {}
}
```

`[State any additional envelope field this product requires, and why — e.g. a deduplication key derived from the business act for evidence-style events, or a buyer-side correlation identifier that must be carried end to end.]`

The envelope is this document's. **Topic naming, event kinds, versioning rules and delivery semantics are Integration's** (INT-3). Stating the envelope here and the taxonomy there is deliberate: the shape of the record is data, the routing of it is integration.

## DAT-2.2 Initial Event Register

Events the architecture already knows about at Cycle 0.

| Event | Owner | Purpose | Version |
| --- | --- | --- | --- |
| `[context].[entity].[event]` | `[context]` | `[why it exists]` | `Planned` / `Active` |
| *Example:* `catalogue.listing.published` | Catalogue | A listing became visible to buyers; drives search indexing and producer notification | Planned |
| *Example:* `orders.order.placed` | Orders | Hands a completed order to financial processing without gating capture on Billing's availability | Planned |
| *Example:* `identity.registration.verified` | Identity | Records that a producer's food-safety registration was checked and found valid — an assertion, not a state change | Planned |
| *Example:* `billing.payout.scheduled` | Billing | Tells Notifications a producer has money owed for a period | Planned |

*Example:* all four are `Planned` at Cycle 0 — the architecture recognises them, no producing feature has shipped. `identity.registration.verified` is the one to watch: it is an **evidence** event (INT-3.2), so its ordering, retention and replay policy differ from the other three even though the envelope is identical.

`Planned` means the architecture recognises the event; it becomes `Active` only when the feature that produces it lands.

## DAT-2.3 Event Ownership

The producing context owns the business meaning of its event. A consumer does not become an owner of the entity.

*Example:* `orders.order.placed` is owned by Orders. Billing consumes it, creates a Transaction and a Fee from it, and does not thereby become an owner of Order — if the meaning of "placed" changes, Orders changes it and versions the contract (INT-3.3). Billing cannot redefine it, and Billing cannot emit it.

---

# DAT-3 — Classification, Retention and Residency

## DAT-3.1 Classification Model

The classes this product uses, taken from `kb-L1-enterprise-security` ES2 and extended only where the product genuinely needs a class the standard does not name.

| Classification | Meaning |
| --- | --- |
| `[class]` | `[meaning]` |
| *Example:* Public | Safe for public disclosure |
| *Example:* Internal | Internal operational information |
| *Example:* Confidential | Sensitive to a specific party |
| *Example:* PII | Personally identifiable information |
| *Example:* Financial | Financially sensitive information |
| *Example:* Regulated Evidence | Must be preserved, append-only, for audit or dispute |

## DAT-3.2 Data Classification Register

**The same entity set as DAT-1.1, in the same order.** Resolve classification from ES2, retention from ES3 and the regulatory posture, residency from ES9.

| Entity | Classification | Retention | Residency |
| --- | --- | --- | --- |
| `[Entity]` | `[class]` | `[period + source]` / `PENDING` | `[approved operating region]` / `PENDING` |
| *Example:* Listing | Internal | Business lifecycle; no regulatory obligation | Approved operating region |
| *Example:* Fee | Financial / Regulated Evidence | 10 years — PRD regulatory posture (tax audit). This **exceeds** the 6-year group floor in ES3; where two sources give different periods the longer obligation prevails and both are named, so a later reader can see the 6-year figure was considered, not missed | Approved financial-data region (ES9) — and must not be replicated outside it, including into an analytical plane, without an approved exception |
| *Example:* Payout | Financial | 6 years from creation (ES3, trade record) | Approved financial-data region |
| *Example:* FoodSafetyRegistration | Regulated Evidence | 6 years from creation (ES3); append-only — a lapsed registration is superseded, never overwritten, because a dispute asks what was true on the day of sale | Approved PII region — UK or an adequacy jurisdiction (ES9) |
| *Example:* Producer | PII | UK GDPR erasure honoured for the personal-data population **not** held under the ES3 6-year obligation. The two populations are distinct and handled distinctly — never a blanket "delete everything" or "retain everything" | Approved PII region (ES9) |
| *Example:* Order | Confidential | `PENDING` — DAT-PEND-02. ES3 covers trade and compliance records; a transactional order record is neither, and the regulatory posture does not supply a period. A plausible "7 years" here would be an invention | Approved operating region |

**Rules that make this table trustworthy:**

- Residency is an **approved operating region** — a policy name (ES9). Never a datacentre, availability zone or cloud region id; that is PLT's realisation.
- Backups, DR copies, log exports and analytical replicas **inherit** the residency of the source entity. A copy is not a new decision, and a residency rule that the backup breaks was never in force.
- A value the cited standards answer is grounded and MUST be stated. A value they do not answer is `PENDING` with a matching DAT-PEND row and a trigger. Never a plausible period; never a default region.
- Every entity classified PII, Financial, Confidential or Regulated Evidence needs **all three** cells resolved or explicitly pending — that triple is what `PRIN-06-C1` (BLOCKING) evaluates.

## DAT-3.3 Encryption Requirement

`[State the requirement for the protected classes, per ES10.]`

```text
encryption at rest
encryption in transit
keys held in the group managed key capability — never application-held, never committed
key rotation without redeploying unrelated consumers
access attributable to a named principal — a shared service account fails attribution
```

**The boundary:** this document states the *requirement* and the classes it applies to. The Platform Architecture (PLT-10) determines the technical realisation. Naming a key-management product here is a scope error.

---

# DAT-4 — Data Planes and Lineage

## DAT-4.1 Operational Data Plane

**Decision:** `[REQUIRED | NOT PRESENT]`

`[Purpose, and the technology chosen. This document MAY name a technology — the FSA may not. State the PRIN-07 check outcome explicitly: is the product in the approved catalogue, and is its lifecycle status outside contain/retire?]`

*Example:* HarvestLink's operational plane is a managed relational capability, one instance, one schema per context. PRIN-07 check — present in the approved catalogue, lifecycle status `invest`, so outside `contain`/`retire`. Passes `PRIN-07-C1`. The group data warehouse was explicitly **not** considered here: it is a reporting destination (DAT-4.4), not an operational store, and EA3 makes that feed outbound-only.

**Ownership model.** Each context maps to its own schema:

```text
[Context] ──► [context schema]
[Context] ──► [context schema]
```

A schema is platform infrastructure. **Provisioning a schema does not transfer domain ownership** — ownership is DAT-1.1, and nothing else changes it.

## DAT-4.2 Object Data

`[Which binaries are not stored as relational blobs, and what holds the business metadata and reference. Omit this subsection entirely if the product has no object data.]`

```text
[Context]
   ├── metadata + reference ──► [context schema]
   └── binary               ──► [object capability]
```

## DAT-4.3 Analytical Plane

**Status:** `[REQUIRED | PENDING | NOT PRESENT]`

`[If not required at Cycle 0, say so plainly — a plane is not created because it may eventually be useful — then give the decision trigger as a numbered list of conditions, any one of which reopens the decision.]`

*Example:* NOT PRESENT at Cycle 0. No requirement in the PRD needs a query that a single context cannot answer, and a plane built now would be a platform with data in it and nobody accountable for the numbers. The decision reopens on any one of:

1. A requirement needs cross-context aggregate reporting no single context can answer — for instance "fee revenue by producer region by month", which spans Billing, Identity and Catalogue.
2. Reporting query load begins to affect a transactional latency budget — concretely, when reporting traffic threatens REQ-07's p95 ≤ 400 ms fee read (INT-4.2).
3. The outbound group reporting feed is committed (EA3 — one-way, aggregate, non-PII).

*Example — the constraint that survives the deferral:* whenever this plane is built, Fee and Payout may not be replicated into it outside the approved financial-data region, and no PII crosses into it at all (ES9, DAT-4.4). Deferring the plane does not defer its residency rule.

A deferral with no trigger is a silence, and `PRIN-01-C1` fails it.

## DAT-4.4 Lineage

For every flow that crosses a plane boundary or a context boundary:

| Flow | Source owner | Destination | What may cross | What may not | Residency constraint |
| --- | --- | --- | --- | --- | --- |
| `[flow]` | `[context]` | `[plane / context]` | `[fields or classes]` | `[fields or classes]` | `[the ES9 rule that applies]` |
| *Example:* Aggregate metrics → enterprise DW | All contexts | Group data warehouse (EA3, outbound-only, no read dependency back) | Aggregate, non-PII counts: orders per period, listings published, fee revenue in total | Any PII field; any individual Fee, Payout or Producer record; any registration evidence | Financial records must not leave the approved financial-data region, including into this feed, without an approved exception (ES9) |
| *Example:* ListingImage binary → object store | Catalogue | Object capability (DAT-4.2) | The binary and its content hash | Any buyer or producer identifier embedded in the object path | The object store and its backups inherit Catalogue's approved operating region — a copy is not a new decision |
| *Example:* Fee → backup and DR copy | Billing | Platform backup capability (PLT-14) | The whole record | — | Inherits the approved financial-data region. A DR region chosen on availability grounds alone would break a residency rule that was in force |

---

# DAT-5 — Consistency Model

## Inside One Context

`[What may use strong transactional consistency, with a worked example showing one transaction boundary.]`

```text
BEGIN
  [write entity A]
  [write entity B]        both owned by the same context
COMMIT
```

*Example:*

```text
BEGIN                          Billing, one transaction boundary
  write Transaction
  write Fee                    immutable once written
COMMIT
```

A Transaction without its Fee is not a state the business recognises — that is the invariant which makes them one aggregate and keeps them in one context. Order and OrderLine are the same case inside Orders.

## Across Contexts

Distributed database transactions are **not** the default integration mechanism for this product.

`[A worked example showing where eventual consistency results, and which context becomes eventually consistent with which — named explicitly, because "eventually consistent" without a direction is not a decision.]`

*Example:* `orders.order.placed` is published by Orders and consumed by Billing (INT-4.4). **Billing's view of a given order is eventually consistent with Orders'** — stated with a direction, because "eventually consistent" without one names no decision. For a short window an order exists in Orders with no Transaction in Billing; that window is acceptable precisely because REQ-07's fee was already resolved synchronously at confirmation (INT-4.2), so nothing a buyer has been shown depends on Billing having caught up.

*Example — the contrast that makes the rule legible:* the same product refuses eventual consistency for the confirmation-time fee and for publication eligibility (REQ-12). In both, the caller cannot complete its own transaction without the answer, so the propagation is synchronous and there is no window to reason about.

---

# DAT-6 — Read Models and Replication Register

| Read Model | Source Owner | Consumer | Staleness Budget | Status |
| --- | --- | --- | --- | --- |
| `[name]` | `[owning context]` | `[consuming context]` | `[budget + source]` / `PENDING` | `Planned` / `Active` |

*Example:* `None at Cycle 0.` Two candidates were considered and both were refused, which is why this table is empty by decision rather than by omission:

| Candidate | Wanted by | Refused because |
| --- | --- | --- |
| `fee_amount` on OrderLine | Orders — to render confirmation without a call | REQ-07 needs the figure charged, not a figure; an honest staleness budget would be zero (DAT-1.4) |
| `producer_status` in Catalogue | Catalogue — to avoid checking registration on every publish | REQ-12 needs validity at the point of sale; a cached status lets an unregistered producer sell (INT-4.3) |

*Example of what would qualify:* a buyer-facing "producer rating" surfaced in Catalogue and owned by Identity would be a legitimate read model — nobody is refused or charged on the strength of it — and it would enter this table with an explicit staleness budget before a line of code used it.

`None at Cycle 0` is a valid and common content. Follow the table with the standing rule: **any future replicated attribute must be entered here, with a staleness budget, before it is used.** A copied attribute that is not in this register is exactly the drift `PRIN-02-C2` reports.

---

# DAT-7 — Data Architecture Demand Traceability

One row per REQ-DAT-\*, per CON-\* binding DAT, and per principle applied. Every one. An unanswered demand becomes an open question, never an omitted row.

| FSA Demand / Principle | Data Architecture Satisfaction |
| --- | --- |
| `[REQ-DAT-nn / CON-n / PRIN-nn]` | `[DAT section id + one line saying how]` |
| *Example:* REQ-DAT-03 (fee immutability, 10 yr) | DAT-3.2 classifies Fee as Financial / Regulated Evidence, retention 10 years with both sources named, residency the approved financial-data region; DAT-5 keeps Transaction and Fee in one transaction boundary so a fee is never written without its transaction; DAT-C3 checks the triple |
| *Example:* REQ-DAT-07 (registration authoritative at point of sale) | DAT-1.1 gives Identity sole ownership; DAT-6 records the refusal to cache it and why; DAT-C2 fails any later copy that appears without a read-model row |
| *Example:* CON-2 (no cross-context store access) | DAT-1.b states the rule; DAT-C1 checks the writer count and PLT-3 Access Boundary is the mechanism that makes it true rather than aspirational |
| *Example:* PRIN-06 | DAT-3.2 (the ES2 · ES3 · ES9 triple on every protected entity); DAT-3.3 (encryption requirement, realised at PLT-10); DAT-4.4 (residency inherited by every copy) |

---

# DAT-8 — Pending Decisions

| ID | Decision | Status | Trigger |
| --- | --- | --- | --- |
| `DAT-PEND-nn` | `[what is not yet decided]` | `PENDING` | `[the condition that reopens it]` |
| *Example:* DAT-PEND-01 | Analytical plane — whether one exists, and what realises it | PENDING | Any one of the three DAT-4.3 conditions fires. Referenced from DAT-4.3 |
| *Example:* DAT-PEND-02 | Order retention period | PENDING | The regulatory posture, an NFR classification, or a dispute-handling requirement supplies a retention obligation for transactional order records. Referenced from DAT-3.2 |
| *Example:* DAT-PEND-03 | Session retention and erasure | PENDING | The external identity provider's session policy is agreed with the security team (ES1, ES5). Referenced from DAT-3.2 |

*Example of a trigger that would be rejected at review:* "revisit the analytical plane in Q3". That is a calendar entry — nobody fails a check by ignoring it, and the impact assessor cannot evaluate it. "When a requirement needs cross-context aggregate reporting" is a condition the assessor tests on every cycle.

**A trigger is a condition, never a date.** "Revisit in Q3" is a calendar entry; "when a requirement needs cross-context aggregate reporting" is a trigger the impact assessor can evaluate mechanically.

Every `PENDING` anywhere in this document has a row here, and every row here is referenced from the section that defers it.

---

# DAT-9 — Conformance Checks

One subsection per check, each expressed so a checker can evaluate it — not as prose. Cover at minimum: one writer per entity; no unregistered replication; protected data has classification **and** retention **and** residency.

### DAT-C1 — One Writer Per Entity

```text
for each entity in DAT-1.1:
    count(writing_contexts) == 1
severity: BLOCKING            source: PRIN-02-C1
```

### DAT-C2 — No Unregistered Replication

```text
for each attribute held by a context that does not own its entity:
    attribute == entity_identifier
    or exists read_model in DAT-6 with staleness_budget
severity: MAJOR               source: PRIN-02-C2
```

### DAT-C3 — Protected Data Has Governance

```text
for each entity in DAT-3.2 where classification in
        [PII, Financial, Confidential, Regulated Evidence]:
    exists classification and exists retention and exists residency
    or exists DAT-PEND row with trigger
severity: BLOCKING            source: PRIN-06-C1
```

### DAT-C[n] — `[additional check this product needs]`

```text
[evaluable expression]
severity: [BLOCKING | MAJOR | MINOR]    source: [principle check id]
```

---

# DAT-10 — Change Model

Feature cycles do **not** rewrite this document. They emit a delta:

```json
{
  "target_document": "data-architecture.md",
  "from_version": "1.0",
  "changes": [
    {
      "type": "add_entity | change_classification | register_read_model | resolve_pending",
      "section": "DAT-1.1",
      "content": "[the change]"
    }
  ],
  "version_bump": "minor | major",
  "structural": false,
  "adr_required": false
}
```

The transition: a delta is merged only after the feature that motivated it is merged and verified. The merge raises the version per the rule in § 1, appends a version-history row, and re-runs DAT-9. A `structural: true` delta — an ownership move, a new plane, a classification downgrade — requires an ADR and the Enterprise Architect gate before merge.

---

## Version History

| Version | Change |
| --- | --- |
| 1.0 | Initial Cycle 0 `[product]` Data Architecture |

---

## Appendix A — Brownfield reconciliation [BF]

Present only in `BROWNFIELD-RETROFIT`, or where a delta reconciles known drift. The baseline tells you where the data *is*; it must never be transcribed as where it *should be*.

### A.1 Recovery method

`[What was read — application-baseline.md, data-model-overview.md, live schema, grant tables — and at what commit or export date.]`

### A.2 Divergence register

| DAT section | Target says | Baseline shows | Classification | Resolution |
| --- | --- | --- | --- | --- |
| `[DAT-1.1]` | `[intended owner]` | `[actual writers]` | Drift / Accepted exception / Target error | `[remediation or EXC id]` |
| *Example:* DAT-1.1 Producer | Identity is sole writer | Onboarding and a legacy admin tool both write `producer` | Drift — BLOCKING (PRIN-02-C1) | Remediation epic. No exception is available: PRIN-02 is MANDATORY, and a TRANSITIONAL exception would encode the violation as intent |
| *Example:* DAT-3.2 FoodSafetyRegistration | Append-only, 6-year retention | Rows updated in place; no history | Drift — BLOCKING | Remediation before first external onboarding; a dispute about what was true on the day of sale is unanswerable from the current shape |
| *Example:* DAT-6 | No read models registered | Reporting holds a copy of `producer_status` | Accepted exception — EXC-PRIN-02-001 | Already approved and recorded in § 4; entered here as known drift, not re-litigated and not silently fixed |

### A.3 Legacy decisions adopted into the target

`[Decisions the target deliberately keeps, with the reason. A decision adopted without a reason is drift that has been renamed.]`

### A.4 Known violations not to be encoded as intent

`[From binding-principles.json brownfield.principle_posture. These stay visible as violations; a retrofit that writes them into DAT-1 has laundered them.]`

---

## Appendix B — Authoring agent self-check and quality gate

### B.1 Content boundary — BLOCKING

- [ ] No `CREATE TABLE`, column type, index, migration, ORM class or SQL anywhere in the document.
- [ ] No runtime, sizing, backup or cluster configuration (that is PLT).
- [ ] No topic name, contract version, endpoint path or retry policy (that is INT).
- [ ] Ownership is assigned to bounded contexts only — never a team, a service name or a database.

### B.2 Completeness — BLOCKING

- [ ] Every APP-3 entity appears exactly once in DAT-1.1; no entity has two owning contexts.
- [ ] Every DAT-1.1 row names a context that exists in APP-1; every APP-1 context is accounted for, including those owning nothing.
- [ ] DAT-3.2 covers the same entity set as DAT-1.1, in the same order.
- [ ] Every PII / Financial / Confidential / Regulated-Evidence row has classification **and** retention **and** residency, or a `PENDING` with a DAT-PEND trigger.
- [ ] Every REQ-DAT-\* and every DAT-binding CON-\* has a DAT-7 row.
- [ ] Every `PENDING` has a trigger; every DAT-PEND row is referenced from the section that defers it.
- [ ] DAT-9 contains at least DAT-C1, DAT-C2 and DAT-C3, each as an evaluable expression.

### B.3 Grounding — BLOCKING

- [ ] No retention period, residency region or staleness budget appears that no cited source supports.
- [ ] Every classification traces to ES2, every retention to ES3 or the regulatory posture, every residency to ES9.
- [ ] Any technology named in DAT-4 has its PRIN-07 lifecycle check stated, with the outcome.
- [ ] If `binding-principles.json` was absent or failed validation, § 4 says so and names the fallback source — and distinguishes *unusable input* from *non-conformant product*.

### B.4 Quality — review findings

- [ ] Ownership decisions that were not obvious carry a stated reason (which invariant the entity protects).
- [ ] The analytical plane is not created speculatively, and its deferral has real trigger conditions.
- [ ] Text diagrams are plain ASCII in fenced `text` blocks.
- [ ] Guardrails evaluated and recorded: `gr-L1-schema-validator`, `gr-L1-pii-detection`; downstream `gr-L1-architecture-conformance`.

### B.5 Anti-patterns the reviewer looks for

| Anti-pattern | Why it fails |
| --- | --- |
| Two writers "for now" | The BLOCKING failure this document exists to prevent; it is never removed later |
| A plausible retention period | An invention with a citation-shaped wrapper; `PENDING` is the honest answer |
| Residency stated as a cloud region id | Confuses the policy with its realisation (ES9); the platform picks the region, not the data architect |
| Ownership assigned to a service or a team | Services get renamed and teams get reorganised; bounded contexts are the stable unit |
| An analytical plane "because we will want reporting" | A plane created before a requirement is a platform nobody owns |
| A read model appearing in a feature cycle with no DAT-6 row | Unregistered replication — invisible staleness, and drift by construction |
