# React Coding Standards (kb-L1-react-standards)

> Layer: L1 | Version: 1.0.0 | Status: Active
> Purpose: React + TypeScript standards for UI code generator agents

---

## RS1: Technology Stack

### Core Framework
- **React 18** — concurrent features, automatic batching, Suspense for data fetching
- **TypeScript 5** — strict mode enabled, latest type features

### Build & Dev
- **Vite 5** — dev server and production bundler
- **Vitest** — unit and integration testing (Vite-native)

### Routing & State
- **React Router 6** — file-system-aware routing with `createBrowserRouter`
- **Zustand** (preferred) or **Redux Toolkit** — client-side shared state
- **TanStack Query v5** — server state management, caching, synchronization

### Styling
- **Tailwind CSS** (preferred) — utility-first styling
- **CSS Modules** (alternative) — scoped class names when Tailwind is not viable

### Forms
- **React Hook Form** — performant form state
- **Zod** — schema-based validation

### Quality
- **ESLint** — static analysis with `eslint-plugin-react`, `eslint-plugin-react-hooks`, `@typescript-eslint`
- **Prettier** — code formatting (runs before ESLint)

### Required `tsconfig.json` Baseline
```json
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "noUncheckedIndexedAccess": true,
    "forceConsistentCasingInFileNames": true
  }
}
```

---

## RS2: Project Structure

### Standard Layout
```
src/
├── pages/                  # Route-level page components
│   ├── Dashboard/
│   │   ├── DashboardPage.tsx
│   │   ├── DashboardPage.test.tsx
│   │   └── components/     # Page-specific components
│   └── Settings/
├── components/             # Shared UI components (atomic design)
│   ├── atoms/              # Button, Input, Badge, Icon
│   ├── molecules/          # SearchBar, FormField, Card
│   └── organisms/          # Header, Sidebar, DataTable
├── hooks/                  # Shared custom hooks
│   ├── useAuth.ts
│   ├── useDebounce.ts
│   └── useFetch.ts
├── services/               # API client, external service wrappers
│   ├── apiClient.ts
│   └── authService.ts
├── stores/                 # Zustand stores or Redux slices
│   ├── authStore.ts
│   └── uiStore.ts
├── types/                  # Shared TypeScript types/interfaces
│   ├── api.ts
│   └── models.ts
├── utils/                  # Pure utility functions
│   ├── formatCurrency.ts
│   └── dateHelpers.ts
├── assets/                 # Static assets (images, fonts, icons)
├── styles/                 # Global styles, Tailwind config overrides
│   └── globals.css
├── App.tsx
├── main.tsx
└── router.tsx              # Route definitions
```

### Rules
1. Tests live alongside source files: `Component.tsx` → `Component.test.tsx`
2. Feature-based grouping inside `pages/` — co-locate page-specific components, hooks, types
3. Shared code goes in top-level `components/`, `hooks/`, `utils/`, etc.
4. Index files (`index.ts`) only for barrel exports from `components/` subdirectories
5. Max one component per file; file name matches component name

---

## RS3: Component Pattern

### Rules
1. **Functional components only** — no class components
2. **TypeScript interfaces** for all props (not `type` aliases)
3. **Destructure props** in the function signature
4. **Default export** for page components; **named export** for all other components
5. Declare the interface directly above the component in the same file

### Page Component Example
```tsx
// src/pages/Dashboard/DashboardPage.tsx
import { Suspense } from 'react';
import { DashboardStats } from './components/DashboardStats';
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner';

interface DashboardPageProps {
  title?: string;
}

function DashboardPage({ title = 'Dashboard' }: DashboardPageProps) {
  return (
    <main>
      <h1>{title}</h1>
      <Suspense fallback={<LoadingSpinner />}>
        <DashboardStats />
      </Suspense>
    </main>
  );
}

export default DashboardPage;
```

