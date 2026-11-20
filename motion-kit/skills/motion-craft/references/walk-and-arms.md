# Walks and arm swing: the numbers

Measured gait data and animators' rules of thumb for walks and the arms in them. Most gait studies are of adults; where children differ it says so. Points marked unverified were seen only in search snippets or abstracts.

## The arms

- **Phase.** Each arm swings against its own leg: fully back as its own foot lands, fully forward as the other foot lands. Every child does this by about age 4 (Sutherland 1988, via [OUHSC](https://ouhsc.edu/bserdac/dthompso/web/gait/matgait/matgait.htm)).
- **Range at the shoulder: mostly behind the body.** In 30 men at their own pace the arm reached 24 ± 6° behind vertical and only 8 ± 10° in front, 32° in all; walking faster added backward swing only, 31° back and still 8° forward ([Murray et al. 1967, Phys Ther 47:272](https://academic.oup.com/ptj/article/47/4/272/4648918)). Children of 3 to 6 carry the arm further back than older children and adults, with more elbow bend and the wrist bent back more ([Van de Walle et al. 2018](https://documentserver.uhasselt.be/handle/1942/26634), abstract only).
- **The elbow is never straight.** About 17° bent at the back of the swing and 47° at the front at free speed, 55° walking fast; it bends as the arm comes forward (Murray). Walking averages about 36°, running about 90° ([Yegian et al. 2019, J Exp Biol 222](https://doi.org/10.1242/jeb.197228)). A nearly straight arm at a brisk cadence reads as marching.
- **The shoulder leads.** Murray saw the shoulder reverse before the elbow in 111 of 180 observations, the elbow first in 32. The shoulder is furthest forward at or just before the other foot's heel strike; the elbow peaks a little after. Animators key the same chain: shoulder, then elbow, wrist and fingers, the hand flipping a little at each end of the swing ([Lemay, arm swing](https://www.brianlemay.com/Pages/animationschool/animation/animationexamples/armswing.html); [overlapping pendulum](https://www.brianlemay.com/Pages/animationschool/animation/animationexamples/overlappingpendulum.html)). One or two frames at 24 fps is the usual arm offset.
- **Not a pure sine.** Some walkers hold the arm forward briefly before it comes back (Murray). Left and right passing through identical positions looks like stopping and reversing (a stop-motion guide, unverified).
- **The chest turns with them.** The thorax rotates against the pelvis, more at speed ([Kerkman et al. 2020](https://www.frontiersin.org/article/10.3389/fphys.2020.00751/full); degree values unverified). "If the arms are moving, so is the chest" ([Pluralsight walk cycle](https://www.pluralsight.com/blog/tutorials/12-steps-walk-cycle-animation)).
- **Mostly passive.** The arm is largely a pendulum driven by the body ([Pontzer et al. 2009](https://pubmed.ncbi.nlm.nih.gov/19181900/), abstract). But an arm's natural pendulum period rarely matches the stride: a 0.3 m arm swings at about 1.1 Hz against a 2 Hz stride. So simulate only the lag, and key the swing itself.
- **Slow walks change pattern.** Below about 0.8 m/s for adults the arms can swing twice per stride ([Wikipedia, arm swing in human locomotion](https://en.wikipedia.org/wiki/Arm_swing_in_human_locomotion)).

## Cadence and stride

- **Animators' timing at 24 fps:** 12 frames a step is a natural walk, 8 a brisk walk, 6 (4 steps a second) a slow run or cartoon walk ([Monmouth, after Williams' *Animator's Survival Kit*](https://animation.monmouth.edu/instruct/?p=351)).
- **The Froude check for any leg length.** Fr = v² / (g L), L the leg length (hip to floor), g 9.81. People prefer to walk near Fr 0.25 and change to running near 0.5 ([Donelan and Kram 1997](https://www.sfu.ca/locomotionlab/assets/dynsimwalk1997.pdf); the preference figure from a stilt study, snippet only). Use it when a stylised character has short legs: if its walk scores 0.35 or more it reads as hurrying, whatever its clip says.
- **A worked case.** A 1.1 m child with legs about 0.52 m walking 1.1 m/s scores 0.24, a normal walk, at about 2.6 steps a second. A stylised 1.1 m figure with legs of 0.34 m at the same speed scores 0.36, and at a step of 0.8 of its leg it takes 4 steps a second. Lengthening the step to 0.95 of leg length gives about 3.4.
- **Real children:** 4- and 5-year-olds are 106 to 115 cm tall with legs of 50 to 55 cm ([GOS-ICH centiles, Alderson et al.](https://ora.ox.ac.uk/objects/uuid:348eb63f-6a1c-4d8f-a2c6-02768a19f2f6/files/mdd066d6d13f9a9a85c570effd0a1c446)). Cadences of 150 to 160 steps a minute for that age are often quoted (unverified).
- **Faster walking** adds backward arm swing and elbow bend at the front (Murray), and at jogging pace the elbows bend toward 90° (Yegian).

## The walk's other parts, briefly

- **Contact, down, passing, up:** the four poses of each step. The body is lowest just after contact (the down) and highest at the up, as the trailing foot pushes off ([Pluralsight](https://www.pluralsight.com/blog/tutorials/12-steps-walk-cycle-animation); A in `principles.md`).
- **The hips** rise and fall, tilt toward the swinging leg's side, and turn with the forward leg; the shoulders turn the other way.
- **The head** rides the body's bob and settles; on a big-headed character keep its bob small, or it nods.
- **A walk's personality** comes from its cadence, its bob, how far the arms go back and how much the chest leads: a hurried walk leans forward with short quick steps, a careful one has small arm swing and a level head.

## A starting pose sheet for an arm swing

Values to start from, for a natural walk at its preferred cadence; adjust to the brief and judge on the reel.

| Pose (of its own side's step) | Shoulder (+ forward) | Elbow bend | Hand | Chest turn |
|---|---|---|---|---|
| Own foot contact | about -16° (fully back) | about 15° | trailing, palm back | own shoulder back about 3°, against the hips |
| Down | coming forward | 15 to 20° | still trailing | |
| Passing | about -5° | 25° | catching up | neutral |
| Other foot contact | about +6° (fully forward) | about 35°, peaking a pose later | a small flip as it turns | own shoulder forward about 3° |
| Up | going back | 30° | leading back | |

On a stepped character the "pose later" offsets are whole drawn poses; see `stepped-and-puppet.md`.
