# Untype Project Status Report

**Range:** 2026-04-10 to 2026-04-13 (sessions 11–24, ~90 commits)

## What is Untype?

A native macOS voice-to-text overlay app (Swift, AppKit + SwiftUI). Press-and-hold `fn` to dictate, see a live waveform, review the cleaned transcript in an overlay anchored near the focused input, press `Return` to insert at the caret. Goal: a speech-to-message layer that's faster and more forgiving than macOS Dictation and cheaper than Wispr Flow.

---

## Research Conducted (2026-04-10)

Sessions 11 and 12 were a two-day research sprint. 11 product/technical docs + 13 Claude Code workflow deep-dives landed in `research/`.

| Doc | Session | Takeaway |
|---|---|---|
| `cloud-llm-provider-research.md` | 11 | Single OpenAI-compat client covers ~80% of providers; gpt-4o-mini baseline |
| `whisper-vs-apple-speech.md` | 11 | Keep Apple Speech for streaming, add WhisperKit as opt-in final pass |
| `distribution-monetization.md` | 11 | Developer ID only (sandbox breaks core features); freemium + BYOK, Lemon Squeezy |
| `voice-activity-detection.md` | 11 | Silero VAD via FluidAudio, auto-stop after 1.5s silence |
| `competitive-landscape.md` | 11 | Speech-to-message layer niche is open; Wispr Flow is closest |
| `prompt-optimization.md` | 11 | Few-shot + "Editor" role + temp 0.1 + mandatory `stripPreamble()` |
| `text-insertion-compatibility.md` | 11 | CGEvent Cmd+V works everywhere except VMs; fixes: full clipboard snapshot, transient markers, 150ms delay |
| `context-aware-cleanup.md` | 11 | Bundle ID mapping is MVP; zero new permissions |
| `on-device-translation.md` | 11 | One-pass LLM (cleanup + translate) beats dedicated translation models |
| `voice-editing-commands.md` | 11 | Phase-based disambiguation solves command/dictation ambiguity |
| `ralph-loop.md`, `bmad-method.md`, `gsd-workflow.md`, `head-to-head-comparison.md` | 12 | Autonomous workflow frameworks; recommendation: stick with native Claude Code + worktrees for Untype |
| `mcp-servers.md`, `skills-system.md`, `claude-md-rules.md`, `hooks-system.md` | 12 | Claude Code primitive deep-dives |
| `cli-reference.md`, `multi-agent-patterns.md`, `settings-reference.md`, `source-code-insights.md`, `community-patterns.md` | 12 | Operational + community workflow reference |

---

## What Was Achieved

### 2026-04-10 (sessions 11–14)

| Area | Outcome |
|---|---|
| Research | 24 research docs produced across 2 parallel sprints |
| Tooling | `/report` skill, `scripts/strip-co-authored.sh` |
| First manual test | Exercised full flow; found duplicate Dock icon, permissions-flagged-as-missing, etc. |
| Fixes | `setActivationPolicy(.accessory)`, `PermissionsChecker` only flags denied/restricted, permissions menu item, audio level throttle, recording-error cleanup |

### 2026-04-11 (sessions 15–17)

| Area | Outcome |
|---|---|
| Bug sweep | 6 MainActor / concurrency fixes across `RecordingCoordinator`, `ProcessingCoordinator`, `AppDelegate`, `LocalProvider` |
| End-to-end flow working | First successful voice-to-text cycle after 12 debug cycles (sandbox, permissions, DerivedData, Dictation-disabled, stale recognizer, etc.) |
| Xcode project | 14 missing files added to `pbxproj`, HotKey SPM dep wired |
| Sandbox | Disabled for development (blocks CGEvent + Accessibility) |
| Hotkey UX | Removed Enter-as-accept; ⌘⇧Space cycles all states |
| Knowledge base | `knowledge/macos-dev.md`, `knowledge/issues.md` (11 issues), UX audit (8 issues) |
| New skills | `/macos-expert`, `/issues`, `/ux-expert`, `/commit` |
| Convention | `prefix(topic): title` commits documented; `commit-msg` hook strips Co-Authored-By |
| UX quick wins | Red to cyan waveform, "Listening…" relabelled to "Speak now…", SF-Symbol icons |

### 2026-04-12 (sessions 18–21)

| Area | Outcome |
|---|---|
| Notion export | 24 research docs exported; `tools/notion_import.py` built (mistune AST to Notion API, bypasses MCP escaping) |
| UX direction pivot | Replaced ⌘⇧Space toggle with **fn push-to-talk** (Whisper Flow model); `knowledge/ux-direction-2026-04-12.md` as executable spec; second audit folded back into same doc |
| fn push-to-talk impl (8 slices) | `FnPushToTalkMonitor` w/ 200ms debounce, 300ms release grace, `.setup`/`.onboarding` phases, `BlobWaveform`, `FocusedElementLocator` (AXUIElement), adaptive overlay resize, onboarding card w/ passive Globe detection |
| AppDelegate refactor | Extracted `PermissionsCoordinator` and `MenuBarController`; AppDelegate shrank from 287 to 173 lines |
| Cloud LLM (parallel worktree) | `UntypeCore` library split, `KeychainStore`, `CloudProvider` actor (OpenAI-compat), `ProviderRegistry`, 12 HTTP-mapping tests, `UntypeBench` exec + 30-sample EN/RU corpus + pricing table |
| Pivot | MLX dropped mid-session (Intel dev machine); cloud-only path for now |

