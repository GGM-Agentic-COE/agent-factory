# High-Level Design (HLD)
**Document Version:** 1.0.0
**Baseline Reference:** `kb-L1-enterprise-architecture` v2.1
**Feature Coverage:** F-03.1, F-03.2, F-03.3 (committed, Cycle 4) · F-03.4, F-03.5 (designed, not built — see §8)
**Stack:** Python 3.12 + FastAPI + PostgreSQL 16 (target) / SQLite (Cycle 4) · React 18 + TypeScript + Vite (frontend)
**Correlation ID:** `wf-3c9e1a52-7b4d-4f0e-9a61-d25b8c04e7f3`

---

## 0. Revision note

Initial version (1.0.0). Covers the ClinicFlow Appointments module (EP-03) as built for the Cycle 4
advisory-board demo: booking, clinician confirm/decline and patient cancel, set against the
enterprise target in `kb-L1-enterprise-architecture` v2.1. Derived from `prd.md` v1.2,
`platform-architecture.md` v1.0, `data-architecture.md` v1.0 and `integration-architecture.md` v1.0.
One open conflict between the PRD and the data architecture (cancellation window) is recorded in
§2.3, §3 and the open questions rather than resolved silently.

---

## 1. System Component Diagram

```
          ┌──────────────────┐                ┌──────────────────┐
          │  Patient Browser │                │ Clinician Browser│
          │  React 18 SPA    │                │  same SPA,       │
          │                  │                │  /clinician route│
          └────────┬─────────┘                └────────┬─────────┘
                   │  target: HTTPS · MVP: plain HTTP  │
                   └─────────────────┬─────────────────┘
                                     ▼
                  ┌─────────────────────────────────────┐
                  │  Ingress                              │
                  │  target: AWS ALB, TLS 1.3, rate limits│
                  │  MVP:    none — direct localhost, §8  │
                  └──────────────────┬──────────────────┘
                                     │
          ┌──────────────────────────┴──────────────────────────┐
          ▼                                                      ▼
┌───────────────────────────┐   REST /v1, auth   ┌───────────────────────────┐
│  patient-portal             │◀- - - header - - ->│  appointments-api           │
│  React 18 · TS · Vite       │                    │  FastAPI · uvicorn          │
│  target: nginx, EKS HPA 2-6 │                    │  target: EKS HPA 2-10       │
│  MVP: npm run dev :5173     │                    │  MVP: one process :8000    │
└───────────────────────────┘                    └─────────────┬─────────────┘
                                                                 ▼
                                               ┌───────────────────────────────┐
                                               │  AuthMiddleware                  │
                                               │  target: Cognito OIDC RS256 JWT  │
                                               │  MVP:    X-Demo-User header vs   │
                                               │          seeded users — MOCKED §8│
                                               └───────────────┬───────────────┘
                                                               ▼
                                               ┌───────────────────────────────┐
                                               │  /v1/appointments routes         │
                                               │  book · confirm · decline ·      │
                                               │  cancel · list                   │
                                               └───────────────┬───────────────┘
                                                               ▼
                                               ┌───────────────────────────────┐
                                               │  Appointment lifecycle logic     │
                                               │  idempotency · status guards     │
                                               └───┬──────────┬──────────┬──────┘
                                                   │          │          │
                     ┌─────────────────────────────┘          │          └──────────────────────┐
                     ▼                                         ▼                                 ▼
┌───────────────────────────────┐   ┌───────────────────────────────┐   ┌───────────────────────────────┐
│  FhirSchedulingConnector        │   │  Primary datastore              │   │  NotificationConnector          │
│  target: sync FHIR R4 Slot read │   │  target: PostgreSQL 16 RDS,     │   │  target: in-app + Twilio SMS    │
│  MVP: seeded JSON — MOCKED §8   │   │          Multi-AZ, KMS at rest  │   │  MVP: console log — MOCKED §8   │
└───────────────┬───────────────┘   │  MVP: SQLite file, unencrypted §8│   └───────────────────────────────┘
                │ target only        └───────────────┬───────────────┘
                ▼                                     ▲
┌───────────────────────────────┐                     │ - -> target: slot availability, 15 s TTL
│  EHR FHIR endpoint (external)   │   ┌───────────────────────────────┐
│  MVP: not called — §8           │   │  Slot cache                     │
└───────────────────────────────┘   │  target: Redis (ElastiCache)    │
                                      │  MVP: not used — §8             │
                                      └───────────────────────────────┘

  Appointment lifecycle logic - -> Event bus (target: EventBridge `clinicflow-events`,
                                    AppointmentConfirmed / AppointmentCancelled · MVP: not implemented, §8)
```

