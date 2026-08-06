---
name: magic-data-visualization
description: Select appropriate chart types and generate publication-quality visualizations (PNG, SVG, interactive HTML). Use when creating charts, plotting distributions, comparing groups visually, visualizing correlations, or supporting findings with visuals. Covers bar, line, scatter, histogram, box, heatmap, and small multiples. Use after profiling or statistical analysis to communicate results.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: medium
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - visualization
  - charts
  - plots
  - matplotlib
  - plotly
  scripts:
  - scripts/chart_selector.py
  - scripts/generate_chart.py
  - scripts/validate_chart.py
  dependencies:
  - pandas
  - matplotlib
  - seaborn
  - plotly
  when_to_use: 'When creating charts or visual representations of data. Trigger phrases: chart, plot, visualize, histogram, bar chart, scatter, heatmap, box plot, dashboard, include a chart, show me a graph.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "create a chart" / "make a visualization"
- "plot the distribution" / "show me a bar chart"
- "visualize the comparison" / "generate a scatter plot"
- "what chart should I use?"

These produce the SAME behavior as the visualization workflow.

## When to Use

- Need to visualize data distributions, comparisons, trends, or correlations
- Need to select the right chart type for the data
- Need publication-quality static or interactive charts
- After magic-statistical-analysis, to support findings with visuals

**When NOT to Use:** Use magic-data-profiling for automated EDA reports; use magic-report-generation for assembling reports.

## Data Processing Expertise

### Thinking

Before choosing a chart, ask:
- **What story does the data tell?** — Distribution (histogram, box), comparison (bar, grouped bar), relationship (scatter), trend over time (line), composition (stacked bar, horizontal bar). The story determines the chart type. If you cannot articulate the story in one sentence, you do not yet understand the data well enough to visualize it.
- **How many variables am I encoding?** — 1 variable: histogram or box plot. 2 variables: scatter, bar, or line. 3+ variables: use facets (small multiples) or color encoding. Do not overload a single chart with more than 3 visual encodings (position, color, size) — beyond that, readers cannot decode them.
- **Who is the audience?** — Technical audiences tolerate density, annotations, and statistical markers. Executive audiences need simplicity: large fonts, one key takeaway in the title, minimal axis detail. Data exploration audiences need interactivity (hover, zoom, filter). Match the format to the consumer.
- **Static or interactive?** — Static (PNG/SVG) for reports, presentations, and print. Interactive (HTML/Plotly) for exploration and dashboards. Context determines format — do not default to interactive when the output will be embedded in a PDF.
- **How many data points?** — Scatter plots with >10,000 points need alpha transparency or density-based rendering. Bar charts with >20 categories need aggregation into top-N + "Other". Line charts with >5 series become unreadable — use small multiples instead.

| Audience | Format | Detail Level |
|----------|--------|-------------|
| Technical report | Static PNG/SVG | Full axis labels, annotations, statistical markers |
| Executive summary | Static PNG | Clean, minimal, large fonts, key takeaway in title |
| Data exploration | Interactive HTML | Hover tooltips, zoom, filter controls |

### Rules

- **Chart type selection by story**: Comparison: bar chart. Trend over time: line chart. Distribution: histogram or box plot. Relationship between two numeric variables: scatter plot. Composition/part-to-whole: horizontal bar (not pie). Ranking: sorted horizontal bar. Correlation matrix: heatmap (3+ numeric columns).
- **Colorblind-safe palette**: Always use `['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442']`. Never rely on red/green distinction alone — 8% of males have red-green color deficiency.
- **Axis formatting**: Always label both axes with human-readable names (not raw column names). Include units where applicable. Bar chart Y-axis must start at zero. Use `tight_layout()` to prevent label clipping.
- **Category limits**: Bar charts with >20 categories become unreadable. Aggregate into top-N plus an "Other" bucket, or switch to horizontal bar sorted by value.
- **Resolution**: Static charts at 300 DPI minimum for print quality. Remove top and right spines for cleaner appearance.
- **Small multiples over dual axes**: When comparing two metrics, use faceted side-by-side panels, never dual Y-axes. Dual axes invite false correlation by manipulating scale alignment.
- **When to use LLM**: Visualization is deterministic — use code for chart generation, axis scaling, color mapping, and layout. Optional LLM use: generating descriptive chart titles, writing annotation text for inflection points, or summarizing what a chart shows for report captions. Hand off to `magic-data-synthesis` for any text generation needs.

