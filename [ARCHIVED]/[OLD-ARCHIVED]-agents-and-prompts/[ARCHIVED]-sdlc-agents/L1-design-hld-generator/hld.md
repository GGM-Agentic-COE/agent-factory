# High-Level Design Document Template

## System Overview

| Attribute | Value |
|-----------|-------|
| Description | {what this system does at a high level} |
| Architecture Style | microservices / monolith / modular-monolith / serverless |
| Backend | {technology} |
| Frontend | {technology} |
| Database | {technology} |
| Cache | {technology} |
| Messaging | {technology} |

---

## Components

| ID | Name | Type | Responsibility | Implements | Technology |
|----|------|------|---------------|------------|------------|
| CMP-01 | {name} | service / database / cache / queue / gateway / client-app | {what it does} | F-XX.X | {tech} |
| CMP-02 | | | | | |

### Component Interactions

```
[Client App] → [API Gateway] → [Service A] → [Database]
                             → [Service B] → [Cache]
                                           → [Message Queue] → [Service C]
```

---

## APIs

| ID | Service | Method | Path | Description | Auth |
|----|---------|--------|------|-------------|------|
| API-01 | CMP-01 | POST | /api/v1/{resource} | {description} | JWT / API-key / none |
| API-02 | | | | | |

### API Detail: API-01

**Request:**
```json
{
  "field_1": "type (constraints)",
  "field_2": "type (constraints)"
}
```

**Response:**
```json
{
  "field_1": "type",
  "field_2": "type"
}
```

---

## Data Model

### Entities

| ID | Entity | Store Type | Technology | Key Fields |
|----|--------|-----------|------------|------------|
| DS-01 | {name} | relational / document / cache / time-series | PostgreSQL / MongoDB / Redis | {fields} |
| DS-02 | | | | |

### DS-01: {Entity Name}

| Field | Type | Constraints |
|-------|------|-------------|
| id | UUID | PK, DEFAULT uuid_generate_v4() |
| {field} | {type} | {constraints} |

### Relationships

| Source | Target | Type | Via Field |
|--------|--------|------|-----------|
| DS-01 | DS-02 | one-to-many | user_id |

---

## Integrations

| ID | External System | Pattern | Direction | Purpose | Implements |
|----|----------------|---------|-----------|---------|------------|
| INT-01 | {system} | REST / event / webhook / file-transfer / gRPC | inbound / outbound / bidirectional | {why} | F-XX.X |

---

## UI Architecture

### Platform

| Attribute | Value |
|-----------|-------|
| Type | web / mobile-native / mobile-cross-platform / desktop |
| Technology | {React / React Native / Swift / Kotlin / Flutter} |
| Targets | {iOS, Android, Web} |

### Screens

| ID | Screen | Purpose | Features | APIs Consumed |
|----|--------|---------|----------|---------------|
| SCR-01 | {name} | {what user does} | F-XX.X | API-XX |
| SCR-02 | | | | |

### Navigation

- **Pattern:** stack / bottom-tabs / drawer / combination
- **Flows:**
  - {Flow Name}: SCR-01 → SCR-02 → SCR-03
  - {Flow Name}: SCR-04 → SCR-05

### State Management

| Store | Scope | Persisted | Purpose |
|-------|-------|-----------|---------|
| {name} | global / feature | yes / no | {what state it holds} |

### Design System

- **Source:** {Material Design 3 / custom / shared library}
- **Key Components:** Button, Card, Input, Modal, Toast, ...

---

## Deployment

| Attribute | Value |
|-----------|-------|
| Topology | kubernetes / serverless / vm-based |

### Services

| Service | Replicas | Resources | Notes |
|---------|----------|-----------|-------|
| {name} | 2 | 256Mi / 0.25CPU | {notes} |

### Infrastructure

- Load balancer
- CDN
- Message broker
- {other}

---

## Architecture Decisions

### ADR-01: {Title}

- **Context:** {why this decision was needed}
- **Decision:** {what was decided}
- **Rationale:** {why this option was chosen}
- **Alternatives Considered:**
  - {Option 2} — rejected because {reason}
  - {Option 3} — rejected because {reason}

---

## Cross-Cutting Concerns

| Concern | Approach |
|---------|----------|
| Authentication | {JWT / OAuth2 / API keys — details} |
| Authorization | {RBAC / ABAC / policy engine — details} |
| Logging | {structured JSON / slog / ELK — details} |
| Monitoring | {OpenTelemetry / Datadog / Prometheus — details} |
| Error Handling | {standardised error responses, never expose internals} |
| Rate Limiting | {token bucket / sliding window — per endpoint/user} |
| Resilience | {circuit breaker, retries, timeouts, bulkhead} |

---

## Security

| Aspect | Approach |
|--------|----------|
| Data at rest | {AES-256 / KMS-managed encryption} |
| Data in transit | {TLS 1.3 / mTLS between services} |
| Secrets management | {Vault / Secret Manager / env-based} |
| Input validation | {validation layer, sanitisation, max payload size} |
| Vulnerability scanning | {SAST / DAST / dependency scanning tools} |
| Data classification | {which components handle Confidential/Restricted data} |

---

## Non-Functional Requirements Mapping

| NFR | Target | How Addressed |
|-----|--------|---------------|
| Performance | {e.g., <3s response time} | {caching, async processing, DB indexing} |
| Scalability | {e.g., 10K concurrent users} | {horizontal scaling, stateless services, connection pooling} |
| Availability | {e.g., 99.9% uptime} | {multi-replica, health checks, auto-restart} |
| Disaster Recovery | {RPO/RTO targets} | {backup strategy, failover, multi-region if needed} |

---

## Environment Strategy

| Environment | Purpose | Infra | Data |
|-------------|---------|-------|------|
| Development | Local dev + feature branches | Docker Compose / local | Seeded test data |
| Staging | Pre-production validation | Kubernetes (scaled down) | Anonymised production data |
| Production | Live users | Kubernetes (full scale) | Real data |

---

## Traceability

| Feature | Components | APIs | Data Stores | Screens |
|---------|-----------|------|-------------|---------|
| F-01.1 | CMP-01 | API-01 | DS-01 | SCR-01 |
| F-01.2 | CMP-01, CMP-02 | API-02 | DS-01, DS-02 | SCR-02 |
