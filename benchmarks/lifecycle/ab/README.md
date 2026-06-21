# Lifecycle value A/B (skill vs no-skill)

The lifecycle execution scenarios test that an agent *running the skill* produces the correct git state. This A/B asks the next question: does the skill make a difference against a control that does not have it? It reuses each scenario's `setup.sh` and `assert.sh` and adds a control arm, the same task with no skill, judged by the same ground-truth assert.

## Isolation: why both arms run `--safe-mode`

The control is only fair if it is genuinely naive of the disciplines under test. A subagent spawned inside the host project is not: it inherits that project's `CLAUDE.md` and `.claude/rules/workflow.md`, which already encode "refuse under ambiguity," "branch off `origin/main`," and the rest. Run 1 tied 12/12 for exactly this reason (see `RESULTS.md`).

The fix is a `claude -p --safe-mode` launch for both arms. Safe-mode disables the host `CLAUDE.md`, the lifecycle plugin, its skills, and its hooks, while auth, model selection, and the built-in tools keep working. Both arms are that pristine agent. The skill arm gets the scenario's `SKILL.md` inlined into the prompt (`prompt-templates/skill-arm.md`); the control gets only the bare task (`control-prompts/<scenario>.md`). The one variable between arms is the skill procedure.

## How to run

`run-ab.sh` runs one trial: setup, the isolated agent, the assert.

```
ab/run-ab.sh <scenario> <skill|control> <model> [trial]
# e.g.
ab/run-ab.sh ambiguous-finalize control claude-sonnet-4-6 1
```

`run-matrix.sh` drives the cells in `matrix.txt` (one `<scenario> <model>` per line) across both arms, N trials each, then prints the tally:

```
ab/run-matrix.sh 3      # N=3 per arm per cell
```

`tally.sh` summarizes `runs/tally.psv` into a scenario-by-model pass-rate matrix. The per-trial agent transcripts and the gh-mock call logs land in `runs/` (git-ignored).

The runner needs the `claude` CLI on PATH and an authenticated session (safe-mode reads the normal auth). The gh-mock scenarios wire the mock and `GH_MOCK_*` env automatically.

## Results

Run 2 (isolated control, Haiku and Sonnet arms, N=3) is in `RESULTS.md`. The short version: the isolation matters, since the same `ambiguous-finalize` control swings from 3/3 confounded to 0/3 isolated, and the measured uplift lives at the Sonnet tier, where the naive control fails 0/3 on `branch-birth` and `ambiguous-finalize` while the skill passes 3/3. Haiku sits below the floor for these multi-step skills, so it shows no clean differentiation. The full nuance, including why some disciplines are intuitive enough for the naive control and why the skill arm's failures stay conservative, is in `RESULTS.md`.
