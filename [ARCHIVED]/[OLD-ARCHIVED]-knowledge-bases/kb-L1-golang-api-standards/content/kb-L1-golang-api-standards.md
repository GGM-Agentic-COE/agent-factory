# Go API Development Standards — Knowledge Base
### kb-L1-golang-api-standards v1.0.0
### Code generator agents MUST follow these standards when generating Go-based API code.

---

## GO1: Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | Go | 1.22+ | Latest stable, modules enabled |
| Web Framework | net/http (stdlib) | — | Standard library preferred; chi router for routing |
| Router | chi | v5 | Lightweight, stdlib-compatible, middleware support |
| Validation | go-playground/validator | v10 | Struct tag-based validation |
| ORM / DB | sqlx | v1.3 | Not a full ORM — thin layer over database/sql |
| Migrations | golang-migrate | v4 | File-based SQL migrations |
| Logging | slog (stdlib) | — | Structured logging (Go 1.21+), JSON handler for production |
| Tracing | OpenTelemetry | v1.24 | Distributed tracing with context propagation |
| Metrics | OpenTelemetry / Prometheus | — | RED metrics (Rate, Errors, Duration) per endpoint |
| Monitoring | Datadog / Grafana | — | Dashboard and alerting (platform-dependent) |
| Configuration | envconfig / viper | — | Environment-based config with struct binding |
| Testing | testing (stdlib) + testify | — | Table-driven tests, testify for assertions |
| Mocking | mockgen (gomock) | v0.4 | Interface-based mocks, auto-generated |
| API Docs | swaggo/swag | v2 | OpenAPI from annotations |
| Dependency Injection | Manual / wire | — | Constructor injection, no magic DI containers |
| HTTP Client | net/http | — | stdlib with custom transport for retries/timeouts |
| Database | PostgreSQL | 16 | Primary relational store |
| Cache | Redis | 7+ | Via go-redis/redis |
| Message Queue | Google Cloud Pub/Sub | — | Async event processing |
| Containerisation | Docker | — | Multi-stage builds, distroless base |
| CI/CD | GitHub Actions / Bitbucket Pipelines | — | Lint → test → build → deploy |

---

## GO2: Project Structure

```
{service-name}/
├── cmd/
│   └── server/
│       └── main.go                  # Entry point — wires dependencies, starts server
├── internal/
│   ├── config/
│   │   └── config.go               # Env-based configuration struct
│   ├── domain/
│   │   ├── {entity}.go             # Domain entities (plain structs)
│   │   ├── {entity}_repository.go  # Repository interface
│   │   └── errors.go               # Domain-specific errors
│   ├── handler/
│   │   ├── {resource}_handler.go   # HTTP handlers (one file per resource)
│   │   └── middleware.go           # Middleware (auth, logging, recovery, cors)
│   ├── service/
│   │   └── {entity}_service.go     # Business logic (implements use cases)
│   ├── repository/
│   │   └── {entity}_postgres.go    # PostgreSQL repository implementation
│   └── dto/
│       ├── request.go              # Request DTOs with validation tags
│       └── response.go             # Response DTOs
├── pkg/
│   ├── httperr/
│   │   └── errors.go              # Standardised HTTP error responses
│   └── pagination/
│       └── pagination.go          # Pagination helpers
├── migrations/
│   ├── 001_initial.up.sql
│   └── 001_initial.down.sql
├── docs/
│   └── swagger.json               # Generated OpenAPI spec
├── go.mod
├── go.sum
├── Makefile
├── Dockerfile
└── .golangci.yml                   # Linter configuration
```

**MANDATORY:** Use `internal/` for non-exportable packages. Use `cmd/` for entry points. Never put business logic in handlers.

---

## GO3: Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Package names | Short, lowercase, no underscores | `handler`, `service`, `repository` |
| File names | Snake_case | `user_handler.go`, `order_service.go` |
| Exported types | PascalCase | `UserService`, `OrderRepository` |
| Unexported | camelCase | `validateInput`, `buildQuery` |
| Interfaces | `-er` suffix or descriptive | `Reader`, `UserRepository`, `OrderCreator` |
| Constructors | `New{Type}` | `NewUserService(repo UserRepository)` |
| Errors | `Err{Description}` | `ErrUserNotFound`, `ErrInvalidInput` |
| Constants | PascalCase (exported), camelCase (unexported) | `MaxRetries`, `defaultTimeout` |
| Test files | `{file}_test.go` | `user_handler_test.go` |
| Mock files | `mock_{interface}.go` | `mock_user_repository.go` |

---

## GO4: Handler Pattern

