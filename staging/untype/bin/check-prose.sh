#!/bin/sh
# Fallback-chain shim (staged by prose-lint P1b; do not hand-edit).
#
# Resolution order:
#   1. `prose-lint` on PATH                     (installed: pipx / uv tool)
#   2. ~/Projects/prose-lint/bin/prose-lint     (local checkout)
#   3. ./check-prose-impl.py                     (the vendored original)
#
# Local dev hits 1 or 2 (the shared tool). CI, which has no prose-lint,
# hits 3 and behaves exactly as before, so prose.yml needs no change and
# the prose-check skill keeps working. prose-lint is byte-identical to the
# original here (proven by the P0 regression gate and the real-repo dogfood).
DIR=$(cd "$(dirname "$0")" && pwd)
if command -v prose-lint >/dev/null 2>&1; then
  exec prose-lint scan "$@"
elif [ -x "$HOME/Projects/prose-lint/bin/prose-lint" ]; then
  exec "$HOME/Projects/prose-lint/bin/prose-lint" scan "$@"
else
  exec python3 "$DIR/check-prose-impl.py" "$@"
fi
