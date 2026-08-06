#!/usr/bin/env python3
"""
deep_quality_analysis.py — 3-Level Progressive Data Quality Analysis
=====================================================================
Level 1 (surface): Missing values, empty strings, sentinel detection (exact), basic stats
Level 2 (pattern): Regex sentinels, CJK checks, length anomalies, frequency flags, pattern extraction
Level 3 (deep): Rich diagnostics — sampled values, cross-column consistency,
                 suggested regex patterns, anomaly flags with recommended actions
                 (All deterministic — NO LLM calls)
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

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
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)

def format_success(output_path=None, rows_in=0, rows_out=0, summary=None, warnings=None):
    """Stub: format a success result dict. See magic-data-lifecycle SKILL.md for full pattern."""
    return {"success": True, "output_path": output_path, "rows_in": rows_in, "rows_out": rows_out, "summary": summary or {}, "warnings": warnings or []}
def format_error(message, suggestion=None, rows_in=None):
    """Stub: format an error result dict."""
    import sys
    result = {"success": False, "error": message}
    if suggestion:
        result["suggestion"] = suggestion
    if rows_in is not None:
        result["rows_in"] = rows_in
    print(result, file=sys.stderr)
    sys.exit(1)
def output_result(result):
    """Stub: print result JSON and exit."""
    import json, sys
    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result.get("success") else 1)
def maybe_checkpoint(path, tag, save=True, checkpoint_format=None, metadata=None):
    """Stub: save checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    return None

try:
    from sentinel_patterns import detect_sentinels, is_cjk_dominant
except ImportError:
    _EXACT_SENTINELS = {"N/A", "NA", "n/a", "na", "N/a", "None", "none", "NONE", "null", "NULL", "Null", "NaN", "nan", "NAN", "-", "--", "---", ".", "..", "...", "?", "??", "???", "TBD", "tbd", "TODO", "todo", "MISSING", "missing", "Missing", "UNKNOWN", "unknown", "Unknown", "X", "x", "placeholder", "Placeholder", "PLACEHOLDER"}
    def detect_sentinels(series, mode="exact"):
        """Stub: detect sentinel values in a series. See magic-data-profiling SKILL.md for full pattern."""
        count = int(series.isin(_EXACT_SENTINELS).sum())
        return {"sentinel_count": count, "sentinel_rate": round(count / max(len(series), 1), 4), "matched_values": {v: int((series == v).sum()) for v in _EXACT_SENTINELS if (series == v).any()}}
    def is_cjk_dominant(series):
        """Stub: detect if a series is CJK-dominant."""
        def _cjk(text):
            if not text:
                return False
            cjk = sum(1 for c in str(text) if '一' <= c <= '鿿')
            return cjk / max(len(str(text)), 1) > 0.3
        sample = series.dropna().astype(str).head(100)
        if len(sample) == 0:
            return False
        return sample.apply(_cjk).mean() > 0.5

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    stream=sys.stderr,
)
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Level 1: Surface Analysis
# ---------------------------------------------------------------------------

def analyze_surface(df, columns):
    """
    Level 1 — quick structural scan.

    Returns dict with keys: missing, sentinels, basic_stats.
    """
    missing = {}
    sentinels = {}
    basic_stats = {}

    for col in columns:
        series = df[col]

        # Missing counts
        missing[col] = {
            "null_count": int(series.isna().sum()),
            "empty_count": int((series.astype(str).str.strip() == "").sum()),
            "null_rate": round(series.isna().mean(), 4),
        }

        # Sentinel detection (exact mode) — stringify first to handle nested types
        try:
            sentinels[col] = detect_sentinels(series, mode="exact")
        except TypeError:
            sentinels[col] = detect_sentinels(series.astype(str), mode="exact")

        # Basic stats — guard against columns with unhashable values (dict/list)
        try:
            unique_count = int(series.nunique())
        except TypeError:
            unique_count = -1  # unhashable type (nested dict/list); skip uniqueness

        basic_stats[col] = {
            "count": len(series),
            "unique": unique_count,
            "dtype": str(series.dtype),
            "null_rate": round(series.isna().mean(), 4),
        }
        non_null = series.dropna()
        if len(non_null) > 0:
            try:
                top = non_null.value_counts().head(1)
                basic_stats[col]["top_value"] = str(top.index[0]) if len(top) > 0 else None
                basic_stats[col]["top_freq"] = int(top.values[0]) if len(top) > 0 else 0
            except TypeError:
                # Column contains unhashable values (nested dict/list) — stringify first
                str_top = non_null.astype(str).value_counts().head(1)
                basic_stats[col]["top_value"] = str(str_top.index[0]) if len(str_top) > 0 else None
                basic_stats[col]["top_freq"] = int(str_top.values[0]) if len(str_top) > 0 else 0

    return {"missing": missing, "sentinels": sentinels, "basic_stats": basic_stats}


