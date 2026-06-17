#!/usr/bin/env bash
# fablize-for-hermes setup — install the skill and optionally inject the operating
# block into AGENTS.md / CLAUDE.md (idempotent, with backup).
#
# Usage: setup.sh [--skill-only|--local|--global]
#   --skill-only   Only install the Hermes skill (default if no AGENTS.md/CLAUDE.md found)
#   --local        Also inject operating block into ./AGENTS.md
#   --global       Also inject operating block into ~/.claude/CLAUDE.md
#
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SKILL_SRC="$ROOT/skills/fablize/SKILL.md"
HERMES_SKILLS="$HOME/.hermes/skills/fablize"

REPO_URL="https://github.com/zeus/fablize-for-hermes"

echo "=== fablize-for-hermes setup ==="

# ---- Pre-flight checks ----
[ -f "$SKILL_SRC" ] || { echo "fablize: SKILL.md not found at $SKILL_SRC"; exit 1; }

if [ -d "$HERMES_SKILLS" ]; then
  echo "  = Updating existing skill at $HERMES_SKILLS"
else
  echo "  + Creating skill directory at $HERMES_SKILLS"
fi

# ---- Install the Hermes skill ----
mkdir -p "$HERMES_SKILLS"
cp "$SKILL_SRC" "$HERMES_SKILLS/SKILL.md"
echo "  ✓ Hermes skill installed → $HERMES_SKILLS/SKILL.md"

# Install packs as reference files in the skill directory
mkdir -p "$HERMES_SKILLS/references"
if ls "$ROOT/packs/"*.txt >/dev/null 2>&1; then
  cp "$ROOT/packs/"*.txt "$HERMES_SKILLS/references/"
  echo "  ✓ Packs copied → $HERMES_SKILLS/references/"
else
  echo "  = No pack files found (skipped)"
fi

# Install scripts (goals.py) alongside the skill so auto-discovery finds them
mkdir -p "$HERMES_SKILLS/scripts"
if ls "$ROOT/scripts/"*.py >/dev/null 2>&1; then
  cp "$ROOT/scripts/"*.py "$HERMES_SKILLS/scripts/"
  chmod +x "$HERMES_SKILLS/scripts/"*.py
  echo "  ✓ Scripts copied → $HERMES_SKILLS/scripts/"
else
  echo "  = No scripts found (skipped)"
fi

# Copy quickstart reference if it exists
if ls "$ROOT/skills/fablize/references/"*.md >/dev/null 2>&1; then
  cp "$ROOT/skills/fablize/references/"*.md "$HERMES_SKILLS/references/"
  echo "  ✓ Quickstart copied → $HERMES_SKILLS/references/"
fi

# ---- Determine scope ----
scope="${1:-}"

if [ "$scope" = "--skill-only" ]; then
  echo ""
  echo "✓ fablize-for-hermes skill installed."
  echo "  Load with:  skill_view(name='fablize')"
  echo "  Or set as default in ~/.hermes/config.yaml"
  echo ""
  echo "  To also inject the operating block into AGENTS.md/CLAUDE.md:"
  echo "    bash $ROOT/setup/setup.sh --local   (project-only)"
  echo "    bash $ROOT/setup/setup.sh --global  (all projects)"
  exit 0
fi

# ---- Inject operating block ----
BLOCK_TPL="$ROOT/setup/fablize-block.md"
command -v python3 >/dev/null 2>&1 || { echo "fablize: python3 is required."; exit 1; }
[ -f "$BLOCK_TPL" ] || { echo "fablize: block template not found ($BLOCK_TPL)"; exit 1; }

case "$scope" in
  --global) TARGET_MD="$HOME/.claude/CLAUDE.md" ;;
  --local|"") TARGET_MD="$PWD/AGENTS.md" ;;
  *) echo "fablize: unknown scope '$scope'. Use --skill-only, --local, or --global."; exit 1 ;;
esac

echo "  Injecting block → $TARGET_MD"
mkdir -p "$(dirname "$TARGET_MD")"; touch "$TARGET_MD"
ts=$(python3 -c "import time;print(int(time.time()))")
cp "$TARGET_MD" "$TARGET_MD.fablize-bak.$ts" && echo "  backup: $TARGET_MD.fablize-bak.$ts"

python3 - "$TARGET_MD" "$BLOCK_TPL" "$ROOT" <<'PY'
import sys, re, pathlib
md, tpl, root = sys.argv[1], sys.argv[2], sys.argv[3]
p = pathlib.Path(md)
cur = p.read_text(encoding="utf-8") if p.exists() else ""
block = pathlib.Path(tpl).read_text(encoding="utf-8").strip().replace("__HERMES_FABLIZE_ROOT__", root)
cur = re.sub(r"<!-- FABLIZE:BEGIN.*?FABLIZE:END -->\n?", "", cur, flags=re.S).rstrip()
p.write_text((cur + "\n\n" + block + "\n") if cur else (block + "\n"), encoding="utf-8")
print("  ✓ Operating block injected (idempotent)")
PY

echo ""
echo "✓ fablize-for-hermes setup complete!"
echo "  Skill installed at: $HERMES_SKILLS/SKILL.md"
echo "  Block injected at:  $TARGET_MD"
echo ""
echo "  Uninstall: bash $ROOT/setup/uninstall.sh [--local|--global]"
echo "  ★ Star the upstream: $REPO_URL"
