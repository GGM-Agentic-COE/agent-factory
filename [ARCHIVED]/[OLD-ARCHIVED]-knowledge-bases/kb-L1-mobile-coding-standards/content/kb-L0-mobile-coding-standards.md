# Mobile Coding Standards (L0)

Platform-agnostic standards for Android (Kotlin/Compose) and iOS (Swift/SwiftUI) development.
All mobile projects MUST comply with sections MC1–MC12.

---

## MC1: Architecture

- MVVM is the mandatory architecture pattern for all mobile projects.
- ViewModel exposes UI state via `StateFlow` (Android) or `@Published`/Combine (iOS).
- Legacy Android projects MAY use `LiveData`; new code MUST use `StateFlow`.
- View layer observes state reactively — no imperative state polling.
- Repository pattern is required for all data access (local + remote).
- Repositories abstract data sources; ViewModels MUST NOT call APIs or DAOs directly.
- UseCase (interactor) classes encapsulate business logic; one public `invoke()` per UseCase.
- UseCases MUST be stateless; any required state lives in the Repository or ViewModel.
- Dependency injection is mandatory for all dependencies (Hilt on Android, Swift DI container on iOS).
- All injectable types MUST be coded to interfaces, not concrete implementations.
- Layer dependency direction: View → ViewModel → UseCase → Repository → DataSource.
- No circular dependencies between layers.
- Feature modules SHOULD define their own DI module/container scoped to the feature lifecycle.

## MC2: State Management

- UI state MUST be modeled as a sealed class/interface with explicit variants:
  - `Loading` — initial or refresh state.
  - `Success(data: T)` — data ready for display.
  - `Error(message: String, retry: (() -> Unit)?)` — recoverable failure.
- Unidirectional data flow: events flow up (View → ViewModel), state flows down (ViewModel → View).
- Single source of truth: ViewModel holds the canonical UI state; View renders it.
- View layer MUST NOT hold mutable state beyond transient UI concerns (e.g., scroll position).
- State updates MUST occur on the main/UI dispatcher.
- Derived state SHOULD use `map`/`combine` operators rather than manual recomputation.
- Side effects (navigation, toasts) modeled as one-shot events via `Channel`/`SharedFlow` or Swift `AsyncStream`.
- ViewModel MUST expose a single `uiState` property; avoid multiple independent state streams per screen.

## MC3: Accessibility

- All screens MUST meet WCAG 2.1 Level AA compliance.
- Minimum touch target size: 48dp (Android) / 44pt (iOS).
- Every interactive element MUST have a content description (`contentDescription` / `accessibilityLabel`).
- Decorative images use `contentDescription = null` / `accessibilityElementsHidden = true`.
- TalkBack (Android) and VoiceOver (iOS) MUST be tested for every screen before merge.
- Screen reader announcements MUST be added for dynamic content changes (e.g., snackbars, loading transitions).
- Dynamic text sizing MUST be supported — no fixed font sizes that break at large scales.
- Layouts MUST reflow gracefully up to 200% text scale without content clipping or overlap.
- Color contrast ratio MUST be ≥ 4.5:1 for normal text, ≥ 3:1 for large text.
- Information MUST NOT be conveyed by color alone — use icons, patterns, or labels as secondary indicators.
- Focus order MUST follow logical reading order; custom `accessibilityTraversalOrder` when needed.
- Accessibility tests MUST be included in the UI test suite (see MC10).

## MC4: Offline-First

- All user-generated content (drafts, forms) MUST be persisted to local DB (Room / Core Data / SwiftData).
- Cached data MUST have explicit TTL; stale indicators shown to user when offline.
- Background sync via `WorkManager` (Android) / `BGTaskScheduler` (iOS) for pending mutations.
- Sync jobs MUST be idempotent and handle conflict resolution (last-write-wins or merge).
- Crash recovery: ViewModel state restored via `SavedStateHandle` (Android) / `@SceneStorage` (iOS).
- Network connectivity MUST be detected reactively (`ConnectivityManager` / `NWPathMonitor`).
- UI MUST display a connectivity banner when the device is offline.
- Optimistic UI updates: reflect user actions immediately, reconcile on sync response.
- Rollback UI state if server rejects an optimistic mutation.
- Offline queue MUST persist across app restarts; retry on connectivity restored.
- Queue processing MUST respect ordering constraints for dependent mutations.

## MC5: Navigation

