# Market sizing — directional TAM table (2026-05)

**Date**: 2026-05-08
**Status**: Directional only. Synthesised from public summaries of paid market-research reports (Fortune Business Insights, Grand View Research, Precedence Research, Mordor Intelligence, Future Market Insights). Numbers are not directly comparable across sources — definitions, inclusions, and methodologies differ.
**Source**: lifted from a co-founder market doc 2026-05-08; repo previously had no TAM data.

---

## Why this exists

Investor decks, gut-checks on category bets, and any "is the market big enough" question need a number. This doc gives a defensible range for each adjacent segment, with the explicit warning that **none of these numbers is Untype's addressable market.**

---

## Directional TAM table

| Segment | Size | Year | CAGR | What it actually measures | Direct relevance to Untype |
|---|---|---|---|---|---|
| Speech-to-text API | $4.66B → $25.28B by 2034 | 2025 | ~20.7% | API revenue (Big Tech + standalone STT vendors) | Low — infra layer, not product layer |
| Speech-to-text API (alt) | $3.8B → $8.57B by 2030 | 2024 | ~14.1% | Same category, more conservative definition | Same as above; range = $3.8B–$4.66B |
| ASR (within conversational AI) | $2.47B → $9.32B by 2030 | 2024 | ~24.8% | ASR as part of broader conversational-AI stack | Low — enterprise/IVR-weighted |
| Transcription market (broad) | $25.18B → $37.59B by 2032 | 2025 | ~5.9% | Includes human transcription services + software | Low — bulked by services, not software |
| AI meeting assistants | $3.47B → $21.48B by 2033 | 2025 | ~25.8% | Otter / Fireflies / Granola category | None — explicit non-target (see `competitive-landscape.md` §6.3) |
| AI meeting assistants (alt) | $1.20B → $6.28B by 2035 | 2025 | ~18.0% | Narrower definition (AI-only, no human review) | Same as above |
| Cloud dictation | $8.86B → $22.23B by 2034 | 2026 | ~12.2% | Cloud dictation solutions (broad) | **Closest analogue** — but heavily healthcare-weighted |
| Smart dictation systems | $5.5B → $18.8B by 2035 | 2025 | ~13.1% | Smart dictation (medical-heavy) | Medium — dilution from healthcare |
| Medical transcription | $80.41B → $108.5B by 2031 | 2025 | ~5.1% | Vertical, services-heavy | None — explicit non-target |
| Legal transcription | $2.56B → $4.99B by 2035 | 2025 | ~6.9% | Vertical, niche | None — explicit non-target |
| Speech analytics | $4.94B → $15.31B by 2034 | 2025 | ~13.2% | Call-center / contact-center analytics | None — explicit non-target |

---

## Why these numbers don't equal Untype's addressable market

Headline TAM numbers mislead in three directions for a tool like Untype:

1. **Vertical bulk**. The $80B "medical transcription" and $25B "transcription market" headlines are dominated by services revenue (humans typing) and vertical compliance work that Untype explicitly does not enter (`competitive-landscape.md` §6.3).

2. **Infra vs. product**. The $4.66B "speech-to-text API" market is what Big Tech / Deepgram / AssemblyAI sell to *other product companies* (including potentially Untype itself as a buyer). Untype competes downstream of this layer, not within it.

3. **Different unit of demand**. Cloud dictation sizing assumes per-seat enterprise licensing. Untype is consumer/prosumer macOS, $7–9/mo individual. The pricing model maps to a different slice.

**Untype's actual addressable market is the intersection of**:
- Consumer/prosumer dictation users (slice of "cloud dictation" / "smart dictation systems" — not the whole)
- macOS-only users (Apple holds ~10–15% of global desktop OS share; higher among target segments — knowledge workers, founders, designers)
- C2 bilingual professionals as primary ICP (subset of the above; no public sizing exists)

A defensible v1 estimate would require:
1. macOS user base globally (~250M devices, plausibly ~100M+ active knowledge-worker users — Apple does not publish this precisely)
2. % who would pay $7–9/mo for an AI dictation tool (unknown — Wispr Flow's user count is not public; getlatka.com claims $10M ARR with 50-person team but conversion rates are not disclosed)
3. % who fit the bilingual L1→L2 profile in step 2

This is **not** doable from public data. The honest answer to "how big is your TAM" is: *the dictation category is multi-billion-dollar and growing 12–25% annually depending on slice; Untype's serviceable share is unknown and will be sized empirically post-launch.*

---

## When this doc is useful

- Investor or partner conversations where a market-size number is required as a sanity check, not a forecast
- Internal arguments about whether to even continue ("is this category big enough" — yes, demonstrably)
- Justification for *not* expanding into adjacent verticals (medical, legal, meetings) — those are someone else's billion-dollar games

## When this doc is misleading

- Sizing how big Untype can get
- Choosing pricing
- Forecasting revenue

For those, use behavioural data from `validation-metrics-v1.md` once it exists.

---

## Sources

Public summaries (paid reports themselves not accessible):
- Fortune Business Insights (speech-to-text, AI meeting assistants)
- Grand View Research (transcription market)
- Precedence Research (smart dictation systems, speech analytics)
- Mordor Intelligence (ASR, conversational AI)
- Future Market Insights (medical transcription)
- Various investor-facing aggregators (Statista, MarketsandMarkets summaries)

**Caveat**: paid-report summaries published online are typically marketing for the underlying report. Numbers may be inflated to make the report sound consequential. Treat any single number as ±30% directional.
