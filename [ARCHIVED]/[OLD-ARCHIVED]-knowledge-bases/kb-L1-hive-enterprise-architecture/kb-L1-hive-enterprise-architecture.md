# Enterprise Architecture Standards — The Hive - Predictive Expiry & Waste Prevention Engine (Schreiber Foods)
### kb-L1-hive-enterprise-architecture v1.0.0
### This KB defines the enterprise-level architecture standards for The Hive - Predictive Expiry & Waste Prevention Engine. All design and construction agents MUST ground their decisions in these standards.

---

## EA1: Technology Stack

| Layer | Technology | Version | Purpose | Status |
|-------|-----------|---------|---------|--------|
| Frontend | React | 18.x | UI framework | Mandatory |
| Frontend | TypeScript | 5.x | Type-safe JavaScript | Mandatory |
| Frontend | Vite | 5.x | Build tool | Mandatory |
| Frontend | React Router | 6.x | Client-side routing | Mandatory |
| Frontend | TanStack Query | 5.x | Server state management | Mandatory |
| Frontend | Zustand | 4.x | Client state management | Mandatory |
| Frontend | Axios | 1.x | HTTP client | Mandatory |
| Frontend | React Hook Form | 7.x | Form management | Mandatory |
| Frontend | Zod | 3.x | Schema validation | Mandatory |
| Frontend | Recharts | 2.x | Dashboard charts/graphs | Mandatory |
| Frontend | Tailwind CSS | 3.x | Utility-first CSS | Mandatory |
| Frontend | Radix UI | Latest | Accessible headless components | Mandatory |
| Frontend | date-fns | 3.x | Date manipulation | Mandatory |
| Backend | Python | 3.12+ | Primary language | Mandatory |
| Backend | FastAPI | 0.110+ | API framework | Mandatory |
| Backend | Pydantic | 2.x | Data validation & serialization | Mandatory |
| Backend | SQLAlchemy | 2.x | ORM | Mandatory |
| Backend | cx_Oracle / oracledb | Latest | Oracle DB driver | Mandatory |
| Backend | Alembic | 1.x | Database migrations | Mandatory |
| Backend | Celery | 5.x | Async task queue | Mandatory |
| Backend | Redis | 7.x | Caching & Celery broker | Mandatory |
| Backend | structlog | 24.x | Structured logging | Mandatory |
| Backend | httpx | 0.27+ | Async HTTP client | Mandatory |
| Backend | Uvicorn | 0.29+ | ASGI server | Mandatory |
| Database | Oracle Database | 19c+ | Primary database | Mandatory |
| Database | PL/SQL | — | Stored procedures, triggers, functions | Mandatory |
| Database | Redis | 7.x | Caching layer | Mandatory |
| Infrastructure | Docker | Latest | Containerization | Mandatory |
| Infrastructure | Kubernetes | Latest | Container orchestration | Mandatory |
| Infrastructure | NGINX | Latest | Reverse proxy / API gateway | Mandatory |
| Infrastructure | GitHub Actions | Latest | CI/CD pipelines | Mandatory |
| Infrastructure | Vault (HashiCorp) | Latest | Secrets management | Mandatory |
| Infrastructure | Prometheus + Grafana | Latest | Monitoring & dashboards | Mandatory |
| Testing | pytest | 8.x | Python unit/integration testing | Mandatory |
| Testing | pytest-asyncio | Latest | Async test support | Mandatory |
| Testing | httpx (TestClient) | Latest | FastAPI integration testing | Mandatory |
| Testing | factory_boy | 3.x | Test data factories | Mandatory |
| Testing | Jest | 29.x | React unit testing | Mandatory |
| Testing | React Testing Library | 14.x | Component testing | Mandatory |
| Testing | Playwright | Latest | E2E browser testing | Mandatory |
| Testing | Vitest | 1.x | Vite-native unit testing | Approved |
| Security | Bandit | Latest | Python SAST | Mandatory |
| Security | ESLint Security | Latest | JS/TS SAST | Mandatory |
| Security | Trivy | Latest | Container vulnerability scanning | Mandatory |
| Security | Snyk | Latest | Dependency vulnerability scanning | Mandatory |

