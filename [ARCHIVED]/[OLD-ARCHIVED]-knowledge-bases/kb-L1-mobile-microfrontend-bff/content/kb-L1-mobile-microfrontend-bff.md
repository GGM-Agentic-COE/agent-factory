# Mobile Micro-Frontend with BFF Pattern

> Layer: L1 | Sections: MM1–MM12 | Version: 1.0

---

## MM1: Core Principles

The mobile micro-frontend pattern decomposes a monolithic mobile application into
independently developable feature modules coordinated by a thin App Shell, with a
dedicated Backend-for-Frontend (BFF) layer optimizing server communication for
mobile constraints.

**Guiding principles:**

1. **Modular mobile architecture** — the app is a composition of feature modules,
   not a single codebase with package-level separation. Each module compiles
   independently and can be developed by a separate team.
2. **Feature modules as independent units** — a feature module owns its screens,
   business logic, data layer, and DI graph. It exposes only a navigation entry
   point to the App Shell.
3. **BFF per mobile app, not per feature** — one BFF serves the entire mobile app.
   It aggregates microservice calls into screen-shaped responses. Feature-level
   BFFs create deployment sprawl and cross-cutting concern duplication.
4. **Shared design system module** — a single `:core:ui` module provides the
   design tokens, atoms, and molecules so every feature module renders a
   consistent UI without duplicating components.
5. **Independent feature development** — feature teams can build, test, and
   release their module without coordinating with other feature teams. Only
   `:core` module changes require cross-team alignment.

---

## MM2: Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Mobile App Shell                   │
│  ┌───────────┬───────────┬────────────┬───────────┐ │
│  │Navigation │   Auth    │   Theme    │  Crash    │ │
│  │  (NavHost)│  (Token)  │ (Design)   │ Reporting │ │
│  └───────────┴───────────┴────────────┴───────────┘ │
│                        │                             │
│  ┌─────────────────────┼─────────────────────────┐  │
│  │                     │                         │  │
│  ▼                     ▼                         ▼  │
│ ┌──────────┐   ┌──────────────┐   ┌────────────┐   │
│ │ Feature  │   │   Feature    │   │  Feature   │   │
│ │Module A  │   │  Module B    │   │ Module C   │   │
│ │(Products)│   │(Application) │   │  (Loans)   │   │
│ └────┬─────┘   └──────┬───────┘   └─────┬──────┘   │
│      │                │                  │          │
│      └────────────────┼──────────────────┘          │
│                       │                             │
│              ┌────────┴────────┐                    │
│              │  :core:network  │                    │
│              │  (API Client)   │                    │
│              └────────┬────────┘                    │
└───────────────────────┼─────────────────────────────┘
                        │  HTTPS / gRPC
                        ▼
              ┌─────────────────┐
              │   Mobile BFF    │
              │  (Single BFF)   │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ▼            ▼            ▼
   ┌───────────┐ ┌──────────┐ ┌──────────┐
   │ Product   │ │ Lending  │ │ Customer │
   │ Service   │ │ Service  │ │ Service  │
   └───────────┘ └──────────┘ └──────────┘
