#!/usr/bin/env bash
# Daily publisher for the Middle East brief GitHub Pages site.
# Uses your already-logged-in Git/GitHub identity. No tokens stored here.
set -euo pipefail

# Always operate from the folder this script lives in.
cd "$(dirname "$0")"

DATE="$(date +%F)"                 # YYYY-MM-DD
STAMP="$(date '+%F %H:%M')"

# Archive today's page before committing.
mkdir -p archive
cp -f index.html "archive/${DATE}.html"

# Stage everything, commit with a timestamped message, push to origin main.
git add -A
if git diff --cached --quiet; then
  echo "No changes to publish."
else
  git commit -m "Update Middle East brief ${STAMP}"
  git push origin main
  echo "Published: ${STAMP}"
fi