**MANDATORY RULE:** Agents MUST NOT introduce technologies not on this list. If a requirement needs unlisted tech, output `UNLISTED_TECHNOLOGY_REQUIRED:[name]` for ARB review.

---

## EA2: Architecture Patterns

### Backend: Layered Architecture with FastAPI

Three layers with strict dependency direction (inward only):

1. **Domain** — Models (SQLAlchemy ORM), enums, schemas (Pydantic), repository interfaces (Protocol classes). Zero external framework dependencies beyond SQLAlchemy.
2. **Service** — Business logic, use cases, orchestration. Depends only on Domain. Contains the predictive scoring engine, alert generation, and scheduling suggestion logic.
3. **API** — FastAPI routers, dependency injection, middleware, exception handlers. Entry point; depends on Service.

```
backend/
  app/
    api/                    # FastAPI routers, dependencies, middleware
      routers/              # One router per domain (lots, alerts, scoring, work_orders, etc.)
      dependencies.py       # Dependency injection (get_db, get_current_user)
      middleware.py          # Correlation ID, logging, error handling
    domain/
      models/               # SQLAlchemy ORM models
      schemas/              # Pydantic request/response schemas
      enums.py              # Enums (LotStatus, AlertType, RiskLevel, etc.)
      repositories/         # Repository interfaces (Protocol classes)
    service/
      scoring_engine.py     # Predictive expiry scoring
      alert_service.py      # Role-based alert generation
      fefo_service.py       # Dynamic FEFO reprioritization
      scheduling_service.py # Production scheduling suggestions
      waste_tracker.py      # Waste prevention tracking
    infrastructure/
      database.py           # Oracle DB session management
      repositories/         # Repository implementations
      cache.py              # Redis cache layer
      tasks.py              # Celery async tasks
    core/
      config.py             # Settings (Pydantic BaseSettings, env vars)
      security.py           # JWT auth, password hashing
      exceptions.py         # Custom exception classes
  migrations/               # Alembic migrations
  tests/
    unit/                   # pytest unit tests (mocked dependencies)
    integration/            # pytest integration tests (TestClient + test DB)
    factories/              # factory_boy test data factories
  main.py                   # FastAPI app creation, startup/shutdown
  pyproject.toml            # Dependencies (Poetry or pip)
```

### Frontend: Feature-Based React Architecture

```
frontend/
  src/
    app/                    # App shell, providers, router
    features/               # Feature modules (one per domain)
      dashboard/            # Operations leader dashboard
      lots/                 # Lot management & inventory
      alerts/               # Alert center & acknowledgment
      scoring/              # Risk scoring views
      scheduling/           # Work order & production suggestions
      settings/             # Admin configuration
      auth/                 # Login, session management
    shared/
      components/           # Reusable UI components (design system)
      hooks/                # Custom React hooks
      api/                  # Axios client, API functions
      utils/                # Formatters, validators, helpers
      types/                # Shared TypeScript types
    assets/                 # Static assets, icons
  public/
  tests/                    # Jest/Vitest + RTL tests
```

### Communication
- **Synchronous (REST over HTTPS):** Frontend → Backend via FastAPI endpoints.
- **Asynchronous (Celery + Redis):** Background scoring, alert generation, report computation.
- **WebSocket (FastAPI WebSocket):** Real-time dashboard updates and alert push.

### State Management
- **Server state:** TanStack Query for all API data (caching, refetching, optimistic updates).
- **Client state:** Zustand for UI state (sidebar, filters, preferences).
- **Form state:** React Hook Form + Zod for all forms.

### Error Handling

**Backend (FastAPI):**
- Global exception handler converts all exceptions to RFC 7807 ProblemDetails JSON.
- Custom exceptions: `BusinessRuleError` → 422, `NotFoundError` → 404, `ConflictError` → 409.
- Pydantic validation errors → 400 with field-level errors.
- Database errors → 503 with correlation ID.
- Unhandled exceptions → 500 with correlation ID (no stack trace in response).

