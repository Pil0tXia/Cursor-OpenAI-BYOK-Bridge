#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
GH_BIN="${GH_BIN:-gh}"
REPO="Pil0tXia/Cursor-OpenAI-BYOK-Bridge"
BRANCH="fix/dedupe-v1-upstream-url"
GIT=/usr/bin/git

cd "$ROOT_DIR"

if ! command -v "$GH_BIN" >/dev/null 2>&1; then
  echo "gh not found. Set GH_BIN or install GitHub CLI." >&2
  exit 1
fi

if ! "$GH_BIN" auth status >/dev/null 2>&1; then
  echo "GitHub CLI is not authenticated. Run: gh auth login" >&2
  exit 1
fi

"$GH_BIN" repo fork "$REPO" --clone=false --remote=false || true
FORK="$("$GH_BIN" api user -q .login)/Cursor-OpenAI-BYOK-Bridge"

"$GIT" push "git@github.com:${FORK}.git" "$BRANCH:$BRANCH" --force

ISSUE_URL="$("$GH_BIN" issue create \
  --repo "$REPO" \
  --title "Upstream requests hit /v1/v1/... and return 404" \
  --body-file "$ROOT_DIR/contrib/upstream-issue-body.md")"

FORK_OWNER="${FORK%%/*}"
ISSUE_NUM="${ISSUE_URL##*/}"

"$GH_BIN" pr create \
  --repo "$REPO" \
  --head "${FORK_OWNER}:${BRANCH}" \
  --base main \
  --title "fix: dedupe /v1 prefix when resolving upstream URLs" \
  --body "Fixes #${ISSUE_NUM}

$(cat "$ROOT_DIR/contrib/upstream-pr-body.md")"

echo "Issue: $ISSUE_URL"
