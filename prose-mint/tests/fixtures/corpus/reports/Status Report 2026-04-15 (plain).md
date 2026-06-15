# Untype Status Report 2026-04-15

**Period:** April 14–15, 2026 (4 work sessions, 37 changes shipped)

Two busy days across four sessions. I cleaned up accumulated development debris, ran a thorough codebase health check and fixed every issue found, improved voice recognition quality, and built an automated testing system so future improvements can be measured objectively instead of relying on manual mic tests.

## Research & Investigation

| Topic | What I learned |
|---|---|
| Voice recognition tuning | I audited every available setting on Apple's built-in speech recognition engine to find ways to improve transcription quality. The biggest free win was enabling automatic punctuation (periods, commas, question marks). Previously users had to speak punctuation out loud. The next major lever is training a custom vocabulary model tailored to Untype's domain. |
| Code health audit | I ran a comprehensive review of the entire codebase looking for bugs, performance issues, and maintainability concerns. Found 13 issues across critical, medium, and minor severity. All critical and medium items were fixed. |
| Animation planning | I surveyed the app's current visual state and identified 7 candidate animation effects to make the overlay feel more polished. No animations exist today. This is a wide-open opportunity. Decision on direction is pending. |

## What was achieved

### Voice recognition improvements

I made two changes that directly improve the quality of what users see when they dictate:

- **Automatic punctuation is now enabled.** The app now adds periods, commas, and question marks automatically based on speech patterns. Previously, dictated text came through as a wall of unpunctuated words.
- **Domain vocabulary hints are wired in.** The speech engine now recognises "Untype" and other product-specific terms more reliably. The system is ready to grow this vocabulary from user settings or usage patterns in the future.

I also researched and prototyped a custom vocabulary model that could significantly improve accuracy for technical and domain-specific terms. The building blocks are in place but not yet active in the app.

### Automated quality testing

Previously, the only way to verify voice recognition or text cleanup changes was to speak into a microphone and visually inspect the result. That made it impossible to track regressions or compare approaches objectively.

I built an automated testing system that can:

- Play pre-recorded audio through the real voice recognition pipeline
- Score the transcription accuracy against a known reference (using industry-standard word error rate)
- Run the AI text cleanup step and score the output
- Produce a report comparing multiple configurations side by side

Three initial test recordings are included as a smoke test. The system is validated and working. Real-world recordings are the next step to make the scores meaningful.

### App stability and code quality

A comprehensive code health audit found 13 issues. I fixed all critical and medium items across 8 targeted changes:

- Fixed several potential crash scenarios related to unsafe type assumptions
- Resolved resource cleanup issues where background tasks and timers could outlive their owners
- Improved a performance hotspot in the audio level monitoring that was creating unnecessary work every 50 milliseconds
- Made the voice recognition service fail gracefully instead of crashing when the system doesn't support on-device recognition
- Broke two large, complex files into smaller, focused components; every source file now meets the project's maintainability guidelines

### Development tooling and process

- Built a reusable tool for auditing code health that can be re-run at any time
- Reworked the session management workflow into a cleaner three-step lifecycle (start, report, end)
- Cleaned up 8 stale development branches and standardised the report archiving system
- Added opt-in performance caching for the AI text cleanup API calls, which can reduce costs and latency on supported providers

## Current state

### What's working

- The app builds and all 26 automated tests pass
- The automated voice recognition test suite runs end-to-end with accurate scoring
- Automatic punctuation and vocabulary hints are active in the app
- The voice recognition system has a clean interface that will allow swapping in alternative engines in the future
- All source files meet the project's size and quality guidelines after the health audit

### Known limitations

- **No real-world test recordings yet.** The current test audio is computer-generated, which is useful for smoke testing but doesn't reflect how real people speak. Meaningful quality measurements require human voice recordings.
- **Custom vocabulary model is built but not active.** The model compiler and integration hooks exist, but the app doesn't load the model at startup yet. No before/after quality comparison has been done.
- **API cost caching hasn't been tested live.** The caching feature is implemented and unit-tested, but hasn't been verified against a real API endpoint.
- **Full manual end-to-end app test is still pending.** The app hasn't been tested manually with the default AI provider and offline fallback since the recent changes.
- **No animations yet.** The animation plan exists but no visual polish has been implemented.

## What's next

### Immediate priorities

1. **Add real-world voice recordings** to the test suite (clean speech, false starts, background noise, and technical vocabulary). This unlocks meaningful accuracy comparisons for every future change.
2. **Activate the custom vocabulary model** in the app at startup and measure its impact on transcription accuracy using the new test suite.
3. **Verify API cost caching** against a live endpoint to confirm the savings are real.
4. **Add the first visual animation** (a smooth transition effect between app states), which is the safest starting point for the polish track.
5. **Run a full manual test** of the app end-to-end with the default AI provider and offline fallback.

### Later

- **Voice recognition track:** Show confidence levels in the overlay (dim uncertain words), pass alternative interpretations to the AI cleanup step, support additional languages, evaluate alternative recognition engines.
- **API track:** Add a direct connection to Anthropic's API for better streaming and cost visibility, add automatic retry logic for transient failures.
- **Visual polish track:** Decide on animation direction and implement the remaining 6 planned effects (fade-in, breathing indicator, audio-reactive glow, resize animation, error pulse, streaming text).
- **Housekeeping:** Clean up a few stray files from earlier development phases.
