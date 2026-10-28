# Microservices Architecture Standards — Knowledge Base
### kb-L1-microservices-architecture v1.0.0
### Standards for designing and building microservices. All API development agents MUST comply.

---

## MS1: Core Principles

1. **Single Responsibility**: Each service owns ONE business capability (not a technical layer)
2. **Autonomous Deployment**: Each service is independently deployable without coordinating with other services
3. **Decentralised Data**: Each service owns its data store — no shared databases
4. **Smart Endpoints, Dumb Pipes**: Business logic lives in services, not in the communication layer
5. **Design for Failure**: Every inter-service call can fail — handle it gracefully
6. **Evolutionary Design**: Services can be rewritten/replaced without affecting others

---

## MS2: Service Boundaries

### Bounded Context Alignment
- Each microservice maps to ONE bounded context from Domain-Driven Design
- A bounded context is a boundary within which a domain model is consistent
- Cross-context communication happens via APIs or events — never shared models

### Service Sizing
| Signal | Too Large | Right Size | Too Small |
|--------|-----------|------------|-----------|
| Team ownership | Multiple teams | One team (2-pizza) | Fraction of a team |
| Deployment frequency | Blocked by unrelated changes | Independent release cycle | Deployed only with others |
| Data ownership | Multiple aggregates, mixed concerns | One aggregate root or cohesive set | Single entity with no logic |
| Change coupling | Changes ripple to many services | Changes are local | Every change needs orchestration |

### Decomposition Strategies
| Strategy | When to Use | Example |
|----------|-------------|---------|
| By business capability | Default approach | Payments Service, Lending Service, KYC Service |
| By subdomain | Complex domains | Core (lending), Supporting (notifications), Generic (auth) |
| By data ownership | Data isolation critical | Customer Service owns PII, Loan Service owns financial data |
| Strangler fig | Migrating from monolith | Extract one capability at a time behind a facade |

### Anti-Patterns
- **Distributed Monolith**: Services that must be deployed together — defeats the purpose
- **Shared Database**: Two services reading/writing the same tables — creates coupling
- **Chatty Services**: Service A calls Service B 10 times per request — merge or redesign
- **Nano-services**: Services so small they add overhead without value — merge related ones

---

## MS3: Inter-Service Communication

### Synchronous (Request-Response)

| Pattern | Protocol | When to Use | Latency |
|---------|----------|-------------|---------|
| REST | HTTP/JSON | CRUD operations, queries, simple commands | Low |
| gRPC | HTTP/2 + Protobuf | High-throughput internal calls, streaming | Very low |
| GraphQL | HTTP/JSON | Client-driven queries across services (BFF) | Medium |

**REST Rules:**
- Use for external-facing APIs and simple internal calls
- Follow OpenAPI 3.0 standards (kb-L1-openapi-standards)
- Timeout: 30s default, 5s for internal service-to-service
- Always include `X-Correlation-Id` for distributed tracing

**gRPC Rules:**
- Use for internal service-to-service when performance matters
- Define contracts in `.proto` files (versioned in repo)
- Use deadlines (not timeouts) — propagate remaining time across calls
- Bidirectional streaming for real-time data flows

### Asynchronous (Event-Driven)

| Pattern | When to Use | Delivery |
|---------|-------------|----------|
| Event Notification | "Something happened" — consumer decides what to do | At-least-once |
| Event-Carried State Transfer | Consumer needs data without calling back | At-least-once |
| Command Message | "Do this" — directed to specific consumer | Exactly-once (with idempotency) |
| Saga / Choreography | Multi-service transaction | At-least-once + compensation |

**Event Rules:**
- Events are FACTS (past tense): `OrderPlaced`, `PaymentReceived`, `LoanDisbursed`
- Commands are REQUESTS (imperative): `ProcessPayment`, `SendNotification`
- Events are immutable — never modify a published event
- Every event has: `eventId` (UUID), `eventType`, `source`, `timestamp`, `correlationId`, `data`
- Consumers MUST be idempotent — handle duplicate delivery gracefully

### Choosing Sync vs Async

| Criteria | Use Sync (REST/gRPC) | Use Async (Events) |
|----------|---------------------|-------------------|
| Caller needs immediate response | ✅ | ❌ |
| Operation can be deferred | ❌ | ✅ |
| Tight coupling acceptable | ✅ (temporarily) | ❌ |
| Multiple consumers need to react | ❌ | ✅ |
| Transaction across services | ❌ (use saga) | ✅ (choreography) |
| Query/read operation | ✅ | ❌ |

