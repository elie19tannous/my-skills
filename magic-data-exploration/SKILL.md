---
name: magic-data-exploration
description: Explore data interactively and detect patterns systematically. Use when investigating a dataset — freely exploring quality issues, comparing segments, discovering correlations, or running automated pattern detection. Covers both interactive investigation (asking questions, following threads) and scripted analysis (pattern detection, segment comparison, relationship exploration).
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
  - exploration
  - patterns
  - segments
  - relationships
  - interactive
  - discovery
  scripts:
  - scripts/detect_patterns.py
  - scripts/prepare_for_exploration.py
  - scripts/segment_analysis.py
  - scripts/relationship_explorer.py
  dependencies:
  - pandas
  - numpy
  - scipy
  - matplotlib
  - seaborn
  when_to_use: 'When investigating data patterns or comparing segments. Trigger phrases: explore, investigate, patterns, what patterns, look into, understand data, compare groups, segment analysis, find templates, similarity.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "let me explore this data" / "I want to investigate this"
- "what's in this dataset?" / "tell me about this data"
- "what patterns do you see?" / "look into this"
- "I want to understand this data before deciding"
- "detect patterns in this data" / "find patterns"
- "run segment analysis" / "compare groups"
- "explore relationships between columns"
- "run automated exploration" / "run pattern detection"

These produce the SAME behavior as the data exploration workflow.

## When to Use

- User wants to investigate data interactively before committing to a processing plan
- User wants to understand quality issues, patterns, or structure
- Need to discover patterns and insights using automated scripts
- Need to compare statistics across groups/segments
- Need to explore pairwise relationships between columns
- After magic-data-profiling, for deeper systematic investigation

**When NOT to Use:** Use `magic-data-profiling` for initial quality scoring and distribution overview. Use `magic-data-cleaning` for applying fixes. Use `magic-statistical-analysis` for formal hypothesis testing. Use `magic-data-lifecycle` for full multi-step processing.

## Data Processing Expertise

### Thinking

Before exploring or interpreting results, ask:

