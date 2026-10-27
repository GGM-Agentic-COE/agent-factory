# Test Strategy: HarvestLink

> **Status: Evaluated review draft — NOT APPROVED.**
>
> **Decision: escalate_to_hitl.**
>
> Requirements-baseline conflicts, incomplete governance and unresolved delivery prerequisites prevent approval.
> This document defines testing policy, not test cases.

| Document control | Value |
|---|---|
| Evaluation date | 2026-10-26 |
| Programme Increment | Not supplied; roadmap absent |
| Workflow execution | wf-c6be9715-a552-4dd7-8c3a-56477f3d2f16 |
| Target baseline | target-architecture.md v4.1; status `approved`; approved_by `enterprise-architect`; approved_on `2026-11-21` |
| Solution baseline | solution-architecture%20(2).md; status `DRAFT`; satisfies_from `target-architecture.md@4.1`; `gate_ready: false` |
| Requirements baseline | prd.md; no version header; explicitly illustrative |
| Publication | Not published; Confluence tools unavailable; space key not supplied |

Baseline metadata is reproduced, not endorsed. The target approval date is later than the evaluation date and requires confirmation. Source files were independently retrieved through knowledge search and read in full; they were not fetched from the workflow's Confluence folder.[1]​[2]​[3]

## 1. Scope and standing

HarvestLink has six bounded contexts: Catalogue, Orders and Billing are Core; Identity and Tax & Compliance are Supporting; Notifications is Generic. APP-2 declares six services and two experience components.

The intended standing is approval once per PI, with test cases approved per cycle. **That approval has not been granted.** The PI identifier, cycle duration, band boundaries and release windows are not supplied. Roadmap absence does not waive numeric governance requirements.

**Requirements grounding.** FR-001 through FR-009 remain requirements inputs. Explicit epic IDs, committed stories and AC IDs are not supplied. APP-2 identifies ownership boundaries, but does not establish implementation of every PRD requirement. Discovery partially relates to Catalogue search; registration, trading and compliance have related architectural concepts. Such overlaps are not sufficient to prove end-to-end requirement coverage. The previous blanket claim that every FR has no architectural home is withdrawn.

The target cites `prd.md@1.0`; the supplied PRD is unversioned and illustrative. The solution records that no PRD was supplied. Product and architecture owners must reconcile these baselines and map all nine FRs before feature acceptance can be approved.

**Declaration coverage.** APP-1–APP-3, DAT-1–DAT-4, INT-1–INT-4 and PLT-1–PLT-6 are present. APP-2 and DAT-3 satisfy the minimum structural input requirement. No viewpoint section is absent; several contain unresolved policy decisions. The complete read register is in §8.

**traced_to:** APP-1, APP-2, APP-3; solution Inputs and technology sources; PRD FR-001 through FR-009.[1]​[2]​[3]

## 2. The four tiers

The tier policies and coverage targets below are retained from the submitted strategy for review. They are not execution results. Cadences remain provisional until checked against the PI roadmap.

| Tier | Entry condition | Quantified exit policy | Cadence | Load-bearing in |
|---|---|---|---|---|
| Feature | Committed story and ACs exist; PRD-to-APP-2 ownership is agreed; fixtures satisfy §4; relevant responsibility exclusions are identified | 100% of committed-story ACs pass; 100% of applicable INV-01–INV-07 asserted; APP-2 responsibility boundaries satisfied = true | Every cycle; PI scheduling and justification unresolved | greenfield, brownfield, bugfix |
| Contract | INT-2 contract, provider/consumer boundaries, SEC-3 authentication and DAT-2 schemas identified; required substitutes available; release eligibility subject to blockers below | 7/7 planned contracts and 7/7 schemas verified for complete-baseline exit; 0 breaking changes within a major version; 100% of contracts declare authentication; 100% of system-boundary-crossing contracts use Kong Gateway | Every cycle; provider/consumer changes determine applicable scope; PI justification unresolved | greenfield, brownfield |
| Integration | PLT-3 exit proof signed by Platform Lead; PEND-07 resolved; unchanged artifact promoted to Staging; substitutes expose declared edge behavior; Financial read-model restrictions observed | 11/11 edges covered for normal and declared failure behavior; 4/4 snapshots captured once and not reconciled; Fee copy in Orders = false; 4/4 consumer bindings verified; FLOW-00 correlation trace complete = true | Every cycle; Staging promotion is execution trigger; PI justification unresolved | greenfield, brownfield, bugfix |
| Regression + NFR | Integration passes on same artifact; PLT-4 telemetry available; immutable financial-store demonstration complete; production prerequisites respected | 100% of applicable numeric targets and boolean controls in §5 pass; 0 application UPDATE/DELETE grants on billing.fee; 25/25 proposed adversarial obligations covered; flake rate meets approved §6 policy | Band boundary and release; windows absent | brownfield, bugfix |

