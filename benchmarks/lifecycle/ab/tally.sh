#!/bin/sh
# Summarize ab/runs/tally.psv into a scenario x model x arm pass-rate matrix.
# Reads the PSV the runner appends (SCEN|ARM|MODEL|TRIAL|VERDICT|RC|REPO).
set -u
HERE=$(cd "$(dirname "$0")" && pwd)
PSV="${1:-$HERE/runs/tally.psv}"
[ -f "$PSV" ] || { echo "no tally at $PSV"; exit 1; }

awk -F'|' '
  { key=$1"|"$3; tot[key"|"$2]++; if($5=="PASS") pass[key"|"$2]++;
    seen[key]=1; scen[key]=$1; model[key]=$3 }
  END {
    printf "%-24s %-28s %-9s %-9s\n", "scenario", "model", "control", "skill"
    printf "%-24s %-28s %-9s %-9s\n", "------------------------", "----------------------------", "--------", "--------"
    for (k in seen) {
      c = (pass[k"|control"]+0)"/"(tot[k"|control"]+0)
      s = (pass[k"|skill"]+0)"/"(tot[k"|skill"]+0)
      printf "%-24s %-28s %-9s %-9s\n", scen[k], model[k], c, s
    }
  }
' "$PSV" | (head -2; tail -n +3 | sort)
