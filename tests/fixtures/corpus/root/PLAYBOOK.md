# Untype Claude Code Playbook

## Workflow Choice: Why Not Ralph/BMAD/GSD

**Ralph Loop** shines for large task backlogs with automated verification (test suites, type checkers). Untype is a native macOS app where most milestones require *running the app and observing behavior*. There's no `npm test` that proves the overlay doesn't steal focus. Running Ralph overnight against an empty Xcode project with no test harness will produce code that compiles but doesn't work.

**BMAD** is enterprise ceremony for a project that already has a tight spec. You already *are* the PM, architect, and scrum master.

**GSD** adds value for long autonomous sessions, but its 4:1 token overhead and context-rotation machinery is overkill for 8 focused phases where each needs manual verification on a real Mac.

**Recommended approach**: Interactive phased sessions with worktrees for parallel exploration. Each phase is one focused Claude Code session. You verify the milestone manually, commit, then start the next phase fresh.

---

## 1. Project CLAUDE.md

Create `Untype/CLAUDE.md`:

```markdown
# Untype

macOS voice-to-text overlay app. Native Swift, AppKit + SwiftUI.

## Build & Run

- Build: `xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build`
- Run: `open Build/Products/Release/Untype.app` (or run from Xcode)
- Clean: `xcodebuild clean -project Untype.xcodeproj -scheme Untype`

## Architecture

- State machine in `AppState.swift` drives all UI — never mutate UI directly
- `OverlayPanel` is NSPanel (non-activating) — must never steal focus from target app
- All async work uses Swift concurrency (async/await), not Combine
- Single external dependency: HotKey via SPM

## Rules

- NEVER use storyboards or XIBs — all UI is programmatic (AppKit) or SwiftUI
- NEVER add dependencies beyond HotKey unless explicitly discussed
- NEVER use Combine — use async/await and @Observable
- Keep each Swift file under 200 lines — split if larger
- All AppKit window/panel code goes in Window/ — SwiftUI views reference no AppKit types
- Entitlements and Info.plist must stay in sync with required permissions

## File Layout

See IMPLEMENTATION_PLAN.md for full structure. Key convention:
- App/ — lifecycle, menu bar
- Window/ — NSPanel, hosting controller
- Audio/ — mic capture
- Transcription/ — STT providers (protocol + implementations)
- Processing/ — LLM text cleanup
- Insertion/ — clipboard + CGEvent paste
- Hotkey/ — global shortcut
- State/ — observable state enum
- Settings/ — prefs UI and storage

## Verification

After any change, confirm it builds:
`xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build 2>&1 | tail -5`
```

---

## 2. Settings Configuration

### Project settings (`.claude/settings.json`)

```json
{
  "permissions": {
    "allow": [
      "Read",
      "Bash(xcodebuild *)",
      "Bash(swift *)",
      "Bash(open *)",
      "Bash(git log *)",
      "Bash(git diff *)",
      "Bash(git status)",
      "Bash(git add *)",
      "Bash(git branch *)",
      "Bash(git checkout main)",
      "Bash(git checkout -b *)",
      "Bash(ls *)",
      "Bash(cat *)",
      "Bash(xcrun *)",
      "Bash(plutil *)",
      "Bash(defaults *)",
      "Bash(swiftformat *)",
      "Bash(swift package *)"
    ],
    "deny": [
      "Bash(rm -rf *)",
      "Bash(git push *)",
      "Bash(git reset --hard *)",
      "Bash(git clean *)",
      "Bash(git commit *)"
    ]
  }
}
```

> **Note:** `git commit` is denied so Claude prompts for confirmation before committing. It's a safety gate, not a block. Approve when ready.

### User-level additions (`~/.claude/settings.json`)

```json
{
  "effortLevel": "high",
  "autoMemoryEnabled": true,
  "hooks": {
    "Notification": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "osascript -e 'display notification \"Claude Code needs attention\" with title \"Untype\"'"
          }
        ]
      }
    ]
  }
}
```

---

## 3. Conditional Rules (`.claude/rules/`)

### `.claude/rules/swiftui.md`

