# OpenAPI 3.0 Specification Standards — Knowledge Base
### kb-L1-openapi-standards v1.0.0
### This KB defines OpenAPI 3.0 specification standards for all API design agents. Agents creating or updating API specs MUST comply with these standards.

---

## OA1: Document Structure

Every OpenAPI 3.0 document MUST have this top-level structure:

```yaml
openapi: "3.0.3"                    # MUST be 3.0.x (3.0.3 recommended)
info:                                # REQUIRED — API metadata
  title: string                      # REQUIRED — human-readable name
  version: string                    # REQUIRED — API version (semver)
  description: string                # RECOMMENDED — markdown supported
  contact:                           # RECOMMENDED
    name: string
    email: string
    url: string
  license:                           # RECOMMENDED
    name: string
    url: string
servers:                             # REQUIRED — at least one
  - url: string                      # REQUIRED — base URL
    description: string              # RECOMMENDED
    variables: {}                    # OPTIONAL — URL template variables
paths:                               # REQUIRED — API endpoints
  /resource:                         # path item
    get: {}                          # operation
security:                            # OPTIONAL — global security
components:                          # OPTIONAL — reusable schemas
tags:                                # RECOMMENDED — logical grouping
externalDocs:                        # OPTIONAL
```

### Version Rules
- `openapi` field MUST be `"3.0.3"` (latest stable 3.0.x)
- `info.version` follows semver: `{major}.{minor}.{patch}`
- Major bump: breaking changes (removed endpoints, changed field types)
- Minor bump: new endpoints, new optional fields
- Patch bump: description fixes, example updates

---

## OA2: Info Object

```yaml
info:
  title: "Tasheel Finance API"
  version: "1.0.0"
  description: |
    RESTful API for the Tasheel Finance lending platform.
    
    ## Authentication
    All endpoints require Bearer JWT unless marked as public.
    
    ## Error Handling
    All errors follow RFC 7807 Problem Details format.
  contact:
    name: "API Team"
    email: "api-team@example.com"
  license:
    name: "Proprietary"
```

**RULES:**
- `title` MUST be the product/service name, not "API" alone
- `description` SHOULD include: auth overview, error format, rate limits
- `version` MUST match the URL path version (`/api/v1/` → version `"1.0.x"`)

---

## OA3: Servers

```yaml
servers:
  - url: "https://api.example.com/api/v1"
    description: "Production"
  - url: "https://staging-api.example.com/api/v1"
    description: "Staging"
  - url: "http://localhost:5000/api/v1"
    description: "Local development"
```

**RULES:**
- MUST include at least production and local dev servers
- URLs MUST include the base path (`/api/v1`)
- No trailing slash on URLs
- Server variables for multi-tenant or regional deployments:
  ```yaml
  servers:
    - url: "https://{region}.api.example.com/api/v1"
      variables:
        region:
          default: "sa"
          enum: ["sa", "ae", "bh"]
  ```

---

## OA4: Paths & Operations

### Path Naming
```yaml
paths:
  /products:                          # plural nouns — NEVER verbs
    get: {}                           # list products
    post: {}                          # create product
  /products/{productId}:              # singular resource by ID
    get: {}                           # get product
    put: {}                           # replace product
    patch: {}                         # partial update
    delete: {}                        # delete product
  /products/{productId}/reviews:      # nested sub-resource
    get: {}                           # list reviews for product
  /applications/{id}/submit:          # action on resource
    post: {}                          # submit application
```

**PATH RULES:**
1. Resource names: plural nouns (`/products`, `/applications`, `/loans`)
2. NEVER use verbs in paths (`/getProducts` ❌, `/products` ✅)
3. Actions on resources: `POST /{resource}/{id}/{action}` (`/applications/{id}/submit`)
4. Nested resources for ownership: `/{parent}/{parentId}/{child}`
5. Path parameters: camelCase (`{productId}`, `{applicationId}`)
6. Max nesting depth: 2 levels (`/loans/{id}/payments` ✅, `/loans/{id}/payments/{pid}/refunds` ❌ — flatten to `/payments/{pid}/refunds`)
7. No PII in paths — NEVER `/users/{email}` or `/users/{nationalId}`

