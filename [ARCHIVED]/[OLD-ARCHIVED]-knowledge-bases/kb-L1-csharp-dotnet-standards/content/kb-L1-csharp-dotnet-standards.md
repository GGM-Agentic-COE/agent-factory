# C# / .NET 8 API Development Standards — Knowledge Base
### kb-L1-csharp-dotnet-standards v1.0.0
### Derived from Tasheel Finance codebase + industry best practices. Code generator agents MUST follow these standards.

---

## CS1: Technology Stack

| Component | Technology | Version | Notes |
|-----------|-----------|---------|-------|
| Language | C# | 12 | Primary constructors, file-scoped namespaces, records |
| Runtime | .NET | 8.0 | LTS, `global.json` pins SDK version |
| Web Framework | ASP.NET Core Web API | 8.0 | Minimal hosting model (`WebApplication.CreateBuilder`) |
| CQRS / Mediator | MediatR | 12 | `IRequest<T>` / `IRequestHandler<TRequest, TResponse>` |
| Validation | FluentValidation | 11 | `IPipelineBehavior` integration |
| ORM | Entity Framework Core | 8 | Code-first, `DbContext`, `IEntityTypeConfiguration<T>` |
| Logging | Serilog | 4 | Structured JSON, `WriteTo.Console()`, `Enrich.FromLogContext()` |
| API Docs | Swashbuckle | 6 | OpenAPI / Swagger auto-generation |
| Database | SQL Server 2022 | — | In-memory for dev (`UseInMemoryDatabase`) |
| Testing | xUnit + NSubstitute | — | Unit + integration |
| DI | Built-in .NET DI | — | Constructor injection via primary constructors |

---

## CS2: Solution Structure

```
{SolutionName}.sln
global.json                          # SDK version pinning
Dockerfile                           # Multi-stage build
src/
  {Project}.Domain/                  # Layer 0: No dependencies
    Entities/                        # Domain entities (one file per entity)
    Enums/                           # Domain enums (one file per enum)
    Interfaces/                      # Repository + service interfaces
    {Project}.Domain.csproj

  {Project}.Application/             # Layer 1: Depends on Domain only
    {Feature}/
      Commands/                      # Write operations (MediatR IRequest)
      Queries/                       # Read operations (MediatR IRequest)
    Common/
      Behaviours/                    # MediatR pipeline behaviours
    DTOs/                            # Data transfer objects (records)
    {Project}.Application.csproj

  {Project}.Infrastructure/          # Layer 2: Implements Domain interfaces
    Persistence/
      AppDbContext.cs                # EF Core DbContext
      Configurations/               # IEntityTypeConfiguration per entity
      Repositories/                 # Repository implementations
    Services/                       # External service implementations (mocks)
    Seed/                           # Data seeding
    {Project}.Infrastructure.csproj

  {Project}.Api/                     # Layer 3: Entry point
    Controllers/                    # One controller per resource
    Middleware/                     # Exception handling, correlation ID
    Properties/
      launchSettings.json
    Program.cs                      # DI, middleware, pipeline setup
    appsettings.json
    {Project}.Api.csproj

tests/                              # Alongside src
  unit/
  contract/
  integration/
  bdd/
  helpers/
```

**RULES:**
- One `.csproj` per layer — strict dependency direction (Domain ← Application ← Infrastructure ← Api)
- Domain project has ZERO NuGet dependencies
- Application references Domain only
- Infrastructure references Domain + Application
- Api references all (entry point)

---

## CS3: Naming Conventions

| Element | Convention | Example |
|---------|-----------|---------|
| Namespaces | `{Project}.{Layer}.{Feature}` | `LoanApp.Application.Applications.Commands` |
| Classes | PascalCase | `AssessApplicationHandler` |
| Interfaces | `I` prefix + PascalCase | `IApplicationRepository` |
| Methods | PascalCase | `GetByIdAsync()` |
| Async methods | `Async` suffix | `GetByIdAsync()` |
| Properties | PascalCase | `RequestedAmount` |
| Private fields | `_camelCase` | `_applicationRepository` |
| Constants | PascalCase | `MaxRetryCount` |
| Enums | PascalCase (singular) | `ApplicationStatus.Submitted` |
| Records (DTOs) | PascalCase + `Dto` suffix | `AssessmentResultDto` |
| Commands | `{Verb}{Entity}Command` | `CreateApplicationCommand` |
| Queries | `Get{Entity}Query` | `GetProductsQuery` |
| Handlers | `{Command/Query}Handler` | `AssessApplicationHandler` |
| Controllers | `{Resource}Controller` | `ApplicationsController` |
| Configurations | `{Entity}Configuration` | `LoanApplicationConfiguration` |
| Files | One class per file, PascalCase | `AssessApplicationCommand.cs` |

