# Issues A/B results

This dir folds the former `issues-ab` (add) and `issues-ops-ab` (verify/search) into one scenario harness. The runs below were produced by the earlier harness, which inlined the **whole** SKILL.md into the skill arm. The harness now inlines only the command-relevant slice (see README). A re-run under the sliced harness is pending; the search cell is the one expected to move, because its skill-arm misses were attributed to prompt weight from the three irrelevant command blocks. The add and verify findings are not expected to change (the decisive cells are wide). The prior tables are kept here for the before/after comparison.

## add (run 2026-06-24, full-file inline)

Both arms add the same new bug to a tracker already holding ISS-001..005. Verdict is `assert-add.py`: all five originals preserved, exactly one new entry at the next sequential id (ISS-006), canonical fields present. N=3 per arm per model.

| model | arm | pass | preserved | seq | schema |
|---|---|---:|---:|---:|---:|
| haiku 4.5 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| haiku 4.5 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| sonnet 4.6 | skill | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | control | 3/3 | 3/3 | 3/3 | 3/3 |
| opus 4.8 | skill | 3/3 | 3/3 | 3/3 | 3/3 |

Eighteen of eighteen pass, both arms, every tier. `issues add` is self-documenting: the agent reads the tracker to find the next id, and once the file is open the format, the highest id, and the five existing entries are all in front of it. The control reconstructs the convention by copying what it sees, on every trial, even on Haiku. Where the discipline is reconstructable from the artifact in front of the agent, the skill adds determinism, not capability. The tracker is its own spec.

## verify (run 2026-06-25, full-file inline)

`setup-verify.sh` plants four "Resolved (verify)" issues (two fixes held, two reverted) and two non-target issues that must not change. `assert-verify.py` scores the transitions and breaks out `detected` from `regressed`. N=3 per arm per model.

| model | arm | pass | targets | regressed | detected | nontargets |
|---|---|---:|---:|---:|---:|---:|
| haiku 4.5 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| haiku 4.5 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| sonnet 4.6 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| sonnet 4.6 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| opus 4.8 | control | 0/3 | 1.3/4 | 0/2 | 0/2 (rc=1) | 2/2 |
| opus 4.8 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |

The pass rate looks like a rout (skill 9/9, control 0/9), but `detected` is what actually happened. On every completed control trial the control read the referenced files and noticed the two reverted fixes were gone (`detected` 2/2). It did the verification. What it never did was use the project's status word for a lost fix: Haiku wrote `Reverted`, Sonnet wrote `Open`, neither wrote `Regressed`, so `regressed` is 0/2 across all nine control trials and the strict transition check fails. The skill gives the agent the status schema, not the capability to verify. The value is load-bearing here only because the divergence (a fragmented Status field) is invisible to the agent that caused it and breaks any filter keyed on `Status: Regressed`.

## search (run 2026-06-25, full-file inline)

`setup-search.sh` plants an issue whose only "thermal throttling" link lives in a session log. `assert-search.py` scores whether the agent's report cites ISS-207. N=3 per arm per model.

| model | arm | pass (found ISS-207) | note |
|---|---|---:|---|
| haiku 4.5 | control | 3/3 | |
| haiku 4.5 | skill | 2/3 | the one miss was an agent error (rc=1) |
| sonnet 4.6 | control | 1/3 | two genuine misses (searched only the tracker) |
| sonnet 4.6 | skill | 2/3 | the one miss was an agent error (rc=1) |
| opus 4.8 | control | 3/3 | |
| opus 4.8 | skill | 2/3 | the one miss was an agent error (rc=1) |

No measurable skill effect. The control found the log-only match 7 of 9 times; the skill 6 of 9. All three skill-arm misses were agent errors (rc=1): the heavier inlined SKILL.md, with four commands and manifest resolution, occasionally ran the agent out of turns on what is otherwise a one-line grep. This is the cell the section-slice targets, so the re-run should remove that prompt-weight handicap.

## The honest read, for the whole issues skill

Across its three measured commands the `issues` skill adds consistency, not capability. `add` ties because the tracker is self-documenting. `verify` is a strict-pass rout that, read honestly, is a vocabulary-conformance win on top of a capability the agent already has. `search` shows no effect and some heavier-prompt cost (the cost the slice removes). This fits the suite-wide pattern: capability uplift concentrates in genuine judgment calls and high-recall scans the agent cannot match by eye, while tracker bookkeeping is reconstructable from the artifact or from common sense, leaving the skill as schema and vocabulary insurance.

## Scope and caveats

- N=3 per cell, one fixture per scenario. The add tie and the verify split are uniform, so not small-sample artifacts; the search result is noisy by nature and reported as a null, not a measured equality.
- The verify control's failure is a strict-conformance failure (wrong status word), not a missed regression; `detected` is reported precisely so it is not misread as "the control cannot verify."
- The search assert scores the agent's final report for the issue id; skill-arm agent errors (rc=1) count as failures, conservative against the skill.