### HTTP Methods

| Method | Semantics | Idempotent | Request Body | Success Code |
|--------|-----------|------------|--------------|--------------|
| GET | Read resource(s) | Yes | No | 200 |
| POST | Create resource or trigger action | No | Yes | 201 (create), 200 (action) |
| PUT | Full replace of resource | Yes | Yes | 200 |
| PATCH | Partial update | No | Yes | 200 |
| DELETE | Remove resource (soft delete) | Yes | No | 204 |

**METHOD RULES:**
- GET MUST NOT have a request body
- POST for creation MUST return 201 with Location header
- POST for actions (submit, assess, accept) returns 200
- PUT replaces the entire resource — all fields required
- PATCH updates only provided fields — omitted fields unchanged
- DELETE MUST be soft delete (set `isDeleted=true`) — never hard delete

### Operation Object

```yaml
paths:
  /applications:
    post:
      operationId: createApplication          # REQUIRED — unique, camelCase
      summary: "Create a new loan application" # REQUIRED — one line
      description: |                           # RECOMMENDED — detailed
        Creates a new loan application in Draft status.
        The application must be submitted separately via POST /applications/{id}/submit.
      tags:
        - Applications                         # REQUIRED — logical group
      security:
        - bearerAuth: []                       # REQUIRED unless public
      parameters: []                           # query/header/path params
      requestBody:                             # for POST/PUT/PATCH
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/CreateApplicationRequest'
      responses:                               # REQUIRED
        '201':
          description: "Application created"
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/ApplicationResponse'
        '400':
          $ref: '#/components/responses/ValidationError'
        '401':
          $ref: '#/components/responses/Unauthorized'
        '500':
          $ref: '#/components/responses/InternalError'
```

**OPERATION RULES:**
- `operationId` REQUIRED on every operation — camelCase, unique across spec
- `summary` REQUIRED — one sentence, no period
- `tags` REQUIRED — at least one tag per operation
- `responses` MUST include: success code + 400 + 401 + 500 at minimum
- `security` MUST be specified (or inherited from global)

---

## OA5: Parameters

### Path Parameters
```yaml
parameters:
  - name: applicationId
    in: path
    required: true                    # ALWAYS true for path params
    description: "Unique application identifier"
    schema:
      type: string
      format: uuid
      example: "550e8400-e29b-41d4-a716-446655440000"
```

### Query Parameters
```yaml
parameters:
  - name: pageNumber
    in: query
    required: false
    description: "Page number (1-based)"
    schema:
      type: integer
      minimum: 1
      default: 1
  - name: pageSize
    in: query
    required: false
    description: "Items per page"
    schema:
      type: integer
      minimum: 1
      maximum: 100
      default: 20
  - name: sortBy
    in: query
    required: false
    schema:
      type: string
      enum: [createdAt, amount, status]
      default: createdAt
  - name: sortOrder
    in: query
    required: false
    schema:
      type: string
      enum: [asc, desc]
      default: desc
  - name: status
    in: query
    required: false
    description: "Filter by status"
    schema:
      type: string
      enum: [Draft, Submitted, Approved, Active, Settled, Closed]
```

### Header Parameters
```yaml
parameters:
  - name: X-Correlation-Id
    in: header
    required: false
    description: "Correlation ID for distributed tracing. Auto-generated if not provided."
    schema:
      type: string
      format: uuid
  - name: Idempotency-Key
    in: header
    required: true                    # REQUIRED on all POST/PUT/PATCH
    description: "Client-generated UUID for idempotent requests"
    schema:
      type: string
      format: uuid
```

