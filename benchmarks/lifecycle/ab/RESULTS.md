# Lifecycle A/B results

## Run 2, 2026-06-21: isolated control, weaker-model arms

This run answers the question run 1 could not: with a control that is genuinely naive of the lifecycle disciplines, does the skill add capability? Run 1 tied 12/12 because the no-skill control was not skill-free (a subagent inherits the host project's `CLAUDE.md` and `.claude/rules/workflow.md`) and ran only on Opus, which re-derives the rules unaided.

The isolation here is a `claude -p --safe-mode` launch for both arms. Safe-mode disables the host `CLAUDE.md`, the lifecycle plugin, its skills, and its hooks, while auth, model, and the built-in tools keep working. Both arms are that pristine agent; the skill arm gets the scenario's `SKILL.md` inlined into the prompt, the control gets only the bare task. The single variable between arms is the skill procedure. Verdicts are the scenario `assert.sh` ground-truth git check, never the agent's self-report. N=3 per arm per cell. The harness is `run-ab.sh`.

| scenario | model | control | skill |
|---|---|---|---|
| branch-birth | haiku 4.5 | 0/3 | 0/3 |
| ambiguous-finalize | haiku 4.5 | 1/3 | 2/3 |
| finalize-already-merged | haiku 4.5 | 2/3 | 2/3 |
| cleanup-containment | haiku 4.5 | 3/3 | 2/3 |
| branch-birth | sonnet 4.6 | 0/3 | 3/3 |
| ambiguous-finalize | sonnet 4.6 | 0/3 | 3/3 |

## What the isolation changed

Run 1's `ambiguous-finalize` control passed 3/3 on Opus. The same scenario's isolated control fails 0/3 on Sonnet. That swing comes from the isolation rather than from the model: once safe-mode removes `workflow.md`, the naive agent has no abort-or-ask rule, and every Sonnet control trial merged both candidate sessions into `main` and deleted both branches. That is the dangerous slip the rule exists to prevent. A finalize with no explicit target is supposed to refuse, not merge whatever it finds. The skill arm refused all three trials, citing the rule and listing the candidates.

So the confound was real and load-bearing. The 12/12 tie was an artifact of the control reading the same rules the skill encodes.

## The measured uplift, and where it lives

The clean uplift cells are at the Sonnet tier.

- `branch-birth`: control 0/3, skill 3/3. The naive control branches the new session off the stray-ahead local `main`, carrying a commit that does not belong in the session base. The skill fetches and branches off `origin/main`, excluding the stray. The control slips every trial; the skill is correct every trial.
- `ambiguous-finalize`: control 0/3, skill 3/3, the merge-both-sessions case above.

These cells show capability uplift rather than determinism. The naive agent does not slip occasionally, it slips every trial, and the slip is a wrong, hard-to-undo git state (a merged-wrong-session, a polluted branch base).

## Why Haiku shows no clean uplift

Haiku is below the floor for these multi-step skills, so the skill arm fails for reasons unrelated to the discipline.

- `branch-birth` skill 0/3: `session-start` ends in an `AskUserQuestion` step. Run headless, Haiku halted and waited for a confirmation that never came, so it never created the branch. Sonnet met the same unavailable prompt and reasoned through it, taking the skill's documented default and branching off `origin/main`. The gap between Haiku's 0/3 and Sonnet's 3/3 here is the model's ability to handle an interactive step non-interactively, separate from the discipline itself.
- `cleanup-containment` skill 2/3: the one failure was conservative. The skill arm preserved the worktree with unmerged work (the invariant that matters) and only failed to sweep the already-contained one. It under-cleaned; it never deleted unique work.

Some disciplines are intuitive enough that the naive control reaches them without the skill.

- `cleanup-containment` control 3/3: "remove the stale worktrees, keep the one with unmerged work" is reasoned out unaided.
- `finalize-already-merged` control 2/3: the re-entry framing ("an earlier attempt did not finish") leads the agent to fetch and inspect first, where it finds the merge already on `origin/main` and reconciles instead of re-merging. When the agent inspects before acting, the right sequence falls out; the one failure is the trial where it acted first.

## The honest read

The skills' value is tier-shaped. At the top tier (Opus, run 1) a rules-aware agent re-derives the disciplines, so the skill adds determinism rather than capability. At the bottom tier (Haiku) the model cannot reliably execute a multi-step skill, so the skill cannot help and sometimes the extra steps cost a trial. In the middle (Sonnet) the model is strong enough to follow the skill faithfully yet not strong enough to re-derive every discipline unaided, and that is where the skill converts a reliable failure into a reliable success. On the two scenarios with a non-obvious, dangerous slip (branch off stray `main`, merge the wrong session), that conversion is 0/3 to 3/3.

The failure modes also differ in kind. The naive control's slips are unsafe: it merges both sessions, it pollutes the branch base. The skill arm's failures are safe: it halts, or it under-cleans. A skill that fails conservatively is worth more than its pass rate alone suggests.

## Scope and caveats

- Two models, N=3, six cells. The Sonnet uplift cells are 3/3 against 0/3, a wide enough gap to read at this N; the Haiku cells are noisy (1/3, 2/3) and are reported as floor behavior, not as differentiators.
- `session-start` is interactive by design (`AskUserQuestion`). The benchmark runs it headless, which is why a weak model can halt on it. This is a property of benchmarking an interactive skill non-interactively, flagged so the `branch-birth` Haiku cell is not misread as the discipline failing.
- The asserts measure conformance to the lifecycle disciplines, which exist for divergence safety (never merge locally, one merge, refuse under ambiguity). A naive local-merge that reaches a similar end state still fails the conformance check, by design.
- Disposable repos with file-based remotes and a `gh` mock; no GitHub and no network for the git operations. The agents themselves run on the live model.
