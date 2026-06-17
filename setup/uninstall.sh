#!/usr/bin/env bash
# fablize-for-hermes uninstall — remove the FABLIZE block from AGENTS.md/CLAUDE.md
# and optionally remove the skill.
# Usage: uninstall.sh [--skill-only|--local|--global|--all]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
scope="${1:-}"
REMOVE_SKILL=false

if [ "$scope" = "--all" ]; then
  REMOVE_SKILL=true
  scope="--local"
elif [ "$scope" = "--skill-only" ]; then
  REMOVE_SKILL=true
fi

# ---- Remove skill ----
if [ "$REMOVE_SKILL" = true ]; then
  if [ -d "$HOME/.hermes/skills/fablize" ]; then
    rm -rf "$HOME/.hermes/skills/fablize"
    echo "  ✓ fablize skill removed from ~/.hermes/skills/"
  else
    echo "  = no fablize skill found"
  fi
fi

[ "$scope" = "--skill-only" ] && { echo "fablize uninstall complete."; exit 0; }

# ---- Remove operating block ----
case "$scope" in
  --global) TARGET_MD="$HOME/.claude/CLAUDE.md" ;;
  --local|"") TARGET_MD="$PWD/AGENTS.md" ;;
  *) echo "fablize: unknown scope '$scope'."; exit 1 ;;
esac

if [ -f "$TARGET_MD" ]; then
  python3 - "$TARGET_MD" <<'PY'
import sys, re, pathlib
p = pathlib.Path(sys.argv[1])
cur = p.read_text(encoding="utf-8")
new = re.sub(r"\n*<!-- FABLIZE:BEGIN.*?FABLIZE:END -->\n?", "\n", cur, flags=re.S)
p.write_text(new, encoding="utf-8")
print("  ✓ FABLIZE block removed" if new != cur else "  = no FABLIZE block (already removed)")
PY
else
  echo "  = $TARGET_MD not found — nothing to remove."
fi

echo ""
echo "fablize-for-hermes uninstall complete."
echo "  Backups (*.fablize-bak.*) can be deleted manually if no longer needed."
