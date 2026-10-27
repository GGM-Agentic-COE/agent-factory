
# High-Level Design (HLD)
**Document Version:** 1.1.0 (revised — see §0)
**Baseline Reference:** `kb-L1-harvestlink-enterprise-architecture.md` v1.0.0
**Feature Coverage:** F-02a, F-02b, F-02e (MVP-committed, Cycle 3) · F-02c, F-02d (designed, not built — see §8)
**Stack:** Java 17 + Spring Boot 3.x + PostgreSQL (target) / H2 (MVP demo) · React 18 + TypeScript (frontend)
**Correlation ID:** `4B2E7A10-3F5C-4D8E-9A11-6C0F2E7D9B44`

## 0. Revision note

Version 1.0.0 covered order creation only (F-02a) as a single component list. Version 1.1.0
restructures the document into a full system component diagram, a flow diagram per real flow
(including the Cycle 9 brownfield "repeat order" flow), an explicit order state machine, a
deployment view separating the target ECS/RDS topology from the MVP's two-local-process reality,
a security view, an observability section, and a Gap Register consolidating every mocked/deferred
piece — following the same pattern the Solution Architect asked for on the Catalogue Service HLD.

## 1. System Component Diagram

```
                    ┌───────────────┐
                    │  Buyer Browser│
                    │  React 18 SPA │
                    └──────┬────────┘
                           │  HTTPS
                           ▼
              ┌─────────────────────────────┐
              │  Ingress / Reverse Proxy      │
              │  target: AWS ALB                │
              │  MVP:    none, direct localhost  │
              └───────────────┬───────────────┘
                              │
        ┌─────────────────────┴──────────────────────┐
        ▼                                             ▼
┌───────────────────────┐                    ┌───────────────────────────┐
│  buyer-spa              │   REST, Bearer      │  orders-api                 │
│  React 18 · Vite         │◀- - - token - - ->│  Spring Boot                 │
│  target: Nginx, HPA 2-6  │                     │  target: HPA 2-8 pods       │
│  MVP: Vite dev server    │                     │  MVP: single process :8081  │
└───────────────────────┘                    └───────────┬───────────────┘
                                                            ▼
                                             ┌───────────────────────────┐
                                             │  AuthFilter                  │
                                             │  MVP:    mocked bearer token │
                                             │  target: Identity OIDC JWT   │
                                             └─────────────┬─────────────┘
                                     ┌────────────────────┴────────────────────┐
                                     ▼                                         ▼
                       ┌───────────────────────┐              ┌───────────────────────────┐
                       │  OrderController         │              │  OrderHistoryController      │
                       │  (create order)           │              │  (history + repeat order)     │
                       └────────────┬───────────┘              └────────────┬───────────────┘
                                     ▼                                        ▼
                       ┌───────────────────────┐              ┌───────────────────────────┐
                       │  OrderService            │◀─────────────│  RepeatOrderAction (Cy. 9)  │
                       │  placement + idempotency  │              └───────────────────────────┘
                       └──────┬───────┬────┬─────┘
                              │       │    │
              ┌───────────────┘       │    └──────────────────┐
              ▼                       ▼                       ▼
┌───────────────────────┐  ┌───────────────────┐  ┌───────────────────────────┐
│  CatalogueAvailability  │  │  PaymentGateway     │  │  NotificationService         │
│  Client (real, sync)    │  │  Connector          │  └───────────────────────────┘
└───────────────────────┘  │  MOCKED — no real   │
              │              │  Stripe call, §8    │
              ▼              └───────────────────┘
┌───────────────────────┐
│  PostgreSQL              │
│  target per EA4          │
│  MVP: H2 in-memory       │
└───────────┬───────────┘
            ▲
            │ target: cached 30s TTL (OrderHistoryController)
┌───────────────────────┐
│  Redis                   │
│  target: history cache   │
│  MVP: not used            │
└───────────────────────┘
```

