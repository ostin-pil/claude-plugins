# Code Health Audit, 2026-04-14

**Branch**: main
**Commit**: 4732251
**Focus**: broad sweep (first audit, pre-skill)

## Critical

- `Sources/App/AppDelegate.swift:9-15`, implicitly-unwrapped dependencies crash the app silently if any init fails. *Fix:* use proper optionals or `precondition` guards.
- `Sources/Transcription/AppleSpeechService.swift:26`, force-unwrap of fallback `SFSpeechRecognizer` crashes if both locale-current and en-US fail. *Fix:* throw an init error or bind with `guard let`.
- `Sources/Insertion/FocusedElementLocator.swift:31,55,60,81-82`, multiple `as!` casts on AX values that may be malformed. *Fix:* replace with `as?` and defensive guards.
- `Sources/Window/OverlayController.swift:14`, hosting view silently skipped if `panel.contentView` is nil; returns successfully with broken panel. *Fix:* `fatalError` or ensure `OverlayPanel` always sets `contentView`.
- `Sources/Processing/ProcessingCoordinator.swift:45`, closure captures `router`/`route` strongly alongside `self`; potential retain cycle. *Fix:* `[weak self]` only, access `self.router`.

## Medium

- `Sources/Audio/RecordingCoordinator.swift:182-194`, 50ms level timer spawns a new `Task` on every tick. *Fix:* hoist the Task outside the timer or use an async observation loop.
- `Sources/Audio/RecordingCoordinator.swift:65,130,185,203`, fire-and-forget `Task`s can outlive `RecordingCoordinator`; `graceTask`/`transcriptionTask` not cancelled in deinit (line 208). *Fix:* store references, cancel in `deinit`.
- `Sources/App/AppDelegate.swift:200-212`, `phaseObservationTask` re-enters `withCheckedContinuation` forever; leaks if not cancelled on deinit. *Fix:* verify cancellation or switch to `withObservationTracking`.
- `Sources/Permissions/PermissionsCoordinator.swift:73-78`, 1s poll timer keeps ticking past `allGranted`. *Fix:* stop immediately on success.

## Minor

- `Sources/Settings/CloudProviderConfig.swift:41,50,59`, force-unwrap of literal URL strings. *Fix:* `precondition` at startup or static `URL(static:)` helper.
- `Sources/Insertion/TextInserter.swift:22`, hardcoded 100ms clipboard-restore sleep is racy against slow target apps. *Fix:* document the assumption or retry-until-stable.
- `Sources/App/MenuBarController.swift:9`, `NSStatusItem` implicitly unwrapped. *Fix:* guard or fail loudly.
- `Sources/Hotkey/FnPushToTalkMonitor.swift:34-35`, monitor array typed as `Any` with undocumented cleanup contract. *Fix:* type it concretely or document ownership.

## Clean

- No Combine usage
- No storyboards/XIBs
- No AppKit types leaking into SwiftUI views
- No dependencies beyond HotKey
