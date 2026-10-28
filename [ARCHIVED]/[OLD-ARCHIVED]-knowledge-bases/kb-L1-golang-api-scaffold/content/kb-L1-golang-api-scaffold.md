# Go API Scaffold — Knowledge Base
### kb-L1-golang-api-scaffold v1.0.0
### Provides the starter template for new Go API services. Code generator agents MUST use this scaffold as the base.

---

## SCAFFOLD1: Makefile

```makefile
.PHONY: run build test lint migrate swagger

run:
	go run cmd/server/main.go

build:
	CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/server cmd/server/main.go

test:
	go test ./... -race -cover -coverprofile=coverage.out

lint:
	golangci-lint run ./...

migrate-up:
	migrate -path migrations -database "$(DATABASE_URL)" up

migrate-down:
	migrate -path migrations -database "$(DATABASE_URL)" down 1

swagger:
	swag init -g cmd/server/main.go -o docs
```

---

## SCAFFOLD2: Dockerfile

```dockerfile
# Build stage
FROM golang:1.22-alpine AS builder
WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download
COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /server cmd/server/main.go

# Run stage
FROM gcr.io/distroless/static:nonroot
COPY --from=builder /server /server
COPY migrations /migrations
USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/server"]
```

---

## SCAFFOLD3: Main Entry Point

```go
// cmd/server/main.go
package main

import (
    "context"
    "log/slog"
    "net/http"
    "os"
    "os/signal"
    "syscall"
    "time"

    "github.com/go-chi/chi/v5"
    chiMiddleware "github.com/go-chi/chi/v5/middleware"
    "github.com/jmoiron/sqlx"
    _ "github.com/lib/pq"

    "{{module}}/internal/config"
    "{{module}}/internal/handler"
    "{{module}}/internal/repository"
    "{{module}}/internal/service"
)

func main() {
    logger := slog.New(slog.NewJSONHandler(os.Stdout, &slog.HandlerOptions{Level: slog.LevelInfo}))
    slog.SetDefault(logger)

    cfg, err := config.Load()
    if err != nil {
        logger.Error("failed to load config", "error", err)
        os.Exit(1)
    }

    db, err := sqlx.Connect("postgres", cfg.Database.URL)
    if err != nil {
        logger.Error("failed to connect to database", "error", err)
        os.Exit(1)
    }
    defer db.Close()
    db.SetMaxOpenConns(cfg.Database.MaxOpenConns)
    db.SetMaxIdleConns(cfg.Database.MaxIdleConns)
    db.SetConnMaxLifetime(cfg.Database.ConnMaxLifetime)

    // Wire dependencies
    repo := repository.NewUserPostgresRepo(db)
    svc := service.NewUserService(repo, logger)
    h := handler.NewUserHandler(svc, logger)

    // Router
    r := chi.NewRouter()
    r.Use(chiMiddleware.Recoverer)
    r.Use(chiMiddleware.RequestID)
    r.Use(handler.LoggerMiddleware(logger))
    r.Use(chiMiddleware.RealIP)

    // Routes
    r.Route("/api/v1", func(r chi.Router) {
        r.Route("/users", func(r chi.Router) {
            r.Post("/", h.Create)
            r.Get("/", h.List)
            r.Get("/{id}", h.GetByID)
            r.Put("/{id}", h.Update)
            r.Delete("/{id}", h.Delete)
        })
    })
    r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
        w.WriteHeader(http.StatusOK)
    })

    // Server
    srv := &http.Server{
        Addr:         ":" + cfg.Server.Port,
        Handler:      r,
        ReadTimeout:  cfg.Server.ReadTimeout,
        WriteTimeout: cfg.Server.WriteTimeout,
    }

    // Graceful shutdown
    go func() {
        logger.Info("server starting", "port", cfg.Server.Port)
        if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
            logger.Error("server error", "error", err)
            os.Exit(1)
        }
    }()

    quit := make(chan os.Signal, 1)
    signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
    <-quit

    ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
    defer cancel()
    if err := srv.Shutdown(ctx); err != nil {
        logger.Error("forced shutdown", "error", err)
    }
    logger.Info("server stopped")
}
```

---

## SCAFFOLD4: Configuration

```go
// internal/config/config.go
package config

import (
    "time"
    "github.com/kelseyhightower/envconfig"
)

type Config struct {
    Server   ServerConfig
    Database DatabaseConfig
}

type ServerConfig struct {
    Port         string        `envconfig:"SERVER_PORT" default:"8080"`
    ReadTimeout  time.Duration `envconfig:"SERVER_READ_TIMEOUT" default:"10s"`
    WriteTimeout time.Duration `envconfig:"SERVER_WRITE_TIMEOUT" default:"30s"`
}

type DatabaseConfig struct {
    URL             string        `envconfig:"DATABASE_URL" required:"true"`
    MaxOpenConns    int           `envconfig:"DB_MAX_OPEN_CONNS" default:"25"`
    MaxIdleConns    int           `envconfig:"DB_MAX_IDLE_CONNS" default:"5"`
    ConnMaxLifetime time.Duration `envconfig:"DB_CONN_MAX_LIFETIME" default:"5m"`
}

func Load() (*Config, error) {
    var cfg Config
    if err := envconfig.Process("", &cfg); err != nil {
        return nil, err
    }
    return &cfg, nil
}
```

---

## SCAFFOLD5: HTTP Error Helper

```go
// pkg/httperr/errors.go
package httperr

import (
    "encoding/json"
    "net/http"
)

type ErrorResponse struct {
    Error APIError `json:"error"`
}

type APIError struct {
    Code    string `json:"code"`
    Message string `json:"message"`
    Details any    `json:"details,omitempty"`
}

func JSON(w http.ResponseWriter, status int, v any) {
    w.Header().Set("Content-Type", "application/json")
    w.WriteHeader(status)
    json.NewEncoder(w).Encode(v)
}

func BadRequest(w http.ResponseWriter, msg string) {
    JSON(w, http.StatusBadRequest, ErrorResponse{Error: APIError{Code: "BAD_REQUEST", Message: msg}})
}

func NotFound(w http.ResponseWriter, msg string) {
    JSON(w, http.StatusNotFound, ErrorResponse{Error: APIError{Code: "NOT_FOUND", Message: msg}})
}

func InternalError(w http.ResponseWriter) {
    JSON(w, http.StatusInternalServerError, ErrorResponse{Error: APIError{Code: "INTERNAL_ERROR", Message: "internal server error"}})
}
```

---

## SCAFFOLD6: Go Module Init

```
go mod init {{module}}
go mod tidy
```

**Dependencies to include:**
```
github.com/go-chi/chi/v5
github.com/jmoiron/sqlx
github.com/lib/pq
github.com/google/uuid
github.com/go-playground/validator/v10
github.com/kelseyhightower/envconfig
github.com/stretchr/testify
go.uber.org/mock
```

---

## SCAFFOLD7: Linter Configuration

```yaml
# .golangci.yml
linters:
  enable:
    - errcheck
    - govet
    - staticcheck
    - gosimple
    - ineffassign
    - unused
    - misspell
    - gofmt
    - goimports
    - revive
    - gosec
    - bodyclose
    - contextcheck

linters-settings:
  revive:
    rules:
      - name: exported
        arguments: [checkPrivateReceivers]
      - name: unused-parameter

run:
  timeout: 5m
```

---

## SCAFFOLD8: Migration Template

```sql
-- migrations/001_initial.up.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_email ON users(email);
```

```sql
-- migrations/001_initial.down.sql
DROP TABLE IF EXISTS users;
```
