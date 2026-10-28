# C# / .NET 8 API Project Scaffold — Knowledge Base
### kb-L1-csharp-dotnet-scaffold v1.0.0
### Production-ready scaffold for greenfield .NET 8 microservice APIs. Compliant with kb-L1-csharp-dotnet-standards, kb-L1-microservices-architecture, and kb-L1-enterprise-architecture.

---

## SC1: Scaffold Overview

This scaffold produces a fully runnable .NET 8 microservice with:
- Clean Architecture (4 layers)
- CQRS via MediatR
- Health checks (liveness + readiness)
- Structured logging (Serilog) with correlation ID
- OpenTelemetry tracing + metrics
- JWT authentication
- RFC 7807 error handling
- EF Core with migrations
- Docker + Kubernetes manifests
- GitHub Actions CI pipeline (lint → build → test → SAST → SCA → image)

---

## SC2: File Tree

```
{ServiceName}/
├── .github/
│   └── workflows/
│       └── ci.yml                          # CI pipeline
├── src/
│   ├── {ServiceName}.Domain/
│   │   ├── Entities/
│   │   │   └── .gitkeep
│   │   ├── Enums/
│   │   │   └── .gitkeep
│   │   ├── Interfaces/
│   │   │   └── .gitkeep
│   │   └── {ServiceName}.Domain.csproj
│   ├── {ServiceName}.Application/
│   │   ├── Common/
│   │   │   └── Behaviours/
│   │   │       ├── ValidationBehaviour.cs
│   │   │       ├── LoggingBehaviour.cs
│   │   │       └── PerformanceBehaviour.cs
│   │   ├── DTOs/
│   │   │   └── .gitkeep
│   │   └── {ServiceName}.Application.csproj
│   ├── {ServiceName}.Infrastructure/
│   │   ├── Persistence/
│   │   │   ├── AppDbContext.cs
│   │   │   ├── Configurations/
│   │   │   └── Repositories/
│   │   ├── Services/
│   │   │   └── .gitkeep
│   │   ├── Seed/
│   │   │   └── DataSeeder.cs
│   │   └── {ServiceName}.Infrastructure.csproj
│   └── {ServiceName}.Api/
│       ├── Controllers/
│       │   └── HealthController.cs
│       ├── Middleware/
│       │   ├── ExceptionMiddleware.cs
│       │   ├── CorrelationIdMiddleware.cs
│       │   └── RequestLoggingMiddleware.cs
│       ├── Properties/
│       │   └── launchSettings.json
│       ├── Program.cs
│       ├── appsettings.json
│       ├── appsettings.Development.json
│       └── {ServiceName}.Api.csproj
├── tests/
│   ├── {ServiceName}.UnitTests/
│   │   └── {ServiceName}.UnitTests.csproj
│   ├── {ServiceName}.IntegrationTests/
│   │   └── {ServiceName}.IntegrationTests.csproj
│   └── {ServiceName}.ContractTests/
│       └── {ServiceName}.ContractTests.csproj
├── {ServiceName}.sln
├── global.json
├── .editorconfig
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── hpa.yaml
└── README.md
```

---

## SC3: Project Files (.csproj)

### Domain (zero dependencies)
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <TreatWarningsAsErrors>true</TreatWarningsAsErrors>
  </PropertyGroup>
</Project>
```

### Application
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\{ServiceName}.Domain\{ServiceName}.Domain.csproj" />
    <PackageReference Include="MediatR" Version="12.4.1" />
    <PackageReference Include="FluentValidation" Version="11.10.0" />
    <PackageReference Include="FluentValidation.DependencyInjectionExtensions" Version="11.10.0" />
  </ItemGroup>
</Project>
```

