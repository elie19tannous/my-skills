#!/usr/bin/env python3
"""Offline intake completeness checker for a new legal matter.

Python stdlib only. No network. Reads a filled intake form (simple `key: value`
text or JSON), reports which mandatory intake fields are present / empty /
missing, warns on high-risk blanks (conflicts not cleared, limitation absent),
and scores completeness. It is a checklist aid — it does NOT run the conflicts
search or judge the merits.

Usage:
    python intake_check.py path/to/intake.txt
    python intake_check.py path/to/intake.json
    python intake_check.py --selftest
"""
import argparse
import json
import re
import sys

# field -> (is_mandatory_to_open, is_high_risk)
FIELDS = {
    "client_name": (True, False),
    "client_type": (False, False),
    "goal": (False, False),
    "facts": (False, False),
    "parties": (True, False),
    "adverse_party": (True, False),
    "conflicts_status": (True, True),
    "limitation_date": (True, True),
    "scope_in": (True, False),
    "scope_out": (True, False),
    "assumptions": (False, False),
    "fee_basis": (True, False),
    "disbursements": (False, False),
    "recommendation": (True, False),
}

# values that count as "not really cleared" for the high-risk conflict/limitation fields
PENDING = {"", "pending", "not cleared", "unknown", "tbd", "todo", "n/a?", "?"}


def parse(text):
    """Parse JSON or simple `key: value` lines into a flat dict of str values."""
    text = text.strip()
    if text.startswith("{"):
        raw = json.loads(text)
        return {str(k).strip().lower().replace(" ", "_"): _flat(v) for k, v in raw.items()}
    out = {}
    for line in text.splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        out[k.strip().lower().replace(" ", "_")] = v.strip()
    return out


def _flat(v):
    if isinstance(v, (list, tuple)):
        return ", ".join(str(x) for x in v)
    if isinstance(v, dict):
        return json.dumps(v, ensure_ascii=False)
    return "" if v is None else str(v)


def check(data):
    present, empty, missing, warnings, blockers = [], [], [], [], []
    for field, (mandatory, high_risk) in FIELDS.items():
        val = data.get(field, None)
        if val is None:
            (missing if mandatory else empty).append(field)
            if mandatory:
                blockers.append(f"{field}: missing (mandatory to open)")
            continue
        if str(val).strip() == "":
            empty.append(field)
            if mandatory:
                blockers.append(f"{field}: empty (mandatory to open)")
            continue
        present.append(field)
        if high_risk and str(val).strip().lower() in PENDING:
            warnings.append(f"{field} = '{val}' is not resolved — HIGH risk, blocks file-opening")
            blockers.append(f"{field}: not resolved ('{val}')")

    total = len(FIELDS)
    score = round(100 * len(present) / total)
    return {
        "score": score,
        "present": present,
        "empty": empty,
        "missing": missing,
        "warnings": warnings,
        "blockers": blockers,
        "ready_to_open": not blockers,
    }


def render(r):
    lines = [f"Intake completeness: {r['score']}%  ({len(r['present'])}/{len(FIELDS)} fields)"]
    lines.append(f"Ready to open: {'YES' if r['ready_to_open'] else 'NO'}")
    if r["blockers"]:
        lines.append("\nBLOCKERS (must resolve before opening):")
        lines += [f"  - {b}" for b in r["blockers"]]
    if r["warnings"]:
        lines.append("\nWarnings:")
        lines += [f"  - {w}" for w in r["warnings"]]
    if r["empty"]:
        lines.append("\nEmpty (non-mandatory) fields: " + ", ".join(r["empty"]))
    return "\n".join(lines)


def selftest():
    # A deliberately incomplete form: conflicts pending, no limitation, no scope_out.
    form = (
        "client_name: Acme Ltd\n"
        "parties: Acme Ltd, Beta GmbH, guarantor J. Doe\n"
        "adverse_party: Beta GmbH\n"
        "conflicts_status: pending\n"
        "limitation_date:\n"
        "scope_in: draft and file claim to first-instance judgment\n"
        "fee_basis: phased\n"
        "recommendation: hold\n"
    )
    r = check(parse(form))
    assert r["ready_to_open"] is False, "incomplete form must not be ready to open"
    assert any("conflicts_status" in b for b in r["blockers"]), "pending conflicts must block"
    assert any("limitation_date" in b for b in r["blockers"]), "empty limitation must block"
    assert any("scope_out" in b for b in r["blockers"]), "missing scope_out must block"
    assert 0 < r["score"] < 100

    # A complete, clean form should be ready to open.
    good = {
        "client_name": "Acme Ltd", "client_type": "company", "goal": "recover debt",
        "facts": "invoice unpaid 90 days", "parties": "Acme, Beta, guarantor",
        "adverse_party": "Beta GmbH", "conflicts_status": "clear",
        "limitation_date": "2028-09-12 (prescription, from missed payment)",
        "scope_in": "demand + litigation to judgment", "scope_out": "enforcement, appeals",
        "assumptions": "one round, uncontested", "fee_basis": "phased fixed+hourly",
        "disbursements": "court fees", "recommendation": "open",
    }
    r2 = check(parse(json.dumps(good)))
    assert r2["ready_to_open"] is True, "complete clean form must be ready to open"
    assert r2["score"] == 100
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", nargs="?", help="intake form file (.txt key:value or .json)")
    ap.add_argument("--selftest", action="store_true", help="run embedded self-check and exit")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return
    if not args.path:
        ap.error("provide an intake file path or --selftest")
    with open(args.path, encoding="utf-8") as fh:
        data = parse(fh.read())
    r = check(data)
    print(render(r))
    sys.exit(0 if r["ready_to_open"] else 2)


if __name__ == "__main__":
    main()