### Shared Component Example
```tsx
// src/components/atoms/Button.tsx
import { type ButtonHTMLAttributes, type ReactNode } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  children: ReactNode;
}

export function Button({
  variant = 'primary',
  size = 'md',
  isLoading = false,
  children,
  disabled,
  ...rest
}: ButtonProps) {
  return (
    <button
      className={`btn btn-${variant} btn-${size}`}
      disabled={disabled || isLoading}
      aria-busy={isLoading}
      {...rest}
    >
      {isLoading ? <span className="spinner" /> : children}
    </button>
  );
}
```

### Rules for Children
- Use `ReactNode` for arbitrary children
- Use `ReactElement` only when you need to clone/inspect children
- Prefer composition over render props

---

## RS4: Hooks Pattern

### Rules
1. Prefix custom hooks with `use`
2. Each custom hook in its own file under `src/hooks/` (shared) or co-located with feature
3. Always specify dependency arrays explicitly
4. Clean up side effects in `useEffect` return
5. Never call hooks conditionally

### useDebounce Example
```tsx
// src/hooks/useDebounce.ts
import { useEffect, useState } from 'react';

export function useDebounce<T>(value: T, delayMs: number): T {
  const [debounced, setDebounced] = useState(value);

  useEffect(() => {
    const timer = setTimeout(() => setDebounced(value), delayMs);
    return () => clearTimeout(timer);
  }, [value, delayMs]);

  return debounced;
}
```

### useAuth Example
```tsx
// src/hooks/useAuth.ts
import { useAuthStore } from '@/stores/authStore';
import { useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

export function useAuth() {
  const { user, token, setAuth, clearAuth } = useAuthStore();
  const navigate = useNavigate();

  const logout = useCallback(() => {
    clearAuth();
    navigate('/login');
  }, [clearAuth, navigate]);

  return {
    user,
    token,
    isAuthenticated: !!token,
    login: setAuth,
    logout,
  };
}
```

### useEffect Cleanup Pattern
```tsx
useEffect(() => {
  const controller = new AbortController();

  async function fetchData() {
    try {
      const res = await fetch(url, { signal: controller.signal });
      const data = await res.json();
      setData(data);
    } catch (err) {
      if (!controller.signal.aborted) setError(err);
    }
  }

  fetchData();
  return () => controller.abort();
}, [url]);
```

---

## RS5: State Management

### Decision Matrix

| State Type | Tool | When to Use |
|---|---|---|
| Component-local | `useState` / `useReducer` | UI toggles, form inputs, ephemeral state |
| Shared client | Zustand store (or Redux Toolkit slice) | Auth, theme, sidebar state, cross-component UI |
| Server / async | TanStack Query | API data, caching, pagination, polling |
| Form | React Hook Form | Multi-field forms, validation, submission |
| URL | React Router `useSearchParams` | Filters, pagination params, shareable state |

### Zustand Store Example
```tsx
// src/stores/authStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setAuth: (user: User, token: string) => void;
  clearAuth: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setAuth: (user, token) => set({ user, token }),
      clearAuth: () => set({ user: null, token: null }),
    }),
    { name: 'auth-storage' },
  ),
);
```

### Redux Toolkit Slice (Alternative)
```tsx
// src/stores/authSlice.ts
import { createSlice, type PayloadAction } from '@reduxjs/toolkit';

interface AuthState {
  user: User | null;
  token: string | null;
}

const authSlice = createSlice({
  name: 'auth',
  initialState: { user: null, token: null } as AuthState,
  reducers: {
    setAuth(state, action: PayloadAction<{ user: User; token: string }>) {
      state.user = action.payload.user;
      state.token = action.payload.token;
    },
    clearAuth(state) {
      state.user = null;
      state.token = null;
    },
  },
});

export const { setAuth, clearAuth } = authSlice.actions;
export default authSlice.reducer;
```

### Rules
1. Never store server data in Zustand/Redux — use TanStack Query
2. Keep stores small and focused (one concern per store)
3. Derive computed values with selectors, not extra state

---

## RS6: Routing

