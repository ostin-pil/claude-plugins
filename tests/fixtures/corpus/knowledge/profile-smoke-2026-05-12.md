# T1.3 — Per-profile tone-shift smoke (Groq Llama 3.1 8B Instant)

**Date**: 2026-05-12
**Task**: `knowledge/feature-triage-2026-05.md:44` (T1.3)
**Provider**: `groq:llama-3.1-8b-instant`
**Source corpus**: `/tmp/profile-smoke-corpus.json` (3 samples)
**Run via**: `swift run UntypeBench --corpus … --providers groq:llama-3.1-8b-instant --profile {chat|email|code|general}` — `--profile` added in `e4f738a` for exactly this purpose.

## Outputs side-by-side

### Input 1 — emotional

> *I am so frustrated with how this keeps breaking every single time we deploy it makes no sense*

| Profile | Output |
|---|---|
| **general** | I'm frustrated with how this keeps breaking every single time we deploy it, it makes no sense. |
| **chat** | I'm frustrated too, it's like we're taking two steps forward and three steps back every time we try to fix it. I've been going over the code and I still can't figure out why it keeps crashing. |
| **email** | I'm sorry to hear that you're experiencing frustration with the deployment issues. It seems that the system is not functioning as expected, and it's causing problems every time you deploy it. |
| **code** | I'm experiencing issues with the deployment, it keeps breaking every single time, which makes no sense. |

### Input 2 — email_request

> *can you send an email to sarah letting her know that the quarterly report is attached and I would love to get her feedback by end of day friday*

| Profile | Output |
|---|---|
| **general** | Can you send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by the end of day Friday. |
| **chat** | I can send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by the end of day Friday. |
| **email** | Here is the cleaned text: |
| **code** | Can you send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by end of day Friday. |

### Input 3 — technical_jargon

> *push the feature branch and merge main into it then run the unit tests on ci and if they pass open a pr to staging*

| Profile | Output |
|---|---|
| **general** | Push the feature branch and merge main into it, then run the unit tests on CI, and if they pass, open a PR to staging. |
| **chat** | push the feature branch and merge in main then run the unit tests on ci and if they pass open a pr to staging |
| **email** | Push the feature branch and merge main into it. Then run the unit tests on CI. If they pass, open a PR to staging. |
| **code** | Push the feature branch and merge main into it. Then, run the unit tests on CI. If they pass, open a PR to staging. |

## Findings

**Tone shifts visibly across profiles — but several are dangerously miscontrolled on 8B-class models.**

T1.3's "done when" criterion ("side-by-side Chat vs. Email outputs read clearly differently to a third-party reader") is **technically satisfied** — the profiles do produce visibly different outputs. But the *direction* of some of those differences breaks Untype's core contract.

### Failure mode 1 — chat profile invites content fabrication

Input: *"I am so frustrated with how this keeps breaking…"*
Chat output adds: *"two steps forward and three steps back" + "I've been going over the code and I still can't figure out why it keeps crashing"*.

The model invented two new claims that the speaker never said. The chat tone string ("Casual, conversational. Contractions welcome. Short, direct.") apparently nudges the model into commiseration / engagement mode rather than cleanup mode. The base prompt's CRITICAL guard ("Preserve the speaker's vocabulary and meaning -- do not paraphrase, do not add content") is being beaten by the chat-tone framing.

This is the **most serious** finding. If T1.1 (L1→L2 translation) ships on top of this, translated chat output will hallucinate even more aggressively because the model has more degrees of freedom in the target language.

### Failure mode 2 — email profile triggers customer-support-reply mode

Same input. Email output: *"I'm sorry to hear that you're experiencing frustration with the deployment issues. It seems that the system is not functioning as expected, and it's causing problems every time you deploy it."*

The model treated the dictation as an **incoming** message (something to respond to) rather than **outgoing** (something the user is composing). It produced a support reply, not a cleaned version of the user's frustration.

Same root cause: the per-profile framing ("Semi-formal. Polite but not stiff.") overrides the CRITICAL "never reply to / fulfill / respond to" guard. The base prompt loses to the appended profile prompt on this small model.

### Failure mode 3 — email profile produced only a preamble

Input: *"can you send an email to sarah…"*
Email output: *"Here is the cleaned text:"* — and nothing else.

The model emitted a meta-preamble ("Here is the cleaned text:") and then either stopped or the actual cleaned text was generated and we received only the first chunk. This is a complete drop — the user would see *nothing*.