### Feature policy

Ownership follows the relevant APP-2 component. APP-3 covers Listing, Order, Transaction and TaxRate aggregates:

- INV-01: FBO validity at publication and checkout.
- INV-02: positive integer prices in minor currency units.
- INV-03: placement-price snapshot.
- INV-04: idempotency on `(buyer_id, idempotency_key)`.
- INV-05: Fee has no independent existence without Transaction.
- INV-06: Fee immutability.
- INV-07: tax reproducibility.

PRD scope is not replaced by these invariants. Exactly one component/context per story, 100% automation and a prescribed pipeline insertion stage are not established by APP-2/PLT-3; they remain unapproved upstream proposals.

### Contract policy

Providers own the seven INT-2 contracts; consumers own their expectations:

1. `identity.fbo-validity`
2. `catalogue.listing-availability`
3. `tax.vat-calculation`
4. `billing.fee-quote`
5. `tax.invoice-line-data`
6. `buyer-experience.gateway-surface`
7. `producer-experience.gateway-surface`

DAT-2 registers seven schemas at version `1.0.0`: `catalogue.listing.published`, `tax.compliance.expiring`, `orders.order.placed`, `billing.fee.recorded`, `billing.statement.generated`, `billing.payout.scheduled`, `tax.invoice.issued`.

Experience-facing authentication uses Microsoft Entra External ID bearer tokens. Service-to-service authentication uses Azure Managed Identity, validated at the Kong edge under the implemented SEC-3 control. Contract compatibility is additive within a major version; breaking changes follow expand-and-contract.

**Separate blockers:**

- PEND-08 requires genuine consumer-driven verification before a provider release reaches a second registered consumer. `identity.fbo-validity` has two registered consumers. This is not a source-declared prohibition on all preliminary verification.
- PLT-4 separately prohibits shipping request-path contracts without declared p95 budgets. `identity.fbo-validity` has PEND-01; both experience gateway surfaces also have PENDING budgets. The previous blanket statement that the other six contracts can proceed without qualification is incorrect.
- Event-schema verification is not itself a request-path latency gate. Partial verification cannot be reported as 7/7 complete-baseline exit.

### Integration policy

Platform Lead owns environment readiness; the relevant contexts own their edges. The dependency/failure surface is:

| Behavior | Edges |
|---|---|
| Fail closed | E-01, E-02, E-03, E-04, E-06 |
| Degrade | E-05 |
| Retry with dead-letter | E-07, E-08, E-09 |
| Mark stale beyond SLA; never present as current | E-10, E-11 |

Identity failure blocks publication/checkout; Catalogue or Tax failure blocks its protected action; fee-display failure must not block confirmation. PEND-03 restricts Financial-sourced read-model columns, not the two-plane architectural decision.

The four registered consumer bindings are `tax.compliance` → catalogue-service; `orders.order` → billing-service; `billing.statement` → notification-service; `billing.payout` → notification-service. Each requires declared duplicate handling, idempotency, retry, dead-letter and replay behavior. FLOW-00 is the declared lasting Cycle 0 flow.

### Regression + NFR policy

Budget ownership follows the relevant context; PLT-4 routes breaches to its on-call. The completed and remediated PLT-2 penetration test is required before first external-user onboarding. It is a production prerequisite, not evidence that every other check is automated.

