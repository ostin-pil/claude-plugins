# Text Insertion Compatibility Research

**Date:** 2026-04-10
**Status:** Research complete
**Relevance:** Untype text insertion pipeline (`Untype/Insertion/TextInserter.swift`)

## Current Implementation

Untype uses a clipboard-swap approach:

1. Save current pasteboard string (`NSPasteboard.general.string(forType: .string)`)
2. Write transcribed text to pasteboard
3. Post `CGEvent` for Cmd+V (keyDown + keyUp at `.cghidEventTap`)
4. Wait 100ms
5. Restore previous pasteboard string

This requires Accessibility permission (Cmd+V via CGEvent needs it).

---

## 1. CGEvent Cmd+V Compatibility Matrix

### Native macOS Apps

| App | Works? | Notes |
|-----|--------|-------|
| TextEdit | Yes | Full support, no issues |
| Notes | Yes | Full support |
| Mail | Yes | Works in compose fields |
| Messages | Yes | Works reliably |
| Finder (rename) | Yes | Works in rename fields |
| Safari (address bar) | Yes | Works in URL bar and web fields |
| System Settings | Yes | Works in text fields |
| Spotlight | Yes | Works |

**Verdict:** Native apps are universally compatible with CGEvent Cmd+V.

### Electron Apps

| App | Works? | Notes |
|-----|--------|-------|
| Slack | Yes | Electron apps handle Cmd+V at the Chromium level |
| Discord | Yes | Same as Slack |
| VS Code | Yes* | Works, but Electron >= 32.3.0 had a paste regression on some platforms. macOS generally fine |
| Notion | Yes | Standard paste works |
| Obsidian | Yes | Standard paste works |

**Verdict:** Electron apps work because Chromium handles Cmd+V natively. Historical issues existed in early Electron versions where apps shipped without an Edit menu (needed for macOS to wire Cmd+V to the clipboard), but modern Electron apps handle this correctly.

