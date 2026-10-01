<!--
kb-L1-enterprise-architecture · content · binding-principles.md
Layer: L1 (enterprise-wide, cross-phase). The enterprise architecture
principle CATALOGUE — the durable, product-independent half of the binding
principles. The per-product RESOLUTION (which principles bind THIS product,
at what level, with which exceptions) is NOT here: it lives in a
binding-principles.json produced against binding-principles.template.json
and supplied to an agent as an input, never as KB content. BP9 below is the
contract for that file.

Illustrative content for the reference scenario (Thornbury Foods Group).
Not a real company's catalogue. The SHAPE — nine-field entries, binding
levels, conformance checks, hooks, precedence rules — is the reusable part;
the specific principles are replaced when this framework is deployed against
a real enterprise. Cross-references kb-L1-enterprise-security for the
security standards that realise PRIN-06 rather than duplicating them.
-->

# Thornbury Foods Group — Binding Architecture Principles (L1 Catalogue)

## BP0: What this document is, and what it is not

A **principle** is a durable rule of the enterprise. It names no product, no
vendor and no protocol — if it does, it is a *standard*, and it belongs in
the standards catalogue with a reference from here.

Two layers exist, and confusing them is the most common failure:

| Layer | Lives in | Changes when | Answers |
|---|---|---|---|
| **Catalogue** (this document) | `kb-L1-enterprise-architecture` | The enterprise changes its mind — annual or event-driven | *What does the enterprise believe?* |
| **Resolution** (`binding-principles.json`) | An input artifact, per product | A product is chartered, or re-resolved at `valid_until` | *Does this principle bind THIS product, how hard, and with what already-approved exceptions?* |

A viewpoint architect (`L1-design-platform-architect`,
`L1-design-data-architect`, `L1-design-integration-architect`) reads **both**:
the resolution tells it which principles are live and at what binding level;
this catalogue tells it what each one actually requires, what evidence proves
compliance, and where the known trade-offs are. Neither alone is sufficient —
a resolution without the catalogue is a list of ids, and a catalogue without
a resolution cannot say whether PRIN-07 is MANDATORY here or does not apply
at all.

A principle is **not** advice. Every entry below carries at least one
conformance check with a machine-evaluable expression. An entry that cannot
be checked is a slogan and does not belong in this catalogue.

---

## BP1: Vocabulary

### Binding levels
| Level | Meaning |
|---|---|
| `MANDATORY` | Must be satisfied. Non-conformance requires a formal exception with compensating controls and an exit plan. Blocks the EA gate if violated without one. |
| `DIRECTIONAL` | Strong default. Deviation is recorded as a `DEV-nn` entry in the FSA with rationale; no formal exception workflow. |
| `ADVISORY` | Guidance. Considered in option analysis; not checked by conformance. |

### Applicability
| Value | Meaning |
|---|---|
| `APPLIES` | Binds this product at the stated binding level. |
| `PARTIAL` | Binds only the scope named in `resolution.resolved_scope`. |
| `NOT_APPLICABLE` | Does not bind at the FSA level; reason recorded. **It may still bind a viewpoint document** — PRIN-07 is the standing example: the FSA names no technology, so the principle binds PLT and DAT instead. |

### Exception types
| Type | Meaning | Conformance verdict |
|---|---|---|
| `TRANSITIONAL` | Time-bound; has an exit plan, a remediation owner and a due date. | `DRIFTED` with a due date |
| `ACCEPTED` | Permanent, risk-accepted by the named authority. | `CONFORMANT-BY-EXCEPTION` |
| `LEGACY_CONTAINMENT` | The violating component is frozen — no extension, no new consumers. | `DRIFTED`; any change that extends it is `DIVERGES` |

### Hook targets
`APP-1` · `APP-2` · `APP-3` · `CON` · `REQ-DAT` · `REQ-INT` · `REQ-PLT` · `SEC` · `OPEN`

### Hook effects
`SEEDS_CONSTRAINT` · `SHAPES_DECOMPOSITION` · `SEEDS_DEMAND` · `SEEDS_CONTROL` · `SEEDS_DEFERRAL`

---

## BP2: PRIN-01 — Business outcome before technology choice

**Domain:** business

**Statement.** Every architecture decision names the business outcome it
serves before it names the capability or product that delivers it.

**Business rationale.** A decision recorded only as a technology choice
cannot be revisited when the outcome changes, because nobody can tell what it
was for. Recording the outcome first makes the decision reversible and makes
its cost attributable.

