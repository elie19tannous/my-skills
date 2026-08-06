#!/usr/bin/env python3
"""
Content validation script for detecting sentinel/placeholder values and
distribution-based content anomalies.

Provides three detection layers:
  1. Sentinel value detection  - exact matches against known placeholder strings
  2. Distribution-based anomaly detection - flag values far below the mean content length
  3. Content uniformity detection - flag columns where many rows share identical content

Supports random and stratified sampling with confidence-interval extrapolation.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

class _io_utils:
    """Stub module for io_utils. See magic-data-loading SKILL.md for full pattern."""
    @staticmethod
    def load_dataframe(path, **kwargs):
        import pandas as pd
        from pathlib import Path
        p = Path(path)
        if p.suffix == '.parquet': return pd.read_parquet(p)
        if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
        if p.suffix == '.json': return pd.read_json(p)
        return pd.read_csv(p)
    @staticmethod
    def save_dataframe(df, path, **kwargs):
        from pathlib import Path
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        if p.suffix == '.parquet': df.to_parquet(p, index=False)
        elif p.suffix in ('.jsonl', '.json'): df.to_json(p, orient='records', lines=p.suffix == '.jsonl')
        else: df.to_csv(p, index=False)

try:
    from sentinel_patterns import EXACT_SENTINELS, detect_sentinels as _sp_detect_sentinels, is_cjk_dominant
except ImportError:
    EXACT_SENTINELS = {"N/A", "NA", "n/a", "na", "None", "none", "NONE", "null", "NULL", "NaN", "nan", "-", "--", "---", ".", "?", "??", "???", "TBD", "tbd", "TODO", "MISSING", "missing", "Unknown", "unknown", "UNKNOWN", "X", "x", "placeholder", "Placeholder", "PLACEHOLDER"}
    def _sp_detect_sentinels(series):
        """Stub: count sentinel values in series. See magic-data-validation SKILL.md for full pattern."""
        return series.isin(EXACT_SENTINELS).sum()
    def is_cjk_dominant(text):
        """Stub: detect CJK-dominant text. See magic-data-validation SKILL.md for full pattern."""
        if isinstance(text, pd.Series):
            if text.empty:
                return False
            text = text.iloc[0]
        if not text: return False
        cjk = sum(1 for c in str(text) if '一' <= c <= '鿿')
        return cjk / max(len(str(text)), 1) > 0.3


# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

# Fraction of identical values that triggers a uniformity warning
UNIFORMITY_THRESHOLD = 0.10

# Number of standard deviations below the mean to flag as an anomaly
DISTRIBUTION_SIGMA = 3.0

# Maximum number of affected row indices to embed in output (to keep output manageable)
MAX_AFFECTED_ROWS_INLINE = 500

# Maximum number of sample anomaly values to show per column
MAX_SAMPLE_ANOMALIES = 10

# Maximum number of top repeated values to report per column
MAX_TOP_REPEATED = 5


# ──────────────────────────────────────────────────────────────
# Data Loading
# ──────────────────────────────────────────────────────────────

def load_dataframe(path: str, format: str = "auto") -> pd.DataFrame:
    """
    Load a DataFrame, auto-detecting format from file extension.

    Supports: CSV (.csv, .tsv), JSONL (.jsonl), JSON (.json), Parquet (.parquet/.pq),
    Excel (.xlsx/.xls).

    Delegates to io_utils.load_dataframe() for all format handling.
    """
    return _io_utils.load_dataframe(path, format=format)


# ──────────────────────────────────────────────────────────────
# Sampling
# ──────────────────────────────────────────────────────────────

def sample_dataframe(
    df: pd.DataFrame,
    n: int,
    stratify_by: Optional[str] = None,
    random_state: int = 42,
) -> pd.DataFrame:
    """
    Return a sample of at most *n* rows from *df*.

    If *stratify_by* is given, perform proportional stratified sampling so each
    stratum is represented in proportion to its size in the full dataset.
    """
    if n >= len(df):
        return df

    if stratify_by and stratify_by in df.columns:
        # Proportional stratified sample
        strata = df[stratify_by].fillna("__MISSING__")
        counts = strata.value_counts(normalize=True)
        frames = []
        for stratum, proportion in counts.items():
            stratum_df = df[strata == stratum]
            stratum_n = max(1, round(proportion * n))
            stratum_n = min(stratum_n, len(stratum_df))
            frames.append(stratum_df.sample(n=stratum_n, random_state=random_state))
        sampled = pd.concat(frames)
        # Trim to exactly n if rounding pushed us over
        if len(sampled) > n:
            sampled = sampled.sample(n=n, random_state=random_state)
        return sampled.reset_index(drop=True)
    else:
        return df.sample(n=n, random_state=random_state).reset_index(drop=True)


def extrapolation_ci(
    count_in_sample: int,
    sample_size: int,
    population_size: int,
    confidence: float = 0.95,
) -> dict:
    """
    Extrapolate a count from a sample to the full population, with a
    Wilson-score confidence interval.

    Returns a dict with keys: estimated_count, ci_lower, ci_upper, confidence.
    """
    p_hat = count_in_sample / sample_size if sample_size > 0 else 0.0
    # z-score for the requested confidence level (normal approximation)
    z = {0.90: 1.645, 0.95: 1.960, 0.99: 2.576}.get(confidence, 1.960)

    # Wilson score interval for the proportion
    denom = 1 + z ** 2 / sample_size if sample_size > 0 else 1
    center = (p_hat + z ** 2 / (2 * sample_size)) / denom if sample_size > 0 else 0
    margin = (z * math.sqrt(p_hat * (1 - p_hat) / sample_size + z ** 2 / (4 * sample_size ** 2))) / denom if sample_size > 0 else 0

    p_lower = max(0.0, center - margin)
    p_upper = min(1.0, center + margin)

    return {
        "estimated_count": round(p_hat * population_size),
        "ci_lower": round(p_lower * population_size),
        "ci_upper": round(p_upper * population_size),
        "confidence": confidence,
    }


# ──────────────────────────────────────────────────────────────
# Layer 1 – Sentinel Value Detection
# ──────────────────────────────────────────────────────────────

def detect_sentinels(
    df: pd.DataFrame,
    columns: list,
    sentinel_set: frozenset,
    min_content_length: int,
    rows_analyzed: int,
    population_size: int,
    is_sample: bool,
) -> dict:
    """
    Scan *columns* for exact matches to values in *sentinel_set* or strings
    shorter than *min_content_length*.

    Returns a dict conforming to the sentinel_findings schema.
    """
    by_column: dict = {}
    affected_row_indices: list = []
    total_sentinels = 0

    for col in columns:
        if col not in df.columns:
            continue

        series = df[col]
        # Work on string representation of non-null values
        str_series = series.dropna().astype(str)

        # Exact sentinel matches
        sentinel_mask_full = series.index.isin([])  # empty boolean index initially
        sentinel_mask = str_series.isin(sentinel_set)

        # Short-content mask (below min_content_length, excluding empties already NA)
        short_mask = str_series.str.len() < min_content_length

        # Combined: either is a known sentinel OR is suspiciously short
        combined_mask = sentinel_mask | short_mask

        matched_indices = str_series[combined_mask].index.tolist()
        if not matched_indices:
            continue

        # Value breakdown
        matched_values = str_series[combined_mask]
        value_counts = matched_values.value_counts().to_dict()
        value_counts = {str(k): int(v) for k, v in value_counts.items()}

        col_count = len(matched_indices)
        col_pct = round((col_count / rows_analyzed) * 100, 2)

        col_entry: dict = {
            "count": col_count,
            "pct": col_pct,
            "values": value_counts,
        }

        if is_sample:
            col_entry["extrapolation"] = extrapolation_ci(
                col_count, rows_analyzed, population_size
            )

        by_column[col] = col_entry
        total_sentinels += col_count
        affected_row_indices.extend(matched_indices)

    # Deduplicate affected row indices (a row can appear once per affected column)
    affected_rows_unique = sorted(set(affected_row_indices))
    # Trim to MAX_AFFECTED_ROWS_INLINE to avoid bloating the output
    affected_rows_trimmed = affected_rows_unique[:MAX_AFFECTED_ROWS_INLINE]
    truncated = len(affected_rows_unique) > MAX_AFFECTED_ROWS_INLINE

    pct_of_analyzed = round((total_sentinels / rows_analyzed) * 100, 2) if rows_analyzed else 0.0

    # Severity
    if pct_of_analyzed >= 10:
        severity = "HIGH"
    elif pct_of_analyzed >= 2:
        severity = "MEDIUM"
    elif pct_of_analyzed > 0:
        severity = "LOW"
    else:
        severity = "NONE"

    result: dict = {
        "total_sentinels": total_sentinels,
        "pct_of_analyzed": pct_of_analyzed,
        "by_column": by_column,
        "affected_rows": affected_rows_trimmed,
        "severity": severity,
    }
    if truncated:
        result["affected_rows_note"] = (
            f"Showing first {MAX_AFFECTED_ROWS_INLINE} of "
            f"{len(affected_rows_unique)} affected row indices."
        )

    return result


# ──────────────────────────────────────────────────────────────
# Layer 2 – Distribution-Based Anomaly Detection
# ──────────────────────────────────────────────────────────────

def detect_distribution_anomalies(
    df: pd.DataFrame,
    columns: list,
    sigma: float = DISTRIBUTION_SIGMA,
) -> dict:
    """
    For each text column, compute the content-length distribution and flag
    values whose length is more than *sigma* standard deviations below the mean.

    Returns a dict conforming to the distribution_findings schema.
    """
    by_column: dict = {}
    total_anomalies = 0

    for col in columns:
        if col not in df.columns:
            continue

        series = df[col].dropna().astype(str)
        if len(series) < 4:
            # Not enough data to build a meaningful distribution
            continue

        lengths = series.str.len()
        mean_len = float(lengths.mean())
        std_len = float(lengths.std(ddof=1))

        if std_len == 0:
            # All values are the same length — no anomaly possible
            continue

        threshold = mean_len - sigma * std_len

        # Only flag if threshold > 0 to avoid flagging everything as anomalous
        # when the distribution is very tight near zero
        if threshold <= 0:
            # Still compute but only flag extremely short values (length <= 1)
            threshold = 1.0

        anomalous_mask = lengths <= threshold
        anomalous_count = int(anomalous_mask.sum())

        if anomalous_count == 0:
            continue

        sample_anomalies = (
            series[anomalous_mask]
            .unique()
            .tolist()[:MAX_SAMPLE_ANOMALIES]
        )

        by_column[col] = {
            "mean_length": round(mean_len, 1),
            "std_length": round(std_len, 1),
            "anomalous_count": anomalous_count,
            "threshold_length": round(threshold, 1),
            "sample_anomalies": [str(v) for v in sample_anomalies],
        }
        total_anomalies += anomalous_count

    return {
        "anomalies_detected": total_anomalies,
        "by_column": by_column,
    }


# ──────────────────────────────────────────────────────────────
# Layer 3 – Content Uniformity Detection
# ──────────────────────────────────────────────────────────────

def detect_uniformity(
    df: pd.DataFrame,
    columns: list,
    threshold: float = UNIFORMITY_THRESHOLD,
) -> dict:
    """
    For each text column, flag if more than *threshold* fraction of rows share
    the same non-null value.

    Returns a dict conforming to the uniformity_findings schema.
    """
    by_column: dict = {}
    suspicious_columns: list = []

    for col in columns:
        if col not in df.columns:
            continue

        series = df[col].dropna().astype(str)
        if len(series) == 0:
            continue

        value_counts = series.value_counts()
        top_value = value_counts.index[0]
        top_count = int(value_counts.iloc[0])
        top_pct = top_count / len(series)

        if top_pct > threshold:
            suspicious_columns.append(col)
            # Report the top repeated values (up to MAX_TOP_REPEATED)
            top_values = [
                {"value": str(val), "count": int(cnt), "pct": round(cnt / len(series) * 100, 2)}
                for val, cnt in value_counts.head(MAX_TOP_REPEATED).items()
            ]
            by_column[col] = {
                "dominant_value": str(top_value),
                "dominant_count": top_count,
                "dominant_pct": round(top_pct * 100, 2),
                "top_repeated_values": top_values,
            }

    return {
        "suspicious_columns": suspicious_columns,
        "by_column": by_column,
    }


# ──────────────────────────────────────────────────────────────
# Group-level Analysis
# ──────────────────────────────────────────────────────────────

def run_grouped_analysis(
    df: pd.DataFrame,
    group_by: str,
    columns: list,
    sentinel_set: frozenset,
    min_content_length: int,
    run_distribution: bool,
) -> dict:
    """
    Repeat sentinel (and optionally distribution) detection per group,
    returning a compact per-group breakdown.
    """
    if group_by not in df.columns:
        return {"error": f"group-by column '{group_by}' not found in data"}

    groups = df[group_by].dropna().unique()
    group_results: dict = {}

    for group_val in groups:
        group_df = df[df[group_by] == group_val].reset_index(drop=True)
        n = len(group_df)

        sentinel_findings = detect_sentinels(
            group_df,
            columns=columns,
            sentinel_set=sentinel_set,
            min_content_length=min_content_length,
            rows_analyzed=n,
            population_size=n,
            is_sample=False,
        )

        entry: dict = {
            "rows": n,
            "sentinel_total": sentinel_findings["total_sentinels"],
            "sentinel_pct": sentinel_findings["pct_of_analyzed"],
            "severity": sentinel_findings["severity"],
        }

        if run_distribution:
            dist_findings = detect_distribution_anomalies(group_df, columns=columns)
            entry["distribution_anomalies"] = dist_findings["anomalies_detected"]

        group_results[str(group_val)] = entry

    return group_results


# ──────────────────────────────────────────────────────────────
# Recommendation Builder
# ──────────────────────────────────────────────────────────────

def build_recommendation(
    sentinel_count: int,
    sentinel_cols: int,
    distribution_count: int,
    uniformity_cols: int,
) -> str:
    """Compose a human-readable recommendation string."""
    parts = []
    if sentinel_count > 0:
        parts.append(
            f"Review {sentinel_count:,} sentinel value{'s' if sentinel_count != 1 else ''} "
            f"in {sentinel_cols} column{'s' if sentinel_cols != 1 else ''}"
        )
    if distribution_count > 0:
        parts.append(
            f"Investigate {distribution_count:,} distribution anomal{'ies' if distribution_count != 1 else 'y'}"
        )
    if uniformity_cols > 0:
        parts.append(
            f"Inspect {uniformity_cols} column{'s' if uniformity_cols != 1 else ''} with high value uniformity"
        )
    if not parts:
        return "No content issues detected"
    return "; ".join(parts)


# ──────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────

def main(
    input_path: str,
    output_path: str,
    columns: Optional[list] = None,
    sentinel_values: Optional[list] = None,
    min_content_length: int = 3,
    sample_n: Optional[int] = None,
    stratify_by: Optional[str] = None,
    group_by: Optional[str] = None,
    distribution_check: bool = False,
    input_format: str = "auto",
    cjk_aware: bool = True,
    depth: str = "surface",
) -> dict:
    """
    Run the full content validation pipeline and return the result dict.

    Also writes a detailed JSON report to *output_path* and returns the
    summary dict for printing to stdout.
    """
    # ── Load data ────────────────────────────────────────────
    try:
        df_full = load_dataframe(input_path, format=input_format)
    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check that the file path is correct",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Failed to load input file: {exc}",
            "suggestion": "Ensure the file is valid CSV or JSONL",
        }

    if df_full.empty:
        return {
            "success": False,
            "error": "Input file is empty",
            "suggestion": "Provide a non-empty CSV or JSONL file",
        }

    rows_in = len(df_full)

    # ── Resolve columns to analyse ───────────────────────────
    if columns:
        # Validate requested columns exist
        missing_cols = [c for c in columns if c not in df_full.columns]
        if missing_cols:
            return {
                "success": False,
                "error": f"Columns not found in data: {missing_cols}",
                "suggestion": f"Available columns: {list(df_full.columns)}",
            }
        analysis_columns = columns
    else:
        # Default: all object/string columns
        analysis_columns = [
            col for col in df_full.columns
            if df_full[col].dtype == object or pd.api.types.is_string_dtype(df_full[col])
        ]
        if not analysis_columns:
            # Fall back to all columns if no string columns detected
            analysis_columns = list(df_full.columns)

    # ── Build sentinel set ───────────────────────────────────
    if sentinel_values:
        # Custom list replaces (rather than extends) the built-in set when provided
        sentinel_set = frozenset(sentinel_values)
    else:
        sentinel_set = EXACT_SENTINELS

    # ── CJK-aware column detection ─────────────────────────────
    cjk_columns: list = []
    if cjk_aware:
        for col in analysis_columns:
            if col in df_full.columns and is_cjk_dominant(df_full[col]):
                cjk_columns.append(col)

    # ── Sampling ─────────────────────────────────────────────
    is_sample = False
    if sample_n and sample_n < rows_in:
        df = sample_dataframe(df_full, n=sample_n, stratify_by=stratify_by)
        is_sample = True
    else:
        df = df_full

    rows_analyzed = len(df)

    # ── Layer 1: Sentinel detection ──────────────────────────
    # CJK-aware: for CJK-dominant columns, use min_content_length=1
    if cjk_aware and cjk_columns:
        non_cjk_columns = [c for c in analysis_columns if c not in cjk_columns]
        # Run sentinel detection on non-CJK columns with configured min_content_length
        sentinel_findings_non_cjk = detect_sentinels(
            df,
            columns=non_cjk_columns,
            sentinel_set=sentinel_set,
            min_content_length=min_content_length,
            rows_analyzed=rows_analyzed,
            population_size=rows_in,
            is_sample=is_sample,
        ) if non_cjk_columns else {"total_sentinels": 0, "pct_of_analyzed": 0.0, "by_column": {}, "affected_rows": [], "severity": "NONE"}
        # Run sentinel detection on CJK columns with min_content_length=1
        sentinel_findings_cjk = detect_sentinels(
            df,
            columns=cjk_columns,
            sentinel_set=sentinel_set,
            min_content_length=1,
            rows_analyzed=rows_analyzed,
            population_size=rows_in,
            is_sample=is_sample,
        ) if cjk_columns else {"total_sentinels": 0, "pct_of_analyzed": 0.0, "by_column": {}, "affected_rows": [], "severity": "NONE"}
        # Merge findings
        merged_by_column = {}
        merged_by_column.update(sentinel_findings_non_cjk.get("by_column", {}))
        merged_by_column.update(sentinel_findings_cjk.get("by_column", {}))
        merged_total = sentinel_findings_non_cjk["total_sentinels"] + sentinel_findings_cjk["total_sentinels"]
        merged_pct = round((merged_total / rows_analyzed) * 100, 2) if rows_analyzed else 0.0
        merged_rows = sorted(set(sentinel_findings_non_cjk.get("affected_rows", []) + sentinel_findings_cjk.get("affected_rows", [])))
        if merged_pct >= 10:
            merged_severity = "HIGH"
        elif merged_pct >= 2:
            merged_severity = "MEDIUM"
        elif merged_pct > 0:
            merged_severity = "LOW"
        else:
            merged_severity = "NONE"
        sentinel_findings = {
            "total_sentinels": merged_total,
            "pct_of_analyzed": merged_pct,
            "by_column": merged_by_column,
            "affected_rows": merged_rows[:MAX_AFFECTED_ROWS_INLINE],
            "severity": merged_severity,
        }
        if len(merged_rows) > MAX_AFFECTED_ROWS_INLINE:
            sentinel_findings["affected_rows_note"] = (
                f"Showing first {MAX_AFFECTED_ROWS_INLINE} of "
                f"{len(merged_rows)} affected row indices."
            )
    else:
        sentinel_findings = detect_sentinels(
            df,
            columns=analysis_columns,
            sentinel_set=sentinel_set,
            min_content_length=min_content_length,
            rows_analyzed=rows_analyzed,
            population_size=rows_in,
            is_sample=is_sample,
        )

    # ── Layer 2: Distribution anomalies ──────────────────────
    if distribution_check:
        distribution_findings = detect_distribution_anomalies(
            df, columns=analysis_columns
        )
    else:
        distribution_findings = {
            "anomalies_detected": 0,
            "by_column": {},
            "note": "Pass --distribution-check to enable this layer",
        }

    # ── Layer 3: Uniformity detection ───────────────────────
    uniformity_findings = detect_uniformity(df, columns=analysis_columns)

    # ── Group-level breakdown ────────────────────────────────
    group_findings: Optional[dict] = None
    if group_by:
        group_findings = run_grouped_analysis(
            df,
            group_by=group_by,
            columns=analysis_columns,
            sentinel_set=sentinel_set,
            min_content_length=min_content_length,
            run_distribution=distribution_check,
        )

    # ── Summary ──────────────────────────────────────────────
    total_issues = (
        sentinel_findings["total_sentinels"]
        + distribution_findings["anomalies_detected"]
        + len(uniformity_findings["suspicious_columns"])
    )

    recommendation = build_recommendation(
        sentinel_count=sentinel_findings["total_sentinels"],
        sentinel_cols=len(sentinel_findings["by_column"]),
        distribution_count=distribution_findings["anomalies_detected"],
        uniformity_cols=len(uniformity_findings["suspicious_columns"]),
    )

    summary = {
        "total_issues": total_issues,
        "sentinel_issues": sentinel_findings["total_sentinels"],
        "distribution_anomalies": distribution_findings["anomalies_detected"],
        "uniformity_issues": len(uniformity_findings["suspicious_columns"]),
        "recommendation": recommendation,
    }

    # ── Assemble full result ─────────────────────────────────
    result: dict = {
        "success": True,
        "output_path": output_path,
        "rows_in": rows_in,
        "rows_analyzed": rows_analyzed,
        "is_sample": is_sample,
        "cjk_columns": cjk_columns,
        "sentinel_findings": sentinel_findings,
        "distribution_findings": distribution_findings,
        "uniformity_findings": uniformity_findings,
        "summary": summary,
    }

    if is_sample:
        result["sampling_info"] = {
            "sample_size": rows_analyzed,
            "population_size": rows_in,
            "sample_fraction": round(rows_analyzed / rows_in, 4),
            "stratify_by": stratify_by,
        }

    if group_findings is not None:
        result["group_findings"] = group_findings

    # ── Write detailed report ────────────────────────────────
    try:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            json.dump(result, fh, indent=2, default=str)
    except Exception as exc:
        return {
            "success": False,
            "error": f"Failed to write output file: {exc}",
            "suggestion": "Check disk space and write permissions",
            "rows_in": rows_in,
        }

    # Return the full result (caller prints it to stdout)
    return result


# ──────────────────────────────────────────────────────────────
# CLI Entry Point
# ──────────────────────────────────────────────────────────────

def parse_args():
    parser = argparse.ArgumentParser(
        description=(
            "Detect sentinel/placeholder values and distribution-based content "
            "anomalies in a dataset."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic scan of all string columns
  content_validator.py data.csv report.json

  # Scan specific columns, add custom sentinels
  content_validator.py data.csv report.json --columns examples_yue,examples_eng \\
      --sentinel-values X,TODO,REVIEW

  # Enable distribution-based anomaly detection
  content_validator.py data.jsonl report.json --distribution-check

  # Sample 5000 rows, stratified by dialect column
  content_validator.py data.csv report.json --sample 5000 --stratify-by dialect

  # Group-level breakdown
  content_validator.py data.csv report.json --group-by source
        """,
    )
    parser.add_argument("input_path", help="Path to input CSV or JSONL file")
    parser.add_argument("output_path", help="Path to output JSON report file")
    parser.add_argument(
        "--columns",
        help="Comma-separated list of columns to analyse. Defaults to all string columns.",
        default=None,
    )
    parser.add_argument(
        "--sentinel-values",
        help=(
            "Comma-separated list of custom sentinel values. "
            "When provided, replaces the built-in sentinel list."
        ),
        default=None,
    )
    parser.add_argument(
        "--min-content-length",
        type=int,
        default=3,
        help=(
            "Minimum acceptable content length. Values strictly shorter than this "
            "are flagged as potential sentinels. (default: 3)"
        ),
    )
    parser.add_argument(
        "--sample",
        type=int,
        default=None,
        metavar="N",
        help="Analyse a random sample of N rows instead of the full dataset.",
    )
    parser.add_argument(
        "--stratify-by",
        default=None,
        metavar="COL",
        help="Column to use for proportional stratified sampling (requires --sample).",
    )
    parser.add_argument(
        "--group-by",
        default=None,
        metavar="COL",
        help="Column to use for per-group breakdown analysis.",
    )
    parser.add_argument(
        "--distribution-check",
        action="store_true",
        default=False,
        help=(
            "Enable distribution-based anomaly detection (Layer 2). "
            "Flags values whose length is >3 standard deviations below the column mean."
        ),
    )
    parser.add_argument(
        "--cjk-aware",
        action="store_true",
        default=True,
        dest="cjk_aware",
        help=(
            "Enable CJK-aware content validation: use min_content_length=1 for "
            "CJK-dominant columns instead of the configured default. (default: enabled)"
        ),
    )
    parser.add_argument(
        "--no-cjk-aware",
        action="store_false",
        dest="cjk_aware",
        help="Disable CJK-aware content validation.",
    )
    parser.add_argument(
        "--depth",
        choices=["surface", "pattern", "deep"],
        default="surface",
        help="Validation depth: surface (default), pattern, or deep.",
    )
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Input file format (default: auto)",
    )
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    _start_time = time.time()

    # Parse comma-separated lists
    columns = [c.strip() for c in args.columns.split(",")] if args.columns else None
    sentinel_values = (
        [s.strip() for s in args.sentinel_values.split(",")]
        if args.sentinel_values
        else None
    )

    result = main(
        input_path=args.input_path,
        output_path=args.output_path,
        columns=columns,
        sentinel_values=sentinel_values,
        min_content_length=args.min_content_length,
        sample_n=args.sample,
        stratify_by=args.stratify_by,
        group_by=args.group_by,
        distribution_check=args.distribution_check,
        input_format=args.input_format,
        cjk_aware=args.cjk_aware,
        depth=args.depth,
    )

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            meta = {
                "script": os.path.relpath(__file__),
                "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
                "rows_in": result.get("rows_in", 0),
                "rows_out": result.get("rows_out", 0),
                "duration_seconds": round(time.time() - _start_time, 3),
            }
            ckpt_path = maybe_checkpoint(output_path, "content_validation", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))
    sys.exit(0 if result.get("success") else 1)
