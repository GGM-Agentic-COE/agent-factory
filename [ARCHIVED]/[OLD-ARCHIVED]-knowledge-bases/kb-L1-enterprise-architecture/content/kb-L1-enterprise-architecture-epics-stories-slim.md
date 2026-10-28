# EA Standards for Epics & Stories Generation
## kb-L1-enterprise-architecture-epics-stories-slim v1.0.0
Use these standards to ground epics/stories in architecture patterns, solution structure, and technical constraints.

## Architecture Pattern (→ story technical context)
Backend: Clean Architecture — Domain (entities, interfaces) → Application (handlers, DTOs, validators) → Infrastructure (EF Core, external clients) → Presentation (controllers, middleware)
Mobile: MVVM — ViewModel (Hilt) → StateFlow → Compose UI. Repository pattern. Room persistence. WorkManager background sync.
Communication: REST (client→server), Service Bus (inter-service events), event-driven state changes.
CQRS: Commands via MediatR with FluentValidation pipeline. Queries via MediatR (may skip validation). Separate read models for dashboards.
DDD Bounded Contexts: Auth, Products, Applications, KYC, Offers, Loans, Notifications. Each owns schema + events.

## Solution Structure (→ story file/component references)
Backend: `src/LoanApp.{Domain|Application|Infrastructure|Api|Shared}/` + `tests/LoanApp.{*}.Tests/`
Mobile: `app/src/main/java/com/loanapp/{core|data|domain|ui/{feature}|workers}/`
UI components: `ui/components/` (atoms, molecules, organisms), `ui/theme/` (colors, typography)

## Tech Stack (→ story acceptance criteria constraints)
Mobile: Kotlin 2.0, Jetpack Compose 1.7, Room 2.6, Hilt 2.51, Retrofit 2.11, OkHttp 4.12, WorkManager 2.9, CameraX, Navigation Compose, Coil 2.6
Backend: C# 12, .NET 8, EF Core 8, MediatR 12, FluentValidation 11, Polly 8, Serilog 4
DB: SQL Server 2022, Redis 7.2
Infra: AKS, API Management, Key Vault, Service Bus, App Configuration

## NFR Targets (→ story acceptance criteria)
- API p95 < 500ms, app cold start < 2s
- 99.95% availability, 10K concurrent users
- Circuit breaker + retry on external calls
- Offline form saving (Room + WorkManager sync)
- WCAG 2.1 AA, 48dp touch targets, TalkBack support
- All screens: ViewModel + StateFlow + UiState (Loading/Success/Error)

## Security (→ story acceptance criteria)
- Auth: OAuth 2.0 + PKCE, JWT 15-min, refresh 24hr rotated
- PII: AES-256 at rest, no PII in logs/URLs, masked in non-prod
- Input: server-side validation mandatory (client is UX only)
- Mobile: FLAG_SECURE on sensitive screens, cert pinning, root detection
- Sensitive actions: PSD2 SCA (two-factor)
- All auth events audit-logged

## Data Patterns (→ story data model context)
- Required columns on every table: Id (GUID), CreatedAt, CreatedBy, UpdatedAt, UpdatedBy, IsDeleted, Version (ROWVERSION)
- Soft delete only. PII encrypted (AES-256). Parameterized queries.
- Schemas: one per bounded context (auth, products, applications, kyc, offers, loans, notifications)
- Classification: Public | Internal | Confidential (name, email) | Restricted (NationalID, income, biometrics)
- Redis cache: product catalog 1hr, session 15min. Invalidate on write.

## Integration Patterns (→ story integration points)
- Sync: REST via API Gateway. Timeout 30s. Idempotency-Key on writes.
- Async: Service Bus topics — application-events, kyc-events, offer-events, loan-events, notification-events
- Event schema: {eventId, eventType: "domain.action", source, timestamp, correlationId, data, metadata}
- Third-party: circuit breaker + fallback (queue for retry, manual entry, block submission)
- Webhooks inbound: HMAC verification, idempotent, respond 200 immediately, process async

## Testing (→ story DoD criteria)
- Unit tests: 80% coverage on Application layer (xUnit + NSubstitute)
- Integration tests: all API endpoints (Testcontainers + WireMock)
- Mobile UI: Espresso + Compose UI Test for critical flows
- Naming: `MethodName_Scenario_ExpectedResult` (C#), backtick descriptive (Kotlin)
- All PRs: pass all tests + Snyk scan + SonarQube gate

## Sprint Structure (→ epic decomposition)
- 4 × 2-week sprints, production-deployable at each sprint end
- Sprint 1: Foundation (auth, design system, data models, CI/CD)
- Sprint 2: Core flows (primary capabilities)
- Sprint 3: Value-add (secondary capabilities)
- Sprint 4: Polish & cross-cutting (error handling, resilience, observability)
- Epics = business capabilities (not technical layers)

## Error Handling (→ story error scenarios)
Backend: Global middleware → RFC 7807. BusinessRule→422, NotFound→404, Conflict→409, Validation→400, Timeout→503.
Mobile: Result<T> sealed (Success/Error). ViewModel→UiState. User-friendly messages + retry. Technical→Crashlytics.

## Feature Flags (→ story rollout criteria)
All new features behind flag. Naming: `{context}.{feature}.{variant}`. Rollout: internal→staging→1%→10%→50%→100%. Both paths tested. Max 90-day lifetime.

## Design System (→ UI story constraints)
Atomic: Atoms (Button, TextField) → Molecules (FormField, SearchBar) → Organisms (RegistrationForm) → Templates → Pages
All components: @Preview (light+dark), contentDescription, min 48dp target, skeleton loading, error+retry states.
Theme: MaterialTheme custom ColorScheme. Spacing: 4dp base. Border radius: 4dp buttons, 8dp cards, 12dp modals.