**PARAMETER RULES:**
- Path params: ALWAYS `required: true`, use `format: uuid` for IDs
- Query params: camelCase names (`pageSize`, `sortBy`, `filterStatus`)
- Pagination: `pageNumber` (1-based) + `pageSize` (max 100, default 20)
- Sorting: `sortBy` + `sortOrder` (asc/desc)
- Filtering: `filter{Field}` or just field name as query param
- NEVER put PII in query parameters (logged in access logs)
- `X-Correlation-Id`: auto-generated if missing, echoed in response
- `Idempotency-Key`: REQUIRED on all write operations (POST/PUT/PATCH)

---

## OA6: Request Bodies

```yaml
requestBody:
  required: true
  content:
    application/json:
      schema:
        $ref: '#/components/schemas/CreateApplicationRequest'
      examples:
        standard:
          summary: "Standard application"
          value:
            productId: "11111111-1111-1111-1111-111111111111"
            requestedAmount: 50000
            requestedTenure: 24
            fullName: "Jane Doe"
            nationalId: "1234567890"
```

### File Uploads
```yaml
requestBody:
  required: true
  content:
    multipart/form-data:
      schema:
        type: object
        required: [file, documentType]
        properties:
          file:
            type: string
            format: binary
            description: "Document file (max 10MB)"
          documentType:
            type: string
            enum: [nationalId, payslip, bankStatement]
      encoding:
        file:
          contentType: "image/jpeg, image/png, application/pdf"
```

**REQUEST BODY RULES:**
- Content type: `application/json` for data, `multipart/form-data` for files
- `required: true` for POST/PUT, `required: false` for PATCH
- ALWAYS provide `examples` with realistic (but fake) data
- File uploads: max 10MB per file, 25MB per request
- Allowed file types: `image/jpeg`, `image/png`, `application/pdf`
- No PII in examples — use placeholder data ("Jane Doe", "1234567890")

---

## OA7: Responses

### Success Response Envelope
ALL success responses MUST use this envelope:

```yaml
components:
  schemas:
    SuccessResponse:
      type: object
      properties:
        data:
          description: "Response payload"
        meta:
          $ref: '#/components/schemas/PaginationMeta'
        errors:
          type: array
          items: {}
          default: []

    PaginationMeta:
      type: object
      properties:
        pageNumber:
          type: integer
          example: 1
        pageSize:
          type: integer
          example: 20
        totalCount:
          type: integer
          example: 150
        totalPages:
          type: integer
          example: 8
```

### Single Resource Response
```yaml
responses:
  '200':
    description: "Product retrieved"
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              $ref: '#/components/schemas/Product'
```

### List Response with Pagination
```yaml
responses:
  '200':
    description: "Products listed"
    content:
      application/json:
        schema:
          type: object
          properties:
            data:
              type: array
              items:
                $ref: '#/components/schemas/Product'
            meta:
              $ref: '#/components/schemas/PaginationMeta'
    headers:
      X-Total-Count:
        schema:
          type: integer
        description: "Total number of items"
```

### Standard Response Headers
```yaml
headers:
  X-Correlation-Id:
    schema:
      type: string
      format: uuid
    description: "Echo of request correlation ID"
  X-RateLimit-Limit:
    schema:
      type: integer
    description: "Max requests per window"
  X-RateLimit-Remaining:
    schema:
      type: integer
    description: "Remaining requests in window"
  X-RateLimit-Reset:
    schema:
      type: integer
    description: "Window reset time (Unix epoch)"
```

**RESPONSE RULES:**
- ALL success responses wrapped in `{ "data": ... }` envelope
- List endpoints include `meta` with pagination info
- Single resource: `{ "data": { ... } }`
- List: `{ "data": [ ... ], "meta": { ... } }`
- Created (201): include `Location` header with resource URL
- No content (204): no response body (DELETE)
- ALWAYS include `X-Correlation-Id` in response headers

---

## OA8: Error Responses (RFC 7807)

ALL error responses MUST use RFC 7807 Problem Details:

