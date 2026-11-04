<!--
kb-L0-architecture-patterns · content · architecture-patterns.md
Layer: L0 (enterprise-wide, cross-phase — NOT domain-specific).
The enterprise's catalogue of binding architecture principles and the
sanctioned patterns that realise them. Grounds L0-binding-principles-generator
(which resolves every principle in AP2 against a product's PRD) and
L0-target-architecture-generator (which applies the patterns in AP3 and the
decision rules in AP4 when drawing bounded contexts, context maps, invariants,
constraints and demands). Enterprise system landscape lives in
kb-L0-enterprise-architecture; security and compliance standards live in
kb-L0-enterprise-security — neither is duplicated here. Illustrative content
for the Thornbury Foods Group reference scenario.
-->

# Thornbury Foods Group — Architecture Principles and Patterns

## AP1: How this catalogue is used

- **Principles (AP2) bind; patterns (AP3) realise.** A principle is a rule every
  new digital product must satisfy or record a deviation against. A pattern is
  a sanctioned way of satisfying one or more principles. A product may use a
  pattern not listed here, but it may not break a principle listed here
  without a recorded deviation (AP4.3).
- **Two kinds of principle.** *Decomposition-shaping* principles are applied in
  a product's target architecture (the technology-free statement of what the
  system is). *Technology-selecting* principles are applied in its solution
  architecture. A target architecture records a technology-selecting principle
  as "applied in solution architecture", never as "satisfied".
- **Every normative statement carries a stable key.** Principles use
  `L0-{FAMILY}-NN`; patterns use `PAT-NN`; decision rules use `RULE-NN`.
  Product documents cite these keys rather than restating the text.

## AP2: Binding principle catalogue

| ID | Family | Principle | Statement | Kind | Source | Deviation permitted? |
|---|---|---|---|---|---|---|
| **L0-ARCH-01** | Architecture | Decompose by domain | Decompose the system by business domain into DDD bounded contexts. Each context owns its entities, has its own model and language, and is realised by exactly one independently deployable service with its own datastore. | Decomposition-shaping | kb-L0-enterprise-architecture EA4 ("API-first, microservices"; "independently deployable, own datastore") | Yes, recorded |
| **L0-ARCH-02** | Architecture | Prefer event-driven integration | Integration between bounded contexts is event-driven by default: the owning context publishes a fact and does not wait for consumers. A synchronous request between contexts is the exception and must be named, budgeted and justified. | Decomposition-shaping | Group integration standard; kb-L0-enterprise-architecture EA4 ("never direct database-to-database") | Yes, recorded, bounded to named flows |
| **L0-ARCH-03** | Architecture | API-first | Every integration, request or event, is a published, versioned, consumer-verified contract. Any service exposed beyond its own boundary publishes through the group API Gateway, never point-to-point. | Decomposition-shaping | kb-L0-enterprise-architecture EA2 (API Gateway mandatory), EA4 | No for the contract rule; gateway routing deviations recorded |
| **L0-ARCH-04** | Architecture | Standard relational store | PostgreSQL is the standard relational store for new digital products. Another store is used only where a documented workload characteristic (search, immutable archive, analytics, object storage) is outside a relational store's fit. | Technology-selecting | Group technology standard | Yes, recorded per store |
| **L0-DATA-01** | Data | One system of record per entity | Every business entity has exactly one system of record. No other component stores, recomputes or caches an authoritative value of that entity; copies exist only as a registered snapshot (PAT-07) or a registered analytical read model (PAT-08). | Decomposition-shaping | kb-L0-enterprise-architecture EA3 (SMDS and ERP are read-only / not written), EA8 (fragmented supplier identity is a known defect) | No |
| **L0-SEC-01** | Security | No long-lived credentials | No long-lived credential exists in any runtime or pipeline. Workloads authenticate with short-lived workload identity; secrets that must exist live in the group secrets vault and are never committed or hardcoded. | Decomposition-shaping (stated as a required control in the target architecture; the mechanism is chosen in the solution architecture) | kb-L0-enterprise-security ES5 | No |
| **L0-SEC-02** | Security | Classification drives controls | Every entity carries a data classification (ES2) and a retention period per record type (ES3). Classification determines encryption at rest, residency, access-grant policy and audit logging. | Decomposition-shaping | kb-L0-enterprise-security ES2, ES3, ES4 | No |