- Declarative routing is mandatory (Navigation Compose / NavigationStack).
- Deep linking MUST be supported for all top-level destinations; URI scheme registered in manifest/Info.plist.
- Navigation arguments MUST be type-safe — no raw string key/value passing.
- Single Activity (Android) / single Window (iOS) architecture required.
- Each feature module defines its own nested navigation graph.
- Navigation events MUST originate from the ViewModel or a shared navigator — Views do not call navigate directly.
- Back-stack management MUST be predictable; no manual stack manipulation outside the nav framework.
- Modal/bottom-sheet routes use the same navigation system — no ad-hoc dialog management.
- Auth-gated destinations MUST redirect to login and restore the original destination after authentication.

## MC6: Design System

- Design tokens MUST be defined centrally for: colors, typography, spacing, corner radii, elevation.
- Token values sourced from Figma design system; code tokens auto-generated where possible.
- Component library follows atomic design: atoms (Button, Text), molecules (SearchBar), organisms (Card).
- All components MUST support light and dark themes via token switching.
- Every composable/SwiftUI view MUST have an `@Preview` / `#Preview` annotation.
- Previews MUST cover: default state, loading state, error state, dark theme, large font.
- Custom components MUST NOT hard-code colors or dimensions — always reference tokens.
- Spacing uses a 4dp/4pt base grid system.
- Typography scale MUST define semantic names (headlineLarge, bodyMedium, labelSmall) mapped to token values.
- Icon assets MUST be vector-based (XML vector drawable / SF Symbols / SVG) — no raster icons.

## MC7: Networking

- A single, centralized API client instance per base URL (Retrofit+OkHttp / URLSession).
- Auth interceptor MUST inject bearer token from secure storage on every authenticated request.
- Token refresh handled transparently via authenticator/interceptor — no manual refresh in ViewModels.
- Default timeouts: connect 30s, read 30s, write 30s.
- Retry policy: exponential backoff (base 1s, max 3 retries) for 5xx and network errors only.
- 4xx client errors MUST NOT be retried automatically.
- Certificate pinning MUST be enabled for production API endpoints.
- Pinned certificates MUST be rotatable via remote config to avoid bricking on cert rotation.
- Request/response logging enabled in debug builds only; PII MUST NOT appear in logs.
- All API models (DTOs) MUST be separate from domain models; mapping occurs in the Repository layer.
- Pagination MUST use cursor-based or keyset patterns — no offset-based pagination for large datasets.

## MC8: Security

- No secrets, API keys, or credentials in source code — use build-time injection or remote config.
- Auth tokens stored in encrypted storage: Android Keystore / iOS Keychain.
- Biometric authentication MUST be offered for sensitive operations (payments, profile changes).
- Biometric prompt MUST include a fallback to device PIN/password.
- Screenshot prevention: `FLAG_SECURE` (Android) / `UIApplicationDelegate` hiding (iOS) on sensitive screens.
- Root/jailbreak detection MUST be implemented; app MAY degrade functionality on compromised devices.
- Code obfuscation mandatory: ProGuard/R8 (Android), bitcode + symbol stripping (iOS).
- Network security config MUST disallow cleartext traffic in production.
- WebView content MUST be sandboxed; JavaScript injection disabled unless explicitly required.
- Clipboard MUST be cleared after a timeout when sensitive data (OTP, passwords) is copied.
- Session tokens MUST have server-enforced expiry; client MUST handle 401 gracefully.
- All third-party SDKs MUST be reviewed for data collection and privacy compliance before integration.

## MC9: Performance

- App cold start MUST complete in < 2 seconds on mid-range reference devices.
- Lazy loading for lists (LazyColumn / LazyVStack) and feature modules.
- Image loading via caching library: Coil (Android) / Kingfisher (iOS); no manual bitmap handling.
- Images MUST specify explicit size constraints to avoid unnecessary decoding and recomposition.
- Memory leak prevention: no Activity/ViewController references in long-lived objects; use LeakCanary/Instruments.
- Main thread MUST NOT be blocked — all I/O, parsing, and computation on background dispatchers.
- Frame rendering target: 60fps; jank detected via systrace / Instruments.
- Startup profiling MUST be run before each release; regressions block the release.
- Baseline profiles (Android) / pre-compilation hints SHOULD be generated for critical user journeys.
- Large assets (images, animations) MUST be lazy-loaded or streamed.
- App size budget: monitor APK/IPA size per release; increases > 5% require justification.

