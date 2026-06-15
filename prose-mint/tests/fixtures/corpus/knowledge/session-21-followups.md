# Session 21 Follow-ups

**Date opened**: 2026-04-12
**Source**: manual testing of session 21's 8-slice implementation of `ux-direction-2026-04-12.md`
**Status**: pending

Three items surfaced during on-device testing of the fn push-to-talk MVP. All three are post-merge refinements, the core interaction is working end-to-end (fn hold to record, release to review, Esc/Return after the deferred-monitor fix in `5a1ee20`).

---

## 1. Stable ad-hoc signing for `swift build` to `Build/Untype.app`

### Problem

Every `swift build && cp .build/debug/Untype Build/Untype.app/Contents/MacOS/Untype` produces a fresh ad-hoc signature (different `CodeDirectory` hash). macOS TCC caches permission grants keyed on designated-requirement + identity; ad-hoc builds look like a "new" app each time, so:

- Accessibility / Input-Monitoring grants are not preserved across rebuilds in some cases.
- `com.untype.app` bundle ID collides with the Xcode DerivedData build, and TCC deduplicates to the stale DerivedData entry (the source of the "DerivedData path showing in Accessibility" confusion earlier today).
- `.build/debug/Untype` is `Mach-O thin (x86_64)` ad-hoc; `codesign -dv` showed `Signature=adhoc`, `TeamIdentifier=not set`.

### Approach

Create a **self-signed local code-signing identity** in the login keychain once, then re-sign on every build. TCC matches by the certificate's SHA1 + subject, which is stable across rebuilds.

Steps:

1. **One-time identity creation** (manual; document in `CLAUDE.md`): create a self-signed certificate named `Untype Dev` via Keychain Access to Certificate Assistant to Create a Certificate to Code Signing. Trust is local-only; not a real Apple Developer identity.
2. **New `bin/build.sh`** wrapper replacing the current `swift build && cp` dance:
   ```sh
   swift build
   cp .build/debug/Untype Build/Untype.app/Contents/MacOS/Untype
   codesign --force \
            --sign "Untype Dev" \
            --identifier com.untype.app \
            --entitlements Untype/Resources/Untype.entitlements \
            --options runtime \
            Build/Untype.app
   touch Build/Untype.app
   ```
3. **`CLAUDE.md` update**: replace the current "App Bundle" section's manual `swift build && cp …` commands with `./bin/build.sh`, and document the one-time identity creation above it.
4. **`.gitignore`** if needed: the script itself is committed; nothing per-user to ignore.

### Fallback if local identity doesn't stabilize TCC

If TCC still flakes (possible on Sequoia, where signing-identity matching has tightened), the secondary option is to fix the Xcode project file, `CLAUDE.md` flags `.xcodeproj` as broken because pbxproj references only 6 of ~20 Swift files. A one-time `project.pbxproj` cleanup gives a properly-signed Debug bundle and stable TCC caching. `swift build` stays the inner loop; Xcode is used only when TCC needs a stable identity.

### Critical files

- `bin/build.sh` (new)
- `CLAUDE.md`, Build & Run section
- `Untype/Resources/Untype.entitlements`, referenced by the codesign invocation
- Optionally: `Untype.xcodeproj/project.pbxproj` if fallback path is taken

---

## 2. Anchor positioning fails inside Electron / VSCode-family apps

### Problem

The overlay anchors correctly for native AppKit text inputs but falls back to top-center for almost anything inside VSCode / Cursor / Electron-based editors. The user also prefers **bottom-center** as the fallback, not top-center, top is surprising and visually collides with the menu bar.

Two distinct issues mixed here:

**2a. Electron/VSCode AX geometry is unreliable.** VSCode exposes AX elements but their frames often report the whole window or a non-input ancestor (Monaco renders its own text surface inside a webview). `FocusedElementLocator.screenFrame()` returns a valid rect that is the entire editor area (sometimes larger than the screen), so the `spaceAbove / spaceBelow >= size.height + padding` check fails for both, dropping to the fallback.

**2b. Top-center fallback is the wrong default.** `positionAboveDock` (session 19) was bottom-center, closer to where attention lives, doesn't collide with menu bar notches / native notifications, consistent with Spotlight's bias. Top-center was a convenience choice during session 21 and feels wrong in practice.

### Approach

Two small fixes plus one defensive one:

1. **Change the fallback to bottom-center.** In `OverlayPanel.preferredFrame`, when the anchor branch doesn't apply, compute `y = visible.minY + padding` instead of `y = visible.maxY - size.height - padding`. (Matches session 19 `positionAboveDock` intent.)

2. **Reject absurd anchor rects.** Inside `FocusedElementLocator.screenFrame()` or in `OverlayPanel.preferredFrame`, discard any anchor whose height exceeds ~70% of `screen.visibleFrame.height`, or whose width exceeds ~90% of the visible width. A "focused element" that's almost the whole screen is not the text caret, it's the editor panel or the window itself. Fall through to bottom-center.