**Architectural implications.**
- Every architecturally significant decision cites a requirement, an NFR budget or a named business driver — never "industry standard" or "best practice".
- An option analysis that compares products without comparing outcomes is rejected at review.
- A decision with no outcome behind it is deferred, with a trigger, rather than made on preference.

**Scope.** enterprise-wide. Heightened rigour when: business-critical, regulated, or irreversible within one PI.

**Evidence of compliance.**
- Every ADR states the outcome and the requirement id it serves.
- Every `PENDING` decision in a viewpoint document carries a trigger condition, not a date.

**Trade-offs.** *Tension with delivery speed* — insisting on an outcome slows the first decision and speeds every later revision of it.

**Exception conditions.** A reversible, low-cost decision inside one component's own boundary may be made on team preference and recorded without an outcome.

**Owner:** Head of Enterprise Architecture · **Review cadence:** annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-01-C1` | Deferred decisions have triggers | `for each decision where status == PENDING: exists trigger_condition` | any viewpoint document § pending decisions | MAJOR |

**FSA hooks.**
| Target | Effect | Seed text |
|---|---|---|
| `OPEN` | `SEEDS_DEFERRAL` | A decision the architecture is not yet qualified to make is recorded as PENDING with an explicit trigger condition, never guessed and never silently omitted. |

**Review questions.** Does this change make a technology choice with no stated outcome behind it? Does it resolve a PENDING decision whose trigger has not fired?

---

## BP3: PRIN-02 — One accountable owner and one authoritative source per data domain

**Domain:** data

**Statement.** Every critical data entity has one accountable owner and
exactly one system of record.

**Business rationale.** Two sources of truth create conflicting definitions,
reconciliation effort and untrustworthy reporting. For financial and
regulated data there is no "correct" value to restore once they diverge.

**Architectural implications.**
- Every solution design identifies where each critical entity is created, maintained and consumed *before* it is persisted.
- Uncontrolled replication of customer, product, employee or financial data is challenged; replication is permitted only as a **registered read model** with lineage and a declared staleness budget.
- Ownership is assigned to a business capability (bounded context), not to a team and not to a database.

**Scope.** enterprise-wide. Heightened rigour when: financial data, PII, regulated-evidence data.

**Evidence of compliance.**
- A system-of-record register exists and covers 100% of critical entities.
- No entity has more than one writing component.
- Every replicated attribute is a registered read model with a declared staleness budget.

**Trade-offs.** *Tension with reporting and low-latency reads* — both pull towards replication. Resolved by permitting replication only as a governed read model or an analytical plane, never as a second writer.

**Exception conditions.** Transitional replication during a migration, with lineage, synchronisation rules and a decommission date.

**Owner:** Chief Data Officer · **Review cadence:** annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-02-C1` | Exactly one writer per entity | `for each entity in data-model-overview: count(writing_components) == 1` | `data-architecture.md` § DAT-1 | BLOCKING |
| `PRIN-02-C2` | Replicated attributes are registered read models | `for each column mirroring an attribute owned by another context: exists read_model_registration with staleness_budget` | `data-architecture.md` § read models | MAJOR |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `CON` | `SEEDS_CONSTRAINT` | Exactly one system of record per entity. No exceptions. | DAT |
| `CON` | `SEEDS_CONSTRAINT` | Non-owning contexts hold references to another context's entities by identifier only, never replicated attributes, except in an explicitly registered read model. | DAT |
| `REQ-DAT` | `SEEDS_DEMAND` | Every entity in APP-3.1 has exactly one system of record, recorded in a register available before the first feature cycle. | DAT |

**Related standards:** `STD-DATA-04` read-model registration

**Review questions.** Does this change write an entity owned by another bounded context? Does it copy an attribute owned elsewhere without registering a read model?

---

## BP4: PRIN-03 — Integrate through governed, reusable interfaces

**Domain:** integration

**Statement.** Systems exchange information through governed, versioned
interfaces — never through database-level or point-to-point coupling.

**Business rationale.** Direct coupling makes both sides unversionable, slows
change and raises replacement cost. Governed interfaces make staleness and
dependency explicit rather than discovered during an incident.

**Architectural implications.**
- Capabilities are exposed through contracts (APIs or events) that are owned, versioned and discoverable.
- **Asynchronous exchange is the default**; a synchronous dependency is deliberate, budgeted and named.
- Direct database access and one-off file transfers are transitional and carry an exit plan.

