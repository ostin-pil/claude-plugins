# Issues A/B (skill vs no-skill)

One scenario-based harness for the `issues` skill, covering the three commands worth an A/B: `add`, `verify`, and `search`. The `issues` skill is a pure agent procedure (no backing script), so this is the cleanest "does the procedure help the agent" test of the knowledge-kit skills. This dir folds the earlier `issues-ab` (add) and `issues-ops-ab` (verify/search) into one runner.

## Scenarios

- `add` builds a tracker holding ISS-001..005 in the canonical format and asks both arms to add the same new bug. `assert-add.py` scores the tracker: all five originals preserved, exactly one new entry at the next sequential id (ISS-006), and the canonical fields present. The tracker is self-documenting, so this is the floor case.
- `verify` plants four "Resolved (verify)" issues, two whose fix marker still sits in the referenced file and two whose marker was reverted, plus two non-target issues that must not change. `assert-verify.py` scores the exact status transitions and breaks out `detected` (did the agent notice the fix was gone, whatever word it used) from `regressed` (did it use the canonical `Regressed`).
- `search` plants an issue whose only link to the query "thermal throttling" lives in a session log, not its tracker entry. `assert-search.py` scores the agent's report for the log-only match (ISS-207).

## Isolation and the command-sliced inline

Both arms run a fresh `claude -p --safe-mode` agent (no host CLAUDE.md, plugin, skills, or hooks; auth and tools intact). The control gets the goal but not the procedure. The skill arm gets the `issues` SKILL.md, but `run-ab.sh` inlines only the slice relevant to the scenario's command: the shared head (intro, project-configuration, the `## Commands` lead-in), the single `### /issues <cmd>` block, and the shared tail (Entry Format, Status Values, Guidelines). The three sibling command blocks and the no-arg list block are dropped, so the skill arm is not handicapped by prose for commands the task never exercises. The single variable stays the skill's procedure for that one command.

## Run

```
sh run-ab.sh <add|verify|search> <skill|control> <model> [trial]
sh run-matrix.sh 3        # add/verify/search x control/skill x haiku/sonnet/opus x 3
python3 tally.py
```

`assert-add.py <repo>` and `assert-verify.py <repo>` score the tracker file directly; `assert-search.py <agent-log>` scores the agent's report (search is read-only). Never the agent's self-report. Per-trial transcripts and `tally.psv` land in `runs/` (git-ignored).

## Results

See `RESULTS.md`.
