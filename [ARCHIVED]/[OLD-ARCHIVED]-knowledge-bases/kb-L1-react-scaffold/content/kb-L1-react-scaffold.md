# KB-L1-React-Scaffold — Production-Ready React Project Scaffold

> Layer: L1 | Status: Active | Version: 1.0.0
> Dependencies: kb-L1-react-standards, kb-L0-ui-coding-standards, kb-L1-enterprise-architecture

---

## SF1: Overview

This knowledge base defines the canonical scaffold for production-ready React 18 + TypeScript
applications. Every new frontend project MUST be bootstrapped from this scaffold to ensure
consistency across teams.

### Stack Summary

| Concern            | Technology                        | Version |
|--------------------|-----------------------------------|---------|
| UI Library         | React                             | 18.3    |
| Language           | TypeScript                        | 5.5     |
| Build Tool         | Vite                              | 5.4     |
| Unit Testing       | Vitest + Testing Library          | 2.1     |
| Routing            | React Router                      | 6.26    |
| State (server)     | TanStack React Query              | 5.56    |
| State (client)     | Zustand                           | 4.5     |
| Styling            | Tailwind CSS                      | 3.4     |
| Validation         | Zod                               | 3.23    |
| Forms              | React Hook Form                   | 7.53    |
| HTTP Client        | Axios                             | 1.7     |
| API Mocking        | MSW                               | 2.4     |
| Accessibility      | @axe-core/react                   | 4.10    |
| Container          | Docker (multi-stage)              | —       |
| Orchestration      | Kubernetes                        | —       |
| CI/CD              | GitHub Actions                    | —       |

### Principles

1. **Type-safe by default** — strict TypeScript, no `any` escape hatches.
2. **Accessible first** — WCAG 2.1 AA compliance enforced via linting and runtime checks.
3. **Test-driven** — minimum 80% coverage gate in CI.
4. **Design-system aligned** — all UI built from shared tokens and atomic components.
5. **Container-ready** — every app ships as a <50 MB Docker image with health checks.
6. **Observable** — correlation IDs on every request, structured error logging.

---

## SF2: File Tree

All scaffold projects MUST follow this directory structure exactly. Deviations require
architecture review approval.

