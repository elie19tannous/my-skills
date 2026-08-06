#!/usr/bin/env python3
"""
Generate Chart - Create static and interactive charts
"""
# SCRIPTABLE TOOL — Call directly for standard use. Read source for advanced customization.


import argparse
import glob
import json
import os
import shutil
import sys
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from collections import Counter
import re

def load_dataframe(path, **kwargs):
    import pandas as pd
    from pathlib import Path
    p = Path(path)
    if p.suffix == '.parquet': return pd.read_parquet(p)
    if p.suffix == '.jsonl': return pd.read_json(p, lines=True)
    if p.suffix == '.json': return pd.read_json(p)
    return pd.read_csv(p)

def maybe_checkpoint(df, path, metadata=None):
    """Stub: save DataFrame as checkpoint. See magic-data-lifecycle SKILL.md for full pattern."""
    from pathlib import Path
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(p, index=False)
    return str(p)

# Plotly import (optional)
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Colorblind-safe palette
COLORBLIND_PALETTE = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442']


def detect_column_type(series):
    """Detect semantic type of a column."""
    if pd.api.types.is_numeric_dtype(series):
        return "numeric"
    elif pd.api.types.is_datetime64_any_dtype(series):
        return "datetime"
    elif pd.api.types.is_object_dtype(series):
        non_null = series.dropna()
        if len(non_null) == 0:
            return "categorical"
        avg_len = non_null.astype(str).str.len().mean()
        if avg_len > 20:
            return "text"
        return "categorical"
    return "categorical"


def auto_select_chart(df, x_col, y_col, group_col):
    """Automatically select best chart type based on column types."""
    if x_col and x_col in df.columns:
        x_type = detect_column_type(df[x_col])
    else:
        x_type = None

    if y_col and y_col in df.columns:
        y_type = detect_column_type(df[y_col])
    else:
        y_type = None

    # Single numeric column
    if x_col and not y_col and x_type == "numeric":
        return "histogram"

    # Single text column
    if x_col and not y_col and x_type == "text":
        return "word_frequency_bar"

    # Datetime x, numeric y
    if x_type == "datetime" and y_type == "numeric":
        return "line"

    # Categorical x, numeric y
    if x_type == "categorical" and y_type == "numeric":
        return "bar"

    # Two numeric columns
    if x_type == "numeric" and y_type == "numeric":
        return "scatter"

    # Default
    return "bar"