### Declared capability gaps and substitute policy

PLT-6 contains **17 capabilities: 11 AVAILABLE, 4 PARTIAL, 2 NOT PRESENT**. Therefore **6**, not 7, are non-AVAILABLE. REQ-PLT-06 is marked NOT_YET_BUILT in the satisfaction index.[2]

| Capability | Declared status | Contract / Integration treatment | Trace |
|---|---|---|---|
| Immutable long-retention financial store | PARTIAL; configuration/proof pending; no PEND ID | A substitute may expose write acceptance/modification refusal; it cannot prove storage immutability or satisfy Regression + NFR entry | DAT-1, PLT-1, PLT-5, PLT-6, REQ-PLT-03 |
| Container registry | PARTIAL; Azure Container Registry PROPOSED; PEND-07 | No substitute establishes unchanged-artifact promotion; Integration entry remains blocked | PLT-2, PLT-3, PLT-6 |
| Outbound email including evidenced invoices | PARTIAL; PEND-04 | Substitutes distinguish delivery/non-delivery and evidence presence/absence; evidence shape remains undefined; general notice delivery is already decided | PLT-1, PLT-6, REQ-PLT-06 |
| Analytical plane / registered read models | PARTIAL; PEND-03 | Substitutes expose current/stale behavior; no unauthorized Financial-source replication; substitutes do not prove residency compliance | DAT-4, INT-1 E-10/E-11, PLT-6 |
| Consumer-driven contract verification | NOT PRESENT; Pact PROPOSED; PEND-08 | Tooling gap, not a component stub; second-consumer release requires genuine verification | INT-2, PLT-6 |
| Auditor-facing evidence access | NOT PRESENT; Second (or later); no PEND ID | No contract is declared; do not invent one. The first change needing access must define its boundary | target §2.1, PLT-6 |

The two experience gateway surfaces are planned INT-2 contracts with PENDING budgets, not additional PARTIAL PLT-6 capabilities. Substitute policies are not test cases or invented delivery-evidence formats.

**traced_to:** APP-1, APP-2, APP-3, CON-3–CON-6, CON-8, CON-9, DAT-1, DAT-2, INT-1–INT-4, PLT-2–PLT-6, SEC-1–SEC-4.[1]​[2]

## 3. Environment topology

**Isolation.** Preserve independent deployment and no shared runtime state. PLT-1 specifies Azure Container Apps, isolated relational storage and one managed identity per deployable component. DAT-4 identifies five owning storage contexts; Notifications is stateless. No cross-context storage grants or shared identities. This is policy, not a per-component environment inventory. **traced_to:** PLT-1, DAT-4, APP-2, CON-1, CON-3.

**Residency.** UK South is primary; UK West is backup/DR only. Backups inherit source residency. Financial/tax-evidence replication outside the approved financial-data region requires an approved exception; PEND-03 specifically leaves Financial-source analytical population unresolved. Do not use an all-stores-in-UK-South assertion that contradicts declared backups. **traced_to:** solution Platform preamble, DAT-1, DAT-3, DAT-4. No numbered PLT section explicitly states the region rule; Gate 4's numbered-PLT trace requirement remains unresolved rather than assigning a false reference.

**Environment model.** Dev → Test → Staging → Production. Build one immutable artifact and promote unchanged. Production requires the signed PLT-3 exit proof and, before first external-user onboarding, the completed/remediated penetration test. Pipeline: commit → build → unit test → dependency/vulnerability scan → push image → Terraform apply → GitHub Actions deploy → smoke test → promote. Image push remains dependent on PEND-07. **traced_to:** PLT-2, PLT-3.

**Supporting topology.** Azure Event Hubs provides at-least-once transport/replay; Kong Gateway provides the system edge; Microsoft Entra External ID provides external-party identity; Azure Monitor / Application Insights with OpenTelemetry provides telemetry. Azure Blob Storage supports listing images and financial immutability archives; the locked-policy demonstration remains pending. **traced_to:** PLT-1, PLT-4, PLT-5.