```python
# Exception handler pattern
@app.exception_handler(BusinessRuleError)
async def business_rule_handler(request: Request, exc: BusinessRuleError):
    return JSONResponse(status_code=422, content={
        "type": "business-rule-violation",
        "title": exc.title,
        "status": 422,
        "detail": exc.detail,
        "instance": str(request.url),
        "correlation_id": request.state.correlation_id,
    })
```

**Frontend (React):**
- Axios interceptors for global error handling (401 → redirect to login, 5xx → toast).
- TanStack Query `onError` callbacks for query-specific handling.
- Error boundaries at route level for unhandled React errors.
- User-friendly error messages; technical details logged to console/monitoring.

---

## EA3: API Standards

### Base URL Pattern
- Development: `http://localhost:8000/api/v1/{resource}`
- Production: `https://api.hive.schreiber.com/api/v1/{resource}`

### REST Conventions
- Resource names: plural nouns (`/lots`, `/alerts`, `/work-orders`)
- Actions on resources: `POST /lots/{id}/score`, `POST /alerts/{id}/acknowledge`
- JSON only, `camelCase` properties in responses, `snake_case` in Python internals
- ISO 8601 dates, enums as strings
- Path parameters: `snake_case` (`lot_id`, `facility_id`)

### Response Envelope
```json
{
  "data": { ... },
  "meta": { "page": 1, "page_size": 20, "total_count": 150, "total_pages": 8 }
}
```

### Error Response (RFC 7807)
```json
{
  "type": "https://api.hive.schreiber.com/errors/business-rule-violation",
  "title": "Lot Already Expired",
  "status": 422,
  "detail": "Lot BN-2026-0042 expired on 2026-04-28 and cannot be reprioritized.",
  "instance": "/api/v1/lots/BN-2026-0042/reprioritize",
  "correlation_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

### Standard Headers
- `Authorization: Bearer {JWT}` — on all authenticated endpoints
- `X-Correlation-Id` — auto-generated UUID, propagated through all services
- `X-Facility-Id` — current facility context (multi-tenant isolation)
- `Content-Type: application/json`
- `Idempotency-Key` — required on all POST/PUT/PATCH (UUID)

### Pagination
- `page` (1-based, default 1) + `page_size` (max 100, default 20)
- Response includes `meta.total_count` and `meta.total_pages`

### Rate Limiting
- Read: 200 req/min per user
- Write: 50 req/min per user
- Scoring engine: 10 req/min (heavy computation)

### Versioning
- URL path versioning: `/api/v1/`, `/api/v2/`
- Breaking changes require new version; additive changes in current version

### Bulk Import / Export
- **Import:** `POST /api/v1/lots/import` accepts `multipart/form-data` with CSV file (max 10MB)
  - Async processing via Celery task; returns `202 Accepted` with `task_id`
  - Poll `GET /api/v1/tasks/{task_id}` for status (pending, processing, completed, failed)
  - Validation errors returned as downloadable CSV with error column
- **Export:** `GET /api/v1/lots/export?format=csv&facility_id=...` returns CSV download
  - Large exports (>10,000 rows) processed async with download link via email/notification
  - PDF reports for waste metrics via `GET /api/v1/reports/waste?format=pdf&period=monthly`

---

## EA4: Data Architecture

### Oracle Database Standards

**Schema per Domain:**
| Schema | Tables | Purpose |
|--------|--------|---------|
| `HIVE_CORE` | FACILITIES, USERS, ROLES, USER_ROLES | Core identity & multi-tenancy |
| `HIVE_INVENTORY` | PRODUCTS, LOTS, LOT_MOVEMENTS, CONSUMPTION_RECORDS | Inventory management |
| `HIVE_SCORING` | RISK_SCORES, SCORING_HISTORY, VELOCITY_CACHE | Predictive engine data |
| `HIVE_ALERTS` | ALERTS, ALERT_ACKNOWLEDGMENTS, ALERT_THRESHOLDS | Alert management |
| `HIVE_PRODUCTION` | WORK_ORDERS, WO_INGREDIENTS, SCHEDULING_SUGGESTIONS | Production planning |
| `HIVE_REPORTING` | WASTE_EVENTS, WASTE_METRICS, AUDIT_LOGS | Reporting & compliance |

**Mandatory Columns (all tables):**
```sql
ID              RAW(16) DEFAULT SYS_GUID() PRIMARY KEY,
CREATED_AT      TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
CREATED_BY      VARCHAR2(100) NOT NULL,
UPDATED_AT      TIMESTAMP DEFAULT SYSTIMESTAMP NOT NULL,
UPDATED_BY      VARCHAR2(100) NOT NULL,
IS_DELETED      NUMBER(1) DEFAULT 0 NOT NULL,
VERSION_NUM     NUMBER DEFAULT 1 NOT NULL,
FACILITY_ID     RAW(16) NOT NULL  -- multi-tenant isolation
```

**PL/SQL Standards:**
- Stored procedures for complex scoring calculations (performance-critical)
- Packages group related procedures: `PKG_SCORING`, `PKG_ALERTS`, `PKG_FEFO`, `PKG_REPORTING`
- All procedures include exception handling with `RAISE_APPLICATION_ERROR`
- Use bind variables (never string concatenation) to prevent SQL injection
- Bulk operations via `FORALL` and `BULK COLLECT` for lot scoring (10,000+ lots)
- Partitioning on `FACILITY_ID` and `CREATED_AT` for large tables (LOTS, RISK_SCORES)

```sql
-- Example: Scoring procedure pattern
CREATE OR REPLACE PACKAGE BODY PKG_SCORING AS
  PROCEDURE SCORE_FACILITY_LOTS(
    p_facility_id IN RAW,
    p_scored_count OUT NUMBER
  ) IS
  BEGIN
    -- Bulk score all active lots in facility
    FORALL i IN 1..l_lots.COUNT
      INSERT INTO HIVE_SCORING.RISK_SCORES (LOT_ID, RISK_SCORE, DAYS_TO_EXPIRY, VELOCITY, SCORED_AT)
      VALUES (l_lots(i).id, l_scores(i), l_days(i), l_velocities(i), SYSTIMESTAMP);
    p_scored_count := SQL%ROWCOUNT;
    COMMIT;
  EXCEPTION
    WHEN OTHERS THEN
      ROLLBACK;
      RAISE_APPLICATION_ERROR(-20001, 'Scoring failed: ' || SQLERRM);
  END;