### 2026-04-13 (sessions 22–24)

| Area | Outcome |
|---|---|
| Stable signing | `bin/build.sh` + local `Untype Dev` identity so TCC grants survive rebuilds; `knowledge/signing-setup.md` walkthrough (incl. Always-Trust gotcha) |
| Follow-ups | Adaptive review-toast height (`NSHostingView.fittingSize`, 72–200pt clamp); caret-aware anchoring via `kAXBoundsForRangeParameterizedAttribute` + absurd-rect rejection; bottom-center fallback |
| Cleanup | `Untype.xcodeproj` retired. SPM via `open Package.swift` is the Xcode path. |
| `/start-session` skill | Read-only briefing skill (counterpart to `/session` and `/report`) |
| OpenRouter pivot | All cloud candidates routed through OpenRouter (user's only key). Added `@free`/`@paid`/`@all` bench shortcuts, per-provider pacing, `--min-interval-ms` autodefault, Retry-After retry, HTTP body capture in errors |
| Bench results (paid) | **`openai/gpt-4o-mini` wins**: 30/30, 1.2s mean, $0.00004/call, best on Russian edge cases |
| Bench results (free) | **`openai/gpt-oss-120b:free` wins**: 30/30, 3.8s mean, good enough for dev default |
| Broken models dropped | `qwen3-32b` (reasoning-mode empties `content`), `gemma-3-4b-it` (rejects system-role messages) |
| Dev default | unset `UNTYPE_PROVIDER` now resolves to `openrouter:openai/gpt-oss-120b:free` + `.cloudPrimaryWithLocalFallback` |

---

## Current State

**Working end-to-end:**
- fn push-to-talk with 200ms debounce + 300ms release grace
- Live cyan blob waveform, silence detection hint
- Caret-anchored adaptive review toast (72–200pt)
- Return inserts, Esc cancels
- First-run onboarding card w/ passive Globe detection
- Cloud cleanup via OpenRouter with transparent local fallback
- Stable ad-hoc signing (`bin/build.sh` + `Untype Dev` identity)
- `UntypeBench` harness over 30 EN/RU samples, 4 bench reports captured

**Committed but not yet manually verified on-device (session 22 follow-ups):**
- Adaptive toast height at 3-word / one-sentence / paragraph scales
- Caret anchoring in Cursor/VSCode vs native fields
- TCC survival across rebuilds (user reported re-prompts; signing path verified, `tccutil reset` recommended)

**Known gaps / tech debt:**
- `RecordingCoordinator.swift` = 208 lines (over 200-line rule)
- `HotKey` SPM dep unused since slice 8a; removal deferred
- `FocusedElementLocator` assumes main screen for AX Y-flip (multi-monitor edge case)
- Mid-session permission revocation not handled
- **Biggest finding from manual testing (session 24): Apple `SFSpeechRecognizer` is the real quality bottleneck, not the LLM cleanup.** Cleaned text is limited by what the recognizer produces.

---

## What's Next

**Immediate:**
1. Manual end-to-end test with `gpt-oss-120b:free` default; verify offline fallback when Wi-Fi yanked mid-recording.
2. Finish verification of session 22 follow-ups (adaptive toast, caret anchoring, TCC stability).
3. Remove unused `HotKey` SPM dep (one-commit cleanup).

**Next investment area (per session 24 finding):** transcription quality, not LLM cleanup. Options:
- Better STT provider (WhisperKit final-pass already researched)
- Diff partial vs final Apple results to recover dropped words
- Cloud STT fallback for hard audio

**Queued slices:**
- Complexity-based routing (free for easy EN inputs, paid for hard/RU)
- Reasoning-mode parser (unblocks Qwen3, fixes GLM residual errors)
- Prompt caching once production provider is locked
- Settings UI (KeychainStore is ready)
- Selector architecture design (tone / output-language in review toast; blocked on key-panel vs NSEvent decision since `OverlayPanel` is nonactivating)
- Cost tracking + usage caps (BYOK prerequisite)
- Bucket-aware pacing (unblocks Gemma if ever wanted back)
- LLM-as-judge quality scoring for bench regression tests
- `RecordingCoordinator` split into `RecognitionStream` helper
- Multi-monitor AX frame conversion
- Lock-mode gesture for long dictations (post-MVP)

**Out-of-MVP, unchanged:**
- MLX local inference (deferred until Apple Silicon dev machine)
- Context detection via bundle ID mapping
- Monetization infrastructure
