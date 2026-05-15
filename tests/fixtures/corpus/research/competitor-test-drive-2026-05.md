# Competitor test-drive kit — dictation scripts (EN + RU)

**Date:** 2026-05-07
**Purpose:** Hands-on qualitative evaluation of competing voice-to-text tools using a fixed corpus of 12 passages — 8 contextual + 4 edge-case probes — across English and Russian, in the four professional contexts where Untype gets used (email, Slack, meeting notes, technical/code-adjacent text).

**Companion docs (analytical, not duplicated here):**
- [`competitor-deep-diff-2026-05.md`](./competitor-deep-diff-2026-05.md) — 8-row coverage matrix and positioning deltas
- [`competitive-landscape.md`](./competitive-landscape.md) — broader commercial map + emerging tools
- [`oss-competitor-landscape-2026.md`](./oss-competitor-landscape-2026.md) — OSS-only deep profiles
- [`whisper-bench-2026-04-18.md`](./whisper-bench-2026-04-18.md) — quantitative WER benchmarks (incl. 1 RU sample)

This kit asks how each tool *feels* in the hand, not what its WER number is. Numeric benchmarks live in `whisper-bench-2026-04-18.md`.

---

## How to use this kit

**Time budget**
- Must-test tier (5 tools × 12 passages, ~1 take per passage): **2–3 hours**
- Full bench (10 tools): **4–6 hours**, ideally split across two sessions

**Workflow per tool**
1. Install + grant permissions (Mic, Speech Recognition, Accessibility).
2. Open the four target apps so insertion can be tested without app-switching cost: **Mail.app, Slack, VS Code, Notes.app**.
3. Read each passage once, naturally. No retakes. (Retakes inflate scores — real users get one shot.)
4. Capture the rendered output into the per-tool rubric (§ "Per-tool results template" below).
5. Note any UX delight or pain that doesn't fit the rubric in the **Notes** column.

**Rules of the road**
- One mic, one room, one time of day across all tools (variance kills comparison).
- Read at normal pace — not slow, not rushed.
- Where a tool has a polish layer toggle, run **two passes**: polish off (raw STT), polish on (with default polish prompt). Note which mode produced what.
- For the four Russian-only tests (`*-RU-N`), keep target apps the same — but flip macOS dictation language if testing Apple Dictation.

---

## Pre-flight checklist

- [ ] Single mic chosen and committed (built-in vs. external — pick one)
- [ ] Quiet room, door closed, notifications muted
- [ ] All four target apps open, signed in: Mail.app, Slack, VS Code, Notes.app
- [ ] macOS Dictation: language switcher includes both English and Russian (System Settings → Keyboard → Dictation → Edit)
- [ ] Sketch a one-line free-form note before starting: which mic, which room, what time, what's the latest version of each tool — pasted at the top of each per-tool rubric block

---

## Tools to test — tiered

### Must-test tier (5 tools)

#### 1. Wispr Flow — cloud commercial flagship
- **Install:** `https://wisprflow.ai/` (signup → direct download)
- **Cost:** Free 2k words/wk · Pro $15/mo (or $12/mo annual)
- **Watch:** clipboard-restore behavior across the four target apps; aggressiveness of cloud Llama polish (does it rewrite vs. transcribe?); end-to-end latency feel