END PKG_SCORING;
```

**Data Encryption:**
- PII columns: encrypted via Oracle TDE (Transparent Data Encryption)
- Application-level encryption for sensitive fields not covered by TDE
- All connections via TLS 1.2+

**Soft Delete:**
- All deletes set `IS_DELETED = 1` — never hard delete
- Views filter `WHERE IS_DELETED = 0` for application queries
- Archival job moves soft-deleted records older than retention period

**Indexing Strategy:**
- Primary key: `ID` (all tables)
- Foreign keys: indexed by default
- Composite indexes on frequently filtered columns (e.g., `FACILITY_ID + STATUS + EXPIRY_DATE`)
- Function-based indexes for scoring queries (e.g., `TRUNC(EXPIRY_DATE) - TRUNC(SYSDATE)`)

---

## EA5: Security Architecture

### Authentication
- JWT (RS256) tokens issued by the backend
- Access token: 30-minute expiry
- Refresh token: 7-day expiry, rotated on use, stored in HttpOnly cookie
- Password hashing: bcrypt with cost factor 12

### Authorization
- Role-Based Access Control (RBAC) with 5 roles:
  | Role | Permissions |
  |------|------------|
  | System Admin | Full access, user management, configuration |
  | Operations Leader | Dashboards, reports, facility management |
  | Warehouse Supervisor | Pick lists, lot movements, alerts (warehouse) |
  | Production Planner | Work orders, scheduling suggestions, alerts (production) |
  | QA Manager | QA holds, disposition, alerts (QA), compliance reports |

- Facility-level isolation: users see only data for their assigned facilities
- `X-Facility-Id` header validated against user's facility assignments

### API Security
- All endpoints require Bearer JWT (except `/api/v1/auth/login`, `/health`)
- CORS: whitelist frontend origin only
- Rate limiting per user per endpoint
- Input validation via Pydantic schemas on every endpoint
- SQL injection prevention: SQLAlchemy parameterized queries + PL/SQL bind variables

### Data Security
- Oracle TDE for encryption at rest
- TLS 1.2+ for all connections (API, database, Redis)
- No PII in logs (structlog processors strip sensitive fields)
- Audit log for all write operations (who, what, when, affected entity)

### Frontend Security
- JWT stored in HttpOnly secure cookie (not localStorage)
- CSRF protection via SameSite=Strict cookie + CSRF token
- XSS prevention: React's built-in escaping + CSP headers
- No secrets in frontend code or environment variables exposed to browser

---

## EA6: Infrastructure & Deployment

### Container Strategy
- Each component is a separate Docker container:
  | Container | Base Image | Port |
  |-----------|-----------|------|
  | hive-api | python:3.12-slim | 8000 |
  | hive-frontend | node:20-alpine (build) → nginx:alpine (serve) | 3000 |
  | hive-worker | python:3.12-slim (Celery) | — |
  | hive-scheduler | python:3.12-slim (Celery Beat) | — |
  | redis | redis:7-alpine | 6379 |

- Oracle DB: managed service (Oracle Cloud or on-premise) — not containerized
- All images: non-root user, <200MB, health check defined
- Multi-stage builds for frontend (build → serve)

### CI/CD Pipeline
```
lint → type-check → unit-test → build → integration-test → security-scan → docker-build → image-scan → deploy-staging → smoke-test → deploy-prod
```

### Environment Strategy
| Environment | Purpose | Database |
|-------------|---------|----------|
| Local | Developer workstation | SQLite (test) or Oracle XE |
| CI | Automated testing | Oracle XE in Docker |
| Staging | Pre-production validation | Oracle (staging schema) |
| Production | Live system | Oracle (production schema) |

---

## EA7: Non-Functional Requirements

| Category | Metric | Target |
|----------|--------|--------|
| Latency (API) | p95 response time | < 500ms for reads, < 2s for scoring |
| Latency (Alerts) | Alert generation after trigger | < 5 minutes |
| Latency (Dashboard) | Dashboard refresh | < 1 minute |
| Throughput | Concurrent lot scoring | 10,000 lots per facility |
| Availability | System uptime | 99.9% |
| Scalability | Facilities | 100 concurrent |
| Scalability | Total lots | 1,000,000 (100 × 10,000) |
| Recovery | Failover time | < 5 minutes |
| Data retention | Scoring history | 2 years |
| Data retention | Audit logs | 7 years |

---

## EA8: Integration Patterns

### Internal (Backend ↔ Database)
- SQLAlchemy ORM for standard CRUD
- PL/SQL stored procedures for bulk scoring operations (performance)
- Redis cache for velocity calculations and scoring results (TTL: 5 minutes)

### External (Future — Nice-to-Have)
- ERP integration via REST API with circuit breaker (httpx + tenacity)
- Transportation system integration via webhook callbacks
- Circuit breaker: 3 failures → open 60s → half-open probe

### Async Processing (Celery)
- `score_facility_lots` — periodic task (every 5 minutes per facility)
- `generate_alerts` — triggered after scoring completes
- `compute_waste_metrics` — periodic task (every hour)
- `cleanup_expired_scores` — daily maintenance

### WebSocket (Real-Time Updates)
- `/ws/alerts/{facility_id}` — push new alerts to connected users
- `/ws/dashboard/{facility_id}` — push metric updates
- Authentication via JWT query parameter on WebSocket connect:
  ```python
  @app.websocket("/ws/alerts/{facility_id}")
  async def alert_ws(websocket: WebSocket, facility_id: str, token: str = Query(...)):
      user = verify_jwt(token)  # Validate JWT before accepting connection
      if not user or facility_id not in user.facility_ids:
          await websocket.close(code=4001)
          return
      await websocket.accept()
  ```

### Celery Task Error Handling
- All tasks use `autoretry_for=(Exception,)` with `retry_backoff=True`, `max_retries=3`
- Dead letter queue for permanently failed tasks
- Flower dashboard for task monitoring (port 5555, auth-protected)
- Task results stored in Redis with 24h TTL
- Structured logging in every task (correlation_id, facility_id, task_name)
```python
@celery_app.task(bind=True, autoretry_for=(Exception,), retry_backoff=True, max_retries=3)
def score_facility_lots(self, facility_id: str):
    logger.info("scoring_started", facility_id=facility_id, task_id=self.request.id)
    try:
        # scoring logic
    except Exception as exc:
        logger.error("scoring_failed", facility_id=facility_id, error=str(exc))
        raise  # triggers autoretry