```
project-root/
├── .github/
│   └── workflows/
│       └── ci.yml
├── k8s/
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── configmap.yaml
│   └── hpa.yaml
├── public/
│   └── favicon.svg
├── src/
│   ├── components/
│   │   ├── atoms/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Skeleton.tsx
│   │   │   └── ErrorState.tsx
│   │   ├── molecules/
│   │   └── organisms/
│   ├── hooks/
│   │   └── useAuth.ts
│   ├── pages/
│   │   ├── HomePage.tsx
│   │   └── NotFoundPage.tsx
│   ├── services/
│   │   └── api.ts
│   ├── stores/
│   ├── styles/
│   │   ├── tokens.css
│   │   └── global.css
│   ├── types/
│   │   └── index.ts
│   ├── utils/
│   ├── App.tsx
│   ├── main.tsx
│   └── router.tsx
├── tests/
│   ├── setup.ts
│   └── mocks/
│       └── handlers.ts
├── index.html
├── vite.config.ts
├── tsconfig.json
├── .eslintrc.cjs
├── .prettierrc
├── tailwind.config.ts
├── postcss.config.js
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Directory Purposes

| Directory              | Purpose                                              |
|------------------------|------------------------------------------------------|
| `src/components/atoms`    | Primitive UI elements (Button, Input, Card, etc.)  |
| `src/components/molecules`| Composed atoms (FormField, SearchBar, etc.)        |
| `src/components/organisms`| Complex sections (Header, Sidebar, DataTable)      |
| `src/hooks/`              | Custom React hooks                                 |
| `src/pages/`              | Route-level page components                        |
| `src/services/`           | API client and external service integrations       |
| `src/stores/`             | Zustand client-state stores                        |
| `src/styles/`             | Design tokens, global CSS                          |
| `src/types/`              | Shared TypeScript type definitions                 |
| `src/utils/`              | Pure utility functions                             |
| `tests/`                  | Test setup, mocks, integration tests               |
| `k8s/`                    | Kubernetes manifests                               |

---

## SF3: package.json

The scaffold `package.json` pins exact versions to ensure reproducible builds.

```json
{
  "name": "@org/app-scaffold",
  "version": "0.1.0",
  "private": true,
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc -b && vite build",
    "preview": "vite preview",
    "lint": "eslint . --ext .ts,.tsx --report-unused-disable-directives --max-warnings 0",
    "format": "prettier --write \"src/**/*.{ts,tsx,css}\"",
    "format:check": "prettier --check \"src/**/*.{ts,tsx,css}\"",
    "typecheck": "tsc --noEmit",
    "test": "vitest run",
    "test:watch": "vitest",
    "test:coverage": "vitest run --coverage",
    "test:a11y": "vitest run --config vitest.a11y.config.ts"
  },
  "dependencies": {
    "react": "18.3.1",
    "react-dom": "18.3.1",
    "react-router-dom": "6.26.2",
    "@tanstack/react-query": "5.56.2",
    "zustand": "4.5.5",
    "axios": "1.7.7",
    "zod": "3.23.8",
    "react-hook-form": "7.53.0",
    "@hookform/resolvers": "3.9.0"
  },
  "devDependencies": {
    "typescript": "5.5.4",
    "vite": "5.4.8",
    "@vitejs/plugin-react": "4.3.2",
    "vitest": "2.1.2",
    "@testing-library/react": "16.0.1",
    "@testing-library/jest-dom": "6.5.0",
    "@testing-library/user-event": "14.5.2",
    "jsdom": "25.0.1",
    "msw": "2.4.9",
    "@axe-core/react": "4.10.0",
    "tailwindcss": "3.4.13",
    "postcss": "8.4.47",
    "autoprefixer": "10.4.20",
    "eslint": "8.57.1",
    "@typescript-eslint/eslint-plugin": "8.8.0",
    "@typescript-eslint/parser": "8.8.0",
    "eslint-plugin-react": "7.37.1",
    "eslint-plugin-react-hooks": "4.6.2",
    "eslint-plugin-jsx-a11y": "6.10.0",
    "prettier": "3.3.3",
    "@vitest/coverage-v8": "2.1.2"
  }
}
```

### Rules

- NEVER use `^` or `~` ranges — pin exact versions.
- Update dependencies via a dedicated PR with full CI validation.
- `@axe-core/react` is a devDependency but MUST be conditionally loaded in dev mode (see SF6).

---

## SF4: vite.config.ts

```typescript
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';
import path from 'node:path';

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8080',
        changeOrigin: true,
        rewrite: (p) => p.replace(/^\/api/, ''),
      },
    },
  },
  build: {
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          query: ['@tanstack/react-query'],
        },
      },
    },
  },
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./tests/setup.ts'],
    include: ['src/**/*.test.{ts,tsx}', 'tests/**/*.test.{ts,tsx}'],
    coverage: {
      provider: 'v8',
      reporter: ['text', 'lcov', 'json-summary'],
      thresholds: { statements: 80, branches: 80, functions: 80, lines: 80 },
      exclude: ['src/main.tsx', 'src/vite-env.d.ts', 'tests/mocks/**'],
    },
  },
});
```

### Key Decisions

- **Path alias `@/`** — all imports use `@/components/...` instead of relative paths.
- **API proxy** — `/api` routes proxy to backend during development; production uses env-based URL.
- **Manual chunks** — vendor split keeps main bundle small.
- **Coverage thresholds** — CI fails below 80% on any metric.

---

## SF5: tsconfig.json

```json
{
  "compilerOptions": {
    "target": "ES2022",
    "lib": ["ES2022", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "moduleResolution": "bundler",
    "jsx": "react-jsx",
    "strict": true,
    "noUncheckedIndexedAccess": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    },
    "outDir": "dist",
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true
  },
  "include": ["src", "tests"],
  "exclude": ["node_modules", "dist"]
}
```

### Rules

- `strict: true` is NON-NEGOTIABLE — never disable.
- `noUncheckedIndexedAccess` catches undefined array/object access at compile time.
- Path alias `@/*` MUST match the Vite alias in SF4.

---

## SF6: App.tsx + main.tsx + router.tsx

### main.tsx

```tsx
import React from 'react';
import ReactDOM from 'react-dom/client';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { App } from '@/App';
import '@/styles/tokens.css';
import '@/styles/global.css';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: { staleTime: 30_000, retry: 1 },
    mutations: { retry: 0 },
  },
});

// Accessibility auditing in development only
if (import.meta.env.DEV) {
  import('@axe-core/react').then((axe) => {
    axe.default(React, ReactDOM, 1000);
  });
}

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <QueryClientProvider client={queryClient}>
      <App />
    </QueryClientProvider>
  </React.StrictMode>,
);
```

### App.tsx

```tsx
import { Suspense } from 'react';
import { RouterProvider } from 'react-router-dom';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import { Skeleton } from '@/components/atoms/Skeleton';
import { router } from '@/router';

export function App() {
  return (
    <ErrorBoundary>
      <Suspense fallback={<Skeleton className="h-screen w-full" />}>
        <RouterProvider router={router} />
      </Suspense>
    </ErrorBoundary>
  );
}
```

### router.tsx

```tsx
import { createBrowserRouter, Navigate } from 'react-router-dom';
import { lazy } from 'react';
import { ProtectedRoute } from '@/components/ProtectedRoute';

const HomePage = lazy(() => import('@/pages/HomePage'));
const NotFoundPage = lazy(() => import('@/pages/NotFoundPage'));

export const router = createBrowserRouter([
  {
    path: '/',
    element: <ProtectedRoute />,
    children: [
      { index: true, element: <HomePage /> },
    ],
  },
  { path: '/404', element: <NotFoundPage /> },
  { path: '*', element: <Navigate to="/404" replace /> },
]);
```

### Rules

- `@axe-core/react` MUST only be imported in dev mode via dynamic import.
- All page components MUST be lazy-loaded.
- `QueryClient` is instantiated once at the module level — never inside a component.
- `ErrorBoundary` wraps the entire app; pages may add nested boundaries.

---

## SF7: API Client — src/services/api.ts

```typescript
import axios, { type InternalAxiosRequestConfig, type AxiosError } from 'axios';

let accessToken: string | null = null;

export function setAccessToken(token: string | null) {
  accessToken = token;
}

export function getAccessToken() {
  return accessToken;
}

function generateCorrelationId(): string {
  return crypto.randomUUID();
}

export interface ApiError {
  status: number;
  code: string;
  message: string;
  correlationId: string;
}

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL ?? '/api',
  timeout: 15_000,
  headers: { 'Content-Type': 'application/json' },
});

// Request interceptor — attach auth token and correlation ID
api.interceptors.request.use((config: InternalAxiosRequestConfig) => {
  const correlationId = generateCorrelationId();
  config.headers.set('X-Correlation-ID', correlationId);
  if (accessToken) {
    config.headers.set('Authorization', `Bearer ${accessToken}`);
  }
  return config;
});

// Response interceptor — transform errors into ApiError
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ code?: string; message?: string }>) => {
    const correlationId = error.config?.headers?.['X-Correlation-ID'] as string ?? 'unknown';
    const apiError: ApiError = {
      status: error.response?.status ?? 0,
      code: error.response?.data?.code ?? 'NETWORK_ERROR',
      message: error.response?.data?.message ?? error.message,
      correlationId,
    };
    console.error('[API Error]', apiError);
    return Promise.reject(apiError);
  },
);

export { api };
```

### Rules

- Base URL comes from `VITE_API_BASE_URL` env var; falls back to `/api` for dev proxy.
- Auth tokens are stored in a module-scoped variable — NEVER in `localStorage` or `sessionStorage`.
- Every request gets a unique `X-Correlation-ID` for distributed tracing.
- Error interceptor normalizes all failures into a typed `ApiError` shape.

---

## SF8: Auth — useAuth Hook + ProtectedRoute

### src/hooks/useAuth.ts

```typescript
import { create } from 'zustand';
import { setAccessToken } from '@/services/api';

interface AuthState {
  isAuthenticated: boolean;
  user: { id: string; email: string; roles: string[] } | null;
  login: (token: string, user: AuthState['user']) => void;
  logout: () => void;
}

export const useAuth = create<AuthState>((set) => ({
  isAuthenticated: false,
  user: null,
  login: (token, user) => {
    setAccessToken(token);
    set({ isAuthenticated: true, user });
  },
  logout: () => {
    setAccessToken(null);
    set({ isAuthenticated: false, user: null });
  },
}));
```

### src/components/ProtectedRoute.tsx

```tsx
import { Navigate, Outlet, useLocation } from 'react-router-dom';
import { useAuth } from '@/hooks/useAuth';

export function ProtectedRoute() {
  const isAuthenticated = useAuth((s) => s.isAuthenticated);
  const location = useLocation();

  if (!isAuthenticated) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
```

### Rules

- Tokens are stored in memory only — page refresh requires re-authentication.
- `ProtectedRoute` uses `<Outlet />` to wrap child routes.
- Auth state is managed via Zustand for synchronous access outside React tree.

---

## SF9: Design System Base

### src/styles/tokens.css

```css
:root {
  /* Colors — Primary */
  --color-primary-50: #eff6ff;
  --color-primary-100: #dbeafe;
  --color-primary-500: #3b82f6;
  --color-primary-600: #2563eb;
  --color-primary-700: #1d4ed8;

  /* Colors — Neutral */
  --color-neutral-50: #f9fafb;
  --color-neutral-100: #f3f4f6;
  --color-neutral-200: #e5e7eb;
  --color-neutral-500: #6b7280;
  --color-neutral-700: #374151;
  --color-neutral-900: #111827;

  /* Colors — Semantic */
  --color-success: #16a34a;
  --color-warning: #d97706;
  --color-error: #dc2626;
  --color-info: #2563eb;

  /* Spacing */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  /* Typography */
  --font-sans: 'Inter', system-ui, -apple-system, sans-serif;
  --font-mono: 'JetBrains Mono', ui-monospace, monospace;
  --text-xs: 0.75rem;
  --text-sm: 0.875rem;
  --text-base: 1rem;
  --text-lg: 1.125rem;
  --text-xl: 1.25rem;
  --text-2xl: 1.5rem;

  /* Radii */
  --radius-sm: 0.25rem;
  --radius-md: 0.375rem;
  --radius-lg: 0.5rem;
  --radius-full: 9999px;

  /* Shadows */
  --shadow-sm: 0 1px 2px rgb(0 0 0 / 0.05);
  --shadow-md: 0 4px 6px rgb(0 0 0 / 0.07);
}
```

### tailwind.config.ts

```typescript
import type { Config } from 'tailwindcss';

