# EA Standards for HLD Generation
## kb-L1-enterprise-architecture-hld-slim v1.0.0
Use these standards to ground high-level design decisions in approved architecture, infrastructure, and integration patterns.

## Architecture Patterns (mandatory)
Backend: Clean Architecture — Domain → Application → Infrastructure → Presentation (inward dependency only)
- Domain: entities, value objects, domain events, repository interfaces. Zero external deps.
- Application: use cases (MediatR handlers), DTOs, validators (FluentValidation). Depends on Domain only.
- Infrastructure: EF Core DbContext, repo implementations, external clients. Implements Domain/Application interfaces.
- Presentation: controllers, middleware, filters. Entry point.

Mobile: MVVM + Unidirectional Data Flow
- ViewModel (Hilt) → StateFlow → Compose UI. Repository pattern. Room persistence. WorkManager background. Navigation Compose routing.

CQRS: Commands via MediatR + FluentValidation pipeline. Queries via MediatR (may bypass validation). Separate read models for complex aggregations.

DDD: Bounded contexts — Auth, Products, Applications, KYC, Offers, Loans, Notifications. Each owns schema + entities + events. Cross-context via Service Bus domain events. Shared kernel: Money, DateRange, Address. Anti-corruption layer for third-party integrations.

State Machine: `Draft→Submitted→Verifying→UnderReview→Approved→OfferGenerated→OfferAccepted→Disbursed→Active→Closed`

## Tech Stack (mandatory — do not deviate)
Mobile: Kotlin 2.0, Jetpack Compose 1.7, Material Design 3, Room 2.6, WorkManager 2.9, OkHttp 4.12, Retrofit 2.11, Hilt 2.51, Navigation Compose 2.8, CameraX, Firebase Crashlytics/Performance, Coil 2.6
Backend: C# 12, .NET 8 Web API, EF Core 8, FluentValidation 11, Serilog 4, Polly 8, MediatR 12, AutoMapper 13, Swashbuckle 6
DB: SQL Server 2022, Redis 7.2
Infra: AKS, Azure API Management, Key Vault, Monitor, DevOps, Service Bus, App Configuration
Security tooling: SonarQube (SAST), OWASP ZAP (DAST), Snyk (deps)
Rule: unlisted tech → `UNLISTED_TECHNOLOGY_REQUIRED:[name]`

## Solution Structure
Backend:
```
src/LoanApp.{Domain|Application|Infrastructure|Api|Shared}/
tests/LoanApp.{Domain|Application|Infrastructure|Api}.Tests/
```
Mobile:
```
app/src/main/java/com/loanapp/{core|data|domain|ui/{feature}|workers}/
ui/{feature}/ contains Screen + ViewModel per screen
ui/components/ for design system (atoms/molecules/organisms)
```

## API Standards
- OpenAPI 3.0 required. Base: `/api/v{version}/{resource}`. Plural nouns. URL path versioning.
- Methods: GET(read), POST(create/action), PUT(replace), PATCH(partial), DELETE(soft only)
- Format: JSON, camelCase, ISO 8601. Envelope: `{data, meta, errors}`. Errors: RFC 7807.
- Pagination: offset/limit, max 100/page. Rate limits: read 100/min, write 20/min.
- Idempotency: all writes accept `Idempotency-Key` header, cache 24hr.
- Headers: Authorization (Bearer JWT), X-Correlation-Id (auto-gen), X-Device-Id (mobile), Content-Type, Accept
- File uploads: multipart, max 10MB/file, virus scan before storage.
- Health: /health (liveness), /health/ready (readiness — checks DB, Redis, Service Bus)

## Data Architecture
- One schema per bounded context. No cross-schema joins.
- Required columns: Id (GUID, NEWSEQUENTIALID), CreatedAt, CreatedBy, UpdatedAt, UpdatedBy, IsDeleted, Version (ROWVERSION)
- Soft delete only (hard delete: GDPR erasure + audit entry)
- PII encrypted AES-256 at app level: NationalId, DOB, Phone, Email, Address, Income, BankStatements. Keys in Key Vault.
- Classification: Public | Internal | Confidential | Restricted
- Naming: Tables PascalCase plural, Columns PascalCase, FKs {Table}Id, Indexes IX_{Table}_{Column}
- EF Core: one IEntityTypeConfiguration per entity, global query filter (.HasQueryFilter(!IsDeleted)), owned types for value objects
- Transactions: standard=ReadCommitted, financial=Serializable, reporting=RCSI
- Redis: product catalog 1hr, session 15min, cache-aside, invalidate on write
- Connection pool: max 100/instance. Timeout: 30s connect, 30s command (60s reporting)
- Zero-downtime migrations: additive only per release, 2-release process for destructive changes

