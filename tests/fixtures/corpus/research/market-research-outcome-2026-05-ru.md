# Market research — Outcome (Untype)

**Дата:** 2026-05-08
**Формат:** Minto pyramid, как в исходной заявке.
**Контекст:** свод по результатам аудита репозитория Untype (research/, knowledge/, sessions/) + проверка свежих внешних источников. Большая часть тезисов исходного отчёта уже закреплена в репо в более узкой формулировке; ниже — версия, привязанная к фактическому позиционированию Untype, а не к обобщённой категории "voice-to-text".

---

## 1. Суть

**Строим, но узко. Wedge зафиксирован: "Speak in your language. Send in theirs."**

- Untype — voice keyboard для macOS, ICP v1 — **билингвальный профессионал (C2)**: L1-носитель (RU/ES/ZH/HI/AR/UK/PT/VI), который ежедневно пишет в L2-английском окружении и платит ежедневный налог на качество текста.
- Категория **voice-to-polished-message** реальна и подтверждена раундами (Wispr ~$700M, Granola $1.5B, Deepgram $1.3B, Willow seed). Окно открыто, но сужается — у Wispr есть военный бюджет на retention после "trust gap".
- Конкуренция уже скучилась вокруг "voice keyboard в общем". Дифференциация Untype — не в STT и не в LLM-cleanup, а в **L1→L2-композиции + transparent routing + надёжной вставке + native-macOS-плотности**.
- Два варианта позиционирования из исходного отчёта **отклоняются**: "mobile-first" (Untype — macOS-only by design) и "voice keyboard for work messages" (слишком широкий ICP, размывает wedge).

---

## 2. Рынок: размер и рост

Цифры — **только направление**, не TAM Untype. Источники — публичные summaries paid-отчётов (FBI, GVR, Precedence, Mordor, FMI). Не сопоставимы напрямую.

| Сегмент | Размер | Год | CAGR | Что измеряет | Релевантность Untype |
|---|---|---|---|---|---|
| Speech-to-text API | $4.66B → $25.28B (2034) | 2025 | ~20.7% | API STT (Big Tech + standalone) | Низкая — инфра-слой |
| ASR (внутри conversational AI) | $2.47B → $9.32B (2030) | 2024 | ~24.8% | ASR в conv-AI стеке | Низкая — IVR/enterprise |
| AI meeting assistants | $3.47B → $21.48B (2033) | 2025 | ~25.8% | Otter / Granola / Fireflies | **Не цель** (явный non-target) |
| Cloud dictation | $8.86B → $22.23B (2034) | 2026 | ~12.2% | Облачная диктовка (broad) | **Ближайший аналог**, но healthcare-heavy |
| Smart dictation systems | $5.5B → $18.8B (2035) | 2025 | ~13.1% | Smart dictation | Средняя — медицинская доля |
| Medical transcription | $80.41B → $108.5B (2031) | 2025 | ~5.1% | Вертикаль, services-heavy | **Не цель** |
| Speech analytics | $4.94B → $15.31B (2034) | 2025 | ~13.2% | Call-center / contact-center | **Не цель** |

**So what:** категория растёт двузначными темпами; Untype — **не "speech-to-text", а узкая полоса между cloud-dictation и AI-writing-tools**. Реальный addressable market — пересечение «macOS-prosumer + bilingual L1→L2», публичных данных нет; будем мерить эмпирически после launch (см. §12).

*Источник в репо:* `research/market-sizing-2026-05.md`

---

## 3. Главный сдвиг

**Сдвиг состоялся: ценность переехала с "распознать речь" на "сделать usable output". Категория капитализируется.**

Свежие раунды (проверены против TechCrunch / Bloomberg / press 2026-05-08):

