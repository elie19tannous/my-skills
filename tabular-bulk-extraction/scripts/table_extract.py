#!/usr/bin/env python3
"""Offline first-pass tabular extraction helper (stdlib only, no network).

Reads a delimited table (CSV / TSV / pipe) or a simple JSON array of objects,
sniffs the delimiter, coerces columns to money / date / integer / text using
conservative rules, and reports per-column blank counts plus anomalies
(ambiguous dates, non-numeric money cells, ragged rows). It can emit a
normalized table as CSV or JSON.

This flags candidates for HUMAN review. It does NOT reconcile totals, convert
currencies, OCR scanned images, or guess missing values -- a cell it cannot
read cleanly is reported as a flagged blank, never a plausible number.

Usage:
    python table_extract.py --file invoices.csv
    python table_extract.py --file data.json --format json
    echo "a,b\\n1,2" | python table_extract.py
    python table_extract.py --selftest
"""
import argparse
import csv
import io
import json
import re
import sys

# --- money: US 1,234.50 and EU 1.234,50; parenthesized/CR-DR negatives ---
_MONEY_RE = re.compile(r"^[\s$€£₪]*\(?-?[\d.,]+\)?\s*(?:CR|DR)?[\s$€£₪]*$", re.I)
_DATE_RE = re.compile(r"^\s*(\d{1,4})[/.\-](\d{1,2})[/.\-](\d{1,4})\s*$")
_INT_RE = re.compile(r"^\s*-?\d+\s*$")
_BLANKS = {"", "n/a", "na", "-", "--", "none", "null"}


def sniff_delimiter(sample):
    """Return the most likely delimiter among , \\t | ; using csv.Sniffer, with a fallback."""
    try:
        return csv.Sniffer().sniff(sample, delimiters=",\t|;").delimiter
    except csv.Error:
        counts = {d: sample.count(d) for d in [",", "\t", "|", ";"]}
        best = max(counts, key=counts.get)
        return best if counts[best] else ","


def is_blank(v):
    return v is None or str(v).strip().lower() in _BLANKS


def normalize_money(v):
    """Return (value_or_None, ok). Handles US/EU separators, (x)/CR/DR negatives."""
    s = str(v).strip()
    neg = s.startswith("(") and s.endswith(")") or re.search(r"\b(?:CR)\b|-", s, re.I)
    s2 = re.sub(r"[()\s$€£₪]|CR|DR", "", s, flags=re.I)
    if not s2:
        return None, False
    # decide separator convention: last-seen of . or , that has 1-2 trailing digits is decimal
    if "," in s2 and "." in s2:
        if s2.rfind(",") > s2.rfind("."):        # EU: . thousands, , decimal
            s2 = s2.replace(".", "").replace(",", ".")
        else:                                     # US: , thousands, . decimal
            s2 = s2.replace(",", "")
    elif "," in s2:
        # comma only: treat as decimal if exactly one comma with <=2 trailing digits, else thousands
        if re.match(r"^\d+,\d{1,2}$", s2):
            s2 = s2.replace(",", ".")
        else:
            s2 = s2.replace(",", "")
    try:
        val = float(s2)
    except ValueError:
        return None, False
    return (-abs(val) if neg else val), True


def normalize_date(v):
    """Return (iso_or_None, ambiguous). ISO if resolvable, flag ambiguity for DD/MM vs MM/DD."""
    m = _DATE_RE.match(str(v))
    if not m:
        return None, False
    a, b, c = (int(x) for x in m.groups())
    # normalize year position
    if a > 31:            # YYYY-MM-DD
        y, mo, d = a, b, c
        return _iso(y, mo, d), False
    # a,b are day/month in some order; c is year
    y = c if c > 99 else 2000 + c
    if a > 12 and b <= 12:      # a must be day
        return _iso(y, b, a), False
    if b > 12 and a <= 12:      # b must be day
        return _iso(y, a, b), False
    # both <= 12: genuinely ambiguous
    return _iso(y, a, b), True


