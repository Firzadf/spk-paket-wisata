# ARCHITECTURE.md — System Map & Layer Boundaries

## 1. High-Level Data Flow
`Client (UI)` -> `Boundary (Route Handler / Server Action / Worker: Zod + AuthZ)` -> `Service Layer (Pure Business Logic)` -> `Adapter / Repository (DB / RPC / External API)`

## 2. Directory Ownership
- `src/app/` (or `src/routes/`) — Routing, SSR pages, and thin HTTP/Worker handlers. Zero heavy business logic.
- `src/components/ui/` — Stateless presentational primitives (Button, Badge, Card, Table, CopyHash). Zero API calls.
- `src/components/features/` — Domain UI composed from `ui/`. Receives typed props, emits events.
- `src/services/` — Core business logic, state machines, and invariants. Must be unit-testable without HTTP or DOM.
- `src/lib/` — Infrastructure clients (DB, RPC with fallback, auth, structured logger, validated `env.ts`).
- `src/schemas/` — Shared Zod schemas & inferred types (Single Source of Truth across FE & BE).

## 3. Strict Dependency Rules (NEVER VIOLATE)
1. **Unidirectional imports:** `app` -> `components` / `services` -> `lib`. Never import `app/` or `components/` inside `services/` or `lib/`.
2. **No DB/Secret SDKs in UI:** React components never import database clients or server-only env vars.
3. **Single Source of Truth:** Never manually duplicate request/response interfaces between FE and BE; infer from `src/schemas/`.
4. **Typed Domain Errors:** Services throw/return structured `AppError` (`code`, `httpStatus`, `safeMessage`). Boundaries map them cleanly without leaking stack traces or SQL errors.