```go
// handler/user_handler.go
type UserHandler struct {
    service domain.UserService
    logger  *slog.Logger
}

func NewUserHandler(s domain.UserService, l *slog.Logger) *UserHandler {
    return &UserHandler{service: s, logger: l}
}

func (h *UserHandler) Create(w http.ResponseWriter, r *http.Request) {
    var req dto.CreateUserRequest
    if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
        httperr.BadRequest(w, "invalid request body")
        return
    }
    if err := validator.Validate(req); err != nil {
        httperr.ValidationError(w, err)
        return
    }
    user, err := h.service.Create(r.Context(), req)
    if err != nil {
        httperr.Handle(w, err)
        return
    }
    httputil.JSON(w, http.StatusCreated, dto.UserResponse{}.FromDomain(user))
}
```

**Rules:**
- Handlers ONLY decode request, validate, call service, encode response
- No business logic in handlers
- Always pass `context.Context` from request
- Use structured error responses (see GO7)

---

## GO5: Service Pattern

```go
// service/user_service.go
type userService struct {
    repo   domain.UserRepository
    cache  cache.Cache
    logger *slog.Logger
}

func NewUserService(repo domain.UserRepository, cache cache.Cache, l *slog.Logger) domain.UserService {
    return &userService{repo: repo, cache: cache, logger: l}
}

func (s *userService) Create(ctx context.Context, req dto.CreateUserRequest) (*domain.User, error) {
    existing, _ := s.repo.GetByEmail(ctx, req.Email)
    if existing != nil {
        return nil, domain.ErrUserAlreadyExists
    }
    user := &domain.User{
        ID:    uuid.New(),
        Email: req.Email,
        Name:  req.Name,
    }
    if err := s.repo.Create(ctx, user); err != nil {
        return nil, fmt.Errorf("create user: %w", err)
    }
    return user, nil
}
```

**Rules:**
- Services contain all business logic
- Accept and return domain types (not HTTP types)
- Wrap errors with context: `fmt.Errorf("operation: %w", err)`
- Use dependency injection via constructor

---

## GO6: Repository Pattern

```go
// domain/user_repository.go (interface)
type UserRepository interface {
    Create(ctx context.Context, user *User) error
    GetByID(ctx context.Context, id uuid.UUID) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    List(ctx context.Context, filter ListFilter) ([]*User, int, error)
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id uuid.UUID) error
}

// repository/user_postgres.go (implementation)
type userPostgresRepo struct {
    db *sqlx.DB
}

func NewUserPostgresRepo(db *sqlx.DB) domain.UserRepository {
    return &userPostgresRepo{db: db}
}

func (r *userPostgresRepo) GetByID(ctx context.Context, id uuid.UUID) (*domain.User, error) {
    var user domain.User
    err := r.db.GetContext(ctx, &user, "SELECT * FROM users WHERE id = $1", id)
    if errors.Is(err, sql.ErrNoRows) {
        return nil, domain.ErrUserNotFound
    }
    return &user, err
}
```

**Rules:**
- Interface defined in domain package
- Implementation in repository package
- Always accept `context.Context` as first parameter
- Use parameterised queries (never string concatenation)
- Map `sql.ErrNoRows` to domain errors

---

## GO7: Error Handling

```go
// pkg/httperr/errors.go
type APIError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details any    `json:"details,omitempty"`
}

func Handle(w http.ResponseWriter, err error) {
    switch {
    case errors.Is(err, domain.ErrNotFound):
        JSON(w, http.StatusNotFound, APIError{Code: "NOT_FOUND", Message: err.Error()})
    case errors.Is(err, domain.ErrAlreadyExists):
        JSON(w, http.StatusConflict, APIError{Code: "CONFLICT", Message: err.Error()})
    case errors.Is(err, domain.ErrInvalidInput):
        JSON(w, http.StatusBadRequest, APIError{Code: "BAD_REQUEST", Message: err.Error()})
    default:
        slog.Error("unhandled error", "error", err)
        JSON(w, http.StatusInternalServerError, APIError{Code: "INTERNAL_ERROR", Message: "internal server error"})
    }
}
```

**Rules:**
- Use sentinel errors in domain: `var ErrUserNotFound = errors.New("user not found")`
- Wrap errors with context at every level: `fmt.Errorf("get user: %w", err)`
- Never expose internal error details to clients
- Log unhandled errors with full context
- Use `errors.Is()` and `errors.As()` for error checking

---

## GO8: Middleware

```go
func RequestID(next http.Handler) http.Handler {
    return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
        id := r.Header.Get("X-Request-ID")
        if id == "" {
            id = uuid.New().String()
        }
        ctx := context.WithValue(r.Context(), requestIDKey, id)
        w.Header().Set("X-Request-ID", id)
        next.ServeHTTP(w, r.WithContext(ctx))
    })
}

func Logger(logger *slog.Logger) func(next http.Handler) http.Handler {
    return func(next http.Handler) http.Handler {
        return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
            start := time.Now()
            ww := middleware.NewWrapResponseWriter(w, r.ProtoMajor)
            next.ServeHTTP(ww, r)
            logger.Info("request",
                "method", r.Method,
                "path", r.URL.Path,
                "status", ww.Status(),
                "duration_ms", time.Since(start).Milliseconds(),
                "request_id", r.Context().Value(requestIDKey),
            )
        })
    }
}
```