### AP2.1 Rules that are binding but carried under a principle above

| Enterprise rule | Where stated | Carried under |
|---|---|---|
| New services are independently deployable, with their own datastore; no shared database with legacy systems | EA4 | L0-ARCH-01 |
| Cross-system integration is via Group ESB or API Gateway, never direct database-to-database | EA4 | L0-ARCH-02, L0-ARCH-03 |
| Legacy systems are read-only where touched; writes need Enterprise Architecture review | EA4, EA10 | L0-DATA-01 |
| External parties use a separate, group-approved external identity provider; internal AD is never extended to them | ES1 | L0-SEC-01 (identity boundary), realised as a single identity authority (PAT-13) |
| Server-side enforcement cannot be bypassed by altering a client request | ES1 | PAT-11 (experience components hold no business rule) |
| A new system's availability tier is stated explicitly, never inherited | ES4 | L0-SEC-02 (classification implies tier) |

## AP3: Pattern catalogue

Each pattern states its intent, when to use it, what a target architecture
must state when it applies, and which principles it serves.

| Key | Pattern | Intent | Use when | Target architecture must state | Serves |
|---|---|---|---|---|---|
| **PAT-01** | Bounded context by reason-for-change | Draw a boundary around things that change for the same reason, on the same clock, under the same approval | Always, for decomposition | For each context: subdomain type (core / supporting / generic), purpose, owned entities, published events, boundary (what it explicitly does not own), rationale | L0-ARCH-01 |
| **PAT-02** | Context map relationship types | Make every dependency between contexts explicit, with its DDD relationship type | Whenever two contexts interact | For each relationship: asking/consuming context, answering/publishing context, type (customer-supplier, conformist, open host service, published language, anti-corruption layer), interaction (request or event), consistency (current / eventual with a bound) | L0-ARCH-01, L0-ARCH-02 |
| **PAT-03** | Event-carried fact publication | The owner publishes an immutable fact; consumers react without the owner waiting | Any cross-context interaction that is not inside a user's action | Event name, publisher, consumers, end-to-end latency bound, delivery guarantee (at-least-once, ordered per entity, replayable) | L0-ARCH-02, L0-ARCH-03 |
| **PAT-04** | Budgeted synchronous request | A request to another context, permitted only inside a user's action where a stale answer would be visible or disputable | Only under RULE-01 | Asking and answering context, p95 latency budget, failure mode (fail-closed or degrade), the invariant or constraint it protects, the deviation record it falls under | L0-ARCH-02 (as deviation), L0-ARCH-03 |
| **PAT-05** | Fail-closed versus degrade | Decide the failure mode of every request from what it protects | Every PAT-04 request | A request protecting a regulatory or financial invariant fails closed and preserves the user's in-flight state; a request that only improves a display degrades with the reduced information explicitly marked | L0-ARCH-02 |
| **PAT-06** | Single system of record | Exactly one context owns each entity and is the authority on its value | Always | A canonical entity list with its owning context; the rule that a value owned elsewhere is obtained through the owner's contract and never recomputed locally | L0-DATA-01 |
| **PAT-07** | Transactional snapshot | A context captures another context's value once, at the moment of an event, as part of an immutable record, and never reconciles it with the source | A price, rate, title or term that forms part of a record of an event (an order, an invoice) | A snapshot register: each snapshot's holder, owner, value captured, capturing event. The explicit distinction from a replicated attribute, which tracks its source and is a defect | L0-DATA-01 |
| **PAT-08** | Registered analytical read model | Cross-context joins happen only in a separate analytical plane, in a derived model owned by one context, with a declared freshness | Reporting, statements, returns, dashboards | For each read model: owner, source contexts, freshness SLA surfaced to consumers, and the rule that it is never a source of truth and never read by an operational path | L0-DATA-01 |
| **PAT-09** | Immutable ledger with compensating entries | Financial and regulatory records are written once; corrections are new entries that reference the original | Fees, transactions, payouts, invoices, attestations, sign-offs | The immutable aggregates, the correction mechanism (compensating entry, credit note), retention period per record type, and a storage demand for demonstrable immutability no operator can override | L0-SEC-02 |
| **PAT-10** | Effective-dated reference data | Policy values that change on a statutory or commercial clock are stored with validity windows so the value in force at any past time is reproducible | Tax rates, fee rate cards, compliance rules, registration validity | The effective-dated entities, the reproducibility invariant, retention aligned to the records that reference them | L0-DATA-01, L0-SEC-02 |
| **PAT-11** | Thin experience components | Web and mobile experiences hold no business rule that is not also enforced server-side | Every user-facing component | Each experience component listed with "any business rule not enforced server-side" as an explicit non-responsibility | ES1 (server-side enforcement) |
| **PAT-12** | Idempotent command | A command that creates a record is idempotent on a caller-supplied key, so a repeated request returns the original result | Order placement, payment capture, registration, any create behind an unreliable network | The idempotency key per command and the aggregate invariant that enforces it | L0-ARCH-03 |
| **PAT-13** | Single identity authority, trust boundary at the edge | One context is the authority on who someone is and what they may do; every service verifies the caller itself and trusts no other service's claim | Always | Identity as upstream of every context; no context implements its own authentication; external parties on the group-approved external identity provider | L0-SEC-01, ES1 |
| **PAT-14** | Stateless generic context | A context that solves a common problem (notifications, document rendering) owns no entity and holds no state, so it can be retried, replayed or replaced | Generic subdomains | "Owns nothing" declared explicitly; the publishing context decides what is noteworthy, the generic context only delivers | L0-ARCH-01 |
| **PAT-15** | Scheduled job with single-execution guarantee | Batch work runs on behalf of a context with retry, exactly-one-run per period, and detection of a run that did not happen | Statements, returns, expiry sweeps, reconciliations | A platform demand naming the guarantee; a platform component (job runner) that owns no entity and no business rule | L0-ARCH-01 |
| **PAT-16** | Evidenced outbound delivery | A document whose delivery is a legal obligation is sent through a channel that returns evidence of delivery, retained with the document | Invoices, statutory notices, breach notifications | A platform demand for evidenced delivery and the record that holds the evidence | L0-SEC-02 |
| **PAT-17** | Latency budget allocation | A user-facing operation has one end-to-end p95 budget, split across its synchronous dependencies; adding a dependency re-splits the budget, it never grows it | Any operation with PAT-04 requests | The quality attribute (QA) for the operation, each dependency's share, and where it is measured | L0-ARCH-02 |
| **PAT-18** | Classification-driven data controls | Every entity's classification (Public, Internal, Confidential, Restricted; plus the product's own regulatory classes such as PII, Financial, Regulatory) selects its encryption, residency, access and retention | Always | A classification and retention policy per entity as a data demand; security controls keyed to classification | L0-SEC-02 |

