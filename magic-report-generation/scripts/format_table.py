#!/usr/bin/env python3
"""
Format Table - Format DataFrame as readable Markdown table
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import json
import os
import sys
import pandas as pd
from pathlib import Path

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)


def truncate_cell(value, max_length=50):
    """Truncate cell content if too long."""
    value_str = str(value)
    if len(value_str) > max_length:
        return value_str[:max_length-3] + "..."
    return value_str


def format_number(value):
    """Format numeric values with appropriate precision."""
    if pd.isna(value):
        return ""

    if isinstance(value, (int, float)):
        # Check if it's a currency-like value (has decimal but close to cents)
        if isinstance(value, float):
            # Check if this looks like currency (0-4 decimal places)
            if abs(value) >= 1000:
                # Large number with thousands separator
                if value == int(value):
                    return f"{int(value):,}"
                else:
                    return f"{value:,.2f}"
            elif abs(value) < 1 and value != 0:
                # Small number (statistics) - use 4 decimal places
                return f"{value:.4f}"
            else:
                # Regular number - 2 decimal places
                return f"{value:.2f}"
        else:
            # Integer - add thousands separator if large
            if abs(value) >= 1000:
                return f"{value:,}"
            return str(value)

    return str(value)


def format_markdown_table(df, max_rows=20, max_cols=10):
    """Format DataFrame as Markdown table."""
    rows_in = len(df)
    cols_in = len(df.columns)

    # Truncate columns
    truncated_cols = False
    if cols_in > max_cols:
        df_display = df.iloc[:, :max_cols].copy()
        truncated_cols = True
    else:
        df_display = df.copy()

    # Truncate rows
    truncated_rows = False
    if rows_in > max_rows:
        df_display = df_display.head(max_rows)
        truncated_rows = True

    # Format values
    for col in df_display.columns:
        if pd.api.types.is_numeric_dtype(df_display[col]):
            df_display[col] = df_display[col].apply(format_number)
        else:
            df_display[col] = df_display[col].apply(lambda x: truncate_cell(x, 50))

    # Build markdown table
    lines = []

    # Header
    headers = [str(col) for col in df_display.columns]
    lines.append("| " + " | ".join(headers) + " |")

    # Separator
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

    # Rows
    for _, row in df_display.iterrows():
        row_values = [str(val) if val != "" else " " for val in row]
        lines.append("| " + " | ".join(row_values) + " |")

    # Add footer if truncated
    footer_lines = []
    if truncated_rows:
        remaining = rows_in - max_rows
        footer_lines.append(f"\n*... and {remaining} more rows*")

    if truncated_cols:
        remaining = cols_in - max_cols
        footer_lines.append(f"\n*... and {remaining} more columns*")

    markdown = "\n".join(lines)
    if footer_lines:
        markdown += "\n" + "\n".join(footer_lines)

    return markdown, len(df_display), truncated_rows or truncated_cols


def format_html_table(df, max_rows=20, max_cols=10):
    """Format DataFrame as HTML table."""
    rows_in = len(df)
    cols_in = len(df.columns)

    # Truncate columns
    truncated_cols = False
    if cols_in > max_cols:
        df_display = df.iloc[:, :max_cols].copy()
        truncated_cols = True
    else:
        df_display = df.copy()

    # Truncate rows
    truncated_rows = False
    if rows_in > max_rows:
        df_display = df_display.head(max_rows)
        truncated_rows = True

    # Format values
    for col in df_display.columns:
        if pd.api.types.is_numeric_dtype(df_display[col]):
            df_display[col] = df_display[col].apply(format_number)
        else:
            df_display[col] = df_display[col].apply(lambda x: truncate_cell(x, 50))

    # Convert to HTML
    html = df_display.to_html(index=False, border=1, classes='dataframe')

    # Add footer if truncated
    footer_lines = []
    if truncated_rows:
        remaining = rows_in - max_rows
        footer_lines.append(f"<p><em>... and {remaining} more rows</em></p>")

    if truncated_cols:
        remaining = cols_in - max_cols
        footer_lines.append(f"<p><em>... and {remaining} more columns</em></p>")

    if footer_lines:
        html += "\n" + "\n".join(footer_lines)

    return html, len(df_display), truncated_rows or truncated_cols


def format_latex_table(df, max_rows=20, max_cols=10):
    """Format DataFrame as LaTeX table."""
    rows_in = len(df)
    cols_in = len(df.columns)

    # Truncate columns
    truncated_cols = False
    if cols_in > max_cols:
        df_display = df.iloc[:, :max_cols].copy()
        truncated_cols = True
    else:
        df_display = df.copy()

    # Truncate rows
    truncated_rows = False
    if rows_in > max_rows:
        df_display = df_display.head(max_rows)
        truncated_rows = True

    # Format values
    for col in df_display.columns:
        if pd.api.types.is_numeric_dtype(df_display[col]):
            df_display[col] = df_display[col].apply(format_number)
        else:
            df_display[col] = df_display[col].apply(lambda x: truncate_cell(x, 50))

    # Convert to LaTeX
    latex = df_display.to_latex(index=False)

    # Add footer if truncated
    footer_lines = []
    if truncated_rows:
        remaining = rows_in - max_rows
        footer_lines.append(f"\\textit{{... and {remaining} more rows}}")

    if truncated_cols:
        remaining = cols_in - max_cols
        footer_lines.append(f"\\textit{{... and {remaining} more columns}}")

    if footer_lines:
        latex = latex.rstrip() + "\n" + "\n".join(footer_lines) + "\n"

    return latex, len(df_display), truncated_rows or truncated_cols


def main(input_path: str, output_path: str,
         max_rows: int = 20, max_cols: int = 10,
         format_type: str = "markdown",
         input_format: str = "auto") -> dict:
    """
    Format DataFrame as readable table.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output file
        max_rows: Maximum rows to display
        max_cols: Maximum columns to display
        format_type: Output format (markdown, html, latex)

    Returns:
        Dictionary with success status and formatting metadata
    """
    try:
        # Read data
        df = load_dataframe(input_path, format=input_format)
        rows_in = len(df)

        if rows_in == 0:
            return {
                "success": False,
                "error": "Input file is empty",
                "suggestion": "Provide a CSV file with at least one row"
            }

        # Format based on type
        if format_type == "markdown":
            formatted_table, rows_displayed, truncated = format_markdown_table(df, max_rows, max_cols)
        elif format_type == "html":
            formatted_table, rows_displayed, truncated = format_html_table(df, max_rows, max_cols)
        elif format_type == "latex":
            formatted_table, rows_displayed, truncated = format_latex_table(df, max_rows, max_cols)
        else:
            return {
                "success": False,
                "error": f"Unknown format type: {format_type}",
                "suggestion": "Use: markdown, html, latex"
            }

        # Write output
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(formatted_table)

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_displayed": rows_displayed,
            "truncated": truncated
        }

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check the file path"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Format DataFrame as readable table")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output file")
    parser.add_argument("--max_rows", type=int, default=20,
                       help="Maximum rows to display (default: 20)")
    parser.add_argument("--max_cols", type=int, default=10,
                       help="Maximum columns to display (default: 10)")
    parser.add_argument("--format", dest="format_type", default="markdown",
                       choices=["markdown", "html", "latex"],
                       help="Output format (default: markdown)")
    parser.add_argument("--input-format", default="auto",
                       choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                       help="Input file format (default: auto)")

    args = parser.parse_args()

    result = main(args.input_path, args.output_path,
                 args.max_rows, args.max_cols, args.format_type,
                 input_format=args.input_format)
    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