3. **Try `kAXSelectedTextRangeAttribute` + `kAXBoundsForRangeParameterizedAttribute`** as a better caret query. Many editors, including VSCode, implement these to give a tight rect around the actual text caret rather than the whole editor. Sequence:
   - Get focused element.
   - If it supports `kAXSelectedTextRangeAttribute`, read the range.
   - If it supports `kAXBoundsForRangeParameterizedAttribute`, query for that range to get a small caret-adjacent rect.
   - Use that as the anchor; fall back to the element's own frame if any step fails; fall back to bottom-center if the frame is absurd.
   - This is a documented AX pattern (used by macOS Dictation itself) and is the difference between a "pops up near the caret" experience and a "pops up near the window" experience.

4. **Optional, cache the last-known-good anchor.** If the current query returns nil or absurd, reuse the previous cycle's anchor (within, say, 10 seconds). Prevents jumps between "anchored" and "bottom-center" when the user is actively dictating into the same field.

### Critical files

- `Untype/Window/FocusedElementLocator.swift`, add the selected-text-range query + size sanity check
- `Untype/Window/OverlayPanel.swift`, change the fallback direction to bottom-center; optionally share the sanity check

### Verification

Test anchoring in: Safari address bar (native, should anchor); TextEdit (native, should anchor); Notes (native, should anchor); Cursor / VSCode editor (Electron, should anchor to caret via `kAXBoundsForRangeParameterizedAttribute`); Cursor search bar (Electron input); desktop / Finder (no input to bottom-center fallback).

---

## 3. Review toast shows fixed 160pt height for any transcription length

### Problem

`OverlayController.reviewingSize` is hardcoded `CGSize(width: 500, height: 160)`. A five-word transcription ("turn the lights on please") renders as a single short line inside a four-row-tall container with three rows of empty space below it, visually a lot of whitespace for a tiny utterance. The direction doc spec'd a **scrollable** area with `.frame(maxHeight: 100)` which only matters when the content exceeds the height; it doesn't shrink when the content is smaller.

### Approach

Make the review-toast height adaptive to the content, with a minimum and maximum:

- **Min**: ~72pt, enough for one line plus the hint row and vertical padding.
- **Max**: ~200pt, roughly 4 lines of 14pt text + hint row + padding. Beyond this, the internal `ScrollView` takes over.
- **Width**: stays at 500pt (matches the compact recording bar, keeps the user's visual model stable).

Implementation options, from simplest to most correct:

1. **Heuristic based on character count.** Count the characters in `text`; divide by ~55 (rough character budget per line at 500pt with 14pt font); cap at 4 lines; compute total height. Cheap, no layout round-trip. Works well enough for the 99% case; margin-of-error cases just round up a line.

2. **Use `NSHostingView.fittingSize` / `sizeThatFits`** for exact measurement. `OverlayController` builds a throwaway `NSHostingView(rootView: ReviewingBody(text: text))`, asks for its `fittingSize(NSView.layoutFittingCompressedSize)` or uses `sizeThatFits(in: CGSize(width: 500, height: .greatestFiniteMagnitude))`, and uses the returned height (clamped). More accurate, one extra layout pass per review transition, negligible.

3. **Self-reporting via `PreferenceKey`.** `ReviewingBody` publishes its natural size via a `PreferenceKey`; `OverlayController` observes it through a shared `@Observable` and resizes. Most "SwiftUI-correct" but overkill for a one-shot measurement, and introduces the usual `PreferenceKey` + animation timing hazards.

**Recommendation**: option 2 (`NSHostingView.fittingSize`). It's local to `OverlayController`, doesn't leak layout coupling into the view hierarchy, and gives pixel-accurate sizing. The computed size is clamped into `[minReviewingSize, maxReviewingSize]` before being passed to `panel.setGeometry(size:)`.

### Related cleanup

- `ReviewingBody` currently hardcodes `ScrollView { ... }.frame(maxHeight: 100)`. With adaptive sizing, the `.frame(maxHeight:)` should be lifted, let the content grow until `OverlayController` clamps it, then the `ScrollView` takes over for truly long transcripts.
- The compact `BarView` HStack is already adaptive (fills whatever height the panel gives it). No change needed there.
- Animation: `panel.setFrame(_, display:, animate: true)` is already used for the recording-to-reviewing transition; the adaptive height will animate from 48pt (compact) to the measured reviewing size without extra work.

### Critical files

- `Untype/Window/OverlayController.swift`, replace `reviewingSize` constant with a `measureReviewingSize(for text: String)` function
- `Untype/Window/BarView.swift`, `ReviewingBody`: drop the inner `.frame(maxHeight: 100)`, let it grow naturally

### Verification

Test with: a 3-word transcription (should be ~72pt tall), a one-sentence transcription (~100pt), a paragraph (~200pt capped, inner scroll takes over beyond that).

---

## Order of execution

1. **#1 first**, unblocks testing ergonomics. Without stable TCC, testing every other fix requires re-granting permissions.
2. **#3 second**, small, self-contained, visually high-impact. One file touched.
3. **#2 third**, most code, touches AX semantics. Needs real testing in VSCode/Cursor to validate the `kAXBoundsForRangeParameterizedAttribute` path.

No dependency between them; they can also be done in any order once #1 lands.
