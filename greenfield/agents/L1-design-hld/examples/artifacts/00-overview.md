# Feature Design Package — C1 Producer registration + FBO verification

**Cycle** `C1-producer-registration` · **PI** PI-2026-Q2 · **Features** F5.1, F1.1
**Run** `wf-hl-pi1-3c4d5e6f` · assembled by `L1-design-hld@1.0.0`

> **This file is the only original content in the package.** Everything else in `deltas/` is a diff against a document with a named canonical home, and everything in `additive/` is added and never merged. Nothing is authored twice, so nothing can drift.

---

## 1. Slice narrative

Cycle 1 makes a producer able to register, and makes the platform able to refuse one.

Two features ship together because neither is useful alone. **F5.1** gives external parties an identity — producers, distributors and buyers authenticate through the group-approved external IdP, never the employee directory. **F1.1** uses that identity to capture a producer's Food Business Operator registration and verify it against the competent authority's register before that producer can sell anything.

F1.1 was sized L and sliced. **S-F1.1-a** is the happy path through to a pending record: a producer submits a well-formed FBO number, ticks an attestation that they and not HarvestLink hold FBO status, and lands on a screen that explains what happens next. **S-F1.1-b** is the verification outcome, and it is the slice carrying the regulatory weight: a valid lookup records evidence and unblocks publication, an invalid one rejects and notifies, and a lookup that does not answer leaves the registration pending forever rather than guessing.

The last of those is the cycle's governing decision. There is no code path in this design that promotes a pending registration to valid on a timeout. An unknown eligibility is a deferral, never an optimistic assumption — assuming eligibility lets an unvetted party create regulatory evidence.

---

## 2. Cross-component sequence

```text
producer ──► external IdP                    : authenticate                    [F5.1]
producer ──► producer-portal                 : submit registration
producer-portal ──► identity-service         : POST /v1/producers/registrations
identity-service ──► identity-service        : validate format
identity-service ──► identity-service        : assert attestation  [server-side]
identity-service ──► identity_schema         : append pending-verification
identity-service ──► producer-portal         : 201 Created

                          ── out of band ──

identity-service ──► COMPETENT AUTHORITY FBO REGISTER : lookup(fbo_number)
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
                     crosses the product boundary — no APP-2.3 edge exists.
                     This is why the integration delta is STRUCTURAL (ADR-012).

  ├─ Verified  ──► identity_schema  : append valid, supersedes prior row
  │               ──► event broker   : identity.registration.verified
  ├─ Invalid   ──► identity_schema  : append rejected, reason passed through
  │               ──► event broker   : identity.registration.verified (rejected)
  └─ No answer ──► retry scheduler   : bounded retry
                  no row appended, no event emitted, status stays pending

event broker ──► notifications-worker        : consume
notifications-worker ──► producer            : outcome email
```

Three components, one external identity provider, one external register, one event. The sequence crosses producer-portal, identity-service, the event broker and notifications-worker — which is exactly why it lives here and is merged into `INT-4` as a canonical flow. No single component HLD can hold it.

---

## 3. Viewpoint assertion table

Checked by `gr-L1-viewpoint-completeness`. **A NONE with a stated reason passes; silence fails**, because an omission is indistinguishable from an oversight.

| Viewpoint | Assertion | Detail |
| --- | --- | --- |
| **APPLICATION** | DELTA | 3 creating HLD deltas + 3 creating LLD deltas (identity-service, producer-portal, notifications-worker), all additive, none structural |
| **DATA** | DELTA | `data-architecture.md` 1.0 → 1.1, extending. `register_reason` classified; `DAT-PEND-04` added; physical schema kept out and emitted as `db-schema.sql` |
| **INTEGRATION** | DELTA **(STRUCTURAL)** | `integration-architecture.md` 1.0 → 2.0. New edge to a party outside the product boundary; propagates to FSA `APP-2.3`; **ADR-012 required**, EA approval pending |
| **PLATFORM** | DELTA | `platform-architecture.md` 1.0 → 1.1, extending. `PLT-6` outbound third-party egress **NOT PRESENT → AVAILABLE**; new `egress-gateway` platform component |

