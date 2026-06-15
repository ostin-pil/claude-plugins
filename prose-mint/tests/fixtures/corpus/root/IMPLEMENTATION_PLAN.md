# Untype Frontend Implementation Plan

## Context

Untype is a voice-driven speech-to-message layer for macOS. The user presses a hotkey, speaks, and a slim floating bar above the dock shows live transcription, AI-cleans the text, then pastes it into whatever app was focused (Slack, Telegram, email, etc.). The project directory is empty; this is a greenfield build.

## Technology: Native Swift (AppKit + SwiftUI)

Every core requirement (non-activating overlay panel, frosted glass, global hotkeys, clipboard manipulation, microphone, accessibility API) is a first-class macOS API. Electron/Tauri would mean fighting the platform to approximate what Swift gives for free. The UI is a single slim bar, not a complex multi-page app.

**Trade-off**: macOS-only. But this app is deeply system-integrated; a Windows port would be a rewrite regardless.

## Project Structure

```
Untype/
  Untype.xcodeproj/
  Untype/
    App/
      UntypeApp.swift              -- @main entry point
      AppDelegate.swift            -- Menu bar icon, dock hiding, app lifecycle
    Window/
      OverlayPanel.swift           -- NSPanel: floating, non-activating, translucent
      OverlayViewController.swift  -- Hosts SwiftUI BarView
      BarView.swift                -- SwiftUI: the slim bar with state-driven content
    Audio/
      AudioRecorder.swift          -- AVAudioEngine mic capture
      AudioPermissions.swift       -- Permission request handling
    Transcription/
      TranscriptionService.swift   -- Protocol for STT providers
      AppleSpeechService.swift     -- SFSpeechRecognizer (on-device, free, streaming)
      WhisperAPIService.swift      -- OpenAI Whisper API (higher accuracy, post-MVP)
    Processing/
      TextProcessor.swift          -- LLM call to clean/structure text
      PromptTemplates.swift        -- System prompts for cleanup, translation
    Insertion/
      TextInserter.swift           -- Pasteboard + synthetic Cmd+V via CGEvent
    Hotkey/
      HotkeyManager.swift          -- Global hotkey registration
    State/
      AppState.swift               -- Observable state enum driving all UI
    Settings/
      SettingsManager.swift        -- UserDefaults for prefs, Keychain for API keys
      SettingsView.swift           -- SwiftUI settings window
    Resources/
      Assets.xcassets/
      Untype.entitlements
      Info.plist
  UntypeTests/
```

## State Machine

```
[Idle] --(hotkey)--> [Listening] --(audio streaming)--> [Transcribing]
   ^                      |                                    |
   |                      |                         (speech ends / hotkey)
   |                      |                                    v
   +------(Esc)-------- [Reviewing] <-----(AI cleanup)--- [Processing]
                             |                                   |
                          (Enter)                               |
                             v                                   |
                        [Inserting] --> [Idle]                   |
                                                                  |
                          +---------- [Error] <----(error)--------+
                          |              ^            ^            ^
                          |              |            |            |
                          |         (retry)     (mic fail)   (STT fail)
                          |                   from [Listening]  from [Transcribing]
                          v
                     (user dismisses)
                          |
                          v
                        [Idle]
```

Error states:
- `[Error: Mic Denied]` - guide to System Settings
- `[Error: API Failed]` - retry with exponential backoff
- `[Error: Network Offline]` - queue for retry when connection restored
- `[Error: Transcription Failed]` - show raw transcription option

## Implementation Phases

### Phase 1: Skeleton + Overlay Window
- Create Xcode project (macOS, SwiftUI lifecycle)
- `LSUIElement = YES` (hide from dock)
- `AppDelegate` with `NSStatusItem` (menu bar icon)
- `OverlayPanel`: `NSPanel` with `.nonactivatingPanel`, `.fullSizeContentView`, `.borderless`
  - `NSVisualEffectView` background (`.hudWindow` material)
  - Floating level, positioned bottom-center above dock via `screen.visibleFrame`
  - Rounded corners, ~48pt height, ~500pt width
- Basic `BarView` (SwiftUI) hosted via `NSHostingView`
- Hardcoded shortcut to toggle panel
- **Milestone**: key press shows/hides frosted glass bar above dock

### Phase 2: Global Hotkey
- Add `HotKey` SPM package (github.com/soffes/HotKey)
- Register default hotkey (e.g. Cmd+Shift+Space)
- Handle Accessibility permission if using CGEvent tap
- **Milestone**: hotkey works from any app

