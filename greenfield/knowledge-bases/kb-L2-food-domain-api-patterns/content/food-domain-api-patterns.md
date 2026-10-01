<!--
kb-L2-food-domain-api-patterns · content · food-domain-api-patterns.md
Layer: L2 (domain — food supply chain / producer marketplace). Integration
patterns that recur in this domain specifically: who the participants are,
what a trade event means, which flows genuinely cannot be asynchronous, and
what regulatory traceability does to contract versioning.

This is the SWAPPABLE half of L1-design-integration-architect. The agent is
domain-agnostic; this KB is what makes its output domain-aware. Deploying
the framework against a different domain replaces this file with that
domain's KB and changes nothing in the agent.

Illustrative content for the reference scenario. Cross-references
kb-L1-enterprise-architecture (estate, EA2/EA3 integration boundaries) and
kb-L1-enterprise-security (ES1 identity, ES9 residency) rather than
duplicating either. States PATTERNS and their rationale — it does not
name a bus, a gateway or a broker product; those belong to the platform
viewpoint.
-->

# Food Supply Chain & Producer Marketplace — Integration Patterns (L2)

## FD1: What is distinctive about integration in this domain

Three properties drive nearly every integration decision here, and none of
them are obvious from a generic marketplace framing:

1. **Physical goods move independently of the digital record.** The platform
   is not the source of truth for whether a pallet arrived. Integration must
   tolerate the digital record and the physical world disagreeing, and must
   never resolve that disagreement by assuming.
2. **Some records are regulatory evidence, not application state.** A
   traceability sign-off or an allergen declaration may be produced in a
   dispute years later. Evidence records are append-only, and an integration
   that can lose or silently re-order them is a compliance failure, not a
   reliability one.
3. **Participants are external parties with uneven technical capability.** A
   producer may be a two-person farm; a distributor may have an established
   EDI estate. The integration surface must not assume both.

## FD2: Participant model and trust boundaries

| Participant | Typical capability | Integration posture |
|---|---|---|
| Producer | Low — web UI, occasional CSV | UI-first; any API is a convenience, never the only path |
| Distributor / logistics | Medium-high — existing EDI or file estate | API + scheduled file exchange as a transitional pattern with an exit plan |
| Foodservice buyer | Medium — procurement systems | API; may require a buyer-side purchase-order correlation identifier carried end to end |
| Certification / audit body | Low, read-oriented | Read-only, time-scoped access to evidence; never write access |
| Internal enterprise systems | Per `kb-L1-enterprise-architecture` EA3 | Read-only or outbound-only as EA3 states; never a write-back from a new digital product |

**Every one of these crosses a trust boundary.** At each boundary, caller
identity is re-established (`kb-L1-enterprise-security` ES1 — external
parties never on the employee IdP), authorisation is applied, and correlation
information is preserved. An identity established at the edge is not
implicitly trusted two hops in.

## FD3: Canonical event taxonomy

Events in this domain fall into four kinds, and conflating them is the most
common modelling error. The distinction drives retention, ordering and replay
policy — not just naming.

| Kind | Meaning | Ordering | Retention | Replayable |
|---|---|---|---|---|
| **Lifecycle** | A domain object changed state (`listing.published`, `order.placed`) | Per aggregate | Application policy | Yes |
| **Evidence** | Something legally assertable happened (`traceability.signed-off`, `allergen.declared`) | Per aggregate, strict | Regulatory (see ES3) | **No — replay is re-assertion** |
| **Movement** | Physical world reported something (`consignment.dispatched`, `consignment.received`) | Best-effort; late and out-of-order arrivals are normal | Application policy | Yes |
| **Notification** | A side effect for a human (`payout.scheduled`) | None | Short | Yes, idempotently |

**Evidence events are the trap.** Replaying an evidence event does not
re-deliver a fact; it asserts the fact a second time, with a second
timestamp. A consumer that treats evidence like lifecycle will produce two
audit records for one real-world act. Every evidence event therefore carries
a deduplication key derived from the business act, not from the message.

**Naming.** `{context}.{entity}.{event}` — lowercase, dot-separated, past
tense for the event segment. The context segment is a bounded context name,
never a team, a system or a product.

## FD4: Synchronous vs asynchronous — the domain's actual decision table

Asynchronous is the default (`PRIN-03`). These are the flows where that
default is genuinely wrong, and the reason in each case:

