# Context-Aware Text Cleanup

Research report for Untype -- adapting voice-to-text cleanup style based on the target application context.

**Date:** 2026-04-10
**Status:** Research complete, ready for design decisions

---

## 1. macOS APIs for Context Detection

### 1.1 Frontmost Application (No special permissions)

**API:** `NSWorkspace.shared.frontmostApplication`
**Returns:** `NSRunningApplication` with `.bundleIdentifier`, `.localizedName`, `.processIdentifier`
**Permission required:** None. Freely available to any app.
**Reliability:** Excellent. KVO-observable via `NSWorkspace.didActivateApplicationNotification`.

```swift
let app = NSWorkspace.shared.frontmostApplication
let bundleId = app?.bundleIdentifier  // e.g. "com.tinyspeck.slackmacgap"
let name = app?.localizedName         // e.g. "Slack"
```

This is the simplest and most reliable context signal. No permissions dialog, no privacy concerns.

### 1.2 Window Title (Requires Accessibility permission)

**API:** `AXUIElementCopyAttributeValue` with `kAXTitleAttribute` on the focused window
**Returns:** Window title string (e.g. "general - Company Workspace - Slack", "Inbox - user@gmail.com - Gmail - Google Chrome")
**Permission required:** Accessibility (System Settings > Privacy & Security > Accessibility)

```swift
let pid = app.processIdentifier
let axApp = AXUIElementCreateApplication(pid)
var windowValue: CFTypeRef?
AXUIElementCopyAttributeValue(axApp, kAXFocusedWindowAttribute as CFString, &windowValue)
var titleValue: CFTypeRef?
AXUIElementCopyAttributeValue(windowValue as! AXUIElement, kAXTitleAttribute as CFString, &titleValue)
let title = titleValue as? String  // "general - Company Workspace - Slack"
```

Window titles are highly informative -- they reveal channel names, email subjects, document names, file paths. This is both a feature (rich context) and a privacy concern (exposes sensitive data).

### 1.3 Focused Text Field Content (Requires Accessibility permission)

**API:** `AXUIElementCopyAttributeValue` with `kAXValueAttribute` and `kAXSelectedTextAttribute`
**Returns:** Full text content of the focused field, plus any selected text
**Permission required:** Accessibility

```swift
var focusedElement: CFTypeRef?
let systemWide = AXUIElementCreateSystemWide()
AXUIElementCopyAttributeValue(systemWide, kAXFocusedUIElementAttribute as CFString, &focusedElement)

var textValue: CFTypeRef?
AXUIElementCopyAttributeValue(focusedElement as! AXUIElement, kAXValueAttribute as CFString, &textValue)
let existingText = textValue as? String  // Everything already typed in the field
```

This is the most invasive context signal. It reads what the user has already typed, which could include passwords, private messages, or confidential content. Some apps (notably web apps in browsers) may not expose this reliably.

### 1.4 Browser URL Detection (Requires Accessibility permission)

For browser-based apps (Gmail, Slack web, GitHub, Notion), the bundle ID is just the browser itself (e.g. `com.google.Chrome`). To distinguish between web apps, you need the URL.

**Approach 1 -- Window title parsing:**
Most browsers include the page title in the window title. Gmail shows "Inbox - user@email.com - Gmail", Slack shows "channel - workspace - Slack". This is often sufficient without reading the URL bar.

**Approach 2 -- AXValue on the address bar:**
Navigate the accessibility tree to find the URL bar element and read its value. This works for Chrome and Safari but requires traversing the AX hierarchy, which varies between browsers and versions.

**Approach 3 -- AppleScript/JXA:**
```swift
// Safari
let script = NSAppleScript(source: "tell application \"Safari\" to get URL of front document")
// Chrome
let script = NSAppleScript(source: "tell application \"Google Chrome\" to get URL of active tab of front window")
```
This requires Automation permission (separate from Accessibility) and shows its own permission dialog per browser.

### 1.5 Document Type in Editors (Requires Accessibility permission)

For code editors, the window title typically includes the filename and extension:
- VS Code: "main.swift -- Untype -- Visual Studio Code"
- Xcode: "AppState.swift -- Untype"

Parsing the window title gives the file extension, which indicates whether the user is editing Swift, Python, Markdown, etc.

### 1.6 Permission Summary

| Signal | Permission Required | Privacy Impact | Richness |
|---|---|---|---|
| Bundle ID | None | None | Low-medium |
| App name | None | None | Low |
| Window title | Accessibility | Medium | High |
| Focused field text | Accessibility | High | Very high |
| Browser URL | Accessibility or Automation | Medium-high | High |
| Selected text | Accessibility | High | Medium |

