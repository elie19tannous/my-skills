# Counting Legal Deadlines — Israeli Rules

How to count a deadline correctly once you know the number of days. Miscounting,
not the raw number, is the usual cause of a blown deadline.

## Core counting rules

| Rule | Detail |
|------|--------|
| Trigger day excluded | The day of the triggering event is generally NOT counted; start counting the next day |
| Service, not filing | Many response windows run from the day a party was SERVED, not from the filing/issue date. Pin the exact service date |
| Roll off rest/closed days | If the last day falls on Shabbat, a festival, or an official court-closed day, the deadline typically rolls to the next working day |
| Weekend in Israel | The rest day is Friday-Saturday, not Saturday-Sunday. Business-day counts must skip Fri-Sat |
| Clear vs calendar days | Some rules use net/"clear" days excluding both endpoints — check the specific rule |

## Court recess (pagrot) — the biggest trap

Israeli courts observe set recesses (e.g. a summer recess and festival recesses).
For many procedural deadlines the recess SUSPENDS or extends the count, so a
window that spans a pagra is effectively longer than the raw day count.

- Always check whether a recess falls inside the window before finalizing a date.
- The recess dates are published by the Judicial Authority and change yearly.
- Not every deadline is affected the same way; confirm the rule for the specific
  step (defense, appeal, motion response).

## Worked example

Claim served on Thursday 4 June 2026, statement-of-defense window 60 days:
1. Trigger day (4 June) excluded → start counting 5 June.
2. Add the period → raw deadline ~3 August 2026.
3. If 3 August is a rest/closed day, roll to the next working day.
4. If a pagra falls in June-August, the practical deadline may extend further —
   check the recess calendar.
5. Set an INTERNAL deadline several days earlier as a safety margin.

Use `scripts/deadline_calculator.py` to reproduce the arithmetic. For non-Israeli
or contractual deadlines, pass the correct `--weekend` and `--holiday` set and do
NOT apply the pagra flag.

## Do / don't

- DO count from the service date when the rule uses service.
- DO roll a rest-day deadline forward, but target the earlier working day.
- DO check for a court recess in the window.
- DON'T count the trigger day.
- DON'T apply Israeli Fri-Sat / pagra defaults to a foreign or contractual deadline.
- DON'T rely on the roll-forward as your buffer — keep a separate safe margin.