- **Deepgram** — Series C, **$130M @ $1.3B**, январь 2026. STT-инфра ушла в unicorn-зону → коммодизация STT-качества ускоряется.
- **Wispr Flow** — Series A + extension, **$30M + $25M = $81M total @ ~$700M post-money**, июнь + ноябрь 2025. Военный бюджет на retention; "trust gap"-окно закрывается.
- **Willow** — seed, **$4.5M** (Box Group / YC / Burst), запуск iOS-клавиатуры ноябрь 2025, +50% MoM users. **iOS-only** — не прямой конкурент на macOS, но валидирует тезис "keyboard replacement".
- **Granola** — Series C, **$125M @ $1.5B** (×6 от $250M), март 2026, Index Ventures. Pivot от prosumer-notetaker к enterprise AI app. Подтверждает: meeting-категория — **чужое поле**.

**Дополнительные сдвиги (2025–2026):**
- Modes (Chat / Email / Note / Code / Meeting / Prompt) стали table stakes — Superwhisper, FluidVoice, Hush Touch, Spokenly, VoiceInk все шипают.
- Context awareness формализовался в три слоя: selected text → clipboard (с временным окном против загрязнения) → frontmost-app context через Accessibility. Все три — text-only, без скриншотов.
- "Trust gap"-нарратив (Ryan Shrott, Reddit) — надёжность и прозрачность стали активным дифференциатором, не гигиеной.

*So what:* окно для нового entrant **сужается, не закрывается**. Скорость и узкое позиционирование критичны. Не входить в категорию "ещё одна voice keyboard".

*Источник в репо:* `research/competitive-landscape.md` §5.8

---

## 4. Где рынок уже переполнен

| Зона | Статус | Кто закрыл |
|---|---|---|
| Raw transcription | Commodity | Whisper, Deepgram, AssemblyAI, Apple Speech |
| Meeting notes / summaries | Saturated | Otter, Fireflies, Fathom, Granola, Notta, native в Zoom/Teams/Meet |
| Captions / subtitles | Mature | Descript, Riverside, video-editors built-in |
| Developer STT API | Hard | Конкурируют по WER/latency/pricing |
| Healthcare transcription | Vertical | MS/Nuance, Abridge, Nabla |
| Legal transcription | Niche mature | Dragon, специализированные vendors |
| Call-center analytics | Enterprise | Gong, NICE, Genesys, CallMiner |
| Cross-app voice keyboard "вообще" | Заполняется | Wispr Flow, Willow (iOS), Superwhisper, VoiceInk |

**So what:** ни через один из этих входов Untype не выигрывает. Wedge — не "лучше транскрибирование" и не "ещё одна клавиатура".

---

## 5. Где остаётся gap

| Gap | Почему не закрыт | Кто чувствует | Сила |
|---|---|---|---|
| **L1→L2 composition** (думаешь по-русски, отправляешь по-английски как native) | Whisper берёт 100+ языков на STT, но ни один тул не делает культурно-адекватный rewrite в другую языковую регистровую систему. ChatGPT-флоу слишком trнтый. | Bilingual professionals (C2) | **High — core wedge** |
| Conversation-aware composition (читать тред перед диктовкой) | Wispr делает screenshot-based — это вызвало legal-grief. Privacy-respecting путь (Accessibility-only) пока пуст. | Все, кто отвечает в треды | High |
| Reply-aware tone (короткое и conversational в реплае, полное в чистом композере) | Modes есть, но переключаются по app, не по контексту реплая | Slack/email-power-users | High |
| Reliability-forward UX (proof-of-life, retry, visible routing) | "Trust gap"-нарратив сделал это load-bearing; Wispr именно тут проигрывает | Все после trial-периода | High |
| Inline alternates popover из `SFTranscription.alternativeSubstrings` | Apple отдаёт это бесплатно — конкуренты заставляют re-dictate | Все, кто диктует homophone-rich тексты | Medium |
| Voice commands inline ("new paragraph", "delete that", "quote") | Apple Voice Control умеет, dictation-overlay-категория пуста | Power users | Medium |
| Native-lightweight как surfaced claim (RAM, launch time) | Electron-fatigue реален; никто не делает это видимым аргументом | Mac-power-users | Medium |