---

## MS4: API Gateway

### Responsibilities
- **Routing**: Route requests to correct service based on path
- **Authentication**: Validate JWT tokens, reject unauthenticated requests
- **Rate Limiting**: Per-client, per-endpoint throttling
- **Load Balancing**: Distribute across service instances
- **Protocol Translation**: External REST → internal gRPC (if applicable)
- **Response Aggregation**: Combine responses from multiple services (BFF pattern)
- **SSL Termination**: Handle TLS at the edge

### Rules
1. Gateway does NOT contain business logic — it's a routing/security layer
2. One gateway per client type (mobile gateway, web gateway, partner gateway)
3. Gateway timeout > downstream service timeout (to avoid premature client errors)
4. Circuit breaker at gateway level for each downstream service
5. Request/response logging at gateway (no PII — only metadata)
6. API versioning enforced at gateway level (`/api/v1/`, `/api/v2/`)

---

## MS5: Data Management

### Database per Service
```
Service A ──→ Database A (PostgreSQL)
Service B ──→ Database B (MongoDB)
Service C ──→ Database C (PostgreSQL)
```
- Each service has its OWN database (or schema)
- No direct cross-service database queries
- Data needed from another service: call its API or consume its events

### Data Consistency Patterns

| Pattern | Consistency | Use When |
|---------|-------------|----------|
| Saga (Choreography) | Eventual | Multi-service workflow, services react to events |
| Saga (Orchestration) | Eventual | Complex workflow with central coordinator |
| Two-Phase Commit | Strong | AVOID in microservices (blocks, doesn't scale) |
| CQRS + Event Sourcing | Eventual | Read/write separation, audit trail needed |
| Outbox Pattern | Eventual | Reliable event publishing with DB transaction |

### Saga Pattern (Choreography)
```
LoanService                PaymentService              NotificationService
    │                           │                            │
    │── LoanDisbursed ─────────▶│                            │
    │                           │── PaymentInitiated ───────▶│
    │                           │                            │── NotifySent
    │                           │                            │
    │   (if payment fails)      │                            │
    │◀── PaymentFailed ────────│                            │
    │── LoanReversed           │                            │
```

### Saga Pattern (Orchestration)
```
Orchestrator
    │── Step 1: Call LoanService.Disburse()
    │── Step 2: Call PaymentService.Initiate()
    │── Step 3: Call NotificationService.Send()
    │
    │   (if Step 2 fails)
    │── Compensate Step 1: Call LoanService.Reverse()
```

### Outbox Pattern
```
Within a single DB transaction:
  1. Write business data to business table
  2. Write event to outbox table
  
Separate process:
  3. Poll outbox table for unpublished events
  4. Publish to message broker
  5. Mark as published
```
- Guarantees: if business data is committed, event WILL be published
- Prevents: "data saved but event lost" or "event published but data rolled back"

---

## MS6: Resilience Patterns

### Circuit Breaker
```
CLOSED ──(failures > threshold)──▶ OPEN ──(timeout expires)──▶ HALF-OPEN
  ▲                                                               │
  └──────────────(success)────────────────────────────────────────┘
  └──────────────(failure)──▶ OPEN
```

| State | Behaviour |
|-------|-----------|
| Closed | Requests pass through. Failures counted. |
| Open | Requests fail immediately (fast-fail). No calls to downstream. |
| Half-Open | Limited requests pass through to test recovery. |

**Configuration per service:**
```yaml
circuit_breaker:
  failure_threshold: 5          # failures before opening
  failure_window: 30s           # window to count failures
  open_duration: 60s            # how long to stay open
  half_open_max_calls: 3        # test calls in half-open
  monitored_exceptions: [TimeoutException, ConnectionException]
  ignored_exceptions: [ValidationException, NotFoundException]
```

### Retry with Backoff
```
Attempt 1 → fail → wait 1s
Attempt 2 → fail → wait 2s
Attempt 3 → fail → wait 4s
Attempt 4 → give up → fallback
```
- Max retries: 3 (configurable per service)
- Backoff: exponential with jitter (prevent thundering herd)
- Only retry on transient errors (timeout, 503) — NOT on 400, 404, 422

### Bulkhead
- Isolate resources per downstream service (separate thread pools / connection pools)
- If Service A is slow, it doesn't exhaust resources needed for Service B
- Implementation: separate HTTP client instances per downstream service

### Timeout
| Call Type | Default Timeout |
|-----------|----------------|
| Internal service-to-service | 5 seconds |
| External third-party API | 30 seconds |
| Database query | 30 seconds (60s for reports) |
| Message publish | 10 seconds |

### Fallback Strategies
| Strategy | When | Example |
|----------|------|---------|
| Cached response | Read operation, stale data acceptable | Return cached product catalog |
| Default value | Non-critical enrichment | Return empty recommendations |
| Graceful degradation | Feature can work without dependency | Allow application save but block submission |
| Queue for retry | Write operation, eventual consistency OK | Queue payment for later processing |
| Fail fast | Critical dependency, no alternative | Return 503 with retry-after header |

---

## MS7: Service Discovery & Configuration

### Service Discovery
| Pattern | How It Works | Example |
|---------|-------------|---------|
| Client-side | Client queries registry, picks instance | Eureka, Consul |
| Server-side | Load balancer queries registry, routes | Kubernetes Service, AWS ALB |
| DNS-based | Service name resolves to instance IPs | Kubernetes DNS, Consul DNS |

**Kubernetes (recommended):**
- Each service is a Kubernetes `Service` object
- DNS: `{service-name}.{namespace}.svc.cluster.local`
- No external service registry needed — Kubernetes handles it

### Configuration Management
1. **Environment-specific config**: via environment variables or config maps
2. **Secrets**: via secret manager (Azure Key Vault, AWS Secrets Manager, K8s Secrets)
3. **Feature flags**: via feature flag service (LaunchDarkly, Azure App Configuration)
4. **Shared config**: via centralised config service (Spring Cloud Config, Consul KV)

**Rules:**
- No secrets in code or config files committed to git
- Config changes should NOT require redeployment (externalised)
- Feature flags for gradual rollout of new capabilities
- Config per environment (dev/staging/prod) — same image, different config

---

## MS8: Observability

### Three Pillars

**1. Logging**
- Structured JSON logs with: timestamp, level, service, correlationId, traceId, spanId
- NO PII in logs (mask sensitive fields)
- Log at service boundaries: request received, response sent, external call made
- Centralised log aggregation (ELK, Loki, CloudWatch)

**2. Metrics**
- RED metrics per service: Rate (requests/sec), Errors (error rate), Duration (latency percentiles)
- USE metrics per resource: Utilisation, Saturation, Errors
- Business metrics: applications/hour, approval rate, disbursement volume
- Export via Prometheus/OpenTelemetry → Grafana dashboards

**3. Distributed Tracing**
- Trace context propagated via W3C Trace Context headers
- Every inter-service call creates a span
- Spans linked by traceId → visualise full request path
- Tools: Jaeger, Zipkin, AWS X-Ray, Azure Application Insights

### Health Checks
```
GET /health          → Liveness (is the process running?)
GET /health/ready    → Readiness (can it serve traffic? checks DB, cache, dependencies)
GET /health/startup  → Startup (has it finished initialising?)
```

### Alerting
| Severity | Condition | Action |
|----------|-----------|--------|
| P1 (page) | Error rate > 5% for 5min, service down | Page on-call engineer |
| P2 (ticket) | Error rate > 1% for 15min, latency p95 > 2s | Create ticket |
| P3 (dashboard) | Cache hit ratio < 80%, queue depth growing | Dashboard alert |

---

## MS9: Security

### Zero Trust
- Every service-to-service call is authenticated (mTLS or JWT)
- No implicit trust based on network location
- Principle of least privilege: services only access what they need

### Authentication & Authorization
| Layer | Mechanism |
|-------|-----------|
| External → Gateway | OAuth 2.0 + JWT (user identity) |
| Gateway → Service | JWT propagation (validated at gateway) |
| Service → Service | mTLS (mutual TLS) or service-account JWT |
| Service → Database | Service-specific credentials (rotated) |

### Data Protection
- PII encrypted at rest (AES-256) and in transit (TLS 1.2+)
- Each service encrypts its own PII — don't rely on DB-level encryption alone
- Data classification per field: Public, Internal, Confidential, Restricted
- GDPR/privacy: each service knows what PII it holds and can delete it on request

### Secrets Management
- All secrets in vault (Azure Key Vault, HashiCorp Vault, AWS Secrets Manager)
- Secrets injected at runtime (env vars or mounted files) — never in code
- Rotation policy: DB passwords every 90 days, API keys every 180 days
- Audit: log every secret access

---

## MS10: Deployment & CI/CD

### Container Standards
- One service per container
- Base image: minimal (Alpine, distroless)
- Non-root user in container
- Health check in Dockerfile
- Image size < 200MB
- Image scanned for vulnerabilities (Trivy, Snyk)
- Image signed for supply chain security

### Kubernetes Deployment
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: loan-service
spec:
  replicas: 2                    # min 2 for availability
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1
      maxUnavailable: 0          # zero-downtime deployment
  template:
    spec:
      containers:
        - name: loan-service
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits: { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /health, port: 8080 }
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            periodSeconds: 5
```

### CI/CD Pipeline
```
Code Push → Build → Unit Test → SAST → Container Build → Integration Test → DAST → Deploy Staging → Smoke Test → Deploy Prod (manual gate)
```

### Deployment Strategies
| Strategy | Risk | Rollback Speed | Use When |
|----------|------|----------------|----------|
| Rolling Update | Low | Medium | Default for most services |
| Blue-Green | Very Low | Instant | Critical services, DB migrations |
| Canary | Very Low | Fast | High-traffic services, risky changes |
| Feature Flag | None | Instant | Gradual feature rollout |

---

## MS11: Testing Strategy

### Test Pyramid for Microservices
```
         ╱  E2E / Contract  ╲        ← Few: cross-service flows
        ╱  Integration Tests  ╲      ← Some: service + DB + mocks
       ╱    Unit Tests          ╲    ← Many: business logic
```

### Contract Testing
- Producer publishes contract (OpenAPI spec or Pact)
- Consumer verifies against contract
- Contract tests run in CI — break the build if contract violated
- Prevents: "Service A changed its response and broke Service B"

### Testing in Isolation
| Dependency | How to Mock |
|------------|-------------|
| Other microservice | WireMock / mock server with recorded responses |
| Database | In-memory DB (H2, SQLite) or Testcontainers |
| Message broker | In-memory broker or embedded Kafka |
| External API | WireMock with stubbed responses |

---

## MS12: Anti-Patterns & Pitfalls

| Anti-Pattern | Problem | Fix |
|-------------|---------|-----|
| Shared database | Tight coupling, schema changes break multiple services | Database per service |
| Synchronous chain | A→B→C→D — latency compounds, one failure breaks all | Use async events for non-critical steps |
| Distributed monolith | Services must deploy together | True independence — no shared libraries with business logic |
| No circuit breaker | Cascading failures | Circuit breaker on every external call |
| Chatty communication | 10+ calls between services per request | Aggregate data, use event-carried state transfer |
| Shared domain model | Services share entity classes | Each service has its own models, translate at boundaries |
| No idempotency | Duplicate messages cause duplicate processing | Idempotency keys on all write operations |
| Ignoring CAP theorem | Expecting strong consistency across services | Design for eventual consistency, use sagas |
| Over-decomposition | 50 services for a 5-person team | Start with fewer, larger services — split when needed |
| No observability | Can't debug production issues | Logging + metrics + tracing from day one |

---

## MS13: Event Schema Versioning

Events evolve over time. Consumers must handle old and new versions.

### Versioning Strategy
```json
{
  "eventId": "uuid",
  "eventType": "loan.disbursed",
  "version": "2",
  "source": "loan-service",
  "timestamp": "ISO8601",
  "data": { ... }
}
```

### Compatibility Rules
| Change | Backward Compatible? | Action |
|--------|---------------------|--------|
| Add optional field | ✅ Yes | Add with default, consumers ignore unknown fields |
| Remove field | ❌ No | Deprecate (keep sending), remove after all consumers migrate |
| Rename field | ❌ No | Add new field, keep old field, deprecate old |
| Change field type | ❌ No | New version (v2), run both versions in parallel |

### Schema Registry
- All event schemas registered in a central schema registry
- Producers validate events against schema before publishing
- Consumers validate events against schema on receipt
- Schema changes require compatibility check before deployment

---

## MS14: Idempotency Implementation

### API Idempotency
```
Client sends: POST /api/v1/payments
Headers: Idempotency-Key: {client-generated-UUID}

Server:
  1. Check idempotency store for this key
  2. If found → return cached response (no re-execution)
  3. If not found → execute, store result with key (TTL: 24hrs), return response
```

### Event Consumer Idempotency
```
Consumer receives event:
  1. Extract eventId from event envelope
  2. Check processed_events table for this eventId
  3. If found → skip (already processed), acknowledge message
  4. If not found → process, insert eventId into processed_events, acknowledge
```

### Idempotency Store
| Field | Type | Notes |
|-------|------|-------|
| idempotency_key | string | PK — the client-provided UUID or eventId |
| response_status | int | HTTP status code of original response |
| response_body | json | Serialised response body |
| created_at | timestamp | For TTL cleanup |

- TTL: 24 hours for API keys, 7 days for event IDs
- Cleanup: background job purges expired entries

---

## MS15: CQRS & Read Models

### When to Use CQRS
- Read and write patterns differ significantly (e.g., complex queries vs simple writes)
- Read scale >> write scale (10:1 or more)
- Different data shapes needed for reads vs writes (denormalised views)

### Implementation
```
Write Side:                          Read Side:
  Command → Handler → Domain →         Event → Projector → Read Model →
  Event Store / Write DB                Read DB (denormalised)
       │                                     ▲
       └── Publish Event ──────────────────┘
```

### Read Model (Materialised View)
- Separate database/table optimised for queries
- Updated asynchronously via events (eventual consistency)
- Can be rebuilt from event history at any time
- Acceptable staleness: typically < 1 second

### Rules
1. Write side: normalised, enforces business rules, source of truth
2. Read side: denormalised, optimised for queries, eventually consistent
3. Read models can be deleted and rebuilt without data loss
4. UI must handle eventual consistency (show "updating..." indicator)

---

## MS16: Service Mesh

### What It Provides
- **mTLS**: Automatic mutual TLS between all services (zero-trust networking)
- **Traffic management**: Retries, timeouts, circuit breaking at infrastructure level
- **Observability**: Automatic metrics, traces, access logs without code changes
- **Traffic splitting**: Canary deployments, A/B testing at network level

### Architecture
```
Service A Pod                    Service B Pod
┌──────────────────┐            ┌──────────────────┐
│ App Container    │            │ App Container    │
│                  │            │                  │
│ Sidecar Proxy ◄─┼── mTLS ──▶┼─► Sidecar Proxy  │
│ (Envoy/Linkerd) │            │ (Envoy/Linkerd)  │
└──────────────────┘            └──────────────────┘
         │                               │
         └───────── Control Plane ───────┘
                   (Istio/Linkerd)
```

### When to Use
| Use Service Mesh | Don't Use |
|-----------------|-----------|
| > 10 services | < 5 services (overhead not justified) |
| Zero-trust security required | Simple internal network |
| Need traffic splitting for canary | Simple rolling deployments sufficient |
| Want observability without code changes | Already have comprehensive instrumentation |

### Rules
1. Service mesh handles cross-cutting concerns — remove from application code
2. Application still handles business-level retries and circuit breaking
3. Mesh retries are for transport failures; app retries are for business failures
4. Configure mesh timeouts LONGER than application timeouts

---

## MS17: API-First Development

### Mandate
1. OpenAPI spec MUST be written BEFORE implementation code
2. Spec is the contract — code is generated from or validated against it
3. Spec reviewed and approved before development starts
4. Breaking changes to spec require API review board approval

### Workflow
```
1. Write OpenAPI spec (per kb-L1-openapi-standards)
2. Review spec (API review board)
3. Generate server stubs / client SDKs from spec
4. Implement business logic in generated stubs
5. Contract tests validate implementation matches spec
6. Spec published to API catalog / developer portal
```

### Consumer-Driven Contracts
- Consumers define what they need from a provider (Pact tests)
- Provider verifies it satisfies all consumer contracts
- Prevents: provider changing API in ways that break consumers
- Run in CI: consumer Pact tests → provider verification → deploy

---

## Cross-References to Enterprise Architecture

This KB aligns with and extends:
- **EA1** (Technology Stack): service-specific tech choices within approved stack
- **EA2** (Architecture Patterns): CQRS, DDD bounded contexts, Clean Architecture per service
- **EA3** (API Standards): REST/OpenAPI for external, gRPC optional for internal
- **EA4** (Data Architecture): database per service, encryption, audit columns
- **EA5** (Security): OAuth 2.0 at gateway, mTLS between services, secrets in vault
- **EA6** (Deployment): AKS, CI/CD pipeline, container standards
- **EA7** (NFRs): p95 latency, availability, resilience patterns
- **EA8** (Integration): event topics, canonical schema, circuit breakers
- **EA9** (Observability): logging, metrics, tracing standards
- **EA12** (Compliance): audit trail, data retention per service
- **EA15** (Feature Flags): gradual rollout of new service capabilities