export default {
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: {
          50: 'var(--color-primary-50)',
          100: 'var(--color-primary-100)',
          500: 'var(--color-primary-500)',
          600: 'var(--color-primary-600)',
          700: 'var(--color-primary-700)',
        },
        neutral: {
          50: 'var(--color-neutral-50)',
          100: 'var(--color-neutral-100)',
          200: 'var(--color-neutral-200)',
          500: 'var(--color-neutral-500)',
          700: 'var(--color-neutral-700)',
          900: 'var(--color-neutral-900)',
        },
      },
      fontFamily: {
        sans: ['var(--font-sans)'],
        mono: ['var(--font-mono)'],
      },
      borderRadius: {
        sm: 'var(--radius-sm)',
        md: 'var(--radius-md)',
        lg: 'var(--radius-lg)',
      },
    },
  },
  plugins: [],
} satisfies Config;
```

### Atom Components

#### src/components/atoms/Button.tsx

```tsx
import { type ButtonHTMLAttributes, forwardRef } from 'react';

type Variant = 'primary' | 'secondary' | 'ghost';
type Size = 'sm' | 'md' | 'lg';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant;
  size?: Size;
}

const variantStyles: Record<Variant, string> = {
  primary: 'bg-primary-600 text-white hover:bg-primary-700 focus-visible:ring-primary-500',
  secondary: 'bg-neutral-100 text-neutral-700 hover:bg-neutral-200',
  ghost: 'bg-transparent text-neutral-700 hover:bg-neutral-100',
};

