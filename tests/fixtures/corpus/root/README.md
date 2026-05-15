# Untype

A voice-driven "speech-to-message" layer for macOS. Press a hotkey, speak, and Untype transcribes your speech in real time, cleans it up with AI, and pastes the result into whatever app you were using -- Slack, Telegram, email, anywhere.

## How it works

1. **Press hotkey** -- a slim frosted-glass bar appears above the dock
2. **Speak** -- live transcription streams into the bar
3. **AI cleanup** -- filler words removed, grammar fixed, meaning preserved
4. **Review** -- edited text shown in bar, Enter to confirm or Esc to cancel
5. **Paste** -- text inserted into the previously-focused app, bar dismisses

The overlay never steals focus from your active application.

## Tech stack

- **Swift** -- native macOS (AppKit + SwiftUI)
- **AVAudioEngine** -- microphone capture
- **SFSpeechRecognizer** -- on-device live transcription (free, works offline)
- **LLM API** -- provider-agnostic text cleanup (OpenAI, Anthropic, or local models)
- **NSPanel** -- non-activating floating overlay with frosted glass

Single external dependency: [HotKey](https://github.com/soffes/HotKey) via SPM.

## Requirements

- macOS 14+
- Xcode 15+
- Microphone and Accessibility permissions

## Building

```bash
xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build
open Build/Products/Debug/Untype.app
```

Or open `Untype.xcodeproj` in Xcode and run.

## Status

Pre-implementation. See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for the phased build plan.