---

## CS4: Entity Pattern

```csharp
using {Project}.Domain.Enums;

namespace {Project}.Domain.Entities;

public class LoanApplication
{
    public Guid Id { get; set; }
    // Business fields
    public decimal RequestedAmount { get; set; }
    public ApplicationStatus Status { get; set; } = ApplicationStatus.Draft;

    // Nullable fields for optional data
    public string? Address { get; set; }
    public DateOnly? DateOfBirth { get; set; }

    // Audit fields (EA4 mandatory)
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public string CreatedBy { get; set; } = "system";
    public DateTime? UpdatedAt { get; set; }
    public string? UpdatedBy { get; set; }
    public bool IsDeleted { get; set; }

    // Navigation properties
    public Product? Product { get; set; }
    public ICollection<Offer> Offers { get; set; } = [];
}
```

**RULES:**
- File-scoped namespace (`namespace X;` not `namespace X { }`)
- `Guid` for all IDs (not int/long)
- Nullable reference types enabled (`string?` for optional)
- Default values on creation fields (`= DateTime.UtcNow`)
- Collection initializer `= []` (C# 12)
- EA4 audit columns on EVERY entity

---

## CS5: CQRS Handler Pattern (MediatR)

### Command (Write)
```csharp
namespace {Project}.Application.{Feature}.Commands;

// Command record — immutable, serializable
public record CreateApplicationCommand(
    Guid ProductId, decimal RequestedAmount, int RequestedTenure,
    string FullName, string NationalId
) : IRequest<ApplicationDto>;

// Handler — primary constructor for DI
public class CreateApplicationHandler(
    IApplicationRepository repo,
    IProductRepository productRepo
) : IRequestHandler<CreateApplicationCommand, ApplicationDto>
{
    public async Task<ApplicationDto> Handle(CreateApplicationCommand cmd, CancellationToken ct)
    {
        var product = await productRepo.GetByIdAsync(cmd.ProductId, ct)
            ?? throw new KeyNotFoundException("Product not found");

        var app = new LoanApplication { /* map from cmd */ };
        await repo.AddAsync(app, ct);
        return new ApplicationDto(/* map from app */);
    }
}
```

### Query (Read)
```csharp
namespace {Project}.Application.{Feature}.Queries;

public record GetProductsQuery : IRequest<List<ProductDto>>;

public class GetProductsHandler(IProductRepository repo)
    : IRequestHandler<GetProductsQuery, List<ProductDto>>
{
    public async Task<List<ProductDto>> Handle(GetProductsQuery query, CancellationToken ct)
        => (await repo.GetAllAsync(ct)).Select(p => new ProductDto(/* map */)).ToList();
}
```

**RULES:**
- Commands and Queries are `record` types (immutable)
- One handler per command/query (Single Responsibility)
- Handlers use primary constructors for DI (C# 12)
- Handlers are < 50 lines (extract complex logic to domain services)
- `CancellationToken` propagated through all async calls
- Throw `KeyNotFoundException` for 404, `InvalidOperationException` for 422

---

## CS6: Controller Pattern

```csharp
namespace {Project}.Api.Controllers;

[ApiController]
[Route("api/v1/{resource}")]
public class ApplicationsController(IMediator mediator) : ControllerBase
{
    [HttpPost]
    public async Task<IActionResult> Create(CreateApplicationCommand cmd)
        => Created($"api/v1/applications", await mediator.Send(cmd));

    [HttpGet("{id:guid}")]
    public async Task<IActionResult> Get(Guid id)
        => Ok(await mediator.Send(new GetApplicationQuery(id)));

    [HttpPost("{id:guid}/submit")]
    public async Task<IActionResult> Submit(Guid id)
        => Ok(await mediator.Send(new SubmitApplicationCommand(id)));
}
```

**RULES:**
- `[ApiController]` attribute on every controller
- Route: `api/v1/{plural-resource}` (lowercase, plural)
- Primary constructor for `IMediator` injection
- Controllers are THIN — delegate to MediatR handlers
- Return `Created()` for POST creation, `Ok()` for everything else
- Use route constraints (`{id:guid}`)
- No business logic in controllers

---

## CS7: Middleware Pattern

### Exception Middleware (RFC 7807)
```csharp
public class ExceptionMiddleware(RequestDelegate next, ILogger<ExceptionMiddleware> logger)
{
    public async Task InvokeAsync(HttpContext context)
    {
        try { await next(context); }
        catch (KeyNotFoundException ex) { await WriteProblem(context, 404, "Not Found", ex.Message); }
        catch (InvalidOperationException ex) { await WriteProblem(context, 422, "Business Rule Violation", ex.Message); }
        catch (ValidationException ex) { await WriteProblem(context, 400, "Validation Error", ex.Message); }
        catch (Exception ex) { logger.LogError(ex, "Unhandled"); await WriteProblem(context, 500, "Internal Error", null); }
    }

    private static async Task WriteProblem(HttpContext ctx, int status, string title, string? detail)
    {
        ctx.Response.StatusCode = status;
        ctx.Response.ContentType = "application/problem+json";
        await ctx.Response.WriteAsJsonAsync(new ProblemDetails { Status = status, Title = title, Detail = detail });
    }
}
```

### Correlation ID Middleware
```csharp
public class CorrelationIdMiddleware(RequestDelegate next)
{
    public async Task InvokeAsync(HttpContext context)
    {
        var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString();
        context.Response.Headers["X-Correlation-Id"] = correlationId;
        using (LogContext.PushProperty("CorrelationId", correlationId))
            await next(context);
    }
}
```

---

## CS8: Pipeline Behaviours

### Validation Behaviour
```csharp
public class ValidationBehaviour<TRequest, TResponse>(IEnumerable<IValidator<TRequest>> validators)
    : IPipelineBehavior<TRequest, TResponse> where TRequest : notnull
{
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        if (!validators.Any()) return await next();
        var context = new ValidationContext<TRequest>(request);
        var failures = (await Task.WhenAll(validators.Select(v => v.ValidateAsync(context, ct))))
            .SelectMany(r => r.Errors).Where(f => f != null).ToList();
        if (failures.Count != 0) throw new ValidationException(failures);
        return await next();
    }
}
```

### Audit Behaviour
```csharp
public class AuditBehaviour<TRequest, TResponse>(IAuditRepository audit, ILogger<AuditBehaviour<TRequest, TResponse>> logger)
    : IPipelineBehavior<TRequest, TResponse> where TRequest : notnull
{
    public async Task<TResponse> Handle(TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        logger.LogInformation("Handling {Request}", typeof(TRequest).Name);
        var response = await next();
        // Audit log write (async, non-blocking)
        return response;
    }
}
```

---

## CS9: EF Core Patterns

### DbContext
```csharp
public class AppDbContext(DbContextOptions<AppDbContext> options) : DbContext(options)
{
    public DbSet<Product> Products => Set<Product>();
    public DbSet<LoanApplication> Applications => Set<LoanApplication>();
    // ... one DbSet per entity

    protected override void OnModelCreating(ModelBuilder modelBuilder)
        => modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

### Entity Configuration
```csharp
public class LoanApplicationConfiguration : IEntityTypeConfiguration<LoanApplication>
{
    public void Configure(EntityTypeBuilder<LoanApplication> builder)
    {
        builder.HasKey(e => e.Id);
        builder.Property(e => e.Id).HasDefaultValueSql("NEWSEQUENTIALID()");
        builder.Property(e => e.RequestedAmount).HasColumnType("decimal(18,2)");
        builder.HasQueryFilter(e => !e.IsDeleted); // Soft delete
        builder.HasIndex(e => e.UserId);
    }
}
```

### Repository
```csharp
public class ApplicationRepository(AppDbContext db) : IApplicationRepository
{
    public async Task<LoanApplication?> GetByIdAsync(Guid id, CancellationToken ct = default)
        => await db.Applications.FirstOrDefaultAsync(a => a.Id == id, ct);

    public async Task AddAsync(LoanApplication app, CancellationToken ct = default)
    {
        db.Applications.Add(app);
        await db.SaveChangesAsync(ct);
    }

    public async Task UpdateAsync(LoanApplication app, CancellationToken ct = default)
    {
        app.UpdatedAt = DateTime.UtcNow;
        await db.SaveChangesAsync(ct);
    }
}
```

---

## CS10: Program.cs (Startup)

```csharp
var builder = WebApplication.CreateBuilder(args);

// Logging
Log.Logger = new LoggerConfiguration().WriteTo.Console().Enrich.FromLogContext().CreateLogger();
builder.Host.UseSerilog();

// EF Core
builder.Services.AddDbContext<AppDbContext>(o => o.UseInMemoryDatabase("DevDb"));

// MediatR + Behaviours
builder.Services.AddMediatR(cfg => cfg.RegisterServicesFromAssemblyContaining<GetProductsQuery>());
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(ValidationBehaviour<,>));
builder.Services.AddTransient(typeof(IPipelineBehavior<,>), typeof(AuditBehaviour<,>));

// FluentValidation
builder.Services.AddValidatorsFromAssemblyContaining<GetProductsQuery>();

// Repositories
builder.Services.AddScoped<IProductRepository, ProductRepository>();
builder.Services.AddScoped<IApplicationRepository, ApplicationRepository>();

// External services
builder.Services.AddScoped<ISimahService, SimahService>();

// Controllers + JSON
builder.Services.AddControllers().AddJsonOptions(o => {
    o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
    o.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
});

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

// Seed
using (var scope = app.Services.CreateScope())
{
    var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
    db.Database.EnsureCreated();
    DataSeeder.Seed(db);
}

// Middleware pipeline (order matters)
app.UseMiddleware<CorrelationIdMiddleware>();
app.UseMiddleware<ExceptionMiddleware>();
app.UseSwagger();
app.UseSwaggerUI();
app.MapControllers();
app.Run();
```

---

## CS11: DTO Pattern

```csharp
namespace {Project}.Application.DTOs;

// Use records for immutable DTOs
public record ProductDto(Guid Id, string Name, string Type, decimal MinAmount, decimal MaxAmount);
public record AssessmentResultDto(Guid ApplicationId, string Status, decimal? ApprovedAmount, string? RejectionReason);
public record SettlementFigureDto(Guid LoanId, decimal OutstandingPrincipal, decimal AccruedProfit, decimal EarlyClosureFee, decimal TotalSettlement);
```

**RULES:**
- DTOs are `record` types (immutable, value equality)
- Positional records for simple DTOs (constructor syntax)
- Never expose domain entities directly — always map to DTOs
- Nullable properties for optional fields (`decimal?`, `string?`)
- No business logic in DTOs

---

## CS12: Testing Standards

### Unit Test (xUnit + NSubstitute)
```csharp
public class AssessApplicationHandlerTests
{
    [Fact]
    public async Task Handle_WhenIncomeAboveThreshold_ShouldApprove()
    {
        var appRepo = Substitute.For<IApplicationRepository>();
        var productRepo = Substitute.For<IProductRepository>();
        // Arrange, Act, Assert
    }
}
```

### Integration Test (WebApplicationFactory)
```csharp
public class ApplicationsApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    [Fact]
    public async Task CreateApplication_ReturnsCreated()
    {
        var client = _factory.CreateClient();
        var response = await client.PostAsJsonAsync("/api/v1/applications", new { ... });
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
    }
}
```

**Test naming**: `{Method}_When{Condition}_Should{Result}`
**Coverage**: ≥ 80% on Application layer handlers
**Test data**: synthetic only, no real PII

---

## CS13: Code Quality Rules

1. File-scoped namespaces (`namespace X;`)
2. Primary constructors for DI (C# 12)
3. `record` for DTOs and commands/queries
4. Collection expressions `= []` (C# 12)
5. `var` for obvious types, explicit for ambiguous
6. No `async void` — always `async Task`
7. `CancellationToken` on all async methods
8. No `#region` blocks
9. Max method: 30 lines, max class: 300 lines
10. All public APIs have XML doc comments