All four assert DELTA. That is unusual and it is what a first cycle looks like — Cycle 1 touches everything.

**Component-level NONE assertions within APPLICATION**

| Component | Assertion | Reason |
| --- | --- | --- |
| catalogue-service | NONE | `INT-4.3` declares Catalogue as a consumer of `identity.registration-status`, but Catalogue does not consume it this cycle — no listing publication exists yet to gate |
| orders-service | NONE | No Cycle 1 Work Unit touches it |
| billing-service | NONE | No Cycle 1 Work Unit touches it |
| buyer-web | NONE | The public landing is unchanged |

---

## 4. NFR budget allocation

| Hop | Budget | Source |
| --- | --- | --- |
| `getRegistrationStatus` (identity-service) | p95 ≤ 250 ms | INT-4.3 |
| identity-service availability | 99.9% | ES4 — an FBO-status dispute is a regulatory-defence case |
| FoodSafetyRegistration retention | 6 years from creation | ES3 |
| FoodSafetyRegistration residency | approved PII region | ES9 |
| FBO register lookup | **PENDING** | No NFR supplies one and the authority publishes none — `INT-PEND-04` |

**The pending budget is a pending number, not a pending decision.** The behaviour on non-answer is decided: bounded retry, registration stays pending, never optimistically valid. A plausible "2 seconds" written here would become the timeout the retry policy is built around, derived from nothing.

`identity-service`'s 99.9% **does not extend to the competent authority's register**. The register's availability is outside this product's control; the product absorbs a register outage through the degraded mode rather than by reporting its own availability as degraded.

---

## 5. Package contents

```text
cycles/C1-producer-registration/
├── 00-overview.md                                  ← this file, the only original content
├── deltas/
│   ├── openapi.yaml                                → services/identity-service/openapi.yaml
│   ├── hld-identity-service.delta.json             → services/identity-service/hld.md
│   ├── hld-producer-portal.delta.json              → frontend/producer-portal/hld.md
│   ├── hld-notifications-worker.delta.json         → services/notifications-worker/hld.md
│   ├── lld-identity-service.delta.json             → services/identity-service/lld.md
│   ├── lld-producer-portal.delta.json              → frontend/producer-portal/lld.md
│   ├── lld-notifications-worker.delta.json         → services/notifications-worker/lld.md
│   ├── data-architecture.delta.json                → architecture/data-architecture.md
│   ├── db-schema.sql                               → services/identity-service/schema/
│   ├── integration-architecture.delta.json         → architecture/integration-architecture.md
│   ├── ADR-012-fbo-register-direct-consumption.md  → architecture/adr/ADR-012.md
│   ├── platform-architecture.delta.json            → architecture/platform-architecture.md
│   ├── hld-egress-gateway.delta.json               → platform/egress-gateway/hld.md
│   └── lld-egress-gateway.delta.json               → platform/egress-gateway/lld.md
└── additive/
    ├── user-journeys.md                            (never merged)
    └── wireframes.md                               (never merged)
```

Every file in `deltas/` names exactly one canonical destination, and no two name the same one.

---

## 6. Merge readiness

**Not ready.** ADR-012 is `PROPOSED`.

The integration delta is structural and propagates a new external edge to `foundational-solution-architecture.md`. The platform delta provisions the egress path that edge requires, and its IaC is committed but **not applied**. Neither merges until the Enterprise Architect approves.

The other twelve files are independently mergeable in principle and are held with them anyway — merging the application and data halves of a cycle whose integration half is unapproved would leave a component HLD describing a call the architecture has not authorised.

### Open items carried into the PR, none blocking

| ID | Summary |
| --- | --- |
| HLD-F02 | `producer-portal`'s RegistrationStatusView is designed and has no Work Unit. Raised at journey stage (UJ-F01), again at wireframe stage (WF-F01), again here |
| PLTD-F01 | `PLT-19`'s exit proofs contain nothing that exercises egress. A seventh proof is proposed, not added — amending a signed gate is the Platform Lead's call |
| DATD-F01 | `register_reason`'s Confidential classification is defensive, made without a single real register response |
| LLD-F03 | No test can prove the absence of an assume-valid branch. For the adversarial case writer: a malformed or ambiguous register response |
