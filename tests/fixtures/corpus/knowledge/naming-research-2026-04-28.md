<!-- prose-check: skip bold-colon-opener -->
# Renaming Untype: Naming Discovery & State

## TL;DR: Executive Summary

**Goal**: pick a new name for Untype (macOS voice-to-text overlay) with a cheap (<$30/yr) available domain and no App Store / GitHub / trademark conflict in voice/productivity space.

**Scope of investigation**: 158 candidate names checked across 13 TLDs (`.app`, `.com`, `.io`, `.me`, `.eu`, `.club`, `.world`, `.pro`, `.win`, `.art`, `.cloud`, `.tech`, `.today`) plus targeted domain hacks (`vi.be`, `ya.pe`, etc.) plus compound `.com` forms (`get<n>.com`, `<n>app.com`). Five expansion rounds of name angles + a sixth round on the user's bonus picks. Due diligence (GitHub user/repo + USPTO screening) on the user's three picks: Untype, Voq, Voxgrab.

**Headline conclusions**:
1. **Every short English word is gone** on every common TLD. Same for short coined letter-strings (3 letters), Greek mythology names, and most foreign-language speech words.
2. **The `.com` market is fully squatted** for short single words; cybersquatters even own coined niche letter-strings.
3. **The user's original shortlist (Vibe, Yap, Riff, Vox)** is universally shut out, every TLD checked is taken; even domain hacks (`vi.be`) are squatted. **Voq** has the best path within the shortlist via `voqapp.com` or `voq.cloud`, but the GitHub voice-AI namespace (`voquill` 884★, `voqal` 191★) is already crowded.
4. **The available zone** is invented multi-syllable coinages (Vorato, Voxgrab, Voxbeam, Saytak, Saypod, Vaark, Yapra), descriptive compounds (Mikepad, Untype, Notype, Micpad, Micin), or onomatopoeia (Thwap).

**Top three after due diligence**:
- 🟢 **Voxgrab**, `.app` + `.io` + `.me` + all 9 extended TLDs FREE; zero App Store, GitHub repo, or USPTO collision; GitHub user handle FREE. Cleanest pick by all measures.
- 🟢 **Untype**, `.me` + all extended TLDs free; multiple clean compound `.com`s; zero voice/productivity collision (TS-namespace overlap is irrelevant). Highest semantic punch.
- 🟡 **Voq**, domain story is fine but voice-AI GitHub namespace is poisoned by two established projects in the exact product space.

**User-added bonus picks** (round 6) that also pass screening: **Micpad** and **Micin**, both have `.app` + `.io` + `.me` FREE with zero App Store collision.

## What this plan executes (on approval)

User asked: "Save all the options + checks to a document, AND create scripts so I can re-run name checks and apply the rename when I pick a winner."

On approval, I will:

### 1. Save the research document
Copy this document to `Untype/knowledge/naming-research-2026-04-28.md` (alongside `code-health-audit-*.md`, `ux-audit-*.md`, etc.).

### 2. Create `bin/check-name.sh`, name-availability checker
Reproduces the methodology used in this exploration. Single-shot CLI:
```
bin/check-name.sh <name>
```
Output: a one-page Markdown report with sections,
- **Domain availability**: `.app` (RDAP via `pubapi.registry.google`), `.com`/`.io`/`.me`/`.eu`/`.be` (whois with authoritative servers), 9 extended TLDs (`.club`, `.world`, `.pro`, `.win`, `.art`, `.cloud`, `.tech`, `.today` via RDAP)
- **App Store**: iTunes Search API for software/macSoftware in US, flagging exact-prefix matches and Productivity/Voice/Dictation collisions
- **GitHub**: user-handle availability (api.github.com/users/X) and repo search (api.github.com/search/repositories)
- **Verification commands** for the user to run manually: USPTO TESS link, X/Instagram URLs

Fail-soft: if any single check errors, the rest of the report still prints with that section showing `?`. Exit 0 always (the report itself communicates findings).

### 3. Create `bin/rename-project.sh`, project-wide renamer
Renames "Untype" to "<NewName>" across the repo. Must be:
- **Dry-run by default.** Prints the diff that would be applied. Only applies on `--apply` flag.
- **Case-aware.** Handles `Untype` (PascalCase), `untype` (lowercase), `BOUNCE` (uppercase).
- **Scoped to tracked files.** Uses `git ls-files` so untracked build artifacts and `Build/` are skipped.
- **Idempotent.** Safe to re-run.
- **No auto-commit.** The user reviews the diff and commits manually with `/commit`.

Files it touches:
- `Package.swift`, product `name` + target `name` and `path` references
- `Info.plist` (`Untype/Info.plist` if present, plus any source-controlled `Info.plist`s), `CFBundleName`, `CFBundleDisplayName`, `CFBundleIdentifier`
- `bin/build.sh`, signing identity (`Untype Dev` to `<NewName> Dev`), output paths, app-bundle name
- `CLAUDE.md`, all "Untype" references in docs and command examples
- `README.md` if present
- `knowledge/**.md`, `sessions/**.md`, historical references stay untouched (history is history); only **current** ones rewrite (heuristic: today's session log)
- Source files that reference the literal string `"Untype"` (e.g., process names, log identifiers, debug log path `/tmp/untype_debug.log`)
- `.entitlements`, `.xcconfig` files if present
- Any directory named `Untype/` itself, `git mv` to `<NewName>/`

Files it explicitly does NOT touch:
- `Build/` (regenerated by build.sh)
- `.git/`, `.swiftpm/`, `.build/`
- Binary files (`.o`, `.swiftdeps`, etc.)
- Anything ignored by `.gitignore`

After the script: prints a checklist of **manual steps** (one-time TCC re-grant for the new bundle ID, signing-cert renaming, updating GitHub repo name, securing social handles).

### 4. No code changes from the rename itself
The scripts are tools. The user runs them when ready; this plan doesn't actually run a rename.

## Context

Untype (the macOS voice-to-text overlay) needs a name that:
1. Hints at voice / speech / quick capture (current "Untype" is generic and wrong-signal)
2. Is easy to digest, remember, and pronounce verbally
3. Has an available domain in the **<$30/yr** budget tier (cheap-only, `.com`, `.app`, `.io`-edge, `.me`, `.dev`)
4. Doesn't collide with an existing macOS/iOS app in the productivity / voice / dictation namespace

The user's initial shortlist was **Vibe, Yap, Rif/Riff, Vox/Voq, Untype**. They asked to expand the list and gather *state* (don't knock anything out for collisions or domain unavailability, just record).

