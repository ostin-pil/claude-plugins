# Overlay Animation Direction, 2026-04-14

Discussion notes, not a decision. Captured so we can resume the animation planning thread without re-deriving the terrain.

## Current state of the overlay (from the survey earlier in session 26)

- `NSPanel` + `NSVisualEffectView` (`.hudWindow` material, 16px radius) hosting a SwiftUI `BarView`.
- State-driven: every `AppState.Phase` maps to a specific visual. Phases: `.idle`, `.setup`, `.onboarding`, `.listening`, `.transcribing`, `.processing`, `.reviewing`, `.inserting`, `.error`.
- `BlobWaveform` draws the cyan listening visualization via `Canvas`.
- **Zero SwiftUI animations in the source today.** Grep for `.animation(`, `withAnimation`, `.transition(`, `spring`, `TimelineView` returns no matches. `NSPanel.setFrame(animate:)` is the only motion.

Greenfield. Every effect below is additive.

## Reference target

"Claude Desktop-like" recording feel: soft glows, breathing halos, audio-reactive distortion, smooth phase crossfades, spring-easing on resizes, gentle color washes, continuous subtle motion that makes the overlay feel alive without being loud.

No concrete design brief yet. A 30-second capture of the target app would pin the direction down fast; without it we would be iterating against a mental image.

## Technical ceiling on our stack

What SwiftUI + AppKit can give us on macOS 14–15:

**Cheap and native**
- `.shadow(radius:)`, `.blur(radius:)`, `.background()` with gradients
- `LinearGradient`, `RadialGradient`, `AngularGradient`
- `MeshGradient` (macOS 15+, gorgeous for living color washes)
- `.animation(.spring())`, `withAnimation`, `.transition(...)`
- `TimelineView(.animation)` for continuous clock-driven loops
- Arbitrary `Canvas` drawing, already used by `BlobWaveform`
- Compositor-accelerated for free

**Mid-effort but doable**
- Metal shader effects via `.colorEffect` / `.distortionEffect` / `.layerEffect` (macOS 14+). Plumb `appState.audioLevel` into a shader uniform for pixel-level audio reactivity: moving gradients, warping glows, noise-modulated halos. This is how Claude Desktop, Raycast AI, and Wispr Flow get their "alive" feel.

**Hard / out of scope**
- True 3D or particle systems (SceneKit / raw Metal)
- Exact pixel-match to a reference app without its source assets

## Untype-specific constraints

1. **Tiny canvas.** 500×48 normally; resizes to ~500×200 in `.reviewing`. Fine particle effects just look like noise at that size, go for large, soft, low-frequency motion.
2. **Frosted background.** `NSVisualEffectView` (`.hudWindow`) composites with whatever is behind the panel. Great for soft washes, bad for high-contrast effects, anything saturated will fight the material.
3. **Continuous-motion GPU cost.** Breathing loops and shader effects burn GPU while visible. OK during active recording (~5s), not OK while `phase == .idle`. Every continuous animation must pause when the panel is hidden or idle.
4. **No focus stealing.** The panel must never steal focus, no SwiftUI APIs requiring key-window status, no `NSApp.activate`, and all input stays routed to the target app.
5. **Must read at a glance.** The overlay is glanceable UX, a user should identify the phase in <200ms without parsing. Motion should reinforce state, not fight it.

## Design space

Five concrete candidate effects, ordered by impact-per-effort estimate:

1. **Pulsing halo**, soft radial glow behind the `BlobWaveform`, radius and opacity modulated by live audio level. Single highest-impact effect. ~30 lines in `BlobWaveform.swift`.
2. **Phase-transition crossfade**, `.animation(.smooth(duration: 0.25), value: phase)` on the root switch in `BarView`, plus `.transition(.opacity.combined(with: .scale(0.92)))` on icons and spinners. Kills the current "pop" between states. Maybe 20 lines.
3. **Breathing baseline**, the `BlobWaveform` baseline amplitude oscillates ±20% at ~1Hz during `.listening` even in silence. Prevents dead-flat look. Needs a `TimelineView` wrapper or a `@State` counter driven by a `Timer`.
4. **Animated mesh gradient background**, `MeshGradient` with control points drifting slowly (macOS 15+ only). Replaces or overlays the frosted background for a living color wash. Distinct feel; costs one branch on OS version.
5. **Shader-warped waveform**, Metal shader via `.layerEffect` that distorts the `BlobWaveform` fill based on `audioLevel` + elapsed time. "Liquid" feel. Biggest visual upside, highest effort, macOS 14+ only.

Orthogonal ideas we shouldn't forget:
- **Overlay fade-in on show**, `OverlayController.show()` currently does an instant `orderFront`. Animate the hosting view's layer opacity 0-to-1 over 0.15s. Cheap polish.
- **Spring-timed panel resize**, replace the system linear `setFrame(animate:)` with `CABasicAnimation` + spring timing on the `.reviewing` height jump.
- **Error pulse**, on `.error`, briefly scale the icon 0.8-to-1.1-to-1.0.
- **Partial-text stream-in**, transition new words in from the left with opacity + x-offset.

## Open questions before committing

1. **Reference clip or no reference?** Designing to a named target is ~3x faster than designing blind. If we have a Claude Desktop capture we can match, pick effects against it. If not, the risk is iterating to a local maximum that doesn't feel like the thing we actually wanted.
2. **Maximalist vs subtle?** "Claude-Desktop-like" spans a wide range. Subtle (gentle glow + crossfades only) is safer and gets 80% of the perceived polish. Maximalist (mesh gradient + shader warp + breathing + halo) is more distinctive but risks the overlay feeling busy at 500×48.
3. **macOS 15 hard dep?** `MeshGradient` is macOS 15+. If we want it we need a deployment-target bump or a fallback path. Current `Package.swift` is 14+.
4. **How do we prototype?** Three options:
   - (a) Pick one single effect (e.g. pulsing halo) and land it as the
     calibration point before committing to anything else.
   - (b) Sketch 2–3 distinct visual directions side by side in code
     and pick after seeing them live.
   - (c) Build a standalone "animation playground" SwiftUI preview
     target isolated from the main app to iterate faster.

## Performance budget

Rough rule of thumb for continuous motion on the overlay:
- `TimelineView(.animation)` with simple SwiftUI shapes: essentially free
- `.shadow()` + `.blur()` over `NSVisualEffectView`: cheap, ~1–2% GPU
- `LinearGradient`/`RadialGradient`: cheap
- `MeshGradient` with moving control points: moderate, ~3–5% GPU on M1
- `.layerEffect` Metal shader: depends on the shader, budget 5–10% GPU
- Any combination: pause everything when `!appState.isOverlayVisible`

Hard rule: **no continuous animation runs while the overlay is hidden.** Gate every `TimelineView` or Timer-driven animation on `phase != .idle` and on panel visibility.

## What we agreed NOT to do (yet)

- No concrete design commitments until we anchor on a reference or prototype one effect.
- No deployment-target bump (macOS 15) until we know we want `MeshGradient`.
- No standalone animation playground until we've tried the one-effect calibration approach first.
- No skills-time implementation, animation work is its own session slice, not bolted onto audit triage.