**Tier placement proposal.** Feature/Contract → Test and Integration/Regression + NFR → Staging are submitted strategy choices. PLT-2 names environments but does not allocate tiers. These assignments require approval and are not presented as declaration facts.[1]​[2]

## 4. Fixture policy

**Ownership.** DAT-1 declares 20 entities, five owning services and no Notifications-owned entities. Provision through the single system of record. Cross-context references use IDs except registered snapshots. **traced_to:** DAT-1, CON-2, CON-3.

**Snapshots.** The four permitted captures are `OrderLine.price_at_placement`, `OrderLine.vat_rate_at_placement`, `Transaction.order_amount_at_confirmation`, `Invoice.line_items_at_issuance`. Capture once through the declared contract/event and never reconcile. Fee is explicitly not copied into Orders. **traced_to:** DAT-1 snapshot register, RULE DAT-1.e, CON-8.

| Classification | Entities | Retention | At rest / erasure |
|---|---|---|---|
| Public | Product, Listing, ListingImage, Category | PENDING — PEND-02 | Platform-default encryption; erasure honoured |
| PII | Order, OrderLine, OrderStatus, SavedBasket, Producer, Buyer, Session | PENDING — PEND-02 | Group-managed-key encryption; erasure honoured, distinct from overlapping compliance records |
| Regulatory | FboRegistration, TaxRule, ComplianceDocument | 6 years | Group-managed-key encryption; erasure subject to legal hold; compliance window not shortened |
| Financial | Transaction, Fee, Payout, Statement, TaxRate, Invoice | ≥10 years | Encryption plus locked time-based immutability; statutory retention overrides erasure |

**traced_to:** DAT-1, DAT-3, SEC-2.[2]

**PII prohibition.** No real, production-derived or re-identifiable PII in Dev, Test or Staging. Synthetic personal-data fixtures only. No real credentials. This is the strategy's protective non-production restriction derived from classification/security controls and required by evaluation Gate 5; it is not a quotation of an explicit DAT-3 non-production rule. The wider submitted prohibition on copying any Regulatory or Financial record remains a conservative proposal requiring policy-owner ratification, not an existing DAT-3 masking rule. **traced_to:** DAT-1, DAT-3, SEC-2, SEC-4; evaluation Gate 5.[1]​[4]​[2]

**Provisioning constraints.** Monetary values follow positive integer minor-unit rules. Order identity is unique on `(buyer_id, idempotency_key)`. FBO validity windows support publication/checkout boundaries. TaxRate/TaxRule are effective-dated; historical rows are not updated in place. Fee application roles have 0 UPDATE/DELETE grants; corrections are compensating entries. Fee, Transaction and Invoice archives use the locked immutability mechanism. DAT-1 does not establish an equivalent operational insert-only application rule for Transaction and Invoice. Event fixtures conform to DAT-2, including `correlation_id`. **traced_to:** DAT-1 rules c, d, f, g, h; DAT-2; DAT-3.

**Unresolved provisioning.** Public/PII cleanup requires PEND-02; Financial-source analytical fixtures require PEND-03. Non-production locked-retention configuration is not declared. Do not invent shortened retention or imply immediate fixture teardown is possible. **traced_to:** DAT-3, DAT-4, PLT-5, PLT-6.[2]

## 5. NFR approach

Numeric budgets and boolean conformance controls are separate. A numeric PRD requirement remains budgeted when architectural realization is missing. Missing realization blocks verification; it does not erase the number.

### 5.1 Architecture numeric targets