```yaml
components:
  schemas:
    ProblemDetails:
      type: object
      required: [type, title, status]
      properties:
        type:
          type: string
          description: "URI identifying the problem type"
          example: "https://api.example.com/problems/validation-error"
        title:
          type: string
          description: "Short human-readable summary"
          example: "Validation Error"
        status:
          type: integer
          description: "HTTP status code"
          example: 400
        detail:
          type: string
          description: "Human-readable explanation"
          example: "The requestedAmount must be between 5000 and 250000"
        instance:
          type: string
          description: "URI identifying this specific occurrence"
          example: "/api/v1/applications/550e8400/assess"
        errors:
          type: array
          description: "Field-level validation errors"
          items:
            type: object
            properties:
              field:
                type: string
                example: "requestedAmount"
              message:
                type: string
                example: "Must be between 5000 and 250000"

  responses:
    ValidationError:
      description: "Request validation failed"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "validation-error"
            title: "Validation Error"
            status: 400
            errors:
              - field: "requestedAmount"
                message: "Must be between 5000 and 250000"

    Unauthorized:
      description: "Authentication required"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "unauthorized"
            title: "Unauthorized"
            status: 401
            detail: "Bearer token is missing or expired"

    Forbidden:
      description: "Insufficient permissions"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "forbidden"
            title: "Forbidden"
            status: 403

    NotFound:
      description: "Resource not found"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "not-found"
            title: "Not Found"
            status: 404

    BusinessRuleViolation:
      description: "Business rule violated"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "business-rule-violation"
            title: "Application must be Submitted to assess"
            status: 422

    RateLimited:
      description: "Too many requests"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "rate-limited"
            title: "Too Many Requests"
            status: 429
      headers:
        Retry-After:
          schema:
            type: integer
          description: "Seconds to wait before retrying"

    InternalError:
      description: "Internal server error"
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/ProblemDetails'
          example:
            type: "internal-error"
            title: "Internal Server Error"
            status: 500
            detail: "An unexpected error occurred. Reference: {correlationId}"
```

### Standard Error Codes

| Code | Type | When |
|------|------|------|
| 400 | validation-error | Request body fails schema/business validation |
| 401 | unauthorized | Missing/expired/invalid JWT |
| 403 | forbidden | Valid JWT but insufficient role/scope |
| 404 | not-found | Resource ID doesn't exist |
| 409 | conflict | Idempotency conflict or optimistic concurrency |
| 422 | business-rule-violation | Valid request but violates business rule |
| 429 | rate-limited | Rate limit exceeded |
| 500 | internal-error | Unhandled server error |
| 503 | service-unavailable | Dependency down (DB, external service) |

**ERROR RULES:**
- Error responses MUST NOT be wrapped in `{ "data": ... }` envelope
- Error responses are the ProblemDetails object directly
- 400 errors MUST include field-level `errors` array
- 500 errors MUST include correlation ID, MUST NOT include stack trace
- 401/403 MUST NOT leak information about resource existence
- No PII in error messages — never "User john@example.com not found"

---

## OA9: Schema Design

### Naming Conventions
- Schema names: PascalCase (`CreateApplicationRequest`, `ProductResponse`)
- Property names: camelCase (`requestedAmount`, `monthlyPayment`)
- Enum values: PascalCase (`Draft`, `Submitted`, `Approved`)
- Date/time: ISO 8601 (`2026-04-20T10:30:00Z`)
- Currency: minor units or decimal with explicit precision

### Schema Patterns

**Request schema** (what client sends):
```yaml
CreateApplicationRequest:
  type: object
  required: [productId, requestedAmount, requestedTenure, fullName]
  properties:
    productId:
      type: string
      format: uuid
      description: "Product to apply for"
    requestedAmount:
      type: number
      format: double
      minimum: 1000
      maximum: 500000
      description: "Requested loan amount in SAR"
    requestedTenure:
      type: integer
      minimum: 3
      maximum: 60
      description: "Requested tenure in months"
    fullName:
      type: string
      minLength: 2
      maxLength: 100
      description: "Applicant full legal name"
```

