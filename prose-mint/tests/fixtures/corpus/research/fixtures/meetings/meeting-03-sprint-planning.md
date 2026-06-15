# Sprint Planning — Sprint 47

**Attendees:** Wei (EM), Ana (Backend), Theo (Frontend), Imani (QA), Felix (PM)

---

Felix: Welcome to sprint 47 planning. Sprint goal is to ship the new permissions screen behind a flag and clean up the two highest-priority bugs from last sprint. Anything else we should add before we walk through the backlog?

Wei: We need at least one slot for the database migration prep. We can't keep deferring it — the connection pool is starting to throttle on Tuesday peaks.

Felix: Agreed, we'll add it. Theo, where are we on the permissions screen design handoff?

Theo: I have the Figma file with the latest revisions. There's one open question about the empty-state copy — Priya is finalizing it tomorrow. I can start the layout work without it but I'll need the final copy by end of Wednesday to ship clean.

Felix: Priya, are you on the chat? She said she'd join. OK, I'll ping her after this and confirm the Wednesday deadline.

Imani: From QA, I want to flag that the regression suite is now taking 40 minutes on CI. If we don't trim it this sprint, it's going to keep getting worse. I propose we carve out a half-sprint task to remove the ten flakiest tests and replace them with smaller, deterministic ones.

Wei: Imani, take that on. I'll back you up on the engineering side if any of those tests need refactoring.

Imani: Will do. I'll have a list of the ten target tests by Tuesday and the replacements written by sprint end.

Felix: Sprint goal — let me restate it. Ship the permissions screen behind a flag, fix bugs 4421 and 4438, prep the database migration, and trim the regression suite. Five workstreams, sprint is ten working days. Capacity?

Wei: Ana is at full capacity. Theo is at full minus a half-day for the Friday all-hands. Imani is at 80% — she has the QA-onsite on Thursday next week.

Ana: I can take the database migration prep. That includes writing the rollback script and dry-running it on staging. Probably four days of work.

Wei: That works. Theo, you own permissions screen frontend?

Theo: Yes.

Wei: Ana, after migration prep wraps, can you take bug 4421? It's the auth-token refresh issue, mostly backend.

Ana: Yes, I can pick that up around day six.

Felix: Bug 4438 is frontend — the calendar widget reflow on Safari. Theo, can you fit it after the permissions screen?

Theo: It depends on how much polish the permissions screen needs after Priya's copy lands. Best case yes, worst case it slips to sprint 48. I'll commit to sprint 48 if it's tight.

Felix: Fair. We'll mark 4438 as stretch.

Imani: One more — the new permissions screen needs an accessibility audit before we flip the flag. Theo, can you set that up with the accessibility team for the end of next week?

Theo: I'll email them today and book the slot.

Wei: Felix, on the migration — the prep is ready by sprint end but the actual migration window is the following Saturday. We should book the on-call rotation now so two engineers are awake. I'll send the calendar holds.

Felix: Good catch. Wei, please send those holds today.

Imani: Last item: the test-data refresh. The fixture set for the integration tests is two months old. I'll refresh it next Wednesday.

Felix: OK, recap. Theo: permissions screen frontend, accessibility audit booked today, copy deadline confirmed with Priya. Ana: migration prep including rollback script and staging dry-run, then bug 4421. Imani: regression-suite trimming with target list by Tuesday and replacements by sprint end, plus integration-test fixture refresh next Wednesday. Wei: sends migration on-call calendar holds today. Stretch goal: bug 4438. I'll confirm Priya's Wednesday copy deadline after this call. We meet again Thursday for mid-sprint check.

Wei: Sounds good.

Felix: Thanks all.
