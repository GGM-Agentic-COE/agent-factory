
# Low-Level Design (LLD)
**Document Version:** 1.1.0 (revised — see §0)
**Baseline Reference:** `kb-L1-harvestlink-enterprise-architecture.md` v1.0.0
**Feature Coverage:** F-02a, F-02b, F-02e (MVP-committed)
**Stack:** Java 17 + Spring Boot 3.3 + Spring Data JPA + H2 (MVP) / PostgreSQL (target)
**Correlation ID:** `4B2E7A10-3F5C-4D8E-9A11-6C0F2E7D9B44`

## 0. Revision note

Version 1.0.0 covered `Order`/`OrderLine` and the `POST /v1/orders` handler only. Version 1.1.0
adds `RepeatOrderAction` and its handler (§4.3), the `repeated_from_order_id` schema addition
(§2.1), the full order state-transition table (§6), and expands test coverage to the double-click
regression found during Cycle 9's live testing — matching the depth requested for the Catalogue
Service LLD.

## 1. Domain Model

```
┌───────────────────────────┐            ┌───────────────────────────┐
│           Order              │            │         OrderLine           │
├───────────────────────────┤            ├───────────────────────────┤
│ + id: String                 │  1     * │ + id: String                 │
│ + buyerId: String            │─────────▶│ + orderId: String            │
│ + status: OrderStatus        │ contains  │ + listingId: String          │
│ + idempotencyKey: String     │            │ + quantity: int              │
│ + repeatedFromOrderId: String│            │ + unitPrice: double          │
│ + createdAt: Instant         │            └───────────────────────────┘
└───────────────────────────┘

┌───────────────────────────┐            ┌───────────────────────────┐
│    <<enumeration>>          │            │    <<enumeration>>          │
│      OrderStatus             │            │      AuditAction             │
├───────────────────────────┤            ├───────────────────────────┤
│  PAYMENT_AUTHORIZED          │            │  CREATED                     │
│  CONFIRMED                    │            │  PAYMENT_AUTHORIZED           │
│  CANCELLED                    │            │  CONFIRMED                    │
│  FULFILLED                    │            │  PAYMENT_FAILED               │
│  REFUNDED                      │            │  REPEATED                     │
└───────────────────────────┘            └───────────────────────────┘

              Order.status : OrderStatus         (order write path emits AuditAction entries)
```

**MVP simplification vs. this diagram's implication:** `repeatedFromOrderId` is a plain nullable
column, not a formal self-referencing relationship in the ORM mapping — sufficient for
traceability queries, without introducing recursive-fetch complexity for a field that's read far
more often than it's joined on.

## 2. Database Schema

> Full DDL: `docs/sdlc/phase-4-design/db-schema.sql` (PostgreSQL — target, EA4). The MVP runs on
> H2 with Hibernate `ddl-auto: update`, kept conceptually aligned but not executed verbatim.

### 2.1 `orders`

| Column | Type (target Postgres) | Constraints | Notes |
|---|---|---|---|
| id | VARCHAR(64) | PK | UUID string |
| buyer_id | VARCHAR(64) | NOT NULL FK → users.id | |
| status | VARCHAR(32) | NOT NULL CHECK IN (PAYMENT_AUTHORIZED, CONFIRMED, CANCELLED, FULFILLED, REFUNDED) | |
| idempotency_key | VARCHAR(128) | UNIQUE, NOT NULL | Enforces at-most-one order per key |
| repeated_from_order_id | VARCHAR(64) | FK → orders.id, NULLABLE | **Added Cycle 9** — additive column, no migration risk |
| created_at | TIMESTAMPTZ | NOT NULL | |

**Indexes:** unique index on `idempotency_key` (supports the ≤300ms NFR by avoiding a full scan
on the uniqueness check).

### 2.2 `order_lines`

| Column | Type | Constraints | Notes |
|---|---|---|---|
| id | VARCHAR(64) | PK | |
| order_id | VARCHAR(64) | NOT NULL FK → orders.id | |
| listing_id | VARCHAR(64) | NOT NULL | Validated against Catalogue at write time, not FK-enforced (cross-context, no shared DB — ADR-003) |
| quantity | INTEGER | NOT NULL CHECK > 0 | |
| unit_price | DOUBLE | NOT NULL CHECK >= 0 | Snapshotted at order time; not recalculated if the listing's price later changes |

## 3. Migration Plan

