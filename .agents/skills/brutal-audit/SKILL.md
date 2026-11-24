---
name: brutal-audit
description: Hostile Senior/Staff Engineer self-review of code diffs, security boundaries, architecture, and build verification.
---

# Skill: Brutal Pre-Finish Audit

## When to Trigger
- Before completing any feature, bugfix, or refactor.
- Whenever the user invokes `/audit` or asks for a code review.

## Execution Protocol
1. **Run Deterministic Checks First:**
   - Execute typecheck, linter, and test suite. Never skip failing tests.
2. **Inspect `git diff` Line-by-Line:**
   - Apply all 5 lenses from `.ai/AUDITOR.md` (Correctness, Security/AuthZ, Architecture, Performance/Reliability, AI Slop).
3. **Fix All P0 & P1 Issues Immediately:**
   - Do not leave `TODO` comments for security checks, error handling, or broken edge cases. Patch them before reporting completion.
4. **Report Transparently:**
   - Summarize: (a) files changed, (b) verification commands passed, (c) skills used/created, and (d) explicit scope boundaries or remaining risks.
