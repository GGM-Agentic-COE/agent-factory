# Micro-Frontend with BFF Pattern

> Knowledge Base: kb-L1-microfrontend-bff | Layer: L1 | Status: Active

---

## MF1: Core Principles

Micro-frontends extend microservice principles to the frontend. Each vertical slice is owned
end-to-end by a single team — from UI to BFF to data store.

### Principles

1. **Independent Deployment Per Team** — each micro-frontend (MFE) is built, tested, and
   deployed on its own release cadence. No coordination with other teams required for shipping.

2. **Technology Agnostic Per Micro-Frontend** — Team A can use React, Team B can use Vue,
   Team C can use Svelte. The composition layer does not dictate framework choice. In practice,
   standardizing on one framework reduces overhead; the principle preserves the *option*.

3. **Shared Nothing (No Shared State)** — MFEs do not share runtime state. No global Redux
   store, no shared context providers spanning MFE boundaries. Each MFE owns its own state
   tree entirely. Communication happens through explicit, loosely-coupled channels only.

4. **Composition at Runtime** — MFEs are integrated in the browser (or at the edge), not at
   build time. This enables independent deployment. Build-time integration creates a distributed
   monolith — avoid it.

5. **BFF Per Frontend** — each MFE (or team) has its own Backend-for-Frontend service. The BFF
   aggregates downstream microservice calls and shapes data specifically for that frontend's
   needs. No shared BFF across teams.

### Why These Principles Matter

| Violation                     | Consequence                                      |
|-------------------------------|--------------------------------------------------|
| Shared state between MFEs    | Tight coupling, coordinated deployments required |
| Build-time integration        | Distributed monolith, no independent deployment  |
| Single BFF for all frontends | Bottleneck team, deployment coupling              |
| Mandated single framework    | Limits team autonomy, harder to migrate           |

---

## MF2: Architecture Overview

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                          Browser                                │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                      App Shell                            │  │
│  │  ┌─────────┐  ┌──────────┐  ┌─────────────┐              │  │
│  │  │ Routing  │  │  Auth    │  │ Shared Chrome│              │  │
│  │  │ Engine   │  │  Module  │  │ (Nav/Footer) │              │  │
│  │  └─────────┘  └──────────┘  └─────────────┘              │  │
│  │                                                           │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐                │  │
│  │  │  MFE-A   │  │  MFE-B   │  │  MFE-C   │                │  │
│  │  │ (Orders) │  │ (Catalog)│  │ (Account)│                │  │
│  │  └────┬─────┘  └────┬─────┘  └────┬─────┘                │  │
│  └───────┼──────────────┼─────────────┼──────────────────────┘  │
└──────────┼──────────────┼─────────────┼─────────────────────────┘
           │              │             │
     ┌─────▼─────┐ ┌─────▼─────┐ ┌─────▼─────┐
     │  BFF-A    │ │  BFF-B    │ │  BFF-C    │
     │ (Orders)  │ │ (Catalog) │ │ (Account) │
     └─────┬─────┘ └─────┬─────┘ └─────┬─────┘
           │              │             │
     ┌─────▼──────────────▼─────────────▼─────┐
     │         Downstream Microservices        │
     │  ┌─────────┐ ┌──────┐ ┌────────────┐   │
     │  │ Order   │ │ Inv. │ │ User Svc   │   │
     │  │ Service │ │ Svc  │ │            │   │
     │  └─────────┘ └──────┘ └────────────┘   │
     └─────────────────────────────────────────┘
