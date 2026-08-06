#!/usr/bin/env python3
"""
Multi-Dataset Reference Enrichment CLI
=======================================
Enrich an input dataset by joining one or more reference datasets using
exact, fuzzy, or semantic match strategies.

Match strategies:
  exact    — pandas merge (fast, zero tolerance)
  fuzzy    — rapidfuzz process.extractOne() per row (string similarity)
  semantic — TF-IDF cosine similarity from synthesis_utils

Per-reference-dataset match rate reporting and high null rate warnings
(>50% null in any enriched column after join) are included.

Supports:
  - Multiple reference datasets via --reference-paths or --join-config JSON
  - Per-dataset join key configuration
  - --sample-size for preview runs
  - --max-cost placeholder (no LLM calls; reserved for future agentic enrichment)
  - --workspace for checkpoint/log output

NOTE: Agentic enrichment (LLM-based fallback for unmatched rows) is not yet
implemented. It is noted here as a planned future capability.

Usage:
    python enrich_from_reference.py INPUT_PATH OUTPUT_PATH \\
      --reference-paths ref1.csv,ref2.csv \\
      [--join-config config.json] \\
      [--source-key col_name] [--reference-key col_name] \\
      [--match-type exact|fuzzy|semantic] [--fuzzy-threshold 80] \\
      [--enrich-columns col1,col2] \\
      [--sample-size N] [--max-cost FLOAT] \\
      [--workspace DIR]

Join config JSON format:
    {
      "joins": [
        {
          "reference_path": "ref1.csv",
          "source_key": "word",
          "reference_key": "term",
          "match_type": "exact",
          "enrich_columns": ["frequency", "category"]
        },
        {
          "reference_path": "ref2.csv",
          "source_key": "word",
          "reference_key": "word",
          "match_type": "fuzzy",
          "fuzzy_threshold": 85,
          "enrich_columns": ["etymology"]
        }
      ]
    }
"""
# REFERENCE IMPLEMENTATION — Read for patterns, write custom code adapted to your task.

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Optional

_SCRIPT_DIR = Path(__file__).resolve().parent
_SKILLS_DIR = _SCRIPT_DIR.parent.parent


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
def save_checkpoint(df, workspace, step=1, operation="checkpoint"):
    """Stub: save a checkpoint CSV. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    import os
    p = Path(workspace) / f"ckpt_step{step}_{operation}.csv"
    os.makedirs(workspace, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)

class _io_utils:
    @staticmethod
    def load_dataframe(path, format="auto", **kwargs):
        import pandas as pd
        ext = str(path).rsplit(".", 1)[-1].lower()
        fmt = format if format != "auto" else ext
        if fmt == "parquet":
            return pd.read_parquet(path)
        if fmt in ("jsonl", "ndjson"):
            return pd.read_json(path, lines=True)
        if fmt == "json":
            return pd.read_json(path)
        if fmt == "tsv":
            return pd.read_csv(path, sep="\t")
        return pd.read_csv(path)
    @staticmethod
    def save_dataframe(df, path, format="auto", input_format=None):
        ext = str(path).rsplit(".", 1)[-1].lower()
        fmt = format if format != "auto" else ext
        if fmt == "parquet":
            df.to_parquet(path, index=False)
        elif fmt in ("jsonl", "ndjson"):
            df.to_json(path, orient="records", lines=True)
        elif fmt == "json":
            df.to_json(path, orient="records", indent=2)
        elif fmt == "tsv":
            df.to_csv(path, sep="\t", index=False)
        else:
            df.to_csv(path, index=False)
    @staticmethod
    def detect_format_from_path(path):
        return str(path).rsplit(".", 1)[-1].lower()

def load_dataframe(path, format="auto", **kwargs):
    """Stub: load a DataFrame from path. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    ext = str(path).rsplit(".", 1)[-1].lower()
    fmt = format if format != "auto" else ext
    if fmt == "parquet":
        return pd.read_parquet(path)
    if fmt in ("jsonl", "ndjson"):
        return pd.read_json(path, lines=True)
    if fmt == "json":
        return pd.read_json(path)
    if fmt == "tsv":
        return pd.read_csv(path, sep="\t")
    return pd.read_csv(path)