**Untype already requires Accessibility permission** for CGEvent-based text insertion (Cmd+V simulation in `TextInserter`), so window title and focused element access come "for free" once the user has granted that permission.

---

## 2. Context-to-Behavior Mapping

### 2.1 Proposed Context Profiles

| Context | Bundle ID / Detection | Tone | Formatting | Special Rules |
|---|---|---|---|---|
| **Slack / Discord** | `com.tinyspeck.slackmacgap`, `com.hnc.Discord` | Casual | Short paragraphs, no greeting/sign-off | Allow emoji, contractions, lowercase OK |
| **Telegram / Messages** | `ru.keepcoder.Telegram`, `com.apple.MobileSMS` | Very casual | Single message, brief | Minimal punctuation, conversational |
| **Email (Mail.app)** | `com.apple.mail` | Semi-formal | Proper paragraphs, greeting/sign-off | Capitalize, full sentences |
| **Email (Outlook)** | `com.microsoft.Outlook` | Semi-formal | Same as Mail | Same as Mail |
| **Gmail (browser)** | Browser + title contains "Gmail" | Semi-formal | Same as Mail | Same as Mail |
| **Code editor (VS Code)** | `com.microsoft.VSCode` | Technical | Preserve technical terms | If window title suggests code file, format as comment |
| **Code editor (Xcode)** | `com.apple.dt.Xcode` | Technical | Same as VS Code | Detect file type from window title |
| **Terminal** | `com.apple.Terminal`, `com.googlecode.iterm2` | Passthrough | Minimal cleanup | Preserve exact words, no style changes |
| **Notes (Apple Notes)** | `com.apple.Notes` | Neutral | Structured, bullet-friendly | Add Markdown-style bullets if listing |
| **Notion (app)** | `notion.id` | Neutral | Structured | Markdown-aware formatting |
| **Notion (browser)** | Browser + title contains "Notion" | Neutral | Same | Same |
| **Google Docs (browser)** | Browser + title contains "Google Docs" | Neutral-formal | Proper paragraphs | Full sentences, structured |
| **Twitter/X (browser)** | Browser + title contains "X" or URL | Concise | Under 280 chars | Punchy, no formalities |
| **Linear / Jira** | `com.linear`, browser + title | Technical-neutral | Structured | Bug report / ticket style |
| **Default / Unknown** | Any unrecognized app | Neutral | Clean sentences | Standard cleanup, no strong style bias |

### 2.2 Window Title Refinements

Within a single app, window titles can distinguish sub-contexts:

| App | Window Title Pattern | Sub-Context |
|---|---|---|
| Slack | `#general - Workspace` | Public channel (slightly more formal) |
| Slack | `User Name - Workspace` | DM (more casual) |
| Slack | `thread` in title | Thread reply (concise) |
| Gmail | `Compose` or `New Message` | Composing (full email style) |
| Gmail | `Inbox` | Reading, not composing (maybe skip?) |
| VS Code | `*.swift` in title | Swift code (format as `//` comment) |
| VS Code | `*.py` in title | Python code (format as `#` comment) |
| VS Code | `*.md` in title | Markdown (prose, not code comment) |

### 2.3 LLM Prompt Template

The context profile translates into a system prompt modifier for the LLM processing step:

```
You are cleaning up voice-dictated text for insertion into {app_name}.
Context: {context_profile.description}
Tone: {context_profile.tone}
Formatting rules: {context_profile.rules}

The user said: "{raw_transcription}"

Output ONLY the cleaned text, ready to paste. No explanations.
```

For the local (non-LLM) processing path, context maps to simpler rule sets:
- Capitalization: always for email, optional for chat
- Punctuation: full for email/docs, minimal for chat
- Line breaks: preserve for docs/notes, collapse for chat
- Greetings/sign-offs: add for email if detected, never for chat

---

## 3. Implementation Approaches

### 3.1 Tier 1 -- Bundle ID Mapping (Recommended for MVP)

**Complexity:** Low
**Integration point:** `ProcessingCoordinator.startProcessing()`

A simple lookup table maps bundle identifiers to context profiles. No accessibility tree traversal needed beyond what Untype already does.

