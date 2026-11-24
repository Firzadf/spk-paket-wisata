---
name: autonomous-ideation
description: Proactive senior-engineer research, root-cause investigation, and high-leverage ideation before coding.
---

# Skill: Autonomous Ideation & Deep Investigation ("Ngulik Mode")

## When to Trigger
- Every new feature request, product concept, refactor, or optimization task.
- Whenever the user asks you to explore, improve, or build something autonomously.

## Execution Protocol
1. **Reconnaissance (Read Before Thinking):**
   - Inspect codebase structure, schemas, existing services, and git history.
   - Identify existing patterns so new ideas integrate cleanly without duplicating infrastructure.
2. **Gap & Leverage Analysis:**
   - Ask: *Where will a real user get stuck? Where could data corrupt? What can be automated? How do we prove this works without friction?*
   - Benchmark against top-tier developer products (Linear, Stripe, Cloudflare) for UX and reliability.
3. **Structured Proposal (Concise & Opinionated):**
   - Present **3 concrete ideas/paths** ranked by leverage:
     - **Option 1 (Recommended — High Leverage):** Best impact-to-effort ratio, with exact architecture & UX flow.
     - **Option 2 (Ambitious / Differentiator):** Deeper automation, interactive sandbox, or cryptographic/verifiable proof feature.
     - **Option 3 (Fastest MVP):** Minimal viable slice shippable immediately.
   - Include explicit **Trade-offs** and **Risks** for each.
4. **Bias for Action:**
   - If the user already granted autonomous authority ("langsung eksekusi / ngulik sendiri"), pick Option 1, log it in `SPEC.md`, and start building the first vertical slice immediately after presenting the plan.