| Target | Assertion | Trace |
|---|---|---|
| Listing availability/price | p95 ≤ 200 ms | REQ-INT-03, E-03 |
| VAT calculation | p95 ≤ 150 ms | REQ-INT-07, E-04 |
| Checkout enclosing budget | ≤ 800 ms | REQ-INT-07, E-04 |
| Fee quote | p95 ≤ 150 ms | REQ-INT-06, E-05 |
| Confirmation enclosing budget | ≤ 400 ms, including degrading fee display | REQ-INT-06, E-05 |
| Invoice line data | p95 ≤ 150 ms | REQ-INT-07, E-06 |
| Invoice-data enclosing budget | ≤ 800 ms as declared; execution boundary requires confirmation | REQ-INT-07, E-06 |
| Order placed to Billing | ≤ 5 s end to end | REQ-INT-04, E-07 |
| Producer earnings freshness | 24-hour freshness SLA; mark stale beyond SLA, never present as current | CON-9, E-10, DAT-4 |
| Quarterly VAT return freshness | 24-hour freshness SLA; mark stale beyond SLA, never present as current | CON-9, E-11, DAT-4 |
| billing-service availability | ≥ 99.9% | PLT-5 |
| tax-service availability | ≥ 99.9% | PLT-5 |
| identity-service availability | ≥ 99.9% | PLT-5 |
| Financial retention | ≥10 years configured | REQ-DAT-02, REQ-DAT-04, REQ-DAT-06, DAT-3, PLT-5 |
| Regulatory retention | 6 years configured; erasure does not shorten compliance window | DAT-3, PLT-5 |

Availability measurement windows and traffic/load profiles are not supplied. PEND-03 blocks Financial-source read-model proof. The invoice-generation/checkout budget linkage is preserved as written, not silently redesigned.[1]​[2]

### 5.2 PRD numeric targets — realization unresolved

| PRD / category | Declared target and strategy assertion | Verification gap |
|---|---|---|
| FR-001 / Compliance | Retain attestation 6 years from creation | Attestation population and owning implementation not mapped |
| FR-003 / Availability | 99.9% uptime for traceability records | Service boundary and observation window not mapped |
| FR-008 / Performance | P95 time-to-first-compliant-trade < 14 days, onboarding start → first compliance-complete trade | Measurement events, reporting owner and method not mapped |
| FR-009 / Performance | Reported completeness score ≥ 95% at first trade | Scoring methodology and owning implementation not mapped |

These are not substituted with similar architecture targets. FR-003 availability is not proven by billing-service availability; FR-001 attestation retention is not automatically proven by FboRegistration retention. **traced_to:** PRD FR-001, FR-003, FR-008, FR-009; APP-2; DAT-1.[3]​[1]​[2]

### 5.3 Boolean conformance controls

| Control | Assertion | Trace |
|---|---|---|
| Fee immutability | 0 application UPDATE/DELETE grants; locked archive modification refused = true | INV-06, DAT-1, REQ-PLT-03 |
| Tax reproducibility | Historical effective-dated reconstruction available = true; placement-rate snapshot preserved = true | INV-07, DAT-1, REQ-DAT-06 |
| Delivery/replay | At-least-once handling verified = true; evidence-kind replay permitted = false | REQ-PLT-02, INT-3 |
| Latency attribution | Breach attributable to a context using correlation_id = true | REQ-PLT-05, PLT-4 |
| Contract p95 declaration | Request-path contract declares p95 before shipping = true | INT-2, PLT-4 |
| Financial chain | price-snapshot → VAT-snapshot → Fee → Invoice reconstructable = true | PLT-4 |
| Credentials | Hardcoded secrets = 0; managed identity per deployable component = true | SEC-4, PLT-1, PLT-3 |
| Edge trust boundary | System-boundary contracts bypassing Kong = 0 | SEC-1, PLT-1, INT-2 |
| Encryption | DAT-3 classification-driven at-rest controls satisfied = true | SEC-2, DAT-3 |
| Residency | Primary placement conforms to UK South = true; backup/DR conforms to UK West restriction = true; prohibited replication = 0 | DAT-1, DAT-3, DAT-4, Platform preamble |

These are 10 control groups, not 10 numeric NFR budgets.[1]​[2]

### 5.4 Classified obligations without numeric budgets

**Reason for every row: no budget provided.** Applicable functional/conformance behavior may still be checked; only the unresolved numeric or policy assertion is unavailable.