```swift
enum ContextProfile: String, CaseIterable {
    case chat       // Slack, Discord, Telegram, Messages
    case email      // Mail, Outlook
    case code       // VS Code, Xcode
    case notes      // Notes, Notion, Docs
    case terminal   // Terminal, iTerm
    case social     // Twitter/X in browser
    case general    // Default fallback
}

struct ContextDetector {
    static func detect(bundleId: String?) -> ContextProfile {
        guard let id = bundleId else { return .general }
        switch id {
        case "com.tinyspeck.slackmacgap", "com.hnc.Discord",
             "ru.keepcoder.Telegram", "com.apple.MobileSMS":
            return .chat
        case "com.apple.mail", "com.microsoft.Outlook":
            return .email
        case "com.microsoft.VSCode", "com.apple.dt.Xcode":
            return .code
        case "com.apple.Notes", "notion.id":
            return .notes
        case "com.apple.Terminal", "com.googlecode.iterm2":
            return .terminal
        default:
            return .general
        }
    }
}
```

**Pros:** Zero additional permissions, zero privacy risk, trivial to implement.
**Cons:** No browser-based app detection, no sub-context within apps.

### 3.2 Tier 2 -- Bundle ID + Window Title (Recommended for v1.1)

**Complexity:** Medium
**Additional requirements:** Accessibility permission (already required by Untype)