## Integration Architecture
Sync: REST via API Gateway (Mobile → Gateway → Backend). Timeout 30s.
Async: Service Bus topics:
- application-events (submitted, approved, rejected)
- kyc-events (started, completed, failed)
- offer-events (generated, accepted, declined, expired)
- loan-events (created, payment.due, payment.received)
- notification-events (send)

Event schema: `{eventId, eventType: "domain.action", source, timestamp, correlationId, data, metadata: {version, userId}}`
Dead letter queue, max delivery 5.

Third-party integrations: all wrapped in circuit breaker (Polly) + fallback.
| Integration | Pattern | Fallback |
|-------------|---------|----------|
| KYC provider | Async callback | Queue for retry |
| Credit bureau | Synchronous | Block submission |
| SMS/FCM | Fire-and-forget | Queue and retry |
| Address lookup | Sync, cached | Manual entry |

Webhooks inbound: `POST /api/v1/webhooks/{provider}`, HMAC verification, idempotent (event ID dedup), respond 200 immediately, process async.

## Infrastructure & Deployment
- AKS: one namespace per env (dev/staging/prod). Resource limits mandatory. HPA on CPU/memory.
- Containers: base `mcr.microsoft.com/dotnet/aspnet:8.0-alpine`, multi-stage, <200MB, non-root, Trivy scan, Cosign signing.
- K8s resources: API 250m-500m CPU / 256-512Mi RAM. Workers 100m-250m / 128-256Mi. PDB minAvailable 1. Replicas 2-10.
- Network: default deny. Allow Gateway→API(8080), API→SQL(1433), API→Redis(6379), API→ServiceBus(5671).
- CI/CD: Azure DevOps. Pipeline: Build→UnitTest→SAST→ContainerBuild→IntegrationTest→DAST→Staging→Smoke→Prod(manual gate).
- DR: active-passive (paired regions). DB geo-replication + auto failover. Redis/ServiceBus geo-DR. Traffic Manager DNS failover. Quarterly drill.

## Security Architecture
- Auth: OAuth 2.0 + PKCE (mobile), JWT RS256 15-min, refresh 24hr rotated + device-bound
- Roles: Customer, Agent, Admin, System. Claims-based fine-grained. Gateway validates JWT, backend validates claims.
- Transport: TLS 1.2+, cert pinning (mobile), HSTS, security headers (CSP, X-Content-Type-Options, X-Frame-Options)
- PII: encrypted at rest, no PII in logs/URLs/errors, masked non-prod
- Secrets: Key Vault only. Rotation: JWT 90d, API keys 180d, DB passwords 90d.
- Mobile: root detection, FLAG_SECURE, Play Integrity, no sensitive data in backups, R8 obfuscation
- Input: FluentValidation at boundary, max length, HTML stripped, magic bytes for files, virus scan
- OWASP Top 10: role+claims(A01), AES+TLS+KeyVault(A02), parameterized(A03), threat modeling(A04), hardened containers(A05), Snyk(A06), OAuth+PKCE+MFA(A07), signed JWTs(A08), structured no-PII logging(A09), allowlist external calls(A10)

## Observability
- Logging: Serilog structured JSON. Correlation ID on every entry. NO PII. Levels: Debug(dev), Info(req/res), Warning(degraded), Error(failed), Fatal(crash).
- Metrics: Azure Monitor + App Insights. request_duration_ms, request_count, error_rate, circuit_breaker_state, queue_depth, cache_hit_ratio.
- Tracing: OpenTelemetry, W3C Trace Context. Spans for: HTTP, DB, cache, message, external API.
- Alerting: P1(page): error>5% 5min or p95>2s. P2(ticket): error>1% 15min. P3(dashboard): cache<80%, queue>100.

## NFR Targets
- API p95 < 500ms, p99 < 1000ms
- App cold start < 2s, warm < 500ms
- 99.95% availability (≤22min/month)
- RTO < 1hr, RPO < 15min
- 10K concurrent, 1K apps/hour
- Resilience: circuit breaker + retry (1s/2s/4s max 3) + bulkhead + graceful degradation
- Accessibility: WCAG 2.1 AA

## Compliance Constraints (for HLD to address)
- GDPR: data minimization, lawful basis, erasure support, consent granular, marketing OFF default
- PSD2 SCA: two-factor for payments + sensitive data. Exemptions for catalog + status views.
- FCA Consumer Duty: transparent fees, plain language, total cost visible
- PRA: impact tolerances for important business services
- Audit: all PII access, state transitions, auth events logged. Append-only, 7yr retention.
- Data retention: app data 7yr, rejected 3yr, KYC 5yr, audit 7yr
