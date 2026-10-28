# EA Standards for Requirements Extraction
## kb-L1-enterprise-architecture-requirements-slim v1.0.0
Use these standards to generate CON, NFR, INT, and DR items that the vision document doesn't explicitly state but EA mandates.

## Mandatory Tech Stack (→ CON-Technology if product deviates)
Mobile: Kotlin 2.0, Jetpack Compose, Room, WorkManager, Hilt, OkHttp/Retrofit, CameraX, Firebase
Backend: C# 12, .NET 8, EF Core 8, MediatR, FluentValidation, Polly, Serilog
DB: SQL Server 2022, Redis 7.2
Infra: AKS, Azure API Management, Key Vault, Service Bus, App Configuration, DevOps
Security: SonarQube (SAST), OWASP ZAP (DAST), Snyk (dependency scan)
Rule: unlisted tech → output `UNLISTED_TECHNOLOGY_REQUIRED:[name]`

## NFR Targets (→ NFR items if vision doc is vague)
- API p95 < 500ms, p99 < 1000ms
- App cold start < 2s, warm < 500ms
- DB query p95 < 100ms
- Availability: 99.95% (≤22min downtime/month)
- RTO < 1hr, RPO < 15min
- Scalability: 10K concurrent users, 1K applications/hour
- Resilience: circuit breaker + retry (1s/2s/4s, max 3) on all external calls
- Timeouts: 30s API, 60s file upload
- Mobile: offline form saving, background sync, crash recovery
- Accessibility: WCAG 2.1 AA, min 48dp touch targets, TalkBack

## Security Constraints (→ CON-Regulatory / NFR-Security)
- Auth: OAuth 2.0 + PKCE, JWT RS256 15-min expiry, refresh 24hr rotated + device-bound
- Password: min 12 chars, BCrypt factor 12, lockout 5 failures/30min
- OTP: 6-digit, 90s expiry, rate 3/10min, SHA-256 hashed
- Transport: TLS 1.2+ mandatory, cert pinning (mobile)
- PII: encrypted at rest (AES-256), no PII in logs/URLs/errors, masked in non-prod
- Secrets: all in Key Vault, never in code/config
- Input validation: server-side mandatory, max length, HTML stripped
- Mobile: root detection, FLAG_SECURE on sensitive screens, Play Integrity API

## Compliance (→ CON-Regulatory items)
- GDPR: lawful basis required, data minimization, rights (access/erasure/portability), consent granular, marketing OFF by default
- PSD2 SCA: required for payments, sensitive data access. Two factors from knowledge/possession/inherence
- FCA Consumer Duty: transparent fees, plain-language terms, total cost visible, 14-day cooling-off
- PRA Operational Resilience: impact tolerances for important business services
- DORA: incident reporting within 4hr, third-party register, resilience testing

## Data Classification (→ DR items)
| Classification | Examples | Encryption |
|---------------|----------|-----------|
| Public | Product catalog, rates | No |
| Internal | App status, config | No |
| Confidential | Name, email, employment | AES-256 |
| Restricted | National ID, income, bank statements, biometrics | AES-256 |

PII fields requiring encryption: NationalId, DOB, Phone, Email, Address, Income, BankStatements
Soft delete only (hard delete only for GDPR erasure + audit entry)

## Data Retention (→ CON-Regulatory)
Application data: 7yr post-closure. Rejected apps: 3yr. KYC docs: 5yr post-relationship. Audit logs: 7yr. Marketing consent: duration + 1yr.

## Integration Infrastructure (→ INT items)
- Sync: REST/HTTPS via API Gateway (Mobile → Gateway → Backend)
- Async: Azure Service Bus topics (application-events, kyc-events, offer-events, loan-events, notification-events)
- All third-party calls: circuit breaker + fallback required
- Webhooks: HMAC signature verification, idempotent processing
- Event schema: {eventId, eventType, source, timestamp, correlationId, data, metadata}

## Audit Requirements (→ NFR / CON)
All PII access, state transitions, auth events, consent changes, data exports, admin actions MUST be audit-logged.
Append-only audit schema. Async writes (<5s). 7yr retention.