*Источник в репо:* `research/competitive-landscape.md` §5.6, `research/user-pain-points-and-desires-2026.md`

---

## 6. Конкурентная карта

| Кластер | Игроки | Релевантность Untype |
|---|---|---|
| Big Tech ASR APIs | Google, AWS, Azure, OpenAI Whisper | Поставщики, не конкуренты |
| AI transcription APIs | Deepgram, AssemblyAI, Speechmatics, Rev AI | Build-vs-buy слой |
| Meeting assistants | Otter, Fireflies, Fathom, **Granola** ($125M @ $1.5B), Notta | **Не цель** |
| Creator tools | Descript, Rev | Не daily messaging |
| Enterprise / Healthcare / Legal | Dragon / Nuance / Abridge / Nabla | **Не цель** |
| OS/mobile dictation | Apple Dictation, Google Keyboard | Реальный baseline competitor (Apple) |
| **Voice-to-polished-message (прямые)** | **Wispr Flow** (~$700M), **Superwhisper**, **Willow** (iOS), VoiceInk, FluidVoice, Voibe, Sotto, Spokenly, Pipit, Aqua Voice | **Прямое поле** |

**Топ-3 непосредственных:**
- **Wispr Flow** — context-aware formatting, кросс-платформенность, $15/мес, cloud-only, Electron, "trust gap"-репутация. Выигрывает на UX out-of-box, проигрывает на reliability и privacy.
- **Superwhisper** — privacy-first, on-device Whisper, кастомные modes, $8.49/мес или $249 lifetime, SOC2/HIPAA. Сложный setup, перегруженные настройки.
- **Apple Dictation** — бесплатно, нативно, лимит 30–60s, без AI cleanup, без custom vocabulary. **Реальный baseline**, который Untype должен очевидно превосходить.

*Источник в репо:* `research/competitive-landscape.md`, `research/competitor-deep-diff-2026-05.md`, `research/oss-competitor-landscape-2026.md`

---

## 7. Лучший wedge

**Wedge: "Speak in your language. Send in theirs." — для билингвальных профессионалов в L2-английском окружении.**

Первый ICP: **C2 — bilingual professional** (по скоринг-матрице из `knowledge/icp-v1.md`, 23/25, top score):
- L1: RU / ES / ZH / HI / AR / UK / PT / VI; рабочий язык L2 = EN.
- Ежедневно пишет в Slack / Mail / Linear / Notion / ChatGPT в L2.
- Платит ежедневный налог: тратит время на перевод, использует DeepL + ChatGPT + редактирует руками, тревожится из-за тона.
- WTP высокая (5/5), reachability через диаспора-комьюнити и in-language YouTube/X.
- White space: ни один competitor не закрывает L1→L2 на уровне «думаю на L1, готовый L2-текст в нужном тоне».

**Secondary ICP — C1 (privacy-pragmatic power knowledge worker, 17/25)** оставлен как fallback и фундамент общих фич.

**Не делать ICP:** "founders / PMs / designers / operators / consultants / creators / non-native speakers" — это **broad-ICP framing из исходного отчёта**, размывает wedge до "ещё одна voice keyboard" и кладёт нас прямо в зону Wispr.

**Не делать сегмент:** mobile-first. macOS-only — это часть дифференциации, не ограничение. Willow уже занял iOS-полосу.

*Источник в репо:* `knowledge/icp-v1.md` §3 + §8 (rejected framings)

---

## 8. Что должно быть ядром продукта