### Infrastructure
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\{ServiceName}.Domain\{ServiceName}.Domain.csproj" />
    <ProjectReference Include="..\{ServiceName}.Application\{ServiceName}.Application.csproj" />
    <PackageReference Include="Microsoft.EntityFrameworkCore" Version="8.0.10" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.SqlServer" Version="8.0.10" />
    <PackageReference Include="Microsoft.EntityFrameworkCore.InMemory" Version="8.0.10" />
    <PackageReference Include="Microsoft.Extensions.Http.Polly" Version="8.0.10" />
    <PackageReference Include="Polly" Version="8.4.2" />
  </ItemGroup>
</Project>
```

### Api
```xml
<Project Sdk="Microsoft.NET.Sdk.Web">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <LangVersion>12</LangVersion>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
    <DockerDefaultTargetOS>Linux</DockerDefaultTargetOS>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\{ServiceName}.Application\{ServiceName}.Application.csproj" />
    <ProjectReference Include="..\{ServiceName}.Infrastructure\{ServiceName}.Infrastructure.csproj" />
    <PackageReference Include="Serilog.AspNetCore" Version="8.0.2" />
    <PackageReference Include="Serilog.Sinks.Console" Version="6.0.0" />
    <PackageReference Include="Serilog.Enrichers.Environment" Version="3.0.1" />
    <PackageReference Include="Swashbuckle.AspNetCore" Version="6.8.1" />
    <PackageReference Include="Microsoft.AspNetCore.Authentication.JwtBearer" Version="8.0.10" />
    <PackageReference Include="OpenTelemetry.Extensions.Hosting" Version="1.9.0" />
    <PackageReference Include="OpenTelemetry.Instrumentation.AspNetCore" Version="1.9.0" />
    <PackageReference Include="OpenTelemetry.Instrumentation.Http" Version="1.9.0" />
    <PackageReference Include="OpenTelemetry.Instrumentation.EntityFrameworkCore" Version="1.0.0-beta.12" />
    <PackageReference Include="OpenTelemetry.Exporter.OpenTelemetryProtocol" Version="1.9.0" />
    <PackageReference Include="AspNetCore.HealthChecks.SqlServer" Version="8.0.2" />
    <PackageReference Include="AspNetCore.HealthChecks.Redis" Version="8.0.1" />
  </ItemGroup>
</Project>
```

---

## SC4: Program.cs (Full Scaffold)

```csharp
using System.Text.Json.Serialization;
using FluentValidation;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Diagnostics.HealthChecks;
using Microsoft.EntityFrameworkCore;
using Microsoft.IdentityModel.Tokens;
using OpenTelemetry.Metrics;
using OpenTelemetry.Resources;
using OpenTelemetry.Trace;
using Serilog;
using {ServiceName}.Api.Middleware;
using {ServiceName}.Application.Common.Behaviours;
using {ServiceName}.Infrastructure.Persistence;

var builder = WebApplication.CreateBuilder(args);
var config = builder.Configuration;
var serviceName = "{ServiceName}";

// ── Logging (Serilog) ──────────────────────────────────────
Log.Logger = new LoggerConfiguration()
    .ReadFrom.Configuration(config)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithProperty("Service", serviceName)
    .WriteTo.Console(outputTemplate: "[{Timestamp:HH:mm:ss} {Level:u3}] {CorrelationId} {Message:lj}{NewLine}{Exception}")
    .CreateLogger();
builder.Host.UseSerilog();

// ── OpenTelemetry (Tracing + Metrics) ──────────────────────
builder.Services.AddOpenTelemetry()
    .ConfigureResource(r => r.AddService(serviceName))
    .WithTracing(t => t
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddEntityFrameworkCoreInstrumentation()
        .AddOtlpExporter(o => o.Endpoint = new Uri(config["Otlp:Endpoint"] ?? "http://localhost:4317")))
    .WithMetrics(m => m
        .AddAspNetCoreInstrumentation()
        .AddHttpClientInstrumentation()
        .AddOtlpExporter());

