#!/usr/bin/env python3
"""
Auto-derive numeric features from text columns for use with exploration scripts.

Convenience script that enriches a CSV with numeric representations of text
columns (length, word count, presence flag) so that detect_patterns.py,
segment_analysis.py, and relationship_explorer.py can operate on them.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import time
from pathlib import Path

import pandas as pd

# ---------------------------------------------------------------------------
# Shared utilities (same approach as other scripts in this project)
# ---------------------------------------------------------------------------

def detect_column_types(df):
    """Stub: classify each column as numeric, text, categorical, etc."""
    result = {}
    for col in df.columns:
        import pandas as pd
        if pd.api.types.is_numeric_dtype(df[col]):
            result[col] = "numeric"
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            result[col] = "datetime"
        else:
            non_null = df[col].dropna()
            avg_len = non_null.astype(str).str.len().mean() if len(non_null) > 0 else 0
            result[col] = "text" if avg_len > 50 else "categorical"
    return result

def format_error(message, suggestion=None, **kwargs):
    """Stub: format a standardised error dict."""
    result = {"success": False, "error": message}
    if suggestion:
        result["suggestion"] = suggestion
    result.update(kwargs)
    return result

def output_result(result):
    """Stub: print result as JSON to stdout."""
    import json, sys
    print(json.dumps(result, indent=2, default=str))

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)

def save_dataframe(df, path, format=None, input_format=None, **kwargs):
    """Stub: save DataFrame to path, inferring format from extension."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.parquet':
        df.to_parquet(p, index=False)
    elif p.suffix == '.jsonl':
        df.to_json(p, orient='records', lines=True)
    elif p.suffix == '.json':
        df.to_json(p, orient='records', indent=2)
    else:
        df.to_csv(p, index=False)


# ---------------------------------------------------------------------------
# Safe --derive whitelist
# ---------------------------------------------------------------------------

# Maps expression keyword → actual pandas operation factory.
# Each value is a callable(series) -> series.
# We deliberately DO NOT use eval(); expressions are matched by keyword prefix.

_SAFE_OPERATIONS = {
    "str.len()":              lambda s: s.astype(str).str.len(),
    "str.lower()":            lambda s: s.astype(str).str.lower(),
    "str.upper()":            lambda s: s.astype(str).str.upper(),
    "str.strip()":            lambda s: s.astype(str).str.strip(),
    "str.split().str.len()":  lambda s: s.fillna("").astype(str).str.split().str.len(),
    "notna()":                lambda s: s.notna().astype(int),
    "isna()":                 lambda s: s.isna().astype(int),
    "str.count(digits)":      lambda s: s.astype(str).str.count(r"\d"),
    "str.count(spaces)":      lambda s: s.astype(str).str.count(r"\s"),
    "str.count(punctuation)": lambda s: s.astype(str).str.count(r"[^\w\s]"),
    "str.isnumeric()":        lambda s: s.astype(str).str.isnumeric().astype(int),
    "str.isalpha()":          lambda s: s.astype(str).str.isalpha().astype(int),
    "astype(float)":          lambda s: pd.to_numeric(s, errors="coerce"),
    "astype(int)":            lambda s: pd.to_numeric(s, errors="coerce").astype("Int64"),
    "fillna(0)":              lambda s: pd.to_numeric(s, errors="coerce").fillna(0),
}


def apply_safe_derive(series: pd.Series, expression: str) -> pd.Series:
    """
    Apply a whitelisted pandas operation to a series.

    Args:
        series: The source column.
        expression: Must exactly match one of the keys in _SAFE_OPERATIONS.

    Returns:
        Transformed Series.

    Raises:
        ValueError if expression is not in the whitelist.
    """
    key = expression.strip()
    if key not in _SAFE_OPERATIONS:
        allowed = sorted(_SAFE_OPERATIONS.keys())
        raise ValueError(
            f"Expression '{key}' is not in the safe-operations whitelist. "
            f"Allowed expressions: {allowed}"
        )
    return _SAFE_OPERATIONS[key](series)


# ---------------------------------------------------------------------------
# Core derivation logic
# ---------------------------------------------------------------------------

