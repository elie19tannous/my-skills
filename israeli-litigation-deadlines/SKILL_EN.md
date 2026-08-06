---
name: israeli-litigation-deadlines
description: Compute and track legal deadlines, limitation periods, and court response windows for Israeli litigation and contract matters, and (where noted) general-purpose date math for any jurisdiction. Use when a user asks how long they have to sue (limitation / hitiyashnut), the deadline to file a defense (ktav hagana), to appeal (irur), to respond to a motion, to serve process, when a limitation clock starts or is tolled, how to count days around Israeli court recesses (pagrot) and rest days, or wants a tracked list of deadlines for a matter. Covers the Limitation Law, 5718-1958, common civil-procedure response windows, tolling/suspension rules, and safe-margin practice. Do NOT use for criminal statutes of limitation, tax assessment deadlines, or as a substitute for a lawyer's docketing on a live matter — always advise verifying against the current rules and the specific court file.
license: MIT
compatibility: No network required. Includes an offline date-math script (Python stdlib only).
---

# Israeli Litigation Deadlines and Limitation Periods

## Instructions

> **Safety first:** deadlines are malpractice-sensitive. This skill produces ESTIMATES to plan around, never a guarantee. Always advise the user to confirm each date against the current procedure rules, any court-issued order, and the actual file, and to build in a safe margin. When unsure, count conservatively (assume the EARLIER deadline).

### Step 1: The Two Kinds of Clocks — Limitation vs. Procedural
Keep these separate; they are governed by different rules.

| Clock | Hebrew | What It Controls | Miss It And... |
|-------|--------|------------------|----------------|
| Limitation period (hitiyashnut) | התיישנות | How long after a cause of action you may FILE a claim | The defendant can raise a limitation defense and bar the claim |
| Procedural deadline | מועד דיוני | Response/appeal/service windows AFTER proceedings start | The step is barred unless the court grants an extension (arka) |

Limitation is substantive and largely fixed by statute. Procedural deadlines come from the Civil Procedure Regulations and specific court orders and can sometimes be extended by the court for good cause.

### Step 2: Israeli Limitation Periods (Limitation Law, 5718-1958)
General civil limitation under the Limitation Law:

| Matter Type | Hebrew | Period |
|-------------|--------|--------|
| General civil claim (non-land) | תביעה שאינה במקרקעין | 7 years |
| Claims in unregistered land | מקרקעין לא מוסדרים | 15 years |
| Claims in registered land | מקרקעין מוסדרים | 25 years |
| When the defendant is abroad or other special rules apply | — | May be suspended/extended; check the statute |

**When the clock starts (accrual):** generally on the day the cause of action arose (nolad ilat hatvia). Special rules move the start:

| Rule | Hebrew | Effect |
|------|--------|--------|
| Discovery rule | כלל הגילוי | For facts the plaintiff could not have known, the clock can start when they were or should have been discovered (with an outer cap for certain claims) |
| Minority | קטינות | The period does not run against a minor until they reach majority (18) |
| Legal incapacity | חוסר כשירות | Suspended while the plaintiff lacks legal capacity |
| Fraud / concealment by the defendant | תרמית / הונאה | Clock can start when the plaintiff discovered the fraud |
| Acknowledgment of the debt | הודאה בקיום זכות | A written acknowledgment by the defendant can restart the clock |

**Suspension (tolling) events** pause the clock (e.g. plaintiff's minority or incapacity, defendant's absence abroad in some cases). Do not treat the 7 years as always a clean calendar count — check for tolling.

### Step 3: Common Procedural Response Windows
Typical civil-procedure deadlines (Civil Procedure Regulations, 5779-2018, and court practice). **Always verify against the current Regulations and any specific order — these are updated and a judge can shorten or lengthen them.**

| Step | Hebrew | Typical Window |
|------|--------|----------------|
| File a defense (statement of defense) | כתב הגנה | Commonly 60 days from service of the claim (fast-track / specific tracks differ) |
| Reply to a defense | כתב תשובה | Short window after the defense, when permitted |
| Response to a motion | תגובה לבקשה | Often ~ a few weeks; set by the regulation or the order |
| Appeal as of right to a higher court | ערעור בזכות | Commonly 45 days from the judgment (verify per court/track) |
| Leave to appeal (interlocutory) | בקשת רשות ערעור | Shorter, commonly ~30 days |
| Small claims appeal (leave) | רשות ערעור תביעות קטנות | 30 days (15 days for proceedings opened before 11 Apr 2025) |
| Serve the claim on the defendant | מסירת כתב תביעה | The plaintiff must effect and prove service within the rule's window |

Because these numbers move between reforms and differ by track, the skill's job is to flag the RELEVANT deadline and tell the user to confirm the exact current figure — not to assert a stale number as final.

### Step 4: Counting Rules — Israeli Specifics
How days are counted matters as much as the number.