Adds window title parsing to handle browsers and sub-contexts. The window title is captured once when the hotkey is pressed (before Untype's overlay appears).

```swift
struct AppContext {
    let bundleId: String?
    let appName: String?
    let windowTitle: String?

    var profile: ContextProfile { /* bundle ID + title heuristics */ }
}
```

Window title patterns for browser detection:
- `"Gmail"` in title -> `.email`
- `"Slack"` in title -> `.chat`
- `"GitHub"` in title -> `.code` (or `.general` depending on page)
- `"Notion"` in title -> `.notes`
- `"Google Docs"` in title -> `.notes`

**Pros:** Catches browser-based apps, enables sub-context (channel vs DM, file type).
**Cons:** Window title formats change across app versions; needs maintenance.

### 3.3 Tier 3 -- Surrounding Text Context (Future)

**Complexity:** High
**Privacy impact:** Significant

Reads the existing text in the focused field to provide the LLM with conversational context. For example, if the user is replying to a Slack message, the LLM can see the message they're replying to and match the tone.

```swift
// Read surrounding text from focused element
var textValue: CFTypeRef?
AXUIElementCopyAttributeValue(focusedElement, kAXValueAttribute as CFString, &textValue)
let surroundingText = textValue as? String
```

**Pros:** Highest quality context, LLM can match tone precisely.
**Cons:** Major privacy concern, unreliable across apps (especially web), performance overhead. Many apps (especially Electron-based) expose limited or no AX text values.

### 3.4 Tier 4 -- Full LLM Context (Future, cloud-only)

Pass the full app context (bundle ID, window title, optionally surrounding text) as structured metadata in the LLM request. The LLM handles all tone/style decisions.

This is what Wispr Flow appears to do with their cloud processing.

**Requires:** Cloud LLM provider, careful prompt engineering, user trust.

---

## 4. Integration with Untype Architecture

### 4.1 Data Flow

```
Hotkey pressed
  -> Capture context (bundleId, windowTitle) from frontmost app
  -> Record audio, transcribe
  -> ProcessingCoordinator receives rawText + AppContext
  -> LLMRequest includes context metadata
  -> LLMProvider uses context to adjust prompt/rules
  -> Cleaned text inserted back into original app
```

### 4.2 Changes Required

**New file:** `Untype/Processing/ContextDetector.swift`
- `AppContext` struct (bundleId, appName, windowTitle, contextProfile)
- `ContextDetector` with static `captureCurrentContext()` method
- `ContextProfile` enum with tone/formatting properties

**Modified:** `Untype/Processing/LLMModels.swift`
- Add `context: AppContext?` field to `LLMRequest`

**Modified:** `Untype/Processing/ProcessingCoordinator.swift`
- Capture context before transitioning to `.processing`
- Pass context through to LLM request

**Modified:** `Untype/Processing/LocalProvider.swift`
- Use context profile to adjust rule-based cleanup

**Modified:** `Untype/State/AppState.swift`
- Optionally store captured context on AppState for display in overlay

### 4.3 Timing Consideration

Context must be captured at hotkey press time (before the overlay appears), because once Untype's overlay panel is shown, the frontmost app changes to Untype itself. The `RecordingCoordinator.handleHotkey()` method is the right capture point.

---

## 5. Privacy Analysis

### 5.1 Data Sensitivity by Signal

| Signal | Sensitivity | Example of Exposure |
|---|---|---|
| Bundle ID | Minimal | Reveals what apps user has installed |
| App name | Minimal | Same as above |
| Window title | Medium | Exposes document names, email subjects, Slack channels, URLs |
| Focused field text | High | Exposes message content, passwords (if not masked), private conversations |
| Browser URL | Medium-high | Exposes browsing history, account info |

### 5.2 What Wispr Flow Does (Benchmark)

Wispr Flow's approach provides a useful reference:

1. **Context Awareness is on by default** but can be toggled off in Settings > Data & Privacy
2. **Reads app name and limited text content** (e.g. email recipient names)
3. **Password fields are never read** -- they detect `kAXIsSecureTextFieldAttribute`
4. **Banking apps suppress context entirely** -- when a banking app is frontmost, context awareness is disabled
5. **Screen Capture permission** is requested on Mac for context-aware features (separate from Accessibility)
6. **Privacy Mode** option: when enabled, no audio, transcripts, or context data is stored

Source: [Wispr Flow Context Awareness docs](https://docs.wisprflow.ai/articles/4678293671-feature-context-awareness), [How Context Awareness Works](https://docs.wisprflow.ai/articles/5020906721-how-does-context-awareness-work), [Data Controls](https://wisprflow.ai/data-controls)

### 5.3 Recommended Privacy Posture for Untype

**Principle:** Collect the minimum context needed. Be transparent.

1. **Tier 1 (MVP):** Bundle ID only. Zero additional privacy exposure. No disclosure needed beyond "Untype detects which app you're typing in to adjust formatting."

2. **Tier 2 (v1.1):** Bundle ID + window title.
   - Show a clear Settings toggle: "Use window title for smarter formatting"
   - Default: ON (following Wispr Flow's precedent)
   - Never log or transmit window titles to cloud -- use locally for profile selection only
   - If sending to cloud LLM, send only the derived `ContextProfile` enum value, not the raw title

3. **Tier 3 (future):** Surrounding text.
   - Opt-in only, default OFF
   - Never read secure text fields (`kAXIsSecureTextFieldAttribute`)
   - Suppress in banking/financial apps
   - Clear disclosure: "Untype reads nearby text to match your writing style"
   - If cloud LLM: explicit user consent for sending text context

### 5.4 Per-App Opt-Out

Users should be able to exclude specific apps from context detection:

```
Settings > Context Awareness
  [x] Detect app for formatting (bundle ID)
  [x] Use window title for better detection
  [ ] Read surrounding text (advanced)

  Excluded apps:
    [x] 1Password
    [x] Keychain Access
    [+] Add app...
```

---

## 6. Competitor Analysis

### 6.1 Wispr Flow

**Context approach:** Reads active app name + limited text content via accessibility. Automatically adjusts tone (formal for Gmail, casual for Slack). Explicitly suppresses context for banking apps and password fields.

**Key insight:** They use Screen Capture permission on Mac in addition to Accessibility, suggesting they may read more than just AX attributes (possibly OCR or screen region analysis).

**Privacy stance:** Context Awareness on by default, toggleable. Privacy Mode disables all storage. HIPAA compliant.

Source: [Wispr Flow Context Awareness](https://docs.wisprflow.ai/articles/4678293671-feature-context-awareness), [Privacy](https://wisprflow.ai/privacy)

### 6.2 Superwhisper

**Context approach:** Custom "modes" that users define manually. Supports automatic mode switching based on app or website context. Users create modes with specific AI instructions (e.g., "code mode", "email mode").

**Key insight:** User-defined modes rather than automatic detection. More control, less magic. The auto-switching is opt-in and user-configured per mode.

**Privacy stance:** Supports fully local (offline) processing with Whisper models, which sidesteps cloud privacy concerns entirely.

Source: [Superwhisper](https://superwhisper.com/), [Superwhisper Changelog](https://superwhisper.com/changelog)

### 6.3 Grammarly

**Context approach:** As a browser extension and native app plugin, Grammarly has deep integration with each platform. It detects context through its extension's DOM access (in browsers) and native integrations. Uses ML-based tone detection on the text itself, not just the app.

**Key insight:** Grammarly's advantage is being embedded in the writing surface, not external. It can read the full document context because the user explicitly installed it in that context.

**Privacy stance:** Has been criticized for reading all typed text. Enterprise version offers more controls.

Source: [Grammarly AI](https://www.grammarly.com/ai), [Grammarly Tone](https://www.grammarly.com/tone)

### 6.4 Comparison Matrix

| Feature | Wispr Flow | Superwhisper | Grammarly | Untype (proposed) |
|---|---|---|---|---|
| App detection | Auto (accessibility) | Manual + auto-switch | Embedded per-app | Auto (bundle ID) |
| Tone adaptation | Automatic | User-defined modes | ML on text content | Automatic (profile map) |
| Sub-context (DM vs channel) | Limited | No | Yes (DOM access) | Via window title (Tier 2) |
| Surrounding text | Yes (limited) | No | Yes (full) | Opt-in future (Tier 3) |
| Privacy controls | Toggle + banking block | Local processing | Limited | Toggle + per-app exclude |
| Offline capable | No | Yes | No | Yes (local provider) |

---

## 7. Implementation Recommendation

### Phase 1 -- MVP (implement now)

**Bundle ID context detection with profile mapping.**

- Add `ContextDetector.swift` to `Untype/Processing/`
- Capture `NSWorkspace.shared.frontmostApplication?.bundleIdentifier` at hotkey press in `RecordingCoordinator`
- Map to `ContextProfile` enum (chat/email/code/notes/terminal/general)
- Pass profile to `LLMRequest` as new field
- Modify `LocalProvider` to use profile for rule-based cleanup adjustments
- Modify cloud LLM prompt to include context profile name and tone guidance
- No new permissions required
- Estimated effort: 1-2 sessions

### Phase 2 -- Window Title Enhancement (next iteration)

**Add window title parsing for browser detection and sub-context.**

- Read `kAXTitleAttribute` from focused window at hotkey press
- Parse title for browser-based app detection (Gmail, Slack web, Notion, etc.)
- Detect sub-context within apps (Slack DM vs channel, code file type)
- Add Settings toggle for window title usage
- Already covered by existing Accessibility permission
- Estimated effort: 1 session

### Phase 3 -- User-Defined Profiles (future)

**Allow users to create custom context profiles.**

- Settings UI for creating/editing profiles
- Per-app profile assignment (override auto-detection)
- Custom LLM prompt templates per profile
- Export/import profiles
- Follows Superwhisper's successful model of user control

### Phase 4 -- Surrounding Text Context (future, opt-in)

**Read focused field content for deeper context.**

- Opt-in only, clear privacy disclosure
- Secure text field detection and exclusion
- Banking/financial app blocklist
- Only use with cloud LLM (too complex for local rules)
- Consider: is this worth the privacy tradeoff vs. just better prompts?

---

## 8. Open Questions

1. **Should context detection be visible in the overlay?** Showing "Detected: Slack (casual)" gives users confidence but adds UI complexity. Wispr Flow does not show this.

2. **What about dictation for non-text contexts?** If the user triggers Untype in Finder or Preview, there's no text field. Should Untype warn, or just use general mode and copy to clipboard?

3. **How to handle app updates changing window title formats?** Regex patterns for title parsing will break. Consider a community-maintained mapping or fuzzy matching.

4. **Should Untype support Superwhisper-style user-defined modes alongside auto-detection?** This gives power users control while keeping the default experience automatic. The two systems (auto-detect + manual override) are complementary.

5. **Local vs. cloud context passing:** For the local provider, context adjusts simple rules (capitalization, punctuation). For cloud, the full context profile can be part of the prompt. Should the local provider even attempt tone adjustment, or just handle formatting?

---

## Sources

- [Wispr Flow Context Awareness](https://docs.wisprflow.ai/articles/4678293671-feature-context-awareness)
- [How Context Awareness Works (Wispr Flow)](https://docs.wisprflow.ai/articles/5020906721-how-does-context-awareness-work)
- [Wispr Flow Data Controls](https://wisprflow.ai/data-controls)
- [Wispr Flow Privacy](https://wisprflow.ai/privacy)
- [Wispr Flow Banking App Detection](https://docs.wisprflow.ai/articles/4909908692-banking-app-detection-support-in-wispr-flow)
- [Wispr Flow Review (Filip Konecny, March 2026)](https://filipkonecny.com/2026/03/25/wispr-flow-review/)
- [Superwhisper](https://superwhisper.com/)
- [Superwhisper Changelog](https://superwhisper.com/changelog)
- [Grammarly AI](https://www.grammarly.com/ai)
- [Grammarly Tone Detector](https://www.grammarly.com/tone)
- [Apple: NSWorkspace.frontmostApplication](https://developer.apple.com/documentation/appkit/nsworkspace/frontmostapplication)
- [Apple: Accessibility API](https://developer.apple.com/documentation/accessibility/accessibility-api)
- [Swift/macOS: Get Browser URL (Medium, Feb 2026)](https://medium.com/@itsuki.enjoy/swift-macos-get-browser-opened-tab-url-2-ways-e6722fb5998d)
- [AXSwift (GitHub)](https://github.com/tmandry/AXSwift)
- [Accessibility Permission on macOS (jano.dev)](https://jano.dev/apple/macos/swift/2025/01/08/Accessibility-Permission.html)
- [Accessing AXValue from any app (Mac Developers)](https://macdevelopers.wordpress.com/2014/01/31/accessing-text-value-from-any-system-wide-application-via-accessibility-api/)