// ── Database ───────────────────────────────────────────────
var connString = config.GetConnectionString("DefaultConnection");
if (string.IsNullOrEmpty(connString))
    builder.Services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase($"{serviceName}Db"));
else
    builder.Services.AddDbContext<AppDbContext>(o => o.UseSqlServer(connString));

// ── MediatR + Behaviours ───────────────────────────────────
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssemblyContaining<AppDbContext>());
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehaviour<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(LoggingBehaviour<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(PerformanceBehaviour<,>));
builder.Services.AddValidatorsFromAssemblyContaining<AppDbContext>();

// ── Authentication (JWT) ───────────────────────────────────
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(o => {
        o.Authority = config["Auth:Authority"];
        o.TokenValidationParameters = new TokenValidationParameters {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidAudience = config["Auth:Audience"],
            ValidateLifetime = true,
        };
    });
builder.Services.AddAuthorization();

// ── Health Checks ──────────────────────────────────────────
var hcBuilder = builder.Services.AddHealthChecks();
if (!string.IsNullOrEmpty(connString))
    hcBuilder.AddSqlServer(connString, name: "database");

// ── Repositories + Services (register here) ────────────────
// builder.Services.AddScoped<IMyRepository, MyRepository>();

// ── Controllers + JSON ─────────────────────────────────────
builder.Services.AddControllers().AddJsonOptions(o => {
    o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    o.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
    o.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
});
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c => {
    c.SwaggerDoc("v1", new() { Title = serviceName, Version = "v1" });
    c.AddSecurityDefinition("Bearer", new() { Type = SecuritySchemeType.Http, Scheme = "bearer", BearerFormat = "JWT" });
});

// ── Build ──────────────────────────────────────────────────
var app = builder.Build();

// ── Seed (dev only) ────────────────────────────────────────
if (app.Environment.IsDevelopment())
{
    using var scope = app.Services.CreateScope();
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
}

// ── Middleware Pipeline ────────────────────────────────────
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<RequestLoggingMiddleware>();
app.UseMiddleware<ExceptionMiddleware>();

app.UseAuthentication();
app.UseAuthorization();

app.UseSwagger();
app.UseSwaggerUI();

app.MapHealthChecks("/health", new HealthCheckOptions { Predicate = _ => false }); // liveness
app.MapHealthChecks("/health/ready", new HealthCheckOptions { Predicate = _ => true }); // readiness
app.MapControllers();

Log.Information("{Service} starting on {Urls}", serviceName, app.Urls);
app.Run();

public partial class Program { } // For WebApplicationFactory in tests
```

---

## SC5: Middleware (Scaffold)

### RequestLoggingMiddleware
```csharp
namespace {ServiceName}.Api.Middleware;

public class RequestLoggingMiddleware(RequestDelegate next, ILogger<RequestLoggingMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        try
        {
            await next(context);
            sw.Stop();
            logger.LogInformation("HTTP {Method} {Path} responded {StatusCode} in {Elapsed}ms",
                context.Request.Method, context.Request.Path, context.Response.StatusCode, sw.ElapsedMilliseconds);
        }
        catch (Exception)
        {
            sw.Stop();
            logger.LogWarning("HTTP {Method} {Path} failed after {Elapsed}ms",
                context.Request.Method, context.Request.Path, sw.ElapsedMilliseconds);
            throw;
        }
    }
}
```

### PerformanceBehaviour (MediatR)
```csharp
namespace {ServiceName}.Application.Common.Behaviours;

public class PerformanceBehaviour<TRequest, TResponse>(ILogger<PerformanceBehaviour<TRequest, TResponse>> logger)
    : IPipelineBehavior<TRequest, TResponse> where TRequest : notnull
{
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        var sw = System.Diagnostics.Stopwatch.StartNew();
        var response = await next();
        sw.Stop();
        if (sw.ElapsedMilliseconds > 500)
            logger.LogWarning("Long running handler {Handler} took {Elapsed}ms", typeof(TRequest).Name, sw.ElapsedMilliseconds);
        return response;
    }
}
```

---

## SC6: Health Controller

```csharp
namespace {ServiceName}.Api.Controllers;