### Router Setup
```tsx
// src/router.tsx
import { createBrowserRouter, type RouteObject } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import { RootLayout } from '@/components/organisms/RootLayout';
import { ProtectedRoute } from '@/components/organisms/ProtectedRoute';
import { RouteErrorBoundary } from '@/components/organisms/RouteErrorBoundary';
import { LoadingSpinner } from '@/components/atoms/LoadingSpinner';

const DashboardPage = lazy(() => import('@/pages/Dashboard/DashboardPage'));
const SettingsPage = lazy(() => import('@/pages/Settings/SettingsPage'));
const LoginPage = lazy(() => import('@/pages/Login/LoginPage'));

function lazySuspense(Component: React.LazyExoticComponent<React.ComponentType>) {
  return (
    <Suspense fallback={<LoadingSpinner />}>
      <Component />
    </Suspense>
  );
}

const routes: RouteObject[] = [
  {
    path: '/',
    element: <RootLayout />,
    errorElement: <RouteErrorBoundary />,
    children: [
      {
        element: <ProtectedRoute />,
        children: [
          { index: true, element: lazySuspense(DashboardPage) },
          { path: 'settings', element: lazySuspense(SettingsPage) },
        ],
      },
    ],
  },
  { path: '/login', element: lazySuspense(LoginPage) },
];

export const router = createBrowserRouter(routes);
```

### Protected Route Wrapper
```tsx
// src/components/organisms/ProtectedRoute.tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export function ProtectedRoute() {
  const { isAuthenticated } = useAuth();
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
```

### Rules
1. All routes lazy-loaded except the root layout shell
2. Each route group has its own `errorElement`
3. Layout routes use `<Outlet />` for nested content
4. Redirect after login to the original `location.state.from`

---

## RS7: API Integration

### Centralized API Client
```tsx
// src/services/apiClient.ts
const BASE_URL = import.meta.env.VITE_API_BASE_URL ?? '/api';

interface ApiError {
  status: number;
  message: string;
  code?: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const token = localStorage.getItem('auth-storage');
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...(token && { Authorization: `Bearer ${token}` }),
    ...options?.headers,
  };

  const response = await fetch(`${BASE_URL}${path}`, { ...options, headers });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw {
      status: response.status,
      message: body.message ?? response.statusText,
      code: body.code,
    } satisfies ApiError;
  }

  return response.json() as Promise<T>;
}

export const api = {
  get: <T>(path: string) => request<T>(path),
  post: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
  put: <T>(path: string, body: unknown) =>
    request<T>(path, { method: 'PUT', body: JSON.stringify(body) }),
  delete: <T>(path: string) => request<T>(path, { method: 'DELETE' }),
};
```

### TanStack Query Hook Example
```tsx
// src/hooks/useUsers.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { api } from '@/services/apiClient';
import type { User } from '@/types/models';

export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.get<User[]>('/users'),
  });
}

export function useCreateUser() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (newUser: Omit<User, 'id'>) => api.post<User>('/users', newUser),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['users'] });
    },
  });
}
```

### Rules
1. All API calls go through `apiClient.ts` — never call `fetch` directly in components
2. Use TanStack Query for all GET requests (caching, deduplication, refetching)
3. Use `useMutation` for all write operations
4. Invalidate related queries on mutation success
5. Handle errors in `onError` callbacks or via query `error` state

---

## RS8: Styling

### Tailwind CSS (Preferred)
```tsx
export function Card({ title, children }: CardProps) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-6 shadow-sm dark:border-gray-700 dark:bg-gray-800">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">{title}</h3>
      <div className="mt-4">{children}</div>
    </div>
  );
}
```

### CSS Modules (Alternative)
```tsx
// src/components/atoms/Card.module.css
.card {
  border-radius: var(--radius-lg);
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  padding: var(--spacing-6);
}

// src/components/atoms/Card.tsx
import styles from './Card.module.css';

export function Card({ title, children }: CardProps) {
  return (
    <div className={styles.card}>
      <h3>{title}</h3>
      <div>{children}</div>
    </div>
  );
}
```

