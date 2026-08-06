#!/usr/bin/env python3
"""Jurisdiction-aware legal deadline calculator (stdlib only, no network).

Computes raw and adjusted deadlines from a trigger date plus a period, with
optional business-day counting, weekend/holiday skipping, roll-forward off
non-working days, and a suggested safe internal date.

Israeli mode defaults: Friday-Saturday weekend. Pass --pagra-days to model a
court-recess suspension (adds N calendar days before adjustment). Outside
Israel, pass --weekend and --holiday explicitly. This is a planning ESTIMATE,
not legal advice; always verify against the current rules and the actual file.
"""
import argparse
from datetime import date, timedelta

WEEKENDS = {
    "fri-sat": {4, 5},   # Israel (Mon=0 .. Sun=6): Fri=4, Sat=5
    "sat-sun": {5, 6},   # most Western
    "none": set(),
}


def parse_date(s: str) -> date:
    y, m, d = (int(x) for x in s.split("-"))
    return date(y, m, d)


def add_calendar(start: date, n: int, unit: str) -> date:
    if unit == "days":
        return start + timedelta(days=n)
    if unit == "weeks":
        return start + timedelta(weeks=n)
    if unit == "months":
        # naive month add with clamping
        month = start.month - 1 + n
        year = start.year + month // 12
        month = month % 12 + 1
        day = min(start.day, [31, 29 if year % 4 == 0 and (year % 100 or year % 400 == 0) else 28,
                              31, 30, 31, 30, 31, 31, 30, 31, 30, 31][month - 1])
        return date(year, month, day)
    if unit == "years":
        try:
            return start.replace(year=start.year + n)
        except ValueError:  # Feb 29
            return start.replace(year=start.year + n, day=28)
    raise ValueError(f"unknown unit {unit}")


def add_business_days(start: date, n: int, weekend: set, holidays: set) -> date:
    d = start
    step = 1 if n >= 0 else -1
    remaining = abs(n)
    while remaining > 0:
        d += timedelta(days=step)
        if d.weekday() not in weekend and d not in holidays:
            remaining -= 1
    return d


def roll_forward(d: date, weekend: set, holidays: set) -> date:
    while d.weekday() in weekend or d in holidays:
        d += timedelta(days=1)
    return d


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--trigger", required=True, help="Trigger/service date YYYY-MM-DD")
    p.add_argument("--period", type=int, required=True, help="Length of the period, e.g. 7 or 60")
    p.add_argument("--unit", default="days", choices=["days", "weeks", "months", "years"])
    p.add_argument("--business", action="store_true",
                   help="Count business days (only valid with --unit days)")
    p.add_argument("--count-trigger-day", action="store_true",
                   help="Include the trigger day in the count (default: exclude)")
    p.add_argument("--weekend", default="fri-sat", choices=list(WEEKENDS),
                   help="Weekend set (default fri-sat = Israel)")
    p.add_argument("--holiday", action="append", default=[],
                   help="Holiday/court-closed date YYYY-MM-DD (repeatable)")
    p.add_argument("--pagra-days", type=int, default=0,
                   help="Court-recess days to add before adjustment (Israeli mode)")
    p.add_argument("--no-roll", action="store_true",
                   help="Do NOT roll a deadline off a weekend/holiday to next working day")
    p.add_argument("--safe-margin", type=int, default=5,
                   help="Days before the adjusted deadline for the safe internal date")
    args = p.parse_args()

    weekend = WEEKENDS[args.weekend]
    holidays = {parse_date(h) for h in args.holiday}
    trigger = parse_date(args.trigger)

    # Exclude the trigger day by starting the count the next day, unless told otherwise.
    start = trigger if args.count_trigger_day else trigger + timedelta(days=1)

    if args.business:
        if args.unit != "days":
            p.error("--business requires --unit days")
        # period-1 because the start day is the first counted business day
        first = roll_forward(start, weekend, holidays)
        raw = add_business_days(first, max(args.period - 1, 0), weekend, holidays)
    else:
        # calendar count: the deadline is start + (period - 1) so a 7-day window
        # beginning the day after the trigger ends on the 7th such day.
        base = add_calendar(start, max(args.period - 1, 0), args.unit) \
            if args.unit == "days" else add_calendar(trigger, args.period, args.unit)
        raw = base

    if args.pagra_days:
        raw = raw + timedelta(days=args.pagra_days)

    adjusted = raw if args.no_roll else roll_forward(raw, weekend, holidays)
    safe = adjusted - timedelta(days=args.safe_margin)

    print(f"Trigger date        : {trigger.isoformat()} ({trigger:%A})")
    print(f"Period              : {args.period} {args.unit}"
          f"{' (business days)' if args.business else ''}")
    print(f"Weekend set         : {args.weekend}")
    if holidays:
        print(f"Holidays skipped    : {', '.join(sorted(h.isoformat() for h in holidays))}")
    if args.pagra_days:
        print(f"Recess (pagra) added: {args.pagra_days} days")
    print(f"Raw deadline        : {raw.isoformat()} ({raw:%A})")
    print(f"Adjusted deadline   : {adjusted.isoformat()} ({adjusted:%A})"
          f"{'' if args.no_roll else '  <- rolled off rest/closed days'}")
    print(f"Safe internal date  : {safe.isoformat()} ({safe:%A})  [{args.safe_margin}-day margin]")
    print("\nESTIMATE for planning only. Verify against the current rules and the actual court file.")


# --- self-check: run `python deadline_calculator.py --selftest` ---
def _selftest():
    # 7 calendar days, trigger excluded: 2026-01-01 -> ends 2026-01-08
    weekend = WEEKENDS["fri-sat"]
    t = date(2026, 1, 1)
    start = t + timedelta(days=1)
    raw = add_calendar(start, 6, "days")
    assert raw == date(2026, 1, 8), raw
    # roll-forward off a Saturday (2026-01-10 is Sat) -> Sunday 2026-01-11
    sat = date(2026, 1, 10)
    assert sat.weekday() == 5
    assert roll_forward(sat, weekend, set()) == date(2026, 1, 11)
    # business days skip Fri/Sat: 3 business days from Thu 2026-01-08
    thu = date(2026, 1, 8)
    assert thu.weekday() == 3
    b = add_business_days(thu, 3, weekend, set())
    assert b == date(2026, 1, 13), b  # Fri/Sat skipped -> Sun,Mon,Tue
    print("selftest OK")


if __name__ == "__main__":
    import sys
    if "--selftest" in sys.argv:
        _selftest()
    else:
        main()