---

## CS14: External Service Interface Pattern

Define interfaces in Domain, implement as mocks in Infrastructure:

```csharp
// Domain/Interfaces/IExternalServices.cs
namespace {Project}.Domain.Interfaces;

public interface ISimahService
{
    Task<int> GetCreditScoreAsync(string userId, decimal income, CancellationToken ct = default);
}

public interface ICitcService
{
    Task<bool> VerifyEmploymentAsync(string employerName, CancellationToken ct = default);
}

public interface IPaymentProcessorService
{
    Task<(string Token, string Last4)> TokenizeCardAsync(string cardNumber, CancellationToken ct = default);
}
```

```csharp
// Infrastructure/Services/SimahService.cs — mock for dev
namespace {Project}.Infrastructure.Services;

public class SimahService : ISimahService
{
    public Task<int> GetCreditScoreAsync(string userId, decimal income, CancellationToken ct = default)
        => Task.FromResult(income > 8000 ? 700 : 450); // Mock: score based on income
}
```

**RULES:**
- One interface per external system in Domain/Interfaces
- Mock implementations in Infrastructure/Services for local dev
- Real implementations swap in via DI config per environment
- All external calls accept `CancellationToken`
- Mock behaviour should be deterministic and testable (e.g., "FAIL" in employer name triggers failure)

