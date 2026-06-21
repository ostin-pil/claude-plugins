#!/bin/sh
# Drive the isolated-control A/B across the cells in matrix.txt.
#   run-matrix.sh [N]   N = trials per arm per cell (default 3)
# Each cell runs both arms (control, skill) N times via run-ab.sh, then tally.sh
# prints the summary. Runs are sequential on purpose: one autonomous claude agent
# at a time keeps the load predictable and the logs readable.
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
N="${1:-3}"
CELLS_FILE="${LCK_CELLS_FILE:-$HERE/matrix.txt}"

while IFS= read -r line; do
  case "$line" in ''|\#*) continue;; esac
  SCEN=$(printf '%s\n' "$line" | awk '{print $1}')
  MODEL=$(printf '%s\n' "$line" | awk '{print $2}')
  [ -n "$SCEN" ] && [ -n "$MODEL" ] || continue
  for ARM in control skill; do
    i=1
    while [ "$i" -le "$N" ]; do
      bash "$HERE/run-ab.sh" "$SCEN" "$ARM" "$MODEL" "$i" || true
      i=$((i + 1))
    done
  done
done < "$CELLS_FILE"

echo ""
bash "$HERE/tally.sh"
