# Transcription pain points from Reddit, HN, GitHub, App Store — May 2026

**Date:** 2026-05-07
**Purpose:** Primary-source inventory of *transcription-quality* failures users report. Fills the Reddit gap noted in `user-pain-points-and-desires-2026.md` and adds dimensions specific to STT failure modes (acoustic, language, hallucination, format) — i.e. how dictation tools fail at the speech-to-text *job*, not at pricing/support/UX.
**Scope:** macOS dictation tools (Wispr Flow, Superwhisper, VoiceInk, FluidVoice, MacWhisper, macparakeet, Apple Dictation) plus Whisper / whisper.cpp / Parakeet model-level reports.
**Date range mined:** primary focus on signal opened or refreshed **after 2026-04-18**; older threads cited where they're load-bearing for failure-mode taxonomy.
**Companion docs:**
- [`user-pain-points-and-desires-2026.md`](./user-pain-points-and-desires-2026.md) — product-level complaints (pricing, support, UX). This doc focuses on the *transcription job* itself.
- [`competitor-deep-diff-2026-05.md`](./competitor-deep-diff-2026-05.md) — canonical 8-tool matrix.
- [`whisper-bench-2026-04-18.md`](./whisper-bench-2026-04-18.md) — quantitative WER (incl. 1 RU sample).

---

## 0. Methodology

**Sources mined:**
- **GitHub Issues** (primary; richest fresh signal): `Beingpax/VoiceInk`, `altic-dev/FluidVoice`, `moona3k/macparakeet`, `ggerganov/whisper.cpp`. `openai/whisper` Issues are disabled — Discussions used instead.
- **Hacker News + HN Algolia API** for whisper / dictation / Wispr / Superwhisper threads.
- **Substack/blog**: afadingthought, samwize, Simon Willison, Danny Smith (already mined in prior doc; only new posts cited here).
- **Habr.com** (Russian-language source — the prior doc had no Russian-language signal at all).
- **X/Twitter** for one specific Russian-language Whisper-hallucination tweet from `@dimonb`.

**Sources tried but blocked / unavailable:**
- **reddit.com / old.reddit.com** — `WebSearch site:reddit.com` returns "no links found" across every tool/term combo I tried (`whisper hallucination`, `Wispr Flow inaccurate`, `VoiceInk language wrong`, `Superwhisper transcription quality`, `r/russian whisper`). Direct WebFetch on `news.ycombinator.com` works fine, suggesting the block is reddit-specific and matches the prior doc's experience. The Reddit signal here is therefore **still routed through aggregators or HN refs**; the situation has not improved since 2026-04-18.
- **App Store reviews** — `apps.apple.com/us/app/superwhisper/...` returned HTTP 429 (rate-limited); Wispr Flow Mac App Store ID returned HTTP 402. Pre-existing review quotes from the prior doc stand; no fresh App-Store extracts in this pass.
- **X/Twitter generally** — only one specific tweet was successfully extracted via WebSearch snippet; broader X scraping not attempted (low ROI vs. cost).

**Cross-corroboration rule:** every claim has a primary URL footnote. Aggregator sources marked `*(affiliate)*` inline. Quotes >10 words are blockquoted with the original handle/source.

---

## 1. Failure modes (cross-tool synthesis)

### 1.1 Hallucinations on silence — the dominant model-level failure

**Pattern:** Whisper-family models fed pure silence, music, or background-only audio produce stock training-data ghosts — credits, "Thanks for watching!", subtitle-author signoffs. The phenomenon is well-documented and is **language-specific by training-data origin**: each language has its own canonical hallucinations.