---

## CS15: Resilience Pattern (Polly)

```csharp
// In Program.cs or DI setup
builder.Services.AddHttpClient<ISimahService, SimahService>()
    .AddPolicyHandler(Policy.Handle<HttpRequestException>()
        .WaitAndRetryAsync(3, attempt => TimeSpan.FromSeconds(Math.Pow(2, attempt))))
    .AddPolicyHandler(Policy.Handle<HttpRequestException>()
        .CircuitBreakerAsync(5, TimeSpan.FromSeconds(30)));
```

**Configuration per EA7:**
| External Service | Timeout | Retries | Circuit Breaker |
|-----------------|---------|---------|-----------------|
| SIMAH | 30s | 3 (1s, 2s, 4s) | 5 failures / 30s → 60s break |
| CITC | 30s | 3 | 3 failures / 30s → 30s break |
| Payment Processor | 30s | 2 | 5 failures / 30s → 60s break |
| SMS Gateway | 10s | 2 | 10 failures / 60s → 30s break |

**RULES:**
- Every `HttpClient` for external services MUST have Polly policies
- Retry only on transient errors (timeout, 503) — NOT on 400, 404, 422
- Circuit breaker prevents cascading failures
- Fallback: queue for retry (writes) or return cached/default (reads)

---

## CS16: NuGet Package Versions (Pinned)