**What changed vs. a from-scratch design:** Appointments is a net-new module; no existing ClinicFlow
service books appointments. The genuinely open integration points are external — the EHR scheduling
source of record (stubbed with seeded slots), the notification provider (console only) and the
analytics event bus (absent). All three sit behind connector interfaces (ABP-04), so swapping stubs
for real calls does not change the routes or lifecycle logic. The double-booking guard is internal
and real today: a partial unique index enforced in the database.

---

## 2. Data Flow Diagrams

### 2.1 Book appointment [F-03.1 · UF-1]

Participants: Patient Browser | AuthMiddleware (target: Cognito JWT, MVP: X-Demo-User) |
/v1/appointments routes | Appointment lifecycle logic | FhirSchedulingConnector (mock) |
Primary datastore | NotificationConnector (mock)

```
1. Patient Browser   ──POST /v1/appointments {clinicianId, slotId, idempotencyKey}──▶  AuthMiddleware
2. AuthMiddleware    ──caller = PATIENT (see §5)──▶                                   /v1/appointments routes
3. routes            ──book(cmd)──▶                                                   Lifecycle logic
4. Lifecycle logic   ──lookup idempotency_key──▶                                      Primary datastore
   ├─ [key already used]
   │    5. Lifecycle logic ──return original appointment, no insert──▶                Patient Browser
   └─ [new key]
        6. Lifecycle logic ──isSlotFree(slotId) [MOCK]──▶                             FhirSchedulingConnector
           ├─ [slot not free]
           │    7. Lifecycle logic ──409 "slot no longer available"──▶                 Patient Browser
           └─ [slot free]
                8. Lifecycle logic ──INSERT appointment(status=REQUESTED)──▶          Primary datastore
                   ├─ [partial unique index on slot_id violated — concurrent booking]
                   │    9. Lifecycle logic ──409 "slot no longer available"──▶        Patient Browser
                   └─ [insert succeeds]
                        10. Lifecycle logic ──notify(clinician, REQUESTED) [MOCK]──▶  NotificationConnector
                        11. Lifecycle logic ──created appointment──▶                  Patient Browser
```

### 2.2 Confirm or decline [F-03.2 · UF-2]

Participants: Clinician Browser | AuthMiddleware | /v1/appointments routes | Lifecycle logic |
Primary datastore | NotificationConnector (mock)

```
1. Clinician Browser ──POST /v1/appointments/{id}/confirm | /decline──▶   AuthMiddleware
2. AuthMiddleware    ──caller = CLINICIAN, own schedule (see §5)──▶       /v1/appointments routes
3. routes            ──confirm(id) | decline(id)──▶                       Lifecycle logic
4. Lifecycle logic   ──load appointment──▶                                Primary datastore
   ├─ [status ≠ REQUESTED]
   │    5. Lifecycle logic ──rejected, no transition──▶                   Clinician Browser
   └─ [status = REQUESTED]
        ├─ [confirm]
        │    6. Lifecycle logic ──UPDATE status=CONFIRMED──▶              Primary datastore
        │    7. Lifecycle logic ──notify(patient, CONFIRMED) [MOCK]──▶    NotificationConnector
        │       (target only: publish AppointmentConfirmed - -> event bus — not implemented, §8)
        └─ [decline]
             8. Lifecycle logic ──UPDATE status=DECLINED (slot released)──▶ Primary datastore
             9. Lifecycle logic ──notify(patient, DECLINED) [MOCK]──▶     NotificationConnector
10. Lifecycle logic ──updated appointment──▶                              Clinician Browser
```

