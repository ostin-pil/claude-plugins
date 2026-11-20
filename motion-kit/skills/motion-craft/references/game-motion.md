# Motion in games: what film animation doesn't have to solve

The player is waiting on the character, sees it from wherever the camera is, and plays its clips back in any order, at any speed, blended with each other. Sources as in `principles.md` (G1, G2), plus engine practice.

## Responsiveness first

- **Player moves start now.** Every frame of anticipation is a frame of input lag. Start the action on the first frame and sell the force with a squash or contact frame and a strong follow-through (G1). A long windup is acceptable only as a deliberate trade (a charged or heavy move) the player chooses.
- **Non-player characters telegraph.** Their anticipation is the player's warning; longer for bigger effects, and the same every time if the game wants it learnable (G1, G2).
- **Control frames.** Mark the frame where the player can act again; play the follow-through only if no input arrives (G2). Without engine support, cut the follow-through short instead.
- **Ambient motion never delays a deed.** Idles, fidgets and looks yield at once to input; a gesture the rules start must reach its contact on time whatever was playing.

## Blending and layers

- **Blend between poses that are near each other.** A cross-fade between distant poses passes through a pose neither clip has, often through the body. Keep blend windows short (a few frames at 30 to 60 fps) for actions, longer for locomotion speed changes, and test the midpoint.
- **Don't lose momentum in a blend.** A blend into a zero-speed pose reads as a stall; carry the outgoing motion's velocity, or blend into a pose that is already moving the same way.
- **Additive layers** (a breath, a look, a lowered arm, a shrink) let secondary motion run over any base clip, outlast it, and fade by weight (G2). Two additive layers that both move the same joint compound; give each joint one owner, or fade one out while the other is in.
- **Masked or partial layers** play an upper-body action over any lower-body locomotion. The seam (the waist or spine bone) needs a weight ramp, not a hard mask, or it shears.
- **A state machine picks clips; a blend tree mixes similar ones** (walk and run by speed, aims by direction).

## Cycles

- **Drive the cycle by distance, not time,** so the planted foot holds at any speed: advance the phase by distance travelled over stride length.
- **Loop seamlessly:** the last pose leads into the first, with no repeated frame at the seam.
- **Whole poses per stride.** If the cycle is stepped (see `stepped-and-puppet.md`), make a stride at cruising speed a whole, even number of drawn poses, or the two steps differ.
- **Starts and stops** need their own short clips or a lean and push-off; a cycle that begins at full speed is weightless (G2).

## Readability

- **Judge at the gameplay camera.** A motion tuned close can vanish at gameplay distance: a 110-pixel figure shows a face only as brows and mouth, and an arm swing of ten degrees as a flicker. Push poses ("plusing") until they read there (G2).
- **Silhouette first.** The pose should read as a flat shape; check key poses against the background they'll be seen on.
- **Repetition shows everything.** A clip seen hundreds of times exposes every arc break and pop; mocap cleanup is mostly removing them (G2).

## Determinism

- If the game is learnable (enemies on patterns, puzzles timed to motion), clips should play the same every time: keyed or baked, not simulated live. Simulate to find the feel, then bake it into keys.