# ---------------------------------------------------------------------------
# Level 2: Pattern Analysis
# ---------------------------------------------------------------------------

def analyze_patterns(df, columns, cjk_aware=True):
    """
    Level 2 — regex sentinels, CJK detection, length anomalies,
    frequency flags, and pattern extraction.
    """
    regex_sentinels = {}
    cjk_columns = []
    length_anomalies = {}
    frequency_flags = {}
    detected_patterns = {}

    for col in columns:
        series = df[col]

        # Regex sentinels
        try:
            regex_sentinels[col] = detect_sentinels(series, mode="regex")
        except TypeError:
            regex_sentinels[col] = detect_sentinels(series.astype(str), mode="regex")

        # CJK detection
        if cjk_aware and is_cjk_dominant(series):
            cjk_columns.append(col)

        # Length anomalies (z-score based)
        str_series = series.dropna().astype(str)
        lengths = str_series.str.len()
        if len(lengths) > 1:
            mean_len = lengths.mean()
            std_len = lengths.std()
            if std_len > 0:
                short_mask = lengths < (mean_len - 2 * std_len)
                long_mask = lengths > (mean_len + 3 * std_len)
                if short_mask.any() or long_mask.any():
                    length_anomalies[col] = {
                        "mean_length": round(mean_len, 1),
                        "std_length": round(std_len, 1),
                        "short_count": int(short_mask.sum()),
                        "long_count": int(long_mask.sum()),
                        "short_samples": str_series[short_mask].head(5).tolist(),
                        "long_samples": str_series[long_mask].head(5).tolist(),
                    }

        # Frequency flags (values in >5% of rows)
        if len(str_series) > 0:
            value_counts = str_series.value_counts()
            threshold = len(str_series) * 0.05
            dominant = value_counts[value_counts > threshold]
            if len(dominant) > 0:
                frequency_flags[col] = {v: int(c) for v, c in dominant.head(10).items()}

        # Pattern extraction
        patterns_found = {}
        email_count = int(str_series.str.match(r'^[\w.+-]+@[\w-]+\.[\w.]+$').sum())
        if email_count > 0:
            patterns_found["email"] = email_count
        url_count = int(str_series.str.match(r'^https?://').sum())
        if url_count > 0:
            patterns_found["url"] = url_count
        numeric_count = int(str_series.str.match(r'^\d+\.?\d*$').sum())
        if numeric_count > 0:
            patterns_found["numeric_string"] = numeric_count
        if patterns_found:
            detected_patterns[col] = patterns_found

    return {
        "regex_sentinels": regex_sentinels,
        "cjk_columns": cjk_columns,
        "length_anomalies": length_anomalies,
        "frequency_flags": frequency_flags,
        "detected_patterns": detected_patterns,
    }


# ---------------------------------------------------------------------------
# Level 3: Deep Analysis
# ---------------------------------------------------------------------------

