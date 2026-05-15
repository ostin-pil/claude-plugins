# Discovery Call — Brightline Logistics

**Attendees:** Lena (AE, our side), Tom (SE, our side), Ravi (VP Ops, Brightline), Diane (IT Director, Brightline)

---

Lena: Thanks for making time today, Ravi, Diane. Tom and I want to use this call to understand your current dispatch workflow and figure out whether our platform is a fit. Ravi, want to start with the pain you're trying to solve?

Ravi: Sure. We run about 1,200 deliveries a day across four hubs. Right now dispatch is split between two systems — the legacy TMS we've had since 2018 and a homegrown spreadsheet-and-Slack process for last-mile. The handoff between them is where we lose time. Drivers wait an average of eleven minutes between getting the route and actually rolling.

Lena: Eleven minutes per driver per day adds up fast. Diane, what's the architectural picture from your side?

Diane: The TMS is on-prem, with a SQL Server backend. We have an API but it's read-only. Any write integration has to go through their consultancy, and the lead time is six to eight weeks. We're under contract with them through next March.

Tom: That's a real constraint. For a first phase we'd want to do read-only sync from your TMS, run our dispatch optimizer, and write the manifest back through your existing channel — probably the dispatcher email blast they already use. That avoids the write-API problem entirely.

Diane: That could work. What do you need from our side to scope the read sync?

Tom: A schema dump of the route and shipment tables, plus a sample export covering one week. If you can share those by next Friday, I can have a technical scoping doc back to you within ten business days.

Diane: I can pull a non-production sample. Let me check with our DBA on the schema dump but I think Friday is fine.

Ravi: Lena, on commercial terms — we've talked to two other vendors. Both came in with annual contracts. What does your pricing look like?

Lena: We do annual or two-year. Two-year gets you a 12% discount and locks in the per-driver rate. For a fleet your size we're typically looking at the mid-tier package with a usage cap. I'll put together a one-page pricing scenario this week — let's say I send it to you by Wednesday.

Ravi: Wednesday works.

Tom: One more thing on integration — your drivers are mostly on Android tablets, correct?

Ravi: Yes. About 80% Android, 20% iPhone for the supervisors.

Tom: Then our existing mobile app covers the fleet without a custom build. That's good news for timeline.

Lena: Ravi, can I ask — what's the decision process on your side? Who's the buyer beyond you?

Ravi: It's me, Diane on the technical side, and the CFO will sign for anything over $200K annually. We typically run a four-week procurement review.

Lena: Got it. So if we can wrap technical scoping in three weeks, we'd be in a good window for a decision before the end of the quarter. Diane, can you confirm the procurement window in your end-of-quarter cycle?

Diane: I'll confirm with finance and let you know on Monday.

Ravi: Last thing — we'd want a reference call with another logistics customer of similar size before we sign.

Lena: I'll set that up. We have two references that match — Hartwell Freight and Coastline Express. I'll reach out to both and offer them a 30-minute slot. I'll get the introductions out by Thursday.

Ravi: Perfect.

Lena: Recap from my side: Diane shares the TMS schema dump and a one-week sample export by next Friday. Tom returns the technical scoping doc within ten business days of receiving the data. I send the pricing scenario by Wednesday. Diane confirms the procurement window on Monday. I make customer-reference introductions by Thursday. Anything missing?

Ravi: That covers it. Talk Monday.

Lena: Thanks Ravi, Diane.