## MC10: Testing

- Unit tests required for every ViewModel; repositories and data sources mocked.
- Test naming: `fun methodName_givenCondition_expectedResult()`.
- UI tests for every screen: Compose Test Rule (Android) / XCTest + ViewInspector (iOS).
- Accessibility tests: verify content descriptions, touch targets, contrast via automated checks.
- Minimum coverage: 80% line coverage on ViewModel layer; measured per PR in CI.
- Integration tests for Repository layer with fake data sources.
- End-to-end tests for critical user journeys (login, checkout) run nightly in CI.
- Snapshot/screenshot tests for design system components (Paparazzi / Swift Snapshot Testing).
- Flaky tests MUST be quarantined and fixed within one sprint.
- Test doubles (fakes preferred over mocks) MUST live in a shared `testFixtures` / `TestSupport` module.

## MC11: Error Handling

- All fallible operations return `Result<T>` (Kotlin `Result` / Swift `Result<Success, Failure>`).
- Domain-specific error types MUST be defined as sealed classes/enums — no raw exceptions across layer boundaries.
- ViewModel maps `Result` to `UiState.Error` with user-friendly message and optional retry action.
- Raw exception messages MUST NOT be shown to users.
- Network errors categorized: no connectivity, timeout, server error, auth expired — each with distinct UX.
- Crash reporting via Firebase Crashlytics (or equivalent); non-fatal errors logged with context.
- Unhandled exceptions MUST be caught at the coroutine scope / Combine pipeline level.
- Error screens MUST include a retry button that re-triggers the failed operation.
- Validation errors MUST be displayed inline next to the relevant input field.

## MC12: Code Quality

- Naming conventions:
  - Screens/Views: `PascalCase` (e.g., `ProfileScreen`, `ProfileView`).
  - Functions/methods: `camelCase`.
  - Constants: `UPPER_SNAKE_CASE`.
  - Packages/modules: `lowercase` with dot/dash separation.
- Max ViewModel size: 60 lines (excluding imports); extract UseCases to reduce size.
- Max Screen composable/View body: 150 lines; extract sub-components.
- No business logic in the View layer — Views only render state and forward events.
- Linting mandatory: `ktlint` (Android), `SwiftLint` (iOS); CI blocks on lint failures.
- Code formatting enforced via `.editorconfig` / `.swiftlint.yml` checked into repo.
- TODOs MUST include a ticket reference (e.g., `// TODO(PROJ-123): ...`).
- Dead code and unused imports removed before merge.
- PR reviews MUST verify compliance with MC1–MC12 via a checklist.

---

## MC13: Internationalisation & RTL

1. All user-facing strings externalised into resource files (strings.xml / Localizable.strings / .arb)
2. No hardcoded text in code — use string resource references
3. Support RTL layouts (Arabic, Hebrew) — use start/end instead of left/right
4. Date/time displayed in user's locale and timezone, stored as UTC
5. Currency formatted per locale (SAR 1,234.56 vs 1.234,56 SAR)
6. Number formatting locale-aware (decimal separator, grouping)
7. Pluralisation handled via platform plural resources
8. Text expansion: allow 40% extra space for translated strings
9. Test with pseudo-locale to catch hardcoded strings and layout issues

---

## Cross-References

| Standard | Related EA | Relationship |
|----------|-----------|--------------|
| MC1 (Architecture) | EA10 | Mobile architecture patterns and layer separation |
| MC2 (State Management) | EA10 | Unidirectional data flow in mobile apps |
| MC3 (Accessibility) | EA7 | Accessibility compliance and audit standards |
| MC4 (Offline-First) | EA10 | Mobile-specific data and sync architecture |
| MC5 (Navigation) | EA10 | Mobile navigation and routing patterns |
| MC6 (Design System) | EA11 | Design system tokens and component library alignment |
| MC7 (Networking) | EA5 | Secure networking, certificate pinning, PII protection |
| MC8 (Security) | EA5 | Mobile security: storage, obfuscation, device integrity |
| MC9 (Performance) | EA7 | Performance budgets and profiling requirements |
| MC10 (Testing) | EA7, EA10 | Test coverage targets and accessibility test integration |
| MC11 (Error Handling) | EA10 | Error propagation through mobile architecture layers |
| MC12 (Code Quality) | EA10 | Code standards enforcement in mobile codebases |