```

### App Shell Responsibilities

- **Routing**: top-level route resolution, delegates sub-routes to MFEs
- **Authentication**: login flow, token acquisition, token refresh
- **Shared Chrome**: navigation bar, footer, notification area
- **MFE Loading**: dynamically loads MFE bundles based on route
- **Error Boundaries**: catches MFE load/render failures, shows fallback UI

### What the App Shell Does NOT Do

- Business logic — that belongs in MFEs
- API calls to downstream services — that belongs in BFFs
- State management for MFE data — each MFE owns its state

---

## MF3: Composition Patterns

### Pattern Comparison

| Pattern              | Runtime? | Framework Agnostic? | DX    | Performance | Recommended |
|----------------------|----------|---------------------|-------|-------------|-------------|
| Module Federation    | Yes      | Partial             | High  | High        | ✅ Yes       |
| Web Components       | Yes      | Yes                 | Med   | High        | Conditional |
| iframe               | Yes      | Yes                 | Low   | Low         | Legacy only |
| Server-Side (SSI/ESI)| Yes     | Yes                 | Low   | Med         | Edge cases  |

### Module Federation (Webpack 5 / Vite)

The recommended approach for React-based micro-frontends. Allows sharing dependencies at
runtime, lazy-loading remote modules, and type-safe contracts between host and remotes.

- Webpack 5: native `ModuleFederationPlugin`
- Vite: `@originjs/vite-plugin-federation`

### Web Components

Useful when MFEs use different frameworks. Each MFE registers a custom element. The App Shell
renders `<mfe-orders></mfe-orders>`. Drawback: React integration with Web Components has
friction (event handling, props vs attributes).

### iframe (Legacy)

Full isolation but poor UX — no shared routing, no shared styling, performance overhead.
Use only for embedding legacy applications during migration.

### Server-Side Composition (SSI/ESI)

Fragments assembled at the CDN/edge layer. Good for content-heavy pages. Not suitable for
highly interactive SPAs. Consider for marketing pages or CMS-driven content.

### Decision Matrix

- React-only teams → **Module Federation**
- Mixed frameworks → **Web Components**
- Legacy embedding → **iframe**
- Content-heavy, low interactivity → **SSI/ESI**

---

## MF4: Module Federation Config

### Host Configuration (App Shell)

```js
// app-shell/vite.config.js
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'appShell',
      remotes: {
        mfeOrders: 'http://localhost:3001/assets/remoteEntry.js',
        mfeCatalog: 'http://localhost:3002/assets/remoteEntry.js',
        mfeAccount: 'http://localhost:3003/assets/remoteEntry.js',
      },
      shared: ['react', 'react-dom', 'react-router-dom'],
    }),
  ],
});
```

### Remote Configuration (MFE)

```js
// mfe-orders/vite.config.js
import federation from '@originjs/vite-plugin-federation';

export default defineConfig({
  plugins: [
    react(),
    federation({
      name: 'mfeOrders',
      filename: 'remoteEntry.js',
      exposes: {
        './OrdersPage': './src/pages/OrdersPage',
        './OrderDetail': './src/pages/OrderDetail',
      },
      shared: ['react', 'react-dom', 'react-router-dom'],
    }),
  ],
});
```

### Shared Dependency Rules

- `react` and `react-dom` — **singleton: true, requiredVersion** pinned. Multiple React
  instances cause hooks to break.
- `react-router-dom` — singleton to share browser history.
- Design system package — shared but **not** singleton (allows version drift during rollout).

### Consuming a Remote Module

```tsx
// In App Shell
const OrdersPage = React.lazy(() => import('mfeOrders/OrdersPage'));

function App() {
  return (
    <Suspense fallback={<Skeleton />}>
      <Routes>
        <Route path="/orders/*" element={<OrdersPage />} />
      </Routes>
    </Suspense>
  );
}
```

---

## MF5: BFF Pattern

### What Is a BFF?

A Backend-for-Frontend is a server-side component that exists solely to serve one frontend
(or one team's set of frontends). It sits between the frontend and downstream microservices.

### BFF Responsibilities

1. **Aggregate** — combine data from multiple microservices into a single response shaped
   for the UI. One BFF call replaces N microservice calls from the browser.
2. **Transform** — reshape microservice responses into the exact structure the UI components
   expect. The frontend should not need to transform API data.
3. **Auth Token Exchange** — accept the user's JWT, exchange it for service-to-service tokens
   when calling downstream services. The browser never sees internal service tokens.
4. **Cache UI-Specific Data** — cache aggregated/transformed responses. Cache keys are
   UI-oriented (e.g., "dashboard summary for user X"), not microservice-oriented.
5. **Absorb Backend Complexity** — shield the frontend from microservice versioning, protocol
   differences (gRPC vs REST), and service discovery.

### BFF Is NOT

- ❌ A general-purpose API gateway (that's a separate concern — see MS4)
- ❌ A place for business logic (that belongs in microservices)
- ❌ A shared service consumed by multiple frontends (one BFF per frontend/team)
- ❌ A proxy that passes through microservice responses unchanged

### BFF Per Team Mapping

| Team     | Frontend | BFF         | Downstream Services              |
|----------|----------|-------------|----------------------------------|
| Orders   | MFE-A    | bff-orders  | order-svc, payment-svc, inv-svc  |
| Catalog  | MFE-B    | bff-catalog | product-svc, search-svc, inv-svc |
| Account  | MFE-C    | bff-account | user-svc, auth-svc, notif-svc    |

---

## MF6: BFF Implementation

### Technology Choice

- **Node.js/Express** — natural fit when frontend team owns the BFF (same language).
- **.NET Minimal API** — when the organization standardizes on .NET for backend services.
- **GraphQL** — optional layer on top of REST BFF for complex aggregation scenarios where
  the frontend needs flexible queries.

### Route Design Principle

BFF routes mirror **frontend needs**, not microservice structure:

```
# Good — routes match UI views
GET  /api/dashboard/summary       → aggregates order-svc + inv-svc + user-svc
GET  /api/orders/:id/details      → aggregates order-svc + payment-svc
POST /api/orders/:id/cancel       → orchestrates order-svc + payment-svc + notif-svc