```

**App Shell responsibilities:**

- Owns the root `NavHost` and top-level navigation (bottom bar, drawer).
- Manages authentication state and token lifecycle.
- Applies the global theme from `:core:ui`.
- Initializes crash reporting (Crashlytics / Sentry).
- Registers deep link handlers and delegates to feature modules.

---

## MM3: Feature Module Pattern

Each feature is a **Gradle module** (Android) or **Swift Package** (iOS).

**Internal structure of a feature module:**

```
:feature:products/
├── src/main/kotlin/com/app/feature/products/
│   ├── navigation/
│   │   └── ProductsNavigation.kt      // FeatureNavigation impl
│   ├── ui/
│   │   ├── ProductListScreen.kt
│   │   └── ProductDetailScreen.kt
│   ├── viewmodel/
│   │   ├── ProductListViewModel.kt
│   │   └── ProductDetailViewModel.kt
│   ├── data/
│   │   ├── ProductRepository.kt
│   │   └── ProductLocalDataSource.kt
│   └── di/
│       └── ProductsModule.kt          // Hilt / Koin module
└── build.gradle.kts
```

**Rules:**

- A feature module exposes **only** its `FeatureNavigation` implementation.
- All screens, ViewModels, repositories, and DI bindings are `internal`.
- No direct dependency between feature modules — ever. If Feature A needs data
  from Feature B, it goes through the BFF or a `:core:domain` shared model.
- Each feature module declares its own Hilt/Koin module for DI.

---

## MM4: Module Structure

```
:app                          // App Shell — composes features, owns NavHost
:feature:products             // Product catalog browsing
:feature:application          // Loan/account application flow
:feature:loans                // Active loans management
:feature:dashboard            // Home dashboard with aggregated data
:core:ui                      // Design system — theme, atoms, molecules
:core:network                 // Retrofit/Ktor client, AuthInterceptor
:core:domain                  // Shared domain models, DTOs
:core:auth                    // Biometric unlock, token storage
:core:analytics               // Analytics abstraction
```

**Dependency rules (enforced via Gradle module boundaries):**

```
:app          → :feature:*    (composes all features)
:app          → :core:*       (initializes core modules)
:feature:*    → :core:ui      (uses design system)
:feature:*    → :core:network (makes API calls)
:feature:*    → :core:domain  (shares models)
:feature:*    → :core:auth    (checks auth state)
:feature:*    ✗ :feature:*    (NEVER — hard rule)
:core:network → :core:auth    (attaches tokens)
:core:ui      → (no deps)    (leaf module)
```

Enforce with Gradle's `api` / `implementation` scoping and a custom lint rule or
dependency-guard plugin that fails the build on `:feature → :feature` edges.

---

## MM5: Mobile BFF

The Mobile BFF is a **single backend service** dedicated to the mobile app.

**What the BFF does:**

- **Aggregates microservice calls** — a single BFF endpoint calls 2–5
  microservices and merges the results into one response shaped for a mobile
  screen.
- **Auth token exchange** — accepts the mobile OAuth token, exchanges it for
  internal service tokens, and forwards requests with proper scopes.
- **Response shaping** — strips fields the mobile screen does not need, flattens
  nested structures, and converts enums to display-ready strings when appropriate.
- **Push notification registration** — accepts device tokens and registers them
  with the notification service.
- **Offline sync endpoints** — provides delta-sync endpoints that return only
  records changed since a given timestamp.

**What the BFF is NOT:**

- Not a general-purpose API gateway — it serves only the mobile app.
- Not a place for business logic — it orchestrates and shapes, never decides.
- Not shared with the web app — the web app has its own BFF (see MF5).

**Tech stack:** Kotlin + Ktor or Node.js + Express, deployed as a single service
behind the API gateway. Scales horizontally. Stateless — all session state lives
in the mobile client or downstream services.

---

## MM6: BFF API Design for Mobile

**Screen-oriented endpoints:**

```
GET  /mobile/v1/dashboard
GET  /mobile/v1/products?cursor={cursor}&limit=20
GET  /mobile/v1/products/{id}
GET  /mobile/v1/application-form/{type}
POST /mobile/v1/application-form
GET  /mobile/v1/loans
GET  /mobile/v1/loans/{id}/schedule
POST /mobile/v1/sync/delta
POST /mobile/v1/devices/register
```

**Design rules:**

1. **One screen, one call** — the `/mobile/v1/dashboard` endpoint returns
   everything the dashboard screen needs: greeting, account summary, recent
   transactions, product offers. No client-side orchestration.
2. **Mobile-only fields** — responses include only fields the mobile screen
   renders. No `createdBy`, `internalNotes`, or audit fields.
3. **Cursor-based pagination** — optimized for infinite scroll. Response includes
   `nextCursor` and `hasMore`. No offset-based pagination.
4. **Delta sync** — `POST /mobile/v1/sync/delta` accepts `{ lastSyncTimestamp }`
   and returns `{ updated: [...], deleted: [...], serverTimestamp }`.
5. **Versioned paths** — `/mobile/v1/` prefix. New breaking changes go to `/v2/`.
   Old versions supported for at least 2 app release cycles.

**Example dashboard response:**

```json
{
  "greeting": "Good morning, Alex",
  "accounts": [
    { "id": "acc-1", "name": "Current Account", "balance": "£1,234.56" }
  ],
  "recentTransactions": [
    { "id": "tx-1", "description": "Coffee Shop", "amount": "-£3.50", "date": "2026-04-21" }
  ],
  "offers": [
    { "id": "offer-1", "title": "Personal Loan", "subtitle": "From 3.9% APR" }
  ],
  "nextSyncTimestamp": "2026-04-21T10:00:00Z"
}
```

---

## MM7: Shared Design System Module

The `:core:ui` module is the single source of truth for visual components.

**Structure:**

```
:core:ui/
├── theme/
│   ├── Color.kt              // Brand palette, semantic colors
│   ├── Type.kt               // Typography scale
│   └── Dimens.kt             // Spacing, radius, elevation
├── atoms/
│   ├── AppButton.kt          // Primary, Secondary, Text variants
│   ├── AppTextField.kt       // With label, error, helper text
│   └── AppCard.kt            // Elevated, outlined variants
├── molecules/
│   ├── FormField.kt          // Label + TextField + validation
│   └── ProductCard.kt        // Image + title + subtitle + CTA
└── util/
    └── PreviewHelpers.kt     // @Preview wrappers with theme