### Design Tokens (Tailwind Config)
```js
// tailwind.config.js
export default {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        brand: { 50: '#eff6ff', 500: '#3b82f6', 900: '#1e3a8a' },
      },
      spacing: { 18: '4.5rem' },
      borderRadius: { DEFAULT: '0.5rem' },
    },
  },
};
```

### Rules
1. **No inline styles** — use Tailwind classes or CSS Modules
2. Use Tailwind `dark:` variant for dark mode
3. Responsive design with Tailwind breakpoints: `sm:`, `md:`, `lg:`, `xl:`
4. Extract repeated class combinations into component abstractions, not `@apply`
5. Design tokens live in `tailwind.config.js` or CSS custom properties

---

## RS9: Form Handling

### React Hook Form + Zod Example
```tsx
// src/pages/Settings/components/ProfileForm.tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const profileSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  bio: z.string().max(500).optional(),
});

type ProfileFormData = z.infer<typeof profileSchema>;

export function ProfileForm({ onSubmit }: { onSubmit: (data: ProfileFormData) => void }) {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  });

  return (
    <form onSubmit={handleSubmit(onSubmit)} noValidate>
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          aria-describedby={errors.name ? 'name-error' : undefined}
          aria-invalid={!!errors.name}
          {...register('name')}
        />
        {errors.name && (
          <p id="name-error" role="alert">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          type="email"
          aria-describedby={errors.email ? 'email-error' : undefined}
          aria-invalid={!!errors.email}
          {...register('email')}
        />
        {errors.email && (
          <p id="email-error" role="alert">{errors.email.message}</p>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Saving…' : 'Save'}
      </button>
    </form>
  );
}
```

### Rules
1. Always use `zodResolver` for schema validation
2. Every `<input>` must have a `<label>` with matching `htmlFor`/`id`
3. Use `aria-describedby` to link error messages to inputs
4. Use `aria-invalid` on fields with errors
5. Disable submit button during submission (`isSubmitting`)
6. Use `noValidate` on `<form>` to rely on JS validation, not browser defaults

---

## RS10: Error Handling

### Error Boundary Component
```tsx
// src/components/organisms/ErrorBoundary.tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';

interface ErrorBoundaryProps {
  fallback?: ReactNode;
  children: ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  state: ErrorBoundaryState = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('ErrorBoundary caught:', error, info.componentStack);
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <div role="alert">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false, error: null })}>
            Try again
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Route Error Boundary
```tsx
// src/components/organisms/RouteErrorBoundary.tsx
import { useRouteError, isRouteErrorResponse, useNavigate } from 'react-router-dom';

export function RouteErrorBoundary() {
  const error = useRouteError();
  const navigate = useNavigate();

  if (isRouteErrorResponse(error)) {
    return (
      <div role="alert">
        <h1>{error.status} — {error.statusText}</h1>
        <button onClick={() => navigate(-1)}>Go back</button>
      </div>
    );
  }

  return (
    <div role="alert">
      <h1>Unexpected Error</h1>
      <p>Something went wrong. Please try again.</p>
      <button onClick={() => navigate('/')}>Go home</button>
    </div>
  );
}
```

### API Error Handling in Queries
```tsx
export function useUsers() {
  return useQuery({
    queryKey: ['users'],
    queryFn: () => api.get<User[]>('/users'),
    retry: 2,
    meta: { errorMessage: 'Failed to load users' },
  });
}

// Global error handler in QueryClient
const queryClient = new QueryClient({
  queryCache: new QueryCache({
    onError: (error, query) => {
      const message = (query.meta?.errorMessage as string) ?? 'An error occurred';
      toast.error(message);
    },
  }),
});
```

### Rules
1. Wrap every route with an `errorElement`
2. Use `ErrorBoundary` around risky component subtrees
3. Show user-friendly messages — never expose stack traces in production
4. Provide retry/go-back actions in every error UI
5. Log errors to monitoring service in `componentDidCatch` / `onError`

---

## RS11: Testing

### Test File Example
```tsx
// src/components/atoms/Button.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, it, expect, vi } from 'vitest';
import { Button } from './Button';