**Standard middleware chain:** Recovery → RequestID → Logger → CORS → Auth → Handler

---

## GO8b: Observability

```go
// OpenTelemetry setup in main.go
import "go.opentelemetry.io/otel"

// Trace a service call
func (s *userService) Create(ctx context.Context, req dto.CreateUserRequest) (*domain.User, error) {
    ctx, span := otel.Tracer("user-service").Start(ctx, "UserService.Create")
    defer span.End()
    // ... business logic
}
```

**Rules:**
- Every service method must create a span
- Propagate context through all layers (handler → service → repository)
- Record errors on spans: `span.RecordError(err); span.SetStatus(codes.Error, err.Error())`
- Export traces via OTLP (gRPC) to collector
- Track RED metrics per endpoint: request Rate, Error rate, Duration (p50/p95/p99)
- Use slog for application logs, OpenTelemetry for traces/metrics — don't duplicate

---

## GO9: Testing Standards

```go
// Table-driven test pattern
func TestUserService_Create(t *testing.T) {
    tests := []struct {
        name    string
        req     dto.CreateUserRequest
        setup   func(repo *mock.MockUserRepository)
        wantErr error
    }{
        {
            name: "success",
            req:  dto.CreateUserRequest{Email: "test@example.com", Name: "Test"},
            setup: func(repo *mock.MockUserRepository) {
                repo.EXPECT().GetByEmail(gomock.Any(), "test@example.com").Return(nil, nil)
                repo.EXPECT().Create(gomock.Any(), gomock.Any()).Return(nil)
            },
            wantErr: nil,
        },
        {
            name: "duplicate email",
            req:  dto.CreateUserRequest{Email: "exists@example.com", Name: "Test"},
            setup: func(repo *mock.MockUserRepository) {
                repo.EXPECT().GetByEmail(gomock.Any(), "exists@example.com").Return(&domain.User{}, nil)
            },
            wantErr: domain.ErrUserAlreadyExists,
        },
    }
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            ctrl := gomock.NewController(t)
            repo := mock.NewMockUserRepository(ctrl)
            tt.setup(repo)
            svc := service.NewUserService(repo, nil, slog.Default())
            _, err := svc.Create(context.Background(), tt.req)
            assert.ErrorIs(t, err, tt.wantErr)
        })
    }
}
```

**Rules:**
- Table-driven tests for all service methods
- Use gomock for interface mocking
- Test files in same package (`_test.go` suffix)
- Integration tests use testcontainers for real DB
- Target ≥80% coverage on service layer

---

## GO10: Configuration & Environment

```go
// internal/config/config.go
type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
    Redis    RedisConfig
}

type ServerConfig struct {
    Port         int           `envconfig:"SERVER_PORT" default:"8080"`
    ReadTimeout  time.Duration `envconfig:"SERVER_READ_TIMEOUT" default:"10s"`
    WriteTimeout time.Duration `envconfig:"SERVER_WRITE_TIMEOUT" default:"30s"`
}

type DatabaseConfig struct {
    URL             string        `envconfig:"DATABASE_URL" required:"true"`
    MaxOpenConns    int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
    MaxIdleConns    int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
    ConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`
}
```

**Rules:**
- All config from environment variables (12-factor)
- Struct tags for binding and defaults
- Secrets via secret manager (never in env files committed to repo)
- Separate configs for server, database, cache, external services

---

## GO11: API Response Standards

```go
// Success response
{"data": {...}, "meta": {"request_id": "...", "timestamp": "..."}}

// List response
{"data": [...], "meta": {"total": 100, "page": 1, "per_page": 20, "request_id": "..."}}

// Error response
{"error": {"code": "NOT_FOUND", "message": "user not found", "details": null}}
```

**Rules:**
- All responses wrapped in `data` (success) or `error` (failure)
- Include `meta` with request_id and timestamp
- List endpoints include pagination meta
- Use consistent HTTP status codes: 200 (OK), 201 (Created), 204 (No Content), 400, 401, 403, 404, 409, 422, 500

---

## GO12: Security Standards

- Input validation on every handler (use validator struct tags)
- Parameterised SQL queries only (no string interpolation)
- Rate limiting via middleware (token bucket)
- CORS configured explicitly (no wildcard in production)
- Authentication via JWT/OAuth2 middleware
- Secrets in environment or secret manager (never hardcoded)
- TLS termination at load balancer
- Request body size limits (`http.MaxBytesReader`)
- Timeout on all external HTTP calls (`http.Client{Timeout: 10*time.Second}`)
