---
name: motion-craft
description: Animate game characters so their motion reads as natural and intended, and judge whether it does. Covers the twelve principles of animation as games apply them (anticipation against responsiveness, follow-through and control frames, overlap, arcs, spacing, blending), walk and arm-swing numbers, stepped (on twos) and rigid-puppet motion, planning a motion as a pose sheet before keying, measuring arcs, spacing and lag with the bundled motion-path probe, and judging a reel against a rubric. Use it whenever a walk, run, arm swing, idle, gesture, reach, jump or transition is being keyed, procedurally generated, tuned or reviewed, whenever someone says a motion looks stiff, robotic, floaty, twitchy, mechanical or unnatural, and before changing animation curves, clip timing or a blend tree's parameters for feel, in any engine.
---

# Motion craft

Motion reads as alive when its parts do not all move at once, travel on arcs, ease where weight demands it, and come in the order the body would produce them. Most "unnatural" motion breaks one of those in a measurable way. This skill gives the order of work that catches it: plan the motion as poses, key it, measure it, and have it judged by someone who did not make it.

## The order of work

1. **Write the brief.** One paragraph: who moves, what the motion must say (hurried, careful, tired, proud), the speed and cadence the rules give it, the camera it is seen from, and the frame rate it is drawn at (on ones, on twos, stepped). The judge gets this brief and nothing else of yours, so it has to stand alone.
2. **Plan a pose sheet before keying.** Name the key poses (for a cycle: contact, down, passing, up, for each side), and for each joint give its angle at each pose and which pose it peaks on. Write down what leads and what follows, by how many frames or poses. `references/pose-sheet.md` has the method and a template; the `animator` agent drafts one.
3. **Key it** in whatever the project uses: clip data in code, a DCC's timeline, or a procedural rig. Change one thing at a time when reworking, so each change can be seen and kept or dropped.
4. **Measure it.** Record the paths of the parts that matter (hands, feet, head, the tip of anything that trails) and run `scripts/motion_path.py` on them: it draws the paths and reports arcs, reversals, spacing and the lag between two parts. Make a contact sheet and an onion skin of the reel with `scripts/motion_sheet.py`. Numbers catch what eyes forgive after the fiftieth viewing.
5. **Have it judged blind.** Give the `motion-judge` agent the brief, the contact sheet, the onion skin and the path report, and not your reasoning or the pose sheet: a judge who knows what you meant sees what you meant. It scores each principle in `references/rubric.md` with evidence.
6. **Show the person who owns the look** the reel beside the previous take, the judge's verdict and the numbers. Taste decides between takes; the measures only rule out the broken ones.

## What breaks motion, most often

- **Everything starts and stops together.** Real bodies lead with the mass (hips, shoulders) and the extremities follow a beat later; animators call it overlap and drag. One or two frames of lag on the forearm and hand behind the upper arm is the usual cure.
- **Straight lines and sharp reversals.** Natural paths are arcs; a hand that goes back and forth on one line, or turns a corner between two poses, reads mechanical. Check the extremity's path, not the joint angles.
- **Even spacing.** A pure sine or linear tween has no weight. Weight lives in where the spacing tightens: slow in and out around the extremes for a swing, fast in and slow out for a heavy follow-through.
- **Symmetry.** Left and right identical, forward and back identical, a swing centred where the body would not centre it ("twins"). Natural arm swing sits mostly behind the body.
- **The wrong cadence for the body.** Short legs at a long-legged speed scurry; a fast cycle with tiny amplitude ticks rather than swings. See `references/walk-and-arms.md`.
- **Too few distinct poses.** Stepped on twos, a fast cycle can show only four positions per swing; the lag and arcs then have to be built into those poses, as there are no in-betweens to carry them. See `references/stepped-and-puppet.md`.
- **Game feel ignored.** Anticipation on a player move costs responsiveness; follow-through must not hold the player. See `references/game-motion.md`.

## References, and when to read them

- `references/principles.md`: the twelve principles, each with how games bend it. Read when naming what is wrong or planning a new motion.
- `references/game-motion.md`: responsiveness, control frames, blending, layers, cycles, readability at gameplay distance. Read for anything the player drives or any blend tree work.
- `references/walk-and-arms.md`: gait numbers (arm swing range, elbow bend, phase, lag, chest counter-rotation, cadence by leg length, the Froude check, animators' timing). Read for any walk, run or arm swing.
- `references/stepped-and-puppet.md`: on twos, rigid pieces that hinge, stop-motion practice, deterministic clips. Read when the style is stepped, carved, puppet-like or low frame rate.
- `references/pose-sheet.md`: how to plan a motion as poses with per-joint offsets and lag, with a template. Read before keying anything new.
- `references/rubric.md`: what the judge checks, the evidence each check needs, and the verdict scale. Read when judging or preparing material for a judge.
- `references/tools.md`: which tools help (motion paths in a DCC, spring bones, Cascadeur, text-to-motion, video capture) and their licence terms as of late 2026. Read before adopting a tool.

## The probe

Run the scripts with `uv` so their few dependencies come with them:

```bash
# Paths: a JSON of named points per frame (format in the script's docstring)
uv run --with pillow python <skill>/scripts/motion_path.py paths.json --out paths.png --lag HandL:UpperArmL
# Reels: a contact sheet of every 2nd frame from frame 60, and an onion skin of the same
uv run --with av --with pillow --with numpy python <skill>/scripts/motion_sheet.py walk.mp4 --out sheet.jpg --start 60 --every 2 --count 12 --onion onion.png
```

`scripts/godot/bone_path_recorder.gd` records bones or nodes in a Godot 4 scene (world or screen space) and writes the probe's JSON; other engines need only write the same format.

## Judging is separate from making

The maker always sees intent. Keep the judge blind to the plan, give it the brief and the evidence, and treat its verdict as one input: it can be wrong about taste, and it is usually right about a part that never moves or a hand that reverses on a corner.