const sizeStyles: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-4 py-2 text-base',
  lg: 'px-6 py-3 text-lg',
};

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  ({ variant = 'primary', size = 'md', className = '', children, ...props }, ref) => (
    <button
      ref={ref}
      className={`inline-flex items-center justify-center rounded-md font-medium
        transition-colors focus-visible:outline-none focus-visible:ring-2
        focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50
        ${variantStyles[variant]} ${sizeStyles[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  ),
);
Button.displayName = 'Button';
```

#### src/components/atoms/Input.tsx

```tsx
import { type InputHTMLAttributes, forwardRef } from 'react';

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label: string;
  error?: string;
}

export const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, id, className = '', ...props }, ref) => {
    const inputId = id ?? label.toLowerCase().replace(/\s+/g, '-');
    return (
      <div className="flex flex-col gap-1">
        <label htmlFor={inputId} className="text-sm font-medium text-neutral-700">
          {label}
        </label>
        <input
          ref={ref}
          id={inputId}
          aria-invalid={!!error}
          aria-describedby={error ? `${inputId}-error` : undefined}
          className={`rounded-md border border-neutral-200 px-3 py-2 text-base
            focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20
            ${error ? 'border-error' : ''} ${className}`}
          {...props}
        />
        {error && (
          <p id={`${inputId}-error`} role="alert" className="text-sm text-error">
            {error}
          </p>
        )}
      </div>
    );
  },
);
Input.displayName = 'Input';
```

#### Other Atoms (Card, Badge, Skeleton, ErrorState)

```tsx
// src/components/atoms/Card.tsx
export function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return <div className={`rounded-lg border border-neutral-200 bg-white p-4 shadow-sm ${className}`}>{children}</div>;
}

// src/components/atoms/Badge.tsx
type BadgeVariant = 'default' | 'success' | 'warning' | 'error';
const badgeStyles: Record<BadgeVariant, string> = {
  default: 'bg-neutral-100 text-neutral-700',
  success: 'bg-green-100 text-green-800',
  warning: 'bg-yellow-100 text-yellow-800',
  error: 'bg-red-100 text-red-800',
};
export function Badge({ variant = 'default', children }: { variant?: BadgeVariant; children: React.ReactNode }) {
  return <span className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeStyles[variant]}`}>{children}</span>;
}

