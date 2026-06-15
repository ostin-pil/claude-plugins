# Untype Status Report 2026-04-15

**Range:** 2026-04-14 to 2026-04-15 (sessions 25–28, 37 commits)

Four sessions in two days. Session 25 was pure tooling (worktree cleanup, skill rework). Session 26 ran a broad code-health audit and landed 8 triage commits on top of a new `/code-health-audit` skill. Session 27 opened the STT-quality track with an `SFSpeechRecognizer` audit and the first free wins. Session 28 built an automated E2E audio-benchmark harness and hung three new threads off it: transcription protocol seam, custom language-model spike, and opt-in cloud prompt caching.

## Research conducted

| Doc | Session | Summary |
|---|---|---|
| `research/stt-quality-apple-speech.md` | 27 | Full inventory of every `SFSpeechRecognizer` / `SFSpeechAudioBufferRecognitionRequest` quality knob on macOS 14+. Identifies `addsPunctuation`, `contextualStrings`, `customizedLanguageModel`, and confidence/alternatives as the live levers. Verdict: custom LM is the biggest remaining lever; server-side recognition is a dead end. |
| `knowledge/code-health-audit-2026-04-14.md` + `_2` / `_3` / `_4` | 26 | Four audit runs (1 hand-written, 3 via the new skill) over the same commit. Used to tune the skill's prompt for coverage, mandatory mechanical checks, and false-positive guards. |
| `knowledge/animation-direction-2026-04-14.md` | 26 | Survey of the overlay's current visual state (zero SwiftUI animations today), 5 candidate effects ranked by impact-per-effort, and open direction questions. Decision deferred. |

## What was achieved

### Session 25: repo cleanup and session-skill rework (2026-04-14)

Pure tooling/process session. No source changes.

| Area | Delivered |
|---|---|
| Worktree sweep | Removed 8 stale worktrees and 14 orphan local branches (all `ahead=0` vs main). `.claude/worktrees/` and `git branch` both cleaned to a single entry. |
| `/cleanup-worktrees` skill | New skill codifying the audit, classify, confirm, delete workflow. Safety rule: `ahead=0` AND dirty state is allowlisted noise only. Supports `--dry-run`. Commit `9120fb4`. |
| `/report` skill rework | Reports now save to `reports/Status Report {end-date}.md`, not an overwritten `STATUS_REPORT.md`. Header format updated, "What is Untype?" template block dropped. Commit `24c53de`. |
| Session-skill triad | Split the lifecycle into `/session-start` (read-only briefing), `/session-report` (log writer), `/session-end` (5-phase finalizer: build+test gate, report, finalize-worktree, cleanup-worktrees, summary). `CLAUDE.md` updated. Commit `79456c1`. |

### Session 26: code-health audit pass and triage (2026-04-14)

| Area | Delivered |
|---|---|
| `/code-health-audit` skill | New skill dispatching an Explore subagent with a self-contained prompt that audits correctness, rule violations, perf smells, and refactor candidates. Writes to `knowledge/code-health-audit-YYYY-MM-DD.md`. Commits `3b88b17`, `27341e0` (tune 1: coverage + targeted greps), `7fdf69e` (tune 2: bind `wc -l` + hot-path sweep to output), `b83eea6` (tune 3: false-positive guards for `Task.sleep`, body-verification, stop-on-success). |
| Critical triage | Landed 8 fix commits with `swift build` green between each: `FocusedElementLocator` AX force-casts guarded (`d1c2e2d`), `deinit` cancelling owned tasks/timers in `RecordingCoordinator` + `AppDelegate` (`98700d1`), 50 ms level-timer dropped per-tick `Task` allocation (`b561459`), failable `AppleSpeechService.make()` factory (`640f9f5`), `MenuBarController.statusItem` IUO replaced with a guarded optional (`9e69a06`), extracted `AudioLevelMonitor` from `RecordingCoordinator` (`3911a94`), split `AppDelegate` into `OnboardingCoordinator` + `AppRouterBuilder` (`ade0119`). |
| 200-line rule compliance | All Untype sources now under 200 lines. Largest is `RecordingCoordinator.swift` at 193. |
| Animation direction notes | `knowledge/animation-direction-2026-04-14.md` with 5 candidate effects and open questions. No code written. |

### Session 27: STT quality spike (2026-04-14)

Ran in a `feature/stt-quality` worktree in parallel with session 26's `main` work; merged cleanly (`d32ae00`).

| Area | Delivered |
|---|---|
| SFSpeechRecognizer audit | `research/stt-quality-apple-speech.md`, a 144-line doc covering every quality knob, custom LM workflow, server-side verdict, prioritized follow-ups. |
| Free wins shipped | `AppleSpeechService` now sets `addsPunctuation = true` and wires a private `baselineContextualStrings` (seeded with `"Untype"`) as phonetic bias. Commits `56047d4`, `9b060e2`. |
| Deferred to later sessions | Custom language model, confidence + alternatives consumption, locale-aware `supportsOnDeviceRecognition` fallback, `TranscriptionProvider` protocol seam. All scoped in the research doc. |