[ApiController]
public class HealthController : ControllerBase
{
    [HttpGet("/health")]
    public IActionResult Liveness() => Ok(new { status = "Healthy", service = "{ServiceName}" });

    [HttpGet("/health/ready")]
    public IActionResult Readiness([FromServices] HealthCheckService hc)
        => Ok(new { status = "Healthy" }); // Actual checks via MapHealthChecks
}
```

---

## SC7: Configuration Files

### appsettings.json
```json
{
  "ConnectionStrings": {
    "DefaultConnection": ""
  },
  "Auth": {
    "Authority": "https://auth.example.com",
    "Audience": "{ServiceName}"
  },
  "Otlp": {
    "Endpoint": "http://localhost:4317"
  },
  "Serilog": {
    "MinimumLevel": { "Default": "Information", "Override": { "Microsoft": "Warning", "System": "Warning" } }
  }
}
```

### appsettings.Development.json
```json
{
  "Serilog": { "MinimumLevel": { "Default": "Debug" } }
}
```

### .editorconfig
```ini
root = true
[*.cs]
indent_style = space
indent_size = 4
charset = utf-8
end_of_line = lf
insert_final_newline = true
dotnet_sort_system_directives_first = true
csharp_style_namespace_declarations = file_scoped:warning
csharp_style_var_for_built_in_types = true:suggestion
```

### global.json
```json
{ "sdk": { "version": "8.0.100", "rollForward": "latestMinor" } }
```

---

## SC8: Dockerfile

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0-alpine AS build
WORKDIR /src
COPY *.sln .
COPY src/{ServiceName}.Domain/*.csproj src/{ServiceName}.Domain/
COPY src/{ServiceName}.Application/*.csproj src/{ServiceName}.Application/
COPY src/{ServiceName}.Infrastructure/*.csproj src/{ServiceName}.Infrastructure/
COPY src/{ServiceName}.Api/*.csproj src/{ServiceName}.Api/
RUN dotnet restore
COPY . .
RUN dotnet publish src/{ServiceName}.Api -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:8.0-alpine AS runtime
RUN adduser -D appuser
WORKDIR /app
COPY --from=build /app .
USER appuser
EXPOSE 8080
ENV ASPNETCORE_URLS=http://+:8080
HEALTHCHECK --interval=10s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1
ENTRYPOINT ["dotnet", "{ServiceName}.Api.dll"]
```

**Per MS10/EA6:** Alpine base, non-root user, health check, < 200MB.

---

## SC9: Kubernetes Manifests

### deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {service-name}
  labels: { app: {service-name} }
spec:
  replicas: 2
  selector:
    matchLabels: { app: {service-name} }
  strategy:
    type: RollingUpdate
    rollingUpdate: { maxSurge: 1, maxUnavailable: 0 }
  template:
    metadata:
      labels: { app: {service-name} }
    spec:
      containers:
        - name: {service-name}
          image: {registry}/{service-name}:latest
          ports: [{ containerPort: 8080 }]
          envFrom: [{ configMapRef: { name: {service-name}-config } }]
          resources:
            requests: { cpu: 250m, memory: 256Mi }
            limits: { cpu: 500m, memory: 512Mi }
          livenessProbe:
            httpGet: { path: /health, port: 8080 }
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet: { path: /health/ready, port: 8080 }
            initialDelaySeconds: 5
            periodSeconds: 5
```

### hpa.yaml
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: {service-name}
spec:
  scaleTargetRef: { apiVersion: apps/v1, kind: Deployment, name: {service-name} }
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource: { name: cpu, target: { type: Utilization, averageUtilization: 70 } }
```

---

## SC10: GitHub Actions CI Pipeline

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push: { branches: [main] }
  pull_request: { branches: [main] }

