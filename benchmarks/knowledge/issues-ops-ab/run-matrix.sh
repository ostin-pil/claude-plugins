#!/bin/sh
# Drive the issues verify/search A/Bs across models.
#   run-matrix.sh [N]    N = trials per arm per model per scenario (default 3)
# Scenarios from $KAB_SCENARIOS (default "verify search"); models from
# $KAB_MODELS (default haiku/sonnet/opus). Sequential.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
N="${1:-3}"
SCENARIOS="${KAB_SCENARIOS:-verify search}"
MODELS="${KAB_MODELS:-claude-haiku-4-5-20251001 claude-sonnet-4-6 claude-opus-4-8}"

for SCEN in $SCENARIOS; do
  for MODEL in $MODELS; do
    for ARM in control skill; do
      i=1
      while [ "$i" -le "$N" ]; do
        sh "$HERE/run-ab.sh" "$SCEN" "$ARM" "$MODEL" "$i" || true
        i=$((i + 1))
      done
    done
  done
done

echo ""
python3 "$HERE/tally.py"
