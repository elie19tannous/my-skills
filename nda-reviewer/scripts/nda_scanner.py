#!/usr/bin/env python3
"""Offline first-pass NDA clause flagger (stdlib only, no network).

Scans NDA plaintext and flags candidate issues by category:
  - mutuality: one-way vs mutual signals
  - carve_outs: which of the five standard carve-outs appear to be missing
  - term: perpetual / over-long survival language
  - ip_traps: IP-assignment, feedback-grab, broad-licence, non-compete patterns

This flags candidates for HUMAN review. It does NOT decide whether a clause is
fair or enforceable -- that requires reading the clause and knowing the deal.

Usage:
    python nda_scanner.py --file nda.txt
    python nda_scanner.py --file nda.txt --format json
    echo "text..." | python nda_scanner.py
    python nda_scanner.py --selftest
"""
import argparse
import json
import re
import sys

# --- IP / licence / feedback / restraint trap patterns (highest severity) ---
IP_TRAP_PATTERNS = {
    "ip_assignment": re.compile(
        r"\b(?:hereby assigns?|shall (?:be )?(?:owned by|belong to)|assigns? all"
        r"|all (?:intellectual property|IP|inventions?|work product) (?:created|developed)"
        r"[^.]{0,40}(?:owned by|belong|assign))\b", re.I),
    "feedback_grab": re.compile(
        r"\b(?:feedback|suggestions?|comments?|ideas?)\b[^.]{0,80}"
        r"\b(?:become[s]?|shall be|property of|owned by|assigns?|royalty[- ]free|perpetual)\b", re.I),
    "broad_licence": re.compile(
        r"\b(?:licen[cs]e|right to use)\b[^.]{0,60}"
        r"\b(?:any (?:purpose|business purpose)|for all purposes|unlimited)\b", re.I),
    "non_compete": re.compile(
        r"\b(?:non[- ]?compete|not (?:to )?compete|non[- ]?solicit|shall not solicit"
        r"|restraint of trade)\b", re.I),
    "improvements_grab": re.compile(
        r"\bimprovements?\b[^.]{0,60}\b(?:belong to|owned by|property of|assign)\b", re.I),
}

# --- one-way vs mutual signals ---
MUTUAL_RE = re.compile(
    r"\b(?:each party|both parties|mutual|reciprocal|either party"
    r"|as (?:Discloser|Disclosing Party).{0,10}(?:Recipient|Receiving Party))\b", re.I)
ONEWAY_RE = re.compile(
    r"\b(?:disclosed by (?:the )?(?:Company|Disclosing Party|Discloser)\b"
    r"|Recipient (?:shall|will|must|agrees)|the Receiving Party (?:shall|will|agrees))", re.I)

# --- the five standard carve-outs ---
CARVE_OUTS = {
    "public": re.compile(r"\b(?:publicly (?:available|known)|in the public domain|becomes public)\b", re.I),
    "already_known": re.compile(r"\b(?:already (?:known|in (?:its|the) possession)|known to (?:the )?Recipient (?:before|prior))\b", re.I),
    "independently_developed": re.compile(r"\bindependently (?:developed|derived|created)\b", re.I),
    "third_party": re.compile(r"\b(?:received from|obtained from) (?:a )?third part(?:y|ies)\b", re.I),
    "required_by_law": re.compile(r"\b(?:required (?:to be disclosed )?by law|court order|legal (?:process|compulsion)|subpoena)\b", re.I),
}

# --- term / survival ---
PERPETUAL_RE = re.compile(r"\b(?:perpetual|perpetuity|indefinite(?:ly)?|forever|in perpetuity|no expiration)\b", re.I)
YEARS_RE = re.compile(r"\b(\d{1,2})\s*(?:\(\w+\)\s*)?years?\b", re.I)
TRADE_SECRET_RE = re.compile(r"\btrade secret", re.I)