def _iso(y, mo, d):
    if not (1 <= mo <= 12 and 1 <= d <= 31):
        return None
    return f"{y:04d}-{mo:02d}-{d:02d}"


def guess_type(values):
    """Guess a column type from its non-blank sample values.

    Uses a majority (>=60%) vote rather than requiring every cell to pass, so a
    single unreadable cell does not strip a column of its type -- the bad cell is
    surfaced separately as an anomaly instead.
    """
    vals = [str(v).strip() for v in values if not is_blank(v)]
    if not vals:
        return "text"
    n = len(vals)
    def frac(pred):
        return sum(1 for v in vals if pred(v)) / n

    all_int = all(_INT_RE.match(v) for v in vals)
    if all_int:
        return "integer"
    if frac(lambda v: _DATE_RE.match(v)) >= 0.6:
        return "date"
    money_has_sep = any(re.search(r"[.,]|[$€£₪]", v) for v in vals)
    if money_has_sep and frac(lambda v: normalize_money(v)[1]) >= 0.6:
        return "money"
    if frac(lambda v: _INT_RE.match(v)) >= 0.6:
        return "integer"
    return "text"


def load_rows(text):
    """Return (headers, list[dict]) from JSON array or delimited text."""
    stripped = text.lstrip()
    if stripped.startswith("["):
        data = json.loads(text)
        headers = list(data[0].keys()) if data else []
        return headers, [dict(r) for r in data]
    delim = sniff_delimiter(text[:2048])
    reader = csv.reader(io.StringIO(text), delimiter=delim)
    rows = [r for r in reader if any(c.strip() for c in r)]
    if not rows:
        return [], []
    headers = [h.strip() for h in rows[0]]
    out = []
    for r in rows[1:]:
        out.append({headers[i]: (r[i] if i < len(r) else "") for i in range(len(headers))})
    return headers, out


def analyze(headers, rows):
    col_types = {h: guess_type([r.get(h) for r in rows]) for h in headers}
    blanks = {h: sum(1 for r in rows if is_blank(r.get(h))) for h in headers}
    anomalies = []
    for i, r in enumerate(rows, 1):
        for h in headers:
            v = r.get(h)
            if is_blank(v):
                continue
            t = col_types[h]
            if t == "money" and not normalize_money(v)[1]:
                anomalies.append({"row": i, "col": h, "issue": "non-numeric money cell", "raw": v})
            elif t == "date":
                iso, amb = normalize_date(v)
                if iso is None:
                    anomalies.append({"row": i, "col": h, "issue": "unparseable date", "raw": v})
                elif amb:
                    anomalies.append({"row": i, "col": h, "issue": "ambiguous DD/MM date", "raw": v})
    ragged = sum(1 for r in rows if len(r) != len(headers))
    return {"col_types": col_types, "blanks": blanks, "anomalies": anomalies,
            "rows": len(rows), "ragged_rows": ragged}


def normalize_rows(headers, rows, col_types):
    out = []
    for r in rows:
        nr = {}
        for h in headers:
            v = r.get(h)
            if is_blank(v):
                nr[h] = None
                continue
            t = col_types[h]
            if t == "money":
                val, ok = normalize_money(v)
                nr[h] = val if ok else str(v).strip()
            elif t == "date":
                iso, _ = normalize_date(v)
                nr[h] = iso if iso else str(v).strip()
            elif t == "integer":
                nr[h] = int(str(v).strip()) if _INT_RE.match(str(v).strip()) else str(v).strip()
            else:
                nr[h] = str(v).strip()
        out.append(nr)
    return out


