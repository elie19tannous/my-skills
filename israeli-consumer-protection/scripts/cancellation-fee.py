#!/usr/bin/env python3
"""Israeli consumer-protection cancellation fee + refund deadline calculator.

The lawful cancellation fee for a change-of-mind cancellation is the LOWER of
5% of the transaction price or 100 NIS (Consumer Protection Law / 2010
cancellation regulations). For a defective or misdescribed item the fee is 0.
The seller must refund within 14 days of the cancellation notice.

ponytail: fee cap (5% / 100 NIS) and refund window (14 days) hardcoded from the
regulations as of authoring. Upgrade path: if the regulator changes the cap or
window, edit FEE_PCT / FEE_CAP_NIS / REFUND_DAYS below.
"""
import argparse
from datetime import date, timedelta

FEE_PCT = 0.05
FEE_CAP_NIS = 100.0
REFUND_DAYS = 14


def cancellation_fee(price: float, defective: bool) -> float:
    if defective:
        return 0.0
    return round(min(price * FEE_PCT, FEE_CAP_NIS), 2)


def refund_deadline(notice: date) -> date:
    return notice + timedelta(days=REFUND_DAYS)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--price", type=float, required=True, help="transaction price in NIS")
    p.add_argument("--defective", action="store_true", help="item is defective / not as described")
    p.add_argument("--notice-date", default=date.today().isoformat(),
                   help="cancellation notice date YYYY-MM-DD (default: today)")
    a = p.parse_args()

    notice = date.fromisoformat(a.notice_date)
    fee = cancellation_fee(a.price, a.defective)
    refundable = round(a.price - fee, 2)

    print(f"Transaction price:     {a.price:>10.2f} NIS")
    print(f"Reason:                {'defective / mismatch' if a.defective else 'change of mind'}")
    print(f"Max lawful cancel fee: {fee:>10.2f} NIS")
    print(f"Amount to refund:      {refundable:>10.2f} NIS")
    print(f"Refund by (deadline):  {refund_deadline(notice).isoformat()}")


if __name__ == "__main__":
    # self-check
    assert cancellation_fee(1000, False) == 50.0      # 5% = 50 < 100 cap
    assert cancellation_fee(5000, False) == 100.0     # 5% = 250, capped at 100
    assert cancellation_fee(1000, True) == 0.0        # defect => no fee
    assert refund_deadline(date(2026, 1, 1)) == date(2026, 1, 15)
    main()