def scan(text):
    text_norm = re.sub(r"\s+", " ", text)

    ip_traps = []
    for name, pat in IP_TRAP_PATTERNS.items():
        for m in pat.finditer(text_norm):
            snippet = text_norm[max(0, m.start() - 30): m.end() + 30].strip()
            ip_traps.append({"trap": name, "match": m.group(0)[:80], "context": snippet[:160]})

    mutual_hits = len(MUTUAL_RE.findall(text_norm))
    oneway_hits = len(ONEWAY_RE.findall(text_norm))
    if mutual_hits == 0 and oneway_hits > 0:
        mutuality = "likely_one_way"
    elif mutual_hits > 0 and mutual_hits >= oneway_hits:
        mutuality = "likely_mutual"
    else:
        mutuality = "mixed_review_manually"

    present = {k: bool(p.search(text_norm)) for k, p in CARVE_OUTS.items()}
    missing_carve_outs = [k for k, v in present.items() if not v]

    perpetual = bool(PERPETUAL_RE.search(text_norm))
    years = [int(y) for y in YEARS_RE.findall(text_norm)]
    max_years = max(years) if years else None
    has_trade_secret = bool(TRADE_SECRET_RE.search(text_norm))
    term_flags = []
    if perpetual and not has_trade_secret:
        term_flags.append("perpetual_without_trade_secret_limit")
    elif perpetual and has_trade_secret:
        term_flags.append("perpetual_present_confirm_limited_to_trade_secrets")
    if max_years is not None and max_years > 5:
        term_flags.append(f"long_survival_{max_years}_years_review")

    return {
        "mutuality": {"signal": mutuality, "mutual_hits": mutual_hits, "one_way_hits": oneway_hits},
        "carve_outs": {"present": present, "missing": missing_carve_outs},
        "term": {"perpetual": perpetual, "max_years": max_years,
                 "mentions_trade_secret": has_trade_secret, "flags": term_flags},
        "ip_traps": ip_traps,
    }


def render_text(r):
    out = ["=== NDA CLAUSE WORKLIST (first pass -- human review required) ==="]
    m = r["mutuality"]
    out.append(f"MUTUALITY: {m['signal']}  (mutual signals={m['mutual_hits']}, one-way signals={m['one_way_hits']})")
    co = r["carve_outs"]
    if co["missing"]:
        out.append(f"CARVE-OUTS MISSING: {', '.join(co['missing'])}  <-- add the standard exclusions")
    else:
        out.append("CARVE-OUTS: all five standard exclusions detected (confirm wording).")
    t = r["term"]
    if t["flags"]:
        out.append(f"TERM FLAGS: {', '.join(t['flags'])}  (max years seen={t['max_years']})")
    else:
        out.append(f"TERM: no perpetual/over-long flags (max years seen={t['max_years']}).")
    if r["ip_traps"]:
        out.append(f"IP/LICENCE TRAPS: {len(r['ip_traps'])} candidate(s) -- HIGH severity, read each:")
        for trap in r["ip_traps"]:
            out.append(f"  [{trap['trap']}] ...{trap['context']}...")
    else:
        out.append("IP/LICENCE TRAPS: none detected by pattern (still confirm 'no IP/licence granted' is stated).")
    out.append("")
    out.append("NOTE: pattern-based first pass. It will miss creatively worded traps and over-flag "
               "benign clauses. Read each flagged clause; do not treat this as a fairness or "
               "enforceability verdict.")
    return "\n".join(out)


def selftest():
    sample = (
        "This Mutual Non-Disclosure Agreement is entered by each party. "
        "Confidential Information disclosed by the Disclosing Party is protected. "
        "Confidential Information does not include information that is publicly available, "
        "or that is independently developed by the Recipient, or required by law. "
        "The Recipient hereby assigns all intellectual property created to the Discloser. "
        "All feedback and suggestions become the property of the Discloser, royalty-free and perpetual. "
        "Recipient is granted a licence to use the information for any business purpose. "
        "The confidentiality obligations continue in perpetuity. "
        "This agreement runs for 7 years."
    )
    r = scan(sample)
    # IP traps must be caught
    traps = {t["trap"] for t in r["ip_traps"]}
    assert "ip_assignment" in traps, traps
    assert "feedback_grab" in traps, traps
    assert "broad_licence" in traps, traps
    # missing carve-outs: already_known and third_party absent in sample
    assert "already_known" in r["carve_outs"]["missing"], r["carve_outs"]
    assert "third_party" in r["carve_outs"]["missing"], r["carve_outs"]
    # present ones detected
    assert r["carve_outs"]["present"]["public"] is True
    assert r["carve_outs"]["present"]["independently_developed"] is True
    # term: perpetual flagged, and 7 years > 5
    assert r["term"]["perpetual"] is True
    assert any("perpetual" in f for f in r["term"]["flags"]), r["term"]["flags"]
    assert r["term"]["max_years"] == 7, r["term"]
    assert any("long_survival" in f for f in r["term"]["flags"]), r["term"]["flags"]
    # mutuality: mutual signals present
    assert r["mutuality"]["mutual_hits"] >= 1, r["mutuality"]
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="First-pass NDA clause flagger (stdlib only).")
    ap.add_argument("--file", help="Path to a plaintext NDA. Omit to read stdin.")
    ap.add_argument("--format", choices=["text", "json"], default="text")
    ap.add_argument("--selftest", action="store_true", help="Run embedded self-check and exit.")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    if args.file:
        with open(args.file, encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()

    if not text.strip():
        print("No input text. Use --file or pipe via stdin.", file=sys.stderr)
        sys.exit(1)

    result = scan(text)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(render_text(result))


if __name__ == "__main__":
    main()
