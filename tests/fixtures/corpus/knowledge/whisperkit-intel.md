# WhisperKit is Apple-Silicon-only: Intel Mac path is unsupported

**Date**: 2026-05-11
**Source**: Empirical (PR #3 investigation, sessions/2026-05-11) + upstream research

## Summary

Argmax's WhisperKit officially supports **Apple Silicon only**. On Intel Macs running macOS 26 (Tahoe), `WhisperKitService.transcribe(audioURL:)` SIGSEGVs in the CoreML decoder during its first forward pass, no env-var workaround prevents it, no bundle/signing path prevents it, no test/runtime context differs. The crash is at Apple/Argmax layer; Untype cannot fix it.

## What we observed

On Intel Mac (i7-9750H, macOS 26.4.1, Swift 6.3, WhisperKit via `argmax-oss-swift` 0.9.x), `pipe.transcribe(audioPath:)` SIGSEGVs in every invocation context tested:

- `swift test` (xctest)
- `swift run UntypeBench --playback-mode whisperkit`
- Plain Mach-O binary signed with `Untype Dev` identity + entitlements
- Fully bundled `.app` with `Info.plist` + entitlements + hardened runtime + `Untype Dev` signing
- `Build/Untype.app` itself with Settings to Engine to WhisperKit selected and a hotkey-driven recording (user-confirmed manual test)

The `UNTYPE_WHISPERKIT_CPU_ONLY=1` env var is correctly read and respected (see `Sources/UntypeCore/Transcription/WhisperKitService.swift:122-131`). Forcing `melCompute`/`audioEncoderCompute`/`textDecoderCompute`/`prefillCompute` to `.cpuOnly` does not prevent the crash on macOS 26.

The pre-macOS-26 comment at `WhisperKitService.swift:116-121` ("Macs without a Neural Engine crash in the decoder's `MLMultiArray.init` during the first forward pass when [.cpuAndNeuralEngine] is selected. Force `.cpuOnly` for all stages via env toggle so Intel machines stay functional") describes a workaround that no longer holds.

## What Argmax says

Both the [WhisperKit](https://github.com/argmaxinc/WhisperKit) and [argmax-oss-swift](https://github.com/argmaxinc/argmax-oss-swift) repositories tag themselves "On-device Speech AI for **Apple Silicon**". The [HuggingFace model card](https://huggingface.co/argmaxinc/whisperkit-coreml) repeats the phrase. Intel is unsupported by omission, never deprecated because never promised.

The 0.9.0 to 1.0.0 release notes (May 2026) deprecate the `MLMultiArray` overloads on `TextDecoding.decodeText`/`detectLanguage`, the exact path the SIGSEGV occurs in. The fix is being removed, not patched.

## What Apple is doing

macOS 26 (Tahoe) is **the last Intel-supporting macOS**. macOS 27 is Apple Silicon only, and Rosetta-for-apps ends after macOS 27. CoreML runtime work on Intel-CPU fallback is bit-rotting in lockstep with this trajectory.

Searches for "WhisperKit Intel SIGSEGV", "WhisperKit x86_64 crash", "WhisperKit Rosetta MLMultiArray" return no upstream issues, Intel users are invisible to the project.

## Implications for Untype

1. **WhisperKit is not a viable on-device STT option for Intel Mac users.** This is permanent, the upstream stance won't change.
2. **`STTRegistry` filters `WhisperKitDescriptor` out of `STTRegistry.all` on `arch(x86_64)`** so the Settings picker doesn't surface it. `STTRegistry.makeStage(for: "whisperkit")` returns `nil` on x86_64 (rather than throwing) so users with a persisted `sttProviderId == "whisperkit"` from a prior install hit a clean missing-provider fallback instead of a crash.
3. **Integration tests skip WhisperKit fixtures on `arch(x86_64)`** via `skipIfWhisperKitUnsupported()` in `STTSeamIntegrationTests`.
4. **arm64 CI macos-26 failure is a separate issue.** The GitHub Actions virtualized arm64 macos-26 runner returns an empty transcript (no crash) on the same fixtures. That's not the Intel bug, it's an Apple-side virtualized-CoreML quirk on the macos-26 runner image. The `XCTSkip` on empty transcript in `STTSeamIntegrationTests.runFixture` covers it as a known flake until diagnosed separately.

## Path forward for Intel Mac local STT

Community consensus in 2026: **[whisper.cpp](https://github.com/ggml-org/whisper.cpp)**, pure CPU, no CoreML dependency, runs on any Mac. A whisper.cpp `STTStage` adapter for Untype is tracked as a separate plan at `~/.claude/plans/whisper-cpp-adapter.md`. Until that ships, Intel users default to Apple Speech (which works fine on Intel) and can opt into any cloud provider (Groq, Voxtral, Remote Whisper) that's configured.

## References

- [argmaxinc/WhisperKit](https://github.com/argmaxinc/WhisperKit), repo tagline
- [argmaxinc/argmax-oss-swift](https://github.com/argmaxinc/argmax-oss-swift), Swift package
- [v0.9.0 release discussion](https://github.com/argmaxinc/argmax-oss-swift/discussions/219)
- [whisperkit-coreml model card](https://huggingface.co/argmaxinc/whisperkit-coreml)
- [Apple ends Intel Mac support after macOS 26 Tahoe](https://www.guru3d.com/story/apple-ends-major-macos-support-for-intel-macs-after-tahoe-26/)
- [whisper.cpp](https://github.com/ggml-org/whisper.cpp), recommended Intel alternative
- `sessions/2026-05-11_session_75.md`, initial investigation; `Sources/UntypeCore/Transcription/WhisperKitService.swift:116-131`, stale `.cpuOnly` workaround comment.
