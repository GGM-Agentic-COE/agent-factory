# ADR-012 — Consume the competent authority's FBO register directly from Identity

| | |
| --- | --- |
| **Status** | **PROPOSED** — awaiting Enterprise Architect approval |
| **Date** | 2026-05-04 |
| **Cycle** | C1-producer-registration · PI-2026-Q2 |
| **Proposed by** | `L1-design-integration-architect@1.0.0` |
| **Gate** | Enterprise Architect |
| **Blocks** | `integration-architecture.delta.json` (1.0 → 2.0) and `platform-architecture.delta.json` (1.0 → 1.1) |

> This ADR exists because the integration delta is **structural**: it adds an edge to `foundational-solution-architecture.md` § APP-2.3. Additive and extending deltas touch component documents only and need no ADR. That asymmetry is what keeps the target stable enough to conform against.

---

## Context

`FR-003` requires a producer's declared Food Business Operator registration to be verified against the competent authority's register before that producer may publish a listing. Publication is the point of sale, so an unverified producer is not merely hidden — they are blocked from trading.

No HarvestLink bounded context can determine this fact for itself. It is external, it changes without notice to us, and it is the basis of a legal position: `kb-L2-food-domain` is explicit that an unknown eligibility must be treated as a refusal, because assuming eligibility lets an unvetted party create regulatory evidence.

No existing group system holds it either. `kb-L1-enterprise-architecture` EA3 records the group Compliance Document Store as SharePoint-based, manually uploaded, API-less, and **deliberately not integrated** — HarvestLink's traceability and allergen services are built standalone by explicit decision, not by oversight.

The FSA's APP-2.3 interaction map has six edges, all internal or outbound to a group system. It has no edge to any party outside the enterprise.

---

## Decision

`identity-service` calls the competent authority's register **directly**, out of band from the producer's registration transaction. The call is not routed through the group ESB.

Concretely:

- A registration is accepted and held `pending-verification` before any lookup is attempted, so the producer's submission never blocks on an external party.
- The lookup runs out of band. On `Verified` or `Invalid` the outcome is appended as evidence and an event is emitted; on no answer the registration stays pending and is retried.
- **There is no code path that promotes a pending registration to valid on a timeout.**

---

## Alternatives considered

### Route via the group ESB (MuleSoft) — *rejected*

EA2 mandates the API gateway for new digital products' **inbound** traffic and does not require the ESB for outbound third-party calls. Adding an ESB hop would place a Tier-1-adjacent shared component in the path of a new product's compliance check, coupling HarvestLink's verification availability to a system it neither owns nor funds.

### Manual verification by an operations team — *rejected*

`FR-003` gates publication. A manual step makes onboarding latency a staffing question, and leaves no evidence record carrying a verification timestamp — which is the artefact a dispute years later actually needs.

### Cache the register periodically and query the copy — *deferred, not rejected*

This is story-generator's open question `OQ-02`. A cached register makes eligibility decisions from stale data, and the domain rule is unambiguous: an unknown or stale eligibility is a refusal, never an optimistic assumption.

Deferred rather than rejected outright — **if the authority publishes a bulk feed, the trade changes.** Recorded so the option is reopened on that trigger rather than forgotten.

---

## Consequences

- **`APP-2.3` gains edge e7.** The FSA's interaction map now shows a dependency on a party outside the enterprise. Every future conformance run sees it.
- **A new contract category exists.** `fbo-register.lookup` is the first contract in this product owned by someone else. We cannot version-negotiate it, we do not set its deprecation timetable, `INT-9`'s expand-and-contract policy does not apply to us, and it cannot be stubbed from our own OpenAPI document.
- **`identity-service`'s 99.9% target does not extend to the register.** The product absorbs a register outage through the degraded mode — registrations stay pending — rather than by reporting its own availability as degraded. This is stated in `PLT-14` because the alternative is discovering it during an incident.
- **A new platform capability is required.** `PLT-6` has no row for outbound third-party egress, which fires the platform architect's conditional delta invocation (`HLD-F03`, `INTD-F01`). The egress gateway and its allowlist exist because of this decision.
- **The latency budget is unknown and stays unknown.** `INT-PEND-04`. Neither an NFR nor the authority supplies one, and a plausible figure written here would become the timeout the retry policy is built around.

---

## Approval

| Gate | Decision | Name | Date |
| --- | --- | --- | --- |
| Enterprise Architect | *pending* | | |

Until this row is completed, the integration and platform deltas do not merge and the egress IaC on `aava/platform-c1-egress` is not applied.
