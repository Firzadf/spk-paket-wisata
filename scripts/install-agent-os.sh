#!/usr/bin/env bash
set -euo pipefail

echo "🔧 Installing Senior Autonomous Agent OS..."

# Ensure directories exist
mkdir -p .ai .agents/skills .claude .cursor/rules

# Symlink .claude/skills -> ../.agents/skills for Claude Code compatibility
if [ ! -e ".claude/skills" ]; then
  ln -s ../.agents/skills .claude/skills
  echo "✅ Linked .claude/skills -> .agents/skills"
fi

# Verify core constitution files
REQUIRED_FILES=(
  "AGENTS.md"
  "CLAUDE.md"
  "DESIGN.md"
  "ARCHITECTURE.md"
  "SECURITY.md"
  "SPEC.md"
  "DECISIONS.md"
  ".ai/AUDITOR.md"
  ".ai/SKILL_INDEX.md"
)

for f in "${REQUIRED_FILES[@]}"; do
  if [ -f "$f" ]; then
    echo "  ✓ $f"
  else
    echo "  ✗ MISSING: $f"
    exit 1
  fi
done

echo ""
echo "🚀 Senior Autonomous Agent OS ready!"
echo "Prompt awal yang disarankan:"
echo '  "Baca AGENTS.md dan .ai/SKILL_INDEX.md. Audit repo ini, aktifkan semua skill relevan, usulkan 3 ide paling berdampak tinggi, lalu eksekusi yang terbaik secara end-to-end."'
