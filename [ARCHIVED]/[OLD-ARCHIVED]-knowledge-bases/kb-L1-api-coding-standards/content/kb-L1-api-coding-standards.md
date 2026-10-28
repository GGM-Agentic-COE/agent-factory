# API Coding Standards — Knowledge Base
### kb-L0-api-coding-standards v1.0.0
### Language-agnostic standards for API code generation. All code generator agents MUST comply.

---

## AC1: Project Structure

Every API project MUST have clear separation:

| Layer | Responsibility | Depends On |
|-------|---------------|------------|
| Presentation (Controllers/Routes) | HTTP handling, request/response mapping | Application |
| Application (Handlers/Services) | Business logic, orchestration, validation | Domain |
| Domain (Entities/Models) | Business rules, value objects | Nothing |
| Infrastructure (Repositories/Clients) | DB access, external service calls | Domain interfaces |

Rules:
1. Domain layer has ZERO external dependencies
2. Application layer depends only on Domain
3. Infrastructure implements interfaces defined in Domain/Application
4. Presentation is the entry point — depends on Application

## AC2: Endpoint Implementation Pattern

Every endpoint MUST follow this flow:
```
Request → Validate → Authorize → Execute → Map Response → Return
```

1. **Validate**: reject malformed input before any business logic (400)
2. **Authorize**: verify the caller has permission for this resource (401/403)
3. **Execute**: run business logic via handler/service (may throw 422)
4. **Map**: convert domain result to response DTO (never expose entities directly)
5. **Return**: appropriate status code + response envelope

## AC3: Error Handling

```
ALL errors → Centralized error handler → RFC 7807 ProblemDetails
```

| Exception Type | HTTP Code | ProblemDetails type |
|---------------|-----------|-------------------|
| Validation failure | 400 | validation-error |
| Authentication missing/invalid | 401 | unauthorized |
| Authorization denied | 403 | forbidden |
| Resource not found | 404 | not-found |
| Conflict (idempotency/concurrency) | 409 | conflict |
| Business rule violation | 422 | business-rule-violation |
| Rate limit exceeded | 429 | rate-limited |
| Unhandled exception | 500 | internal-error |

Rules:
1. NEVER return stack traces in responses
2. ALWAYS include correlation ID in error responses
3. 400 errors MUST include field-level error details
4. 500 errors MUST log full exception server-side, return only correlation ID to client

## AC4: Request Validation

1. Validate at the API boundary (controller/route level)
2. Use the framework's validation mechanism (annotations, decorators, schemas)
3. Validate: required fields, types, ranges, formats, string lengths
4. Return ALL validation errors at once (not one at a time)
5. Validation is separate from business rules (validation = format, business = logic)

## AC5: Response Envelope

```json
// Success (single resource)
{ "data": { ... } }

// Success (list with pagination)
{ "data": [ ... ], "meta": { "pageNumber": 1, "pageSize": 20, "totalCount": 100 } }

// Error (RFC 7807 — NOT wrapped in data)
{ "type": "validation-error", "title": "Validation Error", "status": 400, "errors": [...] }
```

## AC6: Testing Standards

### Unit Tests
- One test class per handler/service
- Mock ALL external dependencies (DB, APIs, message bus)
- Test: happy path, validation failure, business rule violation, edge cases
- Naming: `{method}_when{condition}_should{result}` or `should {result} when {condition}`
- Minimum 80% line coverage on new code

### Contract Tests
- Validate response body matches expected schema (field names, types, nullability)
- Test every endpoint's success response AND error responses
- Ensure backward compatibility: existing fields still present with same types

### Integration Tests
- Test full request→response through the stack (with real/in-memory DB)
- Test: complete happy path flow, rejection paths, state machine transitions
- Use test data factories (no hardcoded PII)
- Each test is independent (own data, no shared state)

### Regression Tests (Brownfield)
- For every modified file: test that existing behaviour is unchanged
- Pattern: "Given existing {feature}, When {change} is deployed, Then {existing behaviour} still works"
- Run existing test suite BEFORE and AFTER changes — same results

## AC7: Database Patterns

1. Use ORM for all DB access (no raw SQL except complex aggregations)
2. Repository pattern: one repository per aggregate root
3. All queries parameterized (ORM handles this)
4. Pagination on all list queries (max 100 per page)
5. Indexes on: all FKs, all WHERE clause columns, all ORDER BY columns
6. Migrations: additive only per release (EA4 zero-downtime)

## AC8: External Service Integration

1. Wrap every external call in a circuit breaker
2. Timeout: 30s default, configurable per service
3. Retry: exponential backoff (1s, 2s, 4s), max 3 retries
4. Fallback: define degraded behaviour when service is down
5. Log: correlation ID, service name, response time, status (no PII)

## AC9: Logging

1. Structured logging (JSON format)
2. Every log entry: timestamp, level, correlation ID, service name
3. NEVER log: passwords, tokens, card numbers, national IDs, full names
4. Log levels: DEBUG (dev only), INFO (request/response summary), WARN (degraded), ERROR (failures)
5. Log at entry and exit of every handler/service method

## AC10: Code Quality

1. No TODO/FIXME in committed code (track as tickets)
2. All public methods have documentation comments
3. Max method length: 30 lines (excluding boilerplate)
4. Max class length: 300 lines
5. Cyclomatic complexity: max 10 per method
6. No unused imports/dependencies
7. Consistent formatting (use project's formatter config)