| Rule | Detail |
|------|--------|
| Day of the triggering event | Generally NOT counted; counting starts the next day |
| Last day on a rest day / holiday | If the deadline falls on a Shabbat, a festival, or an official day when the court is closed, it typically rolls to the next working day |
| Court recess (pagrot) | Israeli courts have set recesses (e.g. summer recess, festival recesses). Certain deadlines are SUSPENDED or extended during a pagra — this can add days you did not expect |
| Service, not filing, often triggers the clock | Many response windows run from when the party was SERVED, not from when the document was filed or dated |
| "Clear days" vs calendar days | Some rules use clear/net days excluding endpoints — check the specific rule |

The pagra (court recess) effect is the single most common way an Israeli deadline is miscounted by non-specialists.

### Step 5: Building a Deadline Register for a Matter
When the user wants a tracked list, capture for each deadline:

| Field | Why |
|-------|-----|
| Trigger event + date | The event the clock runs from (service date, judgment date, cause-of-action date) |
| Rule / basis | Which statute or regulation sets the period (so it can be re-verified) |
| Raw deadline | Trigger + period, before adjustments |
| Adjusted deadline | After rolling off rest days and applying any pagra suspension |
| Safe internal deadline | Set EARLIER (e.g. 3-7 days before) to leave a margin |
| Status / owner | Who is responsible and whether it is done |

Deliver the register sorted by adjusted deadline, ascending, with the nearest deadline first and clearly flagged.

### Step 6: General-Purpose Date Math (any jurisdiction — noted)
The date arithmetic engine here is jurisdiction-agnostic. For non-Israeli or purely contractual deadlines (e.g. "30 days from invoice", "cure period of 10 business days"), use the same script with an explicit rule set: specify the count basis (calendar vs business days), whether the trigger day counts, and which holidays/weekend to skip. When used outside Israel, do NOT apply the Israeli pagra or Fri-Sat rest-day defaults — pass the correct weekend and holiday list for that jurisdiction.

## Examples

### Example 1: Do I Still Have Time to Sue?
**Input:** "A contractor did faulty work on my apartment in March 2019 and I only noticed the damage recently. Can I still sue?"
**Output:** This is a general civil (non-land) claim, so the base limitation period is 7 years under the Limitation Law, 5718-1958, running from when the cause of action arose. The discovery rule matters here: if you genuinely could not have known of the defect earlier, the clock may start from when you discovered (or should have discovered) it, which can extend your window past March 2026 — subject to any outer cap. Because this turns on when a reasonable person would have noticed, it is fact-sensitive; document when and how you discovered the damage. Confirm with a lawyer before relying on the discovery rule, and file with a safe margin rather than at the edge.

### Example 2: Deadline to File a Defense
**Input:** "I was served with a civil claim on 4 June. When is my defense due?"
**Output:** Under the Civil Procedure Regulations, the statement of defense (ktav hagana) is commonly due within 60 days of SERVICE, so counting from 5 June (the trigger day itself is not counted) that points to early August — BUT adjust for two things: (1) if the last day falls on Shabbat, a festival, or a court-closed day, it rolls to the next working day; (2) a court recess (pagra) in that window may suspend or extend the deadline. Verify the exact current window for your track, check the pagra calendar, and calendar an internal deadline several days earlier. If you might miss it, file a motion for an extension (bakashat arka) BEFORE the deadline, not after.

### Example 3: Appeal Window
**Input:** "I got a district court judgment on 10 July that I want to appeal. How long do I have?"
**Output:** An appeal as of right is commonly 45 days from the judgment, but this differs by court and track and is affected by court recesses — a summer pagra around July can extend the practical deadline. Count from the day after the judgment, roll off any rest/closed day, and apply the pagra rule, then set an internal deadline well before the adjusted date. Confirm the exact current appeal period for your specific court and proceeding before relying on it; missing an appeal deadline is usually fatal to the appeal.

### Example 4: Contractual Cure Period (general-purpose)
**Input:** "Our contract gives the other side a '10 business day' cure period after our default notice, sent 12 May. When does it end?"
**Output:** This is general date math, not Israeli procedure. Using business-day counting (skip weekends and applicable public holidays), start counting the day after 12 May and count 10 business days, skipping the contract's/jurisdiction's non-working days. Confirm the contract's definition of "business day" (some exclude only weekends, some also exclude public holidays, some specify a city/jurisdiction). The script can compute this precisely once you pass the weekend and holiday set. Then diarize the resulting date with a safe margin.

## Bundled Resources

### References
- `references/limitation-periods.md` -- Reference table of Israeli limitation periods under the Limitation Law, 5718-1958 (general civil, registered/unregistered land, and special categories), plus accrual, discovery, minority, incapacity, fraud, and acknowledgment rules that move or restart the clock. Consult when assessing whether a claim is time-barred.
- `references/counting-rules.md` -- Reference on how Israeli deadlines are counted: excluding the trigger day, rolling off Shabbat/festivals/court-closed days, the court recess (pagrot) suspension effect, and service-vs-filing triggers. Includes a worked example. Consult whenever computing an exact due date.