### Session 28: STT protocol seam, API layer, automated E2E benchmarks (2026-04-15)

The headline session. Unified three threads under one benchmark harness so every future change becomes a measurable delta instead of a manual mic test.

| Area | Delivered |
|---|---|
| Transcription moved to UntypeCore | `AppleSpeechService` moved out of the app target into `Sources/UntypeCore/Transcription/` behind a new `TranscriptionProvider` protocol (`startRecognition`, `appendBuffer`, `stopRecognition`, `cancelRecognition`, `finalText`, `name`). `UntypeBench` can now exercise the real prod STT path. Commit `507db45`. |
| WER + edit-distance scoring | `Sources/UntypeCore/Scoring/WER.swift` (word-level Levenshtein with case-fold + punctuation-strip normalization) and `Sources/UntypeCore/Scoring/EditDistance.swift` (character-level + similarity score). 14 unit tests. Commit `a95fdce`. |
| Audio E2E harness in UntypeBench | `TranscriptionHarness` with two playback modes: `bufferReplay` (real prod path via `appendBuffer`) and `urlDirect` (`SFSpeechURLRecognitionRequest`). `Runner` branches on `audioPath`: STT, then WER score, then LLM cleanup, then similarity score. New flags `--audio-corpus`, `--audio-root`, `--playback-mode`, `--stt-only`. Commit `5140691`. |
| CloudProvider prompt caching | Opt-in `supportsExplicitCaching` flag on `CloudProviderConfig`. When enabled, the system message is emitted in Anthropic content-parts form with `cache_control: ephemeral`. Passes through OpenRouter to Anthropic routes. Covered by two new wire-format tests. Commit `d7d14c9`. |
| Custom SFSpeechLanguageModel spike | New `SpeechLMBuilder` SPM executable at `tools/speech-lm-builder/` compiles a JSON vocab into a `.bin` `SFCustomLanguageModelData`. `AppleSpeechService.configureCustomLanguageModel(dataURL:clientIdentifier:)` calls `prepareCustomLanguageModel` and applies the config to each request. `bench/custom-lm-vocab.json` seed with 25 Untype-relevant phrases. AppDelegate launch-time wiring deferred. Commit `8dafe69`. |
| Seed fixture pack | 3 TTS fixtures generated via `say -v Samantha` (`clean_en.aiff`, `false_start_en.aiff`, `technical_en.aiff`), `bench/audio-corpus.json` with references and expected cleanups, `bench/README.md` extended with audio mode docs. Commit `82693f0`. |
| Buffer-mode bug found + fixed | First buffer run returned WER 1.0 (empty transcripts). Per-chunk `AVAudioConverter` loop was signalling `endOfStream` after the first chunk and refusing further input. Rewrote `feedFile` to read the whole fixture, resample once to 16 kHz mono Float32, then feed 100 ms chunks with real-time pacing. Validated: `clean_en` 0.100, `false_start_en` 0.067, `technical_en` 0.000 WER. Commit `ae8be04`. |
| Repo hygiene | `benchmarks/` run artifacts moved out of git and into `.gitignore`. Commits `adf87e4`, `1299808`. |

## Current state

**Working now:**
- Build and tests green: `swift build` clean, `swift test` 26/26 passing (12 CloudProvider + 14 Scoring).
- `UntypeBench` runs two modes end-to-end:
  - Text corpus through one or more LLM providers, producing a latency/cost/similarity report (existing).
  - Audio corpus through the real `AppleSpeechService`, scored by WER, then LLM cleanup, then similarity (new).
- Both `buffer` and `url` playback modes validated against the TTS smoke fixtures.
- `AppleSpeechService.addsPunctuation` + `contextualStrings` shipping in the app.
- `TranscriptionProvider` protocol in place as the seam for WhisperKit or any second backend.
- `SpeechLMBuilder` CLI compiles; `configureCustomLanguageModel` is wired on the service side.
- `CloudProvider` supports explicit `cache_control` under a config flag (off by default).
- All source files under the 200-line rule after session 26's triage.

**Not yet tested / validated:**
- **No real (non-TTS) audio fixtures.** TTS smoke numbers are not product-meaningful.
- **Custom LM is unused.** The `.bin` has never been built, the app never calls `configureCustomLanguageModel` at launch, and no before/after WER run exists.
- **Prompt caching has never hit a live endpoint.** Tests assert the request body; no OpenRouter run has confirmed `cached_tokens` in the usage block.
- **Manual end-to-end app test** with the `gpt-oss-120b:free` default + offline fallback verification is still outstanding from session 24.

**Known gaps:**
- `AppleSpeechService.make()` assumes on-device recognition is available for `Locale.current`; latent bug for unsupported locales.
- `SFSpeechRecognitionResult.segments` confidence and `result.transcriptions` alternatives are dropped; the overlay is text-only.
- `CloudProvider` has no retry logic beyond 429 handling in the `UntypeBench` runner.
- Session 25's flagged cruft (`index.js`, `tools/test_output.md`, `.gitignore` drift) still untouched except for the `benchmarks/` line added in session 28.
- Animation direction decision + first slice still on ice.