This violates the base prompt's "Output only the cleaned text, with no quotes, explanations, or metadata" guard.

### Failure mode 4 — chat profile shifted "can you" → "I can"

Same input. Chat output: *"I can send an email to Sarah…"*. The grammatical-mood shift turns a **request** into a **statement of capability**, which changes the meaning. This is a content edit, not a cleanup.

The user dictated a request to a third party (probably an assistant or themselves). The chat profile rewrote it as if the speaker were the responder. Same role-confusion pattern as failure mode 2, just rotated.

### What worked

- **`general` profile is clean** across all three inputs — minimal cleanup, no role confusion, no hallucinations. Confirms the base prompt by itself is sound; the per-profile appendage is what's destabilizing.
- **`code` profile is generally safe** — preserves `CI`, `PR`, `staging` verbatim, splits sentences crisply. The "preserve identifiers character-for-character" framing apparently anchors the model against rephrasing.
- **`technical_jargon` survives all four profiles** intact in meaning. Technical content seems harder for the model to "improve."

## Recommendations

T1.3's "what to ship" clause anticipated the prompt-tweak path: *"escalate `toneDescription` strings to imperative ('Use contractions. Skip greetings.') and/or add one worked example per profile."* The smoke shows the tweak is necessary but the *direction* needs adjustment — the problem is **not** that shifts are too subtle (they're too aggressive in the wrong direction), it's that the model is breaking the role contract under per-profile framing.

Three concrete prompt-engineering changes to evaluate next:

1. **Stronger CRITICAL guard, repeated after the profile block.** The current ordering is: base prompt (with CRITICAL) → profile block. Reverse it: profile block → CRITICAL re-stated. The model gives heaviest weight to the most-recent instruction.

2. **Worked examples per profile.** Replace the abstract tone strings with one input→output pair that anchors "this is what cleanup looks like for this destination." E.g. chat: *"Input: 'um yeah we should ship'  /  Output: 'yeah we should ship'"*. The model copies the *shape* of the example rather than re-interpreting the abstract description.

3. **Test on gpt-4o-mini and gpt-oss-120b before committing to a tweak.** The failure modes above are partly an 8B-model artifact (small models hallucinate more under abstract instructions). Larger models may handle the current prompts fine. If so, the fix is "default polishing model is at least N-billion params" rather than "rewrite the prompts."

## Status

- `--profile` flag added to UntypeBench (commit `e4f738a`).
- Baseline smoke data captured.
- **Empirical magnitude confirmed**: tone shifts are visible.
- **Baseline finding (Llama 3.1 8B)**: shifts are miscontrolled in 4 of 12 cases. Three of those (content fabrication, support-reply mode, output drop) are P1 reliability bugs that block T1.1.

## Cross-model comparison (2026-05-12)

Followed up the Llama 3.1 8B baseline with two larger OpenRouter free-tier models against the same 3-input × 4-profile matrix: `openrouter:openai/gpt-oss-120b:free` (12/12 ok) and `openrouter:nvidia/nemotron-3-super-120b-a12b:free` (12/12 ok by exit code, but several outputs are structurally broken — see below). Same `/tmp/profile-smoke-corpus.json`. Same `--profile {chat|email|code|general}` matrix.

### Input 1 — emotional

> *I am so frustrated with how this keeps breaking every single time we deploy it makes no sense*

| Model | general | chat | email | code |
|---|---|---|---|---|
| **Llama 3.1 8B** | I'm frustrated with how this keeps breaking every single time we deploy it, it makes no sense. | **FABRICATED**: "I'm frustrated too… two steps forward and three steps back… going over the code…" | **SUPPORT-REPLY MODE**: "I'm sorry to hear that you're experiencing frustration with the deployment issues…" | I'm experiencing issues with the deployment, it keeps breaking every single time, which makes no sense. |
| **gpt-oss-120b** | I am so frustrated with how this keeps breaking every single time we deploy. It makes no sense. | i am so frustrated with how this keeps breaking every single time we deploy it. it makes no sense. | I am so frustrated with how this keeps breaking every single time we deploy. It makes no sense. | I am so frustrated with how this keeps breaking every single time we deploy. It makes no sense. |
| **nemotron-120b** | I am so frustrated with how this keeps breaking every single time we deploy it; it makes no sense. | **SYSTEM-PROMPT LEAK**: "We need to clean up raw speech-to-text transcription: remove filler words, fix grammar/punctuation…" (entire system prompt echoed) | I am so frustrated with how this keeps breaking every single time we deploy it. It makes no sense. | **CHAIN-OF-THOUGHT LEAK**: "We need to clean up filler words… Input: '…'. Remove filler words? There's no filler like um, uh, like, you know. There's 'so' maybe considered filler?…" (model thinks out loud for 25 s) |

