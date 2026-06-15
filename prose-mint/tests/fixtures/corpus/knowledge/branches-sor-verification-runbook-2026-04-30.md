# Branches S / O / R: Manual Verification Runbook

**Date**: 2026-04-30 **Status**: Open. The three "Immediate, manual verification" items from session 53 are still unverified as of session 59. **Goal**: close them in a single ~30 min run once the Ubuntu inference host is up.

---

## Context

Three end-to-end paths landed at commit `a582051` (session 53) but were explicitly deferred for live verification, unit tests can't reach the mic, the tap-target popover, or remote services. Session 53 lines 219–237 enumerate them:

1. **Branch S, alternates popover regression.** The stream migration moved the read path from `AppleSpeechService.lastSegments` to `chunk.alternatives`. Belt-and-suspenders fallback is in place; the tap-a-word path remains unconfirmed.
2. **Branch O, Ollama polishing end-to-end.** New `OllamaPolishingAdapter` + Settings picker entry; never exercised live against a real Ollama server.
3. **Branch R, RemoteWhisper STT end-to-end.** New OpenAI-compatible `/v1/audio/transcriptions` adapter; never exercised against `faster-whisper-server`.

Branches O and R require an inference host. The chosen host is a dedicated Ubuntu dual-boot box on a laptop with RTX 5090 mobile + 64 GB RAM, see [`inference-host-ubuntu-setup-2026-04-30.md`](inference-host-ubuntu-setup-2026-04-30.md).

Branch S.1 (alternates popover) is **fully local** and can be closed on the Mac at any time without the inference host.

---

## Pre-flight (≈ 8 min, mostly inference-host dependent)

### Local app & permissions
- `./bin/build.sh` from `/Users/costa/Projects/Untype`
- `open Build/Untype.app`, confirm menu-bar icon, no Dock icon
- System Settings to Privacy & Security:
  - Microphone, Speech Recognition, Accessibility, all granted to
    `Build/Untype.app`. Re-signed bundle preserves TCC because of the
    stable `Untype Dev` identity (see `signing-setup.md`).
- Open a log terminal:
  ```
  log stream --predicate 'process == "Untype"' --info --debug
  ```

### Inference host (Ubuntu via Tailscale)
- Ollama reachable: `curl -s http://<ubuntu-host>:11434/v1/models` returns `gemma3:27b`, `llama3.3:70b`, `qwen2.5:72b`.
- faster-whisper-server reachable: `curl -s http://<ubuntu-host>:8080/v1/models` returns Whisper models.
- SSH tunnel for Ollama (Untype hardcodes `localhost:11434`):
  ```
  ssh -N -L 11434:localhost:11434 <user>@<ubuntu-host>.tailXXXX.ts.net
  curl -s localhost:11434/v1/models | jq '.data[].id'   # confirms tunnel
  ```
- Untype Settings to Remote Whisper URL: `http://<ubuntu-host>.tailXXXX.ts.net:8080`, Model: `large-v3`.

---

## Branch S: STT seam (≈ 8 min)

STT settings are read at recognition time (`SettingsSTTSection.swift:11–12`), so engine swaps don't require restart.

### S.1: Apple Speech + alternates popover regression *(Mac-only, no host needed)*

This is the load-bearing check from Branch S and the highest-fragility item.

- Settings to Transcription Engine to "Apple Speech (on-device)"
- Hotkey to speak: *"I would like to test the alternate suggestions"*
- Confirm: text appears in Original view, polishing runs, insertion works.
- **Tap a word in the Original view.** Candidates popover should appear with ≥ 2 alternatives for at least one word.

**PASS** = popover renders with alternates. **FAIL** = empty popover or no popover (regression in `chunk.alternatives` plumbing, file as bug, fix before further architecture lands).

### S.2: Groq STT *(Mac + cloud, no Ubuntu host needed)*

- Confirm `KeychainStore.read(account: "groq.apiKey")` is populated (skip step if not, note as DEFERRED, not FAILED).
- Settings to Transcription Engine to "Groq (whisper-large-v3)"
- Hotkey to speak short phrase.

**PASS** = transcription returns within ~3 s, polishing runs.

### S.3: RemoteWhisper sanity *(needs Ubuntu host; deeper checks in Branch R)*