## AP4: Decision rules

### AP4.1 Request or event (RULE-01)

| Condition | Interaction | Consistency |
|---|---|---|
| The answer is needed inside a user's action **and** a stale answer would be visible to the user or open to dispute (a price, a tax rate, a seller's standing, a fee shown before confirmation) | Request (PAT-04), named individually, budgeted (PAT-17), failure mode declared (PAT-05) | Current |
| The answer is needed inside a user's action but a stale or absent answer is acceptable if marked (an estimate, a recommendation, a display-only figure) | Request that degrades, or a local projection explicitly marked as such | Current where available |
| Everything else: a fact that other contexts react to after it has happened (order placed, fee recorded, document expiring, payout scheduled) | Event (PAT-03) | Eventual, within a stated bound |

A request that would require the asking context to hold a replicated copy of
another context's attribute is not an alternative to the request; the copy
breaks L0-DATA-01.

### AP4.2 One context holding another's data (RULE-02)

| Need | Sanctioned mechanism | Not permitted |
|---|---|---|
| A value that forms part of an immutable record of an event | Transactional snapshot (PAT-07), registered | An unregistered copy |
| A cross-context join for reporting, statements, returns | Registered analytical read model (PAT-08) | A join in an operational path; a value that exists only in the analytical plane |
| A current value for display or decision | The owner's published contract (PAT-06) | Recomputing or inferring the value locally |
| A searchable projection of the owner's own data | A derived, rebuildable projection inside the owning context | A projection that other contexts write to |

### AP4.3 Recording a deviation (RULE-03)

