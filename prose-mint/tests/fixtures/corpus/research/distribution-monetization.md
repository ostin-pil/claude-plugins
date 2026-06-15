# Untype: Distribution & Monetization Research

**Date:** 2026-04-10  
**Status:** Research complete, recommendations included

---

## Table of Contents

1. [Distribution Paths](#1-distribution-paths)
2. [Competitor Pricing Landscape](#2-competitor-pricing-landscape)
3. [Monetization Models](#3-monetization-models)
4. [Payment Processors](#4-payment-processors)
5. [Tax & Legal Considerations](#5-tax--legal-considerations)
6. [Recommended Strategy](#6-recommended-strategy)

---

## 1. Distribution Paths

### 1.1 Mac App Store (Sandboxed)

#### Required Entitlements

| Entitlement | Key | Purpose |
|---|---|---|
| App Sandbox | `com.apple.security.app-sandbox` | Required for all App Store apps |
| Microphone | `com.apple.security.device.microphone` | AVAudioEngine capture |
| Audio Input | `com.apple.security.device.audio-input` | Speech recognition input |
| Network Client | `com.apple.security.network.client` | LLM API calls |
| Accessibility | `com.apple.security.accessibility` | Text insertion (problematic -- see below) |

**Current entitlements file** (`Untype/Resources/Untype.entitlements`) already includes sandbox, microphone, audio-input, and network-client. Accessibility is missing.

#### Critical Issue: CGEvent.post() in Sandbox

**CGEvent.post() does NOT work reliably in sandboxed apps.** The current `TextInserter.swift` uses `CGEvent.post(tap: .cghidEventTap)` to simulate Cmd+V, which requires the `kTCCServicePostEvent` privilege. This is a separate TCC service from `kTCCServiceAccessibility`.

**The AXUIElement alternative is also problematic in sandbox:**
- When App Sandbox is enabled, the Accessibility permission prompt never appears
- The app cannot be manually added in System Settings > Privacy & Security > Accessibility
- `AXIsProcessTrusted()` always returns `false`
- This is a known, long-standing issue on Apple Developer Forums (threads from 2022-2026)

**Bottom line:** Text insertion via either CGEvent or AXUIElement is fundamentally broken in sandboxed apps. Apps like Wispr Flow that are on the App Store likely use private APIs, temporary entitlement exceptions from Apple, or workarounds like the Input Monitoring privilege (which IS available to sandboxed apps via CGEventTap).

**Possible workarounds for App Store:**
1. Request a private entitlement exception from Apple (unlikely for indie apps)
2. Use Input Monitoring + CGEventTap (available in sandbox, but posting events may still be blocked)
3. Use a non-sandboxed helper tool distributed alongside the app (complex, fragile)
4. Limit to clipboard-only mode on App Store (user manually Cmd+V)

#### App Review Considerations for AI/LLM Apps

Apple's **Guideline 5.1.2(i)** (introduced November 2025) specifically regulates third-party AI:
- Must clearly disclose where personal data is shared with third-party AI services
- Must obtain explicit user consent before sending data to external LLMs
- Voice recordings sent to external transcription services require disclosure
- Apps that mislead about AI capabilities face rejection

**Requirements for Untype:**
- Privacy policy disclosing data flow to LLM providers (OpenAI, Anthropic, etc.)
- In-app consent dialog before first API call
- Clear labeling of which features use cloud AI vs. on-device processing
- Privacy Nutrition Label must list all data categories sent to third parties

#### Apple's 30% Cut

- 30% commission on all App Store sales (first year)
- 15% for developers earning under $1M/year (Small Business Program)
- For subscriptions: 30% year one, 15% from year two onward
- If Untype is priced at $10/month, Apple takes $3/month (year 1) or $1.50/month (year 2+)
- BYOK model avoids Apple's cut on API costs (user pays their provider directly)

### 1.2 Developer ID (Direct Distribution)

#### Notarization Requirements

Notarization is **mandatory** since macOS 10.15 for any app distributed outside the App Store. Without it, macOS will refuse to open the app.

**Process:**
1. Sign with Developer ID Application certificate
2. Enable Hardened Runtime
3. Submit to Apple's notarization service via `xcrun notarytool submit`
4. Apple scans for malware, checks code signing
5. Staple the notarization ticket to the app: `xcrun stapler staple Untype.app`

**Hardened Runtime implications:**
- Prevents code injection, DLL hijacking, process memory tampering
- Must declare entitlements for functions like microphone, accessibility
- CGEvent.post() works without sandbox restrictions (only needs Accessibility permission grant from user)
- No App Sandbox required -- full system access with user-granted permissions

**Key advantage:** CGEvent.post() works perfectly outside sandbox. User grants Accessibility permission once in System Settings, and text insertion works everywhere. This is the approach most competitors use.

#### Auto-Update: Sparkle Framework

[Sparkle](https://sparkle-project.org/) is the standard for macOS auto-updates outside the App Store.

- Open source, well-maintained, widely used
- Supports sandboxed apps via XPC Services (if needed for dual distribution)
- EdDSA (ed25519) signature verification for update integrity
- Requires careful code signing order (XPC services first, then app)
- Supports delta updates to minimize download size
- Can host update feed (appcast.xml) on any static hosting (GitHub Pages, S3, etc.)

#### Payment Processing Options

See [Section 4](#4-payment-processors) for detailed comparison.

### 1.3 Both (Universal Build)

A dual-distribution strategy is possible but adds complexity:

**Runtime capability detection approach:**
```swift
// Pseudocode
if ProcessInfo.processInfo.isSandboxed {
    // Use clipboard-only mode or AX-based insertion
    textInsertionStrategy = .clipboardManual
} else {
    // Use CGEvent.post() for seamless paste
    textInsertionStrategy = .cgEventPaste
}
```

**Considerations:**
- Two separate builds with different entitlements
- App Store version may have degraded text insertion UX
- Increases testing surface and maintenance burden
- Most competitors choose one path (usually direct distribution)

**Recommendation:** Start with Developer ID only. The text insertion limitation in sandbox is a dealbreaker for Untype's core UX. Revisit App Store if/when Apple provides a proper accessibility entitlement for sandboxed apps.

---

## 2. Competitor Pricing Landscape

### 2.1 Pricing Comparison Table (as of April 2026)

| App | Model | Price | Local STT | Cloud STT | AI Cleanup | BYOK | Distribution |
|---|---|---|---|---|---|---|---|
| **Superwhisper** | Freemium + Sub/Lifetime | Free / $8.49/mo / $85/yr / $250 lifetime | Yes | Yes (Pro) | Yes (Pro) | Pro only | Direct |
| **Wispr Flow** | Freemium + Sub | Free (2K words/wk) / $12-15/mo / $144/yr | No | Yes | Yes | No | App Store + Direct |
| **MacWhisper** | Freemium + Sub/Lifetime | Free / $5/wk / $9/mo / $30/yr / $80 lifetime | Yes | Yes (Pro) | Yes (Pro) | No | App Store |
| **AudioPen** | Free + Paid | Free (3 min) / $99/yr / $159/2yr | No | Yes | Yes | No | Web app |
| **Voibe** | Sub/Lifetime | $4.90/mo / $44/yr / $99 lifetime | Yes | No | No | No | Direct |
| **SpeakMac** | One-time | $19 (1 Mac) / $29 (2 Macs) | Yes | No | No | No | Direct |
| **VoiceInk** | One-time (open source) | $25-40 one-time | Yes | Yes | Yes | Yes | Direct + GitHub |
| **Spokenly** | Free + BYOK | Free | Yes | BYOK | BYOK | Yes (free) | Direct |
| **Aqua Voice** | Freemium + Sub | Free (1K words/mo) / $8/mo | No | Yes | Yes | No | Direct |

### 2.2 Market Rate Summary

- **Going rate for voice-to-text macOS utilities in 2026:** $8-15/month subscription, $20-100 one-time, or $100-250 lifetime
- **Free tiers** are now standard, typically with word/time limits
- **BYOK** is emerging as a differentiator, especially among privacy-conscious and technical users
- **Local-first** (on-device Whisper) is increasingly expected as table stakes
- The market is getting crowded; differentiation matters more than ever

### 2.3 How Competitors Handle API Cost Pass-Through

| Approach | Used by | How it works |
|---|---|---|
| **Bundled in subscription** | Wispr Flow, Aqua Voice | API costs absorbed into monthly fee; usage caps prevent abuse |
| **BYOK** | Spokenly, VoiceInk, Superwhisper (Pro) | User provides their own API key; app makes calls directly |
| **One-time + local only** | SpeakMac, Voibe | No cloud costs; all processing on-device |
| **Tiered usage** | Wispr Flow, Superwhisper | Free tier with word limits; paid tier with higher/unlimited limits |

---

## 3. Monetization Models

### 3.1 BYOK (Bring Your Own Key) -- Free App

**How it works:** App is free. User provides their own OpenAI/Anthropic/Groq API key in Settings. App calls the API directly from the user's machine using their key.

| Pros | Cons |
|---|---|
| Zero ongoing costs for developer | High UX friction: user must create API accounts, generate keys |
| No payment processing needed | Not viable for non-technical users |
| Privacy-friendly: no data touches your servers | Support burden: "why is my API key not working?" |
| Attractive to developers/power users | No revenue unless combined with another model |
| Can compete on being truly free | Hard to build a business on free |
| Avoids Apple's 30% cut entirely | No recurring revenue for sustainability |

**Viability for non-technical users:** Low. Creating an API key requires navigating OpenAI/Anthropic dashboards, setting up billing, copying keys. This is a 5-10 minute process that intimidates most users. Spokenly proves it can work for a niche, but it limits total addressable market.

**Verdict:** Good as a tier, not as the only model.

### 3.2 Subscription with Bundled API Credits

**How it works:** User pays monthly/yearly. Untype proxies API calls through its own backend, absorbing the API cost.

| Pros | Cons |
|---|---|
| Predictable recurring revenue | Requires backend infrastructure for API proxying |
| Smooth UX: works out of the box | API costs can exceed subscription revenue if usage is high |
| Standard model users understand | Need usage metering and rate limiting |
| Can offer free trial easily | Apple takes 30% (15% year 2) if on App Store |
| Scales with user base | Must handle API key management, rate limits, errors |

**Pricing benchmark based on competitors:**
- $8-12/month is the sweet spot
- $80-100/year annual discount
- Free tier: 500-2,000 words/week to let users experience the product

**Usage metering approach:**
- Track words processed per billing period
- Set tier limits (e.g., Free: 1K words/week, Pro: 50K words/month, Unlimited: uncapped)
- Client-side counting with server-side verification
- Alert user at 80% and 100% of limit

**API cost economics (rough estimates):**
- Whisper API: ~$0.006/minute of audio
- GPT-4o-mini for cleanup: ~$0.15/1M input tokens (~$0.0003 per message)
- Claude Haiku for cleanup: ~$0.25/1M input tokens (~$0.0005 per message)
- Average user: ~30 dictations/day x 30 words = ~900 words/day
- Monthly API cost per active user: ~$0.50-2.00
- At $10/month subscription, healthy margin even with Apple's cut

### 3.3 One-Time Purchase + BYOK

**How it works:** User pays once ($25-50) for the app. Cloud features require their own API key. On-device features work without a key.

| Pros | Cons |
|---|---|
| Simple, user-friendly pricing | No recurring revenue |
| On-device features work immediately | Cloud features still have BYOK friction |
| Competitive with VoiceInk, SpeakMac | Hard to fund ongoing development |
| No backend needed | Users expect updates "forever" for one-time purchases |
| No API cost risk for developer | Price pressure: competitors at $19-40 |

**Verdict:** Good for bootstrapping, but limits long-term growth. Works well if Untype's core value is local transcription + AI cleanup.

### 3.4 Freemium (Local-Only Free, Cloud Features Paid)

**How it works:** Free tier uses Apple Speech (on-device, free). Paid tier adds cloud Whisper (better accuracy), LLM cleanup, and advanced features.

| Pros | Cons |
|---|---|
| Large free user base for word-of-mouth | Free users cost nothing (no API calls) |
| Clear value upgrade: accuracy + AI cleanup | Conversion rate typically 2-5% |
| On-device free tier is genuinely useful | Apple Speech accuracy may disappoint, hurting brand |
| Natural upsell moment when user sees AI cleanup quality | Must maintain two code paths |

**Tier structure:**
- **Free:** Apple Speech (on-device), basic dictation, no AI cleanup
- **Pro ($10/mo or $80/yr):** Cloud Whisper, AI text cleanup, custom prompts, priority support
- **BYOK option on free tier:** Power users can bring their own keys for cloud features

### 3.5 Pay-Per-Use (Token-Based Credits)

**How it works:** User buys credit packs (e.g., $5 for 500 dictations). Credits are consumed per use.

| Pros | Cons |
|---|---|
| Fair: pay only for what you use | Complex UX: credit balances, top-ups |
| Low barrier to entry | Unpredictable revenue |
| No subscription fatigue | Users anxious about "spending" credits |
| Aligns cost with value delivered | Requires backend for credit tracking |

**Verdict:** Too complex for a utility app. Works for API platforms, not consumer tools.

---

## 4. Payment Processors

### 4.1 Comparison Table

| Processor | Fee | MoR | Tax Handling | License Mgmt | Best For |
|---|---|---|---|---|---|
| **Paddle** | 5% + $0.50 | Yes | Full global VAT/sales tax | Built-in | Established indie apps |
| **Lemon Squeezy** | 5% + $0.50 | Yes | Full global VAT/sales tax | Built-in | Early-stage, simple setup |
| **Stripe** | 2.9% + $0.30 | No* | You handle it | DIY | High volume, custom needs |
| **Gumroad** | 10% | Yes | Partial | Built-in | Side projects, simple sales |
| **FastSpring** | ~5-8% | Yes | Full | Built-in | Enterprise, B2B |

*Stripe acquired Lemon Squeezy in July 2024; Stripe's own MoR service costs ~7.9% + $0.30.

### 4.2 Merchant of Record (MoR) Explained

A Merchant of Record is the legal entity that sells products to customers. When using an MoR (Paddle, Lemon Squeezy), **they** handle:
- Global sales tax / VAT calculation and remittance
- Payment disputes and chargebacks
- Tax compliance in 100+ jurisdictions
- Invoice generation

Without an MoR (using raw Stripe), **you** handle all of the above. This can cost 10-20+ hours/month in tax compliance alone if selling globally.

### 4.3 Recommendation for Untype

**Lemon Squeezy** is the best starting point for an indie macOS app in 2026:
- 5% + $0.50 per transaction (vs. Apple's 30%)
- Full MoR: handles all global tax compliance
- Simple integration: checkout links, license key validation
- Good developer experience and documentation
- Backed by Stripe (acquired 2024), so long-term stability is reasonable
- Supports one-time purchases, subscriptions, and pay-what-you-want

**Paddle** is the fallback if Lemon Squeezy's future becomes uncertain post-Stripe acquisition.

---

## 5. Tax & Legal Considerations

### 5.1 App Store vs. Direct Distribution

| Aspect | App Store | Direct (with MoR) | Direct (raw Stripe) |
|---|---|---|---|
| Sales tax/VAT | Apple handles everything | MoR handles everything | You handle everything |
| Tax registration | Not required | Not required | Required in many jurisdictions |
| EU VAT | Apple is seller of record | MoR is seller of record | You must register for EU VAT |
| US sales tax | Apple collects/remits | MoR collects/remits | You must track nexus by state |
| Income tax | You report revenue minus Apple's cut | You report revenue minus MoR fees | You report all revenue |
| Legal entity | Not required (individual OK) | Not required (MoR is the entity) | LLC/Corp recommended |

### 5.2 Key Tax Facts

- **UK and EU have zero thresholds** for non-resident sellers of digital goods. Selling one $5 app to a UK customer technically creates a registration requirement.
- **US sales tax** varies by state. Even when Apple collects, revenue counts toward economic nexus thresholds.
- **Using an MoR eliminates almost all tax burden** for the developer. This is the primary reason to use Paddle or Lemon Squeezy over raw Stripe.

### 5.3 Privacy & Legal for AI Features

- Privacy policy is mandatory (both App Store and direct)
- Must disclose: microphone recording, speech-to-text processing, LLM API data sharing
- GDPR compliance if serving EU users (data processing agreements with API providers)
- Consider Terms of Service covering: data retention, API provider terms pass-through, liability limitations

---

## 6. Recommended Strategy

### 6.1 Distribution: Developer ID (Direct) Only -- For Now

**Rationale:**
- The sandbox accessibility limitation is a dealbreaker for Untype's core text insertion feature
- CGEvent.post() works perfectly with Developer ID + user-granted Accessibility permission
- Most successful competitors (Superwhisper, VoiceInk, Spokenly, Voibe) distribute directly
- Notarization provides equivalent security trust signal to users
- No 30% Apple tax on revenue
- Sparkle provides reliable auto-updates

**Action items:**
1. Set up Developer ID Application certificate
2. Configure Hardened Runtime with required entitlements (mic, speech, accessibility, network)
3. Integrate Sparkle for auto-updates
4. Set up notarization in CI/CD pipeline
5. Host app on website with download page

### 6.2 Monetization: Freemium + BYOK Hybrid

**Recommended tier structure:**

| Tier | Price | Features |
|---|---|---|
| **Free** | $0 | Apple Speech (on-device), basic dictation, no AI cleanup, 5 dictations/day |
| **Pro** | $10/month or $79/year | Cloud Whisper, AI text cleanup, unlimited dictation, custom prompts, priority support |
| **BYOK** | $0 (free tier) | Bring your own API keys for cloud features on the free tier; no subscription needed |
| **Lifetime** | $199 one-time | All Pro features, forever. Includes reasonable usage cap (e.g., 100K words/month) |

**Why this model:**

1. **Free tier with on-device transcription** removes all barrier to entry. Users experience the core value (voice-to-text) immediately.

2. **Pro subscription** captures users who want better accuracy (cloud Whisper) and AI cleanup. At $10/month, Untype is competitively priced vs. Wispr Flow ($12-15/mo) and cheaper than Superwhisper ($8.49/mo for less).

3. **BYOK on free tier** captures technical users who won't pay subscriptions but will evangelize the product. This is a growth lever, not a revenue source.

4. **Lifetime option** captures users with subscription fatigue. At $199, it's priced to be profitable (break-even at ~20 months of Pro).

### 6.3 Payment Processing: Lemon Squeezy

- Set up Lemon Squeezy store with products for Pro Monthly, Pro Annual, and Lifetime
- Implement license key validation in the app (Lemon Squeezy provides API for this)
- All tax/VAT handled by Lemon Squeezy as MoR
- Checkout happens in browser; app validates license key

### 6.4 API Cost Economics

At $10/month Pro pricing with Lemon Squeezy (5% + $0.50 fee):

| Item | Amount |
|---|---|
| Revenue per user/month | $10.00 |
| Lemon Squeezy fee | -$1.00 |
| Estimated API cost/user | -$1.50 |
| **Net per user/month** | **$7.50** |
| **Gross margin** | **75%** |

At $79/year:

| Item | Amount |
|---|---|
| Revenue per user/year | $79.00 |
| Lemon Squeezy fee | -$4.45 |
| Estimated API cost/user/year | -$18.00 |
| **Net per user/year** | **$56.55** |
| **Gross margin** | **72%** |

### 6.5 Implementation Priority

1. **Phase 1 (MVP launch):** Free tier (on-device only) + BYOK. Zero infrastructure needed. Validate product-market fit.
2. **Phase 2 (after validation):** Add Pro subscription with Lemon Squeezy. Requires: API proxy backend (can be a simple Cloudflare Worker), usage metering, license validation.
3. **Phase 3 (growth):** Add Lifetime option, referral program, team pricing.
4. **Phase 4 (scale):** Evaluate App Store distribution if Apple resolves sandbox accessibility issues or if market demands it.

### 6.6 Key Risks

| Risk | Mitigation |
|---|---|
| API costs exceed subscription revenue | Usage caps, token-level metering, cheap models (Haiku, GPT-4o-mini) |
| Apple changes notarization requirements | Stay current with Xcode/macOS releases; Sparkle community tracks this |
| Competitors race to bottom on price | Differentiate on UX, not price. Untype's overlay UX is unique. |
| BYOK users never convert to paid | That's fine; they're free growth. Focus conversion on users who try free tier's on-device STT and want better. |
| Lemon Squeezy acquired/sunset by Stripe | Paddle is a drop-in replacement with identical MoR model |

---

## Sources

- [Superwhisper Pricing](https://superwhisper.com/)
- [Wispr Flow Pricing](https://wisprflow.ai/pricing)
- [MacWhisper on Gumroad](https://goodsnooze.gumroad.com/l/macwhisper)
- [AudioPen Prime](https://www.audiopen.ai/prime)
- [Spokenly Pricing](https://spokenly.app/pricing)
- [VoiceInk Review](https://www.voicetypingtools.com/tools/voiceink)
- [Aqua Voice](https://aquavoice.com)
- [Voibe Pricing](https://www.getvoibe.com/)
- [SpeakMac Pricing](https://www.speakmac.app/)
- [Apple App Sandbox Docs](https://developer.apple.com/documentation/xcode/configuring-the-macos-app-sandbox)
- [Apple Accessibility Sandbox Issue (Dev Forums)](https://developer.apple.com/forums/thread/707680)
- [Apple Guideline 5.1.2(i) for AI Apps](https://techcrunch.com/2025/11/13/apples-new-app-review-guidelines-clamp-down-on-apps-sharing-personal-data-with-third-party-ai/)
- [Apple Notarization Docs](https://developer.apple.com/documentation/security/notarizing-macos-software-before-distribution)
- [Sparkle Framework](https://sparkle-project.org/)
- [Stripe vs Paddle vs Lemon Squeezy Comparison](https://appstackbuilder.com/blog/stripe-vs-lemon-squeezy-vs-paddle)
- [Lemon Squeezy (Paddle Alternative)](https://www.lemonsqueezy.com/paddle-alternative)
- [Digital Goods VAT Guide 2026](https://calcix.net/guides/tax/selling-digital-products-globally-tax-guide)
- [Code Signing and Notarization with Sparkle](https://steipete.me/posts/2025/code-signing-and-notarization-sparkle-and-tears)