**Response schema** (what server returns):
```yaml
ApplicationResponse:
  type: object
  properties:
    id:
      type: string
      format: uuid
      readOnly: true
    productId:
      type: string
      format: uuid
    productName:
      type: string
    status:
      type: string
      enum: [Draft, Submitted, Verifying, Approved, Referred, OfferGenerated, OfferAccepted, Active, Settled, Closed, Abandoned]
    requestedAmount:
      type: number
    approvedAmount:
      type: number
      nullable: true
      description: "Populated after assessment"
    createdAt:
      type: string
      format: date-time
      readOnly: true
```

### Common Types
```yaml
components:
  schemas:
    Money:
      type: number
      format: double
      description: "Monetary amount in SAR"
      example: 50000.00

    DateOnly:
      type: string
      format: date
      description: "ISO 8601 date"
      example: "2026-04-20"

    DateTime:
      type: string
      format: date-time
      description: "ISO 8601 date-time in UTC"
      example: "2026-04-20T10:30:00Z"

    UUID:
      type: string
      format: uuid
      example: "550e8400-e29b-41d4-a716-446655440000"

    Percentage:
      type: number
      format: double
      minimum: 0
      maximum: 100
      description: "Percentage value (e.g., 20.0 for 20%)"
```

**SCHEMA RULES:**
- ALWAYS specify `type` on every property
- Use `format` for: uuid, date, date-time, email, uri, double, int32, int64
- Use `minimum`/`maximum` for numeric ranges
- Use `minLength`/`maxLength` for strings
- Use `enum` for fixed value sets
- Use `nullable: true` for fields that can be null (not `type: [string, null]`)
- Use `readOnly: true` for server-generated fields (id, createdAt)
- Use `writeOnly: true` for fields only in requests (password, cvv)
- ALWAYS provide `description` on non-obvious properties
- ALWAYS provide `example` on every property
- `required` array MUST list all mandatory fields
- Separate Request and Response schemas — never reuse the same for both

---

## OA10: Security

```yaml
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
      description: "JWT access token (RS256, 15-min expiry)"

    oauth2:
      type: oauth2
      flows:
        authorizationCode:
          authorizationUrl: "https://auth.example.com/authorize"
          tokenUrl: "https://auth.example.com/token"
          scopes:
            read:applications: "Read own applications"
            write:applications: "Create and modify applications"
            read:loans: "Read own loans"
            admin:applications: "Manage all applications (agents)"

# Global security (applies to all endpoints unless overridden)
security:
  - bearerAuth: []
```

### Per-Operation Security Override
```yaml
paths:
  /products:
    get:
      security: []                    # Public — no auth required
      summary: "List products"

  /applications/{id}/accept:
    post:
      security:
        - bearerAuth: []
      x-sca-required: true            # Custom extension: SCA needed
      summary: "Accept loan offer"
```

**SECURITY RULES:**
- Global `security` applies Bearer JWT to all endpoints
- Public endpoints override with `security: []` (products listing, health)
- Use `x-sca-required: true` extension for operations needing Strong Customer Authentication
- Scopes define fine-grained permissions per operation
- Agent/admin endpoints use separate scopes (`admin:applications`)
- NEVER include API keys, secrets, or tokens in the spec examples

---

## OA11: Tags & Organization

```yaml
tags:
  - name: Products
    description: "Product catalog and configuration"
  - name: Applications
    description: "Loan application lifecycle"
  - name: Assessment
    description: "Decision engine and credit assessment"
  - name: Offers
    description: "Loan offer generation and acceptance"
  - name: Loans
    description: "Active loan management and servicing"
  - name: Payments
    description: "Payment collection and processing"
  - name: Cards
    description: "Debit card registration and management"
  - name: BackOffice
    description: "Agent-operated back office functions"
  - name: Health
    description: "Service health and readiness"
```