| Obligation | Classification / unresolved detail | Trace |
|---|---|---|
| FBO-validity latency | Performance; PENDING | INT-1 E-01/E-02, INT-2, PEND-01 |
| Compliance-expiring propagation | Performance/consistency; eventual, no numeric deadline | INT-1 E-08 |
| Payout-notice propagation | Performance/consistency; eventual, no numeric deadline | INT-1 E-09 |
| Both experience gateway surfaces | Performance; PENDING | INT-2 |
| Catalogue, Orders, Notifications availability | Availability; PENDING | PLT-5 |
| All six services' RTO/RPO | Recoverability; PENDING | PLT-5, PEND-05 |
| Public/PII retention | Retention; PENDING | DAT-1, DAT-3, PEND-02 |
| Seven topics' partition counts/retention windows | Throughput/retention; PENDING | INT-3, PEND-06 |
| Evidenced invoice delivery | Delivery/compliance; mechanism/evidence definition unresolved | REQ-PLT-06, PLT-1, PEND-04 |
| FR-002 discovery response time | Performance; TBD | PRD FR-002 |
| FR-004 declaration volume | Scalability; TBD | PRD FR-004 |
| FR-005 limit recalculation frequency | Performance; TBD | PRD FR-005 |
| FR-006 impossible-facilitation-only routing behavior | Availability; TBD; behavior also unresolved | PRD FR-006 |
| FR-007 pilot cohort size | Scalability; TBD | PRD FR-007 |
| FR-008 reporting feed | Availability; Best-effort, no numeric SLA | PRD FR-008 |
| FR-009 buyer names in reporting | Compliance; TBD; policy decision | PRD FR-009 |

PLT-5 associates unresolved service figures with PEND-05, but the formal PEND-05 decision row specifically names RTO/RPO. Do not claim that a separate availability decision has been supplied. **traced_to:** sections and requirements in each row.[2]​[3]

### 5.5 Remaining PRD qualitative constraints

All 21 PRD NFR rows are accounted for: 4 numeric targets, 7 unbudgeted/policy-pending rows, and these 10 qualitative constraints. Source wording is not converted into invented quantitative acceptance criteria.

| PRD / category | Constraint retained for downstream elaboration |
|---|---|
| FR-001 / Usability | Attestation is a clear, explicit step, not a buried checkbox |
| FR-001 / Security | Attestation tied to authenticated producer/distributor identity |
| FR-002 / Usability | Search results display completeness score alongside each producer |
| FR-003 / Security | Traceability record immutable/append-only once dual-signed |
| FR-003 / Compliance | Reg. (EC) 178/2002 Art. 18, one step back/one step forward |
| FR-004 / Compliance | Natasha's Law / EU FIC Reg. 1169/2011 baseline labelling |
| FR-004 / Usability | Clear pending/finalised declaration states |
| FR-005 / Security | Transaction-value limit enforced server-side, not client-configurable |
| FR-006 / Compliance | HarvestLink never recorded as taking title/possession |
| FR-007 / Usability | Non-cohort users receive explicit not-yet-available response |

**traced_to:** PRD FR-001–FR-007; APP-2 ownership mapping remains unresolved.[3]​[1]

## 6. Pack governance

**Approval blocker:** governance is incomplete. An absent roadmap explains missing evidence; it does not make null thresholds acceptable under Gates 7 and 10.

| Threshold | Submitted value / current status | Basis and unresolved decision |
|---|---|---|
| Flake threshold | Proposed 2%; proposed 0% for adversarial obligations | Strategy proposal, not declaration budget; comparator and observation policy unresolved |
| Staleness ceiling | Not supplied | Numeric duration/cycle count required |
| Feature runtime budget | Not supplied; minutes required | Numeric budget and cadence-window fit required |
| Contract runtime budget | Not supplied; minutes required | Numeric budget and cadence-window fit required |
| Integration runtime budget | Not supplied; minutes required | Numeric budget and cadence-window fit required |
| Regression + NFR runtime budget | Not supplied; minutes required | Numeric budget and cadence-window fit required |
| AC coverage | Proposed 100% of committed-story ACs | No committed AC baseline supplied |
| Adversarial coverage | Proposed 100% of 25 obligations | 7 invariants + 5 fail-closed edges + 4 security controls + 9 constraints |
| Staleness audit frequency | Not supplied | Numeric audit cadence required |