### 2.3 Patient cancels [F-03.3 · UF-3]

Participants: Patient Browser | AuthMiddleware | /v1/appointments routes | Lifecycle logic |
Primary datastore | NotificationConnector (mock)

```
1. Patient Browser ──POST /v1/appointments/{id}/cancel──▶                 AuthMiddleware
2. AuthMiddleware  ──caller = PATIENT, own appointment (see §5)──▶        /v1/appointments routes
3. routes          ──cancel(id)──▶                                        Lifecycle logic
4. Lifecycle logic ──load appointment──▶                                  Primary datastore
   ├─ [status is DECLINED / CANCELLED / COMPLETED]
   │    5. Lifecycle logic ──rejected, no transition──▶                   Patient Browser
   ├─ [status = CONFIRMED and slot starts < 24 h from now]   ← PRD says 24 h; data arch says 12 h — OQ-01
   │    6. Lifecycle logic ──rejected, "please call the clinic"──▶        Patient Browser
   └─ [status = REQUESTED, or CONFIRMED and ≥ 24 h before start]
        7. Lifecycle logic ──UPDATE status=CANCELLED (slot released)──▶   Primary datastore
        8. Lifecycle logic ──notify(clinician, CANCELLED) [MOCK]──▶       NotificationConnector
           (target only: publish AppointmentCancelled - -> event bus — not implemented, §8)
        9. Lifecycle logic ──updated appointment──▶                       Patient Browser
```

---

## 3. Appointment State Machine [F-03.1, F-03.2, F-03.3 · BL]

```
        patient books (F-03.1)
       ───────────────────────────▶ ┌──────────────┐
                                     │  REQUESTED    │
                                     └──┬────┬────┬─┘
             clinician confirms         │    │    │   patient cancels
             (F-03.2)          ┌────────┘    │    └────────────┐  (F-03.3)
                               ▼             │ clinician        ▼
                      ┌──────────────┐       │ declines  ┌──────────────┐
                      │  CONFIRMED    │       │ (F-03.2)  │  CANCELLED    │
                      └──┬────────┬──┘       ▼           │  (terminal)   │
                         │        │   ┌──────────────┐   └──────────────┘
                         │        │   │  DECLINED     │           ▲
                         │        │   │  (terminal)   │           │
                         │        │   └──────────────┘           │
                         │        └──── patient cancels, guard: ≥ 24 h before start (OQ-01) ───┘
                         │
                         │ visit checked in (Cycle 8 — not built)
                         ▼
                ┌──────────────┐
                │  COMPLETED    │
                │ (not built)   │
                └──────────────┘
```

CONFIRMED has no outbound transition other than cancel in Cycle 4 — the check-in transition to
COMPLETED is designed but has no code path (GAP-10). DECLINED and CANCELLED release the slot.

### State summary

| State | Reachable from | Clinician confirm/decline allowed | Patient cancel allowed |
|---|---|---|---|
| REQUESTED | Patient books | Yes | Yes |
| CONFIRMED | Clinician confirms | No | Yes, only ≥ 24 h before start (PRD; data arch says 12 h — OQ-01) |
| DECLINED | Clinician declines | No | No (terminal) |
| CANCELLED | Patient cancels | No | No (terminal) |
| COMPLETED | Check-in — not reachable in Cycle 4 | No | No (terminal) |

---

## 4. Deployment View