*Known risk:* Electron version upgrades can introduce regressions (e.g., VS Code issue #238609 with Electron 32.3.0).

### Web Browsers (in-page text fields)

| App | Works? | Notes |
|-----|--------|-------|
| Safari | Yes | Standard paste in `<input>`, `<textarea>`, `contentEditable` |
| Chrome | Yes | Same as Safari |
| Firefox | Yes | Same |
| Arc | Yes | Chromium-based, same behavior |

**Verdict:** Browsers handle Cmd+V at the native level before dispatching to web content. No issues.

*Edge case:* Some web apps (Google Docs, Figma) intercept paste events and may reformat or filter content. This is a content issue, not a delivery issue -- the text still arrives.

### Terminal Emulators

| App | Works? | Notes |
|-----|--------|-------|
| Terminal.app | Yes | Cmd+V pastes into shell. Bracketed paste mode wraps with `\e[200~`/`\e[201~` |
| iTerm2 | Yes | Supports bracketed paste. Configurable paste behavior in Profiles > Terminal |
| Warp | Yes | Reliable Cmd+V support including images |
| Kitty | Yes* | Works but has a known issue with unbracketed pastes > 1024 chars dropping/repeating characters |
| Ghostty | Yes* | Cmd+V works for text. Image paste breaks after 2 pastes (bug #11444). Search box Cmd+V doesn't work |
| Alacritty | Yes | Standard support |

**Verdict:** Terminal emulators all support Cmd+V for text. The main concern is **bracketed paste mode** -- terminals wrap pasted content in escape sequences, which is correct behavior but means the pasted text includes control characters that the shell/program interprets. This is not a problem for Untype since we're inserting text the user wants typed.

*Kitty warning:* For very long transcriptions (> 1024 chars), Kitty may drop characters in unbracketed mode.

### Remote Desktop / VM Apps

| App | Works? | Notes |
|-----|--------|-------|
| Parallels | Partial | Cmd+V is intercepted by the host macOS, not forwarded to guest. User must configure key mapping |
| VMware Fusion | Partial | Same -- Cmd+V goes to host unless remapped. VMware Tools clipboard sync is separate |
| Microsoft RDP | No | Cmd+V is a host shortcut. RDP has its own clipboard channel |
| VNC viewers | No | Cmd+V goes to host. VNC clipboard sync is a separate protocol |

**Verdict:** CGEvent Cmd+V **does not reach the guest OS** in VM/remote desktop apps. The paste goes to the VM app's own text fields (if any), not to the guest. This is an inherent limitation -- clipboard sync between host and guest is a separate mechanism. **Not a fixable issue for Untype** -- users will need to rely on the VM's clipboard sharing feature.

### Java/JetBrains Apps

| App | Works? | Notes |
|-----|--------|-------|
| IntelliJ IDEA | Yes | JetBrains IDEs handle Cmd+V via their own keymap system |
| Android Studio | Yes | Same as IntelliJ |
| Eclipse | Yes | Java AWT handles Cmd+V |

**Verdict:** Java apps on macOS handle Cmd+V through AWT/Swing event dispatch, which correctly receives CGEvent-posted keyboard events. No issues observed.

### Qt Apps

| App | Works? | Notes |
|-----|--------|-------|
| Qt-based apps | Yes | Qt's event loop processes CGEvent keyboard events correctly |

**Verdict:** Qt apps work fine with CGEvent Cmd+V.

### Adobe Apps

| App | Works? | Notes |
|-----|--------|-------|
| Photoshop | Yes | Works in text tool, dialogs |
| Illustrator | Yes* | Works generally. Known issue: Cmd+V doesn't work in Save As dialog filename field |
| Premiere Pro | Yes | Timeline paste and text fields |

**Verdict:** Adobe apps generally work. Minor edge cases in specific dialog fields.

### Microsoft Office

| App | Works? | Notes |
|-----|--------|-------|
| Word | Yes | Full support |
| Excel | Yes | Pastes into active cell/formula bar |
| PowerPoint | Yes | Pastes into text boxes and notes |

**Verdict:** Office apps work reliably with CGEvent Cmd+V.

---

## 2. AXUIElement Alternative Approach

### How It Works

Instead of clipboard + paste, directly set text on the focused UI element via the Accessibility API:

```swift
import ApplicationServices

enum AXTextInserter {
    /// Insert text at the cursor position in the focused element using Accessibility API.
    /// Returns true if the insertion succeeded.
    static func insert(_ text: String) -> Bool {
        let systemWide = AXUIElementCreateSystemWide()
        
        var focusedApp: AnyObject?
        guard AXUIElementCopyAttributeValue(
            systemWide,
            kAXFocusedApplicationAttribute as CFString,
            &focusedApp
        ) == .success else { return false }
        
        var focusedElement: AnyObject?
        guard AXUIElementCopyAttributeValue(
            focusedApp as! AXUIElement,
            kAXFocusedUIElementAttribute as CFString,
            &focusedElement
        ) == .success else { return false }
        
        let element = focusedElement as! AXUIElement
        
        // Set kAXSelectedTextAttribute to insert at cursor position.
        // This replaces the current selection (if any) with the new text,
        // or inserts at cursor if nothing is selected.
        let result = AXUIElementSetAttributeValue(
            element,
            kAXSelectedTextAttribute as CFString,
            text as CFTypeRef
        )
        
        return result == .success
    }
}
```

### Key Details

- **`kAXSelectedTextAttribute`**: Setting this replaces the current selection with the provided text. If nothing is selected, it inserts at the cursor position. This is the correct attribute for text insertion.
- **`kAXValueAttribute`**: Setting this replaces the **entire** field content. Not suitable for insertion -- only for wholesale replacement.
- **No clipboard involvement**: Text goes directly into the field. No save/restore needed.
- **No timing issues**: Synchronous operation, no delay needed.

### Compatibility by App Category

| App Category | AX Insert Works? | Notes |
|--------------|-------------------|-------|
| Native macOS (TextEdit, Notes, etc.) | Yes | Full support via NSTextView/NSTextField |
| Electron (Slack, VS Code, Discord) | **No** | Returns `.success` but text does not appear. Chromium's accessibility implementation is read-only for text attributes |
| Web browsers (page content) | **No** | Browser accessibility exposes web content as AX tree but `kAXSelectedTextAttribute` is not writable for web text fields |
| Terminal emulators | **No** | Terminal views don't expose editable AX text attributes |
| JetBrains / Java | **Partial** | Some fields work, editor views may not |
| Adobe apps | **No** | Custom rendering, no standard AX text support |
| Microsoft Office | **Partial** | Some fields work via AX, others use custom views |

**Verdict:** AXUIElement text insertion is reliable only for **native macOS text fields** (NSTextField, NSTextView, and SwiftUI TextField). It silently fails in Electron, browsers, terminals, and many third-party apps. The silent failure (returns `.success` but doesn't insert) makes it unreliable as a primary method.

### Sandboxing / Mac App Store

AXUIElement requires:
1. App must **not** be sandboxed (App Sandbox entitlement must be disabled)
2. User must grant Accessibility permission in System Settings > Privacy & Security > Accessibility
3. App must be code-signed

**Mac App Store impact:** Sandboxed apps **cannot** use AXUIElement to control other apps. This rules out AX insertion for a Mac App Store build. The App Store path would require clipboard + Cmd+V exclusively.

---

## 3. Other Insertion Methods

### 3a. CGEventKeyboardSetUnicodeString

Types text character-by-character by embedding Unicode characters in keyboard events.

```swift
enum KeystrokeInserter {
    /// Type text character-by-character using CGEvent keyboard events.
    /// Each character is sent as a keyDown + keyUp pair.
    static func insert(_ text: String) {
        for character in text {
            let unichars = Array(String(character).utf16)
            
            guard let keyDown = CGEvent(keyboardEventSource: nil,
                                         virtualKey: 0,
                                         keyDown: true) else { continue }
            keyDown.keyboardSetUnicodeString(
                stringLength: unichars.count,
                unicodeString: unichars
            )
            
            guard let keyUp = CGEvent(keyboardEventSource: nil,
                                       virtualKey: 0,
                                       keyDown: false) else { continue }
            keyUp.keyboardSetUnicodeString(
                stringLength: unichars.count,
                unicodeString: unichars
            )
            
            keyDown.post(tap: .cghidEventTap)
            keyUp.post(tap: .cghidEventTap)
        }
    }
}
```

**Pros:**
- No clipboard involvement at all
- Works in virtually every app that accepts keyboard input
- Works in terminal emulators (characters arrive as keyboard events, not paste)
- No clipboard manager conflicts

**Cons:**
- **Very slow** for long text -- each character requires a keyDown + keyUp event pair
- Typing 200 characters takes noticeable time (visible "typing" effect)
- Can trigger auto-complete, spell-check, and other per-keystroke behaviors
- May trigger keyboard shortcuts if text contains modifier-equivalent characters
- Some apps rate-limit keyboard events
- Kitty has a known bug where > 1024 characters can drop or repeat

**Verdict:** Useful as a **fallback for terminal emulators** or apps where Cmd+V fails, but too slow for primary use with voice transcription (typical output is 20-200 words).

### 3b. InputMethodKit (IME Simulation)

Register as an input method and use `IMKTextInput.insertText(_:replacementRange:)`.

```swift
// Conceptual -- requires full input method bundle structure
// In an IMKInputController subclass:
override func inputText(_ string: String!, client sender: Any!) -> Bool {
    guard let client = sender as? IMKTextInput else { return false }
    client.insertText(
        string,
        replacementRange: NSRange(location: NSNotFound, length: 0)
    )
    return true
}
```

**Pros:**
- This is how macOS Dictation works internally
- Inserts at cursor without clipboard
- Works across all apps that accept text input
- No accessibility permission needed (input methods have their own permission model)

**Cons:**
- Requires registering as an **input method** (separate bundle, installed in `/Library/Input Methods/` or `~/Library/Input Methods/`)
- User must explicitly select/enable the input method
- Complex architecture -- input methods run as XPC services
- Cannot be part of a normal `.app` bundle without significant restructuring
- Apple's private APIs for Dictation bypass these limitations, but they are not available to third parties
- InputMethodKit has limited documentation and known bugs

**Verdict:** Not practical for Untype. The architectural overhead is enormous and the user experience (selecting an input method) is poor. This is the "correct" way to insert text system-wide but the engineering cost is not justified.

### 3c. AppleScript `keystroke` Command

```swift
import Foundation

enum AppleScriptInserter {
    static func insert(_ text: String) {
        let escaped = text
            .replacingOccurrences(of: "\\", with: "\\\\")
            .replacingOccurrences(of: "\"", with: "\\\"")
        let script = """
        tell application "System Events"
            keystroke "\(escaped)"
        end tell
        """
        var error: NSDictionary?
        NSAppleScript(source: script)?.executeAndReturnError(&error)
    }
}
```

**Pros:**
- Simple to implement
- Works across most apps
- No clipboard involvement

**Cons:**
- Same speed problem as CGEventKeyboardSetUnicodeString (character-by-character)
- Requires Accessibility permission (System Events needs it)
- AppleScript execution overhead
- Special characters and Unicode can cause issues
- Some characters trigger shortcuts

**Verdict:** No advantage over CGEvent approaches. Slower due to AppleScript overhead.

### 3d. AXTextMarker

AXTextMarker is used for **reading** text positions in complex text containers (like web views). It is not designed for text insertion and has no write API. Not applicable.

---

## 4. Clipboard Restoration Edge Cases

### 4a. Rich Text (RTF, HTML)

**Problem:** The current implementation only saves/restores `.string` type. If the clipboard contains rich text (RTF, HTML, attributed string), images, or files, those are **lost** on restore.

A clipboard entry can have multiple representations simultaneously:
- `public.utf8-plain-text` (plain text)
- `public.rtf` (RTF)
- `public.html` (HTML)
- `com.apple.webarchive` (web archive)
- Multiple image types (TIFF, PNG)
- File URLs

**Proper save/restore must preserve all items and all types:**

```swift
import AppKit

struct PasteboardSnapshot {
    struct Item {
        var typesAndData: [(NSPasteboard.PasteboardType, Data)]
    }
    let items: [Item]
    let changeCount: Int
    
    /// Capture all items and all types from the pasteboard.
    static func capture(from pasteboard: NSPasteboard = .general) -> PasteboardSnapshot {
        var items: [Item] = []
        for pbItem in pasteboard.pasteboardItems ?? [] {
            var typesAndData: [(NSPasteboard.PasteboardType, Data)] = []
            for type in pbItem.types {
                if let data = pbItem.data(forType: type) {
                    typesAndData.append((type, data))
                }
            }
            items.append(Item(typesAndData: typesAndData))
        }
        return PasteboardSnapshot(items: items, changeCount: pasteboard.changeCount)
    }
    
    /// Restore all items and types to the pasteboard.
    func restore(to pasteboard: NSPasteboard = .general) {
        // Only restore if no other app has changed the pasteboard since capture
        guard pasteboard.changeCount != self.changeCount else { return }
        
        pasteboard.clearContents()
        for item in items {
            let pbItem = NSPasteboardItem()
            for (type, data) in item.typesAndData {
                pbItem.setData(data, forType: type)
            }
            pasteboard.writeObjects([pbItem])
        }
    }
}
```

### 4b. Images on Clipboard

Images on the clipboard typically have multiple representations (TIFF, PNG, PDF). The snapshot approach above handles this correctly by saving raw data for each type. The current `.string`-only approach **silently destroys** image clipboard contents.

### 4c. Multiple Pasteboard Items

NSPasteboard can hold multiple items (e.g., multiple files dragged). The `pasteboardItems` array captures all of them. The snapshot approach handles this.

### 4d. Clipboard Managers (Paste, Maccy, Alfred, etc.)

Clipboard managers monitor `NSPasteboard.general` for changes via polling the `changeCount` property. When Untype writes text to the pasteboard and then restores, clipboard managers see **two** clipboard changes:

1. The transcribed text being written (changeCount increments)
2. The restoration of previous content (changeCount increments again)

Both entries end up in clipboard history, which is undesirable.

**Solution: Use `org.nspasteboard.TransientType`**

Mark the pasteboard entry as transient so well-behaved clipboard managers skip it:

```swift
pasteboard.clearContents()
pasteboard.setString(text, forType: .string)
// Signal to clipboard managers: this is temporary, don't record it
pasteboard.setData(Data(), forType: NSPasteboard.PasteboardType("org.nspasteboard.TransientType"))
pasteboard.setData(Data(), forType: NSPasteboard.PasteboardType("org.nspasteboard.AutoGeneratedType"))
```

**Supported by:** Maccy, Alfred, Paste, Clipy, Raycast clipboard history, and most modern clipboard managers.

### 4e. Timing: Is 100ms Enough?

**For most apps:** Yes. 100ms is sufficient for native macOS apps, Electron apps, browsers, and Office apps.

**Apps that may need more time:**
- **Heavy Electron apps under load** (Slack with many workspaces): May need 150-200ms
- **Adobe apps** (Photoshop with large documents open): May need 200-300ms
- **Remote desktop apps**: Clipboard sync can take 500ms+
- **VMs** (Parallels/VMware): Clipboard sharing can take 1-2 seconds

**Recommendation:** Use 150ms as default. Consider adaptive timing:

```swift
// Post paste event
let pasted = simulatePaste()

// Wait for paste to be processed, then restore
try? await Task.sleep(for: .milliseconds(150))

// Check if changeCount changed (indicates the app read the pasteboard)
// If not, wait longer
if pasteboard.changeCount == postPasteChangeCount {
    try? await Task.sleep(for: .milliseconds(200))  // extra wait
}
```

However, `changeCount` doesn't tell us if the target app read the pasteboard -- it only increments on writes. A simpler approach is a fixed delay of 150ms, which covers ~99% of cases.

---

## 5. How Competitors Handle Insertion

### Superwhisper

- **Primary method:** Clipboard + Cmd+V (same as Untype's current approach)
- **Clipboard restoration:** Saves and restores clipboard content
- **Processing:** Local-first (Whisper model runs on-device), text appears wherever cursor is
- **Permissions:** Requires Accessibility permission
- **Activation:** Menu bar app with configurable hotkey (default: Option+Space)

### Wispr Flow

- **Primary method:** Clipboard + Cmd+V
- **Key difference:** Cloud-based processing (voice sent to server for transcription + LLM cleanup)
- **Insertion:** Same clipboard-swap technique
- **Permissions:** Requires Accessibility permission
- **Note:** Their "smart" insertion may use AXUIElement to read surrounding context before inserting

### macOS Dictation

- **Method:** Private InputMethodKit APIs
- **How:** Dictation registers as a system input method via private frameworks. It uses `TSMDocumentAccess` and private Text Input Source APIs to insert text directly at the cursor
- **Key advantage:** As a system component, it bypasses the limitations that third-party input methods face
- **Not replicable:** These are private APIs that would get an app rejected from the App Store and could break with any macOS update

### TextExpander

- **Primary method:** Accessibility API monitoring + clipboard + Cmd+V
- **How it detects triggers:** Monitors keystrokes via CGEventTap (Accessibility permission)
- **Insertion:** When a trigger abbreviation is typed, TextExpander:
  1. Sends Cmd+Z or delete keystrokes to remove the typed abbreviation
  2. Places expanded text on clipboard
  3. Simulates Cmd+V to paste
  4. Restores clipboard
- **AX fallback:** For apps with known Cmd+V issues, TextExpander can use `AXUIElementSetAttributeValue` with `kAXSelectedTextAttribute`
- **Relevant detail:** TextExpander release notes mention "improving Accessibility Protocol" handling and special-casing `AXScrollArea` for apps that don't fully implement accessibility

### Raycast (Snippets)

- **Trigger method:** Monitors keystrokes for snippet keywords
- **Insertion:** Clipboard + simulated paste (same pattern)
- **Clipboard history:** Raycast's own clipboard history is aware of transient pastes and excludes them

### FreeFlow (Open Source)

- **Method:** Clipboard + CGEvent Cmd+V (confirmed in source code)
- **Architecture:** Fn key activates recording via CGEventTap, transcription via Whisper, optional LLM cleanup, then paste
- **Fallback:** Some forks implement AXUIElement as primary with CGEvent paste as fallback

---

## 6. Recommended Strategy for Untype

### Primary Method: Enhanced Clipboard + Cmd+V

The clipboard + Cmd+V approach is the correct choice. It is what every major competitor uses because it has the broadest compatibility. Enhance the current implementation with:

1. **Full clipboard snapshot/restore** (not just `.string` -- preserve all types and items)
2. **Transient type marking** (`org.nspasteboard.TransientType` + `org.nspasteboard.AutoGeneratedType`)
3. **Increased delay** (150ms default instead of 100ms)

### Optional Fallback: AXUIElement for Native Apps

For cases where the user reports issues with clipboard restoration (e.g., they frequently copy images), offer an AX-based insertion mode that avoids touching the clipboard entirely. This only works for native macOS text fields but avoids all clipboard side effects.

### Detection Strategy

```
1. Try AXUIElement kAXSelectedTextAttribute (no clipboard involvement)
   - If it works -> done, no clipboard restoration needed
   - If it fails (returns error or silently fails) -> fall through

2. Clipboard + Cmd+V (primary path)
   - Full pasteboard snapshot
   - Write text + transient markers
   - Post CGEvent Cmd+V
   - Wait 150ms
   - Restore pasteboard snapshot
```

The dual approach can be **opt-in** via Settings rather than automatic, since detecting AX silent failures is unreliable (the API returns `.success` even when the text doesn't appear in Electron apps).

### What NOT to Pursue

- **InputMethodKit:** Too complex, poor UX, not worth the architectural cost
- **CGEventKeyboardSetUnicodeString as primary:** Too slow for transcription-length text
- **AppleScript keystroke:** No advantage over CGEvent, additional overhead
- **Private APIs:** Would block App Store distribution and break unpredictably

### Improved TextInserter Implementation

```swift
import AppKit

enum TextInserter {

    @discardableResult
    static func insert(_ text: String) async -> Bool {
        let pasteboard = NSPasteboard.general
        let snapshot = PasteboardSnapshot.capture(from: pasteboard)

        pasteboard.clearContents()
        let item = NSPasteboardItem()
        item.setString(text, forType: .string)
        // Mark as transient so clipboard managers ignore it
        item.setData(Data(), forType: NSPasteboard.PasteboardType("org.nspasteboard.TransientType"))
        item.setData(Data(), forType: NSPasteboard.PasteboardType("org.nspasteboard.AutoGeneratedType"))
        pasteboard.writeObjects([item])

        let pasted = simulatePaste()

        // Allow target app time to process the paste
        try? await Task.sleep(for: .milliseconds(150))

        // Restore full clipboard contents
        snapshot.restore(to: pasteboard)

        return pasted
    }

    private static func simulatePaste() -> Bool {
        guard let keyDown = CGEvent(
            keyboardEventSource: nil,
            virtualKey: 0x09, // 'v'
            keyDown: true
        ) else { return false }
        keyDown.flags = .maskCommand

        guard let keyUp = CGEvent(
            keyboardEventSource: nil,
            virtualKey: 0x09,
            keyDown: false
        ) else { return false }
        keyUp.flags = .maskCommand

        keyDown.post(tap: .cghidEventTap)
        keyUp.post(tap: .cghidEventTap)
        return true
    }
}

struct PasteboardSnapshot {
    struct Item {
        let typesAndData: [(NSPasteboard.PasteboardType, Data)]
    }
    let items: [Item]

    static func capture(from pasteboard: NSPasteboard) -> PasteboardSnapshot {
        var items: [Item] = []
        for pbItem in pasteboard.pasteboardItems ?? [] {
            var pairs: [(NSPasteboard.PasteboardType, Data)] = []
            for type in pbItem.types {
                if let data = pbItem.data(forType: type) {
                    pairs.append((type, data))
                }
            }
            items.append(Item(typesAndData: pairs))
        }
        return PasteboardSnapshot(items: items)
    }

    func restore(to pasteboard: NSPasteboard) {
        pasteboard.clearContents()
        for item in items {
            let pbItem = NSPasteboardItem()
            for (type, data) in item.typesAndData {
                pbItem.setData(data, forType: type)
            }
            pasteboard.writeObjects([pbItem])
        }
    }
}
```

---

## 7. Known Limitations (Unfixable)

| Limitation | Why |
|-----------|-----|
| VM/Remote Desktop guest apps | CGEvent goes to host, not guest. Clipboard sharing is a separate VM feature |
| Secure input fields (passwords) | macOS blocks CGEvent posting when secure input is active |
| Apps with disabled paste (DRM, exams) | App explicitly blocks Cmd+V; nothing can override this |
| Full-screen games | May not process CGEvent keyboard events |
| Clipboard manager pollution | Transient markers help but not all managers respect them |

---

## Sources

- [Electron Cmd+V issue #1902](https://github.com/electron/electron/issues/1902)
- [VS Code paste regression #238609](https://github.com/microsoft/vscode/issues/238609)
- [Ghostty Cmd+V paste issue #11444](https://github.com/ghostty-org/ghostty/issues/11444)
- [Kitty large paste issue #5869](https://github.com/kovidgoyal/kitty/issues/5869)
- [NSPasteboard.org -- Transient/Concealed types](http://nspasteboard.org/)
- [AXUIElement Apple Documentation](https://developer.apple.com/documentation/applicationservices/axuielement)
- [InputMethodKit Apple Documentation](https://developer.apple.com/documentation/inputmethodkit)
- [Swift/macOS: Insert Text Two Ways (Level Up Coding)](https://levelup.gitconnected.com/swift-macos-insert-text-to-other-active-applications-two-ways-9e2d712ae293)
- [CGEvent.keyboardSetUnicodeString Apple Docs](https://developer.apple.com/documentation/coregraphics/cgevent/keyboardsetunicodestring(stringlength:unicodestring:))
- [FreeFlow open source (zachlatta)](https://github.com/zachlatta/freeflow)
- [FreeFlow (build-trust)](https://github.com/build-trust/freeflow)
- [Maccy clipboard manager source](https://github.com/p0deje/Maccy/blob/master/Maccy/Clipboard.swift)
- [TextExpander Accessibility](https://textexpander.com/learn/accounts/security/turning-on-accessibility-access-in-textexpander-for-mac)
- [Raycast Snippets](https://manual.raycast.com/snippets)
- [Apple Developer Forums: Paste text into another app](https://developer.apple.com/forums/thread/45330)
- [BetterTouchTool paste delay discussion](https://community.folivora.ai/t/delay-in-copy-pasting/8338)
