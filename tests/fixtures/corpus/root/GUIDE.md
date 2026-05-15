# Untype Build & Run Guide

## Prerequisites

- macOS 14.0 (Sonoma) or later
- Swift 5.9+ toolchain (included with Xcode or Command Line Tools)
- Either:
  - **Xcode** (full IDE, optional) for the `.xcodeproj` workflow
  - **Command Line Tools** (`xcode-select --install`) for the Swift PM workflow

## Building

### With Swift Package Manager (recommended if no Xcode)

```bash
swift build
```

First build fetches the `HotKey` dependency (~20s). Subsequent builds are incremental (~1s).

### With Xcode

```bash
xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build
```

Or open `Untype.xcodeproj` in Xcode and press Cmd+R.

## Running

### From terminal

```bash
swift run
```

Or run the built binary directly:

```bash
.build/debug/Untype
```

### From Xcode

Open `Untype.xcodeproj`, select the Untype scheme, and run (Cmd+R).

## What you should see

1. A waveform menu bar icon appears (no Dock icon, since `LSUIElement = YES`).
2. Press **Cmd+Shift+Space** from any app, or click the menu bar icon and pick "Toggle Overlay".
3. A slim translucent bar appears above the dock, centered on screen.
4. Press Cmd+Shift+Space again to dismiss.

## Troubleshooting

### "Hotkey doesn't work"

The global hotkey requires Accessibility permission on some macOS versions. Go to:
**System Settings > Privacy & Security > Accessibility** and add Untype (or Terminal, if running from terminal).

### "No menu bar icon"

Make sure no other app is using the same menu bar space. Try clicking the waveform (ᯤ) icon area.

### Build fails with "requires Xcode"

If `xcodebuild` fails, use `swift build` instead. The project supports both build systems.

## Cleaning

```bash
swift package clean        # SPM
xcodebuild clean -project Untype.xcodeproj -scheme Untype  # Xcode
```

## Project structure

```
Untype/
  App/
    UntypeApp.swift          — @main entry point
    AppDelegate.swift        — Menu bar icon, hotkey wiring
  Window/
    OverlayPanel.swift       — NSPanel (non-activating, frosted glass)
    OverlayController.swift  — Hosts SwiftUI view in panel
    BarView.swift            — SwiftUI bar with state-driven content
  Hotkey/
    HotkeyManager.swift      — Global Cmd+Shift+Space registration
  State/
    AppState.swift           — Observable state machine
  Audio/                     — (Phase 3 — not yet implemented)
  Transcription/             — (Phase 4)
  Processing/                — (Phase 5)
  Insertion/                 — (Phase 6)
  Settings/                  — (Phase 8)
  Resources/
    Info.plist               — LSUIElement, usage descriptions
    Untype.entitlements      — Sandbox entitlements
    Assets.xcassets/         — App icon (placeholder)
```