| Слой | Реализация Untype |
|---|---|
| **STT** | Apple Speech on-device (по умолчанию) + Whisper API / Cloud STT как опции |
| **LLM polish** | Cloud LLM (BYOK + managed-key tier); intent-aware прагма (ContextProfile) |
| **Translation polish profile** | L1→L2 как отдельный профиль с культурно-адекватным rewrite (не дословный перевод) |
| **Trust-mechanism** | Cleaned · Original · Source toggle перед вставкой; user-visible routing ("on-device · cloud polish") |
| **Insertion** | CGEvent keystroke injection как primary, clipboard fallback. Без screenshots. |
| **Activation** | Hotkey + non-activating NSPanel (overlay не крадёт фокус у target app) |
| **Modes** | Chat / Email / Note / Reply (per-profile tone). PRD-mode и user dictionary — v2. |
| **Privacy stance** | On-device STT + transparent cloud для polish; никаких screenshots; opt-in telemetry only |
| **Multilingual** | EN + RU/ZH/ES/HI/AR/UK/PT/VI как Tier 2 (по product memo) |
| **Distribution** | macOS-only, Developer ID + позже Mac App Store |

**So what:** **выигрываем не точностью STT и не "ещё одной модой", а количеством случаев, когда L1→L2 текст можно отправить без правки.**

*Источник в репо:* `IMPLEMENTATION_PLAN.md`, `knowledge/workflow-modes-current-state.md`

---

## 9. Что НЕ является дифференциацией

Базовые feature-claims, которые в 2026 — гигиена. Если headline-копия пытается вытащить любой из этих пунктов как USP, переписать.

- "95%+ transcription accuracy"
- "Поддержка 100+ языков"
- "Meeting summaries / action items"
- "Speaker diarization"
- "Export to Notion / Google Docs / Slack"
- "Powered by Whisper"
- "AI improves your grammar"
- "Faster than typing"

Пользователь платит **не за это**, а за **confidence-before-send** — что polished-текст можно отправить как есть.

*Источник в репо:* `research/competitive-landscape.md` §6.3

---

## 10. Настоящая дифференциация

| Ось | Преимущество Untype | Главный конкурент по оси |
|---|---|---|
| **L1→L2 composition** | Думай в L1 — получай native L2-текст с нужным регистром (Tier 2: RU/ZH/ES/HI/AR/UK/PT/VI ↔ EN) | **Никто** не делает это first-class. Superwhisper берёт 100+ STT-языков, но без культурно-адекватного rewrite. |
| **Native macOS density** | Swift/AppKit, non-activating NSPanel, без Electron. Малый footprint surfaced claim. | Wispr Flow (Electron), Superwhisper (heavy native) |
| **Transparent routing + pre-send review** | Cleaned · Original · Source toggle; видно, что ушло в cloud, что осталось on-device | Большинство автоматически вставляют без preview |
| **Reliable insertion** | CGEvent primary с clipboard fallback; без screenshot-pipeline | Все используют clipboard paste, страдают от race-conditions и Codex/Alfred-конфликтов |
| **Lightweight surface** | Тонкий бар над Dock, минимум UI | Superwhisper (feature-heavy), Wispr (cross-platform overhead) |

**Hypothesis** (валидируется через метрики из §12): победный продукт воспринимается **не как dictation tool, а как личный writing interface на двух языках**.

**Возможные расширения moat (логированы как OD-006 / OD-007 — parked, ждут данных):**
- Adaptive style memory **per-recipient/per-channel** (как пишу человеку X в канале Y) — не just per-app.
- Voice-driven correction loop ("сделай короче / мягче / оставь живее") поверх Cleaned-toggle.

*Источник в репо:* `knowledge/lean-canvas-v1.md`, `knowledge/open-decisions.md` (OD-006, OD-007)

---

## 11. Главные риски

