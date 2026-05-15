# Untype — Project Status & Health Assessment

> Date: 2026-04-22 | Sessions: 46 | Tests: 101/101 passing

---

## 1. Codebase Health — GOOD

Build clean, 101/101 tests passing, architecture sound and largely follows CLAUDE.md conventions.

### Strengths
- Strong separation of concerns (App / Window / State / Audio / Processing / Settings)
- `AppState` is the single source of truth; no direct UI mutation
- `async/await` + `@Observable` throughout; zero Combine
- AX code properly guarded with `CFGetTypeID` checks before every `as!` cast
- Core business logic has solid test coverage (LLM routing, streaming, scoring, context, thread-context)

### Issues

#### File size violations (12 files exceed 200-line rule)
| File | Lines | Notes |
|------|-------|-------|
| `Tests/.../CloudProviderTests.swift` | 395 | Split into focused test classes |
| `Sources/UntypeAXProbe/main.swift` | 367 | Tool/utility — lower priority |
| `Sources/UntypeBench/Runner.swift` | 323 | Tool/utility |
| `Untype/App/RecordingCoordinator.swift` | 300 | **Primary prod file — split before Phase 3** |
| `Sources/UntypeBench/TranscriptionHarness.swift` | 292 | Tool/utility |
| `Sources/UntypeBench/main.swift` | 250 | Tool/utility |
| `Sources/UntypeCore/Transcription/AppleSpeechService.swift` | 241 | Split streaming vs. non-streaming |
| `Sources/UntypeBench/Report.swift` | 234 | Tool/utility |
| `Tests/.../StreamingTests.swift` | 229 | Test file |
| `Sources/UntypeCore/Processing/CloudProviderConfig.swift` | 223 | Split config vs. validation |
| `Sources/UntypeCore/Processing/AppContext.swift` | 223 | Split profile enum vs. detection logic |
| `Untype/App/AppDelegate.swift` | 222 | Split lifecycle vs. observer setup |

Recommended prod splits:
- `RecordingCoordinator` → state mgmt + `TranscriberFactory` (seam partially extracted in session 46)
- `AppContext` → `AppContextProfile` (enums/tone) + `AppContextDetector` (detection logic)
- `CloudProviderConfig` → config structs + `ProviderConfigValidator`
- `AppDelegate` → lifecycle + `AppObservers`

#### Stale build artifacts in repo root
45 `.o` / `.d` / `.swiftdeps` / `.swiftdeps~` files. `AudioLevelIndicator` was deleted in session 19 but artifacts remain.

Fix: Add to `.gitignore`:
```
*.o
*.d
*.swiftdeps
*.swiftdeps~
```
Then: `git rm --cached *.o *.d *.swiftdeps *.swiftdeps~`

#### Untested layers (expected, low priority)
- `SettingsStore` / `KeychainStore` — Keychain requires real entitlements; fine
- `RecordingCoordinator` — requires mic permission; integration-tested at runtime
- Window views — visual; appropriate

---

## 2. Roadmap Status — ON TRACK, ONE FEATURE MID-FLIGHT

8-phase plan complete. Tier 1 and Tier 3 UX polish shipped. Phase 3 (thread-context reading) is the active front.

### Shipped
| Feature | Status |
|---------|--------|
| Core hotkey-to-paste flow | ✅ |
| Live transcription (Apple Speech + Groq) | ✅ |
| LLM text processing (Anthropic, OpenAI, OpenRouter, local) | ✅ |
| Text insertion (clipboard + AX) | ✅ |
| Review step (Enter/Esc, Cleaned/Original toggle) | ✅ |
| Tier 1: App context detection + chip + override | ✅ Session 44 |
| Tier 3: Retry, alternates popover, UX polish | ✅ Session 42 |
| Settings window | ✅ |
| Silence detection + silence gate | ✅ |
| Launch-at-login | ✅ |
| Error state UX | ✅ |

### In-Flight: Phase 3 — Thread-Context Reading
- `MessagesThreadReader` implemented + 8 tests passing
- `AppThreadReader` protocol defined
- `ContextCaptureCoordinator` seam extracted (ready for wiring)
- Remaining: wire into capture flow, extend prompt template, Settings toggle + chip UI, Mail.app reader (v2)

### Not Started / Deferred
- Tier 2 parity gaps (not yet specified; blocked on Phase 3)
- Slack / web-app thread readers
- Dynamic Type, full VoiceOver support
- High contrast mode

---

## 3. Market Assessment — REAL OPPORTUNITY, 6–12 MONTH WINDOW

### Competitive Landscape
| App | Price | On-device | LLM Cleanup | Context Aware | Edit UI |
|-----|-------|-----------|-------------|---------------|---------|
| Wispr Flow | $15/mo | ❌ Cloud | ✅ Smart | ✅ Screenshot | ❌ |
| Superwhisper | $250 lifetime | ✅ | ⚠️ Model choice | ⚠️ Manual modes | ❌ |
| MacWhisper | $69 lifetime | ✅ | ❌ | ❌ | ❌ |
| macOS Dictation | Free | ✅ | ❌ | ❌ | ❌ |
| **Untype** | TBD | ✅ | ✅ Smart | ✅ Automatic | ✅ |

### Untype's Wedge
1. On-device LLM cleanup, zero configuration — Wispr Flow's power without cloud/privacy tradeoff
2. Edit-friendly results (alternates popover + inline edit) — first in category
3. Context-aware formatting, automatic — simpler than Superwhisper, faster than Wispr Flow
4. Native Swift — snappier than Wispr Flow's Electron
5. Thread-context reading (Phase 3) — no competitor reads the conversation you're replying to

### Market Size
- Speech Recognition: $30B (2026) → $56B (2030), 17% CAGR
- Precedent: VoiceInk at $39.99 has 1,100+ ratings, 4.9/5 — validates $40 willingness to pay

### Distribution
**Direct (DMG)** — not App Store. Global hotkey + AX monitoring + unsandboxed overlay require full system access (same reason Superwhisper is direct-only). 0% commission vs. 15–30% App Store cut.

### Pricing
- **$39–49 one-time** or **$7–9/month** for optional cloud LLM relay tier
- Hybrid: base app one-time; "Pro" subscription for cloud relay / API key management

### Timeline Risk
Wispr Flow is the most resourced competitor. They're cloud-only for context today. If they add on-device inference (Apple Silicon + Core ML), Untype's privacy advantage narrows. Window: ~6–12 months.

---

## 4. Prioritized Recommendations

### Immediate
1. Split `RecordingCoordinator.swift` before Phase 3 wiring pushes it past 350 lines
2. Add `.gitignore` entries for `*.o *.d *.swiftdeps*` and clean repo

### Short-term (Phase 3 completion)
3. Wire `MessagesThreadReader` into capture flow
4. Extend prompt template to include `threadBlock`
5. Settings toggle + chip override for thread-context
6. Smoke-test on real Messages conversations before shipping

### Medium-term (post Phase 3)
7. Mail.app reader (v2)
8. Set up direct sales page before any public announcement
9. Specify and resolve Tier 2 parity gaps
10. Minimal VoiceOver pass