### Constraints

- MUST run chart type selection (heuristic or manual) before generating any chart
- MUST use the colorblind-safe palette for all charts
- MUST include axis labels, title, and legend (when grouped)
- MUST use 300 DPI for static charts
- MUST NOT add chart junk (unnecessary gridlines, decorations, shadows, 3D effects) — every non-data element competes for attention and reduces the data-ink ratio
- NEVER use 3D charts for data communication — 3D perspective distorts area and position perception, making values impossible to compare accurately. A 3D bar chart can make a 20% difference look like 50% depending on viewing angle. Always use 2D alternatives; they are objectively more readable in every tested scenario.
- NEVER use pie charts for comparing values — humans cannot accurately compare angles or areas. A horizontal bar chart communicates the same data with higher precision and supports more categories. The only defensible pie chart is a two-slice chart showing "part vs. whole" — and even then, a single number ("37% of users") is clearer.
- NEVER use dual Y-axes — two Y-axes on the same chart invite false correlation: readers assume visually overlapping lines are related. A revenue line and a temperature line can be made to "correlate" by choosing axis scales. Use faceted panels (side-by-side) or separate charts instead.
- NEVER truncate bar chart Y-axis to exaggerate differences — starting a bar chart Y-axis at a non-zero value makes small differences look dramatic. A bar chart showing values 98 vs 100 with Y-axis starting at 95 visually implies a 5x difference. Line charts may truncate if the range context is clear and labeled.

## Seed Patterns

### Chart type selection logic
```python
def select_chart(df, x_col, y_col=None):
    """Select chart type based on column types and story."""
    x_type = "numeric" if pd.api.types.is_numeric_dtype(df[x_col]) else \
             "datetime" if pd.api.types.is_datetime64_any_dtype(df[x_col]) else \
             "categorical"

    if not y_col:
        return "histogram" if x_type == "numeric" else "horizontal_bar"

    y_type = "numeric" if pd.api.types.is_numeric_dtype(df[y_col]) else "categorical"

    chart_map = {
        ("categorical", "numeric"): "bar",
        ("datetime", "numeric"):    "line",
        ("numeric", "numeric"):     "scatter",
    }
    return chart_map.get((x_type, y_type), "bar")
```

### Bar / scatter / line generation with matplotlib
```python
import matplotlib.pyplot as plt

PALETTE = ['#0072B2', '#E69F00', '#009E73', '#CC79A7', '#56B4E9', '#D55E00', '#F0E442']

def make_chart(df, chart_type, x_col, y_col, output_path, title=None, group_col=None):
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)

    if chart_type == "bar":
        grouped = df.groupby(x_col)[y_col].mean()
        grouped.plot(kind="bar", ax=ax, color=PALETTE[0])
    elif chart_type == "scatter":
        ax.scatter(df[x_col], df[y_col], color=PALETTE[0], alpha=0.6, s=50)
    elif chart_type == "line":
        ax.plot(df[x_col], df[y_col], color=PALETTE[0], linewidth=2)
    elif chart_type == "histogram":
        ax.hist(df[x_col].dropna(), bins=30, color=PALETTE[0], edgecolor="black")

    ax.set_xlabel(x_col)
    ax.set_ylabel(y_col or "Frequency")
    ax.set_title(title or f"{chart_type.title()}: {y_col or x_col}")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
```

### Proper axis labeling and formatting
```python
def format_axes(ax, x_label, y_label, title, rotate_x=False):
    """Apply consistent formatting to any chart axis."""
    ax.set_xlabel(x_label, fontsize=12)
    ax.set_ylabel(y_label, fontsize=12)
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if rotate_x:
        ax.tick_params(axis="x", rotation=45)
        for label in ax.get_xticklabels():
            label.set_ha("right")
```