env:
  DOTNET_VERSION: '8.0.x'
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with: { dotnet-version: '${{ env.DOTNET_VERSION }}' }

      # ── Restore ──────────────────────────────────────────
      - name: Restore
        run: dotnet restore

      # ── Lint (format check) ──────────────────────────────
      - name: Lint
        run: dotnet format --verify-no-changes --verbosity diagnostic

      # ── Build ────────────────────────────────────────────
      - name: Build
        run: dotnet build --no-restore --configuration Release -warnaserror

      # ── Unit Tests ───────────────────────────────────────
      - name: Unit Tests
        run: dotnet test tests/{ServiceName}.UnitTests --no-build -c Release --logger "trx" --collect:"XPlat Code Coverage"

      # ── Integration Tests ────────────────────────────────
      - name: Integration Tests
        run: dotnet test tests/{ServiceName}.IntegrationTests --no-build -c Release --logger "trx"

      # ── Contract Tests ───────────────────────────────────
      - name: Contract Tests
        run: dotnet test tests/{ServiceName}.ContractTests --no-build -c Release --logger "trx"

      # ── Coverage Report ──────────────────────────────────
      - name: Coverage Report
        uses: danielpalme/ReportGenerator-GitHub-Action@5
        with:
          reports: '**/coverage.cobertura.xml'
          targetdir: 'coverage'
          reporttypes: 'HtmlInline;Cobertura'

      - name: Check Coverage Threshold
        run: |
          COVERAGE=$(grep -oP 'line-rate="\K[^"]+' coverage/Cobertura.xml | head -1)
          echo "Coverage: $COVERAGE"
          if (( $(echo "$COVERAGE < 0.80" | bc -l) )); then echo "Coverage below 80%!" && exit 1; fi

      # ── SAST (Security Analysis) ─────────────────────────
      - name: SAST - Security CodeQL
        uses: github/codeql-action/init@v3
        with: { languages: csharp }
      - name: SAST - Autobuild
        uses: github/codeql-action/autobuild@v3
      - name: SAST - Analyze
        uses: github/codeql-action/analyze@v3

      # ── SCA (Dependency Vulnerability Scan) ──────────────
      - name: SCA - Snyk
        uses: snyk/actions/dotnet@master
        env: { SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }} }
        with: { args: --severity-threshold=high }

      # ── Container Build ──────────────────────────────────
      - name: Build Docker Image
        run: docker build -t ${{ env.IMAGE_NAME }}:${{ github.sha }} .

      # ── Container Scan ───────────────────────────────────
      - name: Scan Image (Trivy)
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: '${{ env.IMAGE_NAME }}:${{ github.sha }}'
          severity: 'CRITICAL,HIGH'
          exit-code: '1'

      # ── Push (main only) ─────────────────────────────────
      - name: Push Image
        if: github.ref == 'refs/heads/main'
        run: |
          echo "${{ secrets.REGISTRY_PASSWORD }}" | docker login -u "${{ secrets.REGISTRY_USERNAME }}" --password-stdin
          docker tag ${{ env.IMAGE_NAME }}:${{ github.sha }} ${{ env.IMAGE_NAME }}:latest
          docker push ${{ env.IMAGE_NAME }}:${{ github.sha }}
          docker push ${{ env.IMAGE_NAME }}:latest
```

**Pipeline stages per EA6:**
```
Restore → Lint → Build → Unit Test → Integration Test → Contract Test → Coverage Check (≥80%) → SAST (CodeQL) → SCA (Snyk) → Docker Build → Image Scan (Trivy) → Push
```

---

## SC11: Test Project Scaffolds

### UnitTests.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\src\{ServiceName}.Application\{ServiceName}.Application.csproj" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
    <PackageReference Include="NSubstitute" Version="5.3.0" />
    <PackageReference Include="FluentAssertions" Version="6.12.1" />
    <PackageReference Include="coverlet.collector" Version="6.0.2" />
  </ItemGroup>
</Project>
```

