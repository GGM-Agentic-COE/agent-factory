# UI Coding Standards (L0 — Framework-Agnostic)

These standards apply to all frontend projects regardless of framework. Every UI component, page, and feature MUST comply.

---

## UC1: Component Architecture

- Follow **Atomic Design** hierarchy:
  - **Atoms** — smallest UI elements (Button, Input, Label, Icon)
  - **Molecules** — groups of atoms functioning together (SearchBar = Input + Button)
  - **Organisms** — complex sections composed of molecules (Header, ProductCard grid)
  - **Templates** — page-level layouts defining content structure
  - **Pages** — templates populated with real data
- Each component MUST have a **single responsibility**. If a component does more than one thing, split it.
- Define an explicit **props interface** (TypeScript interface, PropTypes, or equivalent) for every component.
- Prefer **composition over inheritance** — build complex UI by combining smaller components, never extend component classes.
- A component MUST NOT directly fetch data AND render UI. Separate data-fetching containers from presentational components.
- Co-locate component files: component, styles, tests, and types in the same directory.

---

## UC2: State Management

- **Decision matrix** for state placement:
  | Scope | Where to store |
  |---|---|
  | Single component only | Local state |
  | Parent + 1 child | Props (pass down) |
  | Parent + 2+ nested children | Context / store (no prop drilling beyond 2 levels) |
  | Multiple unrelated components | Global store |
  | Server-fetched data | Server state cache (e.g., query cache) |
- **Derived state** MUST be computed from source state, never stored separately.
- Never duplicate state — single source of truth for every piece of data.
- Keep global store minimal: only truly shared state belongs there.
- Side effects (API calls, timers) MUST be isolated in dedicated hooks/composables, not embedded in render logic.

---

## UC3: Accessibility (WCAG 2.1 AA)

- Use **semantic HTML** elements (`<nav>`, `<main>`, `<article>`, `<button>`, `<table>`) — never `<div>` for interactive elements.
- Apply correct **ARIA roles** only when no native semantic element exists. Prefer native elements over ARIA.
- All interactive elements MUST be **keyboard navigable** (Tab, Enter, Escape, Arrow keys where appropriate).
- Manage **focus** explicitly: trap focus in modals, restore focus on close, auto-focus first field in forms.
- **Color contrast** MUST meet 4.5:1 ratio for normal text, 3:1 for large text (18px+ bold or 24px+).
- Run **screen reader testing** (VoiceOver, NVDA) on all critical flows before release.
- **Touch targets** MUST be at least 48×48px with adequate spacing.
- Every `<img>` MUST have meaningful **alt text** (or `alt=""` for decorative images).
- Every form input MUST have an associated **`<label>`** element (visible or `aria-label`).
- Do not rely on color alone to convey information — use icons, text, or patterns as secondary indicators.

---

## UC4: Responsive Design

- **Mobile-first** approach: base styles target smallest screens, use `min-width` media queries to scale up.
- Standard **breakpoints**:
  | Name | Width |
  |---|---|
  | Mobile | 320px |
  | Tablet | 768px |
  | Desktop | 1024px |
  | Wide | 1440px |
- Use **fluid typography** (clamp or viewport-relative units) — text must scale smoothly between breakpoints.
- **No horizontal scroll** at any breakpoint. Test at every breakpoint boundary.
- Interactive elements MUST be **touch-friendly**: minimum 48px tap targets, adequate spacing between tappable items.
- Images and media MUST be responsive (`max-width: 100%`, appropriate `srcset`).
- Test on real devices, not just browser resize.

---

## UC5: Error / Loading / Empty States

- Every data-fetching component MUST handle exactly three states:
  1. **Loading** — show skeleton placeholders matching the layout shape. Never use bare spinners for content areas.
  2. **Error** — display a clear error message with a **retry** action. Include error context when safe to expose.
  3. **Empty** — show a helpful message explaining why there's no data and a call-to-action when applicable.
- Use **optimistic updates** for user-initiated mutations (create, update, delete) — update UI immediately, roll back on failure.
- Loading skeletons MUST match the dimensions of the content they replace to prevent layout shift.
- Error boundaries MUST exist at route level to catch unexpected render failures.

---

## UC6: Design System Compliance

- Use **design tokens** for all visual properties:
  - Colors: `token.color.primary`, `token.color.error`, etc.
  - Spacing: `token.space.sm`, `token.space.md`, `token.space.lg`
  - Typography: `token.font.body`, `token.font.heading`
  - Border radii: `token.radius.sm`, `token.radius.md`
- **No hardcoded values** — never write raw hex colors, pixel spacing, or font stacks directly in component styles.
- Use the shared **component library** for standard UI elements. Only create custom components when the library lacks the pattern.
- Support **light and dark themes** via token switching. Components MUST NOT assume a specific theme.
- All new tokens MUST be added to the design system, not defined locally.

---

## UC7: Performance

- **Lazy load** all route-level components — only the current route's code ships on initial load.
- Apply **code splitting** at route boundaries and for heavy third-party libraries.
- **Image optimization**: use modern formats (WebP/AVIF), responsive `srcset`, lazy loading for below-fold images.
- **Memoize** expensive computations and components that receive stable props to avoid unnecessary re-renders.
- **Bundle size budget**: initial JavaScript payload MUST be under **200KB** (gzipped). CI MUST fail if exceeded.
- Avoid importing entire libraries when only a few functions are needed — use tree-shakeable imports.
- Measure and track **Core Web Vitals** (LCP < 2.5s, FID < 100ms, CLS < 0.1).