### Small multiples (faceted comparison)
```python
def faceted_chart(df, chart_type, x_col, y_col, facet_col, output_path):
    """Create side-by-side panels instead of dual Y-axes."""
    groups = df[facet_col].unique()
    n = len(groups)
    fig, axes = plt.subplots(1, n, figsize=(5 * n, 5), dpi=300, sharey=True)
    if n == 1:
        axes = [axes]
    for ax, group_val in zip(axes, groups):
        subset = df[df[facet_col] == group_val]
        if chart_type == "bar":
            subset.groupby(x_col)[y_col].mean().plot(kind="bar", ax=ax, color=PALETTE[0])
        ax.set_title(f"{facet_col}: {group_val}")
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `chart_selector.py` | A | `python3 chart_selector.py data.csv recommendations.json` | `--relationship distribution\|comparison\|correlation\|composition\|trend\|ranking` to override auto-detection. Note: no `sys.exit(1)` on failure — pipeline callers must check JSON `success` field |
| `generate_chart.py` | A | `python3 generate_chart.py data.csv chart.png` | `--chart_type bar`, `--x_col`, `--y_col` for explicit axes; `--interactive --format html` for Plotly output |
| `validate_chart.py` | B | `python3 validate_chart.py data.csv chart_meta.json report.json` | `--input-format` only option. Requires chart metadata JSON (sidecar from generate_chart.py) |

**Reference implementations** -- read patterns, write custom code:

*(none — all visualization scripts are now scriptable)*

**Chart selector → generator handoff:** `chart_selector.py` outputs a `recommendations.json` with `chart_type`, `x_col`, `y_col` fields that map directly to `generate_chart.py --chart_type`, `--x_col`, `--y_col` flags. Pipeline callers should parse the JSON and pass the values as CLI args to `generate_chart.py`.

Scripts accept `--input-format` (auto/csv/tsv/jsonl/json/parquet/excel). `generate_chart.py` accepts `--format` (png/svg/html) and `--interactive`.

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For visualization specifically:** Chart files ARE the checkpoint — once generated, they serve as both output and intermediate artifact.

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After any chart generation | **Always** | Charts are the output; re-rendering is wasteful |
| After multi-panel/dashboard generation | **Always** | Complex layouts expensive to reproduce |
| Quick exploratory plot | **Optional** | Throwaway plots during exploration don't need persistence |

Save chart metadata alongside image files: chart type, columns used, row count, generation parameters, audience.

**Suggested names:** `chart_distribution.png`, `chart_comparison.png`, `dashboard_overview.png`

**Save pattern:**
```python
import json, datetime
from pathlib import Path

def save_checkpoint(df, path: str, metadata: dict = None) -> str:
    """Save data + provenance metadata. Use at phase boundaries."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == ".parquet":
        df.to_parquet(p, index=False)
    elif p.suffix == ".jsonl":
        df.to_json(p, orient="records", lines=True, force_ascii=False)
    else:
        df.to_csv(p, index=False)
    meta = {
        "rows": len(df), "cols": list(df.columns),
        "saved_at": datetime.datetime.utcnow().isoformat(),
        **(metadata or {}),
    }
    p.with_suffix(".meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False)
    )
    return str(p)
```

## Self-Healing

If chart generation fails:
1. Read error message — check `suggestion` field in JSON output
2. Read script source to understand the failure mode
3. Inspect the data: check column types, null counts, unique values
4. Apply the fix below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Too many categories | >20 unique values for bar chart | Aggregate into top-N + "Other" bucket |
| No numeric data | All text columns | Use `word_frequency_bar` or `text_length_histogram` |
| Memory on large data | Too many points for scatter | Sample first (e.g., 10,000 rows); use alpha transparency |
| Column not found | Mismatched column name | Check `df.columns` against the column name you provided |
| Plotly not installed | Missing dependency for interactive charts | `pip install plotly`; or fall back to static matplotlib |
| Truncated labels | Long category names clipped | Use horizontal bar; or rotate x-labels 45 degrees |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Chart selection | `references/chart_selection.md` | Choosing the right chart type |
| Style guide | `references/style_guide.md` | Publication formatting |
| Accessibility | `references/accessibility.md` | Colorblind or contrast issues |
| Advanced patterns | `references/advanced_patterns.md` | Large datasets (>100K points), small multiples, annotations |

**Do NOT Load** `references/advanced_patterns.md` for simple charts under 10K rows — the default generation path handles these without advanced guidance.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- After chart type selection, present recommendations with rationale: recommended chart types ranked by fit, anti-recommendations (chart types to avoid), and suggested column mappings (x/y/color). Ask user which charts to generate before proceeding.

### Workspace Integration
- Update `workspace_state.md` with generated chart paths and metadata.
- Log visualization decisions in `logs/analysis_journal.md`.