### 4.1 Target (per `kb-L1-enterprise-architecture` EA-06, EA-04)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  EKS Cluster                                                                  │
│                                                                                │
│  ┌──────────────────────── Namespace: appointments ────────────────────────┐ │
│  │                                                                          │ │
│  │   ┌──────────────────────┐          ┌──────────────────────┐            │ │
│  │   │ patient-portal        │          │ appointments-api      │            │ │
│  │   │  Pod 1 ... Pod n      │          │  Pod 1 ... Pod n      │            │ │
│  │   │  HPA 2-6              │          │  HPA 2-10             │            │ │
│  │   └──────────┬───────────┘          └──────────┬───────────┘            │ │
│  │              └───────────────┬──────────────────┘                        │ │
│  │                              ▼                                           │ │
│  │                    ┌─────────────────────┐                               │ │
│  │                    │  ALB Ingress         │                               │ │
│  │                    │  TLS 1.3             │                               │ │
│  │                    │  Read: 300/min/user  │                               │ │
│  │                    │  Write: 60/min/user  │                               │ │
│  │                    └─────────────────────┘                               │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│                                                                                │
│  ┌──────────────────────── Shared data services ───────────────────────────┐ │
│  │   ┌──────────────────────┐   ┌──────────────────────┐                   │ │
│  │   │ PostgreSQL 16 (RDS)   │   │ Redis (ElastiCache)   │                   │ │
│  │   │ Multi-AZ, KMS at rest │   │ slot cache, 15 s TTL  │                   │ │
│  │   │ schema: appointments  │   └──────────────────────┘                   │ │
│  │   └──────────────────────┘                                              │ │
│  └──────────────────────────────────────────────────────────────────────────┘ │
│   External: EHR FHIR endpoint · Twilio · EventBridge bus `clinicflow-events`  │
└─────────────────────────────────────────────────────────────────────────────┘
```

| Service | Image base | Port | Resources (request/limit) | Probes |
|---|---|---|---|---|
| patient-portal | `nginx:1.27-alpine` | 80 | 100m/300m CPU · 128Mi/256Mi | `/` |
| appointments-api | `python:3.12-slim` | 8000 | 250m/1000m CPU · 256Mi/512Mi | `/healthz` (implemented in Cycle 4) |

### 4.2 MVP reality (this repo, right now)

```
┌────────────────────────┐        ┌─────────────────────────┐
│  npm run dev (Vite)     │        │  uvicorn                 │
│  patient-portal         │──────▶│  appointments-api        │
│  http://localhost:5173  │  REST  │  http://localhost:8000  │
│  (single process,       │  HTTP  │  (single process,        │
│   hot reload)           │        │   /healthz returns 200)  │
└────────────────────────┘        └────────────┬────────────┘
                                                 │
                                       ┌─────────▼──────────┐
                                       │  SQLite file         │
                                       │  clinicflow.db       │
                                       │  (unencrypted,       │
                                       │   synthetic data)    │
                                       └─────────────────────┘