**Scope.** enterprise-wide. Heightened rigour when: cross-domain integration, ecosystem/partner integration.

**Evidence of compliance.**
- Every cross-context dependency has a published, versioned contract.
- Count of point-to-point and database-level integrations trends to zero.
- Breaking changes follow an expand-and-contract path.

**Trade-offs.** *Tension with user-facing latency budgets* — some values must be correct at display time; eventual consistency is not acceptable there and a synchronous read is required. That is a budgeted deviation, not a licence.

**Exception conditions.** Legacy containment — an existing direct integration may remain if frozen and scheduled for removal.

**Owner:** Head of Integration Architecture · **Review cadence:** annual · **Abstraction check:** PASS — names no bus, gateway or protocol

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-03-C1` | Every APP-2.3 edge has a contract | `for each edge in fsa.APP-2.3: exists contract with owner and version` | `integration-architecture.md` § contract register, `api-surface.yaml` | MAJOR |
| `PRIN-03-C2` | No cross-context direct data access | `count(cross_context_db_grants) == 0 excluding exceptions[type=LEGACY_CONTAINMENT]` | `platform-architecture.md` § credentials; schema grants | BLOCKING |
| `PRIN-03-C3` | Synchronous edges are budgeted | `for each synchronous cross-context edge: exists latency_budget and exists degraded_mode` | `integration-architecture.md` § flow register | MAJOR |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `CON` | `SEEDS_CONSTRAINT` | No context reads or writes another context's persistent state directly. | DAT, INT, PLT |
| `CON` | `SEEDS_CONSTRAINT` | Every cross-context interaction is asynchronous unless a REQ-INT demand states a synchronous need with a latency budget and a degraded-mode behaviour. | INT |
| `REQ-INT` | `SEEDS_DEMAND` | Cross-context contracts are versioned; a breaking change requires an expand-and-contract path so no consumer breaks on a provider release. | INT |

**Related standards:** `STD-INT-02` contract versioning

**Review questions.** Does this change introduce a cross-context dependency without a published contract? Is any new synchronous call backed by a REQ-INT latency budget and a degraded-mode behaviour?

---

## BP5: PRIN-04 — Decompose by business capability (bounded contexts)

**Domain:** application

**Statement.** Systems are decomposed into bounded contexts aligned to
business capabilities; each context has one ubiquitous language, one owning
team and independent deployability.

**Business rationale.** Boundaries drawn on technical layers couple things
that change for different reasons. Capability boundaries let each part change
at its own cadence under its own approval.

**Architectural implications.**
- Context boundaries are justified by a stated heuristic — a different clock, language, regulator or consistency need.
- Technical layers (UI, API, database) are **never** contexts.
- Each bounded context is realised by at least one independently deployable component; no component spans two contexts.

**Scope.** enterprise-wide. Heightened rigour when: greenfield products, modernisation programmes.

**Evidence of compliance.**
- Each context has a rationale citing a boundary heuristic.
- No component writes entities owned by two contexts.
- 3–9 contexts per product.

**Trade-offs.** *Tension with PRIN-05 reuse* — a shared kernel looks like reuse but couples every consumer to a schema.

**Exception conditions.** Generic subdomains may be realised by a shared enterprise service (e.g. identity) consumed conformist-style.

**Owner:** Head of Enterprise Architecture · **Review cadence:** annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-04-C1` | No component spans two contexts | `for each component: count(distinct owning_context of entities_written) <= 1` | `component-inventory.json`, `data-architecture.md` § DAT-1 | BLOCKING |
| `PRIN-04-C2` | Every context is independently deployable | `for each bounded_context: count(independently_deployable_components) >= 1` | `platform-architecture.md` § runtime | BLOCKING |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `APP-1` | `SHAPES_DECOMPOSITION` | Contexts are cut by boundary heuristics; every card cites at least one. | APP |
| `CON` | `SEEDS_CONSTRAINT` | Every bounded context is realised by at least one independently deployable component; no component spans two contexts. | APP, PLT |

**Review questions.** Which single bounded context owns this change? Does this change make one component write entities of two contexts?

---

## BP6: PRIN-05 — Reuse before buy before build

**Domain:** application

**Statement.** New requirements first evaluate reuse or extension of existing
enterprise capabilities before introducing new products or bespoke solutions.

**Business rationale.** Application sprawl raises licence, integration and
support cost and fragments the user experience.