# Bad — routes mirror microservices (just a proxy)
GET  /api/order-service/orders/:id
GET  /api/payment-service/payments?orderId=:id
GET  /api/inventory-service/stock?productId=:id
```

### Circuit Breaker on Downstream Calls

```ts
// bff-orders/src/clients/orderServiceClient.ts
import CircuitBreaker from 'opossum';

const breaker = new CircuitBreaker(callOrderService, {
  timeout: 3000,
  errorThresholdPercentage: 50,
  resetTimeout: 10000,
});

breaker.fallback(() => ({ orders: [], source: 'fallback' }));
```

### Correlation ID Propagation

Every request entering the BFF gets a correlation ID. This ID is forwarded to all downstream
calls for distributed tracing:

```ts
app.use((req, res, next) => {
  req.correlationId = req.headers['x-correlation-id'] || crypto.randomUUID();
  res.setHeader('x-correlation-id', req.correlationId);
  next();
});
```

---

## MF7: Shared Design System

### Package Structure

```
@org/design-system
├── src/
│   ├── atoms/          # Button, Input, Icon, Badge, Spinner
│   ├── molecules/      # SearchBar, FormField, Card, Modal
│   ├── tokens/         # CSS variables, spacing, typography
│   └── index.ts        # Tree-shakeable named exports
├── package.json
└── tsconfig.json
```

### Rules

1. **Atoms and molecules only** — no business components. A `<Button>` is a design system
   component. An `<OrderSummaryCard>` is a business component and belongs in the MFE.
2. **Versioned independently** — published to npm (private registry). MFEs pin to a version
   range. Breaking changes require a major version bump.
3. **CSS variables for theming** — all colors, spacing, and typography use CSS custom
   properties. MFEs can override theme tokens without forking the package.
4. **Tree-shakeable** — use named exports, no barrel files that defeat tree-shaking.
   Each atom/molecule is independently importable.

### Consumption

```tsx
import { Button, Modal } from '@org/design-system';
import '@org/design-system/tokens.css';
```

### Theming via CSS Variables

```css
/* design-system/tokens.css */
:root {
  --ds-color-primary: #0066cc;
  --ds-color-surface: #ffffff;
  --ds-spacing-md: 16px;
  --ds-font-body: 'Inter', sans-serif;
}

/* MFE override for dark theme */
[data-theme="dark"] {
  --ds-color-primary: #4da6ff;
  --ds-color-surface: #1a1a2e;
}
```

---

## MF8: Shared Authentication

### Flow

1. User navigates to app → App Shell checks for valid token in memory.
2. No token → App Shell redirects to IdP (OAuth2/OIDC authorization code flow with PKCE).
3. IdP returns authorization code → App Shell exchanges for tokens.
4. App Shell stores tokens **in memory only** (not localStorage, not sessionStorage).
5. App Shell passes access token to MFEs via custom event or shared auth context.
6. Each MFE attaches token to BFF requests via `Authorization` header.
7. Each BFF validates the JWT independently (verify signature, check expiry, check audience).
8. Token refresh: App Shell handles silently via iframe or refresh token rotation.

### Token Distribution to MFEs

```ts
// App Shell — dispatch token to MFEs
window.dispatchEvent(new CustomEvent('auth:token', {
  detail: { accessToken: token },
}));

// MFE — listen for token
window.addEventListener('auth:token', (e: CustomEvent) => {
  httpClient.setAuthHeader(`Bearer ${e.detail.accessToken}`);
});
```

### Why Not localStorage?

- XSS vulnerability: any script on the page can read localStorage.
- Memory-only tokens are cleared on tab close (acceptable for most apps).
- If persistence is needed, use `httpOnly` cookies set by the BFF (not accessible to JS).

### BFF JWT Validation

Each BFF validates independently — do not trust that "the App Shell already validated":

```ts
import { expressjwt } from 'express-jwt';
import jwksRsa from 'jwks-rsa';