```

**Rules:**

- Every composable has at least one `@Preview` annotated function.
- Atoms accept only primitive parameters (String, Boolean, lambdas) — no domain
  models.
- Molecules may accept simple data classes but never entities from `:core:domain`.
- The module has **zero dependencies** on other modules — it is a leaf.
- Versioned with the app (not published to a separate artifact repository).
  Breaking changes require a migration guide in the PR description.

---

## MM8: Navigation Between Modules

**App Shell owns the NavHost:**

```kotlin
// :app — MainActivity.kt
@Composable
fun AppNavHost(navController: NavHostController) {
    NavHost(navController, startDestination = "dashboard") {
        productsNavigation(navController)   // from :feature:products
        applicationNavigation(navController) // from :feature:application
        loansNavigation(navController)       // from :feature:loans
        dashboardNavigation(navController)   // from :feature:dashboard
    }
}
```

**Feature module navigation contract:**

```kotlin
// :feature:products — ProductsNavigation.kt
fun NavGraphBuilder.productsNavigation(navController: NavController) {
    navigation(startDestination = "products/list", route = "products") {
        composable("products/list") { ProductListScreen(navController) }
        composable("products/{id}") { ProductDetailScreen(navController) }
    }
}
```

**Rules:**

- Each feature module exposes a single `NavGraphBuilder` extension function.
- Route strings are owned by the feature module that declares them.
- Cross-feature navigation uses route strings passed via the App Shell — Feature
  A never imports Feature B's route constants.
- Deep links are declared in the App Shell's `AndroidManifest.xml` and routed to
  the correct feature module via the `NavHost`.

---

## MM9: Shared Authentication

**Token storage and refresh are centralized in `:core:network` and `:core:auth`.**

```
:core:auth
├── TokenStore.kt              // EncryptedSharedPreferences wrapper
├── BiometricAuthManager.kt    // BiometricPrompt abstraction
└── AuthState.kt               // Sealed class: Authenticated | Unauthenticated | Locked

:core:network
├── AuthInterceptor.kt         // OkHttp interceptor — attaches Bearer token
├── TokenRefreshAuthenticator.kt // OkHttp authenticator — refreshes on 401
└── ApiClient.kt               // Configured Retrofit/Ktor instance
```

**Flow:**

1. User logs in → App Shell calls BFF `/mobile/v1/auth/token` → receives
   access + refresh tokens.
2. `TokenStore` persists tokens in `EncryptedSharedPreferences`.
3. Every API call passes through `AuthInterceptor` which reads the token from
   `TokenStore` and attaches `Authorization: Bearer <token>`.
4. On 401, `TokenRefreshAuthenticator` uses the refresh token to obtain a new
   access token, retries the original request.
5. If refresh fails, `AuthState` transitions to `Unauthenticated`, App Shell
   navigates to the login screen.

**Biometric unlock:**

- On app backgrounding, `AuthState` transitions to `Locked`.
- On resume, `BiometricAuthManager` prompts for fingerprint/face.
- Success → `AuthState` transitions to `Authenticated`, no network call needed.
- Failure after 3 attempts → `AuthState` transitions to `Unauthenticated`,
  full re-login required.

---

## MM10: Offline & Sync

**Each feature module owns its local persistence.**

```
:feature:products
└── data/
    ├── local/
    │   ├── ProductDao.kt          // Room DAO
    │   ├── ProductEntity.kt       // Room entity
    │   └── ProductDatabase.kt     // Room database (per-feature)
    └── sync/
        └── ProductSyncWorker.kt   // WorkManager worker