```markdown
---
paths:
  - "Untype/**/BarView.swift"
  - "Untype/**/SettingsView.swift"
---

# SwiftUI Rules

- Use @Observable (not ObservableObject/Published) — requires macOS 14+
- Prefer ViewBuilder composition over large body properties
- No AppKit imports in SwiftUI views — communicate via state only
- Test visual changes by building and describing expected appearance
```

### `.claude/rules/appkit.md`

```markdown
---
paths:
  - "Untype/Window/**"
  - "Untype/App/AppDelegate.swift"
---

# AppKit Rules

- OverlayPanel must use .nonactivatingPanel style mask — this is non-negotiable
- Always set panel.level = .floating
- Position relative to screen.visibleFrame, not screen.frame (accounts for dock/menu bar)
- NSVisualEffectView with .hudWindow material for frosted glass
- Never call makeKeyAndOrderFront — use orderFront(nil) to avoid activation
```

### `.claude/rules/audio.md`

```markdown
---
paths:
  - "Untype/Audio/**"
  - "Untype/Transcription/**"
---

# Audio & Transcription Rules

- Always check AVCaptureDevice.authorizationStatus before starting capture
- AVAudioEngine tap format: 16kHz mono Float32 for speech recognition
- SFSpeechRecognizer: use on-device recognition (.requiresOnDeviceRecognition = true)
- Handle SFSpeechRecognizerDelegate for availability changes
- Always call recognitionTask.finish() on stop, not .cancel() (preserves final results)
```

---

## 4. Custom Skills

### `.claude/skills/build/SKILL.md`

```markdown
---
name: build
description: Build the Untype Xcode project and report errors
allowed-tools: Bash Read
---

Build the Untype project and report results:

1. Run: `xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build 2>&1`
2. If build succeeds, report success
3. If build fails, show only the error lines (filter for ": error:")
4. Never attempt to fix errors — just report them
```

### `.claude/skills/phase/SKILL.md`

```markdown
---
name: phase
description: Start implementation of a specific phase from the plan
allowed-tools: Bash Read Edit Write Grep Glob
effort: high
---

Implement phase $ARGUMENTS from IMPLEMENTATION_PLAN.md.

1. Read IMPLEMENTATION_PLAN.md and find the phase
2. Read all existing source files to understand current state
3. Implement everything listed for that phase
4. After each file created/modified, run a build check:
   `xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build 2>&1 | tail -20`
5. Fix any build errors before moving to the next file
6. Write corresponding unit tests for new code
7. When done, report the milestone status and what to verify manually
```

### `.claude/skills/verify/SKILL.md`

```markdown
---
name: verify
description: Verify the current build state and check milestone completion
allowed-tools: Bash Read Grep Glob
---

Check the current state of the Untype project:

1. Build: `xcodebuild -project Untype.xcodeproj -scheme Untype -configuration Debug build 2>&1 | tail -10`
2. List all Swift source files and their line counts
3. Check which phases from IMPLEMENTATION_PLAN.md appear to be implemented (by looking at which files exist and what they contain)
4. Report: what's done, what's next, any build issues
```

---

## 4a. Custom Skills Registration

Custom skills are placed in `.claude/skills/{skill-name}/SKILL.md` and are auto-discovered by Claude Code.

**Usage:**
- Skills are invoked with slash commands in chat
- Example: `/phase 1` to implement Phase 1
- Example: `/build` to build and check for errors
- Example: `/verify` to check project status

**Skill files:**
- `build/SKILL.md` builds the Xcode project and reports errors
- `phase/SKILL.md` implements a specific phase from the implementation plan
- `verify/SKILL.md` checks current build state and milestone completion

---

## 5. MCP Servers

### Useful for this project

```bash
# Apple developer docs — Context7 injects live framework docs
claude mcp add --transport http context7 https://mcp.context7.com/mcp

# GitHub — for managing the repo, PRs, issues
claude mcp add github -- npx -y @anthropic-ai/mcp-remote@latest https://mcp.github.com/sse
```

### Skip for this project