- Settings to Transcription Engine to "Remote Whisper"
- Confirm fields: URL `http://<ubuntu-host>.tailXXXX.ts.net:8080`, Model `large-v3`.
- Hotkey to speak short phrase.
- `journalctl -u fws -f` on Ubuntu shows `POST /v1/audio/transcriptions`.

**PASS** = transcription returns, server log shows the request.

---

## Branch O: Ollama polishing (≈ 10 min for all three models)

> ⚠ **Polishing changes require app restart.** Caption at
> `SettingsPolishingSection.swift:28`. The router is built once at
> launch, selecting a different model in Settings has no effect until
> Untype is quit and relaunched. The seam-watching follow-up is
> tracked in session 53's "Short-term".

For each of the three models (gemma3:27b, llama3.3:70b, qwen2.5:72b):

1. Settings to Polish Model to select the model.
2. Quit Untype (menu bar to Quit). `open Build/Untype.app`.
3. Hotkey to speak: *"make this clean and grammatical please"*.
4. Watch Original to Polished transition in the overlay.
5. On Ubuntu in another terminal: `ollama ps` should show the selected model active during the request.

### PASS criteria per model

- Polished text differs meaningfully from Original (LLM ran, not a silent fallback to the default Groq path).
- `ollama ps` showed the model active.
- No "polishing failed" / fallback warnings in `log stream`.
- 70b/72b will run at 5–10 tok/s due to partial CPU offload on a 24 GB card. **That's expected, not a regression.** Don't mistake slow for broken.

---

## Branch R: RemoteWhisper deeper checks (≈ 6 min)

STT setting from S.3 still selected; `@AppStorage` persists across launches.

### R.1: Long phrase (~10 s)
- Hotkey to speak ~10 s of natural speech.
- Server logs show one `POST /v1/audio/transcriptions` with the audio payload.
- Untype returns the full transcript; alternates popover still works end-to-end.

### R.2: Short phrase (1 word)
- Hotkey to say one word.
- Untype handles it gracefully, no hang, no crash, polishing still runs (or skipped cleanly for trivially short text).

### R.3: Tunnel-down failure mode
- Stop the Tailscale connection on the Mac (or block port 8080 with a pf rule for a cleaner test).
- Hotkey to speak.
- Overlay should surface an error state; app must not get stuck. Note the exact error message in the session log.
- Restore connectivity; next attempt should recover.

### PASS criteria
- Long, short, and connectivity-down each behave correctly (transcribe / transcribe / visible error + recovery).

---

## Evidence capture

For each of S / O / R, record in the session log:

- **Result**: PASS / FAIL / DEFERRED (with reason, e.g. "Groq key not in Keychain")
- **One-line observation**
- **Any unexpected `log stream` lines** (paste verbatim)
- **Server-side logs** for O and R (Ubuntu `journalctl -u fws` and `journalctl -u ollama`).

---

## After the run

1. `swift build 2>&1 | tail -5`, sanity (no source touched, expected clean).
2. Update today's session log with results per branch.
3. If all three pass: mark session 53's "Immediate, manual verification" trio resolved in the next session log's "What's next" section. Architecture work (Voxtral reasoner, WhisperKit polish, polish-router live rebuild) is unblocked.
4. If any FAIL: open a focused bug fix in its own commit. Don't bundle with verification cleanup.

---

## Critical files (reference, not edited during verification)

- `Sources/UntypeCore/Transcription/STTRegistry.swift`
- `Sources/UntypeCore/Transcription/AppleSpeechDescriptor.swift`
- `Sources/UntypeCore/Transcription/GroqSTTDescriptor.swift`
- `Sources/UntypeCore/Transcription/RemoteWhisperSTTDescriptor.swift`
- `Sources/UntypeCore/Transcription/RemoteWhisperSTTProvider.swift`
- `Sources/UntypeCore/Processing/OllamaPolishingAdapter.swift`
- `Sources/UntypeCore/Processing/CloudProviderConfig.swift` (note the hardcoded `localhost:11434/v1`, see Ubuntu setup guide)
- `Untype/Settings/SettingsSTTSection.swift`
- `Untype/Settings/SettingsPolishingSection.swift`
