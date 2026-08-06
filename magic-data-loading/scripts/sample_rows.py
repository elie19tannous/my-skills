#!/usr/bin/env python3
"""
Sample rows from data file for preview.

Supports three sampling methods:
- head: First N rows
- random: Random N rows
- stratified: Stratified sampling by column
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
from typing import Dict, Any, Optional

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


def sample_head(df: pd.DataFrame, n: int) -> pd.DataFrame:
    """Get first N rows."""
    return df.head(n)


def sample_random(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """Get random N rows."""
    n = min(n, len(df))
    return df.sample(n=n, random_state=seed)


def sample_stratified(df: pd.DataFrame, n: int, column: str, seed: int = 42) -> pd.DataFrame:
    """
    Get stratified sample by column.

    Samples proportionally from each unique value in the column.
    """
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in data")

    # Calculate samples per group
    value_counts = df[column].value_counts()
    total_rows = len(df)

    samples = []
    for value, count in value_counts.items():
        proportion = count / total_rows
        n_samples = max(1, int(n * proportion))

        group_df = df[df[column] == value]
        if len(group_df) <= n_samples:
            samples.append(group_df)
        else:
            samples.append(group_df.sample(n=n_samples, random_state=seed))

    result = pd.concat(samples, ignore_index=True)

    # If we got too many samples, randomly select n
    if len(result) > n:
        result = result.sample(n=n, random_state=seed)

    return result


def load_file(file_path: str, input_format: str = "auto",
              flatten_depth: int = 0) -> pd.DataFrame:
    """
    Load file into DataFrame using io_utils.

    Supports CSV, TSV, Parquet, JSON, JSONL, Excel.
    """
    return load_dataframe(file_path, format=input_format, flatten_depth=flatten_depth)


def main(input_path: str, output_path: str, n: int = 100,
         method: str = "head", stratify_column: Optional[str] = None,
         input_format: str = "auto", output_format: str = "auto",
         flatten_depth: int = 0) -> Dict[str, Any]:
    """
    Sample rows from data file without loading entire file.

    Args:
        input_path: Path to input file
        output_path: Path to write sampled CSV
        n: Number of rows to sample
        method: Sampling method ("head", "random", "stratified")
        stratify_column: Column name for stratified sampling
        flatten_depth: Flatten nested JSON objects to this depth (0=no flattening)

    Returns:
        Dictionary with sampling results
    """
    try:
        # Validate input file exists
        if not os.path.isfile(input_path):
            return {
                "success": False,
                "error": f"Input file not found: {input_path}",
                "suggestion": "Verify the file path is correct"
            }

        # Validate method
        valid_methods = ["head", "random", "stratified"]
        if method not in valid_methods:
            return {
                "success": False,
                "error": f"Invalid method: {method}",
                "suggestion": f"Use one of: {', '.join(valid_methods)}"
            }

        # Validate stratified parameters
        if method == "stratified" and not stratify_column:
            return {
                "success": False,
                "error": "stratify_column required for stratified sampling",
                "suggestion": "Provide --stratify_column argument"
            }

        # Load data
        df = load_file(input_path, input_format, flatten_depth=flatten_depth)

        if df.empty:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Check file content"
            }

        rows_in = len(df)

        # Sample based on method
        if method == "head":
            sampled_df = sample_head(df, n)
        elif method == "random":
            sampled_df = sample_random(df, n)
        elif method == "stratified":
            sampled_df = sample_stratified(df, n, stratify_column)
        else:
            sampled_df = sample_head(df, n)

        rows_out = len(sampled_df)

        # Write to output file
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        save_dataframe(sampled_df, output_path, format=output_format, input_format=input_format)

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
                "suggestion": "Sampling may have failed"
            }

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_out,
            "method": method,
            "sample_ratio": round(rows_out / rows_in, 4) if rows_in > 0 else 0
        }

        if method == "stratified":
            result["stratify_column"] = stratify_column

        return result

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check file format and sampling parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Sample rows from data file")
    parser.add_argument("input_path", help="Path to input file")
    parser.add_argument("output_path", help="Path to write sampled output")
    parser.add_argument("--n", type=int, default=100, help="Number of rows to sample (default: 100)")
    parser.add_argument("--method", default="head",
                        choices=["head", "random", "stratified"],
                        help="Sampling method (default: head)")
    parser.add_argument("--stratify_column", help="Column name for stratified sampling")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")
    parser.add_argument("--output-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Output file format (default: auto)")
    parser.add_argument("--flatten-depth", type=int, default=0,
                        help="Flatten nested JSON objects to this depth (0=no flattening)")

    args = parser.parse_args()

    result = main(
        args.input_path,
        args.output_path,
        n=args.n,
        method=args.method,
        stratify_column=args.stratify_column,
        input_format=args.input_format,
        output_format=args.output_format,
        flatten_depth=args.flatten_depth,
    )

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