```

**Sync strategy:**

1. **Read path** — ViewModel reads from Room (single source of truth). Repository
   fetches from BFF and upserts into Room. UI observes Room via Flow.
2. **Write path** — user action writes to Room with `syncStatus = PENDING`.
   `SyncWorker` picks up pending records and POSTs to BFF. On success, updates
   `syncStatus = SYNCED`.
3. **Delta sync** — `SyncWorker` calls `POST /mobile/v1/sync/delta` with
   `lastSyncTimestamp`. BFF returns changed records. Worker upserts into Room.
4. **Conflict resolution** — default strategy is **server-wins**: if the server
   returns a record with a newer timestamp than the local pending change, the
   server version overwrites. Feature modules may opt into **last-write-wins**
   where the latest timestamp (client or server) wins.

**WorkManager configuration:**

- Constraints: `NetworkType.CONNECTED`.
- Backoff: exponential, starting at 30 seconds.
- Periodic sync: every 15 minutes when app is in background.
- Immediate sync: triggered on app foreground and after user writes.

**Sync status exposed to UI:**

```kotlin
enum class SyncStatus { SYNCED, PENDING, FAILED }

data class SyncableItem<T>(val data: T, val syncStatus: SyncStatus)
```

---

## MM11: Testing

**Each module is tested in isolation.**

| Module          | Unit Tests                  | UI Tests                  | Integration Tests       |
|-----------------|-----------------------------|---------------------------|-------------------------|
| `:feature:*`    | ViewModel, Repository       | Screen composables        | —                       |
| `:core:ui`      | —                           | Component @Preview tests  | —                       |
| `:core:network` | Interceptor, Authenticator  | —                         | MockWebServer           |
| `:core:auth`    | TokenStore, AuthState       | —                         | —                       |
| `:app`          | —                           | Navigation flow tests     | End-to-end with BFF     |

**Rules:**

1. Feature module tests **never** depend on another feature module.
2. Feature module tests mock `:core:network` responses — they do not call the
   real BFF.
3. `:core` modules have their own test suites. Changes to `:core` run all
   downstream feature module tests in CI.
4. Integration tests live in `:app` and verify navigation flows across features
   using a fake NavHost.
5. BFF contract tests use Pact or similar to verify the BFF response shape
   matches what the mobile client expects.

**Test tooling:**

- Unit: JUnit 5 + Turbine (Flow testing) + MockK.
- UI: Compose UI Test + Robolectric for fast feedback.
- Integration: Espresso + MockWebServer.
- BFF contract: Pact JVM.

---

## MM12: Cross-References

| Reference       | KB                          | Relevance                                          |
|-----------------|-----------------------------|----------------------------------------------------|
| MS1–MS12        | Microservices               | Backend services the BFF aggregates                |
| MF1–MF14        | Web Micro-Frontend          | Parallel pattern for web; web has its own BFF      |
| EA10            | Enterprise Architecture     | Mobile architecture decision record                |
| KS1–KS17        | Kotlin Standards            | Coding standards for Android feature modules       |
| MC1–MC12        | Mobile Standards            | Platform-specific guidelines (iOS & Android)       |

**Key alignment points:**

- The Mobile BFF calls the same microservices (MS1–MS12) as the Web BFF (MF5),
  but shapes responses differently for mobile screens.
- Design system tokens in `:core:ui` (MM7) should align with web design tokens
  (MF7) to maintain brand consistency across platforms.
- Authentication flow (MM9) follows the same OAuth2 grant as the web app (MF9)
  but adds biometric unlock and device-bound tokens.
- Offline sync (MM10) has no web equivalent — it is mobile-specific.
- Module dependency rules (MM4) mirror the web micro-frontend isolation rules
  (MF4) adapted for Gradle/Swift Package Manager.