| MCP | Why skip |
|-----|----------|
| Playwright / browser | No web UI to test. |
| Database | No database. |
| Figma | UI is a single bar; not worth the setup. |
| Notion | You already have one configured; use it if your notes are there. |

---

## 6. Workflow Per Phase

### Starting a phase

```bash
# Fresh session, named for easy resumption
cd Untype
claude -n "phase-1-skeleton"

# Then in the session:
/phase 1
```

### If you need to explore an API you're unsure about

```bash
# Parallel worktree for experimentation (won't affect main work)
claude -w spike-nspanel -n "spike-nspanel"

# In that session:
> Build a minimal NSPanel example that demonstrates non-activating overlay behavior.
> I want to understand the style mask combinations before committing to the real implementation.
```

### Resuming after a break

```bash
claude -r "phase-1-skeleton"
# or just
claude -c  # continues most recent
```

### After manual verification passes

```bash
# In the session:
> The milestone works — bar shows and hides on keypress without stealing focus.
> Commit this as "Phase 1: skeleton + overlay window"
```

---

## 7. Phase-Specific Tips

| Phase | Claude Code Strategy | Testing |
|---|---|---|
| **1: Skeleton** | Start here. Have Claude create the Xcode project structure via `swift package init` + manual xcodeproj, or describe the structure and let it generate files. Build-verify after every file. | Add unit tests for AppState state machine transitions |
| **2: Hotkey** | Small scope; single session. Add SPM dependency, wire up HotKey. | Integration test: hotkey triggers state change |
| **3: Audio** | Spike in a worktree first if unfamiliar with AVAudioEngine. The tap format matters. | Unit tests for AudioRecorder: buffer capture, WAV generation, cleanup |
| **4: Transcription** | This is the most API-surface-heavy phase. Use `--effort high`. Have Context7 MCP loaded for Apple Speech docs. | Unit tests for AppleSpeechService with mocked SFSpeechRecognizer |
| **5: AI Processing** | Straightforward URLSession + JSON. Use `/claude-api` skill if calling Anthropic API. | Unit tests for TextProcessor with mocked API responses |
| **6: Insertion** | CGEvent is tricky; clipboard save/restore timing matters. Spike the paste mechanism separately. | Unit tests for TextInserter with clipboard mocking |
| **7: Review** | UI-heavy. Have Claude describe the expected visual state since it can't see the app. | E2E test: full flow with review state |
| **8: Polish** | Good candidate for parallel worktrees: settings UI, animations, and onboarding can be built independently. | VoiceOver accessibility test, offline mode test |

---

## 8. Hooks for Build Verification

Simplified approach: manual build checks are more reliable than fragile hooks.

**Recommended:** After editing Swift files, manually run `build` skill to verify.

**Optional reminder hook** (non-blocking):
```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "message",
            "message": "Swift file modified. Run 'build' to verify compilation."
          }
        ]
      }
    ]
  }
}
```

---

## 9. Rollback and Recovery

**If a phase breaks the build:**
```bash
# See what changed
git diff HEAD~1

# Revert last commit if needed
git reset --soft HEAD~1
# (keeps your changes, undoes the commit)
```

**Use worktrees for risky experiments:**
```bash
# Create isolated worktree for experimentation
git worktree add ../untype-spike spike-branch

# Work in the spike without affecting main
cd ../untype-spike
claude -n "spike-experiment"

# When done, remove worktree
cd /Users/costa/Projects/Untype
git worktree remove ../untype-spike
git branch -D spike-branch
```

**Recovery checklist:**
1. Run `build` skill to check current state
2. Run `git status` to see uncommitted changes
3. If build fails, identify which file caused it
4. Use `git diff` to see recent changes
5. Revert problematic changes with `git restore <file>`
6. Run `build` again to verify fix

**Backup strategy:**
- Tag each completed phase: `git tag phase-1-complete`
- If disaster strikes: `git reset --hard phase-1-complete`

---

## 10. Effort Level Explanation

**What "effort level" does in Claude Code:**
- `high`: More extended thinking time, deeper analysis, considers more alternatives
- `medium` (default): Balanced approach, efficient for straightforward tasks
- `low`: Faster responses, less deliberation

