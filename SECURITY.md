# SECURITY.md — Full-Stack & Web3 Security Invariants

## 1. AuthN, AuthZ & Zero Trust
- Derive `userId` / `role` strictly from verified server-side session/JWT/signature — never from `req.body` or query params.
- **Prevent IDOR:** Every `SELECT`, `UPDATE`, and `DELETE` on user resources must filter by BOTH `resourceId` AND `ownerId` (or explicit RBAC policy).
- **Deny by default:** All mutating endpoints require authentication/authorization unless explicitly documented as public.

## 2. Input Validation & Injection Defense
- Parse all `req.body`, `req.query`, URL params, headers, webhooks, and `process.env` with strict Zod schemas (`.strict()` or `.pick()` to block Mass Assignment).
- Zero `eval`, `new Function`, string-concatenated SQL, or unescaped shell commands.
- **SSRF Guard:** Validate user-supplied URLs (`https:` only, block localhost/private RFC1918 IP ranges) before server-side `fetch()`.

## 3. Concurrency, State & Financial Integrity
- **Atomic State Transitions:** Balance deductions, quota decrements, and status changes must execute inside DB transactions with row locks or conditional updates (`WHERE balance >= amount`).
- **Idempotency:** Payment, claim, mint, and webhook handlers must enforce unique idempotency keys / event IDs to block replay attacks.
- **Webhook Signatures:** Verify HMAC/Ed25519 signatures using timing-safe comparison before parsing JSON body.

## 4. Web3 / RPC Specifics (When Applicable)
- Never trust client-reported tx success without verifying receipt `status === 1`, target contract address, and expected event logs on-chain.
- Never expose private keys in `NEXT_PUBLIC_*` / `VITE_*` or server logs.
- Enforce strict RPC request timeouts (`<= 8s`) and fallback handling so degraded nodes cannot hang workers.