```
No EKS, no ALB, no TLS, no HPA, no RDS, no Redis, no EventBridge — two local processes and a
SQLite file, by design for the Cycle 4 demo on synthetic data. §8 is the authoritative gap list.

---

## 5. Security View

Participants: Browser | AuthMiddleware | Protected Endpoint
target: Cognito OIDC RS256 JWT, roles from `cognito:groups` (EA-05) · MVP: `X-Demo-User` header
mapped to a seeded user table — no signature, no expiry, NOT a real auth scheme, see §8 (GAP-01)

```
1. Browser  ──any /v1/* request + X-Demo-User (MVP) | Bearer JWT (target)──▶   AuthMiddleware
   ├─ [OPTIONS preflight]
   │    2. AuthMiddleware ──pass through (CORS)──▶                               Browser
   └─ [non-OPTIONS]
        3. AuthMiddleware ──resolve caller (seeded users | validate JWT)──▶ (self)
           ├─ [no matching user]
           │    4. AuthMiddleware ──401──▶                                       Browser
           └─ [user found]
                5. AuthMiddleware ──attach currentUser + role──▶                 Protected Endpoint
                6. Protected Endpoint ──RBAC: PATIENT = own appointments;
                   CLINICIAN = own schedule──▶ (self)
                   ├─ [authorized]      7. Protected Endpoint ──2xx──▶          Browser
                   └─ [not authorized]  7. Protected Endpoint ──403──▶          Browser
```

### Encryption boundaries

| Boundary | Target (EA-05, EA-04) | MVP reality |
|---|---|---|
| Browser → API | TLS 1.3 at ALB | Plain HTTP, localhost only |
| API → Database | TLS to RDS; KMS encryption at rest | N/A in transit (local file); no encryption at rest |
| Auth token | RS256 JWT issued by Cognito | Unsigned `X-Demo-User` header |

### Authorization matrix (as actually enforced in code)

| Endpoint | PATIENT | CLINICIAN |
|---|---|---|
| `POST /v1/appointments` | Own patient id only | Forbidden (403) |
| `POST /v1/appointments/{id}/confirm` | Forbidden (403) | Own schedule only |
| `POST /v1/appointments/{id}/decline` | Forbidden (403) | Own schedule only |
| `POST /v1/appointments/{id}/cancel` | Own appointment only | Forbidden (403) |
| `GET /v1/appointments` | Own appointments only | Own schedule only |

---

## 6. Observability

| Signal | Target (EA-09) | MVP reality |
|---|---|---|
| Structured logs | JSON, correlation id per line | uvicorn default access logs to console |
| Metrics | prometheus-fastapi-instrumentator → Prometheus | Not instrumented |
| Health probes | `/healthz` liveness/readiness | **In place** — `/healthz` returns 200 |
| Tracing | OpenTelemetry | Not instrumented |
| PHI access audit trail | Every appointment read/write → central audit store (NFR-5) | Not implemented |

---

## 7. NFR Compliance Summary

| NFR (from PRD) | Target | MVP status |
|---|---|---|
| NFR-1 Booking P95 ≤ 400 ms | No mechanism stated beyond the Redis slot cache (EA-04) | **Not tested** — no load test or metrics in Cycle 4; Redis absent (GAP-06) |
| NFR-2 No double-booking, incl. concurrent | Partial unique index on `slot_id` for REQUESTED/CONFIRMED | **Met** — index applied in SQLite migration `002_slot_unique.sql` |
| NFR-3 99.9% availability | EKS HPA, RDS Multi-AZ | **Not applicable** — single local process has no HA story (GAP-04) |
| NFR-4 PHI encrypted at rest | RDS with KMS (ABP-03) | **Not met** — SQLite file unencrypted; risk contained by synthetic-only data (GAP-05) |
| NFR-5 Access audit log | Audit store (EA-09) | **Not met** — no audit logging (GAP-09) |

---

## 8. Gap Register — Target Architecture vs. This Build

| # | Gap | Target (EA reference) | Owner of the resolution |
|---|---|---|---|
| GAP-01 | Auth is an unsigned `X-Demo-User` header, not Cognito JWT | EA-05 | Identity team — replace `AuthMiddleware` resolution with JWT validation |
| GAP-02 | EHR slot check is a stub over seeded JSON; EHR never called | EA-08 | Integration squad — real `FhirSchedulingConnector` |
| GAP-03 | Notifications written to console only; SMS reminders (F-03.4) not built | EA-08 | Engagement squad (Cycle 6) |
| GAP-04 | No EKS, ALB, TLS or HPA — two local processes over plain HTTP | EA-06 | Platform team — standard onboarding |
| GAP-05 | SQLite file without encryption instead of PostgreSQL RDS with KMS | EA-04, ABP-03 | Appointments squad — must close before any real PHI |
| GAP-06 | No Redis slot-availability cache | EA-04 | Appointments squad |
| GAP-07 | Domain events not published to EventBridge | EA-07 | Appointments squad (owner to be confirmed — OQ-03) |
| GAP-08 | No structured logs, metrics or tracing | EA-09, ABP-06 | Appointments squad |
| GAP-09 | No PHI access audit log (NFR-5) | EA-09 | Appointments squad |
| GAP-10 | Waitlist (F-03.5) and check-in → COMPLETED designed, not built | PRD scope | Appointments squad (Cycle 7 / Cycle 8) |

### Open questions

| # | Question | Blocking |
|---|---|---|
| OQ-01 | Cancellation window: PRD says ≥ 24 h, data architecture says ≥ 12 h. This HLD follows the PRD; which does the Cycle 4 code enforce? | Yes |
| OQ-02 | Do confirm / decline / cancel carry idempotency keys, or rely on status guards alone (ABP-05)? | No |
| OQ-03 | Which team owns the EventBridge publisher (GAP-07)? Assigned to the module owner by default. | No |