**TAG RULES:**
- Every operation MUST have at least one tag
- Tags group operations by business domain (not technical layer)
- Tag names: PascalCase, singular or plural matching the resource
- Tag descriptions: one sentence explaining the domain
- Order tags by typical user journey flow

---

## OA12: Extensions (x- properties)

Custom extensions for enterprise-specific metadata:

```yaml
paths:
  /applications/{id}/assess:
    post:
      x-sca-required: true           # Strong Customer Authentication needed
      x-data-sensitivity: Confidential # Data classification
      x-audit-required: true          # Must be audit logged
      x-rate-limit:                   # Endpoint-specific rate limit
        limit: 10
        window: 60
      x-changelog:                    # What changed (brownfield)
        - version: "1.1.0"
          date: "2026-04-20"
          change: "Added BridgeNow product type support"
      x-circuit-breaker:              # External dependency info
        dependency: "SIMAH"
        timeout: 30
        retries: 3
```

**EXTENSION RULES:**
- All extensions prefixed with `x-`
- `x-data-sensitivity`: REQUIRED on every operation (Public/Internal/Confidential/Restricted)
- `x-audit-required`: true for operations modifying sensitive data
- `x-sca-required`: true for financial transactions and sensitive data access
- `x-changelog`: REQUIRED on modified endpoints in brownfield updates
- Extensions are metadata — they don't affect API behaviour but inform tooling and governance

---

## OA13: Versioning & Backward Compatibility

### URL Path Versioning
```yaml
servers:
  - url: "https://api.example.com/api/v1"    # Version in URL path
```

### Versioning Rules
- Version in URL path: `/api/v1/`, `/api/v2/`
- Breaking changes REQUIRE new major version
- Non-breaking additions allowed in current version

### What Is a Breaking Change

| Change | Breaking? | Action |
|--------|-----------|--------|
| Remove endpoint | YES | New version |
| Remove response field | YES | New version |
| Change field type (string→number) | YES | New version |
| Rename field | YES | New version |
| Make optional field required | YES | New version |
| Add new endpoint | NO | Same version |
| Add optional request field | NO | Same version |
| Add response field | NO | Same version |
| Add new enum value | MAYBE | Same version if clients handle unknown values |
| Change description/example | NO | Same version |
| Add new error code | NO | Same version |

### Brownfield Update Rules
When updating an existing spec:
1. NEVER remove endpoints — deprecate with `deprecated: true`
2. NEVER remove response fields — add new ones alongside
3. NEVER change field types — add new field with new type
4. New request fields MUST be optional (no `required`)
5. New enum values: add to end of list, document in `x-changelog`
6. Deprecated endpoints: add `deprecated: true` + `x-sunset-date`

```yaml
paths:
  /legacy/endpoint:
    get:
      deprecated: true
      x-sunset-date: "2026-12-31"
      summary: "DEPRECATED — use /v2/endpoint instead"
```

---

## OA14: Pagination, Filtering, Sorting

### Standard Pagination Pattern
```yaml
paths:
  /loans:
    get:
      parameters:
        - name: pageNumber
          in: query
          schema: { type: integer, minimum: 1, default: 1 }
        - name: pageSize
          in: query
          schema: { type: integer, minimum: 1, maximum: 100, default: 20 }
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/Loan'
                  meta:
                    type: object
                    properties:
                      pageNumber: { type: integer }
                      pageSize: { type: integer }
                      totalCount: { type: integer }
                      totalPages: { type: integer }
```

### Filtering
```yaml
parameters:
  - name: status
    in: query
    schema:
      type: string
      enum: [Active, Settled, Closed]
  - name: createdAfter
    in: query
    schema:
      type: string
      format: date
  - name: createdBefore
    in: query
    schema:
      type: string
      format: date
  - name: minAmount
    in: query
    schema:
      type: number
  - name: maxAmount
    in: query
    schema:
      type: number
```

### Sorting
```yaml
parameters:
  - name: sortBy
    in: query
    schema:
      type: string
      enum: [createdAt, amount, status]
      default: createdAt
  - name: sortOrder
    in: query
    schema:
      type: string
      enum: [asc, desc]
      default: desc
```

