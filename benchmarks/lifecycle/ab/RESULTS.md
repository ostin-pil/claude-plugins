# Lifecycle A/B results

## Run 2, 2026-06-21/22: isolated control across three model tiers

This run answers the question run 1 could not: with a control that is genuinely naive of the lifecycle disciplines, does the skill add capability? Run 1 tied 12/12 because the no-skill control was not skill-free (a subagent inherits the host project's `CLAUDE.md` and `.claude/rules/workflow.md`) and ran only on Opus, where a tie was wrongly read as the model re-deriving the rules.

The isolation here is a `claude -p --safe-mode` launch for both arms. Safe-mode disables the host `CLAUDE.md`, the lifecycle plugin, its skills, and its hooks, while auth, model, and the built-in tools keep working. Both arms are that pristine agent; the skill arm gets the scenario's `SKILL.md` inlined into the prompt, the control gets only the bare task. The single variable between arms is the skill procedure. Verdicts are the scenario `assert.sh` ground-truth git check, never the agent's self-report. N=3 per arm per cell. The harness is `run-ab.sh`.

| scenario | model | control | skill |
|---|---|---|---|
| branch-birth | haiku 4.5 | 0/3 | 0/3 |
| branch-birth | sonnet 4.6 | 0/3 | 3/3 |
| branch-birth | opus 4.8 | 3/3 | 3/3 |
| ambiguous-finalize | haiku 4.5 | 1/3 | 2/3 |
| ambiguous-finalize | sonnet 4.6 | 0/3 | 3/3 |
| ambiguous-finalize | opus 4.8 | 1/3 | 3/3 |
| finalize-already-merged | haiku 4.5 | 2/3 | 2/3 |
| cleanup-containment | haiku 4.5 | 3/3 | 2/3 |

## What the isolation changed, and why the Opus arm matters

Run 1's `ambiguous-finalize` control passed 3/3 on Opus. The isolated control fails two of three on the same Opus tier (1/3). That swing is the whole point: the 3/3 was the control reading `workflow.md`, the rule the skill encodes. Strip the rule and even Opus does not reliably refuse.

The Opus transcripts show how it slips, and it is not for lack of seeing the problem. All three trials recognized the two equal candidates. Two then rationalized a pick anyway: one finalized `session-302-beta` because the reflog showed it was "most recently checked out"; another tried to ask, found the prompt unavailable, and chose to "go with the best evidence rather than stall." Only the third stopped ("they're all symmetric, I'm going to stop rather than guess, because finalizing is irreversible"). A strong agent left to its own judgment treats the disambiguation prompt as advisory and invents a tiebreak two times in three. The skill's rule (abort-or-ask, never auto-pick, and if the ask is unavailable, abort and list) removes that discretion, and the skill arm refused 3/3.

## Where the uplift lives: scenario-dependent, not tier-dependent

The two scenarios tell opposite stories, and that contrast is the finding.

`ambiguous-finalize` is tier-independent uplift. The isolated control never reliably refuses at any tier (haiku 1/3, sonnet 0/3, opus 1/3); the skill reliably refuses wherever it can execute (sonnet 3/3, opus 3/3). The refuse-under-ambiguity discipline is not something the model re-derives, not even Opus. This is the cell where the skill earns its keep, and run 1's confound hid it completely.

`branch-birth` is tier-shaped uplift. Here the discipline (fetch, branch off `origin/main`, exclude the stray-ahead local commit) is carried by the manifest's `integration_ref`, which a careful agent reads. Opus does (control 3/3); Sonnet does not bother and branches off local `main` (control 0/3, skill 3/3); Haiku cannot execute the multi-step `session-start` skill at all (both 0/3, below). So the skill's value on branch-birth is real at the middle tier and fades to determinism at the top, where the agent reads the manifest unaided.

## Why Haiku shows no clean uplift

Haiku is below the floor for these multi-step skills, so the skill arm fails for reasons unrelated to the discipline.

- `branch-birth` skill 0/3: `session-start` ends in an `AskUserQuestion` step. Run headless, Haiku halted and waited for a confirmation that never came, so it never created the branch. Sonnet met the same unavailable prompt and reasoned through it, taking the skill's documented default and branching off `origin/main`. The gap between Haiku's 0/3 and Sonnet's 3/3 here is the model's ability to handle an interactive step non-interactively, separate from the discipline itself.
- `cleanup-containment` skill 2/3: the one failure was conservative. The skill arm preserved the worktree with unmerged work (the invariant that matters) and only failed to sweep the already-contained one. It under-cleaned; it never deleted unique work.

Some disciplines are intuitive enough that the naive control reaches them without the skill.

- `cleanup-containment` control 3/3: "remove the stale worktrees, keep the one with unmerged work" is reasoned out unaided.
- `finalize-already-merged` control 2/3: the re-entry framing ("an earlier attempt did not finish") leads the agent to fetch and inspect first, where it finds the merge already on `origin/main` and reconciles instead of re-merging. When the agent inspects before acting, the right sequence falls out; the one failure is the trial where it acted first.

## The honest read

The skills' value is not a single number; it is scenario by scenario, and the dominant variable is whether the discipline is one the model re-derives. Where the discipline is reconstructable from the manifest or from common sense (branch off the integration ref, keep the worktree with unmerged work, reconcile an already-merged PR after inspecting), a strong agent gets it unaided and the skill adds determinism. Where the discipline is a judgment call the model will rationalize around (refuse to finalize under ambiguity rather than invent a tiebreak), the skill adds capability the model lacks on its own, at every tier including Opus.

The failure modes also differ in kind. The naive control's slips are unsafe: it merges the wrong session, it pollutes the branch base. The skill arm's failures are safe: it halts, or it under-cleans. A skill that fails conservatively is worth more than its pass rate alone suggests.

## Scope and caveats

- Three models, N=3. The decisive cells are wide (ambiguous-finalize skill 3/3 against control 0-1/3 at sonnet and opus; branch-birth 3/3 against 0/3 at sonnet). The haiku cells are noisy (1/3, 2/3) and are reported as floor behavior.
- `session-start` is interactive by design (`AskUserQuestion`). The benchmark runs it headless, which is why a weak model can halt on it and why the Opus `ambiguous-finalize` control's "the prompt was dismissed, so I went with the best evidence" is part of the slip, not a harness error: the skill's rule says abort when the ask is unavailable, and that is exactly what the control failed to do.
- The asserts measure conformance to the divergence-safety disciplines. A naive local-merge that reaches a similar end state still fails the conformance check, by design.
- Disposable repos with file-based remotes and a `gh` mock; no GitHub and no network for the git operations. The agents themselves run on the live model.