// src/components/atoms/Skeleton.tsx
export function Skeleton({ className = '' }: { className?: string }) {
  return <div className={`animate-pulse rounded-md bg-neutral-200 ${className}`} role="status" aria-label="Loading" />;
}

// src/components/atoms/ErrorState.tsx
import { Button } from './Button';
export function ErrorState({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div role="alert" className="flex flex-col items-center gap-4 p-8 text-center">
      <p className="text-lg text-neutral-700">{message}</p>
      {onRetry && <Button variant="secondary" onClick={onRetry}>Try Again</Button>}
    </div>
  );
}
```

---

## SF10: Error Boundary

### src/components/ErrorBoundary.tsx

```tsx
import { Component, type ErrorInfo, type ReactNode } from 'react';
import { ErrorState } from '@/components/atoms/ErrorState';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', { error: error.message, componentStack: info.componentStack });
    // Integration point: send to observability platform
  }

  private handleRetry = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      return this.props.fallback ?? (
        <ErrorState
          message="Something went wrong. Please try again."
          onRetry={this.handleRetry}
        />
      );
    }
    return this.props.children;
  }
}
```

### Rules

- Every app MUST have a root-level `ErrorBoundary` (see SF6).
- Pages with independent failure modes SHOULD add nested boundaries.
- `componentDidCatch` MUST log to the observability platform in production.
- The retry action resets state, causing children to re-mount.

---

## SF11: ESLint + Prettier

### .eslintrc.cjs

```javascript
module.exports = {
  root: true,
  env: { browser: true, es2022: true },
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module',
    ecmaFeatures: { jsx: true },
  },
  plugins: ['@typescript-eslint', 'react', 'react-hooks', 'jsx-a11y'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-type-checked',
    'plugin:react/recommended',
    'plugin:react/jsx-runtime',
    'plugin:react-hooks/recommended',
    'plugin:jsx-a11y/recommended',
  ],
  settings: {
    react: { version: 'detect' },
  },
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
    'react/prop-types': 'off',
    'react/self-closing-comp': 'error',
    'jsx-a11y/anchor-is-valid': 'error',
    'no-console': ['warn', { allow: ['error', 'warn'] }],
  },
  overrides: [
    {
      files: ['**/*.test.{ts,tsx}'],
      rules: { '@typescript-eslint/no-explicit-any': 'off' },
    },
  ],
  ignorePatterns: ['dist', 'node_modules', '*.config.*'],
};
```

### .prettierrc

```json
{
  "singleQuote": true,
  "semi": true,
  "trailingComma": "all",
  "printWidth": 100,
  "tabWidth": 2,
  "arrowParens": "always",
  "endOfLine": "lf"
}
```

### Rules

- `jsx-a11y/recommended` is REQUIRED — accessibility violations fail the build.
- `no-explicit-any` is an error, not a warning — no `any` in production code.
- Test files may relax `any` restrictions for mock typing convenience.
- Prettier and ESLint MUST not conflict — Prettier handles formatting, ESLint handles logic.

---

## SF12: Dockerfile

```dockerfile
# ── Stage 1: Build ──────────────────────────────────────────
FROM node:20-alpine AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --ignore-scripts