A deviation from a principle in AP2 is permitted only when all four fields are recorded against that principle:

| Field | Content |
|---|---|
| Principle | The `L0-...` key deviated from |
| Scope | The named flows, contexts or stores the deviation covers, and no others. "All inter-context communication" is not a scope |
| Rationale | Why the principle cannot be satisfied for this scope, citing the requirement (FR, NFR boundary condition or constraint) that forces it |
| Approver | The role that approved it (Enterprise Architect for decomposition-shaping principles; Solution Architect with Enterprise Architect for technology-selecting ones) |

An unrecorded deviation is a defect. A deviation is bounded: a new flow of the
same kind needs its own entry, not an extension of the existing scope.

### AP4.4 Verdicts a principle resolution may carry (RULE-04)

| Verdict | Meaning | Required fields |
|---|---|---|
| `satisfied` | The product's requirements can be met while honouring the principle; the pattern(s) that will realise it are identified | evidence, pattern(s) |
| `deviation-required` | A requirement makes full compliance impossible or harmful; a bounded deviation is recorded | rationale, deviation_scope, approved_by (or "pending"), evidence |
| `applied-in-solution-architecture` | Technology-selecting; cannot be assessed from requirements and a target architecture; resolved when technology is chosen | the demand(s) it will be assessed against |
| `at-risk` | Satisfiable in principle, but a gap or open question in the requirements threatens it | the open question that must be answered |
| `not-applicable` | The principle has no subject in this product | reasoning |

### AP4.5 Conformance states (RULE-05)

At each release every normative item is reported as **Conformant**, **Not yet
built** or **Deviating**. *Not yet built* is roadmap visibility; *Deviating*
is a defect logged in the deviation register with an owner and a removal date.
A deviation is never legitimised by an architecture decision record.

## AP5: Anti-patterns

| Anti-pattern | Why it is rejected | Principle broken |
|---|---|---|
| Shared database between contexts or with a legacy system | Couples change cadences; one schema change redeploys several contexts | L0-ARCH-01, EA4 |
| Boundary drawn by team size, effort or convenience | Effort is never the test for a boundary; reason-for-change is | L0-ARCH-01 |
| Chatty synchronous chain across three or more contexts in one user action | The budget cannot be met and a single failure fails the whole action | L0-ARCH-02, PAT-17 |
| Dual write (a context updating its own store and another context's) | Two sources that will disagree; no single owner | L0-DATA-01 |
| Recomputing a value owned elsewhere (a fee, a tax, an earnings figure) | Silent re-implementation of another context's rules, which drift | L0-DATA-01, PAT-06 |
| Undeclared cross-context copy | Indistinguishable from a snapshot in storage; only the register tells them apart | L0-DATA-01, PAT-07 |
| Operational read from the analytical plane | A consumer cannot tell staleness from absence | PAT-08 |
| Updating a financial record in place | The auditor must see what was recorded at the time | PAT-09, L0-SEC-02 |
| Business rule enforced only in the client | Bypassable by altering the request | ES1, PAT-11 |
| A service trusting another service's identity claims | Lateral movement across the trust boundary | PAT-13, L0-SEC-01 |

## AP6: Glossary

- **Bounded context** — a part of the domain with its own model, language and owned entities, realised by one service.
- **Subdomain type** — *core* carries the business model and receives the most design attention; *supporting* is specific to the domain but not differentiating; *generic* solves a common problem and is a candidate for a standard product.
- **Fail closed / degrade** — on dependency failure, *fail closed* refuses the action and preserves in-flight state; *degrade* completes it with reduced or explicitly marked information.
- **Transactional snapshot** — a value captured once from another context at the moment of an event and never reconciled afterwards.
- **Replicated attribute** — a copy of another context's value intended to stay current; a defect unless it is a registered snapshot or read model.
- **Analytical plane** — storage and processing separate from the operational plane, hosting registered read models only.
- **Effective-dated** — stored with a validity window so the value in force at any past moment can be reconstructed.
- **Deviation** — a recorded, bounded, approved departure from a principle in AP2.

---
*Last reviewed: 2026-11-04 · Review cadence: quarterly (patterns and decision
rules change as the group's integration platform matures; the principle
catalogue changes only through Enterprise Architecture governance).*
