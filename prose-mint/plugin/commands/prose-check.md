---
description: Scan a markdown file or PR body for structural AI-prose tells via prose-mint
argument-hint: "[path | PR-number] (empty = current branch's PR)"
allowed-tools: [Bash, Read]
---

Run a prose-mint scan on `$ARGUMENTS`.

Resolve the tool in order: `prose-mint` on `PATH`, then
`~/Projects/prose-mint/bin/prose-mint`. If neither exists, report that
prose-mint is not installed and stop.

Dispatch on `$ARGUMENTS`:

- empty: scan the current branch's PR
  (`gh pr view --json number,title,body`; if none, ask for a path or PR
  number)
- a number or `#NNN`:
  `gh pr view NNN --json title,body -q '.title + "\n\n" + .body' | <tool> scan --stdin --label "PR #NNN"`
- a path: `<tool> scan --file $ARGUMENTS`

Print the output verbatim. Read-only: do not edit the file or PR body, and
do not restate the counts as prose. Offer rewrite suggestions for the
top category only if the user asks.