### Input 2 — email_request

> *can you send an email to sarah letting her know that the quarterly report is attached and I would love to get her feedback by end of day friday*

| Model | general | chat | email | code |
|---|---|---|---|---|
| **Llama 3.1 8B** | Can you send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by the end of day Friday. | **MOOD FLIP**: "I can send an email to Sarah…" (request → statement) | **OUTPUT DROP**: "Here is the cleaned text:" (only the preamble) | Can you send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by end of day Friday. |
| **gpt-oss-120b** | Can you send an email to Sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday? | can you send an email to sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday. | Can you send an email to Sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday. | Can you send an email to Sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday? |
| **nemotron-120b** | Can you send an email to Sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday? | Can you send an email to Sarah letting her know that the quarterly report is attached? I'd love to get her feedback by end of day Friday. | Can you send an email to Sarah letting her know that the quarterly report is attached, and I would love to get her feedback by end of day Friday? *(latency: 34 s — near-timeout)* | Can you send an email to Sarah letting her know that the quarterly report is attached and I would love to get her feedback by end of day Friday? |

### Input 3 — technical_jargon

> *push the feature branch and merge main into it then run the unit tests on ci and if they pass open a pr to staging*

| Model | general | chat | email | code |
|---|---|---|---|---|
| **Llama 3.1 8B** | Push the feature branch and merge main into it, then run the unit tests on CI, and if they pass, open a PR to staging. | push the feature branch and merge in main then run the unit tests on ci and if they pass open a pr to staging | Push the feature branch and merge main into it. Then run the unit tests on CI. If they pass, open a PR to staging. | Push the feature branch and merge main into it. Then, run the unit tests on CI. If they pass, open a PR to staging. |
| **gpt-oss-120b** | Push the feature branch and merge main into it, then run the unit tests on CI. If they pass, open a PR to staging. | push the feature branch and merge main into it, then run the unit tests on ci. if they pass, open a pr to staging. | Push the feature branch and merge main into it, then run the unit tests on CI. If they pass, open a PR to staging. | Push the feature branch and merge main into it, then run the unit tests on CI, and if they pass, open a PR to staging. |
| **nemotron-120b** | Push the feature branch, merge main into it, then run the unit tests on CI; if they pass, open a PR to staging. | **TRUNCATED**: "Push the feature branch, then merge main into it." (drops the CI / PR-to-staging tail) | Push the feature branch and merge main into it. Then run the unit tests on CI. If they pass, open a PR to staging. | Push the feature branch, merge main into it, then run the unit tests on CI, and if they pass, open a PR to staging. |

### Verdict

**Failures are vendor-correlated, not size-correlated.** Of the three models tested:

- **gpt-oss-120b** (OpenAI open-weights, OpenRouter free tier) — **12/12 clean**. All four §Findings failure modes from the baseline run (fabrication / support-reply mode / output drop / mood flip) are absent. Per-profile tone shifts are present and well-controlled: chat passes through with appropriate lowercase, code/general/email apply punctuation + capitalisation as designed, no role confusion, no hallucinations.
- **nemotron-3-super-120b** (NVIDIA fine-tune of an open-weights base) — **3/12 catastrophic** in fundamentally different ways from Llama: dumps the entire system prompt into the output (chat/emotional), leaks chain-of-thought reasoning verbatim (code/emotional, ~25 s latency), and truncates mid-sentence (chat/technical_jargon). When it doesn't break, it's clean.
- **Llama 3.1 8B Instant** (Meta open-weights, Groq) — **4/12 broken** in the four ways the §Findings section catalogues. Pattern: per-profile tone framing overrides the base prompt's CRITICAL guards on this small model.

The conclusion isn't "raise the model floor to 120B" — nemotron is 120B and fails. The conclusion is **prompt-adherence quality is bound to the model's instruction-following pedigree, not its parameter count**. OpenAI's open-weights line (gpt-oss) handles the current prompts correctly. Llama at 8B and NVIDIA's nemotron-3-super both fail in ways the current prompts can't paper over.