**When to use high effort:**
- Phase 1 (project structure decisions compound)
- Phase 4 (SFSpeechRecognizer streaming is subtle)
- Phase 6 (CGEvent + clipboard timing)
- Architectural decisions or API design
- Debugging complex issues

**When medium is fine:**
- Phases 2, 3, 5, 8 (well-documented APIs, straightforward logic)
- Routine implementation work
- Following clear specifications

```bash
# Per-session
claude --effort high -n "phase-4-transcription"

# Or mid-session
/effort high
```

---

## 11. Source Insights Applied to This Project

From Claude Code's internal architecture, things that help specifically here:

1. **Build after every file change.** Claude's Edit tool requires exact string matching. If a build fails, Claude can read the error and fix it in the same turn. But if errors accumulate across files, recovery gets harder. Verify early and often.

2. **Keep files under 200 lines.** Claude reads files with a 2000-line default, but smaller files = faster reads, more precise edits, fewer uniqueness conflicts with the Edit tool.

3. **Use absolute paths in CLAUDE.md.** Claude's Glob/Grep work from CWD, but absolute paths in build commands prevent confusion when sessions start from different directories.

4. **Describe expected visual behavior in words.** Claude can't see your screen. After UI changes, tell it what you see: "The bar appears but it's opaque, not frosted" gives it signal to fix.

5. **Fresh sessions per phase.** Context rot is real. Phase 1's completed code is best understood by reading it fresh, not through 50 turns of conversation history. This is the Ralph Loop insight without the loop.

6. **Write tests alongside implementation.** Testable code is better code. Protocol-based design (used for transcription and AI processing) makes mocking easy for unit tests. Write tests as you implement each phase, not as an afterthought.

---

## 12. Git Strategy

```bash
# Branch per phase
git checkout -b phase-1-skeleton
# ... work ...
git checkout main && git merge phase-1-skeleton

# Or simpler: linear commits on main, tag milestones
git tag phase-1-complete
```

For Phase 8 (polish), worktrees make sense since settings/animations/onboarding are independent:

```bash
claude -w polish-settings -n "settings"
claude -w polish-animations -n "animations"
claude -w polish-onboarding -n "onboarding"
# Merge each when verified
```

---

## 13. App Store Build Steps

**Code Signing:**
```bash
# Sign the app bundle
codesign --deep --force --verify --verbose --sign "Developer ID Application: Your Name" Build/Products/Release/Untype.app

# Verify signature
codesign -vvv --deep --strict Build/Products/Release/Untype.app
```

**Notarization:**
```bash
# Submit for notarization (requires Apple Developer account)
xcrun notarytool submit Build/Products/Release/Untype.app \
  --apple-id "your@email.com" \
  --password "app-specific-password" \
  --team-id "YOUR_TEAM_ID" \
  --wait

# Staple the notarization ticket to the app
xcrun stapler staple Build/Products/Release/Untype.app
```

**Archive Creation:**
```bash
# Create archive for App Store upload
xcodebuild -project Untype.xcodeproj \
  -scheme Untype \
  -configuration Release \
  -archivePath Build/Untype.xcarchive \
  archive
```

**Export for App Store:**
```bash
# Export archive for App Store submission
xcodebuild -exportArchive \
  -archivePath Build/Untype.xcarchive \
  -exportPath Build/export \
  -exportOptionsPlist ExportOptions.plist
```

**ExportOptions.plist example:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store</string>
    <key>teamID</key>
    <string>YOUR_TEAM_ID</string>
    <key>signingStyle</key>
    <string>automatic</string>
    <key>uploadSymbols</key>
    <true/>
</dict>
</plist>
```

---

## 14. Quick Reference

| Action | Command |
|---|---|
| Start phase N | `claude -n "phase-N" --effort high` then `/phase N` |
| Build check | `/build` |
| Project status | `/verify` |
| Spike/experiment | `claude -w spike-name` |
| Resume work | `claude -c` or `claude -r "session-name"` |
| Parallel polish | `claude -w feature-name --tmux` |
| Check costs | `/cost` in session |
| Compact context | `/compact` when session gets long |
