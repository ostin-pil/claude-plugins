#!/bin/sh
# Regression test for assert-trace.sh, run against two traces recorded on
# 2026-08-07 from real agent runs of session-start:
#
#   fixtures/pre-fix-0.2.0.log   lifecycle-kit 0.2.0, before the re-read fix
#   fixtures/post-fix-0.2.2.log  lifecycle-kit 0.2.2, after it
#
# Both runs minted session 7 and both passed every end-state check, which is
# why this scenario needs a process assertion at all. This selftest keeps that
# assertion honest without spending two agent runs to find out it broke.
#
# Usage: selftest.sh. Exit 0 all pass, 1 otherwise.
set -u

DIR=$(unset CDPATH; cd -- "$(dirname -- "$0")" && pwd)
fail=0

expect() {
  want="$1"; trace="$2"; label="$3"
  "$DIR/assert-trace.sh" "$DIR/fixtures/$trace" >/dev/null 2>&1
  got=$?
  if [ "$got" = "$want" ]; then
    echo "ok:   $label (exit $got)"
  else
    echo "FAIL: $label expected exit $want, got $got"
    fail=1
  fi
}

expect 1 pre-fix-0.2.0.log  "pre-fix trace is rejected"
expect 0 post-fix-0.2.2.log "post-fix trace is accepted"

"$DIR/assert-trace.sh" "$DIR/fixtures/does-not-exist.log" >/dev/null 2>&1
got=$?
if [ "$got" = "2" ]; then
  echo "ok:   a missing trace is unusable, not a pass (exit 2)"
else
  echo "FAIL: missing trace expected exit 2, got $got"
  fail=1
fi

echo "VERDICT: $([ $fail -eq 0 ] && echo PASS || echo FAIL)"
exit $fail
