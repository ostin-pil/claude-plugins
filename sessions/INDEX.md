# Session log index

Named by `log_index` in `.claude/lifecycle-manifest.md`. One row per log in
`sessions/`, oldest first. The logs are the record; this is the way into them.

Each log's own header carries its date, branch and type, and the PR that landed
it is the merge commit naming that branch (`git log --merges --oneline`).

Filenames follow `log_pattern`, `{date}_session_{n}[_{suffix}].md`. The session
number is minted once, by `session-start`, and claimed by the branch name; a
session's unique key is the filename, not the bare number, because parallel
workstreams off one session share `n` with different suffixes.

| # | Date | Type | Log | What it was about |
| --- | --- | --- | --- | --- |
| 1 | 2026-08-05 | fix | [session-start acts on a stale read](./2026-08-05_session_1.md) | The fix was three lines. Most of the session went on why a fix to source never reaches a running Claude Code, and the version-is-the-update-key rule that came out of it. |
| 2 | 2026-08-05 | feat | [a regression test for session 1's fix](./2026-08-05_session_2.md) | A git shim that mutates the repo while the agent is mid-run, and the reasoning that the session number, not the branch base, is the value carrying a stale read. |
| 3 | 2026-08-05 | chore | [prose-mint 0.1.1 actually published](./2026-08-05_session_3.md) | The release was one button away for eight days. A failed run is evidence about a moment, and a bump is worth only what it would actually ship. |
| 4 | 2026-08-07 | docs | [a benchmark that passes for the wrong reason](./2026-08-07_session_4.md) | Session 2's regression test passes on both sides of the fix it was written for, which is a fact about the harness. Plus four cleanup items and one correction to session 3. |
| 5 | 2026-08-07 | feat | [the harness can watch, it just cannot ask](./2026-08-07_session_5.md) | Answers session 4's open question and partly overturns it. Distrusting the agent's self-report does not rule out asserting on the mock's own log, so the scenario discriminates after all. |