The adversarial denominator is INV-01–INV-07; E-01, E-02, E-03, E-04, E-06; SEC-1–SEC-4; CON-1–CON-9. These are 25 policy obligations, not 25 authored test cases.

**Flake inconsistency requiring approval.** One non-deterministic outcome in 50 executions is exactly 2%. The submitted table uses ≥1 in 50, while quarantine prose says breaching 2%. A maximum of 2% and a trigger of ≥2% have different boundary behavior. Neither comparator nor observation policy is silently chosen.

**Submitted quarantine policy.** Above the approved trigger, remove the affected non-adversarial member from gating, retain non-gating execution and tag its owning context. Adversarial members are not quarantined; a breach blocks the tier. Without an approved trigger, this is not an executable approved policy.

**Submitted staleness mechanism.** Each pack member traces to a live declaration requirement/invariant/edge/constraint/security control or committed AC. Review obsolete traces after an ADR changes the target. Retire only after confirming the obligation ceased, rather than losing coverage. Audit frequency and maximum age remain unset.

**Submitted runtime-breach policy.** Split or reschedule an over-budget pack and report the cadence breach; never drop adversarial coverage to fit. No budget/window comparison is possible until all four budgets and PI windows exist.

PEND-03 and PEND-08 constrain evidence; neither permits reporting blocked obligations as passed. **traced_to:** APP-3, CON-1–CON-9, SEC-1–SEC-4, INT-1, INT-2, PLT-4, PLT-6; submitted §6 proposals; evaluation Gates 7 and 10.[1]​[4]​[2]

## 7. What this strategy does NOT settle, and why

- **No test cases, scripts or data records.** Downstream authors elaborate committed stories/ACs; these inputs are not supplied.
- **No per-component environment register.** The environment provisioner translates §3 policy into that downstream artifact.
- **No per-component fixture inventory.** The synthetic-data generator translates §4 class/ownership rules into fixtures.
- **No approval by declaration.** Target status metadata does not approve this strategy. Confirm the future-dated `2026-11-21` approval and reconcile the illustrative unversioned PRD with `prd.md@1.0`.
- **No invented PI or governance numbers.** PI identity, cycle/band/release windows, staleness ceiling, four minute budgets and audit cadence require approved planning/policy decisions.
- **No assumed feature traceability.** Map FR-001–FR-009 to APP-2 and downstream ACs; do not discard PRD numeric or qualitative obligations.
- **No assumed non-production lock override.** DAT-3/PLT-5 do not define one. Resolve fixture retention and the wider synthetic-only restriction before provisioning.
- **No fabricated numbered-PLT residency citation.** The Platform preamble and DAT-1/DAT-3 supply the rule; an architecture/rubric owner must resolve the citation mismatch.
- **No assumption that AVAILABLE means proven.** All 14/14 PLT-3 exit-proof rows are NOT YET PROVEN. The Platform Lead signs the proof.
- **No runtime readiness claim.** PEND-07 leaves `gate_ready: false`; submitted Integration entry remains blocked, and Regression + NFR cannot inherit a nonexistent Integration pass.
- **No substitute accepted as statutory proof.** Financial-store configuration/demonstration remains pending without a PEND ID.
- **No invented auditor contract.** PLT-6 defers access to Second (or later), resolved by the first change needing it.
- **No unsupported automation mandate.** The exactly-one-component story restriction, 100% automation and fixed pipeline insertion stage remain unapproved upstream proposals.

### Pending-decision register

