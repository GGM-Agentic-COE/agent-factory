# HarvestLink — User Journeys · Cycle 1

**Feature Design Package** `C1-producer-registration` · `additive/user-journeys.md`
Produced by `L1-design-user-journey-mapper@1.0.0` · `exec-ujm-2a3b4c5e`

> **Additive.** This document is added to the Feature Design Package and is never merged into a canonical document. It has no delta, no version bump and no canonical destination — which is why this agent, unlike the four viewpoint agents, does not run in delta mode.

---

## Personas

| Persona | In scope | Reason |
| --- | --- | --- |
| **P-01 Producer** | **Yes** | Every Cycle 1 story gives the producer something to do |
| P-02 Foodservice buyer | No | No Cycle 1 story touches the buyer. Buyer discovery is F2.1, roadmap band 4 |
| P-03 Distributor / logistics | No | F5.1 provisions distributor roles, but no Cycle 1 story gives a distributor a task |
| P-04 Certification / audit body | No | Evidence read access is INT-PEND-03, not yet scoped |

Named rather than omitted. A persona silently absent from a journey map is indistinguishable from one nobody thought about.

**P-01 in context** — small food producer, typically 1–5 people. Low technical capability: web UI, occasional CSV. Often on a phone, often outdoors, rarely at a desk. Holds Food Business Operator status; HarvestLink does not. *(kb-L2-food-domain FD2)*

---

## UJ-01 — Producer registers and waits for eligibility

**Trigger** A producer has heard about HarvestLink and wants to sell.
**Success** Registered, verified, able to publish a listing.
**Failure** Registered, rejected, and knows why and what to do next.
**Spans** F5.1 · S-F1.1-a · S-F1.1-b

```text
 1  arrive          TP-01  ──►  2  authenticate   TP-02  ──►  3  fill form      TP-03
                                                                    │
                                                                    ▼
 5  pending state   TP-04  ◄──  4  attest         TP-03  ◄──────────┘
        │
        ├──► 6  try to publish → blocked, reason stated        TP-04
        │
        ├──► 7   verified   → publication permitted            TP-05
        ├──► 7a  rejected   → notified with reason             TP-05
        └──► 7b  no answer  → stays pending, indistinguishable TP-04
```

### Steps

| # | Actor | Action | Touchpoint | System response | Covers |
| --- | --- | --- | --- | --- | --- |
| 1 | Producer | Arrives and chooses to sign up | TP-01 | Redirected to the external IdP | F5.1-AC1 |
| 2 | Producer | Authenticates with the external IdP | TP-02 | Session established; role provisioned from the onboarding record | F5.1-AC1, F5.1-AC2 |
| 3 | Producer | Completes business details and FBO number | TP-03 | Field-level validation on the FBO number format | S-F1.1-a-AC1, AC2 |
| 4 | Producer | Reads and ticks the FBO-status attestation | TP-03 | Submission refused if unticked — server-side, not merely hidden in the UI | S-F1.1-a-AC3 |
| 5 | System | Accepts and holds pending-verification | TP-04 | Explicit pending state with what happens next | S-F1.1-a-AC1, AC4 |
| 6 | Producer | Attempts to publish while pending | TP-04 | Blocked, reason stated as "verification in progress" | S-F1.1-a-AC4 |
| 7 | System | FBO lookup returns valid | TP-05 | Registration valid, evidence recorded, producer notified | S-F1.1-b-AC1 |
| 7a | System | FBO lookup returns invalid | TP-05 | Rejected, notified with reason, publication stays blocked | S-F1.1-b-AC2 |
| 7b | System | FBO lookup does not answer | TP-04 | Stays pending and retries; producer sees the same pending state | S-F1.1-b-AC3 |

### Notes that shaped the design

- **Step 1** is the highest abandonment risk in the journey. The producer has no account and no investment in the outcome.
- **Step 3** — the producer may not have their FBO number to hand. The journey must survive being abandoned here and resumed later.
- **Step 4** is what the entire facilitation-only regulatory position rests on. It is a deliberate act by an identified party, and the UI must not let it feel like boilerplate.
- **Step 5** — the producer has finished their part and cannot act further. An unexplained wait is read as failure.
- **Step 6** — a blocked action that does not explain itself generates the support contact this step exists to prevent.
- **Step 7b** — from the producer's side a timeout and a slow answer are indistinguishable, and deliberately so. An unknown eligibility must never be presented as a provisional yes.

---

## Touchpoints

| ID | Name | Channel | Owning component | New | Work Unit |
| --- | --- | --- | --- | --- | --- |
| TP-01 | Public landing | web | buyer-web | No | — |
| TP-02 | External IdP authentication | redirect | external IdP | Yes | WU-F5.1-01 |
| TP-03 | Registration form | web | producer-portal | Yes | WU-F1.1-03 |
| TP-04 | Registration status screen | web | producer-portal | Yes | **UNASSIGNED** — UJ-F01 |
| TP-05 | Verification outcome notification | email | notifications-worker | Yes | WU-F1.1-06 |

---

## Coverage

11 acceptance criteria in scope; 10 reached by a journey step.

**Not reached — correctly.** `S-F1.1-b-AC4` (duplicate verification delivery) has no user-visible surface. The producer cannot perceive a deduplicated event, and inventing a step for it would put a system concern into a persona's path.

---

## Findings

### UJ-F01 · MEDIUM — a screen the journey needs and no Work Unit builds

TP-04 carries steps 5, 6 and 7b — the entire pending state, including the blocked-publication explanation. `S-F1.1-a-AC4` covers the blocking behaviour and `WU-F1.1-04` implements the gate as business logic, but no Work Unit owns the producer-facing surface that shows it.

*Not resolved here.* This agent does not mint Work Units, and folding the status screen into `WU-F1.1-03`'s registration form would breach T1 — a form and a status screen are two nameable objectives. Raised to task-generator and the cycle planner.

### UJ-F02 · LOW — no resumption path, and step 3 predicts abandonment

A producer without their FBO number to hand will leave the form. Nothing in the Cycle 1 stories describes what they return to: a saved draft, a fresh form, or an expired session.

*Not resolved here.* No acceptance criterion covers resumption and none was invented.

### UJ-F03 · LOW — OQ-01 has a visible journey consequence

Story-generator's open question — what happens when a verified registration later lapses — is not an abstract gap. It is a journey with no map: a producer who has published listings and whose registration then lapses appears nowhere in UJ-01, and those listings are already visible to buyers.

*Strengthens OQ-01 rather than answering it.* Journey mapping surfaced a consequence the requirement did not state.

---

## Guardrails

**gr-L1-consistency-check — pass.** Every step's system response was compared against the acceptance criterion it claims to cover. One correction during authoring: step 7b's draft had the status screen show "verification delayed", which contradicts `S-F1.1-b-AC3`. A producer told their verification is delayed has been told something the system does not know.
