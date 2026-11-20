# Stepped and puppet motion

For characters drawn on twos or lower, rigid pieces that hinge (carved, cut-out, toy, marionette), and stop-motion looks. Much of this comes from a carved-puppet game's research (Cashtank's `research/20-character-animation.md` and `33-arm-swing.md`), generalised.

## Stepping

- **Step the poses, not the travel.** Hold each drawn pose for two frames at 24 fps (12 poses a second), but move the character through the world every frame, and keep the camera, flames, springs and wheels on ones. A stepped travel judders against a smooth camera. *Guilty Gear Xrd* rebuilt playback to count frames because time-based playback let character and camera drift apart.
- **Key smooth, step at playback.** Author clips as smooth curves and step them when played, so the step rate is one setting to compare (ones, twos, threes). Stepping at import fixes it into the data; if you must, import at 24 fps, since 12 fps holds on a 30 fps grid alternate 2- and 3-frame holds.
- **Count the distinct poses.** At 4 steps a second on twos, a stride is 6 poses and each sweep of a limb gets 3: the limb shows about 4 positions. Anything that should happen between those poses (lag, an arc's bulge, a hand flip) doesn't exist unless a pose carries it.
- **So build overlap into the poses.** The forearm still trailing at the pose where the shoulder turns; the hand a pose later again. One pose of lag on twos is two frames at 24 fps, about the classic arm offset.
- **Whole, even poses per cycle.** A cruising stride should be an even number of drawn poses, or left and right steps get different samples and limp.
- **Different rates for different characters are a real choice.** *Spider-Verse* put the clumsy Miles on twos and the skilled Peter on ones; a house's clockwork servant can run smooth while a child runs stepped. Give the player character a way to go to ones if input feels laggy (Insomniac shipped that switch).

## Rigid pieces

- **The wood never bends.** One bone per piece, full weights, so nothing shears; joints hinge at real anatomical pivots, even under clothes, and clothes over a moving joint are split into panels that follow it. Del Toro's Pinocchio kept the outside "completely solid" because bending grain looked creepy.
- **Hinges limit motion.** A rigid elbow or knee only folds one way; a swing that needs a twist must be built from the joints there are, or it pops. Measure the extremity's path to catch a joint solver twisting a bone about its own length.
- **Clearance is the constant fight.** Big heads, aprons and props mean a swinging hand or a raised knee meets something solid. Sweep every pose headless against the body's other pieces and keep the limits in the checks, not in eyeballing.
- **Squash and stretch become pose depth:** how far the knees bend, the spine curls, the head tips.

## Puppet and stop-motion practice

- **Trnka** gave puppets fixed faces and acted with gesture, framing and light; turning the head or changing the light changes the expression.
- **Del Toro's Pinocchio** started the boy's motion disjointed and smoothed it as he grew sure; motion can carry a character's growth without changing the body.
- ***Harold Halibut*** dropped true stop-motion for gameplay and keyed bodies over capture acted "a little stop-motion-esque", stepping only faces.
- ***Puppeteer*** (2013) hand-keyed its puppets on a side-on stage with no physics.
- ***Inside***: workers that walk nine steps and stop, learnable by counting; a boy who looks like he is trying his hardest, every failed attempt with its own short clip, his head turning to what matters.
- **Human capture fits puppets badly.** Weight shifts, breathing and finger motion make a wooden puppet look possessed; adult proportions put a big-headed child's hands in its face. Use capture as reference, and key.

## Simulation, baked

- A damped pendulum or spring bone gives natural lag at reversals, but live it steps coarsely on twos and floats on ones against a stepped body. Use it to find the feel, then integrate the same model offline and sample it into keys, so the clip is deterministic and stepped with the rest.
- An arm's own pendulum period rarely matches the stride (a 0.3 m arm at about 1.1 Hz against a 2 Hz stride), so a pure simulation won't give an opposing swing: key the swing, simulate the lag.
