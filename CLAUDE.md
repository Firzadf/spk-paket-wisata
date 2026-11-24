# CLAUDE.md

@AGENTS.md

## Claude Code Specific Directives
- Always read `.ai/SKILL_INDEX.md` and load matching `.agents/skills/*/SKILL.md` files before planning.
- Use subagents or fresh context passes when running `.ai/AUDITOR.md` on large diffs.
- Never conclude a task without running verification commands (`typecheck`, `lint`, `test`) and confirming zero regressions.