| Flow | Style | Why |
|---|---|---|
| Availability / stock check before order creation | **Synchronous** | The buyer cannot be told "your order may exist"; the answer is needed inside the transaction |
| Price or fee shown at confirmation | **Synchronous** | A figure displayed at confirmation must be the figure charged; eventual consistency here is a mis-selling risk, not a staleness one |
| Eligibility / certification check gating a write | **Synchronous** | An ineligible party must be refused at the point of action, not compensated afterwards |
| Order placed → financial processing | Asynchronous | Downstream availability must not gate order capture |
| Evidence recorded → notification | Asynchronous | A side effect, never in the critical path |
| Movement reported → downstream visibility | Asynchronous | Late and out-of-order by nature; forcing sync would make the platform's availability depend on a lorry |
| Aggregate metrics → enterprise reporting | Asynchronous, outbound-only | `kb-L1-enterprise-architecture` EA3 — one-way, no read dependency back |

Every synchronous edge above still owes a latency budget, a timeout, a retry
policy and a **degraded mode**. The degraded mode in this domain is almost
never "proceed on the last known value": an unknown availability, an unknown
fee or an unknown eligibility is a refusal or a deferral, never an optimistic
assumption. Assuming availability sells goods that do not exist; assuming
eligibility lets an unvetted party create regulatory evidence.

## FD5: Contract versioning under regulatory change

Regulatory change in this domain arrives as *new mandatory fields on
existing records*, far more often than as new endpoints. That shapes
versioning:

- A newly mandated evidence field is an **additive change to the contract and
  a breaking change to the business meaning**: old records genuinely lack it.
  Version the contract additively; never backfill a value that was not
  captured, and never default it.
- Expand-and-contract is the only permitted path for a breaking change:
  provider supports old and new → consumers migrate → old deprecated → old
  removed. A provider release must not break an existing consumer.
- An evidence contract's version MUST be recorded **on the stored record**,
  not only on the message. Years later, the question "which rules applied
  when this was signed?" is answerable only from the record.
- Deprecation windows for external-party contracts are longer than for
  internal ones — a two-person producer does not have a migration sprint.

## FD6: Partner and file-based integration

File exchange is not an approved integration style (`PRIN-03`), and it will
still be asked for. The governed pattern, where it is unavoidable:

- Treat the file as a **transport for a contract**, not as an absence of one:
  the schema is versioned, owned and published exactly as an API would be.
- Ingest converts the file into domain events at the boundary; no downstream
  consumer ever learns that a file was involved.
- The exchange is registered with an owner, a schedule, a duplicate-handling
  rule and an **exit plan with a date** — recorded as a `TRANSITIONAL`
  exception (`PRIN-03`), never as a permanent style.
- Residency applies to the file and its staging copies exactly as to the
  entity (`kb-L1-enterprise-security` ES9).

## FD7: Duplicate handling, idempotency and recovery

Every asynchronous consumer in this domain declares all five:

```text
duplicate handling      — the deduplication key, and what it is derived from
idempotency             — what "already applied" means for this consumer
retry strategy          — bounded; with what backoff
dead-letter path        — where a poison message goes, and who looks at it
replay policy           — for evidence events, the policy is usually "never"
```

Domain-specific rules:

- A deduplication key for a **trade or evidence** event derives from the
  business act (party + subject + business timestamp), never from a
  message id a producer might regenerate on retry.
- A **movement** event arriving twice, or out of order, is expected — the
  consumer reconciles on a monotonic business state, it does not reject.
- A poison evidence event is **never** silently dropped. It goes to a
  dead-letter path with a named human owner, because the underlying
  real-world act still happened.

## FD8: Integration observability in this domain

Beyond the standard correlation id, trace id, latency and error metrics
(`PRIN-08`), this domain needs two more, and they are usually forgotten:

- **Evidence-chain completeness** — for a consignment or a trade, can the
  full evidence chain be reconstructed from events alone? A gap is a
  compliance finding, and it must be detectable before a regulator finds it.
- **External-party contract-version distribution** — which producers and
  distributors are still on a deprecated contract version. Without it, a
  deprecation date is a guess about who it will break.

## FD9: Glossary

- **Evidence record** — a record that may be produced to a regulator or in a dispute; append-only, retained per ES3.
- **Consignment** — a physical shipment of goods, tracked independently of the order that caused it.
- **Traceability sign-off** — an assertion, by an identified party, that a consignment's provenance chain is complete.
- **FBO** — Food Business Operator; the party legally accountable for a food product at a point in the chain.
- **Allergen declaration** — a legally significant statement of allergen content attached to a product or listing.
- **Deduplication key** — a value derived from the business act, used to recognise a repeated delivery of the same real-world event.
- **Degraded mode** — the defined behaviour when a synchronous dependency fails; in this domain, a refusal or deferral, not an optimistic assumption.

---
*Last reviewed: 2026-09-22 · Review cadence: quarterly (regulatory field
requirements and partner integration capability change faster than the
participant model). Illustrative content for the reference scenario — replace
wholesale when deploying against a different domain; the agent does not
change.*