COPY . .
RUN npm run build

# ── Stage 2: Serve ──────────────────────────────────────────
FROM nginx:1.27-alpine AS production

# Remove default config
RUN rm /etc/nginx/conf.d/default.conf

# Custom nginx config
COPY --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Health check endpoint
RUN echo "OK" > /usr/share/nginx/html/health

# Non-root user
RUN addgroup -g 1001 -S appgroup && \
    adduser -u 1001 -S appuser -G appgroup && \
    chown -R appuser:appgroup /usr/share/nginx/html /var/cache/nginx /var/log/nginx /etc/nginx/conf.d
RUN touch /var/run/nginx.pid && chown appuser:appgroup /var/run/nginx.pid

USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget -qO- http://localhost:8080/health || exit 1

CMD ["nginx", "-g", "daemon off;"]
```

### nginx.conf (included in scaffold)

```nginx
server {
    listen 8080;
    root /usr/share/nginx/html;
    index index.html;

    location /health {
        access_log off;
        return 200 'OK';
        add_header Content-Type text/plain;
    }

    location / {
        try_files $uri $uri/ /index.html;
    }

    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff2?)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml;
}
```

### Rules

- Final image MUST be under 50 MB.
- Container runs as non-root user (UID 1001).
- Health check endpoint at `/health` returns 200.
- SPA fallback via `try_files` to `index.html`.
- Static assets get 1-year cache with immutable header.

---

## SF13: Kubernetes Manifests

### k8s/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
  labels:
    app: frontend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
        - name: nginx
          image: registry.example.com/frontend:latest
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: 50m
              memory: 64Mi
            limits:
              cpu: 200m
              memory: 128Mi
          livenessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 5
            periodSeconds: 10
          readinessProbe:
            httpGet:
              path: /health
              port: 8080
            initialDelaySeconds: 3
            periodSeconds: 5
          envFrom:
            - configMapRef:
                name: frontend-config
      securityContext:
        runAsNonRoot: true
        runAsUser: 1001
```

### k8s/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  type: ClusterIP
  selector:
    app: frontend
  ports:
    - port: 80
      targetPort: 8080
      protocol: TCP
```

### k8s/configmap.yaml

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: frontend-config
data:
  VITE_API_BASE_URL: "https://api.example.com"
```

### k8s/hpa.yaml

```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 2
  maxReplicas: 10
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 70
```

### Rules

- Minimum 2 replicas for high availability.
- Resource requests and limits are REQUIRED on every container.
- Liveness and readiness probes MUST point to `/health`.
- HPA scales on CPU utilization at 70% threshold.
- `runAsNonRoot: true` enforced at pod level.

---

## SF14: GitHub Actions CI

