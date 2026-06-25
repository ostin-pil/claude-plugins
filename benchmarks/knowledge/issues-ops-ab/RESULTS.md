# Issues verify/search A/B results

## Run 2026-06-25: the issues commands whose procedure is not self-documenting

The `add` A/B tied because the tracker is its own spec. These two scenarios target the commands where the procedure is not visible in a single entry. Both arms run a fresh `claude -p --safe-mode` agent; the skill arm inlines the `issues` SKILL.md, the control gets the goal but not the procedure. N=3 per arm per model.

### verify

| model | arm | pass | targets | regressed | detected | nontargets |
|---|---|---:|---:|---:|---:|---:|
| haiku 4.5 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| haiku 4.5 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| sonnet 4.6 | control | 0/3 | 2.0/4 | 0/2 | 2.0/2 | 2/2 |
| sonnet 4.6 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |
| opus 4.8 | control | 0/3 | 1.3/4 | 0/2 | 1.3/2 | 2/2 |
| opus 4.8 | skill | 3/3 | 4.0/4 | 2/2 | 2/2 | 2/2 |

### search

| model | arm | pass (found ISS-207) | note |
|---|---|---:|---|
| haiku 4.5 | control | 3/3 | |
| haiku 4.5 | skill | 2/3 | the one miss was an agent error (rc=1) |
| sonnet 4.6 | control | 1/3 | two genuine misses (searched only the tracker) |
| sonnet 4.6 | skill | 2/3 | the one miss was an agent error (rc=1) |
| opus 4.8 | control | 3/3 | |
| opus 4.8 | skill | 2/3 | the one miss was an agent error (rc=1) |

## verify: the value is the status vocabulary, not the verification

The pass rate looks like a rout (skill 9/9, control 0/9), but the `detected` column is what actually happened. On every completed control trial at every tier, the control read the referenced files and noticed that the two reverted fixes were gone: `detected` is 2/2. It did the verification. What it never did was use the project's status word for a lost fix. Haiku wrote the reverted issues as `Reverted`, Sonnet wrote them as `Open`; neither wrote `Regressed`, so `regressed` is 0/2 across all nine control trials and the strict transition check fails. (The one opus control trial with `detected` 0/2 was an agent error, rc=1, not a missed regression.)

So the skill does not give the agent the capability to verify; even Haiku checks the files and catches the regression unaided. The skill gives it the schema. The four defined status values (Open, Resolved, Resolved (verify), Regressed) are the part a naive agent cannot reconstruct from the tracker, because no existing entry shows a `Regressed`, and each control invents a reasonable synonym instead. The result is a silently fragmented Status field: the control believes it finished, its prose is correct, and a filter that keys on `Status: Regressed` now misses the issues it most needs to surface. That is the same conformance value the other ties showed, but here it is load-bearing rather than cosmetic, because the divergence is invisible to the agent that caused it.

## search: no measurable skill effect

Searching the session logs as well as the tracker is the discipline `search` adds, and the A/B does not show it helping. The control found the log-only match 7 of 9 times; the skill found it 6 of 9. All three skill-arm misses were agent errors (rc=1): the heavier inlined SKILL.md, with four commands and manifest resolution, occasionally ran the agent out of turns or into an error on what is otherwise a one-line grep. The two genuine control misses were both Sonnet trials that searched only the tracker. So grepping beyond the tracker is a habit agents have inconsistently, with or without the skill, and the heavier skill prompt is as likely to cost a trial as to save one. There is no signal here that the skill instills the broader-search discipline reliably.

## The honest read, for the whole issues skill

Across its three measured commands the `issues` skill adds consistency, not capability. `add` ties because the tracker is self-documenting. `verify` is a strict-pass rout that, read honestly, is a vocabulary-conformance win on top of a capability the agent already has. `search` shows no effect and some heavier-prompt cost. This fits the suite-wide pattern: capability uplift concentrates in genuine judgment calls (the lifecycle ambiguity refusal) and high-recall scans the agent cannot match by eye (secret scrubbing), while tracker bookkeeping is either reconstructable from the artifact or reconstructable from common sense, leaving the skill as schema and vocabulary insurance. That insurance is still worth something, most clearly on `verify`, where the naive divergence is silent and breaks tooling, but it is not capability.

## Scope and caveats

- N=3, one fixture per scenario. The verify result is uniform (every skill trial 4/4, every completed control trial 2/4 with `detected` 2/2), so the qualitative split is not a small-sample artifact; the search result is noisy by nature and is reported as a null, not a measured equality.
- The verify control's failure is a strict-conformance failure (wrong status word), not a missed regression. The `detected` metric is reported precisely so the result is not misread as "the control cannot verify."
- The search assert scores the agent's final report for the issue id; the skill-arm agent errors (rc=1) are counted as failures, which is conservative against the skill.