try:
    from synthesis_utils import tfidf_similarity
except ImportError:
    def tfidf_similarity(a, b):
        """Stub: TF-IDF cosine similarity between two strings."""
        return 0.0

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# ── constants ─────────────────────────────────────────────────
HIGH_NULL_RATE_THRESHOLD = 0.50   # warn if >50% of enriched column is null after join
DEFAULT_FUZZY_THRESHOLD = 80      # rapidfuzz score 0-100


# ──────────────────────────────────────────────────────────────
# Join Config Resolution
# ──────────────────────────────────────────────────────────────

def resolve_join_specs(
    reference_paths: Optional[str],
    join_config_path: Optional[str],
    source_key: Optional[str],
    reference_key: Optional[str],
    match_type: str,
    fuzzy_threshold: int,
    enrich_columns: Optional[str],
) -> list[dict]:
    """
    Build the list of join specifications to execute.

    Join specs are sourced from either:
    1. A --join-config JSON file (takes precedence when present)
    2. CLI flags (--reference-paths, --source-key, --reference-key, etc.)

    Args:
        reference_paths: Comma-separated reference file paths (CLI arg)
        join_config_path: Path to a join config JSON file
        source_key: Source dataset key column (CLI arg)
        reference_key: Reference dataset key column (CLI arg)
        match_type: Match strategy — "exact", "fuzzy", or "semantic" (CLI arg)
        fuzzy_threshold: Fuzzy match score threshold 0-100 (CLI arg)
        enrich_columns: Comma-separated column names to enrich (CLI arg)

    Returns:
        List of join spec dicts, each with keys:
            reference_path, source_key, reference_key, match_type,
            fuzzy_threshold, enrich_columns (list[str] or None)

    Raises:
        ValueError: If no join spec can be resolved
    """
    # ── 1. Config-file path ─────────────────────────────────
    if join_config_path:
        p = Path(join_config_path)
        if not p.exists():
            raise FileNotFoundError(f"Join config file not found: {join_config_path}")
        with open(p, "r", encoding="utf-8") as f:
            config = json.load(f)

        joins = config.get("joins")
        if not isinstance(joins, list) or len(joins) == 0:
            raise ValueError(
                f"Join config '{join_config_path}' must contain a non-empty 'joins' array"
            )

        specs = []
        for i, entry in enumerate(joins):
            if "reference_path" not in entry:
                raise ValueError(f"Join config entry {i} is missing 'reference_path'")
            specs.append({
                "reference_path": entry["reference_path"],
                "source_key": entry.get("source_key", source_key),
                "reference_key": entry.get("reference_key", reference_key),
                "match_type": entry.get("match_type", match_type),
                "fuzzy_threshold": int(entry.get("fuzzy_threshold", fuzzy_threshold)),
                "enrich_columns": entry.get("enrich_columns") or None,
            })
        return specs

    # ── 2. CLI --reference-paths path ───────────────────────
    if reference_paths:
        paths = [p.strip() for p in reference_paths.split(",") if p.strip()]
        if not paths:
            raise ValueError("--reference-paths produced no valid paths after splitting")

        enrich_cols = (
            [c.strip() for c in enrich_columns.split(",") if c.strip()]
            if enrich_columns
            else None
        )

        specs = []
        for rp in paths:
            specs.append({
                "reference_path": rp,
                "source_key": source_key,
                "reference_key": reference_key,
                "match_type": match_type,
                "fuzzy_threshold": fuzzy_threshold,
                "enrich_columns": enrich_cols,
            })
        return specs

    raise ValueError(
        "No join specification provided. "
        "Supply --reference-paths or --join-config."
    )