### .github/workflows/ci.yml

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

permissions:
  contents: read
  packages: write

env:
  NODE_VERSION: '20'
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  quality:
    name: Quality Checks
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - name: Install dependencies
        run: npm ci

      - name: Lint
        run: npm run lint

      - name: Type check
        run: npm run typecheck

      - name: Unit tests
        run: npm run test

      - name: Integration tests
        run: npm run test -- --config vitest.integration.config.ts

      - name: Accessibility tests
        run: npm run test:a11y

      - name: Coverage check
        run: npm run test:coverage

      - name: Upload coverage
        uses: actions/upload-artifact@v4
        with:
          name: coverage
          path: coverage/

  build:
    name: Build & Push
    needs: quality
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: npm

      - name: Install & Build
        run: |
          npm ci
          npm run build

      - name: Log in to registry
        uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: SCA - Dependency vulnerability scan (Snyk)
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
        with:
          args: --severity-threshold=high

      - name: Build Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: false
          tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          load: true

      - name: Trivy vulnerability scan
        uses: aquasecurity/trivy-action@master
        with:
          image-ref: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
          format: table
          exit-code: 1
          severity: CRITICAL,HIGH

      - name: Push Docker image
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ github.sha }}
            ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:latest
```

### Pipeline Stages

| Stage               | Gate                                    |
|----------------------|-----------------------------------------|
| Install              | `npm ci` succeeds                      |
| Lint                 | Zero warnings, zero errors             |
| Type check           | `tsc --noEmit` passes                  |
| Unit tests           | All pass                               |
| Integration tests    | All pass                               |
| Accessibility tests  | All pass                               |
| Coverage             | ≥80% statements, branches, functions, lines |
| Build                | `vite build` succeeds                  |
| Docker build         | Image builds successfully              |
| Trivy scan           | No CRITICAL or HIGH vulnerabilities    |
| Push                 | Image pushed to registry               |

### Rules

- Quality job MUST pass before build job runs.
- Docker push only happens on `main` branch.
- Trivy scan blocks push if CRITICAL or HIGH CVEs are found.
- Coverage artifacts are uploaded for PR review.

---

## SF15: Scaffold Checklist

Every new project bootstrapped from this scaffold MUST pass all 15 checks before
the first PR is merged.

| #  | Check                    | Command / Verification                          | Pass Criteria                  |
|----|--------------------------|--------------------------------------------------|--------------------------------|
| 1  | Build succeeds           | `npm run build`                                  | Exit code 0, dist/ created     |
| 2  | Lint passes              | `npm run lint`                                   | Zero warnings, zero errors     |
| 3  | Type-check passes        | `npm run typecheck`                              | Exit code 0                    |
| 4  | Tests pass               | `npm run test`                                   | All tests green                |
| 5  | Accessibility passes     | `npm run test:a11y`                              | Zero violations                |
| 6  | Health endpoint works    | `curl http://localhost:8080/health`              | Returns 200 OK                 |
| 7  | Docker builds            | `docker build -t app .`                          | Image < 50 MB                  |
| 8  | CI passes                | Push to branch, check GitHub Actions             | All jobs green                 |
| 9  | No secrets in code       | `grep -r "AKIA\|sk-\|password=" src/`            | Zero matches                   |
| 10 | Design tokens applied    | Inspect `tokens.css` loaded, Tailwind uses vars  | CSS variables present in DOM   |
| 11 | Responsive               | Chrome DevTools responsive mode                  | No horizontal scroll at 320px  |
| 12 | Error boundaries         | Throw error in component, verify fallback UI     | ErrorState renders with retry  |
| 13 | Loading states           | Throttle network, verify Skeleton/Suspense       | Skeleton visible during load   |
| 14 | 404 page                 | Navigate to `/nonexistent`                       | NotFoundPage renders           |
| 15 | README complete          | Review README.md                                 | Setup, scripts, architecture documented |

### Sign-off

- [ ] Developer has verified all 15 checks locally.
- [ ] Tech lead has reviewed scaffold customizations.
- [ ] CI pipeline is green on the initial commit.

---

*End of KB-L1-React-Scaffold*
