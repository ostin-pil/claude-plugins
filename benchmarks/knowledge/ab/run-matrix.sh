#!/bin/sh
# Drive the session-archive scrub A/B across models.
#   run-matrix.sh [N]   N = trials per arm per model (default 3)
# Models come from $KAB_MODELS (space-separated) or default to haiku/sonnet/opus.
# Runs sequentially: one autonomous claude agent at a time.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
N="${1:-3}"
MODELS="${KAB_MODELS:-claude-haiku-4-5-20251001 claude-sonnet-4-6 claude-opus-4-8}"

for MODEL in $MODELS; do
  for ARM in control skill; do
    i=1
    while [ "$i" -le "$N" ]; do
      sh "$HERE/run-ab.sh" "$ARM" "$MODEL" "$i" || true
      i=$((i + 1))
    done
  done
done

echo ""
python3 "$HERE/tally.py"