### Phase 3: Audio Capture
- `AudioRecorder` with `AVAudioEngine` input tap
- Request mic permission (`NSMicrophoneUsageDescription`)
- Capture to buffer, write temp WAV on stop
- Subtle audio level indicator in BarView
- **Milestone**: speak, a WAV file is saved

### Phase 4: Live Transcription (Apple Speech)
- `AppleSpeechService` with `SFSpeechRecognizer` + `SFSpeechAudioBufferRecognitionRequest`
- Stream partial results into `AppState.transcribing(partialText:)`
- BarView shows horizontally-scrolling live text
- **Milestone**: speak and see live text in the bar (free, offline)

### Phase 5: AI Text Processing
- `TextProcessor` via LLM API (provider-agnostic protocol design)
- Protocol-based architecture allows testing multiple providers: OpenAI, Anthropic, local models
- Prompt: clean filler words, fix grammar, keep meaning/tone
- API key stored in Keychain
- State flow: transcription complete, then processing, then reviewing
- **Milestone**: messy speech is cleaned to readable text in the bar

### Phase 6: Text Insertion
- `TextInserter`: save the clipboard, write text, paste into the target app, restore the clipboard
  - **Sandboxed (App Store):** Use Accessibility API (`AXUIElementSetAttributeValue` on focused text field) for direct text insertion
  - **Non-sandboxed (Developer ID):** Use `CGEvent.post()` to synthesize Cmd+V
  - Protocol-based `TextInsertionStrategy` to support both approaches
- Non-activating panel means target app stays focused
- Requires Accessibility permission (both approaches)
- **Milestone**: speak, the AI cleans the result, the text is pasted into Slack/Telegram/etc.

### Phase 7: Pre-Send Review
- In `reviewing` state: show final text, Enter to confirm, Esc to cancel
- Optional inline editing in the bar
- **Milestone**: full end-to-end flow with review step

### Phase 8: Polish
- Settings window (hotkey config, API key, language)
- Launch at login (`SMAppService`)
- First-launch onboarding for permissions
- Smooth animations (bar appear/dismiss)
- Error states in bar
- Basic VoiceOver support: accessibility labels on bar content, state change announcements
- Dynamic Type support for font size preferences
- High contrast mode compatibility

## Key Technical Solutions

| Challenge | Solution |
|---|---|
| Non-activating overlay | `NSPanel` with `.nonactivatingPanel` style mask, designed exactly for this |
| Frosted glass | `NSVisualEffectView` with `.hudWindow` material |
| Global hotkey | `HotKey` SPM package (wraps Carbon `RegisterEventHotKey`) |
| Bar positioning above dock | `NSScreen.main.visibleFrame.origin.y + padding` |
| Live transcription | `SFSpeechRecognizer` streams partial results natively |
| Text insertion | Sandboxed: AX API direct insertion. Non-sandboxed: pasteboard + CGEvent Cmd+V |
| Clipboard preservation | Restore original pasteboard contents after 200ms delay |

## Dependencies (SPM)

- **`HotKey`** (github.com/soffes/HotKey) for the global hotkey. Only external dependency for MVP.
- Everything else uses system frameworks: AVFoundation, Speech, AppKit, CoreGraphics.

## App Store Distribution

- **Code Signing:**
  - **App Store:** Standard Apple Developer certificate (via Xcode automatic signing)
  - **Direct distribution:** Developer ID Application certificate
- **Distribution Paths:**
  - **App Store (sandboxed):** Cannot use `CGEvent.post()`. Text insertion must use the Accessibility API (`AXUIElementSetAttributeValue`) instead. Requires sandbox entitlements below.
  - **Developer ID (non-sandboxed):** `CGEvent.post()` works, but requires direct distribution (not App Store). Simpler implementation but no App Store presence.
- **Sandbox Entitlements (App Store path):**
  - `com.apple.security.app-sandbox` (required for App Store)
  - `com.apple.security.device.microphone` (microphone access)
  - `com.apple.security.device.audio-input` (speech recognition)
  - `com.apple.security.network.client` (API calls)
  - `com.apple.security.accessibility` (Accessibility API for text insertion)
- **Notarization:** Required via `xcrun notarytool submit` with Apple Developer account
- **Hardened Runtime:** Required for notarization
- **Privacy Manifest:** Required for microphone/speech usage descriptions
- **App Store Connect:** Prepare screenshots, descriptions, age rating, privacy policy

## Permissions Required

- **Microphone**: system prompt on first AVAudioEngine use.
- **Speech Recognition**: system prompt on first SFSpeechRecognizer use.
- **Accessibility**: manual grant in System Settings (for CGEvent posting).