## What's next

### Immediate (session 29 candidates)

1. **Real audio fixtures.** Drop 5–10 human recordings under `bench/audio/` covering clean, false start, noise, custom-LM vocab, non-English. Unlocks every meaningful WER comparison.
2. **Ship the custom LM.** Run `swift run SpeechLMBuilder bench/custom-lm-vocab.json bench/CustomLM.bin`, wire an `AppDelegate` launch call to `configureCustomLanguageModel` behind a splash state, gate by file existence. Then diff WER on real fixtures before/after.
3. **Prompt-caching A/B via OpenRouter** on an Anthropic route. Enable `supportsExplicitCaching`, run `UntypeBench` twice, confirm `cached_tokens` in the second run's usage.
4. **Phase-transition crossfade in `BarView`**, the universally-safe animation starter. ~20 lines, unblocks the animation track without needing the full direction decision.
5. **Manual end-to-end app test** (carryover from session 24): `./bin/build.sh && open Build/Untype.app`, dictate through the new `addsPunctuation` path, verify `gpt-oss-120b:free` default + offline fallback behaviour.

### Post-MVP / deferred

- **STT track:** confidence + alternatives consumption (dim low-confidence words, pass alternatives into the LLM prompt); locale-aware `supportsOnDeviceRecognition` fallback; second `TranscriptionProvider` conformance (WhisperKit is the real reason the protocol exists).
- **API track:** native Anthropic SDK provider (streaming, citations, extended caching tiers, first-class usage metadata); general retry/backoff scaffolding on `CloudProvider`, not just the benchmark runner.
- **UX track:** animation direction decision and the remaining 6 slices from the session 26 plan (overlay fade-in, breathing blob, audio-reactive glow, spring-timed resize for `.reviewing`, error pulse, partial-text stream-in).
- **Hygiene:** session 25's `index.js` / `tools/test_output.md` / `.gitignore` drift triage.
- **Skill maintenance:** first real-world run of `/cleanup-worktrees` against accumulated debris; focus-arg runs of `/code-health-audit` (`audio`, `transcription`, etc.) to sanity-check post-tune coverage on narrow scopes.

## Commit summary (37 commits)

```
1299808 chore(git): ignore benchmarks/ run artifacts
adf87e4 chore(git): ignore benchmarks/ run artifacts
ae8be04 fix(bench): resample fixture audio to 16 kHz mono and pace buffer feed
82693f0 docs(bench): add audio corpus, TTS seed fixtures, and E2E run instructions
8dafe69 feat(transcription): custom SFSpeechLanguageModel spike — builder CLI + service hook
d7d14c9 feat(processing): add opt-in cache_control on CloudProvider system message
5140691 feat(bench): add audio E2E harness with buffer/URL playback modes and scoring
a95fdce feat(scoring): add WER and character edit-distance scorers with tests
507db45 refactor(transcription): move AppleSpeechService to UntypeCore behind TranscriptionProvider protocol
39211e0 chore(config): add session-report and session-end skills to audit pipeline
a0beb7e docs(sessions): update session 26 log with triage, tunings, animation notes
a928665 docs(sessions): update session 25 log with skill rework
79456c1 feat(tools): rework session skills into start/end/report triad
e58ab2b docs(knowledge): capture overlay animation direction discussion
d32ae00 Merge branch 'feature/stt-quality'
c46c151 docs(sessions): add session 27 log for STT quality spike
50bc90a chore(config): add code-health-audit skill and awk filter to settings
ade0119 refactor(app): split AppDelegate into onboarding + router builder
3911a94 refactor(audio): extract AudioLevelMonitor from RecordingCoordinator
9e69a06 fix(menu): replace statusItem IUO with guarded optional
640f9f5 fix(transcription): make AppleSpeechService construction failable
b83eea6 fix(tools): add false-positive guards to /code-health-audit hot-path sweep
9b060e2 feat(transcription): enable addsPunctuation and contextualStrings
56047d4 docs(research): audit SFSpeechRecognizer quality knobs for Untype
b561459 perf(audio): drop per-tick Task in 50ms level timer
98700d1 fix(app): cancel owned tasks and timers in deinit
d1c2e2d fix(overlay): guard AX force-casts with CFGetTypeID checks
201b6cf docs(knowledge): add /code-health-audit run 4 after second tune
7fdf69e fix(tools): bind wc -l and hot-path checks to output in /code-health-audit
97917a1 docs(knowledge): add tuned /code-health-audit run 3
27341e0 fix(tools): tighten /code-health-audit coverage after first run
3b88b17 feat(tools): add /code-health-audit skill
4732251 docs(sessions): add session 25 log covering worktree cleanup and skill refinements
bc80778 docs(report): add initial status report for 2026-04-13 covering sessions 11–24
24c53de chore(skills): update skill to save dated reports and simplify template
9120fb4 feat(tools): add /cleanup-worktrees skill for pruning stale worktrees
```