### IntegrationTests.csproj
```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <IsPackable>false</IsPackable>
  </PropertyGroup>
  <ItemGroup>
    <ProjectReference Include="..\..\src\{ServiceName}.Api\{ServiceName}.Api.csproj" />
    <PackageReference Include="Microsoft.AspNetCore.Mvc.Testing" Version="8.0.10" />
    <PackageReference Include="Microsoft.NET.Test.Sdk" Version="17.11.1" />
    <PackageReference Include="xunit" Version="2.9.2" />
    <PackageReference Include="xunit.runner.visualstudio" Version="2.8.2" />
    <PackageReference Include="FluentAssertions" Version="6.12.1" />
  </ItemGroup>
</Project>
```

---

## SC12: Scaffold Checklist

Before first commit, verify:

| Category | Check | Standard |
|----------|-------|----------|
| Structure | 4-layer Clean Architecture | CS2 |
| Build | `dotnet build` succeeds with zero warnings | SC10 |
| Health | `GET /health` returns 200 | MS8 |
| Health | `GET /health/ready` returns 200 | MS8 |
| Logging | Structured JSON with CorrelationId | MS8, EA9 |
| Tracing | OpenTelemetry spans on HTTP + DB | MS8 |
| Auth | JWT validation configured | MS9, EA5 |
| Errors | RFC 7807 ProblemDetails on exceptions | CS7, EA3 |
| Docker | Image builds, < 200MB, non-root | MS10, EA6 |
| K8s | Deployment + HPA + health probes | MS10 |
| CI | All pipeline stages pass | SC10 |
| Tests | Unit test project compiles and runs | CS12, EA14 |
| Lint | `dotnet format --verify-no-changes` passes | SC10 |
| Security | No secrets in code or config | MS9, EA5 |
| .editorconfig | File-scoped namespaces enforced | CS13 |

---

## SC13: Security Hardening (Embedded)

Add to `Program.cs` middleware pipeline after `app.Build()`:

```csharp
// ── Security Headers ───────────────────────────────────────
app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    context.Response.Headers["X-Frame-Options"] = "DENY";
    context.Response.Headers["X-XSS-Protection"] = "0";
    context.Response.Headers["Referrer-Policy"] = "strict-origin-when-cross-origin";
    context.Response.Headers["Content-Security-Policy"] = "default-src 'self'";
    await next();
});

if (!app.Environment.IsDevelopment())
    app.UseHsts();

// ── CORS ───────────────────────────────────────────────────
// In builder.Services section:
builder.Services.AddCors(o => o.AddDefaultPolicy(p =>
    p.WithOrigins(config.GetSection("Cors:AllowedOrigins").Get<string[]>() ?? [])
     .AllowAnyMethod().AllowAnyHeader()));

// In middleware pipeline:
app.UseCors();

// ── Rate Limiting (.NET 8 built-in) ────────────────────────
builder.Services.AddRateLimiter(o =>
{
    o.AddFixedWindowLimiter("read", opt => { opt.PermitLimit = 100; opt.Window = TimeSpan.FromMinutes(1); });
    o.AddFixedWindowLimiter("write", opt => { opt.PermitLimit = 20; opt.Window = TimeSpan.FromMinutes(1); });
    o.RejectionStatusCode = 429;
});
app.UseRateLimiter();

// Usage on controllers:
[EnableRateLimiting("read")]
[HttpGet]
public async Task<IActionResult> List() => ...

[EnableRateLimiting("write")]
[HttpPost]
public async Task<IActionResult> Create() => ...
```

**Per EA3/EA5/MS9:** Security headers on all responses, CORS restricted to known origins, rate limiting per EA3 (100 read/min, 20 write/min).

---

## SC14: PII Protection in Logging

