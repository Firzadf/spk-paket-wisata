# DECISIONS.md — Architecture Decision Records (ADR)

Rules marked `LOCKED` MUST NOT be refactored or reversed by any agent without explicit user approval.

---

### ADR-001: Proof-First UI & Recorded Replay Fallback
- **Date:** 2026-11-24
- **Status:** LOCKED
- **Context:** Live RPC/external APIs can be slow or offline during demos/reviews, and wallet-walls kill conversion.
- **Decision:** Render initial public views via SSR/static HTML with bundled real-world replay snapshots (`SIMULATED`/`REPLAY` tagged) that upgrade to live polling when available.
- **Why not alternatives:** Pure CSR with loading spinners fails when nodes stall; mock random numbers destroy credibility.
