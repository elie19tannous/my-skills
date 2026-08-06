#!/usr/bin/env python3
"""Illustrative Israeli debt-balance estimator: principal + CPI linkage + interest.

This is a ROUGH estimate for planning only. The official Execution Office file
balance (yitrat chov) is authoritative — it uses the exact statutory interest
method, published CPI values, and per-action fees this script does not model.

ponytail: models simple annual interest + a flat CPI-linkage rate given by the
user, not the exact statutory compounding or published monthly CPI. Upgrade
path: feed real base/current CPI index values (--base-cpi/--current-cpi) instead
of an annual linkage rate, and swap simple for the statutory interest formula.
"""
import argparse
from datetime import date


def years_between(a: date, b: date) -> float:
    return (b - a).days / 365.25


def estimate(principal: float, start: date, end: date,
             annual_interest_pct: float, annual_linkage_pct: float) -> dict:
    yrs = years_between(start, end)
    linkage = principal * (annual_linkage_pct / 100.0) * yrs
    linked_principal = principal + linkage
    interest = linked_principal * (annual_interest_pct / 100.0) * yrs
    total = linked_principal + interest
    return {
        "years": round(yrs, 2),
        "principal": round(principal, 2),
        "linkage": round(linkage, 2),
        "interest": round(interest, 2),
        "estimated_balance": round(total, 2),
    }


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--principal", type=float, required=True)
    p.add_argument("--start", required=True, help="debt/judgment date YYYY-MM-DD")
    p.add_argument("--end", default=date.today().isoformat(), help="valuation date YYYY-MM-DD")
    p.add_argument("--interest", type=float, default=4.0, help="annual interest %% (illustrative)")
    p.add_argument("--linkage", type=float, default=2.0, help="annual CPI linkage %% (illustrative)")
    a = p.parse_args()
    r = estimate(a.principal, date.fromisoformat(a.start), date.fromisoformat(a.end),
                 a.interest, a.linkage)
    for k, v in r.items():
        print(f"{k:>18}: {v}")
    print("\nNOTE: illustrative only. The official file balance is authoritative.")


if __name__ == "__main__":
    # self-check
    r = estimate(10000, date(2020, 1, 1), date(2021, 1, 1), 4.0, 2.0)
    assert abs(r["linkage"] - 200.0) < 5      # ~2% of 10000 over ~1yr
    assert r["estimated_balance"] > 10000     # balance grows
    main()