app.use(expressjwt({
  secret: jwksRsa.expressJwtSecret({
    jwksUri: `${ISSUER}/.well-known/jwks.json`,
  }),
  audience: 'bff-orders',
  issuer: ISSUER,
  algorithms: ['RS256'],
}));
```

---

## MF9: Routing

### Routing Ownership

- **App Shell** owns top-level routes: `/orders/*`, `/catalog/*`, `/account/*`
- **MFE** owns sub-routes within its mount point: `/orders/`, `/orders/:id`, `/orders/:id/edit`

### App Shell Router

```tsx
function AppShell() {
  return (
    <BrowserRouter>
      <NavBar />
      <Suspense fallback={<PageSkeleton />}>
        <Routes>
          <Route path="/orders/*" element={<MfeOrders />} />
          <Route path="/catalog/*" element={<MfeCatalog />} />
          <Route path="/account/*" element={<MfeAccount />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
```

### MFE Internal Router

```tsx
// Inside MFE-Orders (mounted at /orders/*)
function OrdersApp() {
  return (
    <Routes>
      <Route index element={<OrderList />} />
      <Route path=":id" element={<OrderDetail />} />
      <Route path=":id/edit" element={<OrderEdit />} />
    </Routes>
  );
}
```

### Deep Linking

Deep links like `/orders/abc-123` work because:
1. App Shell matches `/orders/*` → loads MFE-Orders
2. MFE-Orders matches `:id` → renders OrderDetail with id `abc-123`

### 404 Handling

- Unknown top-level path → App Shell renders `<NotFound />`
- Unknown sub-path within MFE → MFE can render its own 404 or bubble up to App Shell

---

## MF10: Communication Between MFEs

### Allowed Patterns (Ranked)

1. **Custom Events** (preferred) — loosely coupled, native browser API, no shared dependencies.
2. **Shared Event Bus** (pub/sub) — thin library exposed by App Shell for typed events.
3. **URL Parameters** — for navigation-related state (e.g., selected filters in query string).

### Custom Events Example

```ts
// MFE-Orders: dispatch event when order is placed
window.dispatchEvent(new CustomEvent('order:placed', {
  detail: { orderId: '123', total: 59.99 },
}));

// MFE-Account: listen for order events to update notification badge
window.addEventListener('order:placed', (e: CustomEvent) => {
  incrementNotificationCount();
});
```

### Event Bus (Typed)

```ts
// Exposed by App Shell as shared module
type EventMap = {
  'order:placed': { orderId: string; total: number };
  'cart:updated': { itemCount: number };
  'user:logout': void;
};

const eventBus = createTypedEventBus<EventMap>();
export { eventBus };
```

### Forbidden Patterns

- ❌ **Shared global state** (Redux store, global context) — creates tight coupling.
- ❌ **Direct imports** between MFEs — creates build-time dependency.
- ❌ **Synchronous function calls** between MFEs — breaks independent deployment.
- ❌ **Shared service instances** — each MFE must instantiate its own services.

---

## MF11: Testing Strategy

### Per-MFE Testing (Owned by MFE Team)

| Level        | Tool                  | Scope                                    |
|--------------|-----------------------|------------------------------------------|
| Unit         | Vitest / Jest         | Components, hooks, utilities             |
| Integration  | Testing Library       | Page-level flows within the MFE          |
| Accessibility| axe-core / jest-axe   | WCAG 2.1 AA compliance per component     |
| Visual       | Chromatic / Percy     | Screenshot regression for design system  |

### Contract Tests (MFE ↔ BFF)

Each MFE team writes contract tests that verify the BFF API shape:

```ts
// mfe-orders/tests/contracts/bff-orders.contract.test.ts
describe('BFF Orders Contract', () => {
  it('GET /api/orders returns expected shape', async () => {
    const res = await fetch(`${BFF_URL}/api/orders`);
    const data = await res.json();
    expect(data).toMatchSchema(ordersResponseSchema);
  });
});
```

Use Pact or schema-based validation. The BFF team runs provider verification.

### Composition Tests (App Shell + MFEs)

Integration tests that verify MFEs load correctly within the App Shell:

- App Shell renders, MFE remote loads without error
- Routing delegates correctly to MFE
- Auth token is received by MFE
- Shared chrome (nav, footer) renders alongside MFE content

Run in CI with Playwright or Cypress against a deployed staging environment.

### Rule: No Cross-MFE Test Dependencies

Tests for MFE-A must never import from or assert on MFE-B. If MFE-A dispatches an event
and MFE-B consumes it, test each side independently:
- MFE-A test: verify event is dispatched with correct payload
- MFE-B test: simulate receiving the event, verify behavior

---

## MF12: Deployment

### Independent Deployment Model

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│  App Shell   │  │   MFE-A      │  │   MFE-B      │  │   MFE-C      │
│  CI/CD       │  │   CI/CD      │  │   CI/CD      │  │   CI/CD      │
│  Pipeline    │  │   Pipeline   │  │   Pipeline   │  │   Pipeline   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
       │                 │                 │                 │
       ▼                 ▼                 ▼                 ▼
   S3/CDN            S3/CDN           S3/CDN            S3/CDN
   (shell)           (mfe-a)          (mfe-b)           (mfe-c)
```

### Deployment Rules

1. **Each MFE deployed independently** — own CI/CD pipeline, own S3 bucket or CDN path.
2. **App Shell deployed separately** — changes to shell are rare and high-impact; gate with
   extra approval.
3. **BFFs deployed as microservices** — containerized, own ECS/EKS service, own scaling policy.
4. **Feature flags per MFE** — use LaunchDarkly or similar to toggle MFE features without
   redeployment. App Shell can feature-flag entire MFE loading.
5. **Canary deployment per MFE** — route a percentage of traffic to the new MFE version.
   Monitor error rates before full rollout.
6. **Design system versioned via npm** — MFEs update on their own schedule. No forced
   simultaneous upgrades.

### Versioning Strategy

- MFE bundles are deployed to versioned paths: `/mfe-orders/v2.3.1/remoteEntry.js`
- App Shell config maps MFE names to current version URLs
- Rollback = update App Shell config to point to previous version

---

## MF13: Anti-Patterns

### ❌ Shared State Between MFEs

**Problem**: MFE-A and MFE-B both read/write to a shared Redux store or global variable.
**Consequence**: Changes in MFE-A's state shape break MFE-B. Coordinated deployments required.
**Fix**: Use custom events for communication. Each MFE owns its own state.

### ❌ MFE Calling Another MFE's BFF Directly

**Problem**: MFE-A calls `bff-catalog` to get product data instead of going through `bff-orders`.
**Consequence**: MFE-A is now coupled to BFF-B's API contract. Team B can't change their BFF
without coordinating with Team A.
**Fix**: BFF-A should call the product microservice directly, or MFEs communicate via events.

### ❌ Monolithic BFF Serving All Frontends

**Problem**: A single BFF serves MFE-A, MFE-B, and MFE-C.
**Consequence**: Defeats the purpose of micro-frontends. The BFF becomes a bottleneck owned
by no single team. Changes require cross-team coordination.
**Fix**: One BFF per frontend/team. Each team owns their full vertical slice.

### ❌ Shared Business Components Across MFEs

**Problem**: `<OrderSummaryCard>` is published as a shared package used by MFE-A and MFE-C.
**Consequence**: Changes to the component require coordinated releases. Business logic leaks
across team boundaries.
**Fix**: Only share design system primitives (atoms/molecules). Duplicate business components
if needed — duplication is cheaper than coupling.

### ❌ Synchronous MFE-to-MFE Communication

**Problem**: MFE-A imports a function from MFE-B and calls it directly.
**Consequence**: Build-time dependency. MFE-A cannot be deployed without MFE-B. Breaks
independent deployment principle.
**Fix**: Use async custom events. If MFE-A needs data from MFE-B's domain, MFE-A's BFF
should call the relevant microservice.

---

## MF14: Cross-References

### Microservices (MS1-MS12)

- **MS1**: Service decomposition — same bounded context principles apply to MFE boundaries
- **MS2**: Inter-service communication — BFF-to-microservice patterns
- **MS3**: Data management — each MFE/BFF pair owns its data access
- **MS4**: API Gateway vs BFF — critical distinction; API Gateway is infrastructure, BFF is
  application-level per-frontend aggregation
- **MS5**: Service discovery — BFFs need to discover downstream services
- **MS6-MS12**: Resilience, observability, security patterns apply to BFFs

### Enterprise Architecture (EA)

- **EA2**: Architecture patterns — micro-frontend is a frontend architecture pattern that
  complements microservices on the backend
- **EA6**: Deployment — MFE deployment aligns with microservice deployment principles
  (independent, automated, observable)

### UI Component Standards (UC1-UC12)

- **UC1-UC4**: Component design principles apply within each MFE
- **UC5-UC8**: Accessibility standards — each MFE must independently meet WCAG 2.1 AA
- **UC9-UC12**: Design tokens and theming — consumed from the shared design system

### React Standards (RS1-RS17)

- **RS1-RS5**: Component patterns — apply within each React-based MFE
- **RS6-RS10**: State management — scoped to individual MFE, never shared across boundaries
- **RS11-RS14**: Performance — lazy loading, code splitting per MFE
- **RS15-RS17**: Testing — per-MFE testing strategy aligns with React testing best practices