def render_report(a):
    out = ["=== TABULAR EXTRACTION REPORT (first pass -- human review required) ==="]
    out.append(f"rows={a['rows']}  ragged_rows={a['ragged_rows']}")
    out.append("column types: " + ", ".join(f"{h}={t}" for h, t in a["col_types"].items()))
    out.append("blanks per column: " + ", ".join(f"{h}={n}" for h, n in a["blanks"].items()))
    if a["anomalies"]:
        out.append(f"anomalies ({len(a['anomalies'])} flagged for review):")
        for an in a["anomalies"][:50]:
            out.append(f"  row {an['row']} col={an['col']}: {an['issue']} (raw={an['raw']!r})")
    else:
        out.append("anomalies: none detected")
    out.append("NOTE: flagged cells are NOT resolved. This tool does not reconcile totals, "
               "convert currencies, OCR images, or guess missing values.")
    return "\n".join(out)


def emit_csv(headers, norm_rows):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=headers, extrasaction="ignore")
    w.writeheader()
    for r in norm_rows:
        w.writerow({h: ("" if r.get(h) is None else r.get(h)) for h in headers})
    return buf.getvalue()


def selftest():
    sample = (
        "invoice,date,amount,currency,qty\n"
        "INV-001,03/04/2024,\"1,234.50\",USD,3\n"
        "INV-002,15/04/2024,\"1.000,00\",EUR,5\n"
        "INV-003,2024-05-01,(500),USD,2\n"
        "INV-004,N/A,not-a-number,USD,\n"
    )
    headers, rows = load_rows(sample)
    assert headers == ["invoice", "date", "amount", "currency", "qty"], headers
    assert len(rows) == 4, rows
    a = analyze(headers, rows)
    # amount typed as money
    assert a["col_types"]["amount"] == "money", a["col_types"]
    assert a["col_types"]["qty"] == "integer", a["col_types"]
    # blanks: date has 1 (N/A), qty has 1
    assert a["blanks"]["qty"] == 1, a["blanks"]
    # anomalies: ambiguous 03/04 date + non-numeric money cell
    issues = {an["issue"] for an in a["anomalies"]}
    assert "ambiguous DD/MM date" in issues, issues
    assert "non-numeric money cell" in issues, issues
    # normalization: US 1,234.50 -> 1234.5 ; EU 1.000,00 -> 1000.0 ; (500) -> -500
    norm = normalize_rows(headers, rows, a["col_types"])
    assert norm[0]["amount"] == 1234.5, norm[0]
    assert norm[1]["amount"] == 1000.0, norm[1]
    assert norm[2]["amount"] == -500.0, norm[2]
    # 15/04 disambiguates to 2024-04-15
    assert norm[1]["date"] == "2024-04-15", norm[1]
    # blank qty -> None, emitted as empty in CSV
    assert norm[3]["qty"] is None, norm[3]
    out_csv = emit_csv(headers, norm)
    assert "INV-001" in out_csv and out_csv.count("\n") >= 5, out_csv
    print("selftest OK")


def main():
    ap = argparse.ArgumentParser(description="First-pass tabular extraction helper (stdlib only).")
    ap.add_argument("--file", help="Path to a CSV/TSV/pipe table or JSON array. Omit to read stdin.")
    ap.add_argument("--format", choices=["text", "csv", "json"], default="text",
                    help="text=report (default); csv/json=emit normalized table.")
    ap.add_argument("--selftest", action="store_true", help="Run embedded self-check and exit.")
    args = ap.parse_args()

    if args.selftest:
        selftest()
        return

    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    if not text.strip():
        print("No input. Use --file or pipe via stdin.", file=sys.stderr)
        sys.exit(1)

    headers, rows = load_rows(text)
    a = analyze(headers, rows)
    if args.format == "text":
        print(render_report(a))
    else:
        norm = normalize_rows(headers, rows, a["col_types"])
        if args.format == "csv":
            sys.stdout.write(emit_csv(headers, norm))
        else:
            print(json.dumps({"columns": a["col_types"], "rows": norm,
                              "report": {"blanks": a["blanks"], "anomalies": a["anomalies"]}},
                             ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