def analyze_deep(df, columns, surface_results, pattern_results):
    """
    Level 3 — rich diagnostics: sampled values, cross-column consistency,
    suggested regex patterns, anomaly flags with recommended actions.
    """
    sampled_values = {}
    cross_column_issues = []
    suggested_regex = {}
    value_distributions = {}
    anomaly_flags = []

    for col in columns:
        series = df[col].dropna()
        str_series = series.astype(str)

        # Sampled values (20-50 representative values)
        sample_size = min(50, len(str_series))
        if sample_size > 0:
            sampled_values[col] = str_series.sample(n=sample_size, random_state=42).tolist()

        # Value distributions
        vc = str_series.value_counts()
        value_distributions[col] = {
            "top_10": {str(k): int(v) for k, v in vc.head(10).items()},
            "unique_ratio": round(str_series.nunique() / len(str_series), 4) if len(str_series) > 0 else 0,
            "length_stats": {
                "min": int(str_series.str.len().min()) if len(str_series) > 0 else 0,
                "max": int(str_series.str.len().max()) if len(str_series) > 0 else 0,
                "mean": round(str_series.str.len().mean(), 1) if len(str_series) > 0 else 0,
            },
        }

        # Suggested regex based on dominant patterns
        if len(str_series) > 10:
            # Check if most values follow a common length pattern
            lengths = str_series.str.len()
            mode_vals = lengths.mode()
            mode_len = int(mode_vals.iloc[0]) if len(mode_vals) > 0 else 0
            mode_pct = (lengths == mode_len).mean()
            if mode_pct > 0.5 and mode_len > 0:
                suggested_regex[col] = f"^.{{{mode_len}}}$"

        # Generate anomaly flags
        sentinel_data = surface_results.get("sentinels", {}).get(col, {})
        sentinel_rate = sentinel_data.get("sentinel_rate", 0)
        if sentinel_rate > 0.01:
            anomaly_flags.append({
                "column": col,
                "issue_type": "sentinel_values",
                "sample_values": list(sentinel_data.get("matched_values", {}).keys())[:10],
                "suggested_action": "FILL" if sentinel_rate < 0.1 else "FLAG",
                "severity": "HIGH" if sentinel_rate > 0.1 else "MEDIUM",
                "investigation_hint": f"Column has {sentinel_rate:.1%} sentinel values — review if these should be filled or removed",
            })

        # Check for very low uniqueness (possible data quality issue)
        unique_ratio = value_distributions[col]["unique_ratio"]
        if unique_ratio < 0.01 and len(str_series) > 100:
            top_val = list(value_distributions[col]["top_10"].keys())[0] if value_distributions[col]["top_10"] else "?"
            anomaly_flags.append({
                "column": col,
                "issue_type": "low_uniqueness",
                "sample_values": list(value_distributions[col]["top_10"].keys())[:5],
                "suggested_action": "FLAG",
                "severity": "LOW",
                "investigation_hint": f"Column has very low uniqueness ({unique_ratio:.1%}) — dominated by '{top_val}'",
            })

    # Cross-column consistency checks
    # pandas 3.x uses dtype 'str' for string columns; handle both old and new dtype
    text_cols = [c for c in columns if df[c].dtype == object or pd.api.types.is_string_dtype(df[c])]
    if len(text_cols) >= 2:
        for i, col_a in enumerate(text_cols):
            for col_b in text_cols[i + 1:]:
                len_a = df[col_a].dropna().astype(str).str.len().mean()
                len_b = df[col_b].dropna().astype(str).str.len().mean()
                if len_a > 0 and len_b > 0:
                    ratio = max(len_a, len_b) / min(len_a, len_b)
                    if ratio > 20:
                        cross_column_issues.append({
                            "columns": [col_a, col_b],
                            "issue": "length_disparity",
                            "detail": f"Average lengths differ by {ratio:.0f}x ({col_a}: {len_a:.0f}, {col_b}: {len_b:.0f})",
                        })

    return {
        "sampled_values": sampled_values,
        "cross_column_issues": cross_column_issues,
        "suggested_regex": suggested_regex,
        "value_distributions": value_distributions,
        "anomaly_flags": anomaly_flags,
    }


# ---------------------------------------------------------------------------
# Summary Builder
# ---------------------------------------------------------------------------