```

### Oracle Connection Pooling
- Use `oracledb` (thin mode, no Oracle Client needed) with SQLAlchemy
- Pool size: min 5, max 20 per worker process
- Connection validation: `pool_pre_ping=True`
- Statement cache: 50 statements per connection
```python
engine = create_engine(
    "oracle+oracledb://user:pass@host:1521/service",
    pool_size=10, max_overflow=10, pool_pre_ping=True,
    pool_recycle=3600,  # recycle connections every hour
)
```

### Date/Timezone Handling
- **All timestamps stored as UTC** in Oracle (`TIMESTAMP WITH TIME ZONE`)
- Backend: `datetime.utcnow()` or `datetime.now(timezone.utc)` — never naive datetimes
- API responses: ISO 8601 with `Z` suffix (e.g., `2026-04-30T10:00:00Z`)
- Frontend: display in user's local timezone via `date-fns` `formatInTimeZone`
- Expiry dates: stored as `DATE` (date-only, no time component) — expiry is end-of-day in facility's timezone

---

## EA9: Observability Standards

| Aspect | Tool | Standard |
|--------|------|----------|
| Logging | structlog → JSON | Every log entry: timestamp, level, correlation_id, facility_id, user_id, message |
| Metrics | Prometheus | Counters: requests, errors, alerts_generated. Gauges: active_lots, at_risk_lots. Histograms: scoring_duration, api_latency |
| Dashboards | Grafana | System health, API performance, scoring throughput, alert delivery |
| Tracing | OpenTelemetry | Distributed tracing across API → Service → DB → Cache |
| Alerting | Grafana Alerts | P1: API down, scoring failure. P2: latency > 2x target. P3: error rate > 1% |
| Health | `/health` + `/health/ready` | Liveness: process alive. Readiness: DB connected, Redis connected, Celery workers alive |

---

## EA10: Frontend Architecture

### React Standards
- Functional components only (no class components)
- TypeScript strict mode enabled
- Custom hooks for all reusable logic (`useAlerts`, `useLotScoring`, `useFacility`)
- TanStack Query for all server state (no manual fetch + useState)
- Zustand stores for UI-only state (sidebar, theme, filters)
- React Hook Form + Zod for all forms (no uncontrolled inputs)
- Lazy loading for route-level code splitting (`React.lazy` + `Suspense`)
- Error boundaries at route level

### Component Patterns
- **Atoms:** Button, Input, Badge, Skeleton, Icon (from Radix UI primitives)
- **Molecules:** AlertCard, LotRow, ScoreIndicator, KPICard, DateRangePicker
- **Organisms:** AlertFeed, LotTable, ScoringDashboard, ProductionSchedule
- **Templates:** DashboardLayout, FormLayout, ListLayout
- **Pages:** One per route, composed from templates + organisms

### Accessibility (WCAG 2.1 AA)
- Radix UI provides accessible primitives (focus management, ARIA, keyboard nav)
- All interactive elements: keyboard navigable, focus visible
- Color contrast: 4.5:1 minimum
- Screen reader: all images have alt text, all icons have aria-label
- Responsive: mobile-first, works on tablet (warehouse floor use)

---

## EA11: Design System Standards

### Based on Schreiber Horizon Brand
- Primary: `#F7A800` (amber/gold)
- Dark: `#1A1A2E` (deep navy)
- Neutrals: 50–900 scale
- Success/Warning/Error: `#2ECC71` / `#F7A800` / `#E74C3C`
- Font: Montserrat (headings), Open Sans (body)
- Spacing: 8px base grid
- Radius: 4/8/12/16px scale
- Shadows: sm/md/lg/xl scale
- Touch targets: 44px minimum (warehouse glove-friendly)

