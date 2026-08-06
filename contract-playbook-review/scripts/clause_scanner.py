#!/usr/bin/env python3
"""Offline first-pass clause/trigger scanner for playbook review (stdlib only, no network).

Splits a plaintext contract into candidate clauses, tags the likely clause topic
(liability, indemnity, termination, IP, confidentiality, data protection,
payment, governing law, assignment, non-compete, insurance, warranty), and
surfaces phrases that commonly signal a HARD REDLINE (e.g. "uncapped",
"unlimited liability", "sole discretion", "irrevocable", "perpetual",
"indemnify and hold harmless") or an ESCALATION TRIGGER (dollar thresholds,
cross-border data, exclusivity, most-favored-customer).

This produces a mapping/triage worklist for HUMAN grading against the firm's
playbook. It does NOT and cannot judge whether a clause falls within a fallback
band -- that requires reading the clause against the actual playbook positions.

Usage:
    python clause_scanner.py --file contract.txt
    python clause_scanner.py --file contract.txt --format json
    echo "text..." | python clause_scanner.py
    python clause_scanner.py --selftest
"""
import argparse
import json
import re
import sys

# --- clause topic patterns (pattern-based; will mis-tag some clauses) ---
TOPIC_PATTERNS = {
    "liability": re.compile(r"\b(?:limitation of liability|liabilit(?:y|ies)|liable|damages cap|aggregate cap)\b", re.I),
    "indemnity": re.compile(r"\b(?:indemnif(?:y|ication|ies)|hold harmless|defend)\b", re.I),
    "termination": re.compile(r"\bterminat\w*|\b(?:expiry|auto[- ]?renew\w*)\b", re.I),
    "ip": re.compile(r"\b(?:intellectual property|licen[cs]e|ownership of|assigns? all right|work product)\b", re.I),
    "confidentiality": re.compile(r"\b(?:confidential(?:ity)?|non[- ]?disclosure|proprietary information)\b", re.I),
    "data_protection": re.compile(r"\b(?:personal data|data protection|GDPR|processor|sub[- ]?processor|data transfer)\b", re.I),
    "payment": re.compile(r"\b(?:payment|fees?|invoice|net\s?\d{1,3}|price escalation|pricing)\b", re.I),
    "governing_law": re.compile(r"\b(?:governing law|governed by the laws|jurisdiction|venue|arbitration|forum)\b", re.I),
    "assignment": re.compile(r"\b(?:assign(?:ment)?|transfer this agreement|novat(?:e|ion))\b", re.I),
    "non_compete": re.compile(r"\b(?:non[- ]?compete|exclusiv(?:e|ity)|restrictive covenant|solicit)\b", re.I),
    "insurance": re.compile(r"\b(?:insurance|insured|coverage of at least|policy limits)\b", re.I),
    "warranty": re.compile(r"\b(?:warrant(?:y|ies|s)|represents? and warrants?|as[- ]is)\b", re.I),
}

# --- hard-redline signal phrases ---
REDLINE_RE = re.compile(
    r"\b(?:uncapped|unlimited liabilit|without limitation of liabilit|sole discretion|"
    r"irrevocabl|in perpetuity|perpetual|indemnif\w* and hold harmless|"
    r"waives? all|no liability cap|unrestricted right|at any time and for any reason)\b",
    re.I,
)

# --- escalation-trigger signal phrases ---
TRIGGER_PATTERNS = {
    "dollar_threshold": re.compile(r"[$€£₪]\s?\d[\d,]*(?:\.\d+)?(?:\s?(?:k|m|million|billion))?", re.I),
    "cross_border_data": re.compile(r"\b(?:cross[- ]?border|transfer\w* .{0,30}outside|international data transfer|third country)\b", re.I),
    "exclusivity": re.compile(r"\b(?:exclusiv(?:e|ity)|most[- ]?favou?red (?:customer|nation)|MFN)\b", re.I),
    "foreign_forum": re.compile(r"\b(?:arbitration .{0,20}(?:seat|venue)|courts? of [A-Z]\w+|laws of [A-Z]\w+)\b"),
}

SENT_SPLIT = re.compile(r"(?<=[.;!?])\s+(?=[A-Z0-9\"“'(§])")


def split_clauses(text):
    text = re.sub(r"\s+", " ", text.strip())
    parts = SENT_SPLIT.split(text)
    return [p.strip() for p in parts if len(p.strip()) > 3]


def tag_topics(clause):
    return [name for name, pat in TOPIC_PATTERNS.items() if pat.search(clause)]


