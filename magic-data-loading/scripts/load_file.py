#!/usr/bin/env python3
"""
Load data file into CSV format for downstream processing.

Supports:
- CSV, TSV, Parquet, JSON, JSONL, Excel
- Auto-detection of encoding and delimiter
- Chunked loading for large files
- Column type detection
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import csv
import glob
import json
import os
import shutil
import sys
import time
from typing import Dict, Any, Optional

import chardet
import pandas as pd

# Add _shared to path for error_utils and io_utils

try:
    from error_utils import suggest_column, format_column_error
except ImportError:
    suggest_column = None
    format_column_error = None


def maybe_checkpoint(df, path, metadata=None):
    """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)


def detect_encoding(file_path: str, sample_size: int = 100000) -> str:
    """
    Detect file encoding using chardet.
    """
    with open(file_path, 'rb') as f:
        raw_data = f.read(sample_size)

    result = chardet.detect(raw_data)
    encoding = result.get('encoding', 'utf-8')
    confidence = result.get('confidence', 0.0)

    if confidence < 0.5:
        encoding = 'utf-8'

    return encoding


def detect_delimiter(file_path: str, encoding: str) -> str:
    """
    Detect delimiter using csv.Sniffer.
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            sample = f.read(8192)

            if not sample.strip():
                return ','

            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=',\t|;')
            return dialect.delimiter
    except (csv.Error, Exception):
        return ','


def detect_column_types(df: pd.DataFrame) -> Dict[str, str]:
    """
    Detect column types using heuristics.

    Returns:
        Dictionary mapping column names to type strings
    """
    column_types = {}

    for col in df.columns:
        # Skip if all null
        if df[col].isna().all():
            column_types[col] = 'null'
            continue

        # Get non-null sample
        sample = df[col].dropna()

        if len(sample) == 0:
            column_types[col] = 'null'
            continue

        # Check pandas dtype first
        dtype = df[col].dtype

        if pd.api.types.is_integer_dtype(dtype):
            column_types[col] = 'integer'
        elif pd.api.types.is_float_dtype(dtype):
            column_types[col] = 'float'
        elif pd.api.types.is_bool_dtype(dtype):
            column_types[col] = 'boolean'
        elif pd.api.types.is_datetime64_any_dtype(dtype):
            column_types[col] = 'datetime'
        elif pd.api.types.is_object_dtype(dtype):
            # Try to infer more specific type
            # Check for numeric
            try:
                pd.to_numeric(sample, errors='raise')
                if (sample.astype(str).str.contains(r'\.', regex=True).any()):
                    column_types[col] = 'float'
                else:
                    column_types[col] = 'integer'
                continue
            except (ValueError, TypeError):
                pass

            # Check for datetime
            try:
                pd.to_datetime(sample, errors='raise')
                column_types[col] = 'datetime'
                continue
            except (ValueError, TypeError):
                pass

            # Check for boolean
            unique_values = set(str(v).lower() for v in sample.unique())
            if unique_values.issubset({'true', 'false', '1', '0', 'yes', 'no', 't', 'f', 'y', 'n'}):
                column_types[col] = 'boolean'
                continue

            # Default to string
            column_types[col] = 'string'
        else:
            column_types[col] = 'string'

    return column_types


def load_csv(file_path: str, encoding: str, delimiter: str, nrows: Optional[int], chunk_size: Optional[int]) -> pd.DataFrame:
    """Load CSV file with optional chunked loading."""
    read_kwargs = {
        'encoding': encoding,
        'sep': delimiter,
        'on_bad_lines': 'skip',
        'engine': 'python'
    }

    if nrows:
        read_kwargs['nrows'] = nrows

    if chunk_size:
        chunks = []
        for chunk in pd.read_csv(file_path, chunksize=chunk_size, **read_kwargs):
            chunks.append(chunk)
            if nrows and sum(len(c) for c in chunks) >= nrows:
                break
        df = pd.concat(chunks, ignore_index=True)
        if nrows:
            df = df.head(nrows)
        return df
    else:
        return pd.read_csv(file_path, **read_kwargs)


def load_json(file_path: str, encoding: str, nrows: Optional[int]) -> pd.DataFrame:
    """Load JSON file."""
    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        data = json.load(f)

    if isinstance(data, list):
        df = pd.DataFrame(data)
    elif isinstance(data, dict):
        df = pd.DataFrame([data])
    else:
        raise ValueError("Unsupported JSON structure")

    if nrows:
        df = df.head(nrows)

    return df


def load_jsonl(file_path: str, encoding: str, nrows: Optional[int],
               chunk_size: Optional[int], flatten_depth: int = 1) -> pd.DataFrame:
    """Load JSONL file with optional nested field flattening."""
    # Use io_utils.flatten_nested if available, else fall back to inline
    _fn = _local_flatten_nested
    records = []

    with open(file_path, 'r', encoding=encoding, errors='replace') as f:
        for i, line in enumerate(f):
            if nrows and i >= nrows:
                break

            line = line.strip()
            if not line:
                continue

            try:
                obj = json.loads(line)
                if flatten_depth > 0 and isinstance(obj, dict):
                    obj = _fn(obj, flatten_depth)
                records.append(obj)
            except json.JSONDecodeError:
                continue

    return pd.DataFrame(records)


def _local_flatten_nested(obj: dict, depth: int, prefix: str = "") -> dict:
    """Local fallback for flatten_nested when io_utils not available."""
    flat = {}
    for key, value in obj.items():
        new_key = f"{prefix}.{key}" if prefix else key
        if isinstance(value, dict) and depth > 0:
            flat.update(_local_flatten_nested(value, depth - 1, new_key))
        else:
            flat[new_key] = value
    return flat


def load_parquet(file_path: str, nrows: Optional[int]) -> pd.DataFrame:
    """Load Parquet file."""
    # Parquet doesn't support nrows directly, read and slice
    df = pd.read_parquet(file_path)

    if nrows:
        df = df.head(nrows)

    return df


def load_excel(file_path: str, nrows: Optional[int]) -> pd.DataFrame:
    """Load Excel file."""
    read_kwargs = {}

    if nrows:
        read_kwargs['nrows'] = nrows

    return pd.read_excel(file_path, **read_kwargs)


def parse_hf_uri(uri: str) -> dict:
    """Parse hf://repo_id[/subset][?split=train&nrows=100] into components."""
    import urllib.parse
    # Remove hf:// prefix
    path = uri[5:]  # Remove "hf://"
    # Split query params
    if "?" in path:
        path, query_str = path.split("?", 1)
        params = dict(urllib.parse.parse_qsl(query_str))
    else:
        params = {}

    # Split path into repo_id and optional subset
    parts = path.split("/")
    if len(parts) >= 3:
        repo_id = "/".join(parts[:2])
        subset = "/".join(parts[2:])
    else:
        repo_id = path
        subset = None

    return {
        "repo_id": repo_id,
        "subset": subset,
        "split": params.get("split", "train"),
        "nrows": int(params["nrows"]) if "nrows" in params else None,
    }


