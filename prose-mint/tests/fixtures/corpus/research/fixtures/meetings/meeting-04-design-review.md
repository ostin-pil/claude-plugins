# Design Review — Settings Refresh

**Attendees:** Priya (Lead Designer), Quentin (Designer), Mariam (Eng), Ben (UX Research)

---

Priya: Quentin, walk us through the new settings IA.

Quentin: Sure. The current settings have 14 top-level entries, which usability tests showed users get lost in. The proposal collapses these into five groups: Account, Notifications, Privacy, Appearance, and Advanced. Each group has its own page with a search bar at the top.

Ben: From research, the top three searches were "delete account," "notification frequency," and "export data." All three are buried at least two levels deep right now. Whatever IA we pick, those need to be one-click reachable.

Quentin: The proposal handles two of those — delete account moves to the bottom of Account, and notification frequency is the first item in Notifications. Export data is more complex because it lives at the boundary of Account and Privacy. I left it under Privacy in the current draft.

Priya: I think Privacy is the right call. It matches user mental model around "my data" living together.

Mariam: From engineering, the only hard constraint is that some of the toggles trigger backend calls that take a few seconds — region change, two-factor enrollment. Make sure the design accounts for the loading states.

Quentin: Yes, I have a loading variant in the spec for those. I'll annotate which toggles need it before handoff.

Ben: I'd like to do one more round of testing with the new IA before engineering builds it. We can do an unmoderated study, five participants, single task — find delete account and find export data. Three days of fielding.

Priya: Is the cost worth the schedule slip?

Ben: I think so. The current IA was the source of two negative App Store reviews this month. If we ship this and miss the mark again, we pay for it twice.

Priya: OK. Ben, kick off the study Monday and we'll have results by Thursday. Quentin, hold the engineering handoff until we read the results.

Quentin: I'll keep iterating on the loading-state annotations and the dark mode pass while we wait.

Mariam: One more from engineering — I'd like the spec to include the deep-link routes. Right now Settings is reachable by pressing the gear icon, but support has been asking for direct links to specific pages. If we publish the routes now, support can update their canned responses.

Quentin: Good call. I'll add a section listing the route for each page when I finalize the spec.

Priya: Ben, when the study lands, send the highlights to engineering and design as a single page summary, not a deck. We'll iterate faster on text.

Ben: Will do. Highlights document Thursday afternoon.

Quentin: One open question — the toggle for analytics opt-out. Legal asked us to make it a default-on with a reminder banner, but the principle from research has always been default-off. Want to bring this to the broader team or hold pending legal?

Priya: Bring it up at next week's design crit. I want at least three perspectives before we lock the default.

Mariam: Heads-up — we've got a system-wide design token migration that lands the same week as your engineering handoff. If you need any tokens that aren't in the new system, flag them now or you'll be retrofitting later.

Quentin: I'll do a token audit alongside the spec and send Mariam a list of any gaps by Wednesday.

Priya: Recap — Ben kicks off the IA study Monday and shares the highlights document Thursday afternoon. Quentin holds engineering handoff until study results are in, finalizes loading-state annotations, dark-mode pass, deep-link route list, and a design-token gap audit (by Wednesday). The analytics opt-out default goes to next week's design crit. Quentin also handles the engineering-spec handoff after Thursday's results.

Ben: Got it.

Priya: See you next week.
