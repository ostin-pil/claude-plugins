# motion-kit

Character animation craft for games, as a Claude Code plugin. It helps an agent
plan motion before keying it, measure what was keyed, and have it judged by
someone who didn't make it. It started from a carved-puppet game whose
apprentice's arm swing read as unnatural, so it is strongest on walks, arm
swings and stepped or puppet-like characters, and it holds for any engine.

## What it ships

| Part | What it does |
| --- | --- |
| `motion-craft` skill | The order of work (brief, pose sheet, key, measure, judge blind, show), the twelve principles as games bend them, walk and arm-swing numbers with sources, stepped and puppet motion, the pose-sheet method and template, a judging rubric, and the tools worth using and their licence terms as of late 2026 |
| `animator` agent | Plans or reworks a motion as a pose sheet from a brief and the rig's code, with every number grounded and the overlap designed in |
| `motion-judge` agent | Reviews recorded motion blind (the brief and the evidence only), scores each rubric check with evidence, compares with the previous take, and names the one change to try next |
| `motion_path.py` | Reads named points per frame and draws their paths; reports distinct poses, the cycle, reversals, the arc's bulge, how open the loop is, the sharpest corner, the spacing at the extremes, and the lag of one part behind another |
| `motion_sheet.py` | Turns a reel (or a folder of frames) into a labelled contact sheet and an onion skin of the same frames |
| `bone_path_recorder.gd` | A Godot 4 node that records bones or nodes per frame, in the world or on screen, and writes `motion_path.py`'s format |

## Install

```
/plugin marketplace add ostin-pil/claude-plugins
/plugin install motion-kit@ostin-pil-plugins
```

## Use

Ask for the work in your own words ("the walk looks robotic", "plan an arm swing
for the child", "judge this reel"); the skill's description brings it in. To run
the parts directly:

```bash
# Measure and draw paths recorded by bone_path_recorder.gd (or any tool writing the format)
uv run --with pillow python <plugin>/skills/motion-craft/scripts/motion_path.py paths.json --out paths.png --lag UpperArmL:HandL

# A contact sheet and an onion skin from a reel
uv run --with av --with pillow --with numpy python <plugin>/skills/motion-craft/scripts/motion_sheet.py walk.mp4 --out sheet.jpg --start 60 --every 2 --count 12 --onion onion.png
```

The agents are `motion-kit:animator` and `motion-kit:motion-judge`. Keep the
judge blind: give it the brief and the evidence, never the pose sheet or the
maker's reasoning.

## Notes

The gait numbers are mostly from adult studies, with what is known of young
children marked; the skill says which numbers are unverified. Tool licences
change, so check the vendor's page before relying on the table in
`references/tools.md`.

## Tests

```bash
uv run --with pytest --with pillow --with numpy python -m pytest motion-kit/tests
```