# ──────────────────────────────────────────────────────────────
# Reference Dataset Loading
# ──────────────────────────────────────────────────────────────

def load_reference(path: str) -> pd.DataFrame:
    """
    Load a reference dataset from CSV, Parquet, or JSONL.

    Args:
        path: File path to the reference dataset

    Returns:
        Loaded DataFrame

    Raises:
        FileNotFoundError: If the file does not exist
        ValueError: If the file cannot be parsed
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Reference file not found: {path}")
    try:
        return load_dataframe(str(p))
    except Exception as e:
        raise ValueError(f"Could not load reference file '{path}': {e}") from e


# ──────────────────────────────────────────────────────────────
# Match Strategies
# ──────────────────────────────────────────────────────────────

def match_exact(
    source_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    source_key: str,
    reference_key: str,
    enrich_columns: Optional[list[str]],
) -> tuple[pd.DataFrame, dict]:
    """
    Enrich source_df by exact-key merge with ref_df.

    Args:
        source_df: Input DataFrame to enrich
        ref_df: Reference DataFrame
        source_key: Join key column name in source_df
        reference_key: Join key column name in ref_df
        enrich_columns: Columns from ref_df to bring in (None = all non-key columns)

    Returns:
        Tuple of (enriched_df, match_stats_dict)
    """
    if source_key not in source_df.columns:
        raise ValueError(f"Source key '{source_key}' not found in input dataset")
    if reference_key not in ref_df.columns:
        raise ValueError(f"Reference key '{reference_key}' not found in reference dataset")

    # Select columns to merge
    ref_cols = _select_ref_columns(ref_df, reference_key, enrich_columns)
    ref_subset = ref_df[ref_cols].drop_duplicates(subset=[reference_key])

    total_rows = len(source_df)

    # Rename reference key to match source key if they differ
    if reference_key != source_key:
        ref_subset = ref_subset.rename(columns={reference_key: source_key})

    result_df = source_df.merge(ref_subset, on=source_key, how="left", suffixes=("", "_ref"))

    matched_rows = int(result_df[source_key].notna().sum())
    # Count rows where at least one enriched column got a non-null value
    enriched_cols_in_result = [c for c in ref_cols if c != reference_key]
    if enriched_cols_in_result:
        matched_mask = result_df[enriched_cols_in_result[0]].notna()
        matched_rows = int(matched_mask.sum())

    match_rate = matched_rows / total_rows if total_rows > 0 else 0.0

    stats = {
        "strategy": "exact",
        "total_rows": total_rows,
        "matched_rows": matched_rows,
        "match_rate": round(match_rate, 4),
    }

    return result_df, stats


def match_fuzzy(
    source_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    source_key: str,
    reference_key: str,
    enrich_columns: Optional[list[str]],
    threshold: int = DEFAULT_FUZZY_THRESHOLD,
) -> tuple[pd.DataFrame, dict]:
    """
    Enrich source_df using fuzzy string matching via rapidfuzz.

    For each row in source_df, find the best-matching row in ref_df
    using rapidfuzz process.extractOne() on the key columns. If the
    best match score is >= threshold, enrich that row.

    Args:
        source_df: Input DataFrame to enrich
        ref_df: Reference DataFrame
        source_key: Join key column name in source_df
        reference_key: Join key column name in ref_df
        enrich_columns: Columns from ref_df to bring in (None = all non-key columns)
        threshold: Minimum fuzzy match score (0-100) to accept a match

    Returns:
        Tuple of (enriched_df, match_stats_dict)

    Raises:
        ImportError: If rapidfuzz is not installed
    """
    try:
        from rapidfuzz import process as rf_process, fuzz as rf_fuzz
    except ImportError as e:
        raise ImportError(
            "rapidfuzz is required for fuzzy matching. "
            "Install it with: pip install rapidfuzz"
        ) from e

    if source_key not in source_df.columns:
        raise ValueError(f"Source key '{source_key}' not found in input dataset")
    if reference_key not in ref_df.columns:
        raise ValueError(f"Reference key '{reference_key}' not found in reference dataset")

    ref_cols = _select_ref_columns(ref_df, reference_key, enrich_columns)
    ref_subset = ref_df[ref_cols].drop_duplicates(subset=[reference_key]).reset_index(drop=True)

    # Build lookup list from reference key column
    ref_choices = ref_subset[reference_key].astype(str).tolist()

    result_df = source_df.copy()

    # Initialize enriched columns in result with NA
    enriched_col_names = [c for c in ref_cols if c != reference_key]
    for col in enriched_col_names:
        if col not in result_df.columns:
            result_df[col] = pd.NA

    total_rows = len(result_df)
    matched_rows = 0

    for idx in result_df.index:
        source_val = result_df.at[idx, source_key]
        if pd.isna(source_val):
            continue

        query = str(source_val)
        match = rf_process.extractOne(
            query,
            ref_choices,
            scorer=rf_fuzz.WRatio,
            score_cutoff=threshold,
        )

        if match is not None:
            matched_string, score, ref_idx = match
            ref_row = ref_subset.iloc[ref_idx]
            for col in enriched_col_names:
                result_df.at[idx, col] = ref_row[col]
            matched_rows += 1

    match_rate = matched_rows / total_rows if total_rows > 0 else 0.0

    stats = {
        "strategy": "fuzzy",
        "threshold": threshold,
        "total_rows": total_rows,
        "matched_rows": matched_rows,
        "match_rate": round(match_rate, 4),
    }

    return result_df, stats


def match_semantic(
    source_df: pd.DataFrame,
    ref_df: pd.DataFrame,
    source_key: str,
    reference_key: str,
    enrich_columns: Optional[list[str]],
    threshold: float = 0.1,
) -> tuple[pd.DataFrame, dict]:
    """
    Enrich source_df using TF-IDF cosine similarity from synthesis_utils.

    For each row in source_df, compute TF-IDF similarity against all
    reference key values and pick the best match above the threshold.

    Args:
        source_df: Input DataFrame to enrich
        ref_df: Reference DataFrame
        source_key: Join key column name in source_df
        reference_key: Join key column name in ref_df
        enrich_columns: Columns from ref_df to bring in (None = all non-key columns)
        threshold: Minimum cosine similarity (0-1) to accept a match

    Returns:
        Tuple of (enriched_df, match_stats_dict)
    """
    if source_key not in source_df.columns:
        raise ValueError(f"Source key '{source_key}' not found in input dataset")
    if reference_key not in ref_df.columns:
        raise ValueError(f"Reference key '{reference_key}' not found in reference dataset")

    ref_cols = _select_ref_columns(ref_df, reference_key, enrich_columns)
    ref_subset = ref_df[ref_cols].drop_duplicates(subset=[reference_key]).reset_index(drop=True)

    ref_keys = ref_subset[reference_key].astype(str).tolist()

    result_df = source_df.copy()

    enriched_col_names = [c for c in ref_cols if c != reference_key]
    for col in enriched_col_names:
        if col not in result_df.columns:
            result_df[col] = pd.NA

    total_rows = len(result_df)
    matched_rows = 0

    for idx in result_df.index:
        source_val = result_df.at[idx, source_key]
        if pd.isna(source_val):
            continue

        query = str(source_val)

        best_score = -1.0
        best_ref_idx = -1

        for ref_i, ref_val in enumerate(ref_keys):
            score = tfidf_similarity(query, ref_val)
            if score > best_score:
                best_score = score
                best_ref_idx = ref_i

        if best_ref_idx >= 0 and best_score >= threshold:
            ref_row = ref_subset.iloc[best_ref_idx]
            for col in enriched_col_names:
                result_df.at[idx, col] = ref_row[col]
            matched_rows += 1

    match_rate = matched_rows / total_rows if total_rows > 0 else 0.0

    stats = {
        "strategy": "semantic",
        "threshold": threshold,
        "total_rows": total_rows,
        "matched_rows": matched_rows,
        "match_rate": round(match_rate, 4),
    }

    return result_df, stats


# ──────────────────────────────────────────────────────────────
# Column Selection Helper
# ──────────────────────────────────────────────────────────────

def _select_ref_columns(
    ref_df: pd.DataFrame,
    reference_key: str,
    enrich_columns: Optional[list[str]],
) -> list[str]:
    """
    Return the columns to include from the reference dataset.

    Always includes the reference_key. If enrich_columns is specified,
    only those columns are added (missing ones are warned about).
    Otherwise all non-key columns are included.

    Args:
        ref_df: Reference DataFrame
        reference_key: Key column name in ref_df
        enrich_columns: Explicit list of columns to enrich, or None

    Returns:
        List of column names to pull from ref_df (key first)
    """
    available = set(ref_df.columns.tolist())

    if enrich_columns:
        missing = [c for c in enrich_columns if c not in available]
        if missing:
            logger.warning(
                "Enrich columns not found in reference dataset and will be skipped: %s",
                missing,
            )
        present = [c for c in enrich_columns if c in available and c != reference_key]
        return [reference_key] + present
    else:
        # All non-key columns
        return [reference_key] + [c for c in ref_df.columns if c != reference_key]


# ──────────────────────────────────────────────────────────────
# Match Rate and Null Rate Reporting
# ──────────────────────────────────────────────────────────────

def compute_null_rate_warnings(
    df: pd.DataFrame,
    enriched_columns: list[str],
    reference_path: str,
) -> list[str]:
    """
    Check for high null rates in enriched columns after a join.

    Warns if more than HIGH_NULL_RATE_THRESHOLD (50%) of values in any
    enriched column are null after the join.

    Args:
        df: DataFrame after enrichment
        enriched_columns: Columns that were added during the join
        reference_path: Reference file path (for warning messages)

    Returns:
        List of warning strings (empty if no high null rates)
    """
    warnings = []
    for col in enriched_columns:
        if col not in df.columns:
            continue
        total = len(df)
        if total == 0:
            continue
        null_count = int(df[col].isna().sum())
        null_rate = null_count / total
        if null_rate > HIGH_NULL_RATE_THRESHOLD:
            warnings.append(
                f"High null rate in enriched column '{col}' after join "
                f"with '{Path(reference_path).name}': "
                f"{null_rate:.1%} null ({null_count}/{total} rows). "
                f"Check that source_key and reference_key values overlap."
            )
    return warnings


# ──────────────────────────────────────────────────────────────
# Single Join Executor
# ──────────────────────────────────────────────────────────────

def execute_join(
    df: pd.DataFrame,
    spec: dict,
) -> tuple[pd.DataFrame, dict, list[str]]:
    """
    Execute a single join spec against the current DataFrame.

    Args:
        df: Current working DataFrame
        spec: Join spec dict (from resolve_join_specs)

    Returns:
        Tuple of:
            enriched_df: DataFrame after this join
            join_stats: Dict with match rate and other stats
            warnings: List of warning strings for this join
    """
    reference_path = spec["reference_path"]
    source_key = spec.get("source_key")
    reference_key = spec.get("reference_key")
    match_type = spec.get("match_type", "exact")
    fuzzy_threshold = int(spec.get("fuzzy_threshold", DEFAULT_FUZZY_THRESHOLD))
    enrich_columns_spec = spec.get("enrich_columns")

    # Validate required keys
    if not source_key:
        raise ValueError(
            f"No source_key specified for reference '{reference_path}'. "
            f"Provide --source-key or include 'source_key' in the join config."
        )
    if not reference_key:
        raise ValueError(
            f"No reference_key specified for reference '{reference_path}'. "
            f"Provide --reference-key or include 'reference_key' in the join config."
        )

    # Load reference dataset
    logger.info("Loading reference dataset: %s", reference_path)
    ref_df = load_reference(reference_path)
    logger.info(
        "Reference '%s': %d rows, columns: %s",
        Path(reference_path).name,
        len(ref_df),
        ref_df.columns.tolist(),
    )

    # Determine enriched columns for null-rate checking
    ref_cols = _select_ref_columns(ref_df, reference_key, enrich_columns_spec)
    enriched_col_names = [c for c in ref_cols if c != reference_key]

    # Execute match strategy
    logger.info(
        "Joining on source_key='%s' <-> reference_key='%s' (strategy: %s)",
        source_key, reference_key, match_type,
    )

    if match_type == "exact":
        enriched_df, join_stats = match_exact(
            source_df=df,
            ref_df=ref_df,
            source_key=source_key,
            reference_key=reference_key,
            enrich_columns=enrich_columns_spec,
        )
    elif match_type == "fuzzy":
        enriched_df, join_stats = match_fuzzy(
            source_df=df,
            ref_df=ref_df,
            source_key=source_key,
            reference_key=reference_key,
            enrich_columns=enrich_columns_spec,
            threshold=fuzzy_threshold,
        )
    elif match_type == "semantic":
        enriched_df, join_stats = match_semantic(
            source_df=df,
            ref_df=ref_df,
            source_key=source_key,
            reference_key=reference_key,
            enrich_columns=enrich_columns_spec,
        )
    else:
        raise ValueError(
            f"Unknown match_type '{match_type}' for reference '{reference_path}'. "
            f"Valid options: exact, fuzzy, semantic."
        )

    join_stats["reference_path"] = reference_path
    join_stats["source_key"] = source_key
    join_stats["reference_key"] = reference_key
    join_stats["enrich_columns"] = enriched_col_names

    logger.info(
        "Join '%s': %d/%d rows matched (%.1f%%)",
        Path(reference_path).name,
        join_stats["matched_rows"],
        join_stats["total_rows"],
        join_stats["match_rate"] * 100,
    )

    # Check null rates after join
    warnings = compute_null_rate_warnings(enriched_df, enriched_col_names, reference_path)
    for w in warnings:
        logger.warning(w)

    return enriched_df, join_stats, warnings


# ──────────────────────────────────────────────────────────────
# Output Saving
# ──────────────────────────────────────────────────────────────

def save_output(df: pd.DataFrame, output_path: str, output_format: str = "auto",
                input_format: str = None) -> str:
    """
    Save the result DataFrame using io_utils (supports CSV, TSV, Parquet, JSONL, JSON, Excel).

    Args:
        df: DataFrame to save
        output_path: Target file path
        output_format: Output format (auto, csv, tsv, jsonl, json, parquet, excel)
        input_format: Source data format for fallback resolution when output_format is "auto"

    Returns:
        Absolute path string to saved file
    """
    _io_utils.save_dataframe(df, output_path, format=output_format, input_format=input_format)
    return str(output_path)


# ──────────────────────────────────────────────────────────────
# CLI
# ──────────────────────────────────────────────────────────────

def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description=(
            "Enrich an input dataset by joining one or more reference datasets "
            "using exact, fuzzy, or semantic match strategies."
        )
    )

    # Positional
    parser.add_argument("input_path", help="Path to input data file (CSV, Parquet, JSONL)")
    parser.add_argument("output_path", help="Path to output data file (CSV, Parquet, JSONL)")

    # Reference dataset specification
    ref_group = parser.add_argument_group("Reference dataset configuration")
    ref_group.add_argument(
        "--reference-paths",
        type=str,
        default=None,
        help=(
            "Comma-separated paths to reference datasets (CSV, Parquet, JSONL). "
            "All datasets use the same --source-key, --reference-key, and --match-type. "
            "For per-dataset config, use --join-config instead."
        ),
    )
    ref_group.add_argument(
        "--join-config",
        type=str,
        default=None,
        dest="join_config",
        help=(
            "Path to a JSON join config file specifying multiple joins with "
            "per-dataset source_key, reference_key, match_type, and enrich_columns."
        ),
    )

    # Join parameters (CLI defaults, overridden per-entry by --join-config)
    join_group = parser.add_argument_group("Join parameters (apply to --reference-paths)")
    join_group.add_argument(
        "--source-key",
        type=str,
        default=None,
        dest="source_key",
        help="Column name in the input dataset to join on",
    )
    join_group.add_argument(
        "--reference-key",
        type=str,
        default=None,
        dest="reference_key",
        help="Column name in the reference dataset to join on",
    )
    join_group.add_argument(
        "--match-type",
        type=str,
        choices=["exact", "fuzzy", "semantic"],
        default="exact",
        dest="match_type",
        help="Match strategy: exact (pandas merge), fuzzy (rapidfuzz), or semantic (TF-IDF). Default: exact",
    )
    join_group.add_argument(
        "--fuzzy-threshold",
        type=int,
        default=DEFAULT_FUZZY_THRESHOLD,
        dest="fuzzy_threshold",
        help=f"Minimum rapidfuzz score (0-100) for a fuzzy match to be accepted. Default: {DEFAULT_FUZZY_THRESHOLD}",
    )
    join_group.add_argument(
        "--enrich-columns",
        type=str,
        default=None,
        dest="enrich_columns",
        help=(
            "Comma-separated column names from reference dataset to bring into the output. "
            "Default: all non-key columns."
        ),
    )

    # Sampling and cost controls
    control_group = parser.add_argument_group("Sampling and cost controls")
    control_group.add_argument(
        "--sample-size",
        type=int,
        default=None,
        dest="sample_size",
        help="Run on a random subset of N input rows for preview",
    )
    control_group.add_argument(
        "--max-cost",
        type=float,
        default=None,
        dest="max_cost",
        help=(
            "Maximum cost in USD (placeholder — no LLM calls are made in this script). "
            "Reserved for future agentic enrichment support."
        ),
    )

    # Workspace
    parser.add_argument(
        "--workspace",
        type=str,
        default=None,
        help="Directory for checkpoint and log files",
    )
    parser.add_argument(
        "--output-format",
        type=str,
        default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        dest="output_format",
        help="Output file format (default: auto)",
    )

    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None):
    """Main entry point."""
    args = parse_args(argv)

    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s: %(message)s",
        stream=sys.stderr,
    )

    # ── 1. Load input data ──────────────────────────────────
    try:
        df = load_dataframe(args.input_path)
    except FileNotFoundError:
        output_result(format_error(
            f"Input file not found: {args.input_path}",
            suggestion="Check the input file path",
        ))
        return
    except Exception as e:
        output_result(format_error(
            f"Failed to load input file: {e}",
            suggestion="Check file path and format (CSV, Parquet, JSONL supported)",
        ))
        return

    rows_in = len(df)
    logger.info("Loaded %d rows from %s", rows_in, args.input_path)

    if rows_in == 0:
        output_result(format_error(
            "Input file is empty",
            suggestion="Provide a non-empty input file",
            rows_in=0,
        ))
        return

    # ── 2. Apply sample-size if requested ───────────────────
    sampled = False
    if args.sample_size and args.sample_size < rows_in:
        import random
        random.seed(42)
        df = df.sample(n=args.sample_size, random_state=42).reset_index(drop=True)
        logger.info("Sampled %d rows for preview (from %d)", len(df), rows_in)
        sampled = True

    # ── 3. Resolve join specifications ─────────────────────
    try:
        join_specs = resolve_join_specs(
            reference_paths=args.reference_paths,
            join_config_path=args.join_config,
            source_key=args.source_key,
            reference_key=args.reference_key,
            match_type=args.match_type,
            fuzzy_threshold=args.fuzzy_threshold,
            enrich_columns=args.enrich_columns,
        )
    except (FileNotFoundError, ValueError) as e:
        output_result(format_error(
            str(e),
            suggestion=(
                "Provide --reference-paths with --source-key and --reference-key, "
                "or --join-config pointing to a valid JSON config file."
            ),
        ))
        return

    logger.info("Resolved %d join specification(s)", len(join_specs))

    # ── 4. Optionally set up workspace ──────────────────────
    workspace = args.workspace
    if workspace:
        Path(workspace).mkdir(parents=True, exist_ok=True)

    # ── 5. Max-cost note (no LLM calls in this script) ──────
    if args.max_cost is not None:
        logger.info(
            "--max-cost=%.4f specified. Note: this script performs no LLM calls. "
            "Cost guard is reserved for future agentic enrichment.",
            args.max_cost,
        )

    # ── 6. Execute all joins sequentially ───────────────────
    working_df = df.copy()
    join_results: list[dict] = []
    all_warnings: list[str] = []

    for i, spec in enumerate(join_specs):
        ref_label = Path(spec["reference_path"]).name
        logger.info(
            "Executing join %d/%d: '%s'",
            i + 1, len(join_specs), ref_label,
        )
        try:
            working_df, join_stats, join_warnings = execute_join(working_df, spec)
            join_results.append({"reference": ref_label, "stats": join_stats})
            all_warnings.extend(join_warnings)

        except FileNotFoundError as e:
            output_result(format_error(
                str(e),
                suggestion="Check that the reference file path exists and is accessible",
                rows_in=rows_in,
            ))
            return
        except ImportError as e:
            output_result(format_error(
                str(e),
                suggestion="Install the missing package: pip install rapidfuzz",
                rows_in=rows_in,
            ))
            return
        except ValueError as e:
            output_result(format_error(
                f"Join {i + 1} ('{ref_label}') failed: {e}",
                suggestion=(
                    "Check source_key and reference_key column names exist in their "
                    "respective datasets and that match_type is valid."
                ),
                rows_in=rows_in,
            ))
            return
        except Exception as e:
            output_result(format_error(
                f"Unexpected error during join {i + 1} ('{ref_label}'): {e}",
                suggestion="Check reference dataset format and join parameters",
                rows_in=rows_in,
            ))
            return

    # ── 7. Optionally checkpoint enriched data ───────────────
    if workspace:
        try:
            save_checkpoint(
                working_df, workspace,
                step=1, operation="enriched_output",
            )
        except Exception as e:
            logger.warning("Could not save checkpoint: %s", e)

    # ── 8. Save output ──────────────────────────────────────
    _input_fmt = _io_utils.detect_format_from_path(args.input_path)
    try:
        output_path = save_output(working_df, args.output_path, output_format=args.output_format,
                                  input_format=_input_fmt)
    except Exception as e:
        output_result(format_error(
            f"Failed to save output: {e}",
            suggestion="Check output path and disk space",
            rows_in=rows_in,
        ))
        return

    rows_out = len(working_df)

    # ── 9. Build summary ─────────────────────────────────────
    summary: dict = {
        "joins_executed": len(join_results),
        "join_results": join_results,
    }

    if sampled:
        summary["sample_size"] = args.sample_size
        summary["original_rows_in"] = rows_in

    if args.max_cost is not None:
        summary["max_cost_usd"] = args.max_cost
        summary["note_agentic_enrichment"] = (
            "Agentic (LLM-based) enrichment is not yet implemented. "
            "--max-cost is reserved for this future capability."
        )

    # ── 10. Emit result ──────────────────────────────────────
    output_result(format_success(
        output_path=output_path,
        rows_in=rows_in,
        rows_out=rows_out,
        summary=summary,
        warnings=all_warnings,
    ))


if __name__ == "__main__":
    main()
