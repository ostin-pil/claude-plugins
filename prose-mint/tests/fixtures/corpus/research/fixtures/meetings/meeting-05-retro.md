# Sprint Retrospective — Sprint 46

**Attendees:** Wei (EM), Ana (Backend), Theo (Frontend), Imani (QA), Felix (PM), Sara (PM)

---

Wei: Welcome to the sprint 46 retro. Standard format — what went well, what didn't, what to change. Felix kicks off.

Felix: What went well: we shipped the analytics dashboard on the day we committed. Good estimation, no surprises during integration. Cross-team coordination with the marketing team was smooth.

Theo: What went well from frontend: pair programming on the chart components saved us at least a day. Ana and I caught a state-management issue that would have been a long debug if we'd hit it solo.

Ana: Agreed. I'd vote we keep doing pair programming on anything that touches shared state.

Wei: OK, that's a candidate change. Let me park it. What didn't go well?

Imani: The QA window was too short. We had two days to test a feature that had three new flows. I escalated on Tuesday but the deploy was already locked in. We got lucky that the smoke tests caught the calendar bug before it shipped.

Felix: I own that. The cutoff date was set assuming the design handoff would be Monday, but it slipped to Wednesday and I didn't push the QA window correspondingly.

Imani: Going forward, can we put a hard rule that QA gets minimum three full days post handoff?

Wei: Yes. Felix, can you write up that rule and add it to the team handbook?

Felix: I'll have the proposal in the handbook by end of next week.

Sara: Another thing that didn't go well — the standup ran long every day. I think it's because we have too many unrelated workstreams reporting in serial. Maybe we split into two standups?

Theo: I'd push back on splitting. We benefit from the cross-team awareness. But maybe we tighten the format — strict two minutes per person, no discussion in the meeting, take detailed conversations offline.

Ana: Two-minute hard cap, agreed. We tried this once before and it slipped. Maybe Wei can be the timer this time.

Wei: I'll be the timer for the next two weeks. If standups are still drifting after that, we revisit.

Imani: One more — the test environment was unstable for three days mid-sprint. I lost about half a day debugging tests that turned out to be infrastructure problems.

Wei: That's been a recurring pattern. I'll open a ticket for the platform team specifically about the staging-database flakiness and tag it as a recurring issue. I'll do that today.

Sara: Finally, on the positive side — the design crit format change worked. Going from open feedback to structured feedback (start with constraints, then strengths, then questions, then suggestions) led to crisper feedback per Quentin and Priya.

Felix: That's three for the keep-doing list: pair programming on shared state, structured design crit format, smoke-test discipline. And three for the change list: minimum-three-days QA rule, two-minute standup cap, recurring infra-flakiness ticket.

Wei: Imani, can you also lead a 30-minute session next week walking the team through the smoke-test patterns that caught the calendar bug? It'll help spread that discipline.

Imani: Sure. I'll book a slot for Tuesday.

Wei: Final action — Felix, summarize this retro in a Slack post by tomorrow so the team has it for reference.

Felix: Will do.

Wei: Thanks everyone. Sprint 47 planning is right after this.
