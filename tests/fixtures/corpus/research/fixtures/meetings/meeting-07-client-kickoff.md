# Project Kickoff — Hartwell Freight Onboarding

**Attendees:** Naomi (CSM, our side), Eli (Solutions Engineer, our side), Greg (Director of Operations, Hartwell), Sandra (Project Lead, Hartwell), Otis (IT, Hartwell)

---

Naomi: Welcome everyone. The goal of this kickoff is to align on scope, milestones, and roles for the next ninety days. Greg, I'd like you to start by re-stating the business outcome we're driving toward.

Greg: We want our four largest customers — accounting for 60% of our shipment volume — onto your platform by end of next quarter. That's the outcome. The pressure is from one of them in particular: Sentinel Foods has been threatening to consolidate volume to a competitor unless we can give them real-time visibility within the next sixty days.

Naomi: That gives us a clear external deadline. Sandra, you're the project lead on Hartwell's side. Can you walk us through your team's availability?

Sandra: I have one full-time analyst, two part-time, and Otis from IT for technical questions. We're free of other major launches this quarter, so I'd say we have moderate-to-high bandwidth.

Eli: From the technical side, we'll need three integrations: your TMS for shipment data, your warehouse management system for inventory snapshots, and your customer-facing portal for status updates. Otis, what's your read on the WMS connection?

Otis: The WMS has a webhook system but it's been flaky in the past. I'd suggest we use a polling approach for the first phase and revisit webhooks once we've stabilized the rest. Polling on a five-minute interval should be enough resolution for what Sentinel needs.

Eli: Agreed. I'll write up the integration spec covering all three systems with the polling-first approach for the WMS. I'll have the spec circulated by Friday next week.

Naomi: Greg, on Sentinel specifically — they need real-time visibility within sixty days. That's tight. The TMS integration alone takes about five weeks. What's the minimum acceptable visibility for them?

Greg: They want shipment-level location updates every fifteen minutes during transit. If we can't hit that, they'll push to consolidate.

Eli: Fifteen minutes is achievable with TMS-only data. We don't need the WMS or the customer portal in place to deliver that. So we can carve out a phase 0 just for Sentinel's TMS integration and ship within thirty-five days. Phase 1 — full integration of WMS and customer portal — completes the original ninety-day target.

Greg: That's the path. Let's do phase 0 first. Sandra, can you align the analyst team on this priority?

Sandra: Yes, I'll talk to the analysts on Monday and we'll re-prioritize.

Naomi: Sandra, I'd also like to schedule weekly status calls for the duration of the engagement. Tuesdays at 2 PM your time?

Sandra: That works. I'll send the recurring invite.

Otis: Naomi, before we cut the spec — I want to make sure security review is built in. Anything that touches customer data needs a 30-day security review window before we can wire it up to production.

Naomi: Good catch. Eli, can you build that buffer into the spec timeline?

Eli: Will do. I'll include a "submit to Hartwell security" milestone in the spec.

Greg: One more — I want a single weekly summary email going to me and the COO covering progress, blockers, and decisions needed. Naomi, you're the right author for that?

Naomi: Yes. I'll send the first one next Friday and weekly Fridays after that.

Sandra: Could we also have a shared dashboard so the analyst team can see the same view?

Naomi: I'll set up a project board with milestones and current status. I'll have it ready by end of next week and share access with you, the analysts, and Otis.

Naomi: Recap. Eli circulates the integration spec by Friday next week, including the security-review buffer. Sandra aligns the analyst team Monday on the phase 0 / phase 1 split. Sandra sends the recurring Tuesday 2 PM status-call invite. I'll send the first weekly summary email next Friday. I'll set up the project board by end of next week. Phase 0 completes within thirty-five days delivering shipment-level updates every fifteen minutes for Sentinel. Phase 1 completes the full integration in ninety days.

Greg: Sounds right.

Naomi: Thanks all.