**Architectural implications.**
- Option analysis includes capability mapping and fit-gap.
- A new tool needs explicit justification if an existing platform can meet the need with reasonable configuration.

**Scope.** enterprise-wide. Heightened rigour when: SaaS procurement.

**Evidence of compliance.** Capability reuse analysis in business cases; fewer overlapping tools per capability.

**Trade-offs.** *Tension with speed and niche functionality* — a new product may be faster; the enterprise impact must be made explicit rather than absorbed silently.

**Exception conditions.** Strategic differentiation with recorded enterprise impact.

**Owner:** Head of Portfolio Architecture · **Review cadence:** annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-05-C1` | Generic contexts consume enterprise services | `for each context where type == Generic: realised_by in enterprise-service-catalogue or exists exception` | FSA APP-1.1, `component-inventory.json` | MINOR |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `APP-1` | `SHAPES_DECOMPOSITION` | Generic subdomains are marked as such and default to enterprise-service reuse via a Conformist relationship. | APP |

**Review questions.** Does this change introduce a capability an enterprise service already provides?

---

## BP7: PRIN-06 — Security and privacy are designed in

**Domain:** security

**Statement.** Security, privacy and control requirements are addressed at
design time and visible in design artifacts, never deferred to test or
operations.

**Business rationale.** Retrofitted controls cost more, work less well and
disrupt delivery. Early controls support compliance, resilience and trust.

**Architectural implications.**
- Trust boundaries, data classification and controls appear in the target architecture before the first component is built.
- Every classified entity has retention and residency decided **before it is first persisted**.
- Secrets are per component and rotated without redeploying dependants.

**Scope.** enterprise-wide. Heightened rigour when: customer-facing, regulated data, business-critical.

**Evidence of compliance.** Threat model and classification present at the EA gate; automated control checks in the pipeline; zero shared secrets across contexts.

**Trade-offs.** *Tension with delivery urgency* — deferral requires compensating controls and formal risk acceptance, never a silent slip.

**Exception conditions.** Time-boxed deferral with risk acceptance by the CISO delegate.

**Owner:** Chief Information Security Officer · **Review cadence:** semi-annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-06-C1` | Classified entities have retention and residency | `for each entity where class in [PII, Financial, Regulated-evidence]: exists retention_policy and exists residency_policy` | `data-architecture.md` § classification | BLOCKING |
| `PRIN-06-C2` | No shared credentials across contexts | `count(credentials shared by two or more bounded contexts) == 0` | `platform-architecture.md` § identity and secrets | BLOCKING |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `SEC` | `SEEDS_CONTROL` | Every PII and Financial entity is encrypted at rest and its access is attributable to a principal. | DAT |
| `CON` | `SEEDS_CONSTRAINT` | Every entity classified Financial or PII carries a retention and residency policy before it is first persisted. | DAT, PLT |

**Related standards:** `kb-L1-enterprise-security` ES1–ES7 · `STD-SEC-01` secrets management

**Review questions.** Does this change persist a new entity without a classification row? Does it cross a trust boundary without re-establishing identity?

---

## BP8: PRIN-07 — Prefer strategically approved platforms and managed services

**Domain:** technology

**Statement.** Technology choices align with the enterprise platform
strategy; standardised, managed services are preferred over bespoke
infrastructure.

**Business rationale.** Platform consistency improves supportability,
resilience, automation and cost transparency, and reduces the set of skills
the organisation must maintain.

**Architectural implications.**
- Default to approved hosting, identity, observability and data services.
- Products in `contain` or `retire` lifecycle status are **not adopted by new solutions**.

**Scope.** enterprise-wide. Heightened rigour when: business-critical, regulated workloads.

**Evidence of compliance.** Adoption of approved platform services; reduced bespoke infrastructure; no new use of `retire`-status products.

**Trade-offs.** *Tension with specialised performance and sovereignty needs* — these may require alternatives, governed as exceptions rather than as quiet local choices.

**Exception conditions.** Sovereignty or workload-specific need with an approved exception.

**Owner:** Head of Technology Strategy · **Review cadence:** annual · **Abstraction check:** PASS

