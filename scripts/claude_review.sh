#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"

if git diff --quiet "${BASE_REF}...HEAD"; then
  echo "No changes against ${BASE_REF}; skipping review." >&2
  exit 0
fi

# Schema generated from the Pydantic models: one source of truth
SCHEMA="$(uv run --with pydantic python models.py)"

git diff "${BASE_REF}...HEAD" | claude -p \
  "The input on stdin is a unified diff of a pull request. Review it for bugs, security issues and missing error handling." \
  --output-format json \
  --json-schema "$SCHEMA" \
  --max-turns 3 \
  | jq -e '.structured_output'
  