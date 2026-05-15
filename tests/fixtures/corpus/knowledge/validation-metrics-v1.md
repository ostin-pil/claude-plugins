<!-- prose-check: skip bold-colon-opener -->
# Post-MVP validation metrics v1

**Date**: 2026-05-08
**Status**: First-pass measurement framework, six behavioural metrics to instrument once Untype has paying users (or a pilot cohort). Pairs with `icp-v1.md` (interview-stage validation) and `lean-canvas-v1.md` §10 (assumption falsification). Thresholds are starting points, not commits.
**Source**: lifted from a co-founder market doc dated 2026-05-08 that surfaced this as a gap in repo research. Repo had Mom Test interview prompts, but no behavioural-metric framework once the build is live.

---

## Why this doc exists

Existing research answers *what to ask in interviews* (`icp-v1.md` §6). It does not answer *what to measure once the product is in users' hands*. Without behavioural numbers, the team can't tell whether positioning is working or whether retention is real. These six metrics are the minimum set.

Two distinct phases:

- **Pilot (≤50 users)**, opt-in instrumentation, qualitative survey, manual review of polished outputs.
- **Post-launch (≥500 users)**, anonymised aggregate metrics, opt-out cohorts, weekly review.

The thresholds below are **what would make us continue investing** in the C2 bilingual wedge. Missing them doesn't auto-pivot, it triggers the question "is the wedge wrong, or is the build wrong?"

---

## The six metrics

### 1. Frequency, voice-dictations/day per active user

**Definition**: number of complete (hotkey-pressed to text-inserted) sessions per user per day, on days the app is open.

**Why it matters**: voice keyboard only wins when friction is low enough that users default to it instead of typing. If frequency stays low, either friction is too high or the use case is shallower than ICP claims.

**Threshold**:
- Pilot: ≥10/day for power users by week 2; range 3–30+ acceptable
- Post-launch: median ≥5/day among 14-day-retained users
- **Red flag**: <3/day after 7 days for self-identified daily users

**How to measure**: in-app counter, opt-in telemetry. Bucket by app of insertion (see metric 4).

### 2. Send-without-edit rate

**Definition**: % of polished outputs that get inserted without the user opening the Cleaned·Original toggle to edit, rephrase, or re-dictate.

**Why it matters**: this is the **trust metric**. Wispr's "trust gap" narrative is exactly this number degrading post-trial. If users have to fix the polish every time, the polish layer isn't working.

**Threshold**:
- ≥70% for English-only flows
- ≥60% for L1-to-L2 (translation polish has more failure modes; lower bar acceptable v1)
- **Red flag**: <50% for any cohort, polish layer needs work before scaling

**How to measure**: track per-session whether toggle was opened OR text was modified between paste preview and final insert. Distinguish "edited" from "rejected" (escape).

### 3. Style trust, "sounds like me" Likert

**Definition**: user-reported 1–5 score on "the polished output sounds like the way I'd write."

**Why it matters**: this is what separates a "voice keyboard" from "ChatGPT-with-voice." If outputs read as generic AI, users churn even when accuracy is high.

**Threshold**:
- ≥4.0 average across sampled users
- ≥80% of users score ≥4
- **Red flag**: <3.5 average, the polish prompt is corporatising/sanitising voice, prompt needs rework

**How to measure**: in-app Likert prompt every Nth session (e.g. every 25 sessions, capped at once/week). Pair with optional one-line "what's wrong" free-text. Don't show until the user has shipped ≥10 successful sessions, otherwise the answer is noise.

### 4. Cross-app value, distribution of insertion targets

**Definition**: histogram of which apps users insert into, weighted by volume.

**Why it matters**: tells us whether the wedge is genuinely cross-app (wide ICP) or driven by one app (narrow ICP). If 70%+ of inserts are into Slack, the marketing angle is "Slack voice-typing for bilinguals," not "voice keyboard."

**Threshold**:
- Track top 5 apps by volume per cohort
- Flag if a single app is ≥70% of volume to consider narrowing positioning
- Flag if no app is ≥20% to consider whether the workflow story is too diffuse

**How to measure**: log frontmost-app bundle ID at insertion time. Aggregate weekly.

### 5. Willingness to pay, conversion within 14 days

**Definition**: % of installed users who upgrade to paid (Pro or BYOK-relay) within 14 days of install.

**Why it matters**: lean canvas anchored pricing at $7–9/mo / $79–129 lifetime, *but the price assumption is unvalidated against actual conversion behaviour.* Wispr is $15/mo, Apple Dictation is free. Untype sits in between; this metric tells us whether bilingual professionals will actually pay.

**Threshold**:
- ≥3% conversion within 14 days at $7–9/mo (already wired as the flip-trigger in `knowledge/pivot-build-vs-extend.md`)
- ≥6% if pricing is BYOK-only (no managed-key markup)
- **Red flag**: <2% at 6 months to flip to Shape 4 (BYOK-relay marketplace) per pivot-build-vs-extend.md

**How to measure**: standard payment provider funnel. Bucket by acquisition channel (in-language YT, HN, direct).

### 6. Retention, 7/14/30-day return without nudges

**Definition**: % of installed users who use the app on day 7, day 14, day 30 after install, with **no prompts, emails, or push notifications** in between.

**Why it matters**: voice tools are novelty-prone. Users try them, find them charming, drop off in 3–5 days. Real retention without nudges separates "this changed my workflow" from "I had a fun weekend."

**Threshold** (day-of-install cohort):
- D7 ≥ 40%
- D14 ≥ 30%
- D30 ≥ 20%
- **Red flag**: D7 < 25%, even the trial users aren't sticking; positioning or onboarding is broken

**How to measure**: install timestamp + last-used timestamp. Separate cohorts by month of install (avoid Simpson's paradox). No nudges in this window, even a "how was your week?" survey biases the result.

---

## What this framework deliberately does NOT include

- **STT WER / accuracy**, measured upstream in `research/whisper-bench-2026-04-18.md` and `research/stt-quality-apple-speech.md`. Not a behavioural metric.
- **Latency**, instrumented in code; should be <700ms end-to-end. Not a validation question.
- **NPS / generic satisfaction**, too noisy to act on at this scale.
- **Feature usage by feature**, track only if a feature's existence is being questioned; otherwise it's noise.

---

## Sequencing

These metrics are useless before there's enough volume to measure them. Order of instrumentation:

1. **First**, frequency (1) and cross-app distribution (4). Cheap to instrument, immediate signal on whether the wedge has any pull.
2. **Second**, send-without-edit rate (2) once the polish layer is stable. This is the trust signal.
3. **Third**, WTP (5) only after pricing is live; meaningless before.
4. **Fourth**, retention (6) only after a stable cohort exists (typically month 2 of any pricing).
5. **Last**, style trust (3) once enough users exist to survey without re-asking the same person every week.

---

## Hooks for downstream work

- *For `pivot-build-vs-extend.md`*: the WTP threshold (5) is already the documented flip-trigger to Shape 4.
- *For `icp-v1.md`*: cross-app distribution (4) directly tests the "bilinguals live in Slack/Mail/Linear" assumption. If they don't, ICP needs revision.
- *For `lean-canvas-v1.md`*: send-without-edit rate (2) is the operational version of "trust toggle works" assumption.
- *For instrumentation*: opt-in telemetry framework needs design (no crash analytics SaaS, Untype is privacy-positioned). Most of these can be done with anonymous local counters posted to a Untype-controlled endpoint at user opt-in.
