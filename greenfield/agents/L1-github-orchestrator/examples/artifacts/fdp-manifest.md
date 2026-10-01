# FDP manifest — C1 Producer registration + FBO verification

Produced by `L1-github-orchestrator@1.0.0` · `exec-gho-1d2e3f4a`
Branch `aava/design-pi2026q2-c1-producer-registration` · commit `4f7be91` · PR #41

> **This is a manifest, not a copy.** The 17 files live with the agents that produced them; this document records where they went, what each one targets, and what the package as a whole is waiting on. Copying them here would be the second authorship the FDP structure exists to prevent.

---

## Package tree

```text
cycles/C1-producer-registration/
├── 00-overview.md                                  ← only original content
├── deltas/                                          (14 files, each with one destination)
└── additive/                                        (2 files, never merged)
```

## deltas/ — every file names one canonical destination

| File | Canonical destination | Type | Structural |
| --- | --- | --- | --- |
| `openapi.yaml` | `services/identity-service/openapi.yaml` | additive | no |
| `hld-identity-service.delta.json` | `services/identity-service/hld.md` | additive · creates | no |
| `hld-producer-portal.delta.json` | `frontend/producer-portal/hld.md` | additive · creates | no |
| `hld-notifications-worker.delta.json` | `services/notifications-worker/hld.md` | additive · creates | no |
| `lld-identity-service.delta.json` | `services/identity-service/lld.md` | additive · creates | no |
| `lld-producer-portal.delta.json` | `frontend/producer-portal/lld.md` | additive · creates | no |
| `lld-notifications-worker.delta.json` | `services/notifications-worker/lld.md` | additive · creates | no |
| `data-architecture.delta.json` | `architecture/data-architecture.md` | extending | no |
| `db-schema.sql` | `services/identity-service/schema/` | additive | no |
| `integration-architecture.delta.json` | `architecture/integration-architecture.md` | **structural** | **yes** |
| `ADR-012-fbo-register-direct-consumption.md` | `architecture/adr/ADR-012.md` | additive | no |
| `platform-architecture.delta.json` | `architecture/platform-architecture.md` | extending | no |
| `hld-egress-gateway.delta.json` | `platform/egress-gateway/hld.md` | additive · creates | no |
| `lld-egress-gateway.delta.json` | `platform/egress-gateway/lld.md` | additive · creates | no |

**No-duplicate-authorship check: PASS.** Fourteen files, fourteen distinct destinations, no collisions. Nothing in the package restates content that lives elsewhere.

**Eight creating deltas.** Cycle 1 is the first cycle for every component, so there was no current document to diff against. Each was taken as a delta against an empty document (`0.0.0 → 1.0.0`) rather than hand-authored, so the first version of each file arrives through the same reviewable mechanism as every later amendment.

## additive/ — never merged

| File | Reason |
| --- | --- |
| `user-journeys.md` | A journey map is a record of this cycle's design thinking, not an amendment to a standing document |
| `wireframes.md` | Same |

---

## Viewpoint completeness — `gr-L1-viewpoint-completeness` PASS

| Viewpoint | Assertion |
| --- | --- |
| APPLICATION | DELTA — 3 HLD + 3 LLD creating deltas; 4 components asserted NONE with reasons |
| DATA | DELTA — extending 1.0 → 1.1 |
| INTEGRATION | DELTA **(STRUCTURAL)** — 1.0 → 2.0, ADR-012 |
| PLATFORM | DELTA — extending 1.0 → 1.1, PLT-6 transition |

The gate blocks on an **omitted** viewpoint, not on a NONE. A NONE with a stated reason passes; silence fails, because an omission is indistinguishable from an oversight.

---

## Merge readiness — **not ready**

**Blocked by:** ADR-012 is `PROPOSED`.

The integration delta is structural and propagates a new external edge to `foundational-solution-architecture.md`. The platform delta provisions the egress path that edge requires. The other twelve files are independently mergeable in principle and are held with them anyway — merging the application and data halves of a cycle whose integration half is unapproved would leave a component HLD describing a call the architecture has not authorised.

Merge happens at **Phase 7.5**, after the PR lands. Committed is not merged: a delta merged at design time would make the baseline describe a system nobody has built.

### Related, not in this package

| | |
| --- | --- |
| `thornbury/harvestlink-platform` @ `aava/platform-c1-egress` | Egress gateway IaC, 6 files. **Committed, not applied.** |

### Open items in the PR body — none blocking

| ID | Summary |
| --- | --- |
| HLD-F02 | `producer-portal`'s RegistrationStatusView is designed and has no Work Unit. Third stage it has survived — UJ-F01, WF-F01, now a component HLD |
| PLTD-F01 | `PLT-19`'s exit proofs contain nothing that exercises egress; a seventh proof is proposed, not added |
| DATD-F01 | `register_reason`'s Confidential classification is defensive, made without a real register response |
| LLD-F03 | No test can prove the absence of an assume-valid branch |

---

## Published to Confluence — space `HLARCH`

| Page | Source | ID |
| --- | --- | --- |
| C1 — Producer registration: Overview | `00-overview.md` | 884736 |
| C1 — Producer journeys | `additive/user-journeys.md` | 884737 |
| C1 — Wireframes | `additive/wireframes.md` | 884738 |
| ADR-012 *(banner: PROPOSED)* | `deltas/ADR-012-…md` | 884739 |

**Not published:** the 10 delta JSON files and `db-schema.sql`. A delta is a diff against a document with a canonical home; publishing diffs to a wiki gives readers a second place to look and a worse one — current for about a week, and then the version somebody finds first.
