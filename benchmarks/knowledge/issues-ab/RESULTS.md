# Issues A/B results

One scenario harness for the `issues` skill, covering `add`, `verify`, and `search` (folded from the former `issues-ab` and `issues-ops-ab`). The authoritative run below uses the command-sliced inline: the skill arm gets only the relevant command's slice of SKILL.md, not the whole file. The earlier full-file-inline run is kept at the bottom for the before/after, because the slice changed the `search` cell.

## Run 2026-06-25 (command-sliced inline)

Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin, skills, or hooks; auth and tools intact). The control gets the goal but not the procedure; the skill arm gets the one relevant `### /issues <cmd>` block plus the shared head and tail. N=3 per arm per model. All 54 trials completed with agent rc=0 (no agent errors).

### add

`assert-add.py` on the tracker: all five planted entries preserved, exactly one new entry at the next sequential id (ISS-006), canonical fields present.

| model | arm | pass | preserved | seq | schema |
|---|---|---:|---:|---:|---:|
| haiku 4.5 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| haiku 4.5 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | skill | 3/3 | 3/3 | 3/3 | 3/3 |

A complete tie, every tier, every check. `issues add` is self-documenting: the agent reads the tracker to find the next id, and once the file is open the format, the highest id, and the five existing entries are in front of it. The control reconstructs the convention by copying what it sees, even on Haiku. Where the discipline is reconstructable from the artifact, the skill adds determinism, not capability. The tracker is its own spec.

### verify

Four "Resolved (verify)" issues (two fixes held, two reverted), two non-target issues that must not change. `assert-verify.py` scores the transitions and breaks out `detected` (noticed the fix was gone, whatever word) from `regressed` (used the canonical `Regressed`).

| model | arm | pass | targets | regressed | detected | nontargets |
|---|---|---:|---:|---:|---:|---:|
| haiku 4.5 | control | 0/3 | 1.3/4 | 0/2 | 2.0/2 | 2/2 |
| haiku 4.5 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| sonnet 4.6 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| sonnet 4.6 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| opus 4.8 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| opus 4.8 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |

The pass rate looks like a rout (skill 9/9, control 0/9), but `detected` is what happened. On every control trial at every tier the control read the referenced files and noticed both reverted fixes were gone (`detected` 2/2, now uniform across all three tiers). It did the verification. What it never did was use the project's status word for a lost fix: Haiku wrote `Reverted`, Sonnet wrote `Open`, neither wrote `Regressed`, so `regressed` is 0/2 across all nine control trials and the strict transition check fails. The skill gives the status schema, not the capability to verify. The value is load-bearing here only because the divergence (a fragmented Status field) is invisible to the agent that caused it and breaks any filter keyed on `Status: Regressed`.

### search

One issue whose only "thermal throttling" link lives in a session log, not its tracker entry. `assert-search.py` scores whether the agent's report cites the log-only match (ISS-207).

| model | arm | pass (found ISS-207) | note |
|---|---|---:|---|
| haiku 4.5 | control | 3/3 | searched the session logs unprompted |
| haiku 4.5 | skill | 3/3 | |
| sonnet 4.6 | control | 0/3 | searched only the tracker, reported "no such issue" |
| sonnet 4.6 | skill | 3/3 | |
| opus 4.8 | control | 3/3 | searched the session logs unprompted |
| opus 4.8 | skill | 3/3 | |

With the prompt-weight handicap removed, a real effect shows: the skill arm finds the log-only match 9 of 9, and all three control misses are Sonnet searching only the tracker and confidently reporting that no such issue exists. The skill's "grep the session logs as well as the tracker" instruction is the difference, and it matters most on the tier that does not do it unprompted. The effect is tier-dependent in this fixture (Haiku and Opus controls both searched the logs on their own, 3/3), so the honest framing is consistency: the skill removes the variance of whether a given tier remembers to look past the tracker, and Sonnet is the tier that needs it.

## What the section-slice changed

The earlier harness inlined the whole SKILL.md (four command blocks plus manifest resolution) into the skill arm even on a one-command task. On `search`, a one-line grep, that weight cost the skill arm trials: it ran the agent out of turns or into an error.

| search cell | full-file inline (prior) | command-sliced (now) |
|---|---|---|
| skill arm | 6/9, three of the misses agent errors (rc=1) | 9/9, zero agent errors |
| control arm | 7/9 | 6/9 |

The skill arm's losses were the harness, not the skill: once the inline carries only the `search` block, the skill arm is clean and the underlying effect (the log search) is visible. `add` and `verify` were already decisive and did not move; the slice only mattered where the task was light enough that prompt weight dominated. The control's 7/9 to 6/9 wobble is within the noise of a tier-dependent habit at N=3.

## The honest read, for the whole issues skill

Across its three measured commands the `issues` skill adds consistency, and on `search` and `verify` that consistency is doing real work. `add` ties because the tracker is self-documenting. `verify` is a strict-pass rout that, read honestly, is a vocabulary-conformance win on top of a capability the control already has (it detects every regression, it just names it wrong). `search` is consistency too, but consequential: the skill guarantees the log search that one tier skips, turning a confident wrong "no such issue" into the right answer. This fits the suite-wide pattern. Capability uplift concentrates in genuine judgment calls and high-recall scans the agent cannot match by eye; tracker bookkeeping is mostly reconstructable, leaving the skill as schema, vocabulary, and habit insurance. That insurance is not nothing, most clearly when the naive divergence is silent.

## Scope and caveats

- N=3 per cell, one fixture per scenario. The add tie and the verify split are uniform across tiers, so not small-sample artifacts. The search effect rests on Sonnet's consistent tracker-only behavior (0/3) against a deterministic skill arm (9/9); a larger control N would sharpen the cross-tier rate but the skill-vs-Sonnet-control gap is clean.
- The verify control's failure is a strict-conformance failure (wrong status word), not a missed regression; `detected` is reported precisely so it is not misread as "the control cannot verify."
- The search assert scores the agent's final report for the issue id. This run had no agent errors, so every miss is a genuine search miss, not a harness artifact.
