#!/usr/bin/env python3
"""
Meta-Profiling Script: Detect All Issues
Run multiple profiling analyses in one call and merge results into a single report.

Sequentially executes:
  1. quality_score.py       - Composite data quality score (0-100)
  2. distribution_analysis.py - Per-column distribution characteristics
  3. outlier_detection.py   - Statistical outlier detection (IQR)
  4. correlation_matrix.py  - Pairwise correlations with significance testing

Optionally:
  5. content_validator.py   - Sentinel/placeholder value detection (from data_validation)

Sub-script failures are captured gracefully; partial results are always returned.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import logging
import os
import time
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


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

try:
    from sentinel_patterns import EXACT_SENTINELS
except ImportError:
    EXACT_SENTINELS = {"N/A", "NA", "n/a", "na", "N/a", "None", "none", "NONE", "null", "NULL", "Null", "NaN", "nan", "NAN", "-", "--", "---", ".", "..", "...", "?", "??", "???", "TBD", "tbd", "TODO", "todo", "MISSING", "missing", "Missing", "UNKNOWN", "unknown", "Unknown", "X", "x", "placeholder", "Placeholder", "PLACEHOLDER"}

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
# Script paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = Path(__file__).resolve().parent

PROFILING_SCRIPTS = {
    "quality": SCRIPT_DIR / "quality_score.py",
    "distributions": SCRIPT_DIR / "distribution_analysis.py",
    "outliers": SCRIPT_DIR / "outlier_detection.py",
    "correlations": SCRIPT_DIR / "correlation_matrix.py",
    "categories": SCRIPT_DIR / "detect_categories.py",
    "answer_classification": SCRIPT_DIR / "classify_answers.py",
}

CONTENT_VALIDATOR_PATH = (
    SCRIPT_DIR / ".." / ".." / "magic-data-validation" / "scripts" / "content_validator.py"
).resolve()


# ---------------------------------------------------------------------------
# Sub-script runner
# ---------------------------------------------------------------------------

def run_subscript(
    script_path: Path,
    input_path: str,
    output_path: str,
    extra_args: list | None = None,
    use_named_args: bool = False,
) -> dict:
    """
    Execute a sub-script via subprocess.run and return parsed JSON output.

    On failure, returns a dict with ``success=False`` and the error details
    so that the caller can include partial results.
    """
    if not script_path.exists():
        return {
            "success": False,
            "error": f"Script not found: {script_path}",
        }

    if use_named_args:
        cmd = [sys.executable, str(script_path), "--input", input_path, "--output", output_path]
    else:
        cmd = [sys.executable, str(script_path), input_path, output_path]
    if extra_args:
        cmd.extend(extra_args)

    log.info("Running: %s", " ".join(cmd))

    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout per sub-script
        )

        # Try to parse stdout as JSON regardless of return code, because
        # some scripts print a JSON error payload even on non-zero exit.
        stdout = proc.stdout.strip()
        if stdout:
            try:
                return json.loads(stdout)
            except json.JSONDecodeError:
                pass

        # If stdout was not valid JSON, fall back to reading the output file
        # (some scripts write there even if stdout is empty).
        output_file = Path(output_path)
        if output_file.exists():
            try:
                with open(output_file, "r", encoding="utf-8") as fh:
                    return json.load(fh)
            except (json.JSONDecodeError, OSError):
                pass

        # Nothing parseable -- report the failure.
        stderr_snippet = (proc.stderr or "").strip()[:500]
        return {
            "success": False,
            "error": f"Script exited with code {proc.returncode}",
            "stderr": stderr_snippet,
            "stdout": stdout[:500] if stdout else "",
        }

    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "error": f"Script timed out after 300 seconds: {script_path.name}",
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Failed to execute {script_path.name}: {exc}",
        }


# ---------------------------------------------------------------------------
# Sentinel detection
# ---------------------------------------------------------------------------

DEFAULT_SENTINEL_PATTERNS = list(EXACT_SENTINELS)


def detect_sentinels(input_path: str, sentinel_patterns: Optional[list] = None,
                     input_format: str = "auto") -> dict:
    """
    Check each column for cells whose stripped value exactly matches a sentinel pattern.

    Args:
        input_path: Path to input file.
        sentinel_patterns: List of sentinel string patterns to check for (whole-cell match only).
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel).

    Returns:
        dict with keys:
            success (bool)
            sentinel_counts (dict: column -> count of sentinel cells)
            total_sentinel_cells (int)
            sentinel_ratio (float: fraction of all cells that are sentinels)
            rows_in (int)
    """
    patterns = sentinel_patterns if sentinel_patterns is not None else DEFAULT_SENTINEL_PATTERNS
    pattern_set = set(patterns)
    try:
        df = load_dataframe(input_path, format=input_format, dtype=str, keep_default_na=False)
        rows_in = len(df)
        total_cells = rows_in * len(df.columns)
        sentinel_counts: dict = {}
        total_sentinel_cells = 0
        for col in df.columns:
            stripped = df[col].fillna("").str.strip()
            count = int(stripped.isin(pattern_set).sum())
            if count > 0:
                sentinel_counts[col] = count
                total_sentinel_cells += count
        sentinel_ratio = total_sentinel_cells / total_cells if total_cells > 0 else 0.0
        return {
            "success": True,
            "sentinel_counts": sentinel_counts,
            "total_sentinel_cells": total_sentinel_cells,
            "sentinel_ratio": round(sentinel_ratio, 6),
            "rows_in": rows_in,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": f"Sentinel detection failed: {exc}",
            "sentinel_counts": {},
            "total_sentinel_cells": 0,
            "sentinel_ratio": 0.0,
        }


# ---------------------------------------------------------------------------
# Summary builder
# ---------------------------------------------------------------------------

def build_summary(results: dict) -> dict:
    """
    Build a top-level summary from the individual sub-script results.

    Keys:
        quality_score    - Overall quality score (0-100), after sentinel penalty, or None on failure
        total_outliers   - Total outlier row count across all columns
        high_correlations - Count of correlation pairs with |r| > 0.7
        total_sentinel_cells - Total sentinel cell count across all columns
        sentinel_ratio   - Fraction of all cells that contain sentinel values
    """
    # -- quality_score --
    quality_score = None
    quality_result = results.get("quality")
    if quality_result and quality_result.get("success"):
        quality_score = quality_result.get("overall_score")

    # -- sentinel counts and penalty --
    total_sentinel_cells = 0
    sentinel_ratio = 0.0
    sentinel_result = results.get("sentinels")
    if sentinel_result and sentinel_result.get("success"):
        total_sentinel_cells = sentinel_result.get("total_sentinel_cells", 0)
        sentinel_ratio = sentinel_result.get("sentinel_ratio", 0.0)
        # Deduct from quality score: up to 20 points based on sentinel ratio
        # (sentinel_ratio=0 → 0 penalty, sentinel_ratio=1.0 → 20 points penalty)
        if quality_score is not None:
            sentinel_penalty = round(min(20.0, sentinel_ratio * 100 * 0.2), 2)
            quality_score = max(0.0, round(quality_score - sentinel_penalty, 2))

    # -- total_outliers --
    total_outliers = 0
    outlier_result = results.get("outliers")
    if outlier_result and outlier_result.get("success"):
        total_outliers = outlier_result.get("total_outlier_rows", 0)

    # -- high_correlations (|r| > 0.7) --
    high_correlations = 0
    corr_result = results.get("correlations")
    if corr_result and corr_result.get("success"):
        pairs = corr_result.get("significant_pairs", [])
        high_correlations = sum(
            1 for p in pairs if abs(p.get("r", 0)) > 0.7
        )

    return {
        "quality_score": quality_score,
        "total_outliers": total_outliers,
        "high_correlations": high_correlations,
        "total_sentinel_cells": total_sentinel_cells,
        "sentinel_ratio": sentinel_ratio,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(
    input_path: str,
    output_path: str,
    include_content_validation: bool = False,
    sentinel_patterns: Optional[list] = None,
    input_format: str = "auto",
) -> dict:
    """
    Run all profiling sub-scripts and merge their outputs.

    Args:
        input_path: Path to input file.
        output_path: Path to merged output JSON file.
        include_content_validation: If True, also run content_validator.py.
        sentinel_patterns: List of string sentinel patterns to check for
            (whole-cell match). Defaults to DEFAULT_SENTINEL_PATTERNS.
        input_format: File format for input (auto, csv, tsv, jsonl, json, parquet, excel).

    Returns:
        dict: Merged results with keys: success, output_path, rows_in,
              summary, quality, distributions, outliers, correlations,
              sentinels, and optionally content_validation.
    """
    results: dict = {}
    errors: list = []

    # ── 0. Sentinel Detection (inline — no subprocess needed) ────
    log.info("Step 0: Running inline sentinel detection")
    results["sentinels"] = detect_sentinels(input_path, sentinel_patterns, input_format)
    if not results["sentinels"].get("success"):
        errors.append({"script": "sentinel_detection", "error": results["sentinels"].get("error", "unknown")})

    # Use a temporary directory for intermediate outputs
    with tempfile.TemporaryDirectory(prefix="detect_all_issues_") as tmp_dir:
        tmp = Path(tmp_dir)

        # Build format args to pass to all sub-scripts
        format_args = ["--input-format", input_format] if input_format != "auto" else []

        # ── 1. Quality Score ─────────────────────────────────────
        log.info("Step 1/4: Running quality_score.py")
        quality_out = str(tmp / "quality.json")
        results["quality"] = run_subscript(
            PROFILING_SCRIPTS["quality"], input_path, quality_out,
            extra_args=format_args or None,
        )
        if not results["quality"].get("success"):
            errors.append({"script": "quality_score.py", "error": results["quality"].get("error", "unknown")})

        # ── 2. Distribution Analysis ─────────────────────────────
        log.info("Step 2/4: Running distribution_analysis.py")
        dist_out = str(tmp / "distributions.json")
        results["distributions"] = run_subscript(
            PROFILING_SCRIPTS["distributions"], input_path, dist_out,
            extra_args=format_args or None,
        )
        if not results["distributions"].get("success"):
            errors.append({"script": "distribution_analysis.py", "error": results["distributions"].get("error", "unknown")})

        # ── 3. Outlier Detection ─────────────────────────────────
        log.info("Step 3/4: Running outlier_detection.py")
        outlier_out = str(tmp / "outliers.json")
        results["outliers"] = run_subscript(
            PROFILING_SCRIPTS["outliers"], input_path, outlier_out,
            extra_args=format_args or None,
        )
        if not results["outliers"].get("success"):
            errors.append({"script": "outlier_detection.py", "error": results["outliers"].get("error", "unknown")})

        # ── 4. Correlation Matrix ────────────────────────────────
        log.info("Step 4/4: Running correlation_matrix.py")
        corr_out = str(tmp / "correlations.json")
        results["correlations"] = run_subscript(
            PROFILING_SCRIPTS["correlations"], input_path, corr_out,
            extra_args=format_args or None,
        )
        if not results["correlations"].get("success"):
            errors.append({"script": "correlation_matrix.py", "error": results["correlations"].get("error", "unknown")})

        # ── 5. Category Detection (on longest text column) ────────
        log.info("Step 5/6: Running detect_categories.py")
        cat_out = str(tmp / "categories.json")
        results["categories"] = run_subscript(
            PROFILING_SCRIPTS["categories"], input_path, cat_out,
            extra_args=format_args or None,
            use_named_args=True,
        )
        if not results["categories"].get("success"):
            errors.append({"script": "detect_categories.py", "error": results["categories"].get("error", "unknown")})

        # ── 6. Answer Classification (on short-text columns) ─────
        log.info("Step 6/6: Running classify_answers.py")
        ans_out = str(tmp / "answer_classification.json")
        # Try to find a short-text column suitable for answer classification.
        # Prefer columns named "answer"/"response"/"output"; skip ID-like columns.
        try:
            _df = load_dataframe(input_path, format=input_format)
            _text_cols = _df.select_dtypes(include=["object"]).columns.tolist()
            _id_patterns = {"id", "uuid", "key", "index", "pk"}
            _text_cols = [c for c in _text_cols if c.lower() not in _id_patterns]
            _short_cols = [
                c for c in _text_cols
                if _df[c].dropna().astype(str).str.len().mean() < 50
            ]
            # Prefer answer-like column names
            _answer_names = {"answer", "response", "output", "result", "target", "label"}
            _ans_col = None
            for c in _short_cols:
                if c.lower() in _answer_names:
                    _ans_col = c
                    break
            if _ans_col is None:
                _ans_col = _short_cols[0] if _short_cols else (_text_cols[0] if _text_cols else None)
        except Exception:
            _ans_col = None

        if _ans_col:
            results["answer_classification"] = run_subscript(
                PROFILING_SCRIPTS["answer_classification"], input_path, ans_out,
                extra_args=["--column", _ans_col] + (format_args or []),
                use_named_args=True,
            )
            if not results["answer_classification"].get("success"):
                errors.append({"script": "classify_answers.py", "error": results["answer_classification"].get("error", "unknown")})
        else:
            results["answer_classification"] = {
                "success": False,
                "error": "No suitable text column found for answer classification",
                "skipped": True,
            }

        # ── 7. Content Validation (optional) ─────────────────────
        if include_content_validation:
            if CONTENT_VALIDATOR_PATH.exists():
                log.info("Step 5 (optional): Running content_validator.py")
                cv_out = str(tmp / "content_validation.json")
                results["content_validation"] = run_subscript(
                    CONTENT_VALIDATOR_PATH, input_path, cv_out,
                )
                if not results["content_validation"].get("success"):
                    errors.append({
                        "script": "content_validator.py",
                        "error": results["content_validation"].get("error", "unknown"),
                    })
            else:
                log.warning(
                    "content_validator.py not found at %s -- skipping content validation",
                    CONTENT_VALIDATOR_PATH,
                )
                results["content_validation"] = {
                    "success": False,
                    "error": f"content_validator.py not available at {CONTENT_VALIDATOR_PATH}",
                    "skipped": True,
                }

    # ── Determine rows_in from first successful sub-script ────
    rows_in = None
    for key in ("sentinels", "quality", "distributions", "outliers", "correlations", "content_validation"):
        sub = results.get(key)
        if sub and sub.get("success"):
            rows_in = sub.get("rows_in")
            if rows_in is not None:
                break

    # ── Build summary ─────────────────────────────────────────
    summary = build_summary(results)

    # ── Assemble merged output ────────────────────────────────
    any_success = any(
        results.get(k, {}).get("success", False)
        for k in ("quality", "distributions", "outliers", "correlations")
    )

    output_data: dict = {
        "success": any_success,
        "output_path": output_path,
        "rows_in": rows_in,
        "summary": summary,
        "sentinels": results.get("sentinels", {}),
        "quality": results.get("quality", {}),
        "distributions": results.get("distributions", {}),
        "outliers": results.get("outliers", {}),
        "correlations": results.get("correlations", {}),
        "categories": results.get("categories", {}),
        "answer_classification": results.get("answer_classification", {}),
    }

    if "content_validation" in results:
        output_data["content_validation"] = results["content_validation"]

    if errors:
        output_data["errors"] = errors

    # ── Write merged output ───────────────────────────────────
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(output_data, fh, indent=2, default=str)
    except Exception as exc:
        output_data["success"] = False
        output_data["error"] = f"Failed to write output file: {exc}"

    return output_data


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Run all data profiling analyses (quality, distributions, outliers, "
            "correlations) and merge results into a single report."
        ),
    )
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output JSON file")
    parser.add_argument(
        "--include-content-validation",
        action="store_true",
        default=False,
        help=(
            "Also run content_validator.py from data_validation skill. "
            "If the script is not available, a warning is logged and it is skipped."
        ),
    )
    parser.add_argument(
        "--sentinel-patterns",
        nargs="+",
        default=None,
        metavar="PATTERN",
        help=(
            "Whitespace-separated list of sentinel string patterns to check for "
            "(whole-cell match only). Defaults to: X TBD N/A ? TBC UNKNOWN NA n/a None null -"
        ),
    )
    parser.add_argument(
        "--input-format",
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Input file format (default: auto-detect from extension)",
    )
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(
        args.input_path,
        args.output_path,
        include_content_validation=args.include_content_validation,
        sentinel_patterns=args.sentinel_patterns,
        input_format=args.input_format,
    )

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            def maybe_checkpoint(path, tag, save=True, checkpoint_format=None, metadata=None):
                """Stub: save checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
                return None
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(output_path, "profile", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result.get("success") else 1)
