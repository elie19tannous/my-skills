#!/usr/bin/env python3
"""Offline first-pass claim/citation scanner (stdlib only, no network).

Splits plaintext into candidate claims, detects whether each carries a citation
marker (footnote ref, parenthetical, Bates/exhibit ref, URL, statute/section
pattern), and outputs a worklist separating citation-bearing from citation-free
sentences with a rough type guess.

This flags candidates for HUMAN grading. It does NOT and cannot judge whether a
cited source actually supports a claim -- that requires reading the source.

Usage:
    python claim_scanner.py --file brief.txt
    python claim_scanner.py --file brief.txt --format json
    echo "text..." | python claim_scanner.py
    python claim_scanner.py --selftest
"""
import argparse
import json
import re
import sys

# --- citation marker patterns (pattern-based; will miss unusual styles) ---
CITE_PATTERNS = {
    "footnote": re.compile(r"(?<!\w)\[\d{1,3}\]|(?<=\w)\d{1,3}(?=\s*$)"),
    "parenthetical": re.compile(r"\((?:see|cf\.|e\.g\.|Ex\.|Exhibit|id\.|supra|infra)[^)]*\)", re.I),
    "bates_exhibit": re.compile(r"\b(?:Ex(?:hibit)?\.?\s*\d+|Bates[\s_-]?\w*\d+|[A-Z]{2,5}[-_]?\d{4,})\b"),
    "url": re.compile(r"https?://\S+"),
    "statute": re.compile(r"\b(?:§+\s*\d+|[Ss]ection\s+\d+|art(?:icle)?\.?\s*\d+|\d+\s+U\.S\.C\.)\b"),
    "case_cite": re.compile(r"\bv\.\s+[A-Z]\w+|\d+\s+[A-Z][a-z]+\.?\s+\d+"),
}

# --- rough claim-type heuristics ---
QUANT_RE = re.compile(r"\b\d[\d,]*\.?\d*\s*(?:%|percent|million|billion|thousand|[$€£₪])|\b[$€£₪]\s?\d|\b\d{1,2}\s+\w+\s+\d{4}\b|\b\d{4}\b")
QUOTE_RE = re.compile(r"[\"“”'‘’].{3,}[\"“”'‘’]")
LEGAL_RE = re.compile(r"\b(?:shall|pursuant to|section|statute|regulation|clause|article|§)\b", re.I)
ARGUMENT_RE = re.compile(r"\b(?:clearly|therefore|thus|obviously|it follows|we submit|in our view|arguably|plainly)\b", re.I)

SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"“'(])")


def split_sentences(text):
    # normalize whitespace, split on sentence boundaries; keep non-trivial spans
    text = re.sub(r"\s+", " ", text.strip())
    parts = SENT_SPLIT.split(text)
    return [p.strip() for p in parts if len(p.strip()) > 3]


def detect_citations(sentence):
    hits = []
    for name, pat in CITE_PATTERNS.items():
        if pat.search(sentence):
            hits.append(name)
    return hits


def guess_type(sentence):
    # order matters: quotation > quantity > legal > argument > fact
    if QUOTE_RE.search(sentence):
        return "quotation"
    if QUANT_RE.search(sentence):
        return "quantity"
    if LEGAL_RE.search(sentence):
        return "law"
    if ARGUMENT_RE.search(sentence):
        return "argument"  # likely exempt, but may hide a factual premise
    return "fact"


def scan(text):
    rows = []
    for i, sent in enumerate(split_sentences(text), 1):
        cites = detect_citations(sent)
        ctype = guess_type(sent)
        rows.append({
            "n": i,
            "type": ctype,
            "cited": bool(cites),
            "citation_markers": cites,
            "needs_review": ctype != "argument",  # argument is candidate-exempt
            "text": sent,
        })
    return rows


def summarize(rows):
    total = len(rows)
    cited = sum(1 for r in rows if r["cited"])
    uncited_facts = sum(1 for r in rows if not r["cited"] and r["type"] != "argument")
    return {
        "sentences": total,
        "cited": cited,
        "uncited": total - cited,
        "uncited_needing_source": uncited_facts,
        "argument_candidate_exempt": sum(1 for r in rows if r["type"] == "argument"),
    }


def render_text(rows):
    out = []
    summ = summarize(rows)
    out.append("=== CLAIM/CITATION WORKLIST (first pass -- human grading required) ===")
    for r in rows:
        flag = "CITED " if r["cited"] else "UNCITED"
        markers = ",".join(r["citation_markers"]) if r["citation_markers"] else "-"
        out.append(f"[{r['n']:>3}] {flag} type={r['type']:<9} markers={markers}")
        out.append(f"       {r['text'][:160]}")
    out.append("")
    out.append(f"sentences={summ['sentences']}  cited={summ['cited']}  "
               f"uncited={summ['uncited']}  uncited_needing_source={summ['uncited_needing_source']}  "
               f"argument_candidate_exempt={summ['argument_candidate_exempt']}")
    out.append("NOTE: a citation marker does NOT mean the source supports the claim. Grade support by reading the source.")
    return "\n".join(out)


def selftest():
    sample = (
        'The contract was signed on 3 March 2024 for $2.4M (Ex. 12). '
        'Revenue fell 12% in Q3. '
        'The email stated "we will not proceed." '
        'Section 7 requires 30 days notice pursuant to the agreement. '
        'Clearly the defendant acted in bad faith. '
        'See https://example.com/report for details.'
    )
    rows = scan(sample)
    summ = summarize(rows)
    assert summ["sentences"] >= 5, summ
    # quantity detection
    assert any(r["type"] == "quantity" for r in rows), "expected a quantity claim"
    # quotation detection
    assert any(r["type"] == "quotation" for r in rows), "expected a quotation claim"
    # law signal present (may be merged into a quotation sentence in this sample)
    assert any("statute" in r["citation_markers"] for r in rows), "expected a statute marker"
    # argument flagged candidate-exempt
    assert any(r["type"] == "argument" and not r["needs_review"] for r in rows), "expected argument exempt"
    # at least one cited (Ex. 12 / URL / section)
    assert summ["cited"] >= 2, summ
    # uncited fact present (revenue sentence has quantity but no cite marker)
    assert summ["uncited_needing_source"] >= 1, summ
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="First-pass claim/citation scanner (stdlib only).")
    ap.add_argument("--file", help="Path to a plaintext document. Omit to read stdin.")
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