| ID | Decision / strategy effect | Source owner and trigger |
|---|---|---|
| PEND-01 | FBO-check latency unresolved; request-path shipping constrained | Solution Architect; add target REQ-INT budget or demonstrate headroom within 800 ms checkout / publication flow |
| PEND-02 | Public/PII retention and fixture cleanup unresolved | Solution Architect / DPO; Legal/DPO assigns periods before first erasure request or retention audit |
| PEND-03 | Financial-source analytical population not authorized | Platform Lead; EA10-approved ES9 exception or redesign to non-Financial aggregates |
| PEND-04 | Invoice delivery-evidence definition/mechanism unresolved | Platform Lead; confirm Azure Communication Services Email receipts meet REQ-PLT-06 or select approved alternative |
| PEND-05 | All six services' RTO/RPO unresolved | Platform Lead; set with DR design before Financial-tier components go live |
| PEND-06 | Seven topics' partition counts/retention windows unresolved | Platform Lead; Cycle 1 profiling or before first production load test |
| PEND-07 | Registry unconfirmed; Cycle 0 exit pipeline blocked | Platform Lead; confirm product/add to EA11 before exit pipeline |
| PEND-08 | Contract verification tool unconfirmed | Platform Lead; confirm/add to EA11 before first INT-2 contract reaches second consumer |

The PRD separately records missing offboarding/suspension and dispute-handling requirements. No new FR IDs or behaviors are invented. Availability observation windows, traffic profiles and the invoice-generation/checkout measurement boundary also require clarification.

**traced_to:** APP-2, DAT-3, DAT-4, INT-2, PLT-2–PLT-6, Pending decisions, PRD Open Questions; evaluation Gate 8.[1]​[4]​[2]​[3]

## 8. Declaration sections read, and sections absent

### Independently read viewpoint sections

| ID | Section title |
|---|---|
| APP-1 | Domain decomposition |
| APP-2 | Component map and responsibility allocation |
| APP-3 | Aggregate boundaries and invariants |
| DAT-1 | Canonical entity model |
| DAT-2 | Event envelope standard |
| DAT-3 | Classification and retention policy |
| DAT-4 | Operational vs analytical planes |
| INT-1 | Protocol decision rules |
| INT-2 | API surface and contract rules |
| INT-3 | Event topology |
| INT-4 | End-to-end flows |
| PLT-1 | Runtime topology |
| PLT-2 | Environment model |
| PLT-3 | Pipeline, supply chain and Cycle 0 exit proof |
| PLT-4 | Observability |
| PLT-5 | Resilience, retention and DR |
| PLT-6 | Capability register |

**Target supporting sections read:** Purpose and scope; Business context; System context (C4 Level 1); Principles applied; APP-1 domain overview, domain view, context map and bounded-context descriptions; APP-3 aggregate subsections; CON Cross-viewpoint constraints (CON-1–CON-9); REQ Demands on the other viewpoints: Data (REQ-DAT-01–REQ-DAT-06), Integration (REQ-INT-01, REQ-INT-02, REQ-INT-03, REQ-INT-04, REQ-INT-06, REQ-INT-07), Platform (REQ-PLT-01–REQ-PLT-06); SEC Required security controls (SEC-1–SEC-4); Decision record (ADR-001–ADR-009); Glossary; front matter.

**Solution supporting sections read:** Inputs and technology sources; Data/Integration/Platform preambles; DAT-1 snapshot register, tax reproducibility, Fee immutability and RULE DAT-1.a–RULE DAT-1.h; DAT-2 Registered schemas; INT-1 Decisions on record; INT-2 Planned contracts; PLT-1 technology subsections; PLT-3 Cycle 0 exit proof; PLT-5 Retention tiers; Security — implemented controls; Satisfaction index; Constraint realisation; Target questions carried; Pending decisions (PEND-01–PEND-08); Deviations and exceptions; Self-check record; front matter.

**Sections absent:** none of the 17 supplied viewpoint sections. Presence does not resolve the sparse policies listed in §7.

**Nonexistent alternative labels:** APP-2.3, §4.2, OPEN-*, DEV-*, TB-*. The solution explicitly substitutes the APP-1 context map and a demand/control-derived PLT-6 register. REQ-INT-05 is absent from the numbering and is not invented. The source cross-reference REQ-E2 has no supplied definition; this strategy relies on the defined REQ-PLT-06 demand instead.

**External inputs absent:** roadmap, prior strategy, committed AC/epic baseline, Confluence space key and accessible Confluence tools. These are not absent architecture sections.

**traced_to:** target front matter and supporting sections; solution front matter and supporting sections.[1]​[2]