> **Standing note on applicability.** This principle is commonly resolved
> `NOT_APPLICABLE` *at the FSA level* and still **MANDATORY** for the
> Platform and Data viewpoint documents. The FSA names no technology, so
> there is nothing there for this principle to bind; the viewpoint architects
> are the first agents permitted to name a product, and so they are the first
> that can violate it. A viewpoint architect must never read
> `applicability: NOT_APPLICABLE` as "ignore me" without also reading
> `resolved_scope`.

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-07-C1` | No contain/retire-status products | `for each technology in platform-architecture.md: lifecycle_status not in [contain, retire] or exists exception` | `platform-architecture.md`, technology-lifecycle register | MAJOR |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `REQ-PLT` | `SEEDS_DEMAND` | Platform demands are stated as capability classes so approved-platform lookup is possible; the FSA does not name products. | PLT |

**Related standards:** `STD-TECH-01` approved platform catalogue

**Review questions.** Does the proposed realisation use a product in `contain` or `retire` status? Was the approved catalogue consulted before the choice?

---

## BP9: PRIN-08 — Operability and observability are architecture, not operations

**Domain:** technology

**Statement.** Every deployable component is observable and operable by
someone who did not build it, from the day it first deploys.

**Business rationale.** A component nobody but its author can diagnose
becomes a single-person dependency and a long outage. Observability retro-fitted
after an incident is designed around that one incident.

**Architectural implications.**
- Correlation identifiers defined by the integration viewpoint are propagated by every workload.
- Logs, metrics, traces and alerts are a platform capability consumed by components, not re-implemented per component.
- A component with no defined failure signal is not considered deployable.

**Scope.** enterprise-wide. Heightened rigour when: business-critical, regulated, or customer-facing.

**Evidence of compliance.** Every deployable emits to the central observability capability; every integration carries correlation and trace identifiers; every SLO has an alert.

**Trade-offs.** *Tension with delivery speed in Cycle 0* — the platform must exist before the first feature, which is exactly why Cycle 0 exists as a phase.

**Exception conditions.** None at MANDATORY. A component may defer dashboards, never signals.

**Owner:** Head of Technology Strategy · **Review cadence:** annual · **Abstraction check:** PASS

**Conformance checks.**
| ID | Description | Check | Evidence source | Severity |
|---|---|---|---|---|
| `PRIN-08-C1` | Every deployable is observable | `for each deployable component: emits(logs) and emits(metrics) and propagates(correlation_id)` | `platform-architecture.md` § observability | MAJOR |

**FSA hooks.**
| Target | Effect | Seed text | Binds |
|---|---|---|---|
| `REQ-PLT` | `SEEDS_DEMAND` | Central logging, metrics, tracing and alerting are available to every workload before the first feature cycle. | PLT |
| `REQ-INT` | `SEEDS_DEMAND` | Every integration is observable through a correlation identifier, a trace identifier and contract-version identification. | INT, PLT |

**Review questions.** Can someone who did not build this component tell that it is failing, and why, without reading its source?

---

## BP10: Precedence rules

Principles conflict predictably. Where they do, the precedence is decided
once here, not re-argued per change.

| ID | When | Prevails | Over | Condition | Recorded in FSA |
|---|---|---|---|---|---|
| `PREC-01` | A regulated control requirement conflicts with standardisation or speed | `PRIN-06` | `PRIN-05`, `PRIN-07` | Always; the standardisation exception is time-bound with an exit plan | `CON.1` |
| `PREC-02` | A display-time correctness need conflicts with async-by-default integration | the `REQ-INT` budget | `PRIN-03` async default | Only with a stated latency budget and degraded-mode behaviour, recorded as an FSA `DEV` entry | `CON-6`, § 4.1 |
| `PREC-03` | Reuse of an enterprise service would put a second writer on an owned entity | `PRIN-02` | `PRIN-05` | Always — reuse is consumption, never co-ownership | `CON.1` |
| `PREC-04` | An approved managed service cannot meet a stated NFR budget | the `REQ-*` budget | `PRIN-07` | Only with the budget cited and an exception recorded; never on preference or unmeasured suspicion | `CON.1`, § 4.1 |

---

## BP11: The resolution file — what a viewpoint architect actually receives

The per-product resolution is a `binding-principles.json` authored against
`binding-principles.template.json`. A viewpoint architect reads these fields
and ignores the rest:

| Field | Why the architect needs it |
|---|---|
| `metadata.product.mode` | `GREENFIELD` vs `BROWNFIELD` — decides whether `brownfield.principle_posture` must be read at all |
| `metadata.product.regulatory_regimes[]` | Drives classification, retention and residency decisions that would otherwise be guessed |
| `principles[].id`, `.name`, `.domain` | Which catalogue entry above to apply |
| `principles[].resolution.applicability` | `APPLIES` / `PARTIAL` / `NOT_APPLICABLE` — **read with `resolved_scope`, see BP8's standing note** |
| `principles[].resolution.binding_level` | Whether a deviation needs a formal exception or only a `DEV` row |
| `principles[].resolution.resolved_scope` | For `PARTIAL`, the contexts, data classes or components it binds |
| `principles[].resolution.program_guardrail` | The one-line, product-specific expression to quote in the document's "Principles Applied" section |
| `principles[].conformance_checks[]` | Copied into the viewpoint document's own conformance section so the checker has something to evaluate |
| `principles[].fsa_hooks[]` where `binds_viewpoints` contains this viewpoint | The normative text this viewpoint must satisfy |
| `principles[].exceptions[]` | Already-approved deviations — recorded as known drift, never re-litigated and never silently "fixed" |
| `precedence_rules[]` | Which principle wins when two demands collide |
| `brownfield.principle_posture[]` | Existing violations, so a retrofit does not encode a known violation as intent |

**Validation before use.** The file is unusable — not the product
non-conformant — if any of these fail:

```text
metadata.resolution.status == APPROVED
today <= metadata.resolution.valid_until
5 <= principles.length <= 15
every principle has >= 1 conformance_check with a non-placeholder expression
every principle with applicability in [APPLIES, PARTIAL] has >= 1 fsa_hooks
every principle.catalogue.abstraction_check == PASS
every TRANSITIONAL exception has due, exit_plan and remediation_owner
every precedence_rules[].prevails and .over reference existing principle ids
if mode == BROWNFIELD then brownfield.principle_posture covers every MANDATORY principle
```

**When no resolution file is supplied.** The FSA's own § 4 `PRIN` rows are
the fallback: the foundational architect writes them from the same source.
Apply the catalogue entries above for the principles the FSA § 4 names, at
the binding level it states. Record in the output document that the
resolution file was absent and that principle application came from FSA § 4 —
do not silently apply the whole catalogue as if every principle were
`MANDATORY`, and do not skip the section as if none were.

---

## BP12: Exception handling

An exception is a governed record, not a note.

| Field | Required |
|---|---|
| `principle_id`, `where`, `why`, `risk` | Always |
| `compensating_controls[]` | Always |
| `type` | `TRANSITIONAL` \| `ACCEPTED` \| `LEGACY_CONTAINMENT` |
| `exit_plan`, `remediation_owner`, `due` | Always for `TRANSITIONAL` |
| `approved_by`, `approved_on` | Always |

**Approver by binding level:** `MANDATORY` → Enterprise Architect + risk
owner · `DIRECTIONAL` → Solution Architect, recorded as an FSA `DEV` row ·
`ADVISORY` → none.

**Pattern signal.** Three or more exceptions against one principle means
either the enterprise capability is weak or the principle no longer fits.
Either way it triggers a catalogue review — it is not evidence that the
principle should be quietly ignored.

---

## BP13: Outcome metrics

| Metric | Principle | Target |
|---|---|---|
| Entities with more than one writer | `PRIN-02` | 0 |
| Cross-context dependencies without a published contract | `PRIN-03` | 0 |
| Components spanning two bounded contexts | `PRIN-04` | 0 |
| Classified entities with no retention or residency policy | `PRIN-06` | 0 |
| New adoptions of `contain`/`retire`-status products | `PRIN-07` | 0 |
| Deployables with no failure signal | `PRIN-08` | 0 |
| Open `TRANSITIONAL` exceptions past due | all | 0 |

---

## BP14: Glossary

- **Binding principle** — a rule of the enterprise that a product must satisfy or formally except.
- **Resolution** — the per-product decision about whether and how hard a principle binds.
- **Conformance check** — a machine-evaluable expression over design artifacts; a principle without one is a slogan.
- **FSA hook** — the normative text the foundational architect lifts into the FSA, and which the named viewpoints must then satisfy.
- **Program guardrail** — the one-line, product-specific phrasing of a principle, quotable in a viewpoint document.
- **Drift** — a known, recorded violation with an owner, as distinct from a new violation nobody has seen.

---
*Last reviewed: 2026-09-22 · Review cadence: annual + event-driven (M&A,
regulatory shift, platform strategy change). The resolution file is
re-resolved at its own `valid_until`, independently of this catalogue.*