### Target (PostgreSQL, EA4/EA6 — not executed by this MVP)

```sql
-- V1__create_orders_schema.sql
CREATE TABLE orders (...);
CREATE TABLE order_lines (...);
-- all indexes created in the same migration
```
Flyway-managed, additive-only per EA6's zero-downtime strategy.

### MVP reality

No migration tool runs. Hibernate `ddl-auto: update` derives the schema from JPA entity
annotations at startup against a fresh H2 in-memory database — recreated from nothing on every
process restart. Documented as a gap in `hld.md` §8, not a real migration strategy.

## 4. Handler Specifications

> Pattern: `@RestController` → `@Service` → Spring Data JPA repository → H2 (target: PostgreSQL).
> Every endpoint below exists in `api/src/main/java` and is covered by at least one test in
> `OrderWorkflowTests.java`.

### 4.1 `createOrder` (`POST /api/v1/orders`) — [F-02a · REQ-03]

```
INPUT (CreateOrderRequest):
  items: [{ listingId, quantity }]  (required, at least one)
  idempotencyKey: string (required)

AUTH: caller must be role=BUYER

BUSINESS LOGIC:
  1. checkIdempotency(idempotencyKey) — if an order already exists for this key,
     return it as-is (200), do not re-insert
  2. For each item: call CatalogueAvailabilityClient.check(listingId, quantity)
     — 409 if any item is insufficient stock
  3. PaymentGatewayConnector.authorize(total) — MOCKED, returns a fabricated
     authorization id, no real card data ever leaves the browser
  4. Persist Order(status=PAYMENT_AUTHORIZED) + OrderLines
  5. status = CONFIRMED (mock authorization always succeeds unless a test forces a decline)
  6. audit CONFIRMED; notify(ORDER_CONFIRMED, buyer AND producer)

OUTPUT: 201 Order | 409 (insufficient stock) | 422 (validation) | 401
```

### 4.2 `getHistory` (`GET /api/v1/orders/history`) — [F-02b]

```
AUTH: any authenticated BUYER; scoped to caller's own orders server-side
      (found missing at code review — a client could pass another buyerId
       query param and see their orders; now hard-blocked)

OUTPUT: 200 Order[], newest first
```

### 4.3 `repeatOrder` (`POST /api/v1/orders` with `repeatFromOrderId`) — [F-02e · brownfield, Cycle 9]

```
INPUT (RepeatOrderRequest):
  repeatFromOrderId: string (required)
  overrides: { quantity?, deliveryAddress? }  (optional, per line item)

AUTH: caller must own the original order (403 otherwise — found missing, IDOR, fixed)

BUSINESS LOGIC:
  1. Fetch original order by repeatFromOrderId (404 if missing)
  2. RepeatOrderAction.execute(originalOrder, overrides) — builds a new
     CreateOrderCommand from the original's line items, applying any overrides,
     and generates a brand-new idempotencyKey (never reuses the original's key —
     otherwise a repeat would collide with the original and return it unchanged)
  3. Delegates to the same path as §4.1 from step 2 onward

OUTPUT: 201 Order | 404 | 403 | 409 (insufficient stock) | 422
```

### 4.4 `cancelOrder` (`POST /api/v1/orders/{id}/cancel`) — target, not built (F-02c)

```
Designed but not implemented in this MVP — see hld.md §8 / §3 state machine.
```

## 5. Validation Rules Reference

| Field | Rule | Error message | Applies when |
|---|---|---|---|
| items | non-empty array | `items: at least one item is required` | createOrder |
| items[].quantity | > 0 | `items[].quantity: must be greater than 0` | Always |
| idempotencyKey | non-blank | `idempotencyKey: is required` | Always |
| repeatFromOrderId | must reference an existing order owned by the caller | `repeatFromOrderId: order not found` (404) or `: not owned by caller` (403) | repeatOrder |
| overrides.quantity | > 0 if provided | `overrides.quantity: must be greater than 0` | repeatOrder, when provided |

## 6. State Transition Table