**Evidence — language-specific catalog** (via OpenAI Whisper Discussion #1873 [^w1] which the community has been crowdsourcing for ~2 years):

| Language | Canonical silence hallucination | Source of the ghost |
|---|---|---|
| English | "Thanks for watching!" / "Welcome to a new video" / "Transcription by CastingWords" | YouTube creator outros, transcription-service watermarks |
| Russian | "Продолжение следует" (To be continued); "Редактор субтитров А.Синецкая Корректор А.Егорова"; "Субтитры сделал DimaTorzok" | Russian dubbed-film credits; YouTube subtitle attributions |
| Chinese | "由 Amara.org 社群提供的字幕" (subtitles by Amara.org community); "中文字幕志愿者 杨茜茜" | Volunteer-subtitled YouTube content |
| Czech | "Titulky vytvořil JohnyX" | Czech subtitle creator credits |
| Arabic | "ترجمة نانسي قنقر" (Translation by Nancy Qanqar) | Arabic-dubbed-film credit canonicals |
| German | Public-broadcaster subtitle credits | ARD/ZDF subtitle imprints |
| Spanish | "Thanks for watching!" equivalents | YouTube dubbed outros |

The Russian "Продолжение следует" hallucination is independently observed in **macparakeet #222** [^mp222] — Whisper Large v3 Turbo on system-audio capture during a meeting recording produced repeated `Продолжение следует` for the English-speaking user. The macparakeet maintainer's investigation note:

> "The artifact is not limited to live preview. It also appears in the saved post-meeting transcript. Repro on the latest local recording split the source: microphone-only 90s excerpt transcribed cleanly; matching system-audio excerpt produced repeated `Продолжение сле[дует]`"

This means the bug surfaces in real product environments, not just contrived silence tests — system-audio capture (often quieter, with codec artifacts) trips the same training-data ghost.

The `@dimonb` tweet [^x1] (Russian dev, Jan 2024) is the cleanest one-line explanation, paraphrased: *"funfact: if you give OpenAI Whisper silence, it recognizes it as 'Редактор субтитров А.Синецкая Корректор А.Егорова' or 'Продолжение следует…'. Conclusion: trained on audio with subtitle tracks)."*

**Tool-level confirmation that this is unsolved at the product layer:**
- **FluidVoice #294** [^fv294] (Apr 22 2026, OPEN, maintainer-acknowledged): all-silence recordings hallucinate looping text (`"he was a student"` repeated). Maintainer altic-dev: *"I've been thinking about it too actually. Full silence causes issues. Thinking what's an optimal VAD to do it with."* The fact that a project specifically focused on real-world dictation hasn't shipped silence-VAD by May 2026 is itself the data point: **VAD-as-silence-guard is still a per-app implementation problem in 2026**, not a solved layer of the stack.
- **whisper.cpp** has `min_silence_duration_ms` exposure for downstream apps to use; many apps don't.

**Frequency:** dominant model-level failure across every Whisper-based tool. The OpenAI cookbook itself acknowledges the issue [^w1].

### 1.2 First-word / cold-start losses — a *different* failure than hallucinations

This is the second mass-pattern, and it isn't a Whisper bug — it's an audio-pipeline activation latency problem on top of Whisper.

**FluidVoice #236** [^fv236] (CLOSED, with detailed root-cause analysis):
> "When activating dictation via hotkey, there is a significant delay (~500ms–1s+) before the microphone actually starts capturing audio. Any words spoken during this startup window are permanently lost… Press the dictation hotkey, immediately begin speaking 'Hello this is a test' — Expected: full sentence; Actual: 'This is a test'."

The FluidVoice author traced it to:
1. ~200ms `Task { @MainActor }` dispatch overhead;
2. Synchronous start-sound playback before `ASRService.start()`;
3. ~85–275ms `configureSession()` to force `AVAudioSession`;
4. Further overhead in audio-tap installation.

**VoiceInk #385** [^v385] (OPEN, multi-user, "Consistently mis-transcribed initial sentence"):
> "VoiceInk consistently misses or incorrectly transcribes the first few words when I start speaking. After the initial words, transcription becomes stable and accurate."

Reproduced across **Whisper Large v3, Large Turbo, and Large Turbo Quantized** — model-agnostic, points to the same activation-window problem. Multiple users in the thread:
- jackielii (Nov 2025): *"It looks like there is always a mic warmup time, like the first word, or the first few words are not registered, i.e. probably flat waveform."*
- zsidnam (Nov 2025): *"I am consistently running into this as well. I don't remember this happening in previous versions; it seems like it is a relatively new issue."*

**VoiceInk #687** [^v687] (May 6, OPEN — fresh): intermittent empty/truncated transcripts after hotkey; reporter notes it's *not* limited to immediately-after-launch — happens during normal use later in the session. Suggests there's a second cold-start mechanism beyond cold-app — possibly model paging or audio-engine sleep.

**VoiceInk #595** [^v595]: "Local model transcription slow after idle — keep model memory paged in" — same family, model-side rather than audio-side.

**FluidVoice #276** [^fv276] (CLOSED): unconditional `guard pcm.count >= 16_000` (1 second at 16kHz) silently drops sub-1s utterances. Comment in code scoped to whisper.cpp's known assertion failure, but the guard runs on Parakeet/Apple-Speech too where it isn't needed. **Short utterances ("yes", "no", "stop", "undo", "next") never produce output and there's no error toast.** This is a particularly insidious pattern because the user thinks the hotkey didn't fire.

**VoiceInk #686** [^v686] (May 4, OPEN — fresh): *"If I say a very short phrase and quickly press the button after, then it won't write anything, just a space."* User's mental model: "starts recording immediately, also starts initializing the model immediately, and then if I press the button before the model finishes initializing (~500ms on M2 MBA), it doesn't use the recording at all."

**Aggregate pattern:** the cold-start failure family is a *product surface* problem (audio pipeline + model warmup + activation race), not a model problem. Every dictation tool ships its own variant; none have publicly solved it. This is less famous than Whisper-hallucinations but probably more frequent in real use.

### 1.3 Word-duplication / looping artifacts (Parakeet-specific)

**macparakeet #102** [^mp102] (CLOSED, maintainer-confirmed):
> "It doesn't [remove] word duplicates and also does not allow to attach a prompt to a LLM to instruct to clear text, so you always have to spend a lot of time rereading so that looks like it has been typed, not spoken text"

Maintainer (`@moona3k`): *"So this is the default behavior/output from the Parakeet model."*

This is the Parakeet analog of Whisper's silence-loop: the model itself emits stutters/duplicates that aren't in the audio, and individual products handle (or don't handle) them in post-processing. **MacWhisper's "Remove duplicated segments" toggle** *also doesn't always work* per the prior doc's Trustpilot quote. The dedupe-in-post-process layer is a recurring weak spot — too aggressive removes correct repetitions ("very, very"), too loose leaves model loops.

### 1.4 Cross-language code-switching collapses ("Franglais")

**FluidVoice #214** [^fv214] (CLOSED — acknowledged-but-unfixable per maintainer): Parakeet 3 TDT multilingual produces "Franglais" mid-sentence — keeping French syntax but substituting badly-chosen English words. Concrete example from the issue:

> Said (FR): *"ce que j'étais dit, c'était juste un exemple, mais qu'est-ce que tu penses de la conversation? Est-ce que tu trouves qu'on pourrait mettre autre chose de mieux que ça? Dis-moi"*
>
> Got (Franglais): *"The mot wizard que je ai dit c'était just an example, but you think that that conversation là? Est-ce que tu trouves que s it's qu'on pourrait mettre autre chose, non de mieux que ça dis moi"*

Maintainer altic-dev: *"This is the model's behavior and not something I can fix easily, unfortunately:("*

This is a **multilingual-model failure mode**, distinct from "wrong-language-detected". The model picks a language token *per token* and flips mid-clause when the speaker code-switches. Implication for Untype: a language *whitelist* (already requested in VoiceInk #518) doesn't fix this — what's needed is per-segment language locking with a confidence threshold.

**FluidVoice #247** [^fv247] (CLOSED, partial-fix, multi-round bug report): Cohere Transcribe outputs *English* for French input, including looping translation hallucinations:
> Input: *"Je vous les ai expliqué"*
> Output: *"I'm going to go to the hospital. I'm going to go to the hospital. I'm going to go to the hospital. I'm going to go to the hospital."*

The `@Keysz` reporter confirmed even after the fix and explicit language selection, it didn't always hold. **Cloud STT providers can have their own language-detection bugs distinct from Whisper / Parakeet.**

### 1.5 Wrong-language detection (no whitelist)

This is the prior-doc's VoiceInk #518 territory. Refresh:

- **VoiceInk #611** [^v611] (Mar 2026, OPEN — *fresh frame on the same problem*): user wants a **single keyboard shortcut to toggle between two languages**: *"I use VoiceInk in both German and English throughout the day — sometimes even within the same app (e.g., German email, then English Slack, both in the browser). Power Mode covers per-app defaults nicely, but when I need the other language in the same app, I have to dig into settings every time."* — argues against #499 (auto-switch-by-keyboard-layout) because *"I type in one language but dictate in another."*
- **VoiceInk #561** [^v561]: iOS keyboard extension locked to English even with multilingual Parakeet V3 selected — language-switching UI doesn't reach iOS.
- **VoiceInk #484** [^v484]: dedicated voice-translation feature request — distinct from "language detection" and from "multilingual STT".

The taxonomy users want (across these issues) is three-dimensional: (1) STT input language, (2) output language for translation, (3) per-app/per-context binding. None of the OSS tools currently expose all three cleanly.

### 1.6 Acoustic-accuracy substitutions ("apartments → ports")

Concrete failures users post are valuable because they reveal **what sounds the model is confusing**. From **macparakeet #217** [^mp217] (May 4, OPEN — fresh):

> Said: *"the noise is constant, including at night. Okay, let's restart the search, I guess. Can you do some research on the best ways to use AI to look for apartments?"*
>
> Got: *"The noise is during close, including at night. Okay, let's pretty start the search, I guess. Can you do some research on the best ways to use AI to look for ports?"*

Three substitutions:
- "constant" → "during close" (phoneme-similar mush)
- "restart" → "pretty start" (re→ pretty: classic Parakeet error mode where the prefix gets re-tokenized)
- "apartments" → "ports" (long word → short-word collapse — Parakeet drops middle phonemes under uncertainty)

Maintainer's note: same model, no algorithmic change, suggests OS / audio-input drift rather than a regression.

**afadingthought** [^afa] confirms a related pattern across tools: monolingual STT engines tend to **drop unfamiliar long words to short rhyming words** under low confidence rather than emit `<unk>` or a confidence flag — which is the *worst* failure mode for downstream polish layers (the LLM rewrite plausibilizes the wrong word).

### 1.7 AI-polish layer infidelity and error leakage

Two distinct sub-modes:

**1.7a — Polish layer rewrites meaning, not just style.** Already documented in the prior doc for Wispr (Trustpilot). New corroboration:

- **HN 47040375 (freeflow Show HN)** [^hn40375] — multiple commenters mention switching away from Wispr/Gemini-voice because the polish stage rewrites their sentences. Concrete quote (commenter on Gemini voice input): *"Gemini's voice input ... literally THE WORST, always trying to transcribe in the wrong language and even if the language is correct produces the uttermost crap imaginable."*

**1.7b — Polish layer error messages typed into user's document.** This is the *terrifying* failure: the LLM call fails (rate-limited, bad key, model overloaded), and instead of falling back to raw transcription, the *error string itself* gets typed.

**FluidVoice #242** [^fv242] (CLOSED, gnarly bug):
> "When AI post-processing is enabled, if the underlying LLM API call fails, the error message is returned as the 'final text' and typed directly into the user's active application. For example, a user dictating into a document could see `Error: HTTP 503: This model is currently experiencing high demand. Spikes in demand are usually temporary. Please try again later.` inserted instead of their spoken words."

Code paths surfaced in the issue: `Empty API response → returns "<no content>"`; `Any LLM error → returns "Error: {description}"`. This is the kind of bug that survives until the first user has it inserted into a Slack message to their boss. **For Untype: never let polish-layer error strings reach the insertion path; always graceful-degrade to raw STT.**

**FluidVoice #320** [^fv320] (May 4, OPEN): "Cannot turn off AI Enhancement mode" — adjacent: users actively *trying to escape* the polish layer because of the same issues, and the toggle doesn't always honor their choice.

### 1.8 Numbers, dates, currency — mostly model-good, polish-bad

Lower direct-complaint volume than expected. The prior doc's PH-review ask for *"customisable math-symbol conversion"* is the strongest single signal. **Cross-cut from sources:**

- Whisper-family generally renders numerals well in English (e.g. `47`, `15:45`, `$1,250.99`) when the prompt is normal speech. Failure mode is **inconsistent format choice** — same model can render the same number as `1250` vs `1,250` vs `one thousand two hundred fifty` across runs.
- **Russian-specific** (habr.com 1026778 [^habr2]): "Что такое **N+1** проблема" gets mistranscribed by Cluely to "Что такое **эн плюс один** проблема" — the model spelled out the alphanumeric token rather than preserving `N+1`. This is a **code-vocabulary collision** that hurts technical Russian dictation specifically.

### 1.9 Acronyms & code identifiers

Strongest evidence is in the **habr.com 1026778** [^habr2] deep-dive on Russian-IT vocabulary drift (see §3 below). Generalized failure pattern: technical acronyms pronounced naturally (not spelled out) collapse to a homophone:
- "Kafka" → "кофта" (sweater) or "как-то" (somehow)
- "subscriber pattern" → "сабскрайп патерн"
- "try-except" → "трое-детей" (three children) — the most damaging because it's a Russian phrase that *parses*
- "retry" → "ритри" or just "три" (three)
- "Kubernetes" with Russian stress → mangled
- "nginx" \[энджи́никс\] → mangled

The article quantifies: vanilla Whisper achieved **~34% WER on technical terms** vs. ~7% with the team's fine-tune — an order-of-magnitude gap that's not bridgeable by polish prompts alone.

For English, the analog is `userInput` rendered as `user input` and `API` as `ay pee eye` (already in the prior doc + competitor-test-drive kit). **macparakeet #95** [^mp95] is a fresh data point on the symbol side: users want to dictate `-` and `/` symbols and the dictation pipeline doesn't have a vocabulary entry for them.

### 1.10 Self-correction handling ("send to John, no, Sarah")

Cross-source signal is thin in 2026-04-18→05-07 window. The prior doc's Wispr complaints stand. New point: **HN 47060832** [^hn60832] (Show HN: macOS transcription apps frustration) — multiple commenters argue that *"voice as composition"* (treating dictation as drafting) breaks because **stream-of-consciousness self-corrections require the polish layer to read intent, and most polish prompts are too dumb to.** From Aqua HN 39828686 (cited in prior doc) — adamesque, SCdF, noahjk all noted self-correction as the dictation-tool failure that drives them back to keyboard.

Implication: the *Reviewing* state in Untype's state machine — where the user can edit *before* insertion — is the only architectural answer that doesn't require the model to read the user's mind.

### 1.11 Long-form / stalls / cross-channel bleed

- **VoiceInk #437, #338** [^v437] (CLOSED / OPEN respectively): "Request timed out when transcribing a file"; "hanging at 'Transcribing'" — pre-2026-04 issues but not solved.
- **YooMoney habr article** [^habr3] documents enterprise-grade stack: with naive 25-30 second chunking, Whisper cuts mid-phrase and loses context. They needed **Silero VAD + faster-whisper + initial_prompt + hotwords + speaker diarization via temporal overlap** to get production-quality call-center transcription. The lesson for product apps: long-form transcription is a *pipeline engineering* problem, not a model problem.
- **Cross-channel audio bleed** (YooMoney): in dual-channel recordings, whispered audio from one channel leaks into the other and Whisper generates *duplicate or garbled text*. Solved by RMS-based filtering. This is meeting-recording territory, but if Untype ever adds meeting capture, it'll hit this.

---

## 2. Tool-specific deltas (since 2026-04-18)

Only listing what's *new* vs. the prior doc.

### 2.1 VoiceInk

- **#687** (May 6) — intermittent empty/truncated transcripts during normal use, multi-session (not just cold-start).
- **#686** (May 4) — short-phrase race with model init.
- **#672** (Apr 27) — fresh high-CPU-in-background bug; continues the pattern from prior doc's #634, #642, #645.
- **#611** (Mar 26) — fresh framing of the multilingual ask: shortcut to toggle between 2 languages, *not* keyboard-layout-bound.
- **#639** (Apr 12) — feature ask: detect whispered speech and apply preprocessing. Connects to Aqua's "shared-space mode" white space.
- **#499** (Jan 18) — change language by macOS keyboard input source (different from #611's user-driven toggle).

### 2.2 FluidVoice

- **#294** (Apr 22, OPEN) — silence-hallucination ask, maintainer engaged on VAD design — **fresh primary-source confirmation that VAD-as-silence-guard is unimplemented in 2026 mainstream apps.**
- **#214** (Mar 20, CLOSED-acknowledged-unfixable) — Franglais code-switching with Parakeet 3 multilingual; concrete French→Franglais example.
- **#247, #246** — Cohere Transcribe French quality bugs (model-side, not pipeline-side).
- **#249** — "models missing big sections of speech" with Parakeet v2/v3 + Apple Speech (CLOSED for repro request — bug not denied).
- **#236** (CLOSED) — first-word drop, with detailed code-path root cause from Opus.
- **#242** (CLOSED) — AI error message typed into user's document.
- **#276** (CLOSED) — sub-1s utterances silently dropped by `minSamples` guard meant for whisper.cpp.

### 2.3 macparakeet (entire repo is fresh — pre-2026-04 history is small)

Active monthly (v0.5.6 → 0.6.0 in April-May 2026), 200+ issues. Transcription-quality signal:
- **#222** (May 4, OPEN) — Whisper Large v3 Turbo on system audio hallucinates `Продолжение следует` (Russian "to be continued") for English-speaking user. Confirmed by maintainer to be system-audio specific.
- **#217** (May 4, CLOSED) — concrete acoustic-substitution example ("apartments → ports").
- **#102** (CLOSED) — Parakeet word-duplication is default model behavior, no built-in dedupe.
- **#95** (Apr 10) — symbol typing (`-`, `/`) not supported.
- **#112** (Apr 18) — feature-ask: model RL-learns new languages from user corrections.

### 2.4 macparakeet vs. VoiceInk vs. FluidVoice — comparative read

All three OSS tools see the same failure modes. Differences in *how the maintainer responds*:

- **FluidVoice** ships engineering fixes (VAD discussion, first-word root-cause analysis, error-fallback fix) but lags multilingual model behavior (treats #214 as model-not-mine).
- **VoiceInk** has many more open issues (~187 in prior doc, more since), maintainer responses are slower; the issue tracker is the most comprehensive *failure-mode catalog* of the three.
- **macparakeet** is the youngest project and the maintainer responds to almost every issue within 24h, but the project is single-engine (Parakeet) so multilingual cross-cuts surface as `Продолжение следует`-style ghosts not as language-detection bugs.

---

## 3. Russian-language pain points

The prior doc had effectively zero Russian-language signal (one mention of VoiceInk #518's "Polish detected as Russian" was the entire surface). This pass — driven by `@dimonb`'s tweet, two habr deep-dives, the macparakeet `Продолжение следует` issue, and inference from the OpenAI hallucination corpus — fills that gap.

### 3.1 Whisper hallucinates *Russian* on silence

Independent corroboration, three sources:

- `@dimonb` X tweet [^x1] (Jan 2024) — first widely-shared identification: silence becomes either *"Редактор субтитров А.Синецкая Корректор А.Егорова"* (subtitle-editor credit) or *"Продолжение следует…"* (to be continued).
- OpenAI Whisper Discussion #1873 [^w1] adds *"Субтитры сделал DimaTorzok"* and *"Редактор субтитров Е.Воинова Корректор А.Кулакова"* as further variants.
- macparakeet #222 [^mp222] (May 4 2026) — same hallucination triggered by *system-audio* capture for an English-speaking user, i.e. the bug fires even when the user has nothing to do with Russian. **System audio (codec compression, low-volume background) is enough acoustic ambiguity to land the model in a Russian training-data attractor.**

This is bad for Russian-locale Untype users (the hallucination will appear *to make sense* and not be flagged) and bad for English-locale users with any Russian-locale background audio source.

### 3.2 Russian-IT vocabulary drift — quantified

The strongest single Russian-language source is `habr.com/ru/articles/1026778/` [^habr2] — *"Why Cluely and others can't hear Russian IT folks: how Whisper breaks and what we did about it"*. Documented failures:

| Spoken (Russian dev mid-sentence) | Whisper output | Failure type |
|---|---|---|
| Kafka | "кофта" (sweater) / "как-то" (somehow) | English-tech term → Russian homophone |
| subscriber pattern | "сабскрайп патерн" | Phonetic transliteration, no recovery |
| try-except | **"трое-детей" (three children)** | Plausible Russian phrase = polish layer can't catch it |
| retry | "ритри" / "три" (three) | Same as above |
| Kubernetes (Russian stress) | mangled | Stress-pattern mismatch on borrowed term |
| nginx \[энджи́никс\] | mangled | Pronunciation drift on transliterated brand |

Real example from the article:
> Said: *"Что такое N+1 проблема, как её избегают в SQLAlchemy и в Django?"*
>
> Cluely: *"Что такое эн плюс один проблема, как её избегают в эс-кью-эль-алкемия и в данже?"*

Vanilla Whisper WER on Russian technical: **~34%**. Authors' fine-tune: **~7%**. The fine-tune required (1) a 4,000-term technical dictionary with metaphone-based phonetic matching, (2) session-context injection into Whisper's `initial_prompt`, and (3) LLM post-processing of low-confidence segments. **None of the four shipping macOS dictation apps (Wispr/Superwhisper/VoiceInk/FluidVoice) currently exposes Russian-IT context-injection or has a dev-vocabulary dictionary.**

### 3.3 Enterprise Russian failure modes

`habr.com/ru/companies/yoomoney/articles/1012870/` [^habr3] — YooMoney call-center transcription:

- Internal corporate terminology and abbreviations not recognized.
- 25-30s fixed chunks cut phrases mid-sentence in Russian (long sentences are common; Russian has freer word order so mid-cut is more semantically destructive than in English).
- Cross-channel bleed produces duplicate/garbled text across speaker channels.

**Their stack (all not in any consumer app):** Silero VAD, faster-whisper, `initial_prompt` + `hotwords` + explicit `language="ru"`, RMS-energy filtering for cross-channel, segment-merging diarization.

### 3.4 Russian users using English-locale apps

macparakeet #102 [^mp102] (the word-duplication complaint) is filed by a Russian-name user using an English-language app — pattern: *non-English speakers using English-defaulted dictation tools end up doing extra rework on the polish stage* because the cleanup prompts assume English idioms. Similar implicit pattern across VoiceInk #561 (iOS keyboard locked to English even when Parakeet V3 multilingual is selected) and FluidVoice #214 (Franglais).

### 3.5 Implications for Russian as a target audience

- Russian is **not** an easy target because Whisper's Russian quality is high on clean, monolingual, native speech (per habr's own caveats — close to ideal on tiny model in clean conditions). The pain is concentrated in:
  - Russian-IT speech with English code-switching (the habr 1026778 use case);
  - Background-audio-in-Russian-locale environments (the macparakeet #222 ghost);
  - Long-form Russian where 30s-chunking destroys grammatical structure.
- A Russian-IT-focused Untype mode (with `initial_prompt` injection of common Russian IT vocabulary, Cyrillic↔Latin-aware polish prompt, and a `try-except → трое-детей` blacklist post-processor) would be a small, opinionated feature with a real audience. **No competitor ships this.**

---

## 4. Signal density / sourcing notes

### Cross-corroboration map

| Claim | Independent sources |
|---|---|
| Whisper hallucinates language-specific credits on silence | OpenAI Discussion #1873; Habr 853916; X (`@dimonb`); HN 44645506; HN 41994278; HN 41974687; HN 41991298; macparakeet #222; FluidVoice #294 |
| First-word / cold-start losses are a category-wide audio-pipeline failure | FluidVoice #236; VoiceInk #385 (Whisper Large v3 + Turbo + Turbo Quantized confirmed); VoiceInk #687, #686, #595 |
| Sub-1s utterance silent-drop | FluidVoice #276 (root-cause in source code) |
| AI-polish error string typed into user's document | FluidVoice #242 (gnarly + obvious) |
| Multilingual code-switching collapses ("Franglais") | FluidVoice #214 (concrete repro) + maintainer "model behavior" |
| Russian "Продолжение следует" silence-hallucination triggered by *system audio* | macparakeet #222 (with maintainer split-source repro) + cross-language pattern in #1873 |
| Russian-IT vocabulary drift (Kafka → кофта) | Habr 1026778 (one source, single team, but quantitative WER measured) |

Single-source claims with no independent replication:
- Habr 1026778 quantitative numbers (~34% → ~7% WER fine-tune). Trustworthy by methodology (technical dictionary + metaphone + session prompt) but only one team's measurement.
- FluidVoice #214 Franglais — single user repro; pattern is consistent with Parakeet 3 multilingual model architecture but no second filer confirmed.

### What the prior doc had that this doc strengthens

- VoiceInk #518 wrong-language detection — **strengthened** by VoiceInk #611 (toggle-shortcut frame), #561 (iOS lock), #499 (keyboard-layout binding) and FluidVoice #214 (the Franglais variant).
- VoiceInk first/last word loss (Danny Smith blog) — **strengthened** to a multi-source pattern via VoiceInk #385, FluidVoice #236, VoiceInk #687, VoiceInk #686.
- Wispr hallucinated/auto-edited polish — **strengthened** by FluidVoice #242 (the polish-error-leakage variant) and the broader silence-hallucination taxonomy in §1.1.

### Open questions for the next refresh

- Reddit primary sourcing remains unattainable through `WebSearch` and `WebFetch`. A future refresh should use Wayback machine on specific known thread IDs (which would need to be sourced via Google or aggregator hops first), or a Reddit-authenticated tool / MCP.
- Apple App Store reviews returned 429/402 in this pass. Worth retrying with a delay / different fetcher before the next quarterly refresh.
- X/Twitter: only one tweet captured. Russian-IT Twitter (and `@dimonb`'s broader thread) likely has more material; not mined here.
- whisper.cpp Issue tracker: my targeted "thanks for watching" search returned 0 hits; the ggerganov repo organizes hallucination reports under different terminology. A broader sweep (`hallucination`, `silence`, `loops`, `repeat`) would surface more.
- VoiceInk paid-license users may file via Beingpax's private support channels rather than GitHub; that signal is invisible here.

---

## 5. Untype implications

Limited to what the data showed; no speculation.

1. **A silence-VAD before the STT call is table-stakes, not a polish.** FluidVoice maintainer is *still designing* one in May 2026 (#294). Untype shipping VAD-as-silence-guard from day-one is a credible "we don't pollute your document with Russian subtitle credits" pitch — *especially* since Untype's `[Reviewing]` state means a hallucinated `Продолжение следует` would at least be visible to the user before insertion, but better to never show it.
2. **First-word loss is a separate engineering problem from STT quality.** The audio-pipeline activation race (FluidVoice #236 root-cause analysis) is reproducible and can be designed around — pre-arming the audio tap on hotkey-down rather than hotkey-up, and warming the model on hotkey-press rather than hotkey-release. Worth verifying Untype's current flow doesn't reproduce this.
3. **Polish-layer failure → raw-STT fallback, not error-string typed.** FluidVoice #242 is the single scariest bug in the corpus. Untype's polish stage should *never* return an error string to the insertion path; always graceful-degrade to raw transcription. Worth a unit test.
4. **Sub-1s utterance drop is a UX choice, not a workaround.** FluidVoice's hard 16k-sample guard silently kills `"yes"` / `"no"` / `"undo"`. Untype should let short utterances through (or surface "no audio captured" toast).
5. **Language-toggle hotkey is a small Tier-2 feature with strong demand.** VoiceInk #611's framing — "I dictate in DE and EN within the same app" — is exactly the bilingual professional ICP that Untype's multilingual pitch targets. One-shortcut-toggle-between-two-languages is a half-day feature.
6. **Russian-IT mode is an opinionated, defensible niche.** Habr 1026778 documents a 5x WER gap for Russian devs vs. fine-tune. Untype can't ship a fine-tune, but it *can* ship: (a) `initial_prompt` injection with common Russian IT vocab; (b) a Cyrillic↔Latin-aware polish prompt that preserves English code identifiers verbatim; (c) a small post-processor for known false-friends (`трое-детей → try-except`). Total scope: a few days of work + a vocabulary file. No competitor has this.
7. **Word-duplication post-processor (Parakeet-flavored) is a safe default.** Untype should run a conservative dedupe pass on Parakeet output (e.g. consecutive identical bigrams with sub-200ms gap). macparakeet's maintainer treats this as user-config; Untype can default it ON because `[Reviewing]` lets the user catch over-correction.
8. **Self-correction is a `[Reviewing]`-state win, not a polish-prompt win.** The HN/Aqua stream-of-consciousness commenters keep landing on the same conclusion: polish prompts can't reliably read user intent on "no, Sarah." The *visible review* before insertion is the architectural fit. Already in Untype's plan; this research strengthens the argument for keeping it Tier-1.
9. **Cross-locale system-audio is a sleeping hazard.** macparakeet #222 shows that an English-speaking user can get Russian hallucinations from system audio alone. If Untype ever adds meeting/system-audio capture, this needs a forced-language hint at the STT call.
10. **Don't ship an aggressive polish layer without an off-switch.** FluidVoice #320 (May 4: *"Cannot turn off AI Enhancement mode"*) is users actively trying to escape polish because of all the above failure modes. Untype already plans polish as a per-mode opt-in; this is the right default — but the off-switch needs to be visible, not buried.

---

## 6. Source log

### GitHub Issues / Discussions (primary)

[^w1]: OpenAI Whisper Discussion #1873 — Share your hallucinations here — `https://github.com/openai/whisper/discussions/1873`
[^fv294]: FluidVoice #294 (Apr 22 2026, OPEN) — Detect and discard all-silence recordings — `https://github.com/altic-dev/FluidVoice/issues/294`
[^fv214]: FluidVoice #214 (Mar 20 2026, CLOSED) — Franglais Parakeet 3 multilingual — `https://github.com/altic-dev/FluidVoice/issues/214`
[^fv247]: FluidVoice #247 (Apr 1 2026, CLOSED) — Cohere French gibberish — `https://github.com/altic-dev/FluidVoice/issues/247`
[^fv236]: FluidVoice #236 (Mar 29 2026, CLOSED) — Activation delay first-word drop with code-path RCA — `https://github.com/altic-dev/FluidVoice/issues/236`
[^fv242]: FluidVoice #242 (Mar 31 2026, CLOSED) — AI error string typed into user's document — `https://github.com/altic-dev/FluidVoice/issues/242`
[^fv276]: FluidVoice #276 (Apr 14 2026, CLOSED) — Sub-1s utterance silent drop, code-quoted — `https://github.com/altic-dev/FluidVoice/issues/276`
[^fv320]: FluidVoice #320 (May 4 2026, OPEN) — Cannot turn off AI Enhancement — `https://github.com/altic-dev/FluidVoice/issues/320`
[^v385]: VoiceInk #385 (Nov 10 2025, OPEN, multi-user) — Consistently mis-transcribed initial sentence — `https://github.com/Beingpax/VoiceInk/issues/385`
[^v687]: VoiceInk #687 (May 6 2026, OPEN, fresh) — Intermittent empty/truncated transcription — `https://github.com/Beingpax/VoiceInk/issues/687`
[^v686]: VoiceInk #686 (May 4 2026, OPEN) — Short phrase no output, model-init race — `https://github.com/Beingpax/VoiceInk/issues/686`
[^v595]: VoiceInk #595 (Mar 18 2026, OPEN) — Local model slow after idle — `https://github.com/Beingpax/VoiceInk/issues/595`
[^v611]: VoiceInk #611 (Mar 26 2026, OPEN) — Toggle shortcut for two languages, German/English — `https://github.com/Beingpax/VoiceInk/issues/611`
[^v561]: VoiceInk #561 (Mar 1 2026, OPEN) — iOS keyboard locked to English — `https://github.com/Beingpax/VoiceInk/issues/561`
[^v484]: VoiceInk #484 (Jan 10 2026, OPEN) — Voice translation feature ask — `https://github.com/Beingpax/VoiceInk/issues/484`
[^v437]: VoiceInk #437 / #338 — file-transcription stalls and timeouts — `https://github.com/Beingpax/VoiceInk/issues/437`
[^mp222]: macparakeet #222 (May 4 2026, OPEN) — Russian "Продолжение следует" on system audio — `https://github.com/moona3k/macparakeet/issues/222`
[^mp217]: macparakeet #217 (May 4 2026, CLOSED) — apartments → ports acoustic substitution — `https://github.com/moona3k/macparakeet/issues/217`
[^mp102]: macparakeet #102 (Apr 11 2026, CLOSED) — Parakeet word duplication is default — `https://github.com/moona3k/macparakeet/issues/102`
[^mp95]: macparakeet #95 (Apr 10 2026, OPEN) — Symbol typing (- /) ask — `https://github.com/moona3k/macparakeet/issues/95`

### Hacker News

[^hn40375]: HN 47040375 — Show HN: freeflow (Feb 2026) — `https://news.ycombinator.com/item?id=47040375`
[^hn60832]: HN 47060832 — Show HN: macOS transcription frustration → built own (Feb 2026) — `https://news.ycombinator.com/item?id=47060832`
[^hn645506]: HN 44645506 — Complete silence hallucinated as "ترجمة نانسي قنقر" (Jul 2025) — `https://news.ycombinator.com/item?id=44645506`
[^hn41974687]: HN 41974687 — Whisper hallucinations in medical transcription (Oct 2024) — `https://news.ycombinator.com/item?id=41974687`
[^hn41991298]: HN 41991298 — Whisper hallucination researcher report (Oct 2024) — `https://news.ycombinator.com/item?id=41991298`
[^hn42119948]: HN 42119948 — Whisper transcribed 7M medical conversations (Nov 2024) — `https://news.ycombinator.com/item?id=42119948`
[^hn41994278]: HN 41994278 — Evaluating Whisper hallucinations on different silences (Oct 2024) — `https://news.ycombinator.com/item?id=41994278`

### Russian-language / habr / X

[^habr1]: habr.com 853916 — Whisper в медицине склонен к галлюцинациям — `https://habr.com/ru/news/853916/`
[^habr2]: habr.com 1026778 — Why Cluely and others can't hear Russian IT folks (with quantitative WER) — `https://habr.com/ru/articles/1026778/`
[^habr3]: habr.com YooMoney 1012870 — Production Russian STT pipeline (Silero VAD + faster-whisper + initial_prompt) — `https://habr.com/ru/companies/yoomoney/articles/1012870/`
[^x1]: `@dimonb` X tweet (Jan 2024) — Whisper Russian silence-hallucination origin — `https://x.com/dimonb/status/1749759167521263619`

### Substack / blog (incremental)

[^afa]: afadingthought — Best AI Dictation Tools for Mac (already cited in prior doc; referenced here for cross-cut on long-word collapse) — `https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac`

### Aggregator / second-hand (flagged)

- onresonant.com Reddit roundup — used in the prior doc; unchanged in this one. *(affiliate)*
- getvoibe.com / writingmate.ai / aidictation.com / wisprflow.ai's own comparison pages — cited only where they reproduce primary quotes. *(affiliate)*
