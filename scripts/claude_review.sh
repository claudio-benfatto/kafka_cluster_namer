#!/usr/bin/env bash
set -euo pipefail

BASE_REF="${BASE_REF:-origin/main}"

if git diff --quiet "${BASE_REF}...HEAD"; then
  echo "No changes against ${BASE_REF}; skipping review." >&2
  exit 0
fi

# Schema generated from the Pydantic models: one source of truth
SCHEMA="$(uv run --with pydantic python models.py)"

# Keep Claude's full JSON envelope so a failure can be diagnosed: on errors
# (auth, max turns, schema retries) it has no .structured_output, and the
# reason is in .subtype / .result.
RESPONSE="$(git diff "${BASE_REF}...HEAD" | claude -p \
  "The input on stdin is a unified diff of a pull request. Review it for bugs, security issues and missing error handling." \
  --output-format json \
  --json-schema "$SCHEMA" \
  --max-turns 3)" || {
  echo "claude exited with an error. Output:" >&2
  echo "$RESPONSE" >&2
  exit 1
}

if ! echo "$RESPONSE" | jq -e '.structured_output'; then
  echo "No structured_output in Claude's response:" >&2
  echo "$RESPONSE" | jq '{subtype, is_error, num_turns, result}' >&2 || echo "$RESPONSE" >&2
  exit 1
fi