```csharp
// In Serilog configuration (Program.cs):
Log.Logger = new LoggerConfiguration()
    .Destructure.ByTransforming<LoanApplication>(a => new {
        a.Id, a.Status, a.RequestedAmount,
        NationalId = "***MASKED***",
        FullName = "***MASKED***",
        Income = "***MASKED***"
    })
    // ... rest of config
```

**RULES per EA5/EA9:**
- NEVER log: NationalId, DateOfBirth, FullName, Income, card numbers, tokens, passwords
- Use Serilog `Destructure.ByTransforming` to mask entity PII automatically
- Log only: Id, Status, correlation ID, timestamps, error codes
- Verify with: `grep -r "NationalId\|FullName\|Income" logs/` should return zero matches

---

## SC15: Graceful Shutdown

```csharp
// In Program.cs:
var app = builder.Build();

app.Lifetime.ApplicationStopping.Register(() =>
{
    Log.Information("Service shutting down — draining requests...");
    // Allow in-flight requests to complete (K8s sends SIGTERM, then waits terminationGracePeriodSeconds)
});

app.Lifetime.ApplicationStopped.Register(() =>
{
    Log.Information("Service stopped");
    Log.CloseAndFlush(); // Flush Serilog before exit
});
```

```yaml
# In k8s/deployment.yaml — add to container spec:
terminationGracePeriodSeconds: 30
lifecycle:
  preStop:
    exec:
      command: ["/bin/sh", "-c", "sleep 5"]  # Allow LB to deregister before stopping
```

**Per MS10:** K8s sends SIGTERM → preStop hook (5s for LB deregistration) → app drains in-flight requests → SIGKILL after 30s.

---

## SC16: K8s Service & ConfigMap

### service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: {service-name}
spec:
  selector: { app: {service-name} }
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
  type: ClusterIP
```

### configmap.yaml
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: {service-name}-config
data:
  ASPNETCORE_ENVIRONMENT: "Production"
  ConnectionStrings__DefaultConnection: ""  # Injected from secret in prod
  Auth__Authority: "https://auth.example.com"
  Auth__Audience: "{service-name}"
  Otlp__Endpoint: "http://otel-collector:4317"
  Cors__AllowedOrigins__0: "https://app.example.com"
```

---

## SC17: docker-compose.yml (Local Dev)

```yaml
version: '3.8'
services:
  api:
    build: .
    ports: ["5000:8080"]
    environment:
      - ASPNETCORE_ENVIRONMENT=Development
    depends_on: [db, otel]

  db:
    image: mcr.microsoft.com/mssql/server:2022-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=DevPassword123!
    ports: ["1433:1433"]

  otel:
    image: otel/opentelemetry-collector:latest
    ports: ["4317:4317"]

  jaeger:
    image: jaegertracing/all-in-one:latest
    ports: ["16686:16686"]  # Jaeger UI for trace viewing
```

---

## SC18: .gitignore

```
bin/
obj/
*.user
*.suo
.vs/
*.DotSettings.user
appsettings.*.local.json
coverage/
TestResults/
*.trx
```

---

## SC19: README Template

```markdown
# {ServiceName}

## Quick Start
```bash
dotnet run --project src/{ServiceName}.Api
# API: http://localhost:5000
# Swagger: http://localhost:5000/swagger
# Health: http://localhost:5000/health
```

## Docker
```bash
docker-compose up
```

## Tests
```bash
dotnet test                          # All tests
dotnet test tests/{ServiceName}.UnitTests  # Unit only
```

## Architecture
- **Domain**: Entities, enums, interfaces (zero dependencies)
- **Application**: CQRS handlers (MediatR), validators, DTOs
- **Infrastructure**: EF Core, repositories, external services
- **Api**: Controllers, middleware, startup

## CI Pipeline
Restore → Lint → Build → Unit Test → Integration Test → Contract Test → Coverage (≥80%) → SAST → SCA → Docker Build → Image Scan → Push
```
