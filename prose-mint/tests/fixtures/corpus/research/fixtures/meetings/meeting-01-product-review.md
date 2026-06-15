# Product Review — Q2 Planning

**Attendees:** Sara (PM), Jordan (Eng Lead), Priya (Design), Marcus (Data)

---

Sara: Thanks everyone for joining. The goal today is to walk through the Q2 candidate features and pick the top three for the planning doc. I want to leave this meeting with owners for each. Marcus, can you start with the engagement numbers?

Marcus: Sure. The 30-day retention chart is in the deck — slide four. We're sitting at 34% on the new free tier, which is roughly flat versus last quarter. The activation drop-off is still in the onboarding flow, specifically step three where we ask for a payment method.

Sara: That matches what we saw in the user interviews last month. Priya, did the team finish the redesign mockups for that step?

Priya: We have two variants. The first defers the payment-method ask until the user hits a paywall trigger. The second keeps the ask in step three but adds a "skip for now" option. Both tested better than the current flow but the deferred version was clearly preferred — about 70% of the testers picked it.

Sara: OK. Let's go with the deferred version. Priya, can you finalize the spec by next Wednesday so engineering can size it?

Priya: Yes, I'll have the spec to Jordan by Wednesday end of day.

Jordan: I can put that on the Q2 candidate list with a rough estimate of two engineering weeks. We'll refine once we have the spec.

Sara: Perfect. Next item — the export feature request. We've had it in the backlog for two quarters. Marcus, do we have data on how many users would use it?

Marcus: Pulled the survey responses last week. About 22% of paid users said they'd use export at least monthly. It's not the biggest ask but it's the second-most-mentioned feature in cancellation surveys. I think it ties into the "I need to leave with my data" objection.

Jordan: We've been wanting to refactor the data layer anyway. If we tackle export, we should fold the refactor into the same workstream. I'll write up a one-pager comparing two approaches — bolt-on export versus refactor-first — and circulate it Thursday.

Sara: Good. Let's tentatively scope it for Q2 and decide on the approach next week. I want a decision before sprint planning.

Priya: One thing — for export, I'd like to do at least one pass on the empty state and the "we're preparing your file" state. The cancellation users specifically called out that the current data pages feel like a dead-end.

Sara: Agreed. Priya, can you sketch those two states alongside the engineering one-pager?

Priya: Yes, I'll have rough sketches by Friday.

Marcus: Sara, one more thing on the data side. The pricing experiment is wrapping up next Tuesday. I'll have the readout ready for Wednesday's leadership sync.

Sara: Make sure to share it with the growth team beforehand — they want to incorporate it into the Q2 forecast.

Marcus: Will do. I'll send the deck to growth on Monday.

Jordan: Last thing from my side — the iOS team is asking for a decision on the SwiftData migration. They've been blocked for two sprints. I think we either commit or punt. Punting is cheaper but the longer we wait the more migrations stack up.

Sara: Let's not punt again. Can you set up a 30-minute call with the iOS leads this week to scope it? I'll join.

Jordan: I'll send the invite for Thursday morning.

Sara: Great. To recap: Priya owns the onboarding-step-three spec by Wednesday and the export-state sketches by Friday. Jordan owns the export approach one-pager by Thursday and the SwiftData scoping call this week. Marcus owns the pricing readout for Wednesday and shares the deck with growth on Monday. We decided to go with the deferred-payment-method onboarding variant. Anything I missed?

Jordan: Nope, that captures it.

Sara: Thanks all. See you Wednesday.