#### 2. Superwhisper — commercial local-first
- **Install:** `brew install --cask superwhisper` (v2.13.2 confirmed on Homebrew 2026-05-07)
- **Cost:** Free tier · Pro $8.49/mo or $84.99/yr · Lifetime $249.99
- **Watch:** mode-switching UX (closest analog to Untype's polish profiles); on-device-vs-cloud transparency; pluggable polish LLM choice

#### 3. VoiceInk — OSS GPLv3, prolific
- **Install:** `brew install --cask voiceink` (v1.74 confirmed on Homebrew 2026-05-07)
- **Cost:** Free OSS build via Homebrew · paid license amount unverified at `tryvoiceink.com`
- **Watch:** provider-picker complexity (3 local engines + 9 cloud STT — UX overload risk); default-on-install experience; Smart Modes vs. Untype's polish profiles

#### 4. FluidVoice — OSS GPLv3, exemplary E2E test discipline
- **Install:** `brew install --cask fluidvoice` (v1.5.13 confirmed on Homebrew 2026-05-07)
- **Cost:** Free, BYOK
- **Watch:** AX-based typing vs. clipboard insertion (the only competitor that explicitly markets AX typing — does it actually feel different?); Parakeet vs. Whisper engine quality side-by-side

#### 5. Apple Dictation (macOS Tahoe / 26) — baseline floor
- **Install:** Built-in. Enable in System Settings → Keyboard → Dictation. Add Russian as second language.
- **Cost:** Free with macOS
- **Watch:** how high the floor sits in 2026 — what does the user already get for free; native textfield insertion (no AX cert needed); raw transcript only (no polish layer to compare apples-to-apples on the polish dimension)

### Optional bench (5 tools)

Install only if must-test tier leaves open questions. Each gets ~15–30 min, not a full pass.

| # | Tool | Install | Why bother |
|---|------|---------|------------|
| 6 | macparakeet | GitHub release `moona3k/macparakeet` | Pure Parakeet TDT on Apple Neural Engine, no Whisper fallback — isolates the Parakeet quality story |
| 7 | MacWhisper | `brew install --cask macwhisper` | Transcription-focused (file → text) but real-time mode is a useful counterpoint to dictation-first tools |
| 8 | Aqua Voice | `https://aqua.so/` | Cloud-aggressive polish; only worth testing if Wispr alone leaves the cloud-polish question under-sampled |
| 9 | Spokenly | direct download | Emerging per `competitive-landscape.md` §1.8; same rationale as Aqua |
| 10 | Whispo | GitHub `egoist/whispo` | Cautionary tale (last release 2024-11-22). 15 min just to log how a feature-complete-but-stagnant project feels in 2026 |

---

## Test scripts

Each passage has:
- **Goal** — what edge case it probes
- **Target output** — the rendered text you want to end up with (capitalization, punctuation, formatting)
- **How to read it** — natural prose with normal prosody (no explicit "comma"/"period" commands) unless the passage explicitly tests command mode
- **Watch for** — 3–5 specific gotchas to look for in the output

Code-switching, punctuation-command, number-formatting, and self-correction probes are isolated in the **Edge-case probes** section after the four contextual blocks.

---

### Email / business writing

#### EN-1 — Polished business email (parallel)
- **Goal:** multi-clause polished prose, mid-sentence em-dash, embedded date + currency, salutation/signoff, polite question
- **Target output:**
> Hi Anna,
>
> Thanks for the quick turnaround on the proposal — the revised pricing of $1,250 per seat per month works for us, and we'd like to lock in the annual commitment before March 15th. Could you send the contract to legal@example.com by end of week?
>
> Best,
> Costa
- **How to read it:** Natural pace, normal prosody. Pause briefly at sentence boundaries; the tool's auto-punct should do the rest.
- **Watch for:**
  - Auto em-dash insertion vs. literal "dash" or two hyphens
  - Currency formatting: `$1,250` vs. `1250 dollars` vs. `$1250.00`
  - Email address rendering: `legal@example.com` vs. `legal at example dot com`
  - Paragraph break after the signoff line "Best," — does the tool sense the structural break?
  - Proper noun "Anna" capitalized? "Costa" capitalized?

#### RU-1 — Polished business email (parallel)
- **Goal:** parallel test in Russian — formal vy-form business register, тире, ruble, vy-form salutation, structured signoff
- **Target output:**
> Здравствуйте, Анна,
>
> Спасибо за оперативный ответ по предложению — пересмотренная стоимость 1 250 ₽ за место в месяц нас устраивает, и мы хотели бы зафиксировать годовой контракт до 15 марта. Не могли бы вы отправить договор юристам на legal@example.com до конца недели?
>
> С уважением,
> Костя
- **How to read it:** Russian formal register, normal prosody. Pause at sentence boundaries.
- **Watch for:**
  - Russian тире (`—`) vs. hyphen vs. literal word "тире"
  - Ruble: rendered as `₽` or `руб.` or "рублей"
  - English email address embedded in Russian — does it stay Latin or get Cyrillicized?
  - Vy-form capitalization: tools sometimes lowercase "Вы" mid-sentence (correct in modern Russian, but inconsistent across tools)
  - "Анна" / "Костя" — proper nouns capitalized

---

### Slack / chat

#### EN-2 — Slack message (parallel)
- **Goal:** casual register, @mention, URL, code identifier, emoji-by-name
- **Target output:**
> hey @anna can you take a look at the PR? the regression is in `parsePolishOutput()` — see https://github.com/costakap/untype/pull/247. shipping today, fingers crossed 🤞
- **How to read it:** Casual fast pace. Say "at-anna" for `@anna`. Say "back-tick parse polish output back-tick" or trust the tool to figure it out — note which way it went.
- **Watch for:**
  - `@anna` vs. "at Anna" vs. "@Anna" (capitalization in chat is usually lowercase)
  - URL: full Latin URL preservation, or does it wreck on "github dot com slash..."
  - Backticked code identifier `parsePolishOutput()` — preserved as code-fence, plain text, or hyphenated?
  - Emoji-by-name: 🤞 from "fingers crossed" — substituted, named, or dropped?
  - Sentence-initial lowercase: most tools force-capitalize, but chat register is lowercase

#### RU-2 — Slack message, casual + transliterated brand names (parallel/native hybrid)
- **Goal:** casual Russian register, transliteration of English brand/tool names, English Latin terms embedded in Cyrillic prose
- **Target output:**
> @анна гляди, регрессия в `parsePolishOutput`, посмотри пиар на гитхабе — https://github.com/costakap/untype/pull/247. катим сегодня, скрещиваю пальцы 🤞
- **How to read it:** Casual Russian, fast pace, лёгкий register.
- **Watch for:**
  - "гитхабе" (Cyrillic transliteration of GitHub) — does the tool guess "GitHub" instead?
  - Code identifier `parsePolishOutput` — Latin preserved or transliterated?
  - English URL embedded mid-Russian sentence
  - "пиар" (PR) — common Russian dev-slang, does the tool render it correctly or as "PR" or as "ПР"?
  - Casual lowercase register preserved or force-capitalized?

---

### Meeting notes / dictation

#### EN-3 — Meeting notes with disfluencies + self-corrections (parallel)
- **Goal:** stream-of-consciousness with um/uh/you-know, two mid-sentence self-corrections, partial restart, action items
- **Target output (best-case polished):**
> Action items from today: ship the polish prompt rewrite by Thursday, get Sarah to review the latency dashboard, and follow up with the Wispr team about the enterprise pricing tier.
- **How to read it (verbatim, including disfluencies):** *"Okay, um, action items from today are, uh — ship the polish prompt rewrite by, uh, end of week, no wait, by Thursday. Get John to review the latency dashboard — actually no, get Sarah, Sarah's the one who owns it. And, you know, follow up with the, the Wispr team about the enterprise pricing tier."*
- **Watch for:**
  - Disfluencies: dropped, kept verbatim, or partially cleaned?
  - Self-correction "John → Sarah": does the polish layer remove the strikethrough, or does it leave both names?
  - "no wait, by Thursday" — does the polish keep "Thursday" and drop "end of week"?
  - Partial restart "the, the Wispr" — collapsed to single "the" or kept as stutter?
  - Tools without polish (Apple Dictation, raw STT) should produce verbatim disfluent output — that's correct behavior, not a fail; record what you saw vs. what the polish tool did

#### RU-3 — Meeting notes, native Russian (not parallel)
- **Goal:** Russian-native dictation with Russian fillers, Russian-style self-correction, name in three case forms (Костя → Косте → Костей), action items in Russian
- **Target output (best-case polished):**
> Действия после встречи: к четвергу подготовить новый prompt для полировки, отдать Анне на ревью дашборд по латентности, и связаться с командой Wispr по поводу корпоративного тарифа.
- **How to read it (verbatim, including Russian fillers):** *"Так, ну, по итогам встречи, э-э, надо к, к концу недели, нет, лучше к четвергу, подготовить новый prompt для полировки. Отдать Косте на ревью дашборд — а, нет, не Косте, Анне, Анна сейчас этим занимается. Ну и, короче, связаться с командой Wispr по поводу, типа, корпоративного тарифа."*
- **Watch for:**
  - Russian fillers (ну, э-э, типа, короче) — dropped, kept, or partially cleaned?
  - "к, к концу недели" — single "к" or stutter preserved?
  - Self-correction "Косте → Анне" — polished out or left verbatim?
  - "prompt" mid-Russian — Latin preserved or Cyrillicized as "промпт"?
  - "Wispr" — preserved as Latin brand name, transliterated as "Виспр"?
  - Russian name case forms: does the polish layer get Russian morphology right (Анне = dative)?

---

### Technical / code-adjacent

#### EN-4 — Technical prose (parallel)
- **Goal:** code-adjacent vocabulary that tortures dictation tools — acronyms, framework names, file path, version string, variable name, snake_case
- **Target output:**
> The new transcription pipeline reads from `~/Projects/Untype/Audio/` and POSTs JSON to the cleanup API over HTTP/2 — version `v1.5.12` of the SwiftUI overlay binds `userInput` directly to the AppKit hosting controller. Make sure the CoreML model loads on first launch, not lazily.
- **How to read it:** Natural pace. Pronounce "API" as "ay-pee-eye", "JSON" as "jay-son", "HTTP" as "h-t-t-p", "SwiftUI" as "swift-u-i", "AppKit" as "app-kit", "CoreML" as "core-m-l". Say "tilde slash projects slash untype slash audio slash" or pause and trust the tool — note your choice.
- **Watch for:**
  - Acronyms: `API` / `JSON` / `HTTP/2` — uppercase preserved? Does HTTP/2 render with the slash and 2?
  - File path: `~/Projects/Untype/Audio/` — tilde, slashes, capitalization
  - Backticked code identifier `userInput` — code-fence applied, camelCase preserved?
  - Version string `v1.5.12` — kept tight or expanded to "v one point five point one two"?
  - PascalCase brand names `SwiftUI` / `AppKit` / `CoreML` — preserved or split?

#### RU-4 — Russian-native technical, code-switching (not parallel)
- **Goal:** Russian discussion that necessarily code-switches to English for tech terms, Russian dev slang
- **Target output:**
> Нужно поправить API в SwiftUI компоненте, и потом запушить ветку в GitHub. Открой PR — там Костя оставил пару комментов на парсере, надо их отресолвить до конца дня. И не забудь обновить версию в `Package.swift` до v1.5.12.
- **How to read it:** Natural Russian dev-team speech — code-switches to English for tech terms are normal, don't force-translate.
- **Watch for:**
  - English terms mid-Russian (`API`, `SwiftUI`, `GitHub`, `PR`) — Latin preserved, transliterated, or split badly across the boundary?
  - Russian dev slang ("запушить", "комментов", "отресолвить") — recognized as Russian or treated as malformed English?
  - Backticked `Package.swift` and version `v1.5.12` — code-fence and exact rendering?
  - "Костя" capitalized? "PR" stays uppercase?
  - The hardest part: tools that lock to one language at a time will mangle this passage. Tools with multi-language detection should glide.

---

### Edge-case probes (4 short standalone scripts)

These are 30–60 second tests that isolate single edge cases. Run after the contextual passages.

#### Probe-1 — Punctuation commands (explicit mode)
- **Goal:** test command-mode punctuation when the tool documents support
- **Target output (EN):** `Hello, world. This is a test of explicit punctuation.`
- **Read aloud (EN):** *"Hello comma world period new paragraph this is a test of explicit punctuation period"*
- **Target output (RU):** `Здравствуйте, мир. Это тест явных команд пунктуации.`
- **Read aloud (RU):** *"Здравствуйте запятая мир точка с новой строки это тест явных команд пунктуации точка"*
- **Watch for:**
  - Tool renders literal word "comma" / "запятая" vs. inserts `,` / `,`
  - "new paragraph" / "с новой строки" — paragraph break or literal text?
  - Tools without command mode will produce literal — that's expected, not a fail; note it as "command mode: not supported"

#### Probe-2 — Numbers, dates, currency, time
- **Goal:** numeric formatting fidelity in both languages
- **Target output (EN):** `We need 47 units by March 15th, 2026 at 3:45 PM, costing $1,250.99.`
- **Read aloud (EN):** *"We need forty-seven units by March fifteenth twenty twenty-six at three forty-five PM costing one thousand two hundred fifty dollars and ninety-nine cents"*
- **Target output (RU):** `Нужно 47 штук к 15 марта 2026 года в 15:45, стоимость — 1 250,99 ₽.`
- **Read aloud (RU):** *"Нужно сорок семь штук к пятнадцатому марта две тысячи двадцать шестого года в пятнадцать сорок пять стоимость одна тысяча двести пятьдесят рублей девяносто девять копеек"*
- **Watch for:**
  - Numerals vs. spelled out: `47` vs. "forty-seven"
  - 12h vs. 24h time rendering
  - Currency symbol vs. words
  - Russian: `15:45` (24h is standard) and decimal comma `1 250,99` (Russian convention)
  - Date format: `March 15th, 2026` vs. `15.03.2026` vs. `March 15, 2026`

#### Probe-3 — Self-correction loop (no explicit punctuation)
- **Goal:** how the polish layer handles two consecutive corrections and a recipient swap
- **Target output (best-case polished):** `Send the email to Sarah at sarah@example.com.`
- **Read aloud (EN, verbatim):** *"Send the email to John, no wait, to Sarah — at sarah at example dot com"*
- **Read aloud (RU, verbatim):** *"Отправь письмо Ивану, нет, погоди, Анне, на anna собака example точка com"*
- **Target output (RU, best-case polished):** `Отправь письмо Анне на anna@example.com.`
- **Watch for:**
  - Both names kept ("John" + "Sarah") vs. polish picks the last one
  - Email address rendering (`@` vs. "at" vs. "собака")
  - Polish layer aggressiveness — does it remove the meta-narration "no wait" / "нет, погоди"?
  - Raw STT tools (Apple Dictation, polish-off mode) should render verbatim — note it as such, not a fail

#### Probe-4 — Code-switching (RU primary with EN brand names)
- **Goal:** Russian sentence with three English brand names mid-stream — the hardest case for monolingual STT models
- **Target output:** `Открой Slack и проверь новый канал для продакт-обновлений, потом запушь ветку в GitHub и сделай PR в main.`
- **Read aloud:** *"Открой Slack и проверь новый канал для продакт обновлений потом запушь ветку в GitHub и сделай PR в main"* — pronounce the English names with their natural English phonetics.
- **Watch for:**
  - "Slack" / "GitHub" / "PR" / "main" — preserved as Latin, or transliterated, or mangled?
  - "продакт-обновлений" — does it get the hyphen?
  - "запушь" — Russian dev slang recognized?
  - Tools that auto-detect language per word/clause will pass; tools with a single-language lock will fail predictably (note which mode the tool was in)

---

## Per-tool results template

Duplicate this block once per tool, keeping the same row order. Scoring vocabulary is qualitative: **clean / minor / major / n/a** for each cell. Numeric WER lives in `whisper-bench-2026-04-18.md`.

```markdown
## <Tool name> — <version>

**Setup:**
- Mic: <built-in MBP 14" / external USB / etc.>
- Target app: <Mail / Slack / VS Code / Notes>
- Polish layer: <off / on — provider + prompt name>
- Language switching: <auto-detect / manual toggle / single-locked>

| Passage   | Verbatim | Punct | Format | Disfluency | Self-correct | Acronym | Code-switch | RU | Latency | Insertion | Polish | Notes |
|-----------|----------|-------|--------|------------|--------------|---------|-------------|----|---------|-----------|--------|-------|
| EN-1 Email      |  |  |  | n/a | n/a | n/a | n/a | n/a |  |  |  |  |
| RU-1 Email      |  |  |  | n/a | n/a | n/a | n/a |  |  |  |  |  |
| EN-2 Slack      |  |  |  | n/a | n/a | minor | n/a | n/a |  |  |  |  |
| RU-2 Slack      |  |  |  | n/a | n/a | minor | yes |  |  |  |  |  |
| EN-3 Meeting    |  |  |  |  |  | n/a | n/a | n/a |  |  |  |  |
| RU-3 Meeting    |  |  |  |  |  | n/a | yes |  |  |  |  |  |
| EN-4 Technical  |  |  |  | n/a | n/a |  | n/a | n/a |  |  |  |  |
| RU-4 Technical  |  |  |  | n/a | n/a |  | yes |  |  |  |  |  |
| Probe-1 Punct   |  |  | n/a | n/a | n/a | n/a | n/a |  | n/a | n/a | n/a |  |
| Probe-2 Numbers |  | n/a |  | n/a | n/a | n/a | n/a |  | n/a | n/a | n/a |  |
| Probe-3 Correct |  |  |  | n/a |  | n/a | n/a |  | n/a | n/a |  |  |
| Probe-4 Switch  |  |  |  | n/a | n/a | n/a |  |  |  |  |  |  |

**Verdict (2–3 sentences):** _What surprised, what disappointed, would I keep using it._

**Untype delta (1 line):** _What this tool does better/worse than Untype today._
```

**Column legend:**
- **Verbatim** — STT accuracy on the words actually spoken (clean = ≈ no errors, minor = 1–2 word errors, major = sentence-level mis-recognition)
- **Punct** — auto-punctuation correctness
- **Format** — paragraph breaks, line breaks, structural formatting
- **Disfluency** — handling of um/uh/ну/типа (clean = removed when polish is on / preserved when polish is off; major = inconsistent or wrong)
- **Self-correct** — does it handle "no wait, X → Y" sensibly
- **Acronym** — uppercase preservation, code identifier handling
- **Code-switch** — mid-sentence language change (n/a for monolingual passages)
- **RU** — Russian-specific quality (case morphology, тире, ruble, vy-form, transliteration); n/a on EN-only passages
- **Latency** — speech-end to text-rendered feel (clean ≈ < 1s, minor ≈ 1–3s, major ≈ > 3s or unpredictable)
- **Insertion** — did it land in the target app correctly (clipboard restore intact, AX-typed without focus steal, etc.)
- **Polish** — quality of the polish layer when on (n/a if tool has none or tested with polish off)

---

## Cross-tool summary

After all per-tool blocks are filled, populate this grid for at-a-glance comparison. Cells: **clean / minor / major / n/a**.

| Passage          | Apple Dict | Wispr | Superwhisper | VoiceInk | FluidVoice | macparakeet | MacWhisper | Aqua | Spokenly | Whispo |
|------------------|------------|-------|--------------|----------|------------|-------------|------------|------|----------|--------|
| EN-1 Email       |  |  |  |  |  |  |  |  |  |  |
| RU-1 Email       |  |  |  |  |  |  |  |  |  |  |
| EN-2 Slack       |  |  |  |  |  |  |  |  |  |  |
| RU-2 Slack       |  |  |  |  |  |  |  |  |  |  |
| EN-3 Meeting     |  |  |  |  |  |  |  |  |  |  |
| RU-3 Meeting     |  |  |  |  |  |  |  |  |  |  |
| EN-4 Technical   |  |  |  |  |  |  |  |  |  |  |
| RU-4 Technical   |  |  |  |  |  |  |  |  |  |  |
| Probe-1 Punct    |  |  |  |  |  |  |  |  |  |  |
| Probe-2 Numbers  |  |  |  |  |  |  |  |  |  |  |
| Probe-3 Correct  |  |  |  |  |  |  |  |  |  |  |
| Probe-4 Switch   |  |  |  |  |  |  |  |  |  |  |

**Top three takeaways (write after the grid is filled):**
1. _<Strongest tool overall and why — one sentence>_
2. _<Sharpest Untype-positioning insight — one sentence>_
3. _<Surprise / inversion of prior assumptions — one sentence>_

---

## Open questions for follow-up sessions

Track here as you test:
- Tools where polish-off vs. polish-on diverged most (suggests Untype should A/B its own polish defaults)
- Edge cases this kit didn't cover that turned up in the wild (background noise, multi-speaker, very quiet voice, accents)
- Insertion mechanism quirks worth specific competitor-doc updates
- Russian-specific failures unique to one tool (could become a Untype positioning angle if Russian users are a target segment)