### Tailwind CSS Configuration
```js
// tailwind.config.js
module.exports = {
  theme: {
    extend: {
      colors: {
        brand: { primary: '#F7A800', dark: '#1A1A2E' },
        success: '#2ECC71', warning: '#F7A800', error: '#E74C3C',
      },
      fontFamily: {
        heading: ['Montserrat', 'sans-serif'],
        body: ['Open Sans', 'sans-serif'],
      },
    },
  },
}
```

---

## EA12: Compliance Architecture

| Regulation | Requirement | Implementation |
|-----------|-------------|---------------|
| FDA FSMA | Traceability of food products | Lot-level tracking with chain-of-custody |
| FDA 21 CFR Part 11 | Electronic records & signatures | Audit logs, user authentication, data integrity |
| GDPR (if EU facilities) | Data protection | PII encryption, data retention policies, right to erasure |
| SOC 2 Type II | Security controls | Access controls, audit logging, encryption |
| Food safety (HACCP) | Hazard analysis | QA hold/release workflow, expiry management |

---

## EA13: Code Standards

### Python (Backend)
- PEP 8 + Black formatter (line length 120)
- Type hints on all function signatures
- Docstrings on all public functions (Google style)
- `ruff` for linting (replaces flake8 + isort)
- No `print()` — use `structlog` logger
- No `*` imports
- Max function length: 50 lines
- Max file length: 300 lines

