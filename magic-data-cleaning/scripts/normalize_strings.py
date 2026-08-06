#!/usr/bin/env python3
"""
String normalization script.
Cleans and normalizes text data: trim whitespace, fix encoding, normalize whitespace, remove special chars.
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import re
import time
import unicodedata
from pathlib import Path
import pandas as pd


def load_dataframe(path, **kwargs):
    """Stub: load DataFrame from file. See magic-data-loading SKILL.md for full pattern."""
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)
def save_dataframe(df, path, **kwargs):
    """Stub: save DataFrame to file. See magic-data-loading SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == '.parquet': df.to_parquet(p, index=False)
    elif p.suffix in ('.jsonl', '.json'): df.to_json(p, orient='records', lines=p.suffix == '.jsonl')
    else: df.to_csv(p, index=False)


def trim_whitespace(series):
    """Remove leading and trailing whitespace."""
    changes = 0
    original = series.copy()
    series = series.astype(str).str.strip()
    changes = (original != series).sum()
    return series, int(changes)


def fix_encoding(series):
    """Detect and fix common mojibake patterns (Latin-1 → UTF-8)."""
    changes = 0

    # Common mojibake patterns and their fixes
    mojibake_fixes = {
        'Ã©': 'é',
        'Ã¨': 'è',
        'Ã ': 'à',
        'Ã¢': 'â',
        'Ã´': 'ô',
        'Ã®': 'î',
        'Ã§': 'ç',
        'Ã¹': 'ù',
        'Ã»': 'û',
        'Ã«': 'ë',
        'Ã¯': 'ï',
        'Ã¶': 'ö',
        'Ã¼': 'ü',
        'Ã¤': 'ä',
        'Ã±': 'ñ',
        'â€™': "'",
        'â€œ': '"',
        'â€': '"',
        'â€"': '–',
        'â€"': '—',
        'Â': ' ',  # Non-breaking space
        'â€¦': '...',
    }

    fixed_series = series.astype(str).copy()

    for wrong, correct in mojibake_fixes.items():
        mask = fixed_series.str.contains(wrong, regex=False, na=False)
        if mask.any():
            fixed_series = fixed_series.str.replace(wrong, correct, regex=False)
            changes += mask.sum()

    return fixed_series, int(changes)


def normalize_whitespace(series):
    """Normalize internal whitespace (multiple spaces → single space)."""
    changes = 0
    original = series.copy()

    # Replace multiple spaces with single space
    series = series.astype(str).str.replace(r'\s+', ' ', regex=True)

    changes = (original != series).sum()
    return series, int(changes)


def remove_special_chars(series):
    """Remove control characters and normalize unicode."""
    changes = 0

    def clean_text(text):
        if pd.isna(text):
            return text

        text = str(text)

        # Remove control characters (except newline, tab)
        text = ''.join(char for char in text if unicodedata.category(char)[0] != 'C' or char in '\n\t')

        # Normalize unicode (NFC normalization)
        text = unicodedata.normalize('NFC', text)

        return text

    original = series.copy()
    series = series.apply(clean_text)
    changes = (original != series).sum()

    return series, int(changes)


def main(input_path: str, output_path: str, columns: str = None,
         operations: str = "all", input_format: str = "auto",
         output_format: str = "auto", flatten_depth: int = 0,
         chunk_size: int = None) -> dict:
    """
    Normalize string data.

    Args:
        input_path: Path to input file
        output_path: Path to output file
        columns: Comma-separated list of columns to process (None = all text columns)
        operations: "all" or comma-separated: "trim,encoding,whitespace,special"
        input_format: File format for input (auto, csv, jsonl, json, parquet)
        output_format: File format for output (auto, csv, jsonl, json, parquet)

    Returns:
        Dictionary with success status and summary
    """
    try:
        # Read input data
        df = load_dataframe(input_path, format=input_format, flatten_depth=flatten_depth,
                            chunk_size=chunk_size)

        # Quality gate: check for empty input
        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a non-empty CSV file"
            }

        rows_in = len(df)

        # Parse columns
        if columns:
            target_columns = [c.strip() for c in columns.split(",")]
            # Validate columns exist
            invalid_cols = [c for c in target_columns if c not in df.columns]
            if invalid_cols:
                return {
                    "success": False,
                    "error": f"Columns not found: {invalid_cols}",
                    "suggestion": "Check column names and try again"
                }
        else:
            # Default to all object/string columns
            target_columns = df.select_dtypes(include=['object']).columns.tolist()

        if not target_columns:
            return {
                "success": False,
                "error": "No text columns found to process",
                "suggestion": "Specify columns explicitly or ensure data has text columns"
            }

        # Parse operations
        if operations == "all":
            ops = ["trim", "encoding", "whitespace", "special"]
        else:
            ops = [op.strip() for op in operations.split(",")]

        # Validate operations
        valid_ops = ["trim", "encoding", "whitespace", "special"]
        invalid_ops = [op for op in ops if op not in valid_ops]
        if invalid_ops:
            return {
                "success": False,
                "error": f"Invalid operations: {invalid_ops}",
                "suggestion": f"Use only: {', '.join(valid_ops)}"
            }

        # Track changes
        changes = {
            "trim": 0,
            "encoding": 0,
            "whitespace": 0,
            "special": 0
        }

        # Process each column
        columns_processed = []
        for col in target_columns:
            # Skip non-string columns
            if df[col].dtype != object:
                continue

            columns_processed.append(col)
            col_data = df[col]

            # Apply operations in order
            if "trim" in ops:
                col_data, count = trim_whitespace(col_data)
                changes["trim"] += count

            if "encoding" in ops:
                col_data, count = fix_encoding(col_data)
                changes["encoding"] += count

            if "whitespace" in ops:
                col_data, count = normalize_whitespace(col_data)
                changes["whitespace"] += count

            if "special" in ops:
                col_data, count = remove_special_chars(col_data)
                changes["special"] += count

            # Update dataframe
            df[col] = col_data

        # Quality gate: check for empty output
        if df.empty:
            return {
                "success": False,
                "error": "Output is empty after processing",
                "suggestion": "Processing removed all data. Check input file"
            }

        rows_out = len(df)

        # Save output
        save_dataframe(df, output_path, format=output_format, input_format=input_format)

        # Build result
        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "summary": {
                "columns_processed": columns_processed,
                "changes": changes
            }
        }

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check that the file path is correct"
        }
    except pd.errors.EmptyDataError:
        return {
            "success": False,
            "error": "Input file is empty or invalid",
            "suggestion": "Provide a valid CSV file with data"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Normalize string data")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to output file")
    parser.add_argument("--columns", help="Comma-separated list of columns to process")
    parser.add_argument("--operations", default="all",
                        help="Operations to perform: all or comma-separated: trim,encoding,whitespace,special")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto-detect from extension)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto-detect from extension)")
    parser.add_argument("--flatten-depth", type=int, default=0,
                        help="Flatten nested JSON objects to this depth (0=no flattening)")
    parser.add_argument("--chunk-size", type=int, default=None,
                        help="Load data in chunks of this size (for large files)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")

    args = parser.parse_args()
    _start_time = time.time()

    result = main(args.input_path, args.output_path, args.columns, args.operations,
                  args.input_format, args.output_format, getattr(args, 'flatten_depth', 0),
                  chunk_size=args.chunk_size)

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
            ckpt_path = maybe_checkpoint(output_path, "normalize", True,
                                         checkpoint_format=args.checkpoint_format,
                                         metadata=meta)
            if ckpt_path:
                result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
