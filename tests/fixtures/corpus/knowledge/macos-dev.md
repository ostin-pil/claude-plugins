# macOS App Development Knowledge Base

Best practices and hard-won lessons for native macOS development with Swift, AppKit, SwiftUI, and Xcode.
Maintained through real development experience on the Untype project.

---

## Permissions & Entitlements

### App Bundle vs Bare Binary
- **macOS only shows permission prompts (Mic, Speech Recognition) for proper .app bundles**, bare binaries from `swift run` do NOT trigger permission dialogs
- `LSUIElement` from Info.plist is only loaded for .app bundles, set `NSApplication.shared.setActivationPolicy(.accessory)` in code as fallback
- Each binary/bundle path needs its own Accessibility entry in System Settings
- After switching between app bundle and bare binary, re-grant Accessibility for the new path

### Permission States
- `AVCaptureDevice.authorizationStatus` and `SFSpeechRecognizer.authorizationStatus` return `.notDetermined` before first prompt, this is NOT "denied"
- Only `.denied` and `.restricted` should be treated as missing/blocking
- `.notDetermined` means "not yet prompted", the system will prompt on first use
- Accessibility (`AXIsProcessTrusted()`) has no prompt, must be added manually in System Settings

### Entitlements & Sandbox
- **Mac App Store sandbox breaks `CGEvent.post()` and Accessibility APIs**, Developer ID distribution is the only option for apps that need these
- Entitlements file and Info.plist must stay in sync
- `com.apple.security.device.audio-input` for microphone
- `com.apple.security.personal-information.speech-recognition` for speech

---

## AppKit

### NSPanel (Non-Activating Overlay)
- Use `.nonactivatingPanel` style mask, this is non-negotiable for overlays that shouldn't steal focus
- Set `panel.level = .floating` for always-on-top
- **Never call `makeKeyAndOrderFront`**, use `orderFront(nil)` to avoid stealing focus from target app
- `canBecomeKey` should return `false` for overlay panels, use global `NSEvent` monitors for keyboard input instead
- Position relative to `screen.visibleFrame` (accounts for dock/menu bar), not `screen.frame`
- `NSVisualEffectView` with `.hudWindow` material for frosted glass effect

### Menu Bar Apps
- Set `LSUIElement = YES` in Info.plist to hide from Dock
- Code fallback: `NSApplication.shared.setActivationPolicy(.accessory)` in `applicationDidFinishLaunching`
- Two menu bar icons = `setActivationPolicy(.accessory)` missing or Info.plist not loaded

### Event Monitoring
- Global keyboard shortcuts: use `NSEvent.addGlobalMonitorForEvents` (works when app is not active)
- Local event monitoring: `NSEvent.addLocalMonitorForEvents` (works when app is active)
- For overlay panels that can't become key, combine both global and local monitors
- Key codes: Enter = 36, Esc = 53

---

## Swift Concurrency & MainActor

### MainActor Isolation
- **All UI state mutations must happen on MainActor**, any `@Observable` property accessed from UI must be set on main thread
- `Task { @MainActor in ... }` for async work that ends by updating UI
- Timer callbacks dispatched on main run loop: `RunLoop.main.add(timer, forMode: .common)`
- Missing `@MainActor` in Task closures accessing shared state causes data races, compiler may not always warn

### Observation Framework
- `withObservationTracking` + `Task {}` introduces an async hop, the observation callback fires first, then the Task body runs later
- For immediate reactions, use `withCheckedContinuation` pattern instead, ensures the handler runs as the next MainActor work item
- Prefer `@Observable` (macOS 14+) over `ObservableObject`/`@Published`
- Never use Combine, use async/await and @Observable

---

## Audio & Speech

### AVAudioEngine
- Tap format for speech recognition: **16kHz mono Float32**
- Audio buffer callbacks fire ~43x/sec, throttle UI updates to ~20fps max to avoid SwiftUI re-render pressure
- Always stop the audio engine in error/cleanup paths, if `speechService.startRecognition()` throws after `audioRecorder.startRecording()` succeeds, stop the recorder in the catch block
- Check `AVCaptureDevice.authorizationStatus` before starting capture

### SFSpeechRecognizer
- Use on-device recognition: `.requiresOnDeviceRecognition = true`
- **Call `recognitionTask.finish()` on stop, not `.cancel()`**, `.cancel()` discards final results
- Handle `SFSpeechRecognizerDelegate` for availability changes (e.g., Siri disabled, language unavailable)
- Apple SpeechAnalyzer (macOS 26) may eventually replace SFSpeechRecognizer

---

## Text Insertion

### CGEvent Approach
- Save clipboard to write text to pasteboard to simulate Cmd+V via `CGEvent.post()` to wait to restore clipboard
- Requires Accessibility permission at runtime
- Works everywhere except VM guests (industry standard limitation)
- **Use 150ms delay** between paste and clipboard restore (100ms can be too fast for some apps)
- Use full clipboard snapshot (all types, not just `.string`) to preserve rich content
- Add transient type markers for clipboard managers to ignore the temporary paste

---

## Build & Distribution

### SPM vs Xcode
- SPM (`swift build`) is fastest for compile-check cycles
- SPM-first development causes Xcode pbxproj to fall out of date, must manually add new Swift files to the project
- For testing with permissions: build with SPM, copy binary into .app bundle
- `swift build && cp .build/debug/Untype Build/Untype.app/Contents/MacOS/Untype`

### Xcode Project Maintenance
- When adding files via SPM, the Xcode `.pbxproj` doesn't auto-update, new files must be added to Xcode project manually
- Build phases, file references, and group structure all need updating
- `xcodebuild` will fail silently if source files are missing from the project

### Developer ID Distribution
- Code signing with Developer ID (not Mac App Store)
- Notarization required for Gatekeeper
- No sandbox = full access to CGEvent, Accessibility APIs
- Signing identity, provisioning profile, and hardened runtime all needed

---

## Debugging

### Console Logging
- `NSLog("...")` appears in Console.app, filter by process name
- `log show --predicate 'processImagePath CONTAINS "Untype"' --last 1m`

### File-Based Logging
- Write to `/tmp/untype_debug.log` for quick debugging
- `FileHandle(forWritingAtPath:)` + `seekToEndOfFile()` for append
- Remove before committing

### Common Issues Checklist
| Symptom | Likely Cause |
|---|---|
| Hotkey not working | Accessibility permission not granted for this binary/bundle |
| "Transcription failed" immediately | Speech Recognition not authorized |
| Two menu bar icons | `setActivationPolicy(.accessory)` missing |
| High CPU/RAM | Audio level update frequency too high, observation loops |
| Permission prompt never appears | Running as bare binary, not .app bundle |
| UI not updating | State mutation not on MainActor |
| Observation handler delayed | Using Task{} in withObservationTracking instead of continuation |
| Final transcription missing | Called .cancel() instead of .finish() on recognition task |

---

## SwiftUI in macOS

- Use `@Observable` (macOS 14+), not `ObservableObject`/`@Published`
- No AppKit imports in SwiftUI views, communicate via state only
- `ViewBuilder` composition over large body properties
- SwiftUI hosted in AppKit via `NSHostingController` / `NSHostingView`

---

*Last updated: 2026-04-11*
*To add entries: describe the issue/lesson and it will be added to the appropriate section*
