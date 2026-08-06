#!/usr/bin/env python3
"""Offline vendor-contract diligence clause-coverage scanner (stdlib only).

Scans plaintext of a vendor/supplier contract and reports which of the key
diligence clauses appear present vs missing, plus a rough risk-tier hint from
data-sensitivity keywords.

ponytail: this is a coverage worklist, not an adequacy judge. A clause flagged
"present" may still be inadequate (e.g. a cap that exists but is too low).
Upgrade path: feed matched snippets to a human/LLM reviewer for adequacy scoring.

Usage:
    python diligence_scanner.py --file contract.txt
    python diligence_scanner.py --file contract.txt --format json
    python diligence_scanner.py --selftest
"""
import argparse
import json
import re
import sys

# clause_id -> (label, [regex patterns], severity_if_missing)
CLAUSE_PATTERNS = {
    "breach_notification": (
        "Breach notification window",
        [r"notif\w*.{0,40}(breach|incident)", r"(breach|incident).{0,40}notif\w*",
         r"without undue delay", r"within\s+\d+\s*(hours?|days?)"],
        "critical",
    ),
    "dpa_subprocessors": (
        "DPA / sub-processor terms",
        [r"data processing (addendum|agreement)", r"\bDPA\b", r"sub-?processor"],
        "critical",
    ),
    "liability_cap": (
        "Liability cap",
        [r"limitation of liability", r"liability.{0,30}(cap|capped|limited to)",
         r"aggregate liability"],
        "high",
    ),
    "breach_carveout": (
        "Data-breach carve-out from cap",
        [r"(breach|security incident).{0,60}(exclu|carve|except|super-?cap)",
         r"(exclu|carve|except).{0,60}(breach|security incident)"],
        "high",
    ),
    "sla_credits": (
        "SLA metrics + service credits",
        [r"service level", r"\bSLA\b", r"service credit", r"uptime"],
        "medium",
    ),
    "chronic_failure_termination": (
        "Termination right on chronic SLA failure",
        [r"(terminat\w*).{0,60}(chronic|repeated|consecutive|material).{0,30}(fail|breach)",
         r"(chronic|repeated|consecutive).{0,60}terminat"],
        "high",
    ),
    "data_return_deletion": (
        "Data return + deletion on exit",
        [r"return.{0,40}data", r"delet\w*.{0,40}(data|certif)", r"certif\w*.{0,30}delet"],
        "high",
    ),
    "auto_renewal": (
        "Auto-renewal clause (flag for review, not a coverage gap)",
        [r"automatic\w*\s+renew", r"auto-?renew"],
        "info",
    ),
    "ip_indemnity": (
        "IP-infringement indemnity",
        [r"indemnif\w*.{0,60}(infring|intellectual property)",
         r"(infring|intellectual property).{0,60}indemnif\w*"],
        "high",
    ),
    "data_breach_indemnity": (
        "Data-breach / confidentiality indemnity",
        [r"indemnif\w*.{0,100}(breach|confidential|security)",
         r"(breach|confidential|security).{0,100}indemnif\w*"],
        "high",
    ),
}

RISK_KEYWORDS = {
    "critical": [r"\bPCI\b", r"payment process", r"production database", r"PHI\b"],
    "high": [r"\bPII\b", r"personal data", r"customer data", r"health record"],
    "medium": [r"business data", r"confidential information"],
}


def scan(text: str) -> dict:
    text_l = re.sub(r"\s+", " ", text.lower())
    results = {}
    for clause_id, (label, patterns, severity) in CLAUSE_PATTERNS.items():
        present = any(re.search(p, text_l, re.IGNORECASE) for p in patterns)
        results[clause_id] = {
            "label": label,
            "present": present,
            "severity_if_missing": severity,
        }

    tier = "low"
    for level in ("critical", "high", "medium"):
        if any(re.search(p, text_l, re.IGNORECASE) for p in RISK_KEYWORDS[level]):
            tier = level
            break

    missing_critical = [c["label"] for c in results.values()
                         if not c["present"] and c["severity_if_missing"] == "critical"]
    missing_high = [c["label"] for c in results.values()
                     if not c["present"] and c["severity_if_missing"] == "high"]

    return {
        "risk_tier_hint": tier,
        "clauses": results,
        "missing_critical": missing_critical,
        "missing_high": missing_high,
        "note": "Coverage worklist only -- presence does not mean adequacy. Judge each present clause by hand.",
    }


def format_text(report: dict) -> str:
    lines = [f"Risk tier hint: {report['risk_tier_hint'].upper()}", ""]
    for cid, c in report["clauses"].items():
        mark = "[x]" if c["present"] else "[ ]"
        lines.append(f"{mark} {c['label']}" + ("" if c["present"] else f"  (missing, severity={c['severity_if_missing']})"))
    lines.append("")
    if report["missing_critical"]:
        lines.append("CRITICAL gaps: " + ", ".join(report["missing_critical"]))
    if report["missing_high"]:
        lines.append("HIGH gaps: " + ", ".join(report["missing_high"]))
    if not report["missing_critical"] and not report["missing_high"]:
        lines.append("No critical/high pattern gaps detected (adequacy still needs human review).")
    return "\n".join(lines)


def run_selftest() -> None:
    good_contract = """
    This DPA governs sub-processor use. Vendor shall notify Customer of any
    security incident without undue delay. Liability is capped at 12 months
    fees; data breach and IP infringement indemnity are excluded from this cap.
    Vendor provides an SLA of 99.9% uptime with service credits, and Customer
    may terminate after 3 consecutive material SLA failures. On termination,
    Vendor shall return Customer data in a usable format and provide a
    certificate of deletion. Vendor indemnifies Customer for IP infringement
    and for losses arising from a data breach. This agreement does not
    automatically renew.
    """
    report = scan(good_contract)
    assert report["clauses"]["breach_notification"]["present"] is True
    assert report["clauses"]["dpa_subprocessors"]["present"] is True
    assert report["clauses"]["liability_cap"]["present"] is True
    assert report["clauses"]["breach_carveout"]["present"] is True
    assert report["clauses"]["sla_credits"]["present"] is True
    assert report["clauses"]["chronic_failure_termination"]["present"] is True
    assert report["clauses"]["data_return_deletion"]["present"] is True
    assert report["clauses"]["ip_indemnity"]["present"] is True
    assert report["clauses"]["data_breach_indemnity"]["present"] is True
    assert report["missing_critical"] == []

    bad_contract = "Vendor will use commercially reasonable efforts. Fees are due monthly."
    report2 = scan(bad_contract)
    assert report2["clauses"]["breach_notification"]["present"] is False
    assert report2["clauses"]["dpa_subprocessors"]["present"] is False
    assert "Breach notification window" in report2["missing_critical"]
    assert "DPA / sub-processor terms" in report2["missing_critical"]

    pci_contract = "Vendor will process PCI cardholder data for payment processing."
    report3 = scan(pci_contract)
    assert report3["risk_tier_hint"] == "critical"

    print("selftest OK")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Offline vendor-contract diligence clause-coverage scanner (stdlib only)."
    )
    parser.add_argument("--file", help="Path to contract plaintext file")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--selftest", action="store_true", help="Run built-in self-check and exit")
    args = parser.parse_args()

    if args.selftest:
        run_selftest()
        return 0

    if not args.file:
        parser.print_help()
        return 1

    with open(args.file, "r", encoding="utf-8", errors="replace") as f:
        text = f.read()

    report = scan(text)
    if args.format == "json":
        print(json.dumps(report, indent=2))
    else:
        print(format_text(report))
    return 0


if __name__ == "__main__":
    sys.exit(main())