From the actual codebase `.csproj` files:

| Package | Version | Project |
|---------|---------|---------|
| MediatR | 12.4.1 | Application |
| FluentValidation.AspNetCore | 11.3.0 | Application |
| Serilog.AspNetCore | 8.0.2 | Api |
| Serilog.Sinks.Console | 6.0.0 | Api |
| Serilog.Enrichers.Environment | 3.0.1 | Api |
| Swashbuckle.AspNetCore | 6.8.1 | Api |
| Microsoft.EntityFrameworkCore.InMemory | 8.0.10 | Infrastructure |
| Microsoft.EntityFrameworkCore.SqlServer | 8.0.10 | Infrastructure (prod) |

**RULES:**
- All versions pinned (no wildcards `*`)
- Update via PR with test verification
- No GPL/AGPL licensed packages (per EA16)

---

## CS17: Brownfield Modification Guide

When adding new features to an existing project:

### Adding a New Entity
1. Create `{Entity}.cs` in `Domain/Entities/`
2. Create `{Entity}Configuration.cs` in `Infrastructure/Persistence/Configurations/`
3. Add `DbSet<{Entity}>` to `AppDbContext`
4. Add EF Core migration: `dotnet ef migrations add Add{Entity}`
5. New fields on existing entities: nullable or with default (backward compatible)

### Adding a New Handler
1. Create `{Verb}{Entity}Command.cs` in `Application/{Feature}/Commands/`
2. Follow exact same pattern as existing handlers (primary constructor, record command)
3. Register automatically via `RegisterServicesFromAssemblyContaining` (no manual DI)

### Adding a New Endpoint
1. Add method to existing controller (if same resource) or create new controller
2. Follow same route pattern: `api/v1/{resource}` or `api/v1/{resource}/{id}/{action}`
3. Delegate to MediatR — no business logic in controller

### Adding a New External Service
1. Define interface in `Domain/Interfaces/`
2. Create mock in `Infrastructure/Services/`
3. Register in `Program.cs`: `builder.Services.AddScoped<INewService, NewService>()`

### DO NOT
- Refactor existing code unless the story requires it
- Change existing method signatures (add overloads instead)
- Modify existing entity properties (add new ones)
- Restructure existing namespaces or folders

---

## Cross-References to Enterprise Architecture

| KB Section | EA Reference | Alignment |
|-----------|-------------|-----------|
| CS1 Tech Stack | EA1 | All technologies from EA1 mandatory list |
| CS2 Solution Structure | EA2 | Clean Architecture with CQRS per EA2 |
| CS4 Entity Pattern | EA4 | Audit columns, soft delete, GUID PKs per EA4 |
| CS6 Controller Pattern | EA3 | API standards (plural nouns, versioned routes) per EA3 |
| CS7 Middleware | EA3 | RFC 7807 ProblemDetails per EA3 |
| CS9 EF Core | EA4 | Data architecture, encryption, migrations per EA4 |
| CS10 Program.cs | EA5 | No secrets in code, Serilog no PII per EA5 |
| CS12 Testing | EA14 | Test pyramid, 80% coverage per EA14 |
| CS15 Resilience | EA7 | Circuit breaker, retry, timeout per EA7 |
| CS16 NuGet | EA16 | Pinned versions, no GPL per EA16 |
