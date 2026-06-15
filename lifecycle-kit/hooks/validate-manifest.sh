#!/bin/sh
# lifecycle-kit SessionStart validation.
#
# Checks that the consuming project has a usable .claude/lifecycle-manifest.md
# before the lifecycle skills try to read it, so a missing or malformed manifest
# surfaces as one clear message instead of a cryptic failure mid-/session-end.
#
# Dependency-free on purpose: sh + git + grep only. No YAML parser, so the
# structural check is "required keys are present", not a full parse.
#
# Non-blocking: SessionStart hooks never abort the session. On a problem this
# emits a SessionStart JSON payload (systemMessage for the user, additionalContext
# for the model) and exits 0. When all is well it prints nothing.

emit() {
  # $1: single-line message (no double quotes, backslashes, or control chars)
  printf '{"systemMessage":"%s","hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$1" "$1"
}

TOPLEVEL=$(git rev-parse --show-toplevel 2>/dev/null) || exit 0   # not a git repo: nothing to validate
MANIFEST="$TOPLEVEL/.claude/lifecycle-manifest.md"

if [ ! -f "$MANIFEST" ]; then
  emit "lifecycle-kit: no .claude/lifecycle-manifest.md. Copy lifecycle-kit/lifecycle-manifest.template.md to .claude/lifecycle-manifest.md and fill it (see the kit README)."
  exit 0
fi

msg=""

# Required keys the skills cannot run without.
missing=
for key in product_name remote integration_ref local_main pr_base branch_pattern branch_glob \
           log_dir log_pattern log_presence_regex build_commands test_commands merge_strategy; do
  grep -qE "^${key}:" "$MANIFEST" || missing="$missing $key"
done
[ -n "$missing" ] && msg="lifecycle-kit: manifest missing required key(s):$missing. See lifecycle-kit/lifecycle-manifest.template.md for the full set."

# requires_remote (default true) needs a real remote configured.
if ! grep -qE "^requires_remote:[[:space:]]*false" "$MANIFEST"; then
  remote=$(grep -E "^remote:" "$MANIFEST" | head -1 | sed -E 's/^remote:[[:space:]]*//; s/[[:space:]]*#.*$//')
  [ -n "$remote" ] || remote=origin
  if ! git remote | grep -qx "$remote"; then
    rmsg="lifecycle-kit: requires_remote is set but git remote '$remote' is not configured; the finalize/cleanup lifecycle needs a fetchable remote (report and read-only briefing still work)."
    [ -n "$msg" ] && msg="$msg $rmsg" || msg="$rmsg"
  fi
fi

[ -n "$msg" ] && emit "$msg"
exit 0