**What changed vs. a from-scratch design:** Orders is a net-new bounded context — no legacy
service does order placement today (per `impact-assessment.md` §1 for Cycle 3). The genuinely
open integration points are downstream (a real payment gateway, mocked here) and cross-context
(Catalogue's availability check, which is real and synchronous, not mocked) — both called out
explicitly rather than glossed over.

## 2. Data Flow Diagrams

### 2.1 Place Order (new order) [F-02a · REQ-03]

Participants: Buyer | OrderController | OrderService | CatalogueAvailabilityClient |
PaymentGatewayConnector (mock) | Database | NotificationService

```
1. Buyer            ──POST /v1/orders {items, idempotencyKey}──▶     OrderController
2. OrderController   ──placeOrder(cmd)──▶                             OrderService
3. OrderService      ──checkIdempotency(key)──▶ (self)
   ├─ [duplicate key]
   │    4. OrderService ──200 (original order, no re-insert)──▶      OrderController
   └─ [new key]
        5. OrderService ──GET availability(listingId)──▶             CatalogueAvailabilityClient
           ├─ [insufficient stock]
           │    6. OrderService ──409 Conflict──▶                    OrderController
           └─ [stock OK]
                7.  OrderService ──authorize(amount) [MOCK]──▶       PaymentGatewayConnector
                8.  PaymentGatewayConnector ──mock authorization id──▶ OrderService
                9.  OrderService ──INSERT orders(status=PAYMENT_AUTHORIZED)──▶ Database
                10. OrderService ──UPDATE status=CONFIRMED──▶        Database
                11. OrderService ──notify(ORDER_CONFIRMED, buyer & producer)──▶ NotificationService
                12. OrderService ──201 Created──▶                    OrderController
```

### 2.2 Repeat Order [F-02e · brownfield, Cycle 9]

Participants: Buyer | OrderHistoryController | RepeatOrderAction | OrderService | Database

```
1. Buyer                  ──POST /v1/orders {repeatFromOrderId, overrides}──▶  OrderHistoryController
2. OrderHistoryController ──execute(originalOrderId, overrides)──▶             RepeatOrderAction
3. RepeatOrderAction       ──findById(originalOrderId)──▶                       Database
4. Database                ──original Order──▶                                  RepeatOrderAction
5. RepeatOrderAction       ──apply overrides (qty/address), new idempotencyKey──▶ (self)
6. RepeatOrderAction       ──placeOrder(cmd)──▶                                 OrderService
                              (from here, same path as §2.1 step 3 onward)
7. OrderService             ──201 Created──▶                                    OrderHistoryController
8. OrderHistoryController  ──201 Created──▶                                     Buyer
```

## 3. Order State Machine [F-02a, F-02e · BL]

```
                                       ┌────────────────────────┐
        place/repeat order,            │                        │
        payment mock-authorized        │  PAYMENT_AUTHORIZED     │
       ────────────────────────────────▶│                        │
                                       └──────────┬─────────────┘
                                                   │
                              auth succeeds ───────┼─────── auth fails
                                                   ▼                  ▼
                                       ┌──────────────┐    ┌──────────────┐
                                       │  CONFIRMED    │    │  CANCELLED    │
                                       └──────┬───────┘    └──────────────┘
                                              │
                       producer marks   ┌─────┴─────┐  refund issued
                       shipped          │           │  (F-02d, not built)
                       (F-02c,          ▼           ▼
                       not built)
                            ┌──────────────┐   ┌──────────────┐
                            │  FULFILLED    │   │  REFUNDED     │
                            │ (not built)   │   │ (not built)   │
                            └──────────────┘   └──────────────┘
```
CONFIRMED is terminal for MVP purposes — fulfillment and refund transitions are designed
(F-02c/F-02d) but have no code path yet.

### State summary

| State | Reachable from | Repeat allowed (source order) | Edit allowed |
|---|---|---|---|
| PAYMENT_AUTHORIZED | Place/repeat order | No (not yet confirmed) | No |
| CONFIRMED | Authorization success | Yes | No (orders are immutable once confirmed) |
| CANCELLED | Authorization failure | Yes (repeat re-attempts payment) | No |
| FULFILLED / REFUNDED | Not reachable in MVP | Yes | No |

## 4. Deployment View

### 4.1 Target (per `kb-L1-harvestlink-enterprise-architecture.md` EA6)

```
┌───────────────────────────────────────────────────────────────────────────┐
│  ECS Cluster                                                                │
│                                                                              │
│  ┌─────────────────────────── Namespace: orders ─────────────────────────┐ │
│  │                                                                        │ │
│  │   ┌─────────────────────┐        ┌─────────────────────┐             │ │
│  │   │ buyer-spa Service     │        │ orders-api Service    │             │ │
│  │   │  Task 1 ... Task n      │        │  Task 1 ... Task n      │             │ │
│  │   │  HPA max: 6              │        │  HPA max: 8              │             │ │
│  │   └──────────┬──────────┘        └──────────┬──────────┘             │ │
│  │              └──────────────┬─────────────────┘                        │ │
│  │                              ▼                                          │ │
│  │                    ┌───────────────────┐                                │ │
│  │                    │  ALB Ingress        │                                │ │
│  │                    │  TLS 1.3             │                                │ │
│  │                    │  Read: 300/min/user   │                                │ │
│  │                    │  Write: 60/min/user   │                                │ │
│  │                    └───────────────────┘                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌───────────────────── Namespace: data — shared ────────────────────────┐ │
│  │   ┌───────────────────┐   ┌──────────────┐   ┌──────────────┐         │ │
│  │   │ PostgreSQL (RDS)    │   │ Redis Primary  │──▶│ Redis Replica │         │ │
│  │   │ Multi-AZ, orders    │   └──────────────┘   └──────────────┘         │ │
│  │   │ schema               │                                              │ │
│  │   └───────────────────┘                                                │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────────────┘
```

| Service | Image base | Port | Resources (request/limit) | Probes |
|---|---|---|---|---|
| buyer-spa | `nginx:alpine` (multi-stage build) | 80 | 100m/500m CPU · 128Mi/256Mi | `/` (200) |
| orders-api | `eclipse-temurin:17-jre-alpine` | 8081 | 250m/1000m CPU · 256Mi/512Mi | `/actuator/health` (target — not yet added, see §8) |

### 4.2 MVP reality (this repo, right now)

```
┌───────────────────────┐      ┌────────────────────────┐
│  npm run dev (Vite)   │      │  mvn spring-boot:run    │
│  buyer-spa             │─────▶│  orders-api             │
│  http://localhost:5174│ REST │  http://localhost:8081 │
│  (single process, no  │      │  (single process, no   │
│   HPA, hot-reload)     │      │   HPA, embedded H2)     │
└───────────────────────┘      └────────────┬────────────┘
                                              │
                                    ┌─────────▼─────────┐
                                    │  H2 in-memory DB   │
                                    │  (state lost on    │
                                    │   process restart)  │
                                    └────────────────────┘
```
No ECS, no ALB, no Redis, no PostgreSQL, no CI runs this MVP — two local processes on a developer
machine, by design (demo scope for Cycle 3). §8 is the authoritative gap list.

## 5. Security View

Participants: Browser | AuthFilter | Protected Endpoint
target: Identity-issued RS256 JWT (EA5) · MVP: Bearer {buyerId}-token against a seeded
in-memory user table — NOT a real auth scheme, see §8

```
1. Browser  ──any /api/* request + Authorization: Bearer {token}──▶  AuthFilter
   ├─ [OPTIONS preflight]
   │    2. AuthFilter ──pass through (CORS)──▶                       Browser
   └─ [non-OPTIONS]
        3. AuthFilter ──parse token, look up buyer──▶ (self)
           ├─ [no matching buyer]
           │    4. AuthFilter ──401──▶                                Browser
           └─ [buyer found]
                5. AuthFilter ──attach currentUser──▶                Protected Endpoint
                6. Protected Endpoint ──RBAC: BUYER=own orders only; PRODUCER=orders
                   against own listings only──▶ (self)
                   ├─ [authorized]      7. Protected Endpoint ──200──▶ Browser
                   └─ [not authorized]  7. Protected Endpoint ──403──▶ Browser
```

### Encryption boundaries

| Boundary | Target (EA5) | MVP reality |
|---|---|---|
| Browser → API | TLS 1.3 | Plain HTTP, localhost only |
| API → Database | TLS 1.2+ | N/A — H2 embedded |
| Auth token | RS256, Identity-issued | Opaque mocked token, no signature |

### Authorization matrix (as actually enforced in code)

| Endpoint | Buyer | Producer |
|---|---|---|
| `POST /v1/orders` | Own `buyerId` only (403 otherwise) | Forbidden (403) |
| `POST /v1/orders` (repeat) | Own prior order only (403 otherwise — found missing, IDOR, fixed) | Forbidden (403) |
| `GET /v1/orders/history` | Own orders only, forced server-side | Orders against own listings only |

## 6. Observability

| Signal | Target (EA9) | MVP reality |
|---|---|---|
| Structured logs | JSON, correlationId per line | Default Spring Boot console logging |
| Metrics | Micrometer → Prometheus | `order.repeated` custom counter only; nothing else instrumented |
| Health probes | `/actuator/health` | Not added |
| Tracing | OpenTelemetry | Not instrumented |

## 7. NFR Compliance Summary

| NFR (from PRD/EA7) | Target | MVP status |
|---|---|---|
| Order placement ≤ 300ms P95 | Async availability check, indexed idempotency lookup | **Met trivially** — sub-second at demo scale, not stress-tested |
| Idempotent submission | DB unique constraint on `idempotency_key` | **Met** — enforced at the DB level, verified by the double-click regression test |
| 99.9% availability | Multi-AZ RDS, ECS auto-scaling | **Not applicable** — single-process local demo has no HA story |
| PCI-DSS scope (card payment) | Tokenized payment via PCI-compliant gateway | **Not applicable yet** — `PaymentGatewayConnector` is fully mocked, no real card data ever leaves the browser in this MVP |

## 8. Gap Register — Target Architecture vs. This Build

| # | Gap | Target (EA reference) | Owner of the resolution |
|---|---|---|---|
| 1 | Payment authorization is fully mocked | EA8 — real gateway integration is an open architectural question | Billing squad to confirm Stripe vs. Adyen before Cycle 8 |
| 2 | Auth is a mocked bearer token, not Identity OIDC | EA5 | Identity team — swap `AuthFilter` for a real OIDC validator |
| 3 | H2 in-memory, not PostgreSQL | EA1, EA4 | Orders squad — schema already documented in LLD §2 |
| 4 | No ECS deployment, no HPA, no ALB | EA6 | Standard platform onboarding once module leaves demo status |
| 5 | No Redis caching layer | EA1 | Add once order-history read volume justifies it |
| 6 | No application-level observability (metrics, tracing, health probes) | EA9 | Add Spring Boot Actuator + Micrometer before staging |
