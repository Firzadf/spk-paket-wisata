---
name: skill-discovery
description: Automatically detect missing domain capabilities, research authoritative docs/patterns, and codify new reusable SKILL.md modules.
---

# Skill: Autonomous Skill Discovery & Self-Expansion

## When to Trigger
- You encounter a framework, SDK, protocol, CLI, or API not yet covered by `.agents/skills/`.
- You hit a non-obvious error, version mismatch, or platform quirk (e.g., metadata version incompatibility, edge runtime constraint).
- You perform a multi-step workflow that will likely be repeated in future tasks.

## Execution Protocol
1. **Check Existing Skills First:**
   - Read `.ai/SKILL_INDEX.md` and scan `.agents/skills/` (plus user-global skill folders if present) to avoid duplicate skills.
2. **Deep-Dive Research:**
   - Inspect local `node_modules` type definitions, official docs, or test against live/local endpoints to verify exact API signatures and pitfalls.
   - Never rely on outdated assumptions; verify version numbers in `package.json` / `Cargo.toml`.
3. **Codify New Skill (`.agents/skills/<skill-slug>/SKILL.md`):**
   - Create a concise, actionable `SKILL.md` (< 120 lines) containing:
     - `name` & `description` frontmatter
     - **Trigger conditions**
     - **Exact verified commands / code patterns**
     - **Known pitfalls & anti-patterns**
4. **Register in `.ai/SKILL_INDEX.md`:**
   - Add a new row to `.ai/SKILL_INDEX.md` so all future sessions automatically discover and use the new skill.
5. **Apply Immediately:**
   - Use the newly created skill right away to complete the current task.