### TypeScript (Frontend)
- ESLint + Prettier (enforced in CI)
- Strict TypeScript (`strict: true` in tsconfig)
- No `any` type (use `unknown` + type guards)
- Named exports only (no default exports)
- Max component length: 150 lines
- Custom hooks for logic > 10 lines

### SQL / PL/SQL
- UPPERCASE for SQL keywords (`SELECT`, `INSERT`, `WHERE`)
- snake_case for table/column names
- Prefix: tables none, views `V_`, packages `PKG_`, procedures `P_`, functions `F_`
- All DDL changes via Alembic migrations (never manual)
- Comments on all stored procedures and complex queries

---

## EA14: Testing Standards

| Level | Tool | Target | Scope |
|-------|------|--------|-------|
| Unit (Backend) | pytest + factory_boy | ≥ 80% coverage | Service layer, domain logic |
| Unit (Frontend) | Jest/Vitest + RTL | ≥ 80% coverage | Components, hooks, utils |
| Integration (Backend) | pytest + TestClient | All API endpoints | Request → Response through stack |
| Integration (Frontend) | Playwright | Critical user journeys | Login → Dashboard → Alert → Acknowledge |
| Contract | Schema validation | All API responses | Response matches Pydantic schema |
| Performance | Locust | Scoring throughput | 10,000 lots scored in < 10 minutes |
| Security | Bandit + Trivy + Snyk | Zero critical/high | SAST + container + dependency scanning |
| Accessibility | axe-core + Playwright | Zero critical violations | WCAG 2.1 AA on all pages |

### Test Naming
- Python: `test_{what}_{when}_{expected}` (e.g., `test_score_lot_when_expired_returns_max_risk`)
- TypeScript: `it('should {expected} when {condition}')` (e.g., `it('should show alert badge when lot is at risk')`)

---

## EA15: Feature Flag Standards

- Feature flags via environment variables (simple) or Redis-backed config (dynamic)
- Naming: `FF_SCORING_ENGINE_V2`, `FF_INBOUND_PREDICTION`
- All new features behind flags in production
- Flags removed after feature is stable (max 30 days)

---

## EA16: Dependency Management

- **Python:** `pyproject.toml` with pinned versions (Poetry or pip-compile)
- **Frontend:** `package.json` with exact versions (no `^` or `~`)
- **Oracle:** Version locked to 19c+ (managed by DBA team)
- Dependency updates: monthly review, automated via Dependabot/Renovate
- No new dependencies without architecture review

---

## EA17: Documentation Standards

- API docs: auto-generated from FastAPI (OpenAPI 3.0 at `/docs`)
- Architecture decisions: ADR format (Context → Decision → Consequences)
- Runbooks: for each Celery task and PL/SQL procedure
- README: in every directory with > 3 files
- Inline comments: only for "why", never for "what"
