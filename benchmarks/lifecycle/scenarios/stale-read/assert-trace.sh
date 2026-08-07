#!/bin/sh
# The process assertion for the stale-read scenario, split out so it can be
# regression-tested against recorded traces without running an agent.
# Usage: assert-trace.sh <git-mock-log>. Exit 0 pass, 1 fail, 2 unusable.
#
# Why this exists. assert.sh's other checks read end-state git, and the
# 2026-08-07 run proved that end state cannot separate the fixed skill from
# the unfixed one: both arms minted session 7 and both passed every outcome
# check. A skill that re-reads because it was told to and one that re-reads
# because the agent got suspicious leave identical repositories behind.
#
# What does separate them is the ORDER of commands, which the shim records.
# The fix prescribes a re-fetch at the top of branch birth, before the session
# number is computed. The session number's branch source is a `git branch
# --list '*session-*'` read. So on a fixed skill that read is preceded by two
# fetches (step 1's and step 7's); on an unfixed one, by step 1's alone.
#
# This is a proxy, not a proof of intent. An unfixed skill whose operator
# happens to fetch twice before the pre-flight will pass. It is strictly more
# than the outcome checks can see, and it fails the recorded pre-fix trace,
# which is the property that matters.
set -u

TRACE="${1:?usage: assert-trace.sh <git-mock-log>}"

if [ ! -f "$TRACE" ]; then
  echo "UNUSABLE: no shim trace at $TRACE; the re-read cannot be checked"
  exit 2
fi

first_read=$(grep -n "branch .*--list .*session" "$TRACE" | head -1 | cut -d: -f1)

if [ -z "$first_read" ]; then
  echo "FAIL: session branches were never listed; the pre-flight's branch source was skipped"
  exit 1
fi

fetches_before=$(head -n "$((first_read - 1))" "$TRACE" | grep -c "fetch")

if [ "$fetches_before" -ge 2 ]; then
  echo "ok: $fetches_before fetches precede the first session-branch read (line $first_read)"
  exit 0
fi

echo "FAIL: only $fetches_before fetch precedes the first session-branch read (line $first_read)"
echo "      the session number was computed from the step-1 snapshot, not a re-read"
exit 1