- **Explore or confirm?** — Are you freely investigating (explore stance: follow threads, ask questions, let the data shape emerge) or testing a specific hypothesis (confirm stance: run targeted scripts, validate with evidence)? The approach differs. Exploration is open-ended; confirmation is targeted.
- **Is this pattern real or artifact?** — Small samples, derived columns, and coincidental correlations can all produce false patterns. Verify with different methods before reporting.
- **Does this persist across subgroups?** — A pattern in the aggregate may vanish in subgroups (Simpson's paradox) or only exist in one subgroup. Always check at least one key subgroup before reporting an aggregate finding.
- **Am I correlating derived columns?** — Two columns derived from the same source (e.g., `text_length` and `text_word_count`) will always correlate highly. This is mathematical, not informational. Filter these out before reporting.
- **What's the null hypothesis?** — Would I expect this pattern by random chance? High correlation between two length-derived columns is expected, not insightful.
- **What sampling strategy fits?** — Head/tail catches header artifacts and truncation. Random gives a representative overview. Filtered targets suspicious patterns. Stratified covers categories. Use multiple strategies during exploration.
- **When is exploration done?** — Exploration crystallizes into action when you can state: "The data has [these characteristics], the key issues are [these], and the next step is [this]." If you cannot state that, keep exploring.

### Rules

- **Explore vs. confirm distinction**: Free exploration (the "explore stance") is open-ended, curiosity-driven, and follows threads wherever they lead. Scripted pattern detection (the "confirm stance") runs automated analysis and reports findings with confidence levels. Both are valid; choose based on the user's intent.
- **Pattern detection methodology**: Run `detect_patterns.py` first to surface top findings, then investigate interesting patterns with `segment_analysis.py` and `relationship_explorer.py`. This is "discover then act."
- **Confidence interpretation**: High (>0.8) = statistically robust, suitable for decisions. Medium (0.5-0.8) = exists but may not generalize, investigate further. Low (<0.5) = weak signal, do NOT use for decisions.
- **Segment analysis**: Always check patterns across subgroups. Aggregate patterns that reverse in subgroups (Simpson's paradox) are more common than analysts expect.
- **Text-heavy datasets**: Exploration scripts require numeric or categorical columns. For text-only data, run `prepare_for_exploration.py` first to derive `{col}_length`, `{col}_word_count`, `{col}_is_present` columns.
- **Transition to action**: When exploration reveals a clear action plan, offer to transition. Update workspace state with discoveries. Hand off to the appropriate skill — don't start executing the action from exploration.
- **When to use LLM**: Exploration is deterministic — use code for pattern detection, statistical comparisons, and relationship analysis. If discovered patterns need semantic interpretation (e.g., "are these text clusters meaningfully different?" or "does this pattern reflect real-world categories?"), hand off to `magic-data-synthesis` for LLM-based analysis.

### Constraints

**MUST:**
- Follow "discover then act" pattern — run `detect_patterns.py` before targeted investigation
- Use uncertainty language in all interpretations
- Include confidence levels for findings (high/medium/low)
- Verify patterns across at least one subgroup before reporting aggregate findings
- Run `prepare_for_exploration.py` first for text-only datasets

**MUST NOT:**
- Claim causation from correlation
- Explore all column pairs exhaustively — use `--max-pairs` to limit
- Report low-confidence (<0.5) patterns as key findings
- Modify data files or create new checkpoints during exploration
- Auto-capture findings without user agreement (in interactive mode)

**NEVER:**
- NEVER report derived-column correlations as insights — `text_length` and `text_word_count` from the same column always correlate highly; this is mathematical, not informational
- NEVER report a pattern found only in aggregate — check at least one key subgroup; aggregate patterns reverse in subgroups more often than analysts expect (Simpson's paradox)
- NEVER modify source data during exploration — exploration is read-only; if action is needed, transition to the appropriate skill

## Seed Patterns

### Prepare text columns for exploration
```python
import pandas as pd

def derive_text_features(df: pd.DataFrame, text_cols: list[str]) -> pd.DataFrame:
    for col in text_cols:
        df[f"{col}_length"] = df[col].astype(str).str.len()
        df[f"{col}_word_count"] = df[col].fillna("").astype(str).str.split().str.len()
        df[f"{col}_is_present"] = df[col].notna().astype(int)
    return df
```

### Detect patterns with confidence ranking
```python
import pandas as pd
import numpy as np
from scipy import stats

def detect_variance_patterns(df: pd.DataFrame, numeric_cols: list[str]) -> list[dict]:
    findings = []
    for col in numeric_cols:
        cv = df[col].std() / df[col].mean() if df[col].mean() != 0 else 0
        if cv > 1.5:
            findings.append({
                "type": "high_variance", "column": col,
                "cv": round(cv, 3), "confidence": "high" if cv > 2.0 else "medium",
            })
    return sorted(findings, key=lambda f: f["cv"], reverse=True)
```

### Segment comparison
```python
import pandas as pd
from scipy import stats

def compare_segments(df: pd.DataFrame, group_col: str, value_col: str) -> dict:
    groups = {name: grp[value_col].dropna() for name, grp in df.groupby(group_col)}
    if len(groups) < 2:
        return {"status": "insufficient_groups"}
    group_list = list(groups.values())
    stat, p_value = stats.kruskal(*group_list)
    return {
        "group_col": group_col, "value_col": value_col,
        "n_groups": len(groups), "p_value": round(p_value, 6),
        "significant": p_value < 0.05,
        "group_sizes": {str(k): len(v) for k, v in groups.items()},
    }
```

### Pairwise relationship scoring
```python
import pandas as pd
from scipy import stats

def score_relationships(df: pd.DataFrame, cols: list[str], max_pairs: int = 20) -> list[dict]:
    results = []
    for i, col_a in enumerate(cols):
        for col_b in cols[i+1:]:
            data = df[[col_a, col_b]].dropna()
            if len(data) < 10:
                continue
            r, p = stats.pearsonr(data[col_a], data[col_b])
            if abs(r) > 0.3:
                results.append({
                    "col_a": col_a, "col_b": col_b,
                    "r": round(r, 4), "p_value": round(p, 6),
                    "strength": "strong" if abs(r) > 0.7 else "moderate",
                })
    return sorted(results, key=lambda x: abs(x["r"]), reverse=True)[:max_pairs]
```

## Database Exploration

When exploring a database source, explore **in-place first** via SQL queries before extracting. Don't dump everything to a checkpoint and then explore — investigate inside the database, decide what's interesting, then extract only what you need.

Read `magic-data-loading/SKILL.md` `## Database Loading` for connection and query patterns. Call `connect_database.py` and `inspect_schema.py` directly for connection and schema discovery. For custom SQL queries during exploration, read `extract_data.py` patterns and write adapted code.

### Exploration Sequence

1. **Connect** — Call `connect_database.py --env-var DATABASE_URL` directly (callable tool)
2. **Discover schema** — Call `inspect_schema.py --env-var DATABASE_URL` directly (callable tool)
3. **Profile in-place via SQL** — Understand data shape without extracting:
   - Null rates: `SELECT COUNT(*) - COUNT(column) as nulls, COUNT(*) as total FROM table`
   - Value distributions: `SELECT column, COUNT(*) as n FROM table GROUP BY column ORDER BY n DESC`
   - Distinct counts: `SELECT COUNT(DISTINCT column) FROM table`
   - Numeric stats: `SELECT MIN(col), MAX(col), AVG(col), COUNT(*) FROM table`
   - Sentinels: `SELECT column, COUNT(*) FROM table WHERE column IN ('N/A','TBD','unknown') GROUP BY column`
4. **Investigate relationships** — Explore across tables before deciding on JOINs:
   - FK integrity: `SELECT COUNT(*) FROM child WHERE fk_col NOT IN (SELECT id FROM parent)`
   - Cardinality: `SELECT fk_col, COUNT(*) FROM child GROUP BY fk_col ORDER BY COUNT(*) DESC LIMIT 10`
   - Cross-table aggregation: `SELECT c.region, COUNT(o.id), SUM(o.total) FROM customers c JOIN orders o ON c.id = o.customer_id GROUP BY c.region`
5. **Sample actual values** — `SELECT * FROM table ORDER BY RANDOM() LIMIT 5` to see real data
6. **Decide what to extract** — Based on findings, extract only the relevant subset to a checkpoint. If you found quality issues (nulls, sentinels, type inconsistencies), the extracted data will likely need `magic-data-cleaning`. If distributions or patterns are interesting, `magic-data-profiling` gives you a structured quality score on the checkpoint.
7. **Extract and continue** — Save to checkpoint. From here, the standard pipeline applies — profiling, cleaning, transformation, visualization, and reporting all work on checkpoint files. If you want to visualize patterns you discovered during exploration, `magic-data-visualization` has chart selection rules and anti-patterns to follow. If a finding needs statistical validation (e.g., "is spending really different across regions?"), `magic-statistical-analysis` has test selection guidance.

### Database Exploration Seed Patterns

```python
from sqlalchemy import create_engine, text
import os

def profile_column_sql(engine, table: str, column: str) -> dict:
    """Profile a single column in-place without extracting the full table."""
    with engine.connect() as conn:
        stats = conn.execute(text(f"""
            SELECT COUNT(*) as total,
                   COUNT({column}) as non_null,
                   COUNT(DISTINCT {column}) as distinct_vals
            FROM {table}
        """)).fetchone()
        return {
            "total": stats[0], "non_null": stats[1],
            "null_pct": round((1 - stats[1]/stats[0]) * 100, 1) if stats[0] > 0 else 0,
            "distinct": stats[2], "uniqueness": round(stats[2]/stats[0] * 100, 1) if stats[0] > 0 else 0,
        }

def investigate_relationship(engine, parent_table: str, child_table: str, fk_col: str, parent_pk: str = "id") -> dict:
    """Check FK integrity and cardinality between two tables."""
    with engine.connect() as conn:
        orphans = conn.execute(text(f"""
            SELECT COUNT(*) FROM {child_table}
            WHERE {fk_col} NOT IN (SELECT {parent_pk} FROM {parent_table})
        """)).fetchone()[0]
        top_parents = conn.execute(text(f"""
            SELECT {fk_col}, COUNT(*) as n FROM {child_table}
            GROUP BY {fk_col} ORDER BY n DESC LIMIT 5
        """)).fetchall()
        return {"orphan_rows": orphans, "top_parents": [(r[0], r[1]) for r in top_parents]}
```

### Database Exploration Rules

- **Always read-only** — Never modify data during exploration.
- **Explore in-place, then extract** — Run SQL queries to understand the data first. Extract only what you need. This is faster and avoids pulling large tables into memory. Once extracted to a checkpoint, hand off to the appropriate skill — `magic-data-profiling` for quality scoring, `magic-data-cleaning` for fixing issues, `magic-data-transformation` for reshaping or aggregating.
- **Schema first, data second** — Inspect structure before querying. Understanding FKs prevents incorrect JOINs.
- **Check cardinality before JOINs** — If both sides have duplicates on the join key, you get a cartesian explosion.
- **Sample before full extract** — `LIMIT 100` to understand shape before pulling full tables.
- **Parameterized queries** — Use `:param` style, never f-string interpolation into SQL.


## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `detect_patterns.py` | A | `python3 detect_patterns.py data.csv patterns.csv` | `--max-findings 20` for broader coverage. 6 detectors: temporal cycle, categorical imbalance, numeric cluster, text pattern (URL/email/phone), outlier presence, correlation |
| `prepare_for_exploration.py` | A | `python3 prepare_for_exploration.py data.csv prepared.csv` | `--columns col1,col2` to restrict; `--derive '{"new_col": "src:expression"}'` for custom derives. Auto: derives `_length`, `_word_count`, `_is_present` for all text cols |
| `relationship_explorer.py` | A | `python3 relationship_explorer.py data.csv relationships.csv` | `--columns col1,col2` to restrict (avoids O(n²) pairs); `--max-pairs 20` for wider coverage. Auto-routes: Pearson for num-num, Mann-Whitney/Kruskal-Wallis for num-cat, Chi-square for cat-cat. Produces PNG charts in `{stem}_charts/` |
| `segment_analysis.py` | A | `python3 segment_analysis.py data.csv segments.csv` | `--group_col col` when auto-detect picks wrong column; `--value_cols col1,col2` to narrow metrics. Auto: finds column with 2-10 unique values |

**Reference implementations** -- read patterns, write custom code:

*(none — all exploration scripts are now scriptable)*

Scripts accept `--input-format`; output scripts accept `--output-format`. Use POSITIONAL arguments (`input_file output_file`), not `--input` flags.

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For exploration specifically:**

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After pattern detection (detect_patterns.py) | **Yes** | Findings are expensive to re-compute on large data |
| After segment analysis | **Yes** if large dataset or >30s | Segment comparisons involve full-dataset scans |
| After relationship exploration | **Optional** | Often exploratory; skip if just browsing |
| Exploration crystallizes into action plan | **Yes** | Save findings that drive the next phase |

**Suggested names:** `patterns_detected.json`, `segment_analysis.json`, `exploration_findings.json`

Include provenance metadata: source file, timestamp, scripts used, confidence levels.

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

If exploration fails:
1. Read error output — check for missing columns or incompatible types
2. Run `prepare_for_exploration.py` if scripts report "no numeric columns"
3. Use `--group_col` with a lower-cardinality column if segment analysis produces too many groups
4. Inspect a sample of rows to understand unexpected data structure

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| No patterns found | Clean/uniform data | Note absence as a finding — uniform data is informative |
| Too many segments | High cardinality group column | Use `--group_col` with lower cardinality column |
| No numeric columns | Text-only dataset | Run `prepare_for_exploration.py` first |
| Correlation all NaN | Insufficient non-null pairs | Check null rates; filter to columns with >50% non-null |
| Script timeout | Dataset too large | Sample first with `sample_rows.py --n 10000`, then explore |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Interpretation | `references/interpretation_guide.md` | MANDATORY — before writing finding descriptions or presenting results |
| Exploration heuristics | `references/exploration_heuristics.md` | MANDATORY — before choosing exploration approach based on data shape |

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### The Explore Stance

When working interactively, adopt the explore stance:
- **Curious, not prescriptive** — Ask questions that emerge from the data, don't follow a script
- **Open threads, not interrogations** — Surface multiple interesting directions, let the user follow what resonates
- **Visual** — Use tables, ASCII diagrams, and charts to communicate findings
- **Adaptive** — Follow interesting threads, pivot when new information emerges
- **Patient** — Don't rush to conclusions, let the shape of the data emerge
- **Grounded** — Read actual data values, cite specific rows and patterns
- **Time-aware** — After 5+ exchanges on the same topic, offer a summary and suggest capturing findings or shifting focus

### PAUSE Gates

- After running `detect_patterns.py`, present top patterns ranked by confidence. Include: pattern description, affected columns, confidence level, and sample values. Ask user which patterns to investigate further.
- If conflicting patterns are discovered, present both with evidence and confidence levels. Don't hide contradictions — they're often the most interesting findings.

### User-Controlled Capture

When a finding or decision crystallizes during exploration:
- Offer to capture it: "That's a quality finding. Record it in the analysis journal?"
- NEVER auto-capture — the user must explicitly agree
- If user declines, continue exploration without pressure

### Transition to Action

When exploration reveals a clear action plan:
- Offer to transition: "We've identified the cleaning strategy. Ready to switch to cleaning mode?"
- Update `workspace_state.md` with discoveries and proposed plan
- Record key decisions in `logs/analysis_journal.md`
- Hand off to the appropriate data skill — don't start executing the action

### Workspace Integration
- Update `workspace_state.md` with exploration results
- Log findings and decisions in `logs/analysis_journal.md`