def format_error(message: str, suggestion: str = None) -> dict:
    """Format an error result dict."""
    result = {"success": False, "error": message}
    if suggestion:
        result["suggestion"] = suggestion
    return result


def output_result(result: dict) -> None:
    """Print a result dict as JSON."""
    print(json.dumps(result, indent=2, default=str))


def main(input_path: str, output_path: str, encoding: str = "auto",
         delimiter: str = "auto", nrows: Optional[int] = None,
         chunk_size: Optional[int] = None,
         flatten_depth: int = 1,
         output_format: str = "auto") -> Dict[str, Any]:
    """
    Load data file into CSV for downstream processing.

    Args:
        input_path: Path to input file
        output_path: Path to write CSV output
        encoding: File encoding ("auto" to detect)
        delimiter: Delimiter for CSV/TSV ("auto" to detect)
        nrows: Maximum number of rows to load
        chunk_size: Chunk size for large file processing

    Returns:
        Dictionary with load results
    """
    try:
        if input_path.startswith("hf://"):
            parsed = parse_hf_uri(input_path)
            try:
                df = load_hf_dataset(
                    parsed["repo_id"],
                    split=parsed.get("split", "train"),
                    subset=parsed.get("subset"),
                    nrows=nrows or parsed.get("nrows"),
                )
            except ImportError as e:
                output_result(format_error(str(e), suggestion="pip install datasets"))
                return
            # Detect column types for the HF-loaded DataFrame
            column_types = detect_column_types(df)
            rows_out = len(df)
            columns = len(df.columns)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            df.to_csv(output_path, index=False, encoding="utf-8")
            return {
                "success": True,
                "output_path": output_path,
                "rows_in": rows_out,
                "rows_out": rows_out,
                "columns": columns,
                "column_types": column_types,
                "summary": {
                    "format": "huggingface",
                    "repo_id": parsed["repo_id"],
                    "split": parsed.get("split", "train"),
                },
            }

        # Validate input file exists
        if not os.path.isfile(input_path):
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path is correct"
            }

        # Detect encoding if auto
        if encoding == "auto":
            encoding = detect_encoding(input_path)

        # Detect file format from extension
        file_ext = os.path.splitext(input_path)[1].lower()

        # Load data based on format
        df = None

        if file_ext in ['.csv', '.txt']:
            if delimiter == "auto":
                delimiter = detect_delimiter(input_path, encoding)
            df = load_csv(input_path, encoding, delimiter, nrows, chunk_size)

        elif file_ext == '.tsv':
            delimiter = '\t'
            df = load_csv(input_path, encoding, delimiter, nrows, chunk_size)

        elif file_ext in ['.parquet', '.pq']:
            df = load_parquet(input_path, nrows)

        elif file_ext == '.json':
            df = load_json(input_path, encoding, nrows)

        elif file_ext in ['.jsonl', '.ndjson']:
            df = load_jsonl(input_path, encoding, nrows, chunk_size, flatten_depth)

        elif file_ext in ['.xlsx', '.xls']:
            df = load_excel(input_path, nrows)

        else:
            # Try CSV with auto-detection as fallback
            if delimiter == "auto":
                delimiter = detect_delimiter(input_path, encoding)
            df = load_csv(input_path, encoding, delimiter, nrows, chunk_size)

        # Check if data was loaded
        if df is None or df.empty:
            return {
                "success": False,
                "error": "No data loaded from file",
                "suggestion": "Check file format and content"
            }

        # Detect column types
        column_types = detect_column_types(df)

        rows_out = len(df)
        columns = len(df.columns)

        # Write to output file
        # Derive the input_format from the file extension for smart format resolution
        _input_fmt_map = {
            '.csv': 'csv', '.txt': 'csv', '.tsv': 'tsv',
            '.parquet': 'parquet', '.pq': 'parquet',
            '.json': 'json', '.jsonl': 'jsonl', '.ndjson': 'jsonl',
            '.xlsx': 'excel', '.xls': 'excel',
        }
        _detected_input_format = _input_fmt_map.get(file_ext, 'csv')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        out_ext = os.path.splitext(output_path)[1].lower()
        out_fmt = output_format if output_format != "auto" else out_ext.lstrip('.')
        if out_fmt in ('parquet', 'pq'):
            df.to_parquet(output_path, index=False)
        elif out_fmt in ('jsonl', 'ndjson'):
            df.to_json(output_path, orient='records', lines=True, force_ascii=False)
        elif out_fmt == 'json':
            df.to_json(output_path, orient='records', force_ascii=False)
        else:
            sep = '\t' if out_fmt == 'tsv' else ','
            df.to_csv(output_path, index=False, sep=sep, encoding='utf-8')

        # Verify output file was created
        if not os.path.isfile(output_path):
            return {
                "success": False,
                "error": "Output file was not created",
                "suggestion": "Check write permissions and disk space"
            }

        # Verify output file is not empty
        if os.path.getsize(output_path) == 0:
            return {
                "success": False,
                "error": "Output file is empty",
                "suggestion": "Input file may be empty or unreadable"
            }

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_out,  # Same as rows_out for single file load
            "rows_out": rows_out,
            "columns": columns,
            "column_types": column_types,
            "summary": {
                "format": file_ext.lstrip('.'),
                "encoding": encoding
            }
        }

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check file format, encoding, and permissions"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load data file into CSV format")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to write CSV output")
    parser.add_argument("--encoding", default="auto", help="File encoding (default: auto)")
    parser.add_argument("--delimiter", default="auto", help="Delimiter for CSV/TSV (default: auto)")
    parser.add_argument("--nrows", type=int, help="Maximum number of rows to load")
    parser.add_argument("--chunk_size", type=int, help="Chunk size for large file processing")
    parser.add_argument("--flatten-depth", type=int, default=1,
                        help="Depth to flatten nested JSONL fields (default: 1, 0=no flattening)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto)")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")

    args = parser.parse_args()
    _start_time = time.time()

    if args.explain:
        # Validate input file exists
        if not os.path.isfile(args.input_path):
            print(json.dumps({
                "success": False,
                "error": f"Input file not found: {args.input_path}"
            }, indent=2))
            sys.exit(1)

        file_ext = os.path.splitext(args.input_path)[1].lower()
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "load_file",
                "input": args.input_path,
                "output": args.output_path,
                "steps": [
                    f"Detect format from extension: {file_ext}",
                    f"Detect encoding: {'auto-detect' if args.encoding == 'auto' else args.encoding}",
                    f"Detect delimiter: {'auto-detect' if args.delimiter == 'auto' else repr(args.delimiter)}",
                    f"Load data{' (max ' + str(args.nrows) + ' rows)' if args.nrows else ''}",
                    "Detect column types",
                    f"Write CSV output to {args.output_path}"
                ],
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(
        args.input_path,
        args.output_path,
        encoding=args.encoding,
        delimiter=args.delimiter,
        nrows=args.nrows,
        chunk_size=args.chunk_size,
        flatten_depth=args.flatten_depth,
        output_format=args.output_format
    )

    if result.get("success") and args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "format": getattr(args, "output_format", "json"),
            "input_path": getattr(args, "input_path", getattr(args, "input", "")),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(args.output_path, "load", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
