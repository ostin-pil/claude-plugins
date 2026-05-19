#!/bin/sh
# Fallback-chain shim (staged by prose-lint P1b; do not hand-edit).
# Same resolution order as check-prose.sh. The vendored fallback
# check-prose-bulk-impl.py still resolves its per-file scanner as
# check-prose.sh (this shim), so the fallback path stays consistent.
DIR=$(cd "$(dirname "$0")" && pwd)
if command -v prose-lint >/dev/null 2>&1; then
  exec prose-lint bulk "$@"
elif [ -x "$HOME/Projects/prose-lint/bin/prose-lint" ]; then
  exec "$HOME/Projects/prose-lint/bin/prose-lint" bulk "$@"
else
  exec python3 "$DIR/check-prose-bulk-impl.py" "$@"
fi