def build_summary(surface_results, pattern_results, deep_results, depth):
    """
    Build a top-level summary aggregating issue counts, severity breakdown,
    and a list of columns that need investigation.
    """
    total_issues = 0
    by_severity = {"HIGH": 0, "MEDIUM": 0, "LOW": 0}
    investigation_needed = []

    # Count sentinel issues from surface results
    for col, sentinel_data in surface_results.get("sentinels", {}).items():
        sentinel_count = sentinel_data.get("sentinel_count", 0)
        if sentinel_count > 0:
            total_issues += 1

    # Count missing-value issues
    for col, missing_data in surface_results.get("missing", {}).items():
        if missing_data.get("null_rate", 0) > 0.05:
            total_issues += 1
            by_severity["MEDIUM"] += 1
            if col not in investigation_needed:
                investigation_needed.append(col)

    # Count pattern-level issues
    if pattern_results:
        for col in pattern_results.get("length_anomalies", {}):
            total_issues += 1
            by_severity["LOW"] += 1
            if col not in investigation_needed:
                investigation_needed.append(col)

    # Count deep-level anomaly flags
    if deep_results:
        for flag in deep_results.get("anomaly_flags", []):
            total_issues += 1
            severity = flag.get("severity", "LOW")
            by_severity[severity] = by_severity.get(severity, 0) + 1
            col = flag.get("column")
            if col and col not in investigation_needed:
                investigation_needed.append(col)

        for issue in deep_results.get("cross_column_issues", []):
            total_issues += 1
            by_severity["LOW"] += 1

    return {
        "depth": depth,
        "total_issues": total_issues,
        "by_severity": by_severity,
        "investigation_needed": investigation_needed,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "3-Level Progressive Data Quality Analysis. "
            "Surface: missing/sentinels/stats. Pattern: regex/CJK/anomalies. "
            "Deep: sampled values, cross-column checks, suggested regex, anomaly flags."
        ),
    )
    parser.add_argument("input_path", help="Path to input data file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument(
        "--depth",
        choices=["surface", "pattern", "deep"],
        default="surface",
        help="Analysis depth level (default: surface)",
    )
    parser.add_argument(
        "--columns",
        default=None,
        help="Comma-separated list of columns to analyze (default: all)",
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        help="Sample N rows for analysis (default: use all rows)",
    )
    parser.add_argument(
        "--cjk-aware",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Enable CJK-aware analysis (default: enabled)",
    )
    parser.add_argument(
        "--auto-checkpoint",
        action="store_true",
        default=False,
        help="Save a checkpoint copy of the output file",
    )
    parser.add_argument(
        "--checkpoint-format",
        choices=["csv", "parquet", "jsonl"],
        default=None,
        help="Format for checkpoint files (default: same as output format)",
    )

    args = parser.parse_args()
    _start_time = time.time()

    # ── Load data ─────────────────────────────────────────────
    try:
        df = load_dataframe(args.input_path)
    except Exception as exc:
        output_result(format_error(
            f"Failed to load input file: {exc}",
            suggestion="Check file path, format, and encoding",
        ))

    rows_in = len(df)

    # ── Column selection ──────────────────────────────────────
    if args.columns:
        requested = [c.strip() for c in args.columns.split(",")]
        missing_cols = [c for c in requested if c not in df.columns]
        if missing_cols:
            output_result(format_error(
                f"Columns not found in data: {missing_cols}",
                suggestion=f"Available columns: {list(df.columns)}",
                rows_in=rows_in,
            ))
        columns = requested
    else:
        columns = list(df.columns)

    # ── Row sampling ──────────────────────────────────────────
    if args.sample and args.sample < len(df):
        df = df.sample(n=args.sample, random_state=42).reset_index(drop=True)
        log.info("Sampled %d rows from %d total", args.sample, rows_in)

    # ── Level 1: Surface (always runs) ────────────────────────
    log.info("Running Level 1 (surface) analysis on %d columns", len(columns))
    surface_results = analyze_surface(df, columns)

    # ── Level 2: Pattern (if depth >= pattern) ────────────────
    pattern_results = None
    if args.depth in ("pattern", "deep"):
        log.info("Running Level 2 (pattern) analysis")
        pattern_results = analyze_patterns(df, columns, cjk_aware=args.cjk_aware)

    # ── Level 3: Deep (if depth == deep) ──────────────────────
    deep_results = None
    if args.depth == "deep":
        log.info("Running Level 3 (deep) analysis")
        deep_results = analyze_deep(df, columns, surface_results, pattern_results)

    # ── Build summary ─────────────────────────────────────────
    summary = build_summary(surface_results, pattern_results, deep_results, args.depth)
    summary["rows_analyzed"] = len(df)
    summary["columns_analyzed"] = len(columns)

    # ── Assemble output ───────────────────────────────────────
    output_data = {
        "depth": args.depth,
        "surface": surface_results,
    }
    if pattern_results is not None:
        output_data["pattern"] = pattern_results
    if deep_results is not None:
        output_data["deep"] = deep_results

    warnings = []
    if args.sample and args.sample < rows_in:
        warnings.append(f"Results based on {args.sample}-row sample of {rows_in} total rows")

    # ── Write output file ─────────────────────────────────────
    try:
        Path(args.output_path).parent.mkdir(parents=True, exist_ok=True)
        result = format_success(
            output_path=args.output_path,
            rows_in=rows_in,
            rows_out=len(df),
            summary=summary,
            warnings=warnings,
        )
        result["analysis"] = output_data

        with open(args.output_path, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)

    except Exception as exc:
        output_result(format_error(
            f"Failed to write output file: {exc}",
            suggestion="Check disk space and write permissions",
            rows_in=rows_in,
        ))

    # ── Checkpoint ────────────────────────────────────────────
    if args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": rows_in,
            "rows_out": len(df),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(
            args.output_path, "deep_quality", True,
            checkpoint_format=args.checkpoint_format,
            metadata=meta,
        )
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    output_result(result)


if __name__ == "__main__":
    main()
