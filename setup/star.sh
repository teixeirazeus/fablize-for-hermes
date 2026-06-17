#!/usr/bin/env bash
# fablize-for-hermes — star the repo on GitHub via gh.
# Consent is obtained by the setup prompt that calls this, so it does not ask again.
# Fail-silent: never blocks. Skips if already starred or gh is unavailable.
set -uo pipefail
REPO="zeus/fablize-for-hermes"

if gh auth status &>/dev/null; then
  if gh api "user/starred/$REPO" &>/dev/null; then
    echo "★ fablize-for-hermes already starred — thank you!"
  elif gh api -X PUT "/user/starred/$REPO" &>/dev/null; then
    echo "★ Starred fablize-for-hermes on GitHub — thank you!"
  else
    echo "Could not star automatically — star here: https://github.com/$REPO"
  fi
else
  echo "Sign in to gh (\`gh auth login\`) to auto-star next time, or star here: https://github.com/$REPO"
fi
exit 0
