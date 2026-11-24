# SPEC.md — Feature Contract (Mini-PRD)

## Feature: [Name]
**Status:** DRAFT | APPROVED | IN_PROGRESS | VERIFIED

## 1. Goal & Non-Goals
- **Goal:** [1–2 concrete sentences on user/system outcome]
- **Non-Goals (Out of Scope):** [Explicitly list what NOT to build to prevent scope creep]

## 2. Deterministic Flow
1. Trigger: [User action / cron / webhook] with [validated input].
2. Guard: [AuthZ + business invariant check].
3. Mutation: [Atomic DB / chain / state change].
4. Result: [Exact output + UI state update].

## 3. Data & API Contract
- **Endpoint / Function:** `...`
- **Input Schema (`src/schemas/...`):** `{ ... }`
- **Success Output:** `{ ... }`
- **Error Map:** `400` validation | `403` forbidden | `409` conflict | `502` upstream timeout

## 4. Edge Cases & Acceptance Criteria
- [ ] Double-submit / replay protection handled
- [ ] Upstream timeout / offline fallback handled
- [ ] All 4 UI states (`loading`, `empty`, `error`, `data`) implemented
- [ ] Unit/integration tests cover happy path + >= 2 failure modes
- [ ] `npm run verify` passes with 0 errors