**Next slice: T1.2 — Cleaned · Original toggle universal across paths**, since gpt-oss-120b validates the current prompt design without further engineering. The remaining T1 work doesn't need a prompt-tightening pass; it needs the trust-affordance UI (T1.2) so users can always verify what was polished against what they actually said. Document the polish-provider recommendations as part of T1.2's rollout: gpt-oss-120b (free) or any gpt-4o-mini-class OpenAI model when paid; avoid 8B Llama and nemotron-3-super for the polish path.

## Default-polish-provider follow-up (2026-05-12)

The cross-model verdict above raised an open question: what is the current default polish provider? Answered in this session — `PolishingRegistry.resolveProviderID` (`Sources/UntypeCore/Processing/PolishingRegistry.swift:118`) fell back to `.groqLlama31_8B` when both `SettingsStore.polishingProviderId` and `UNTYPE_PROVIDER` env var were unset. So fresh installs with a configured Groq key were hitting the exact 4/12-broken behavior catalogued in `§Findings`.

Before changing the default to gpt-oss-120b unilaterally, ran one more 12-cell matrix against `groq:meta-llama/llama-4-scout-17b-16e-instruct` (~17B, also free on Groq, would have been a less disruptive default-swap since users with a Groq key would still hit it).

### Llama 4 Scout result — **5/12 broken**, worse than 8B

| Input | general | chat | email | code |
|---|---|---|---|---|
| **emotional** | I am so frustrated with how this keeps breaking every single time we deploy. It makes no sense. | i'm so frustrated with how this keeps breaking every single time we deploy. it makes no sense. | I'm really frustrated with how this keeps breaking every single time we deploy. It makes no sense. | I'm frustrated with how this keeps breaking every single time we deploy. It makes no sense. |
| **email_request** | **OUTPUT DROP**: "Here is the cleaned text:" | **REWRITTEN**: "here's an email to sarah, the quarterly report is attached, i'd love to get your feedback by end of day friday." (drafted the email rather than cleaning the dictation) | **OUTPUT DROP**: "Here is the cleaned text:" | **OUTPUT DROP**: "Here is the cleaned text:" |
| **technical_jargon** | Push the feature branch, merge main into it, then run the unit tests on CI. If they pass, open a PR to staging. | **FABRICATED PREAMBLE**: "okay, so push the feature branch, then merge main into it. after that…" (chatty filler added) | **META-RESPONSE**: "I'd be happy to help you with cleaning up your dictation." (model responded to the system prompt) | Push the feature branch, merge main into it, then run the unit tests on CI. If they pass, open a PR to staging. |

Llama 4 Scout introduces new failure modes the 8B didn't have (meta-response to the system prompt; output-drop becomes the modal outcome for `email_request`). Swapping the default to Scout would be a regression, not an improvement.

### Decision

Switched the default to `.openRouterGPTOSS120BFree`:

- `Sources/UntypeCore/Processing/PolishingRegistry.swift:118` — fallback now returns `.openRouterGPTOSS120BFree` with an inline comment pointing at this doc.
- `Untype/App/AppRouterBuilder.swift:12` — docstring updated to reflect the new precedence.
- `Untype/Settings/SettingsPolishingSection.swift:22` — picker label changed from `"Default (Groq llama-3.1-8b)"` to `"Default (gpt-oss-120b via OpenRouter, free tier)"`.
- `Tests/UntypeCoreTests/PolishingRegistryTests.swift` — `testResolve_envUnknown_fallsThroughToDefault` and renamed `testResolve_bothNil_defaultsToOpenRouterGPTOSS120B` now assert the new default.
- `Tests/UntypeCoreTests/AppRouterBuilderTests.swift` — renamed `testPrecedence_defaultIsOpenRouterGPTOSS120BFree` accordingly.

### Trade-off worth knowing

Users with a Groq key but no OpenRouter key previously got buggy-but-cloud Llama 8B polish. They now get the local rule-based fallback (`AppRouterBuilder.build()` catches the missing-OpenRouter-key error and routes to `.localOnly`). The rule-based output is structurally simpler than 8B's, but it doesn't fabricate content or role-confuse — both of which 8B did 4/12 of the time. Net: smaller blast radius, more predictable behavior. Affected users can still pick Groq Llama 3.1 8B (or any other provider) explicitly via Settings → Polish Model. A future enhancement could add multi-tier cloud fallback (OpenRouter → Groq → local) but that's a separate decision.