def detect_triggers(clause):
    return [name for name, pat in TRIGGER_PATTERNS.items() if pat.search(clause)]


def scan(text):
    rows = []
    for i, clause in enumerate(split_clauses(text), 1):
        topics = tag_topics(clause)
        redline = bool(REDLINE_RE.search(clause))
        triggers = detect_triggers(clause)
        rows.append({
            "n": i,
            "topics": topics,
            "redline_signal": redline,
            "escalation_triggers": triggers,
            # a clause is worth grading if it maps to a governed topic OR trips a signal
            "needs_grading": bool(topics) or redline or bool(triggers),
            "text": clause,
        })
    return rows


def summarize(rows):
    total = len(rows)
    topic_hits = sum(1 for r in rows if r["topics"])
    redlines = sum(1 for r in rows if r["redline_signal"])
    triggered = sum(1 for r in rows if r["escalation_triggers"])
    return {
        "clauses": total,
        "topic_mapped": topic_hits,
        "redline_signals": redlines,
        "escalation_signals": triggered,
        "needs_grading": sum(1 for r in rows if r["needs_grading"]),
    }


def render_text(rows):
    out = []
    summ = summarize(rows)
    out.append("=== PLAYBOOK-REVIEW WORKLIST (first pass -- human grading required) ===")
    for r in rows:
        topics = ",".join(r["topics"]) if r["topics"] else "-"
        flags = []
        if r["redline_signal"]:
            flags.append("REDLINE?")
        if r["escalation_triggers"]:
            flags.append("TRIGGER:" + ",".join(r["escalation_triggers"]))
        flagstr = " ".join(flags) if flags else ""
        out.append(f"[{r['n']:>3}] topics={topics:<30} {flagstr}")
        out.append(f"       {r['text'][:160]}")
    out.append("")
    out.append(f"clauses={summ['clauses']}  topic_mapped={summ['topic_mapped']}  "
               f"redline_signals={summ['redline_signals']}  "
               f"escalation_signals={summ['escalation_signals']}  "
               f"needs_grading={summ['needs_grading']}")
    out.append("NOTE: a topic tag or redline/trigger signal does NOT mean the clause is a breach or")
    out.append("      within a fallback band. Grade the actual language against the firm's playbook.")
    return "\n".join(out)


def selftest():
    sample = (
        "Vendor shall have unlimited liability for any breach of this Agreement. "
        "Customer shall indemnify and hold harmless the Vendor from all claims. "
        "This Agreement may be terminated for convenience by Vendor on 30 days notice. "
        "Total fees shall not exceed $750,000 per year. "
        "Personal data may be transferred to a third country outside the EEA. "
        "Customer grants an irrevocable, perpetual licence to all work product. "
        "This Agreement is governed by the laws of Singapore. "
        "Vendor is granted exclusivity as the most-favored customer."
    )
    rows = scan(sample)
    summ = summarize(rows)
    assert summ["clauses"] >= 6, summ
    # topic tagging
    assert any("liability" in r["topics"] for r in rows), "expected a liability clause"
    assert any("indemnity" in r["topics"] for r in rows), "expected an indemnity clause"
    assert any("termination" in r["topics"] for r in rows), "expected a termination clause"
    assert any("data_protection" in r["topics"] for r in rows), "expected a data clause"
    # redline signals ("unlimited liability", "irrevocable", "perpetual", "hold harmless")
    assert summ["redline_signals"] >= 2, summ
    # escalation triggers: dollar threshold, cross-border, exclusivity/MFN, foreign forum
    assert any("dollar_threshold" in r["escalation_triggers"] for r in rows), "expected $ trigger"
    assert any("cross_border_data" in r["escalation_triggers"] for r in rows), "expected cross-border trigger"
    assert any("exclusivity" in r["escalation_triggers"] for r in rows), "expected exclusivity trigger"
    # every flagged clause is marked for grading
    assert all(r["needs_grading"] for r in rows if r["topics"] or r["redline_signal"] or r["escalation_triggers"]), summ
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="First-pass clause/trigger scanner for playbook review (stdlib only).")
    ap.add_argument("--file", help="Path to a plaintext contract. Omit to read stdin.")
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

    rows = scan(text)
    if args.format == "json":
        print(json.dumps({"summary": summarize(rows), "rows": rows}, ensure_ascii=False, indent=2))
    else:
        print(render_text(rows))


if __name__ == "__main__":
    main()
