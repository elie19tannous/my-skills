#!/usr/bin/env python3
"""
Classify Answers Script
Classify short-text column values into semantic types using a regex priority chain:
binary → roman → integer → float → word/phrase → special chars → other.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path

import pandas as pd


def load_dataframe(path, format="auto", **kwargs):
    """Stub: load a DataFrame from path. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    ext = str(path).rsplit(".", 1)[-1].lower()
    fmt = format if format != "auto" else ext
    if fmt in ("parquet",):
        return pd.read_parquet(path)
    if fmt in ("jsonl", "ndjson"):
        return pd.read_json(path, lines=True)
    if fmt in ("json",):
        return pd.read_json(path)
    if fmt in ("tsv",):
        return pd.read_csv(path, sep="\t", **{k: v for k, v in kwargs.items() if k in ("dtype", "keep_default_na")})
    return pd.read_csv(path, **{k: v for k, v in kwargs.items() if k in ("dtype", "keep_default_na")})

# ── classification regex chain (priority order) ───────────────────────────────
_BINARY_PATTERN     = re.compile(r"^(yes|no|true|false|1|0|y|n|t|f)$", re.IGNORECASE)
_ROMAN_PATTERN      = re.compile(r"^(M{0,4})(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$", re.IGNORECASE)
_INTEGER_PATTERN    = re.compile(r"^-?\d+$")
_FLOAT_PATTERN      = re.compile(r"^-?\d+[.,]\d+$")
_SPECIAL_PATTERN    = re.compile(r"^[^a-zA-Z0-9\s]+$")
_WORD_PATTERN       = re.compile(r"^[\w\s\-',.]+$")

TYPE_ORDER = [
    ("binary",   _BINARY_PATTERN),
    ("roman",    _ROMAN_PATTERN),
    ("integer",  _INTEGER_PATTERN),
    ("float",    _FLOAT_PATTERN),
    ("special",  _SPECIAL_PATTERN),
    ("phrase",   _WORD_PATTERN),
]


def classify_value(val: str) -> str:
    """Return the semantic type of a single string value."""
    v = val.strip()
    if not v:
        return "empty"
    for type_name, pattern in TYPE_ORDER:
        if pattern.fullmatch(v):
            return type_name
    return "other"


def classify_answers(
    input_path: str,
    output_path: str,
    column: str | None = None,
    input_format: str = "auto",
    sample: int | None = None,
) -> dict:
    t0 = time.time()
    df = load_dataframe(input_path, format=input_format)

    # Select target column
    text_cols = df.select_dtypes(include=["object"]).columns.tolist()
    if not text_cols:
        result = {"success": False, "error": "No text columns found", "rows_in": len(df)}
        with open(output_path, "w") as f:
            json.dump(result, f, indent=2)
        return result

    if column and column in df.columns:
        target_col = column
    elif column:
        # Try case-insensitive match
        match = next((c for c in df.columns if c.lower() == column.lower()), None)
        target_col = match or text_cols[0]
    else:
        # Prefer short-text columns named answer/response/output/result/label
        answer_names = {"answer", "response", "output", "result", "target", "label"}
        preferred = [c for c in text_cols if c.lower() in answer_names]
        short_cols = [
            c for c in text_cols
            if df[c].dropna().astype(str).str.len().mean() < 60
        ]
        target_col = (preferred or short_cols or text_cols)[0]

    series = df[target_col].dropna().astype(str)
    if sample and len(series) > sample:
        series = series.sample(n=sample, random_state=42)

    # Classify each value
    type_counts: Counter = Counter(classify_value(v) for v in series)
    total = len(series)

    breakdown = [
        {
            "type": t,
            "count": type_counts.get(t, 0),
            "pct": round(type_counts.get(t, 0) / max(total, 1) * 100, 2),
        }
        for t in ["binary", "roman", "integer", "float", "phrase", "special", "empty", "other"]
        if type_counts.get(t, 0) > 0
    ]
    breakdown.sort(key=lambda x: -x["count"])

    dominant = breakdown[0]["type"] if breakdown else "other"
    mixed = len([b for b in breakdown if b["pct"] > 5]) > 2

    result = {
        "success": True,
        "column": target_col,
        "rows_in": len(df),
        "values_classified": total,
        "dominant_type": dominant,
        "mixed_types": mixed,
        "breakdown": breakdown,
        "elapsed_seconds": round(time.time() - t0, 3),
    }

    # Add sample examples per type
    examples: dict[str, list] = {}
    type_series_map: dict[str, list] = {}
    for v in series:
        t = classify_value(v)
        type_series_map.setdefault(t, []).append(v)
    for t, vals in type_series_map.items():
        examples[t] = vals[:3]
    result["examples"] = examples

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)

    return result


def main():
    parser = argparse.ArgumentParser(
        description="Classify short-text column values by semantic type"
    )
    parser.add_argument("--input", required=True, help="Input data file path")
    parser.add_argument("--output", default="logs/classification.json", help="Output JSON report path (default: logs/classification.json)")
    parser.add_argument("--column", default=None, help="Column to classify (default: auto-select)")
    parser.add_argument("--sample", type=int, default=None, help="Max rows to sample")
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
    )
    args = parser.parse_args()

    result = classify_answers(
        input_path=args.input,
        output_path=args.output,
        column=args.column,
        input_format=args.input_format,
        sample=args.sample,
    )

    if result.get("success"):
        print(
            f"[classify_answers] column={result['column']} "
            f"dominant={result['dominant_type']} "
            f"mixed={result['mixed_types']} "
            f"types={len(result['breakdown'])} → {args.output}"
        )
    else:
        print(f"[classify_answers] ERROR: {result.get('error')}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