This document is a state-gathering pass, not a final pick.

## Methodology

For each of **158 candidate names** (across 6 expansion rounds + user's bonus picks) I checked:
- `.app` / `.com` / `.club` / `.world` / `.pro` / `.win` / `.art` / `.cloud` / `.tech` / `.today` via RDAP (most reliable)
- `.io` / `.me` / `.eu` / `.be` via authoritative whois
- App Store collision via iTunes Search API (US, software + macSoftware, top 5 results)
- Compound `.com` forms (`get<n>.com`, `try<n>.com`, `<n>app.com`, `<n>hq.com`) for the user's shortlist
- Targeted **domain hacks**, names that span the dot, e.g. `vi.be`, `ya.pe`, `vy.be`

Excluded from this pass: `.xyz`, `.dev`, `.fyi`, `.so` (whois quirks); `.es` (whois requires registration). All cheap (~$15–25/yr) and worth a manual recheck per name once the shortlist narrows.

### Domain-hack findings (TL;DR, they're all gone)

| Hack | State |
|---|---|
| `vi.be` (vibe + Belgium) | ❌ TAKEN (Combell registrar) |
| `vy.be` (vybe + Belgium) | ❌ TAKEN |
| `ya.pe` (yape + Peru) | ❌ TAKEN (Peruvian payment app Yape uses this) |
| `rif.fr` (rif + France) | ❌ TAKEN |
| `voq.eu` | ❌ TAKEN |
| `untype.eu` | ✅ FREE |
| `vaark.eu` | ✅ FREE |
| `yapra.eu` | ✅ FREE |

The clever-domain-hack route doesn't unlock anything new for the user's shortlist.

## Master availability table

`✅` = appears unregistered. `❌` = registered. `⚠️` flag = closest App Store result is in voice / dictation / productivity / utilities (= elevated brand-confusion risk).

### User's shortlist

| Name | .app | .com | .io | .me | Closest App Store match (genre) |
|---|---|---|---|---|---|
| **vibe** | ❌ | ❌ | ❌ | ❌ | Vibe - Make New Friends [Lifestyle] |
| **yap** | ❌ | ❌ | ❌ | ❌ | yap: dream astrology journal [Lifestyle], **but** "Yap - AI Voice Memos" by Yap Labs LLC also exists in Productivity ⚠️ |
| **rif** | ❌ | ❌ | ❌ | ❌ |, (no exact-prefix match) |
| **riff** | ❌ | ❌ | ❌ | ❌ | Riff - Fast AI Photo Edits [Photo & Video] |
| **vox** | ❌ | ❌ | ❌ | ❌ | VOX Cinemas App [Entertainment] |
| **voq** | ❌ | ❌ | ❌ | ❌ | nVoq Wireless Microphone [Business] ⚠️ (medical-dictation co.) |
| **untype** | ❌ | ❌ | ❌ | ✅ |, (no exact-prefix match) |

### Speech-action verbs

| Name | .app | .com | .io | .me | Closest App Store match |
|---|---|---|---|---|---|
| blab | ❌ | ❌ | ❌ | ❌ |, |
| blurt | ❌ | ❌ | ❌ | ✅ | Blurt [Utilities] ⚠️ + 3 "Blurting Study" apps |
| babble | ❌ | ❌ | ❌ | ❌ |, |
| chirp | ❌ | ❌ | ❌ | ❌ | Chirp Audiobooks [Book] ⚠️ |
| holler | ❌ | ❌ | ❌ | ❌ | Holler [Business] |
| mutter | ❌ | ❌ | ❌ | ❌ |, |
| murmur | ❌ | ❌ | ❌ | ❌ | Murmur [Utilities] ⚠️ |
| quip | ❌ | ❌ | ❌ | ❌ | quip: Oral Care |
| spiel | ❌ | ❌ | ❌ | ❌ |, |
| utter | ❌ | ❌ | ❌ | ❌ | utter - Dictation, Voice Notes [Productivity] ⚠️ **DIRECT competitor** |
| yelp | ❌ | ❌ | ❌ | ❌ | Yelp [Food & Drink] |

### Voice metaphors / coined

| Name | .app | .com | .io | .me | Closest App Store match |
|---|---|---|---|---|---|
| echo | ❌ | ❌ | ❌ | ❌ | Echo-Group Voice Chat ⚠️ |
| hush | ❌ | ❌ | ❌ | ❌ | Hush – Express Freely |
| lingo | ❌ | ❌ | ❌ | ❌ | Lingo by Abbott [Health] |
| loqui | ❌ | ❌ | ❌ | ❌ | LOQUI - Order Now |
| sayd | ❌ | ❌ | ✅ | ❌ |, |
| speyk | ✅ | ❌ | ✅ | ✅ |, |
| tongue | ✅ | ❌ | ❌ | ❌ | Tongue - practice pronouncing |
| vaark | ✅ | ❌ | ❌ | ✅ |, |
| voce | ❌ | ❌ | ❌ | ❌ |, |
| voxa | ❌ | ❌ | ❌ | ❌ | Voxa: Audiobooks ⚠️ |
| voxie | ❌ | ❌ | ❌ | ❌ | Voxie Message Hub |
| vyb | ❌ | ❌ | ❌ | ❌ | VyB Capital |
| vyce | ❌ | ❌ | ❌ | ❌ | Vyce [Productivity] ⚠️ **DIRECT** |
| yapra | ✅ | ❌ | ✅ | ✅ |, |

### Speed / capture / mac-app-aesthetic

| Name | .app | .com | .io | .me | Closest App Store match |
|---|---|---|---|---|---|
| arc | ❌ | ❌ | ❌ | ❌ | Arc Search [Utilities] ⚠️ |
| beam | ❌ | ❌ | ❌ | ❌ | Beam Tanning |
| blip | ❌ | ❌ | ❌ | ❌ | Blip: Send Files [Utilities] ⚠️ |
| bolt | ❌ | ❌ | ❌ | ❌ | Bolt: Request a Ride |
| chime | ❌ | ❌ | ❌ | ❌ |, |
| click | ❌ | ❌ | ❌ | ❌ | Click SuperApp |
| ding | ❌ | ❌ | ✅ | ❌ | Ding Top-up [Utilities] ⚠️ |
| dink | ❌ | ❌ | ❌ | ❌ | DINK Social |
| drift | ❌ | ❌ | ❌ | ✅ |, |
| drop | ❌ | ❌ | ❌ | ❌ | drop - Audio Recorder [Music] |
| ember | ❌ | ❌ | ❌ | ❌ | Ember |
| flick | ❌ | ❌ | ❌ | ❌ | Flick: Rate Movies |
| flux | ❌ | ❌ | ❌ | ❌ | Flux Kontext [Graphics] |
| glide | ❌ | ❌ | ❌ | ❌ | Glide [Productivity] ⚠️ |
| ping | ❌ | ❌ | ❌ | ❌ | Ping - network utility ⚠️ |
| pulse | ❌ | ❌ | ❌ | ❌ | Pulse for Booking |
| ripple | ❌ | ❌ | ❌ | ❌ | Ripple: Video Community |
| snap | ❌ | ❌ | ? | ❌ | Snap Finance |
| snip | ❌ | ❌ | ❌ | ❌ |, |
| spark | ❌ | ❌ | ✅ | ❌ | Spark Driver |
| surf | ❌ | ❌ | ❌ | ❌ | Surf Dating |
| whoosh | ❌ | ❌ | ❌ | ❌ | Whoosh Member |
| zap | ❌ | ❌ | ❌ | ❌ | Zap Surveys |

### Inversion / capture / explicit

| Name | .app | .com | .io | .me | Closest App Store match |
|---|---|---|---|---|---|
| brain | ❌ | ❌ | ❌ | ❌ | Brain Test |
| braindump | ❌ | ❌ | ❌ | ❌ | BrainDump: Voice Tasks [Productivity] ⚠️ **DIRECT** |
| dict | ❌ | ❌ | ❌ | ❌ | Dict Plus |
| dump | ❌ | ❌ | ✅ | ❌ | DUMP - Sell Your Books |
| jot | ❌ | ❌ | ✅ | ❌ | Jot - Instant Brain Dump [Productivity] ⚠️ **DIRECT** |
| keyless | ❌ | ❌ | ❌ | ❌ | Keyless App ⚠️ |
| mute | ❌ | ❌ | ❌ | ❌ | Mute Video ⚠️ |
| notype | ❌ | ❌ | ✅ | ✅ |, |
| parlay | ❌ | ❌ | ❌ | ❌ |, |
| scribe | ❌ | ❌ | ❌ | ❌ | Scribe - Voice To Text Note AI [Productivity] ⚠️ **DIRECT competitor** |
| steno | ❌ | ❌ | ❌ | ❌ | Steno Lingo |
| talkie | ❌ | ❌ | ❌ | ❌ | Talkie Lab |
| talkr | ❌ | ❌ | ❌ | ❌ | Talkr [Entertainment] |
| talky | ❌ | ❌ | ✅ | ✅ | Talky - Walkie Talkie ⚠️ |

## Round-2 expansion, fresh angles

User asked for a fresh batch with different angles. Added 30 names across animal-speech metaphors, Sanskrit/Japanese roots, two-syllable invented compounds, vibe-adjacent variants, and unchecked onomatopoeia.

| Name | .app | .com | .io | .me | Closest App Store match | Origin |
|---|---|---|---|---|---|---|
| mynah | ❌ | ❌ | ❌ | ✅ |, | Mynah bird (mimics human speech) |
| parrot | ❌ | ❌ | ❌ | ❌ | Parrot – Learn Spanish | animal/speech |
| canary | ❌ | ❌ | ❌ | ❌ | Canary - Smart Home Security | animal/voice |
| starling | ❌ | ❌ | ❌ | ❌ | Starling - Mobile Banking | animal/voice |
| nada | ❌ | ❌ | ❌ | ❌ | NADA – Official | Sanskrit "sound" |
| vaak | ❌ | ❌ | ❌ | ✅ | Vaak [Education] | Sanskrit "speech" |
| **shabda** | ✅ | ❌ | ✅ | ❌ | Shabda Paheli (Nepali game) | Sanskrit "sound/word" |
| koe | ❌ | ❌ | ❌ | ❌ | KOE Mobile | Japanese "voice" |
| oto | ❌ | ❌ | ❌ | ❌ | OtO Lawn ⚠️ | Japanese "sound" |
| kotoba | ❌ | ❌ | ❌ | ❌ | Kotoba - Voice Translation [Reference] ⚠️ | Japanese "word" |
| voxify | ❌ | ❌ | ❌ | ❌ | Voxify Nuvo AI [Productivity] ⚠️ | invented |
| **saytak** | ✅ | ❌ | ✅ | ✅ |, | invented (say + tak) |
| **mikepad** | ✅ | ❌ | ✅ | ✅ |, | descriptive (mic + pad) |
| voxnote | ❌ | ❌ | ❌ | ❌ | Voxnote AI Meeting [Utilities] ⚠️ | invented |
| **saypod** | ✅ | ❌ | ✅ | ✅ |, | invented (say + pod) |
| voxlet | ❌ | ❌ | ✅ | ✅ |, | invented diminutive |
| talktype | ❌ | ❌ | ❌ | ✅ | TalkType [Productivity] ⚠️ **DIRECT** | descriptive |
| speakr | ❌ | ❌ | ❌ | ❌ | Speakr - Charisma | invented |
| vibz | ❌ | ❌ | ❌ | ❌ | Vibz: Find Your Tribe | vibe-adjacent |
| vyba | ❌ | ❌ | ❌ | ✅ | VYBA Captain | vibe-adjacent |
| vyber | ❌ | ❌ | ❌ | ❌ |, | vibe-adjacent |
| plop | ❌ | ❌ | ❌ | ❌ | plop - poop tracker | onomatopoeia |
| bop | ❌ | ❌ | ❌ | ❌ | Bop - Better Music | onomatopoeia |
| ditty | ❌ | ❌ | ❌ | ❌ |, | "a short tune" |
| wham | ❌ | ❌ | ❌ | ❌ | WHAM WX | onomatopoeia |
| **thwap** | ✅ | ❌ | ✅ | ✅ |, (0 results in Store!) | onomatopoeia |
| clink | ❌ | ❌ | ❌ | ❌ | Clink [Lifestyle] | onomatopoeia |

## Extended-TLD sweep (`.eu`, `.club`, `.world`, `.pro`, `.win`, `.art`, `.cloud`, `.tech`, `.today`)

Cheap-tier alternative TLDs ($10–25/yr). Sweep covered the user's shortlist + top contenders:

| Name | .eu | .club | .world | .pro | .win | .art | .cloud | .tech | .today |
|---|---|---|---|---|---|---|---|---|---|
| **vibe** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| yap | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ❌ | ❌ | ❌ |
| rif | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| **riff** | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ | ❌ |
| vox | ❌ | ❌ | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ❌ |
| **voq** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **untype** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **vaark** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **yapra** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| speyk | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| sayd | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| vyb | ❌ | ❌ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| mutter | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ |
| spiel | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ✅ | ✅ |
| **notype** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **saytak** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **mikepad** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **saypod** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **voxlet** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **thwap** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| mynah | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| vyba | ❌ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| talktype | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |

**Critical observation: Vibe and Riff are completely shut out.** Every common TLD, short and extended, is already taken on both. To use Vibe or Riff you'd need premium reseller pricing on `.com` (5-figure aftermarket) or accept an awkward compound like `tryviberhq.com`. Outside the `<$30/yr` budget.

**`Voq`, `Untype`, `Vaark`, `Yapra`, `Notype`, `Saytak`, `Mikepad`, `Saypod`, `Voxlet`, `Thwap` all have 8–9 of 9 extended TLDs free.**

## Round-3 expansion: Romance/Latin, foreign-language speech, invented multi-syllable, sound-shape

User asked for another fresh angle. Added 25 names: Italian/Latin/Spanish speech roots (`dicto`, `dire`, `parli`, `habla`, `charla`, `sermo`), foreign-language speech words (`bolo` Hindi, `snakk` Norwegian, `tala` Swedish, `baat` Hindi, `prata` Swedish), invented multi-syllable brands (`vorato`, `voxara`, `voxon`, `voxily`, `voxbit`), three-letter coined (`vyq`, `vyr`, `vexo`), tech-modern (`boxy`, `boxr`, `brio`, `tonex`).

| Name | .app | .com | .io | .me | Closest App Store match | Origin |
|---|---|---|---|---|---|---|
| dicto | ❌ | ❌ | ❌ | ✅ | dicto: Read books in Russian | Latin "I say" |
| **vorato** | ✅ | ❌ | ✅ | ✅ |, | invented (Italian-feel) |
| voxara | ❌ | ❌ | ❌ | ✅ |, | invented |
| voxon | ❌ | ❌ | ❌ | ✅ |, | invented |
| voxily | ✅ | ❌ | ✅ | ✅ | Voxily [Lifestyle] ⚠️ exact name | invented |
| bolo | ❌ | ❌ | ❌ | ❌ | Bolo [Productivity] ⚠️ **DIRECT** | Hindi "speak" |
| snakk | ❌ | ❌ | ❌ | ❌ | Snakk: Food Delivery | Norwegian "talk" |
| tala | ❌ | ❌ | ❌ | ❌ | Tala [Lifestyle] | Swedish "talk" |
| baat | ❌ | ❌ | ❌ | ❌ | Baat Live | Hindi "talk" |
| voxbox | ❌ | ❌ | ❌ | ❌ | VoxBox-AI Text to Speech [Utilities] ⚠️ | descriptive |
| **saypal** | ❌ | ❌ | ✅ | ✅ |, | invented (say + pal) |
| **voxbit** | ❌ | ❌ | ❌ | ✅ | Voxbit [Lifestyle] | invented |
| dire | ❌ | ❌ | ❌ | ❌ |, | Italian/French "say" |
| parli | ❌ | ❌ | ❌ | ❌ |, | Italian "you speak" |
| habla | ❌ | ❌ | ❌ | ❌ | Habla: Speak English With AI [Education] ⚠️ | Spanish "speaks" |
| charla | ❌ | ❌ | ❌ | ❌ | Charla Live Chat [Business] ⚠️ | Spanish "chat" |
| sermo | ❌ | ❌ | ❌ | ❌ | Sermo: Physician Network [Medical] | Latin "speech" |
| prata | ❌ | ❌ | ❌ | ✅ | Prata de 15 Reais | Swedish "talk" |
| boxy | ❌ | ❌ | ❌ | ❌ | Boxy [Travel] | tech-modern |
| boxr | ❌ | ❌ | ❌ | ✅ | BOXR GYM | tech-modern |
| brio | ❌ | ❌ | ❌ | ❌ | BRIO World - Railway | Italian "vigor" |
| tonex | ❌ | ❌ | ❌ | ✅ | TONEX Control [Music] | invented |
| vexo | ❌ | ❌ | ❌ | ❌ | Vexo: AI Money Tracker | invented |
| **vyq** | ✅ | ❌ | ❌ | ❌ |, | 3-letter coined |
| vyr | ❌ | ❌ | ❌ | ❌ | VYR Track [Utilities] | 3-letter coined |

### Extended-TLD sweep, round 3 picks

| Name | .eu | .club | .world | .pro | .win | .art | .cloud | .tech | .today |
|---|---|---|---|---|---|---|---|---|---|
| **vorato** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **vyq** | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ |
| **saypal** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **voxbit** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| voxara | ❌ | ✅ | ✅ | ❌ | ✅ | ❌ | ❌ | ❌ | ✅ |
| voxon | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ✅ | ✅ |
| voxily | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **vorat** (variant of vorato) | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Round-3 winners:**
- **Vorato**, `.app` + `.io` + `.me` + all 9 extended TLDs FREE, zero App Store collision. Italian-feeling coined word. **Cleanest name in the entire dataset.**
- **Saypal**, `.io` + `.me` + all 9 extended FREE, no App Store collision. "Say + pal" semantic. (`.app` taken.)
- **Voxbit**, `.me` + all 9 extended FREE, low-risk App Store match. Tech-modern feel.
- **Vyq**, 3-letter ultra-brandable, `.app` + 7/9 extended free, zero App Store collision. Visually distinctive (Q-letter rare).
- **Vorat** (variant of Vorato, no trailing 'o'), same availability profile as Vorato, slightly punchier.

## Round-4 expansion, 3-letter coined, Greek mythology, action+device portmanteaus, sci-fi

User asked for one more angle. Added 25 names: 3-letter coined letter-strings (`ryx`, `kix`, `jox`, `byx`, `nox`, `dox`, `fyx`), Greek/Roman mythology speech-related (`calliope`, `iris`, `hermes`, `oracle`, `sybil`, `mercury`), action+device portmanteaus (`snapsay`, `voxgrab`, `saysnap`, `voxbeam`, `voxhive`, `voxgo`, `voxnow`), sci-fi/poetic (`glitch`, `vapor`, `prism`, `axiom`), word+ly (`voxly`).

| Name | .app | .com | .io | .me | Closest App Store match | Notes |
|---|---|---|---|---|---|---|
| ryx, kix, jox, byx, nox, dox, fyx | ❌ | ❌ | ❌ | ❌ | (mostly Business/Sports/Games matches) | All 3-letter coined are squatted. Skip this angle. |
| calliope | ❌ | ❌ | ❌ | ❌ | Calliope Sim [Music] | Greek muse of voice, gone. |
| iris, hermes, oracle, sybil, mercury | ❌ | ❌ | ❌ | ❌ | (massive existing usage) | Mythology fully squatted. Skip. |
| **voxgrab** | ✅ | ❌ | ✅ | ✅ |, | "vox + grab", capture voice. Strong. |
| **voxbeam** | ✅ | ❌ | ✅ | ✅ |, | "vox + beam", transmit voice. Strong. |
| voxnow | ✅ | ❌ | ❌ | ✅ |, | Solid; .me free, .io taken |
| voxhive | ❌ | ❌ | ❌ | ❌ |, | .app taken |
| voxgo | ❌ | ❌ | ✅ | ✅ | VOXGO [Entertainment] | .app taken |
| voxnow | ✅ | ❌ | ❌ | ✅ |, | (dup) |
| snapsay | ❌ | ❌ | ✅ | ✅ |, | .app taken |
| saysnap | ❌ | ❌ | ✅ | ✅ | SaySnap [Photo & Video] | exact-name collision |
| glitch, vapor, prism | ❌ | ❌ | mostly ❌ | ❌ |, | sci-fi angle: all squatted |
| axiom | ❌ | ❌ | ❌ | ❌ | Axiom Pro [Productivity] ⚠️ | DIRECT productivity collision |
| voxly | ❌ | ❌ | ❌ | ✅ | Voxly: Color By Number [Entertainment] | exact-name collision |

### Extended-TLD sweep, round 4 winners

| Name | .eu | .club | .world | .pro | .win | .art | .cloud | .tech | .today |
|---|---|---|---|---|---|---|---|---|---|
| **voxgrab** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **voxbeam** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| voxnow | ❌ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ |
| snapsay | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| voxgo | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| voxhive | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |

**Round-4 winners:**
- **Voxgrab**, `.app` + `.io` + `.me` + ALL 9 extended TLDs FREE, no App Store collision. Semantic: "voice capture." On-message and on-brand.
- **Voxbeam**, `.app` + `.io` + `.me` + ALL 9 extended TLDs FREE, no App Store collision. Semantic: "voice transmission/instant." On-message and modern-feel.

**Confirmed dead angles after round 4:**
- 3-letter coined letter-strings, universally squatted on common TLDs.
- Greek/Roman mythology names, all squatted (massive cultural usage).
- Sci-fi/poetic single words, all squatted.

## Round-5 expansion, modern-tech short coined, single-syllable English, cultural speech words

User asked for one more angle. Added 25 names: tech-startup short coined (`mulo`, `lume`, `tovo`, `helo`, `wisp`, `glee`, `quay`, `spry`), modern-mac single syllables (`bloom`, `clip`, `glow`, `hum`, `coo`, `caw`, `hoot`, `sift`), CVCV coined (`nipa`, `mola`, `ravi`, `voze`, `sune`), cultural speech words (`olelo` Hawaiian, `mal` Korean, `sabi` Filipino, `hula` Hawaiian).

**Result: essentially a null harvest.** Of 25 names checked, only `voze.me` and `tovo.me` came up FREE on `.me`, and only `voze.app` came up FREE on `.app`. Both have direct App Store collisions:
- `voze` to "Voze [Business]" (exact-name match)
- `tovo` to "TOVO SKN" (Travel)

Other notable collisions in round 5:
- `helo` to "Helo - Discover,Share & Trends" (Reference)
- `wisp` to "Wisp: Online Healthcare" (Medical)
- `bloom` to "Bloom: Learn to Invest" (Finance)
- `glow` to "Glow Ovulation & Period App"
- `sabi` to "Sabi - Bookkeeping" (Productivity)
- `olelo` to "Olelo - Hawaiian Dictionary"

**Round 5 confirms diminishing returns.** The pattern across 150 names checked is fully established:
- Every short English word: gone everywhere
- Every short coined letter-string: gone on common TLDs
- Every common cultural term: gone (mythology, foreign-language, single-syllable English)
- The available names are: invented multi-syllable coinages (Vorato, Voxgrab, Voxbeam, Saytak, Saypod, Vaark, Yapra), descriptive compounds (Mikepad, Untype, Notype), or onomatopoeia (Thwap)

Further expansion rounds will mostly surface more of the same available patterns. **Recommendation: narrow now and do due diligence on the existing leader list.**

## User's bonus candidates (round 6)

User added 8 of their own action+preposition compounds: `micpad`, `onmic`, `dropon`, `jumpon`, `talkon`, `talkin`, `dropin`, `micin`.

| Name | .app | .com | .io | .me | App Store closest match |
|---|---|---|---|---|---|
| **micpad** | ✅ | ❌ | ✅ | ✅ |, |
| **micin** | ✅ | ❌ | ✅ | ✅ |, |
| onmic | ✅ | ❌ | ✅ | ✅ | OnMic: Audiobook & Podcast [Book] |
| dropon | ✅ | ❌ | ❌ | ✅ | Dropon Mobile [Navigation] |
| jumpon | ✅ | ❌ | ❌ | ❌ | jumpON [Sports] |
| talkon | ✅ | ❌ | ❌ | ❌ | TalkOn AI [Education] ⚠️ DIRECT (AI language tutor) |
| talkin | ❌ | ❌ | ❌ | ❌ | Talkin [Social Networking] |
| dropin | ❌ | ❌ | ❌ | ❌ | DropIn 3D [Games] |

**Round-6 winners**: Micpad and Micin both have `.app` + `.io` + `.me` FREE with zero App Store collision. Both are also clean variants of the earlier Mikepad theme.

## Due Diligence: Untype, Voq, Voxgrab

User picked these three from the leader list to validate.

### GitHub presence

| Name | User-handle | Repo competitors |
|---|---|---|
| **Untype** | ❌ TAKEN (`github.com/untype`) | 196 repos, but none in voice space, top hits are TypeScript-related (`unjs/untyped` 520★, `total-typescript/untypeable` 378★). Different domain, TS namespace overlap is irrelevant to a voice-to-text product. |
| **Voq** | ❌ TAKEN (`github.com/voq`) | 364 repos, **including two big direct competitors**: `voquill/voquill` (884★, "Open source voice dictation technology"), `voqal/voqal` (191★, "Voice native AI agent"). **Voice space is already crowded with voq-prefix projects.** ⚠️ |
| **Voxgrab** | ✅ FREE (`github.com/voxgrab`) | 1 repo total: `nikolajlauridsen/VoxGrab` (10★, bulk subtitle downloader). Different category, low profile. **Cleanest by far.** |

### USPTO trademark surface (preliminary, via Google site:uspto.gov)

| Name | Hits |
|---|---|
| Untype | None surfaced |
| Voq | None surfaced |
| Voxgrab | None surfaced |

**Caveat**: Google site-search of USPTO data is a screening signal only, not a definitive search. For legal-grade certainty, run a TESS query at <https://tmsearch.uspto.gov/> in classes 9 (downloadable software) and 42 (SaaS). All three names appear clear at the screening level.

### Social handles (X/Twitter, Instagram)

HTTP-code probing post-Musk policy changes is unreliable, both X and Instagram return 200 even for non-existent handles. **Manual verification recommended** at:
- `x.com/<name>` (look for "This account doesn't exist")
- `instagram.com/<name>` (look for the "Sorry, this page isn't available" message)

### Verdict

| Name | Domain | App Store | GitHub | USPTO (screening) | Overall |
|---|---|---|---|---|---|
| **Voxgrab** | ✅ Clean across `.app`+`.io`+`.me`+all 9 extended | ✅ No collision | ✅ User handle FREE; one tiny repo in different category | ✅ Clear | 🟢 **GREEN, strongest candidate** |
| **Untype** | ✅ `.me` + all extended free; lots of strong compound `.com`s | ✅ No collision | 🟡 User handle taken; TypeScript-namespace overlap (irrelevant to your space) | ✅ Clear | 🟢 GREEN, close behind |
| **Voq** | 🟡 8/9 extended free; `voqapp.com`/`voq.cloud` available; `.app` taken | ✅ No exact collision but nVoq trademark concern | 🔴 **Two big voice-space projects already use the prefix** (`voquill` 884★, `voqal` 191★) | ✅ Clear directly but neighbors are crowded | 🟡 YELLOW, strong domain story but the voice/dictation namespace is already loaded |

**Recommendation: Voxgrab > Untype > Voq.** Voxgrab is the only one with no namespace pollution in any axis (App Store, GitHub repo, GitHub user, domain). Untype is a strong second, only the TypeScript-namespace overlap, which doesn't bleed into voice/productivity. Voq has real competitive risk from `voquill` and `voqal`, the dictation/voice space is already claiming the voq prefix.

## Compound `.com` forms for user's shortlist

When the bare `.com` is taken, prefixed/suffixed forms are usually free at ~$10–15/yr. Verified-free (sample):

| Base | Notable free compound `.com`s |
|---|---|
| **vibe** | (only awkward forms, `tryvibehq.com`, `usevibehq.com`) |
| **yap** | (only awkward, `tryyaphq.com`, `getyapapp.com`) |
| **rif** | `getrif.com` ✅ (clean) |
| **riff** | `useriffapp.com`, `tryriffhq.com` (awkward) |
| **vox** | `tryvoxhq.com`, `usevoxapp.com` (awkward) |
| **voq** | `voqapp.com` ✅, `voqhq.com` ✅, `getvoq.com` ✅, `tryvoq.com` ✅, `usevoq.com` ✅, strong |
| **untype** | `untypeapp.com` ✅, `untypehq.com` ✅, `untypeio.com` ✅, `getuntype.com` ✅, `tryuntype.com` ✅, strong |

## Key observations

1. **Single English words on `.com` are 100% gone**, including obscure coinages, every test (`vaark`, `yapra`, `voq`, `vyce`) was already squatted.
2. **`.app` is almost as bad** for short English words. Only 4 free in this pass: `tongue`, `speyk`, `vaark`, `yapra`. Coined letter-strings have better odds.
3. **`.me` is the surprise winner**, many indie-friendly options free: `untype.me`, `blurt.me`, `vaark.me`, `speyk.me`, `yapra.me`, `notype.me`, `drift.me`, `talky.me`. Cheap (~$15–20/yr).
4. **Direct productivity/voice App Store collisions to weigh seriously:**
   - `utter`, already a dictation app
   - `vyce`, already a productivity app
   - `scribe`, already voice-to-text
   - `jot` / `braindump`, both Productivity-category brain-dump apps
   - `voq`, nVoq is a real medical-dictation company (legal risk)
   - `yap`, Yap Labs has voice memos
5. **Names with no exact-prefix App Store collision** (cleanest brand field): `rif`, `voq`*, `untype`, `blab`, `mutter`, `notype`, `sayd`, `spiel`, `vaark`, `voce`, `yapra`, `speyk`, `chime`, `snip`, `parlay`, `babble`, `drift`. (*voq has the nVoq trademark issue separately.)

## Decision dimensions to weigh

When picking, balance these axes, there's no clean winner across all four:
- **Semantic clarity**, does the name hint at voice/speech? (Blurt, Spiel, Mutter, Speyk, Yapra do; Vaark, Drift, Flux don't)
- **Brand whitespace**, is the App Store / web clear of competitors? (Vaark, Yapra, Speyk, Untype, Notype, Mutter, Spiel, Sayd are clean; Utter, Vyce, Yap, Scribe are crowded)
- **Domain accessibility**, can you get a `.app` or clean `.com` cheaply? (Vaark, Yapra, Speyk, Untype.me yes; Vibe/Riff/Vox no)
- **Verbal/written portability**, can you say it on a podcast and have someone type it correctly? (Vibe ✅, Yap ✅, Riff ✅, V1be ❌, Speyk ❌ ambiguous, Yapra ✅)

## Top contenders by dimension (after round 2)

Synthesizing semantic-fit + brand-whitespace + domain-availability + verbal-portability:

| Name | Strongest pitch | Weakest leg | Best home |
|---|---|---|---|
| **Saytak** | Coined, free across `.app`/`.io`/`.me`/all extended TLDs, zero App Store collision, "say" prefix hints at voice | Coined (no English hook), pronunciation: "say-tack"? | `saytak.app` (~$15) |
| **Saypod** | Coined, free across `.app`/`.io`/`.me`/all extended TLDs, no App Store collision, "say" + "pod" reads modern | Pod-suffix is well-trodden in audio space | `saypod.app` (~$15) |
| **Mikepad** | Descriptive (mic + pad), free across `.app`/`.io`/`.me`/all extended TLDs, no App Store collision | Slightly clunky; reads early-2000s | `mikepad.app` (~$15) |
| **Untype** | Highest semantic punch (literally describes the benefit), `.me`/`.eu`/all extended free, no App Store collision, strong compound `.com`s | "Untype" reads slightly negative; not a natural English word | `untype.me` (~$15) or `untypeapp.com` (~$10) |
| **Voq** | Strong dev-tool aesthetic, free across `.club`/`.world`/`.pro`/`.win`/`.art`/`.cloud`/`.tech`/`.today`, lots of clean compound `.com`s, no exact App Store hit | nVoq medical-dictation trademark adjacent (legal risk), no `.app` | `voqapp.com` (~$10) or `voq.cloud` (~$15) |
| **Vaark** | Coined, free `.app`/`.me`/all extended TLDs, zero brand baggage, single syllable, easy to trademark | No semantic hook to voice/speech (aardvark is a stretch) | `vaark.app` (~$15) |
| **Yapra** | Coined, free across `.app`/`.io`/`.me`/all extended TLDs, no App Store collision, "yap" inside for speech feel | Made-up, slight pronunciation hesitation ("yap-rah") | `yapra.app` (~$15) |
| **Notype** | Like Untype but slightly softer; same availability profile | Same downsides as Untype but less punchy | `notype.me` (~$15) |
| **Speyk** | Free `.app`/`.io`/`.me`/most extended TLDs, no collision, phonetic "speak" is on-message | Pronunciation ambiguous (speak/spike/spake) | `speyk.app` (~$15) |
| **Sayd** | Past tense of "say" reads naturally, `.io` + most extended free, clean App Store | `.com`/`.app` taken, requires compound or `.io` | `sayd.io` (~$35, edge of budget) or `trysayd.com` (~$10) |
| **Thwap** | Onomatopoeia, ZERO App Store hits, free `.app`/`.io`/`.me`/all extended TLDs, very memorable | Cartoon-ish, too playful for productivity tool? | `thwap.app` (~$15) |
| **Mynah** | Speech-bird (mynahs mimic human speech), `.me` + extended TLDs free, no App Store collision | `.app` and `.com` both taken | `mynah.me` (~$15) |
| **Mutter** | "Mutter to your mac" is a great tagline, no App Store collision, very on-theme | All primary TLDs taken; only some extended TLDs | `mutter.club` (~$15) or `mutter.today` (~$25) |
| **Vorato** | Italian-feeling coined; FREE on `.app` + `.io` + `.me` + ALL 9 extended TLDs; zero App Store collision; 6-letter brandable | No semantic anchor in English | `vorato.app` (~$15) |
| **Saypal** | FREE on `.io` + `.me` + ALL 9 extended; "say + pal" reads warm | `.app` taken; "pal" might feel cute | `saypal.io` (~$35, edge) or `saypal.me` (~$15) |
| **Voxbit** | FREE on `.me` + ALL 9 extended; tech-modern feel; "vox + bit" semantic | low-risk Voxbit Lifestyle exists; `.app`/`.io`/`.com` taken | `voxbit.cloud` (~$15) |
| **Vyq** | Ultra-distinctive 3-letter, `.app` FREE, 7/9 extended free, zero App Store collision | 3-letter names often premium-priced even when registered cheap; pronunciation: "vick"? "vy-cue"? | `vyq.app` (~$15 if not premium) |
| **Voxgrab** | "Voice grab", strong semantic fit; `.app` + `.io` + `.me` + ALL 9 extended TLDs FREE; zero App Store collision | Two-word feel ("vox" + "grab") might read clunky; "grab" connotation slightly aggressive | `voxgrab.app` (~$15) |
| **Voxbeam** | "Voice beam", capture-and-transmit metaphor; `.app` + `.io` + `.me` + ALL 9 extended TLDs FREE; zero App Store collision | Same two-word feel; "beam" is gentler than "grab" | `voxbeam.app` (~$15) |

**Universally-shut-out (will require >$30/yr or premium reseller):**
- **Vibe**, every TLD checked is taken; even `vi.be` is squatted. Premium-only path.
- **Riff**, same story.
- **Yap**, voice-memo space is poisoned (Yap Labs LLC has the productivity slot).

## Where to go next

Two reasonable next moves, depending on your gut:

**A. Narrow to 2–3 contenders and do final due diligence.** Run USPTO TESS trademark search (classes 9 + 42), scan Google + GitHub for projects, secure social handles. Then pick.

Suggested narrowing buckets:
- **If you want semantic clarity (the name *describes* the product)**: Untype, Saypod, Saytak, Mikepad
- **If you want a clean coined brand (zero baggage, easy trademark)**: Vaark, Yapra, Saytak, Voxlet, Thwap
- **If you want a stays-close-to-shortlist option**: Voq (with `voqapp.com` or `voq.cloud`)
- **If you want unique character / playful tone**: Thwap, Mynah

**B. Re-expand with a different angle.** If none of the above resonate, useful unexplored areas:
- Latin/Greek roots already explored (`voce`, `loqui`, `vox`); Sanskrit / Japanese roots untouched
- Two-syllable invented compounds (Voxify, Saytak, Mikepad), bigger surface for unique combos
- Animal metaphors (parrot, mockingbird, mynah, lyre, lyrebird), distinctive
- Onomatopoeia not yet checked: `pop`, `plop`, `dink`, `clink`, `bop`, `bing`

This document is state-only, no implementation plan yet. Once you pick a name, the rename plan will cover: `Package.swift` product/target rename, `Info.plist` bundle ID + display name, `bin/build.sh` signing identity (`Untype Dev` to `<Name> Dev`), TCC re-grant, `CLAUDE.md` references, MEMORY.md entries, sessions/ logs going forward, and the `/tmp/untype_debug.log` path.

## Verification

To re-verify domain availability before purchase (state can change daily):
```bash
# .app
curl -s -o /dev/null -w "%{http_code}\n" "https://pubapi.registry.google/rdap/domain/<name>.app"
# 404 = free, 200 = taken

# .com / .io / .me
whois <name>.com | grep -iE "Domain Name:|No match"

# App Store
curl -s "https://itunes.apple.com/search?term=<name>&country=us&entity=software,macSoftware&limit=10" | python3 -m json.tool
```

Trademark + handle:
- USPTO TESS: https://tmsearch.uspto.gov (classes 9 software, 42 SaaS)
- GitHub: `gh search repos <name>` and check `github.com/<name>`
- X / Instagram: manual handle check