### Scripts
- `scripts/deadline_calculator.py` -- Jurisdiction-aware date-math tool (Python stdlib only, no network). Given a trigger date, a period (in calendar or business days/months/years), and options (whether to count the trigger day, a weekend definition, and a holiday list), returns the raw and adjusted deadline and a suggested safe internal date. Supports an Israeli mode (Fri-Sat weekend defaults, optional pagra-window flag) and a generic mode for any jurisdiction. Run: `python scripts/deadline_calculator.py --help`

## Gotchas

- Limitation (hitiyashnut) and procedural deadlines are DIFFERENT clocks with different rules. Limitation controls whether you can file at all; procedural windows control steps once litigation is underway. Agents often blur them and give the wrong number.
- The limitation clock is not always a clean 7-year calendar count. The discovery rule, minority, legal incapacity, the defendant's absence abroad, fraud/concealment, and a written acknowledgment of the debt can delay the start, suspend, or restart it. Assuming a flat 7 years from the event can wrongly declare a live claim dead (or a dead claim live).
- Land claims have longer limitation periods — 15 years (unregistered) and 25 years (registered) — not 7. Applying the general 7-year period to a real-estate claim is a common and serious error.
- Many response windows run from SERVICE, not from filing or the document's date. Counting from the wrong trigger date shifts every downstream deadline. Always pin the exact service date.
- The Israeli court recess (pagrot) can SUSPEND or extend certain deadlines. This is the single most common miscount by non-specialists. Never compute an Israeli litigation deadline without checking whether a recess falls in the window.
- A deadline landing on Shabbat, a festival, or a court-closed day generally rolls to the next working day. But do not rely on the roll as a safety buffer — treat the earlier working day as your practical target.
- Procedural periods (defense, appeal, motion responses) changed with the Civil Procedure Regulations, 5779-2018 and are refined over time; a judge can also shorten or extend them by order. Treat the numbers in this skill as prompts to VERIFY against the current rules and the specific file, not as fixed truth.
- For non-Israeli or contractual deadlines, do NOT apply Israeli defaults (Fri-Sat weekend, pagra). Pass the correct weekend and holiday set to the script, and use the contract's own definition of "business day".
- This skill produces estimates for planning. On a live matter it is not a substitute for a lawyer's docketing. Advise the user to confirm every date and keep a safe margin; a missed limitation or appeal deadline is usually irreversible.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Limitation Law, 5718-1958 | https://www.nevo.co.il/law_html/law01/p212m1_001.htm | Limitation periods, accrual, suspension, discovery, acknowledgment |
| Civil Procedure Regulations, 5779-2018 | https://www.nevo.co.il/law_html/law01/501_632.htm | Current response, appeal, service, and motion windows |
| Judicial Authority (court recess / pagrot calendar) | https://www.gov.il/en/departments/courts | Court recess dates and their effect on deadlines |
| Kol Zchut: Limitation of claims | https://www.kolzchut.org.il/he/התיישנות | Plain-language overview of limitation periods and tolling |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **israel-law**: programmatic access to Israeli primary legislation. Use it to pull the current text of the Limitation Law, 5718-1958, and the Civil Procedure Regulations to confirm exact periods and tolling rules before relying on a deadline.
- **kolzchut**: access to Kol Zchut, Israel's plain-language rights portal, for practical explanations of limitation, tolling, and procedural windows.

Always confirm load-bearing numbers (limitation periods, response/appeal windows, recess dates) against the primary source and the specific court file, since procedure changes and a judge can vary a deadline by order.

## Troubleshooting

### Error: "Two people gave me two different limitation periods for the same claim"
Cause: The claim may fall under a special category (land, insurance, a shorter statutory period in a specific law) rather than the general 7 years, or a tolling event is in play.
Solution: Identify the precise cause of action and check whether a specific statute sets its own limitation period (some do, and they can be shorter). Confirm the land status if property is involved (registered vs unregistered changes it to 25 or 15 years). Then check accrual and tolling (discovery, minority, incapacity, fraud, acknowledgment). Resolve the discrepancy by naming the exact statute, and advise filing with a safe margin.

### Error: "I counted the days but the court says I'm late"
Cause: Usually the trigger day was counted, service (not filing) was the real trigger, or a rest-day/recess adjustment was applied in the wrong direction.
Solution: Recompute: do not count the trigger day; run the clock from the SERVICE date where the rule uses service; roll a deadline off a rest/closed day to the next working day; and apply the pagra suspension if a recess fell in the window. Use the deadline_calculator.py script with the correct options to reproduce the count, and if genuinely late, file a motion for an extension (bakashat arka) explaining good cause immediately.

### Error: "The deadline calculator gives a weekend/holiday as the due date"
Cause: The tool returned the RAW deadline without adjustment, or the wrong weekend/holiday set was supplied.
Solution: Enable the adjustment option so the raw date rolls to the next working day, and confirm you passed the correct weekend definition (Fri-Sat for Israel; Sat-Sun elsewhere) and the correct holiday list. For Israeli litigation also check the pagra flag. Then take the ADJUSTED date, and still target your earlier safe internal date rather than the last legal day.