| Риск | Почему серьёзно | Митигация |
|---|---|---|
| **Wispr закрывает trust-gap** | $700M post-money даёт военный бюджет на retention; "trust gap"-окно сужается | Bias на reliability/transparency как surfaced claim, не как hygiene |
| **Apple Foundation Models в macOS 26+** | Apple встроит structured-output dictation — может вытеснить нижний слой | Apple FM adapter в дорожной карте обязателен; держать polish-слой умнее системного |
| **Generic-LLM-output trap** | Текст звучит как ChatGPT, не как user → пользователь теряет доверие | Style-trust-метрика (§12 #3) ≥4.0; tone-controls и user dictionary в v1.5 |
| **Translation quality bar** | Для high-stakes deliveries (рабочая переписка с клиентами) bar качества высокий; LLM делает культурные ошибки | Per-language polish profile; явный "show original" fallback; v1 — RU↔EN, ZH↔EN, ES↔EN |
| **WTP не подтверждена** | $7–9/мес — anchored vs Wispr ($15) и Apple (free), но не валидировано пилотом | Flip-trigger в `pivot-build-vs-extend.md`: <2% conversion за 6 мес → перейти на Shape 4 (BYOK-relay) |
| **Retention novelty** | Voice-tools имеют новизну, drop-off через 3–5 дней без nudges | Метрика #6 (D7≥40%, D14≥30%, D30≥20%) без nudges — иначе бьём Wedge |
| **Privacy для аудио** | Голос — sensitive data; cloud-routing требует прозрачности | On-device STT default; cloud — text-only LLM polish с явной маркировкой |

---

## 12. Что валидировать до разработки / launch

Шесть метрик с порогами (стартовые, не commit). Подробно в `knowledge/validation-metrics-v1.md`.

| # | Метрика | Порог | Red flag |
|---|---|---|---|
| 1 | **Frequency** — диктовок/день у активного ICP-юзера | ≥10/день у power, медиана ≥5/день у retained | <3/день после 7 дней |
| 2 | **Send-without-edit rate** | ≥70% (EN), ≥60% (L1→L2) | <50% — polish-слой ломается |
| 3 | **Style trust** ("звучит как я", 1–5 Likert) | средняя ≥4.0; ≥80% юзеров ≥4 | <3.5 — промпт корпоратизирует voice |
| 4 | **Cross-app distribution** | top-5 apps по volume; ни одно >70% (узкий wedge), ни одно >20% (диффузный workflow) | — |
| 5 | **WTP** — conversion за 14 дней при $7–9/мес | ≥3% (managed-key) или ≥6% (BYOK) | <2% за 6 мес → flip на Shape 4 |
| 6 | **Retention** D7/D14/D30 без nudges | 40% / 30% / 20% | D7 <25% — onboarding/positioning сломан |

**Sequencing:** инструментировать в порядке (1)+(4) → (2) → (5) → (6) → (3). Раньше времени не мерить — шум.

**Перед инструментированием — Mom Test discovery:** ICP §6 — 5 целевых вопросов для 5–8 интервью с C2-сегментом. Discovery starter kit лежит вне репо в `~/.claude/plans/discovery-starter/`. **Если интервью не выявляют L1→L2 как top-3 ежедневный pain — вернуть C1 как primary.**

---

## 13. Финальная рекомендация

**Build, узко. Держать линию.**

- **ICP v1:** билингвальный профессионал C2. Не расширять до "founders / PMs / designers / operators" — это broad-ICP-ловушка из исходного отчёта.
- **Wedge:** "Speak in your language. Send in theirs." — единственный непокрытый рынок в дистанции от Wispr / Superwhisper.
- **Платформа:** macOS-only by design. Не уходить в mobile-first до v3+ (Willow на iOS уже есть).
- **Pricing:** $7–9/мес или $79–129 lifetime; sweet spot между Wispr ($15) и Apple (free).
- **Триггеры пересборки:**
  - WTP <2% за 6 мес → flip на Shape 4 (BYOK-relay marketplace) per `knowledge/pivot-build-vs-extend.md`.
  - Mom Test 5–8 интервью без L1→L2 top-3 pain → revert на C1 primary.
  - Style trust <3.5 → перебрать polish-prompt и tone-controls до scaling.
- **v2 expansion paths (не сейчас):** C3 accessibility (X5 A3), второй мозг D2 — обе помечены в `knowledge/pivot-ideas-2026-04-30.md` как parked.
- **Soft v2 идеи из исходного отчёта:** PRD-mode и reply-mode (sharper opinionated templates), per-recipient style memory (OD-006), voice-driven correction loop (OD-007). Не v1.

**Decision:** opportunity реальная, urgency высокая. Wispr / Superwhisper / Willow подтвердили категорию. Новый entrant выигрывает на **более узком сегменте + лучшем L1→L2 + лучшем sense of trust перед отправкой**, не на "ещё одной voice keyboard".

---

## 14. Источники

### Внутренние (репо Untype)
- `knowledge/icp-v1.md` — ICP scoring, C2 primary, rejected framings (§8)
- `knowledge/lean-canvas-v1.md` — wedge, UVP, проблемно-решенческая модель
- `knowledge/pivot-build-vs-extend.md` — Shape 1 vs Shape 4 trigger
- `knowledge/pivot-ideas-2026-04-30.md` — рассмотренные альтернативы (A2 / A3 / D2)
- `knowledge/validation-metrics-v1.md` — 6 поведенческих метрик
- `knowledge/open-decisions.md` — OD-006 / OD-007 (parked moat extensions)
- `knowledge/workflow-modes-current-state.md` — 5 рабочих режимов (Intel / AS / server / BYOK / hybrid)
- `research/competitive-landscape.md` — конкурентная карта, §5.8 funding update, §6.3 NOT-differentiation
- `research/competitor-deep-diff-2026-05.md` — feature-matrix по 8 игрокам
- `research/competitor-test-drive-2026-05.md` — hands-on тест-кит
- `research/oss-competitor-landscape-2026.md` — OSS-cohort
- `research/user-pain-points-and-desires-2026.md` — pain mining по 8 игрокам
- `research/distribution-monetization.md` — pricing baseline, MAS vs Developer ID
- `research/market-sizing-2026-05.md` — directional TAM table

### Внешние (проверены 2026-05-08)
- [Deepgram press — $130M Series C](https://deepgram.com/learn/press-release-deepgram-raises-series-c)
- [TechCrunch — Wispr Notable Capital extension (2025-11-20)](https://techcrunch.com/2025/11/20/as-its-voice-dectation-app-takes-off-wispr-secures-25m-from-notable-capital/)
- [TechCrunch — Wispr Series A Menlo (2025-06-24)](https://techcrunch.com/2025/06/24/wispr-flow-raises-30m-from-menlo-ventures-for-its-ai-powered-dictation-app/)
- [TechCrunch — Willow iOS launch (2025-11-12)](https://techcrunch.com/2025/11/12/willows-voice-keyboard-lets-you-type-across-all-your-ios-apps-and-actually-edit-what-you-said/)
- [TechCrunch — Granola $125M Series C (2026-03-25)](https://techcrunch.com/2026/03/25/granola-raises-125m-hits-1-5b-valuation-as-it-expands-from-meeting-notetaker-to-enterprise-ai-app/)
- [afadingthought — True Differentiators in AI Dictation (2026)](https://afadingthought.substack.com/p/best-ai-dictation-tools-for-mac)
- [Ryan Shrott — Wispr Flow Trust Gap (Medium, Feb 2026)](https://medium.com/@ryanshrott/the-wispr-flow-trust-gap-why-reliability-matters-more-than-hype-in-2026-c7dd55392408)
- [Superwhisper — Modes docs](https://superwhisper.com/docs/modes/modes)
- [FluidVoice releases (GitHub)](https://github.com/altic-dev/FluidVoice/releases)

**Caveat:** TAM-цифры — directional, public summaries paid-отчётов. ±30% коридор. WTP / retention / style-trust пока не валидированы — будут заполнены метриками из §12 после launch.
