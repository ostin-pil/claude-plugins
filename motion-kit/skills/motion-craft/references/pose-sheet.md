# Planning a motion as a pose sheet

A pose sheet is the motion written down before it is keyed: the key poses in order, each joint's value at each, which pose each joint peaks on, and what leads what. It turns "make it feel natural" into decisions someone can check, and it is where overlap gets designed rather than hoped for.

## How to write one

1. **The brief at the top:** who, what the motion says, speed and cadence, camera, frame rate (ones, twos), and any rule it must obey (a contact frame the rules need, a pose it must pass through for a prop, a clearance).
2. **Name the poses.** For a cycle, per step: contact, down, passing, up (so 8 for a stride). For a gesture: rest, anticipation (if any is allowed), key, contact, follow-through, settle. For a reach or turn: the leading part's start, the extreme, the settle.
3. **Time them.** Frames (or drawn poses, if stepped) between poses. Check the whole against the brief's speed: a stride's length in frames from its cadence.
4. **Give each joint a row:** its value at each pose, in the unit the rig uses (degrees about a named axis, or a target position). Mark where it peaks.
5. **Write the overlap:** for each chain, the order and the delay. "Shoulder peaks at other-foot contact; elbow one pose later; hand flips one pose after the elbow."
6. **Write the arcs:** the path the extremity should take (a forward-bulging arc for a hand coming forward, a lower arc for a foot's swing), and which pose shows its highest or widest point.
7. **Note what must not happen:** a hand passing through an apron, a knee through a skirt, a reversal on a corner, a pose that pops between two clips.
8. **List the measures** the probe should report to confirm it: the hand's range forward and back, its lag behind the shoulder in frames, the number of distinct poses per swing, the path's sharpest turn.

## Template

```markdown
## Brief
<who, what it says, speed and cadence, camera, frame rate, hard rules>

## Timing
| Pose | Frame (or drawn pose) | Notes |
|---|---|---|
| contact R | 0 | |
| down R | | |
| passing R | | |
| up R | | |
| contact L | | |
| ... | | |

## Joints
| Joint (axis, unit) | contact R | down R | passing R | up R | contact L | ... | Peaks on |
|---|---|---|---|---|---|---|---|
| hips (turn, deg) | | | | | | | |
| chest (turn, deg) | | | | | | | |
| upper arm L (swing, deg, + forward) | | | | | | | |
| forearm L (bend, deg) | | | | | | | |
| hand L (flip, deg) | | | | | | | |

## Overlap
<chain: order and delay, in frames or poses>

## Arcs
<extremity: the path's shape, its widest pose>

## Must not
<collisions, pops, corners>

## Measures to confirm
<probe outputs and their target ranges>
```

## A worked line, for an arm on a stepped walk

"Upper arm L: -16° at own contact, -5° passing, +6° at other contact, peaks forward on other contact. Forearm L: 15° at own contact rising to 35°, peaks one pose after the upper arm's forward peak. Hand L flips 10° forward one pose after the forearm. Chest turns 3° against the hips, own shoulder back at own contact. Measures: the hand travels at least twice as far behind its resting place as in front of it (the shoulder's 16° back against 6° forward), it lags the upper arm by one pose, and no turn along its path is sharper than 60°."