describe('Button', () => {
  it('should render children text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByRole('button', { name: 'Click me' })).toBeInTheDocument();
  });

  it('should call onClick when clicked', async () => {
    const handleClick = vi.fn();
    render(<Button onClick={handleClick}>Click</Button>);
    await userEvent.click(screen.getByRole('button'));
    expect(handleClick).toHaveBeenCalledOnce();
  });

  it('should be disabled when isLoading is true', () => {
    render(<Button isLoading>Save</Button>);
    expect(screen.getByRole('button')).toBeDisabled();
  });

  it('should have no accessibility violations', async () => {
    const { container } = render(<Button>Accessible</Button>);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
});
```

### MSW API Mocking
```tsx
// src/mocks/handlers.ts
import { http, HttpResponse } from 'msw';

export const handlers = [
  http.get('/api/users', () =>
    HttpResponse.json([
      { id: '1', name: 'Alice', email: 'alice@example.com' },
    ]),
  ),
];

// src/mocks/server.ts
import { setupServer } from 'msw/node';
import { handlers } from './handlers';
export const server = setupServer(...handlers);
```

### Rules
1. Test user-visible behavior, not implementation details
2. Query by role, label, or text — never by test ID unless no semantic alternative
3. Use `userEvent` over `fireEvent` for realistic interactions
4. Mock API calls with MSW — never mock `fetch` directly
5. Run `axe` accessibility checks on every component test
6. Naming: `describe('ComponentName')` → `it('should <behavior>')`
7. Coverage target: ≥ 80% lines and branches

---

## RS12: Accessibility

### Semantic HTML First
```tsx
// ✅ Correct — semantic elements
<nav aria-label="Main navigation">
  <ul>
    <li><a href="/dashboard">Dashboard</a></li>
  </ul>
</nav>

// ❌ Wrong — div soup
<div className="nav">
  <div onClick={goToDashboard}>Dashboard</div>
</div>
```

### ARIA Only When Needed
```tsx
// ✅ Button already has implicit role
<button onClick={onClose}>Close</button>

// ✅ ARIA needed — no native element for this pattern
<div role="tablist" aria-label="Settings tabs">
  <button role="tab" aria-selected={activeTab === 'general'}>General</button>
  <button role="tab" aria-selected={activeTab === 'security'}>Security</button>
</div>
```

### Focus Trap in Modals
```tsx
// Use a focus-trap library (e.g., focus-trap-react)
import FocusTrap from 'focus-trap-react';

export function Modal({ isOpen, onClose, children }: ModalProps) {
  if (!isOpen) return null;

  return (
    <FocusTrap>
      <div role="dialog" aria-modal="true" aria-labelledby="modal-title">
        <h2 id="modal-title">Modal Title</h2>
        {children}
        <button onClick={onClose}>Close</button>
      </div>
    </FocusTrap>
  );
}
```

### Skip-to-Content Link
```tsx
// In RootLayout, first child
<a href="#main-content" className="sr-only focus:not-sr-only focus:absolute focus:p-4">
  Skip to content
</a>
// ...
<main id="main-content">{children}</main>
```

### Rules
1. Use semantic HTML elements (`<nav>`, `<main>`, `<section>`, `<button>`, `<a>`)
2. Add ARIA attributes only when no native semantic element exists
3. All interactive elements must be keyboard-accessible (Tab, Enter, Escape)
4. Modals must trap focus and return focus on close
5. Color contrast ratio: ≥ 4.5:1 for normal text, ≥ 3:1 for large text (WCAG AA)
6. Test with screen reader (VoiceOver / NVDA) before release
7. Include skip-to-content link as first focusable element

---

## RS13: Performance

### Code Splitting with React.lazy
```tsx
const AdminPage = lazy(() => import('@/pages/Admin/AdminPage'));

// In router or component
<Suspense fallback={<LoadingSpinner />}>
  <AdminPage />
</Suspense>
```

### Memoization
```tsx
// useMemo for expensive computations
const sortedItems = useMemo(
  () => items.toSorted((a, b) => a.name.localeCompare(b.name)),
  [items],
);

// useCallback for stable function references passed to children
const handleSelect = useCallback(
  (id: string) => setSelectedId(id),
  [],
);
```

### Virtualized Lists
```tsx
import { useVirtualizer } from '@tanstack/react-virtual';

function VirtualList({ items }: { items: Item[] }) {
  const parentRef = useRef<HTMLDivElement>(null);
  const virtualizer = useVirtualizer({
    count: items.length,
    getScrollElement: () => parentRef.current,
    estimateSize: () => 48,
  });

  return (
    <div ref={parentRef} style={{ height: '400px', overflow: 'auto' }}>
      <div style={{ height: virtualizer.getTotalSize() }}>
        {virtualizer.getVirtualItems().map((vItem) => (
          <div key={vItem.key} style={{ height: vItem.size, transform: `translateY(${vItem.start}px)` }}>
            {items[vItem.index].name}
          </div>
        ))}
      </div>
    </div>
  );
}
```

### Rules
1. Lazy-load every route-level page component
2. Use `useMemo` / `useCallback` only for measurable performance gains — not by default
3. Virtualize lists with > 100 items
4. Use `loading="lazy"` on `<img>` elements below the fold
5. Analyze bundle with `npx vite-bundle-visualizer` — keep initial JS < 200 KB gzipped

---

## RS14: TypeScript Patterns

### Strict Mode
All projects must enable `"strict": true` in `tsconfig.json`. No exceptions.

### Interface for Props (Not Type)
```tsx
// ✅ Correct
interface ButtonProps {
  label: string;
  onClick: () => void;
}

// ❌ Avoid for props
type ButtonProps = {
  label: string;
  onClick: () => void;
};
```

### Enum for Constants
```tsx
enum Status {
  Idle = 'idle',
  Loading = 'loading',
  Success = 'success',
  Error = 'error',
}
```

### Utility Types
```tsx
// Partial — make all fields optional
type UpdateUserPayload = Partial<User>;

// Pick — select specific fields
type UserSummary = Pick<User, 'id' | 'name'>;

// Omit — exclude specific fields
type CreateUserPayload = Omit<User, 'id' | 'createdAt'>;

// Record — typed key-value maps
type PermissionMap = Record<string, boolean>;
```

### Discriminated Unions for State
```tsx
interface IdleState {
  status: Status.Idle;
}

interface LoadingState {
  status: Status.Loading;
}

interface SuccessState<T> {
  status: Status.Success;
  data: T;
}

interface ErrorState {
  status: Status.Error;
  error: string;
}

type AsyncState<T> = IdleState | LoadingState | SuccessState<T> | ErrorState;

function renderState(state: AsyncState<User[]>) {
  switch (state.status) {
    case Status.Idle:
      return null;
    case Status.Loading:
      return <LoadingSpinner />;
    case Status.Success:
      return <UserList users={state.data} />;
    case Status.Error:
      return <ErrorMessage message={state.error} />;
  }
}
```

### Rules
1. **No `any`** — use `unknown` and narrow with type guards
2. Use `interface` for object shapes and props; use `type` for unions and intersections
3. Export types/interfaces from `src/types/` for shared models
4. Use `satisfies` operator for type-safe object literals
5. Prefer `as const` over enum when you need a simple string union

---

## RS15: Naming Conventions

| Category | Convention | Example |
|---|---|---|
| Components | PascalCase | `Button.tsx`, `UserCard.tsx` |
| Pages | PascalCase + `Page` suffix | `DashboardPage.tsx` |
| Hooks | camelCase with `use` prefix | `useAuth.ts`, `useDebounce.ts` |
| Utilities | camelCase | `formatCurrency.ts`, `dateHelpers.ts` |
| Stores | camelCase with `Store`/`Slice` suffix | `authStore.ts`, `authSlice.ts` |
| Types/Interfaces | PascalCase | `User`, `ApiResponse<T>` |
| Constants | SCREAMING_SNAKE_CASE | `MAX_RETRY_COUNT`, `API_BASE_URL` |
| CSS Modules | kebab-case | `user-card.module.css` |
| Test files | Same as source + `.test` | `Button.test.tsx` |
| Directories | kebab-case (shared), PascalCase (pages) | `hooks/`, `Dashboard/` |

### Boolean Props and Variables
```tsx
// Prefix with is/has/should/can
interface ModalProps {
  isOpen: boolean;
  hasOverlay: boolean;
  canDismiss: boolean;
}
```

### Event Handler Naming
```tsx
// Props: on + Event (onSubmit, onClick, onChange)
// Handlers: handle + Event (handleSubmit, handleClick, handleChange)
interface FormProps {
  onSubmit: (data: FormData) => void;
}

function MyForm({ onSubmit }: FormProps) {
  const handleSubmit = (data: FormData) => {
    // transform, validate, etc.
    onSubmit(data);
  };
}
```

---

## RS16: Brownfield Guide

When adding React code to an existing codebase, follow these rules to minimize disruption:

### Rules
1. **Match existing patterns** — if the project uses Redux, add a new slice; don't introduce Zustand
2. **Add to existing route config** — extend the current router file; don't create a parallel routing system
3. **Reuse existing components** — check `components/` for existing buttons, inputs, modals before creating new ones
4. **Reuse existing hooks** — check `hooks/` for existing data-fetching or auth hooks
5. **Don't refactor unrelated code** — scope changes to the feature being built
6. **Add to existing store slices** — extend current state management; don't create competing stores
7. **Follow existing naming** — if the project uses `*.component.tsx`, follow that; don't introduce `*.tsx` alone
8. **Preserve existing test patterns** — use the same test runner, assertion style, and file structure

### Decision Checklist (Before Writing Code)
```
□ Have I checked for an existing component that does this?
□ Have I checked for an existing hook that fetches this data?
□ Am I adding to the existing route config (not creating a new one)?
□ Am I using the project's existing state management tool?
□ Am I following the project's existing naming conventions?
□ Is my change scoped to only the feature I'm building?
```

---

## RS17: Cross-References

This section maps React standards to related knowledge bases for agent context.

| React Standard | Related KB | Related Section | Relationship |
|---|---|---|---|
| RS3: Component Pattern | Enterprise Architecture | EA11: Design System | Components must align with design system tokens and patterns |
| RS8: Styling | Enterprise Architecture | EA11: Design System | Design tokens from EA11 feed into Tailwind config / CSS variables |
| RS9: Form Handling | UI Coding Standards | UC5: Forms | Form patterns must meet UC5 accessibility and UX requirements |
| RS11: Testing | UI Coding Standards | UC9: Testing | Test coverage and strategy aligns with UC9 standards |
| RS12: Accessibility | Enterprise Architecture | EA7: Accessibility | All accessibility rules derive from EA7 WCAG compliance requirements |
| RS12: Accessibility | UI Coding Standards | UC7: Accessibility | Component-level a11y patterns from UC7 |
| RS7: API Integration | Microservices Standards | MS4: BFF Pattern | API client connects to BFF layer defined in MS4 |
| RS6: Routing | UI Coding Standards | UC3: Navigation | Route structure follows UC3 navigation patterns |
| RS5: State Management | UI Coding Standards | UC4: State | State management strategy aligns with UC4 guidelines |
| RS13: Performance | UI Coding Standards | UC10: Performance | Performance budgets and metrics from UC10 |
| RS14: TypeScript Patterns | UI Coding Standards | UC1: TypeScript | TypeScript rules extend UC1 base TypeScript standards |
| RS15: Naming Conventions | UI Coding Standards | UC2: Naming | Naming conventions extend UC2 base naming standards |

### How Agents Should Use Cross-References
1. When generating a component (RS3), also check EA11 for design system constraints
2. When generating forms (RS9), validate against both RS12 and EA7 accessibility rules
3. When creating API hooks (RS7), verify the endpoint follows MS4 BFF patterns
4. When adding routes (RS6), ensure navigation aligns with UC3 patterns

---

*End of React Coding Standards — kb-L1-react-standards v1.0.0*