## Data Privacy

- Audio files stored in `NSTemporaryDirectory()` only
- Deleted immediately after successful transcription
- Failed recordings also deleted immediately (no persistence)
- No audio data retained beyond the current session
- API keys stored in Keychain only (never in UserDefaults or plaintext)
- Transcription text never sent to third parties beyond configured LLM provider

## Error Handling Strategy

Two-tier approach: user-visible errors in bar + automatic retries

**Automatic Retry Logic:**
- API failures: 1 retry after 1s delay
- Network errors: 2 retries with exponential backoff (1s, 3s)
- Transcription failures: no retry (show raw transcription option)
- Mic permission denied: no automatic retry (user must grant in System Settings)

**User-Visible Error States:**
- `[Error: Mic Denied]` - bar shows "Microphone access denied. Open System Settings to enable."
- `[Error: API Failed]` - bar shows "AI processing failed. Retrying... (1/2)"
- `[Error: Network Offline]` - bar shows "Offline. Queued for retry when connection restored."
- `[Error: Transcription Failed]` - bar shows "Transcription failed. Press Enter to use raw transcription, Esc to cancel."
- `[Error: API Quota Exceeded]` - bar shows "API quota exceeded. Press Enter to use raw transcription."

**Recovery Paths:**
- All errors can be dismissed with Esc to return to Idle
- Transcription errors offer raw transcription as fallback
- Network errors are queued and automatically retried when connection restored

## Testing Strategy

**Unit Tests:**
- `AudioRecorderTests`: test buffer capture, WAV file generation, cleanup
- `TextProcessorTests`: test prompt templates, API response parsing, error handling
- `TextInserterTests`: test clipboard save/restore, text insertion strategies
- `AppStateTests`: test state machine transitions, error state handling

**Integration Tests:**
- Test the full state machine flow: Idle, Listening, Transcribing, Processing, Reviewing.
- Test error state transitions and recovery
- Test audio file cleanup in all scenarios (success, failure, cancel)

**E2E Tests (XCUITest):**
- Test the full flow: hotkey, bar appears, speak, transcription, AI cleanup, paste.
- Test Esc cancel at each state
- Test Enter confirm at reviewing state
- Test error scenarios (mic denied, network offline)

**Mocking Strategy:**
- Mock AVAudioEngine for audio tests (no real mic required)
- Mock LLM API responses for offline testing
- Mock clipboard for TextInserter tests

## Offline Mode

- **Apple Speech:** Works offline (on-device recognition with `.requiresOnDeviceRecognition = true`)
- **AI Processing:** Requires network - show "Processing requires internet" in bar if offline
- **Queueing:** Failed API calls due to network errors are queued for automatic retry when connection restored
- **Graceful Degradation:** User can proceed with raw transcription if AI processing unavailable
- **Network Monitoring:** Use `NWPathMonitor` to detect connectivity changes and trigger queued retries

## Performance Considerations

- **Memory Usage:**
  - AVAudioEngine: ~10-20MB during recording
  - Transcription buffer: limit to 60 seconds to prevent unbounded memory growth. At 60s, auto-stop recording and proceed to Processing with accumulated transcription. Show countdown in bar at 10s remaining. If transcription is empty at 60s, transition to Error state.
  - Overlay panel: ~5MB when visible, ~1MB when hidden
- **CPU Usage:**
  - Idle: <1% CPU
  - Recording: ~2-3% CPU (audio capture)
  - Transcribing: ~5-10% CPU (on-device speech recognition)
  - Processing: <1% CPU (API call is network-bound)
- **Power Impact:** Minimal when idle, moderate during recording/transcription
- **Threading:**
  - Main thread: UI updates only (never block)
  - Background queue: audio capture, transcription streaming
  - Background queue: API calls (URLSession)
- **Startup Time:** <1 second to launch and register hotkey

## Verification

1. Build and run from Xcode
2. Verify menu bar icon appears, no dock icon
3. Press the hotkey from any app. The bar appears above the dock without stealing focus.
4. Speak. Live transcription is visible in the bar.
5. On stop the AI processes the text and the cleaned version is shown.
6. Press Enter. Text is pasted into the previously-focused app.
7. Press Esc. The bar dismisses; nothing is pasted.
8. Verify clipboard is preserved after insertion
9. Run unit test suite: `xcodebuild test -scheme Untype -destination 'platform=macOS'`
10. Run e2e test suite for critical user flows
11. Test VoiceOver: enable VoiceOver, verify bar content is announced
12. Test offline mode: disable network, verify graceful degradation
