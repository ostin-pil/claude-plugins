# The twelve principles, as games use them

Johnston and Thomas's twelve principles (*The Illusion of Life*, 1981) were written for hand-drawn film. Games keep all of them but bend several, because the player is waiting on the character and can look at it from anywhere. Sources: W = [Wikipedia, Twelve basic principles of animation](https://en.wikipedia.org/wiki/Twelve_basic_principles_of_animation); G1 = [Game Developer, "12 principles for game animation" (2021)](https://www.gamedeveloper.com/game-platforms/12-principles-for-game-animation); G2 = [Game Developer, "The 12 principles of animation in video games" (2019)](https://www.gamedeveloper.com/production/the-12-principles-of-animation-in-video-games); A = [Animost, 3D character movement](https://animost.com/tutorials/3d-character-movement/). Points marked "G1 summary" came through only as a summary of that page's last quarter and are not checked against its text.

## 1. Squash and stretch

Volume stays constant: a stretched ball narrows (W). Games limit it to a few frames, because a body that changes shape no longer matches its collision; some studios give only some parts colliders, which also lets the shape cheat in the player's favour (G1). Many engines don't scale bones, so it is faked by extending limbs (G2). Rigid or carved characters can't squash at all: their equivalent is the bend of the whole chain (knees, spine) and how far the pose dips.

## 2. Anticipation

A small opposite move before the main one (a dancer's knee bend, a golfer's backswing), and also a non-physical beat such as a glance off screen before someone arrives (W). This is where games and film clash most: anticipation frames delay the response to input (G1, G2). Options: start the action on the first frame and put the weight into a squash frame and the stretch after (G1's Little Nemo jump); make a long windup a deliberate risk for a heavy move; keep anticipation for non-player characters, whose attacks should telegraph, longer for bigger effects (G1, G2). No page gives a frame budget for player anticipation.

## 3. Staging

Direct attention with placement, light and camera, and leave out what doesn't help (W). In gameplay the player moves the camera, so staging is done by layout, funnels and light; only authored scenes are staged like film (G2). Check key poses from several angles, and keep a viewport that mimics the gameplay camera (G1). At gameplay distance, push poses further ("plusing") so the action reads (G2).

## 4. Straight ahead and pose to pose

Straight ahead suits fluid, unpredictable motion; pose to pose suits clear composition; most work mixes both (W). In CG the default is pose to pose: keys, then breakdowns, then in-betweens, in passes, because game animations are changed and cut (G1, G2). G1 cites a walk keyed on frames 1 and 17 with breakdowns on 9 and 25. Loose parts (hair, cloth, hit reactions) suit straight ahead or simulation (G1 summary).

## 5. Follow-through and overlapping action

Parts take a few frames to catch up (drag); limbs move on different timing from the torso and head (overlap); soft parts move more than bone (W). The usual junior mistake is every part starting or arriving together: in a punch the head and torso lead, the bent arm trails and then snaps forward before impact (G2). Games add a control frame: the engine lets the animator mark the frame where the player regains control, and the follow-through plays out only if no input comes (G2). Keep attack follow-through short, or move it onto something other than the character (G1 summary).

## 6. Slow in and slow out

More drawings near the start and end of a move, fewer in the middle (W). Weight decides where: a sword that starts at full speed looks light, so its weight goes in the follow-through, fast in and slow out back to rest; a cannon fires instantly and shows its weight in the kickback (G2). A run that starts at full speed looks weightless; give it a lean and a push-off foot (G2). Engines tween automatically, so getting the spacing wanted can take extra keys or curve work (G1 summary).

## 7. Arcs

Most natural motion travels on arcs, which flatten at speed; mechanical motion is the exception (W). Check the extremity, not the joint angles: a fingertip should follow a sensible arc through every in-between (W). Cleaning motion capture is mostly removing arc breaks, which look wrong when a clip repeats; a deliberate break (a head snapping after a hit) reads as force, and making every part follow a clean arc can look floaty (G2).

## 8. Secondary action

Supports the main action without competing with it; a facial change reads better at the start or end of a big move than in the middle (W). Games run secondary motion on additive or partial layers so it can outlast or vary the player-driven base: a tired breath over a long run (G2). Arm swing in a run and idle fidgets add life (G1 summary). Many blended clips make a more fluid character than one perfect clip (G2).

## 9. Timing

The number of frames for an action sets its speed and sells its weight; light things react faster than heavy ones (W). Time is distance over speed: the same pose change over 2 frames reads faster than over 5 (G2). Engines can change playback speed, which film can't; G1's two-frame goat looked too fast at full speed and right at a quarter. For cadence and stride timing see `walk-and-arms.md`.

## 10. Exaggeration

Push past realism, with restraint and balance across the scene (W), and consistently across a team (G2). A boss's roar pose that beat realism was the most replayed moment of its trailer (G1 summary). Exaggeration has to stay within collision and control.

## 11. Solid drawing

Forms with volume and weight; avoid "twins", left and right mirrored (W). In 3D it becomes body mechanics: the centre of mass, balance, the chain of reaction from the foot up the spine, because the character is seen from every side (G2).

## 12. Appeal

Charisma in the design and the motion: clear silhouettes, simplicity, a readable personality, enemies included (W, G2). A walk cycle should match the character's personality (A).

## Gaps

None of these pages gives numbers for blend windows, start and stop transitions, cycle lengths or root motion. For walks, `walk-and-arms.md` has measured numbers; for blending, `game-motion.md` has rules of practice.