**PAGINATION RULES:**
- ALL list endpoints MUST support pagination
- Max page size: 100 items
- Default page size: 20 items
- Page numbering: 1-based (not 0-based)
- Response MUST include `meta.totalCount` and `meta.totalPages`
- Empty results: return `{ "data": [], "meta": { "totalCount": 0 } }` with 200 (not 404)

---

## OA15: Health Endpoints

```yaml
paths:
  /health:
    get:
      operationId: healthLiveness
      summary: "Liveness probe"
      security: []
      tags: [Health]
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [Healthy, Unhealthy]

  /health/ready:
    get:
      operationId: healthReadiness
      summary: "Readiness probe"
      security: []
      tags: [Health]
      responses:
        '200':
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    enum: [Healthy, Unhealthy]
                  checks:
                    type: object
                    properties:
                      database: { type: string }
                      cache: { type: string }
                      messageBus: { type: string }
        '503':
          description: "Service not ready"
```

---

## OA16: Webhooks (Inbound)

```yaml
paths:
  /webhooks/{provider}:
    post:
      operationId: receiveWebhook
      summary: "Receive webhook from external provider"
      security: []                    # Authenticated via HMAC signature
      parameters:
        - name: provider
          in: path
          required: true
          schema:
            type: string
            enum: [payment-processor, open-banking]
        - name: X-Webhook-Signature
          in: header
          required: true
          description: "HMAC-SHA256 signature of request body"
          schema:
            type: string
      requestBody:
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/WebhookPayload'
      responses:
        '200':
          description: "Webhook received and queued for processing"
        '401':
          description: "Invalid signature"
```

---

## OA17: Quality Checklist

Before publishing or updating an OpenAPI spec, verify:

**Structure:**
- [ ] `openapi: "3.0.3"` specified
- [ ] `info` has title, version, description
- [ ] At least one server defined
- [ ] All paths use plural nouns (no verbs)
- [ ] No PII in paths or query parameters

**Operations:**
- [ ] Every operation has `operationId` (unique, camelCase)
- [ ] Every operation has `summary` and at least one `tag`
- [ ] Every operation has `security` (or inherits global)
- [ ] Every operation has success + error responses (400, 401, 500 minimum)
- [ ] All write operations accept `Idempotency-Key` header

**Schemas:**
- [ ] Every property has `type` and `description`
- [ ] Every property has `example`
- [ ] Numeric fields have `minimum`/`maximum`
- [ ] String fields have `minLength`/`maxLength` where appropriate
- [ ] Enums documented with all valid values
- [ ] `nullable: true` used (not `type: [string, null]`)
- [ ] Separate Request and Response schemas

**Responses:**
- [ ] Success responses wrapped in `{ "data": ... }` envelope
- [ ] List responses include `meta` with pagination
- [ ] Error responses use RFC 7807 ProblemDetails (NOT wrapped in data)
- [ ] 201 responses include `Location` header
- [ ] `X-Correlation-Id` in all response headers

**Backward Compatibility (brownfield):**
- [ ] No endpoints removed
- [ ] No response fields removed
- [ ] No field types changed
- [ ] New request fields are optional
- [ ] Modified endpoints have `x-changelog` extension
- [ ] Deprecated endpoints have `deprecated: true` + `x-sunset-date`

**Security:**
- [ ] No secrets, tokens, or real PII in examples
- [ ] `x-data-sensitivity` on every operation
- [ ] `x-sca-required` on financial transaction endpoints
- [ ] Public endpoints explicitly override security with `security: []`

**MANDATORY RULES:**
- Spec MUST parse without errors in any OpenAPI 3.0 validator
- Spec MUST be the single source of truth — code generated from it
- Spec MUST be version-controlled alongside the codebase
- Spec MUST be updated BEFORE implementation (API-first design)
- Breaking changes MUST go through API review board