def create_histogram(df, x_col, title, output_path, format_type, interactive):
    """Create histogram."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.histogram(df, x=x_col, title=title,
                          color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
        ax.hist(df[x_col].dropna(), bins=30, color=COLORBLIND_PALETTE[0], edgecolor='black')
        ax.set_xlabel(x_col)
        ax.set_ylabel('Frequency')
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        # Save PNG
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        # Also save SVG
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_bar(df, x_col, y_col, group_col, title, output_path, format_type, interactive):
    """Create bar chart."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.bar(df, x=x_col, y=y_col, color=group_col, title=title,
                    color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if group_col:
            # Grouped bar
            grouped = df.groupby([x_col, group_col])[y_col].mean().unstack()
            grouped.plot(kind='bar', ax=ax, color=COLORBLIND_PALETTE[:len(grouped.columns)])
            ax.legend(title=group_col)
        else:
            # Simple bar
            grouped = df.groupby(x_col)[y_col].mean()
            grouped.plot(kind='bar', ax=ax, color=COLORBLIND_PALETTE[0])

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_horizontal_bar(df, x_col, y_col, title, output_path, format_type, interactive):
    """Create horizontal bar chart (for composition/ranking)."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.bar(df, y=x_col, x=y_col, orientation='h', title=title,
                    color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if y_col:
            # Ranking
            grouped = df.groupby(x_col)[y_col].mean().sort_values()
        else:
            # Composition
            grouped = df[x_col].value_counts().sort_values()

        grouped.plot(kind='barh', ax=ax, color=COLORBLIND_PALETTE[0])
        ax.set_xlabel(y_col if y_col else 'Count')
        ax.set_ylabel(x_col)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_line(df, x_col, y_col, group_col, title, output_path, format_type, interactive):
    """Create line chart."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.line(df, x=x_col, y=y_col, color=group_col, title=title,
                     color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if group_col:
            for i, (name, group) in enumerate(df.groupby(group_col)):
                ax.plot(group[x_col], group[y_col],
                       color=COLORBLIND_PALETTE[i % len(COLORBLIND_PALETTE)],
                       label=name, linewidth=2)
            ax.legend(title=group_col)
        else:
            ax.plot(df[x_col], df[y_col], color=COLORBLIND_PALETTE[0], linewidth=2)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_scatter(df, x_col, y_col, group_col, title, output_path, format_type, interactive):
    """Create scatter plot."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.scatter(df, x=x_col, y=y_col, color=group_col, title=title,
                        color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if group_col:
            for i, (name, group) in enumerate(df.groupby(group_col)):
                ax.scatter(group[x_col], group[y_col],
                          color=COLORBLIND_PALETTE[i % len(COLORBLIND_PALETTE)],
                          label=name, alpha=0.6, s=50)
            ax.legend(title=group_col)
        else:
            ax.scatter(df[x_col], df[y_col], color=COLORBLIND_PALETTE[0], alpha=0.6, s=50)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_box(df, x_col, y_col, title, output_path, format_type, interactive):
    """Create box plot."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.box(df, x=x_col, y=y_col, title=title,
                    color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if x_col:
            df.boxplot(column=y_col, by=x_col, ax=ax, patch_artist=True,
                      boxprops=dict(facecolor=COLORBLIND_PALETTE[0]))
            plt.suptitle('')
        else:
            ax.boxplot(df[y_col].dropna(), patch_artist=True,
                      boxprops=dict(facecolor=COLORBLIND_PALETTE[0]))
            ax.set_ylabel(y_col)

        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_violin(df, x_col, y_col, title, output_path, format_type, interactive):
    """Create violin plot."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.violin(df, x=x_col, y=y_col, title=title,
                       color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if x_col:
            sns.violinplot(data=df, x=x_col, y=y_col, ax=ax, palette=COLORBLIND_PALETTE)
        else:
            sns.violinplot(data=df, y=y_col, ax=ax, color=COLORBLIND_PALETTE[0])

        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_heatmap(df, title, output_path, format_type, interactive):
    """Create correlation heatmap."""
    # Get only numeric columns
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()

    if interactive and PLOTLY_AVAILABLE:
        fig = px.imshow(corr, text_auto='.2f', title=title,
                       color_continuous_scale='RdBu_r', zmin=-1, zmax=1)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 8), dpi=300)
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                   vmin=-1, vmax=1, ax=ax, cbar_kws={'label': 'Correlation'})
        ax.set_title(title)
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_kde(df, x_col, title, output_path, format_type, interactive):
    """Create KDE plot."""
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    df[x_col].dropna().plot(kind='kde', ax=ax, color=COLORBLIND_PALETTE[0], linewidth=2)
    ax.set_xlabel(x_col)
    ax.set_ylabel('Density')
    ax.set_title(title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    if format_type == "png":
        svg_path = output_path.replace('.png', '.svg')
        plt.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close()


def create_area(df, x_col, y_col, group_col, title, output_path, format_type, interactive):
    """Create area chart."""
    if interactive and PLOTLY_AVAILABLE:
        fig = px.area(df, x=x_col, y=y_col, color=group_col, title=title,
                     color_discrete_sequence=COLORBLIND_PALETTE)
        fig.write_html(output_path)
    else:
        fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

        if group_col:
            for i, (name, group) in enumerate(df.groupby(group_col)):
                ax.fill_between(group[x_col], group[y_col],
                              color=COLORBLIND_PALETTE[i % len(COLORBLIND_PALETTE)],
                              alpha=0.6, label=name)
            ax.legend(title=group_col)
        else:
            ax.fill_between(df[x_col], df[y_col], color=COLORBLIND_PALETTE[0], alpha=0.6)

        ax.set_xlabel(x_col)
        ax.set_ylabel(y_col)
        ax.set_title(title)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        if format_type == "png":
            svg_path = output_path.replace('.png', '.svg')
            plt.savefig(svg_path, format='svg', bbox_inches='tight')
        plt.close()


def create_word_frequency_bar(df, x_col, title, output_path, format_type, interactive):
    """Create word frequency bar chart."""
    # Extract all words
    all_text = ' '.join(df[x_col].dropna().astype(str))
    words = re.findall(r'\b\w+\b', all_text.lower())

    # Count top 20
    word_counts = Counter(words).most_common(20)
    words_df = pd.DataFrame(word_counts, columns=['word', 'count'])

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.barh(words_df['word'], words_df['count'], color=COLORBLIND_PALETTE[0])
    ax.set_xlabel('Frequency')
    ax.set_ylabel('Word')
    ax.set_title(title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.invert_yaxis()
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    if format_type == "png":
        svg_path = output_path.replace('.png', '.svg')
        plt.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close()


def create_text_length_histogram(df, x_col, title, output_path, format_type, interactive):
    """Create text length histogram."""
    lengths = df[x_col].dropna().astype(str).str.len()

    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    ax.hist(lengths, bins=30, color=COLORBLIND_PALETTE[0], edgecolor='black')
    ax.set_xlabel('Text Length (characters)')
    ax.set_ylabel('Frequency')
    ax.set_title(title)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()

    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    if format_type == "png":
        svg_path = output_path.replace('.png', '.svg')
        plt.savefig(svg_path, format='svg', bbox_inches='tight')
    plt.close()


def main(input_path: str, output_path: str,
         chart_type: str = "auto", x_col: str = None, y_col: str = None,
         group_col: str = None, title: str = None,
         format_type: str = "png", interactive: bool = False,
         input_format: str = "auto") -> dict:
    """
    Create static and interactive charts.

    Args:
        input_path: Path to input CSV file
        output_path: Path to output chart file
        chart_type: Type of chart to create
        x_col: X-axis column
        y_col: Y-axis column
        group_col: Grouping column
        title: Chart title
        format_type: Output format (png, svg, html)
        interactive: Create interactive plotly chart

    Returns:
        Dictionary with success status and chart metadata
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

        # Auto-detect columns if not provided
        if not x_col and len(df.columns) > 0:
            x_col = df.columns[0]
        if not y_col and len(df.columns) > 1:
            y_col = df.columns[1]

        # Auto-select chart type
        if chart_type == "auto":
            chart_type = auto_select_chart(df, x_col, y_col, group_col)

        # Default title
        if not title:
            title = f"{chart_type.replace('_', ' ').title()}"
            if x_col and y_col:
                title += f": {y_col} by {x_col}"
            elif x_col:
                title += f": {x_col}"

        # Adjust output path for format
        if interactive or format_type == "html":
            if not output_path.endswith('.html'):
                output_path = output_path.replace('.png', '.html').replace('.svg', '.html')
            interactive = True
        elif format_type == "svg":
            if not output_path.endswith('.svg'):
                output_path = output_path.replace('.png', '.svg').replace('.html', '.svg')
        else:
            if not output_path.endswith('.png'):
                output_path = output_path.replace('.svg', '.png').replace('.html', '.png')

        # Check plotly availability for interactive
        if interactive and not PLOTLY_AVAILABLE:
            return {
                "success": False,
                "error": "Plotly not installed",
                "suggestion": "Install plotly for interactive charts: pip install plotly"
            }

        # Create directory
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        # Create chart based on type
        if chart_type == "histogram":
            create_histogram(df, x_col, title, output_path, format_type, interactive)
        elif chart_type == "bar":
            create_bar(df, x_col, y_col, group_col, title, output_path, format_type, interactive)
        elif chart_type == "horizontal_bar":
            create_horizontal_bar(df, x_col, y_col, title, output_path, format_type, interactive)
        elif chart_type == "line":
            create_line(df, x_col, y_col, group_col, title, output_path, format_type, interactive)
        elif chart_type == "scatter":
            create_scatter(df, x_col, y_col, group_col, title, output_path, format_type, interactive)
        elif chart_type == "box":
            create_box(df, x_col, y_col, title, output_path, format_type, interactive)
        elif chart_type == "violin":
            create_violin(df, x_col, y_col, title, output_path, format_type, interactive)
        elif chart_type == "heatmap":
            create_heatmap(df, title, output_path, format_type, interactive)
        elif chart_type == "kde":
            create_kde(df, x_col, title, output_path, format_type, interactive)
        elif chart_type == "area":
            create_area(df, x_col, y_col, group_col, title, output_path, format_type, interactive)
        elif chart_type == "word_frequency_bar":
            create_word_frequency_bar(df, x_col, title, output_path, format_type, interactive)
        elif chart_type == "text_length_histogram":
            create_text_length_histogram(df, x_col, title, output_path, format_type, interactive)
        else:
            return {
                "success": False,
                "error": f"Unknown chart type: {chart_type}",
                "suggestion": "Use: histogram, bar, line, scatter, box, violin, heatmap, kde, area, horizontal_bar, word_frequency_bar, text_length_histogram"
            }

        result = {
            "success": True,
            "output_path": output_path,
            "rows_in": rows_in,
            "rows_out": rows_in,
            "chart_type": chart_type,
            "format": format_type,
            "interactive": interactive,
            "summary": {
                "x": x_col,
                "y": y_col,
                "group": group_col
            }
        }

        return result

    except FileNotFoundError:
        return {
            "success": False,
            "error": f"Input file not found: {input_path}",
            "suggestion": "Check the file path"
        }
    except KeyError as e:
        return {
            "success": False,
            "error": f"Column not found: {e}",
            "suggestion": "Check column names in the input file"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "suggestion": "Check input file format and parameters"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create static and interactive charts")
    parser.add_argument("input_path", help="Path to input CSV file")
    parser.add_argument("output_path", help="Path to output chart file")
    parser.add_argument("--chart_type", default="auto",
                       help="Type of chart to create (auto, histogram, bar, line, scatter, box, violin, heatmap, kde, area, horizontal_bar, word_frequency_bar, text_length_histogram)")
    parser.add_argument("--x_col", help="X-axis column")
    parser.add_argument("--y_col", help="Y-axis column")
    parser.add_argument("--group_col", help="Grouping column")
    parser.add_argument("--title", help="Chart title")
    parser.add_argument("--format", dest="format_type", default="png",
                       choices=["png", "svg", "html"],
                       help="Output format")
    parser.add_argument("--interactive", action="store_true",
                       help="Create interactive plotly chart")
    parser.add_argument("--auto-checkpoint", action="store_true",
                        help="Save a checkpoint copy of the output file")
    parser.add_argument("--checkpoint-format", choices=["csv", "parquet", "jsonl"], default=None,
                        help="Format for checkpoint files (default: same as output format)")
    parser.add_argument("--explain", action="store_true",
                        help="Print execution plan and exit without creating output")
    parser.add_argument("--input-format", default="auto",
                        choices=["auto", "csv", "tsv", "jsonl", "json", "parquet", "excel"],
                        help="Input file format (default: auto)")

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

        chart_type_desc = args.chart_type if args.chart_type != "auto" else "auto-detect based on column types"
        steps = [
            f"Read CSV from {args.input_path}",
            f"Chart type: {chart_type_desc}",
            f"X column: {args.x_col or '(auto-detect)'}",
            f"Y column: {args.y_col or '(auto-detect)'}",
            f"Group column: {args.group_col or '(none)'}",
            f"Format: {args.format_type}",
            f"Interactive: {args.interactive}",
            f"Render chart to {args.output_path}"
        ]
        plan = {
            "success": True,
            "execution_plan": {
                "operation": "generate_chart",
                "input": args.input_path,
                "output": args.output_path,
                "steps": steps,
                "note": "No files will be created in explain mode"
            }
        }
        print(json.dumps(plan, indent=2))
        sys.exit(0)

    result = main(args.input_path, args.output_path,
                 args.chart_type, args.x_col, args.y_col,
                 args.group_col, args.title,
                 args.format_type, args.interactive,
                 input_format=args.input_format)

    if result.get("success") and args.auto_checkpoint:
        meta = {
            "script": os.path.relpath(__file__),
            "cli_args": {k: v for k, v in vars(args).items() if k not in ("auto_checkpoint",)},
            "rows_in": result.get("rows_in", 0),
            "rows_out": result.get("rows_out", 0),
            "format": getattr(args, "format_type", "json"),
            "input_path": getattr(args, "input_path", getattr(args, "input", "")),
            "duration_seconds": round(time.time() - _start_time, 3),
        }
        ckpt_path = maybe_checkpoint(result.get("output_path", args.output_path), "chart", True,
                                     checkpoint_format=args.checkpoint_format,
                                     metadata=meta)
        if ckpt_path:
            result["checkpoint_path"] = ckpt_path

    print(json.dumps(result, indent=2, default=str))

    sys.exit(0 if result["success"] else 1)