---

## UC8: Testing Standards

- **Unit tests** — every component MUST have tests covering:
  - Correct rendering with default and edge-case props
  - User interactions (click, type, submit)
  - State changes and conditional rendering
- **Integration tests** — cover full page flows:
  - Navigation between routes
  - API calls with mocked responses (success, error, empty)
  - Form submission end-to-end
- **Accessibility tests** — run **axe-core** (or equivalent) automated checks in CI on every component.
- **Visual regression** — screenshot comparison tests for critical UI components. Failures require manual review.
- Code **coverage ≥ 80%** for all UI packages. CI MUST enforce this threshold.
- Tests MUST NOT depend on implementation details (internal state, CSS classes) — test behavior and output.

---

## UC9: Routing

- Define routes **declaratively** in a central route configuration file.
- **Protected routes** MUST use an auth guard that redirects unauthenticated users to login.
- Provide a **404 page** for unmatched routes with navigation back to a known page.
- Support **deep linking** — every meaningful view MUST have a unique, shareable URL.
- Implement **breadcrumbs** for navigation depth > 2 levels, derived from the route hierarchy.
- Route changes MUST update the document `<title>` and announce navigation to screen readers.
- Preserve scroll position on back navigation; scroll to top on forward navigation.

---

## UC10: API Integration

- Use a **centralized API client** — all HTTP requests go through a single configured instance.
- Implement **request interceptors** for: auth token injection, correlation ID header (`X-Correlation-ID`), content-type defaults.
- Implement **response interceptors** for: 401 → redirect to login, 5xx → generic error handling, response normalization.
- Every API call MUST propagate a **correlation ID** for end-to-end tracing.
- Apply a **caching strategy**: cache GET responses with appropriate TTL, invalidate on mutations.
- API error responses MUST be mapped to user-friendly messages — never show raw server errors.
- Centralize base URL and timeout configuration via environment variables.

---

## UC11: Security

- **XSS prevention**: never inject unsanitized HTML. Avoid framework equivalents of `dangerouslySetInnerHTML` unless content is sanitized with a trusted library.
- Include **CSRF tokens** in all state-changing requests (POST, PUT, DELETE).
- Configure **Content Security Policy (CSP)** headers to restrict script sources, disallow `unsafe-inline` in production.
- **No secrets in client code** — API keys, tokens, and credentials MUST NOT appear in frontend bundles. Use backend proxies.
- **Sanitize all user input** before rendering or sending to APIs. Validate on both client and server.
- Use **secure cookie settings**: `HttpOnly`, `Secure`, `SameSite=Strict` for auth cookies.
- Avoid storing sensitive data in `localStorage` — prefer `httpOnly` cookies or in-memory storage.

---

## UC12: Code Quality

- **File naming conventions**:
  - Components: `PascalCase` (e.g., `UserProfile.tsx`, `SearchBar.vue`)
  - Utilities/hooks: `camelCase` (e.g., `useAuth.ts`, `formatDate.ts`)
  - Constants: `UPPER_SNAKE_CASE` for exported constants
- **Max component size**: 200 lines. If exceeded, extract logic into hooks/composables and split sub-components.
- Extract reusable logic into **custom hooks/composables** — components should primarily describe UI.
- **No inline styles** — use design tokens via CSS modules, styled-components, or equivalent. Exception: truly dynamic values computed at runtime.
- **ESLint + Prettier** (or equivalent linter/formatter) MUST be configured and enforced in CI. No warnings allowed in main branch.
- Imports MUST be organized: external libraries → internal modules → relative imports, separated by blank lines.
- Dead code, commented-out code, and `console.log` statements MUST NOT exist in production branches.

---

## Cross-References to Enterprise Architecture

| UC Section | EA/MS Reference | Alignment |
|-----------|----------------|-----------|
| UC1 Component Architecture | EA11 Design System (atomic design hierarchy) | Atoms→molecules→organisms→templates→pages |
| UC2 State Management | EA10 Mobile Architecture (StateFlow pattern) | Local vs global state decision |
| UC3 Accessibility | EA7 NFRs (WCAG 2.1 AA mandatory) | 48px touch targets, TalkBack, contrast 4.5:1 |
| UC4 Responsive Design | EA11 Design System (breakpoints, spacing) | Mobile-first, 4dp grid |
| UC5 Error/Loading/Empty | EA2 Architecture Patterns (error handling) | Result pattern, user-friendly messages |
| UC6 Design System | EA11 Design System (tokens, theming) | Colors, typography, spacing, radii from tokens |
| UC7 Performance | EA7 NFRs (app cold start <2s, p95 <500ms) | Bundle budget, lazy loading, Core Web Vitals |
| UC8 Testing | EA14 Testing Standards (test pyramid, 80% coverage) | Unit, integration, accessibility, visual |
| UC9 Routing | EA10 Mobile Architecture (Navigation Compose) | Declarative routes, deep linking |
| UC10 API Integration | EA3 API Standards (correlation ID, error format) | Centralized client, RFC 7807 error handling |
| UC11 Security | EA5 Security (XSS, CSRF, CSP, no secrets) | No client secrets, sanitize input |
| UC12 Code Quality | EA13 Code Standards (naming, complexity, docs) | ESLint + Prettier, max component 200 lines |