def derive_text_features(
    df: pd.DataFrame,
    columns: list,
) -> tuple[pd.DataFrame, dict]:
    """
    For each text/object column, add three derived numeric columns:
      - {col}_length      : character count (int)
      - {col}_word_count  : word count (int)
      - {col}_is_present  : 1 if non-null and non-empty, else 0 (int)

    Args:
        df: Input DataFrame (will not be mutated; a copy is returned).
        columns: List of column names to process.

    Returns:
        (enriched_df, derived_features_dict)
    """
    df = df.copy()
    derived_features: dict = {}

    for col in columns:
        # Skip already-numeric columns
        if pd.api.types.is_numeric_dtype(df[col]):
            continue

        str_series = df[col].fillna("").astype(str)

        # Character length
        length_col = f"{col}_length"
        df[length_col] = str_series.str.len().astype(int)
        derived_features[length_col] = {
            "type": "numeric",
            "source": col,
            "method": "str.len()",
        }

        # Word count
        wc_col = f"{col}_word_count"
        df[wc_col] = str_series.str.split().str.len().fillna(0).astype(int)
        derived_features[wc_col] = {
            "type": "numeric",
            "source": col,
            "method": "str.split().str.len()",
        }

        # Presence flag: 1 if original is not null AND stripped value is not empty
        presence_col = f"{col}_is_present"
        df[presence_col] = (df[col].notna() & (str_series.str.strip() != "")).astype(int)
        derived_features[presence_col] = {
            "type": "binary",
            "source": col,
            "method": "notna() & len() > 0",
        }

    return df, derived_features


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(
    input_path: str,
    output_path: str,
    columns: str = None,
    derive: str = None,
    input_format: str = "auto",
    output_format: str = "auto",
) -> dict:
    """
    Prepare a CSV for exploration by auto-deriving numeric features from text columns.

    Args:
        input_path:  Path to the input CSV file.
        output_path: Path where the enriched CSV will be written.
        columns:     Comma-separated list of column names to process.
                     If omitted, all text/object columns are processed.
        derive:      JSON string mapping new_column_name -> whitelisted expression,
                     e.g. '{"word_digits": "str.count(digits)"}'.
                     eval() is never used; expressions must match the whitelist.

    Returns:
        dict: Result object with success flag and derivation summary.
    """
    try:
        # --- Load -----------------------------------------------------------
        df = load_dataframe(input_path, format=input_format)

        if df.empty:
            return format_error(
                "Input file is empty",
                suggestion="Provide a non-empty CSV file",
            )

        rows_in = len(df)
        columns_original = len(df.columns)

        # --- Determine which columns to process -----------------------------
        col_types = detect_column_types(df)

        if columns:
            requested = [c.strip() for c in columns.split(",") if c.strip()]
            missing = [c for c in requested if c not in df.columns]
            if missing:
                return format_error(
                    f"Columns not found in input: {missing}",
                    suggestion=f"Available columns: {list(df.columns)}",
                    rows_in=rows_in,
                )
            target_columns = requested
        else:
            # All text or string (non-numeric) columns.
            # Use is_string_dtype to handle both pandas object dtype (<=2.x)
            # and the native str dtype (pandas 3.x+).
            target_columns = [
                col for col in df.columns
                if col_types.get(col) in ("text", "categorical", "mixed", "empty")
                or (
                    (df[col].dtype == object or pd.api.types.is_string_dtype(df[col]))
                    and col_types.get(col) != "numeric"
                )
            ]

        # --- Auto-derive standard text features -----------------------------
        df, derived_features = derive_text_features(df, target_columns)

        # --- Apply custom --derive expressions (whitelist only) -------------
        if derive:
            try:
                custom_exprs: dict = json.loads(derive)
            except json.JSONDecodeError as exc:
                return format_error(
                    f"Could not parse --derive as JSON: {exc}",
                    suggestion='Use valid JSON, e.g. \'{"new_col": "str.len()"}\'',
                    rows_in=rows_in,
                )

            if not isinstance(custom_exprs, dict):
                return format_error(
                    "--derive must be a JSON object mapping column names to expressions",
                    suggestion='Example: \'{"word_digits": "str.count(digits)"}\'',
                    rows_in=rows_in,
                )

            for new_col, expr in custom_exprs.items():
                # Determine source column: default to first target column, or
                # the user may prefix with "source_col:expression" – keep it
                # simple: the expression operates on the series identified by
                # splitting "source_col:expr" if a colon is present.
                if ":" in expr:
                    src_col, real_expr = expr.split(":", 1)
                    src_col = src_col.strip()
                    real_expr = real_expr.strip()
                else:
                    # No source column specified — not supported for custom derives
                    return format_error(
                        f"Custom derive '{new_col}' must specify a source column "
                        f"using the format 'source_col:expression', e.g. "
                        f"'{{\"new_col\": \"word:str.len()\"}}' ",
                        suggestion="Format: source_column:whitelisted_expression",
                        rows_in=rows_in,
                    )

                if src_col not in df.columns:
                    return format_error(
                        f"Source column '{src_col}' for custom derive '{new_col}' "
                        f"not found in input",
                        suggestion=f"Available columns: {list(df.columns)}",
                        rows_in=rows_in,
                    )

                try:
                    df[new_col] = apply_safe_derive(df[src_col], real_expr)
                    derived_features[new_col] = {
                        "type": "numeric",
                        "source": src_col,
                        "method": real_expr,
                    }
                except ValueError as exc:
                    return format_error(
                        str(exc),
                        suggestion="Use only whitelisted expressions (see --help)",
                        rows_in=rows_in,
                    )

        # --- Save -----------------------------------------------------------
        save_dataframe(df, output_path, format=output_format, input_format=input_format)

        columns_derived = len(derived_features)
        columns_total = len(df.columns)
        n_text_cols = len(target_columns)

        return {
            "success": True,
            "output_path": str(output_path),
            "rows_in": rows_in,
            "rows_out": len(df),
            "columns_original": columns_original,
            "columns_derived": columns_derived,
            "columns_total": columns_total,
            "derived_features": derived_features,
            "summary": (
                f"Derived {columns_derived} features from "
                f"{n_text_cols} text column{'s' if n_text_cols != 1 else ''}"
            ),
        }

    except FileNotFoundError:
        return format_error(
            f"Input file not found: {input_path}",
            suggestion="Check the file path and try again",
        )
    except Exception as exc:
        return format_error(
            str(exc),
            suggestion="Check input data format and arguments",
        )


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description=(
            "Auto-derive numeric features from text columns for use with "
            "detect_patterns.py, segment_analysis.py, and relationship_explorer.py."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Enrich all text columns automatically
  python prepare_for_exploration.py data.csv enriched.csv

  # Only process specific columns
  python prepare_for_exploration.py data.csv enriched.csv --columns word,definition

  # Add a custom derived column (whitelist only — no eval)
  python prepare_for_exploration.py data.csv enriched.csv \\
      --derive '{"word_digits": "word:str.count(digits)"}'

Safe expressions for --derive (format: source_col:expression):
  str.len()              Character count
  str.split().str.len()  Word count
  notna()                1 if non-null, else 0
  isna()                 1 if null, else 0
  str.lower()            Lowercase string
  str.upper()            Uppercase string
  str.strip()            Strip whitespace
  str.count(digits)      Count digit characters
  str.count(spaces)      Count whitespace characters
  str.count(punctuation) Count punctuation characters
  str.isnumeric()        1 if all chars are numeric
  str.isalpha()          1 if all chars are alphabetic
  astype(float)          Convert to float (coerce errors to NaN)
  astype(int)            Convert to integer (coerce errors to NaN)
  fillna(0)              Fill nulls with 0
        """,
    )
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output CSV file")
    parser.add_argument(
        "--columns",
        help="Comma-separated list of columns to process (default: all text/object columns)",
    )
    parser.add_argument(
        "--derive",
        help=(
            'JSON object mapping new column names to whitelisted expressions. '
            'Format: \'{"new_col": "source_col:expression"}\'. '
            'eval() is never used; only whitelisted pandas operations are allowed.'
        ),
    )
    parser.add_argument(
        "--input-format", default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Input file format (default: auto)",
    )
    parser.add_argument(
        "--output-format", default="auto",
        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
        help="Output file format (default: auto)",
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
        columns=args.columns,
        derive=args.derive,
        input_format=args.input_format,
        output_format=args.output_format,
    )

    if result.get("success") and args.auto_checkpoint:
        output_path = result.get("output_path", args.output_path)
        if output_path:
            def maybe_checkpoint(df, path, metadata=None):
                """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
                from pathlib import Path
                p = Path(path)
                p.parent.mkdir(parents=True, exist_ok=True)
                df.to_csv(p, index=False)
                return str(p)
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(output_path, "prepared", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    output_result(result)
    if not result.get("success", True):
        sys.exit(1)