| From | To | Trigger | Guard | Side effects |
|---|---|---|---|---|
| — | PAYMENT_AUTHORIZED | Create or repeat order, stock available | — | audit CREATED |
| PAYMENT_AUTHORIZED | CONFIRMED | Mock authorization succeeds | — | audit CONFIRMED; notify buyer + producer |
| PAYMENT_AUTHORIZED | CANCELLED | Mock authorization declines | — | audit PAYMENT_FAILED; notify buyer |
| CONFIRMED | FULFILLED | Producer marks shipped (target, F-02c) | role=PRODUCER, status==CONFIRMED | Not implemented in this MVP |
| CONFIRMED | REFUNDED | Refund issued (target, F-02d) | role=LEGAL/SUPPORT | Not implemented in this MVP |
| any | — (rejected) | Repeat attempted on a non-owned order | ownership check fails | 403, no state change |

## 7. API Error Response Reference

| HTTP Status | When | Body shape |
|---|---|---|
| 200 | Duplicate idempotency key (original order returned) | Order body |
| 201 | New order created | Order body |
| 401 | Missing/invalid Bearer token | `{"message": "..."}` |
| 403 | Wrong role, or ownership mismatch | `{"message": "..."}` |
| 404 | Order not found (repeat) | `{"message": "..."}` |
| 409 | Insufficient stock | `{"message": "..."}` |
| 422 | Field validation failure | `{"orderId": null, "errors": [{"field": "...", "message": "..."}]}` |

Handled centrally in `GlobalExceptionHandler` (`@RestControllerAdvice`) — every service throws a
typed exception (`ApiExceptions.NotFoundException`, `ConflictException`, `ValidationFailedException`)
rather than constructing error responses inline.

## 8. Backend Module Structure (as built)

```
api/src/main/java/com/harvestlink/orders/
├── OrdersApplication.java
├── domain/
│   ├── Order.java, OrderLine.java
│   └── OrderStatus.java, AuditAction.java
├── repository/
│   └── OrderRepository.java, OrderLineRepository.java
├── security/
│   └── AuthFilter.java             # Mocked-SSO bearer filter
├── service/
│   ├── OrderService.java           # F-02a — placement + idempotency guard
│   ├── RepeatOrderAction.java      # F-02e — Cycle 9
│   ├── CatalogueAvailabilityClient.java
│   ├── PaymentGatewayConnector.java  # MOCKED
│   └── NotificationService.java
├── web/
│   ├── OrderController.java, OrderHistoryController.java
│   ├── GlobalExceptionHandler.java
│   └── dto/                        # CreateOrderRequest, RepeatOrderRequest, ApiExceptions
└── config/
    └── DataSeeder.java             # CommandLineRunner — demo buyers/listings

api/src/test/java/com/harvestlink/orders/
└── OrderWorkflowTests.java         # @SpringBootTest + MockMvc integration tests
```

## 9. Frontend Module Structure (as built)

```
ui/src/
├── main.tsx, App.tsx                # Router: /orders/history, /checkout
├── AuthContext.tsx                  # Mocked-SSO demo-buyer picker
├── api.ts                           # Typed fetch wrapper
├── components/
│   ├── OrderHistoryRow.tsx          # "Repeat" button — new, Cycle 9
│   └── OrderStatusBadge.tsx
├── pages/
│   ├── Checkout.tsx                 # F-02a
│   └── OrderHistory.tsx             # F-02b, F-02e
└── test/
    ├── OrderHistoryRow.test.tsx     # Repeat button debounce/disable-on-click
    └── OrderHistory.test.tsx
```

## 10. Test Coverage (as built)

| Suite | Tool | Count | Key scenarios |
|---|---|---|---|
| `OrderWorkflowTests.java` | JUnit 5 + Spring Boot Test + MockMvc | 11 | Unauthenticated 401; golden-path create→CONFIRMED; insufficient-stock→409; duplicate idempotency key→200 with original order, no re-insert; repeat order builds a new idempotency key; repeat on another buyer's order→403 (IDOR fix); repeat on a missing order→404; overrides applied correctly (quantity, address); history scoped to caller only (fix regression) |
| `OrderHistoryRow.test.tsx` | Vitest + RTL | 3 | Repeat button disables on first click; re-enables on error; rapid double-click still fires exactly one request |
| `OrderHistory.test.tsx` | Vitest + RTL | 2 | Renders history newest-first; repeat button visible only on CONFIRMED/CANCELLED orders |

Target per EA14: ≥80% coverage on service layer. Not measured with a coverage tool in this MVP —
the 16 tests above are scenario-driven (one per real behavior, including the double-click
regression found during Cycle 9 live testing), not coverage-percentage-driven; a follow-up should
add JaCoCo (backend) and `vitest --coverage` (frontend) before this leaves demo status.
