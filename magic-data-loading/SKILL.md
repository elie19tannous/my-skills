---
name: magic-data-loading
description: Load and ingest data from any source — files (CSV, TSV, Parquet, JSON, JSONL, Excel), databases (SQLite, PostgreSQL, MySQL via connection string), or remote repositories (HuggingFace Hub datasets). Auto-detects format, encoding, and delimiter for files. Use when a user mentions data, a dataset, a file, a database, a table, records, or any structured data source they want to work with — even vague references like 'I have some data' or 'help me with this dataset'.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: low
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - ingestion
  - loading
  - csv
  - parquet
  - json
  - excel
  - database
  - huggingface
  - data-source
  scripts:
  - scripts/detect_format.py
  - scripts/load_file.py
  - scripts/sample_rows.py
  - scripts/validate_load.py
  - scripts/text_parser.py
  - scripts/connect_database.py
  - scripts/inspect_schema.py
  - scripts/extract_data.py
  - scripts/inspect_hf_dataset.py
  - scripts/download_hf_dataset.py
  - scripts/generate_dataset_card.py
  dependencies:
  - pandas
  - chardet
  - openpyxl
  - pyarrow
  - sqlalchemy
  - huggingface_hub
  - httpx
  when_to_use: 'When user mentions data, dataset, CSV, file, database, table, HuggingFace, records, or any structured data source. Trigger phrases: load, read, import, ingest, open, parse, I have data, I have a dataset, connect to database, check HuggingFace.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "load this file" / "read this CSV" / "import this data"
- "open this dataset" / "ingest this file"
- "parse this file" / "convert to CSV" / "what format is this file"
- User provides a file path ending in `.csv`, `.tsv`, `.jsonl`, `.json`, `.parquet`, `.xlsx`
- "connect to this database" / "query this table" / "extract data from my DB"
- "check this HuggingFace dataset" / "download from HuggingFace" / "inspect this HF repo"
- "generate dataset card" / "create README for dataset"
- "I have some data" / "I have a dataset" / "help me with this data" (vague — ask what the source is)
- User mentions data, records, a table, a dataset, or any structured data source

These produce the SAME behavior as using the data loading workflow directly.

## When to Use

- User provides a data file (CSV, TSV, Parquet, JSON, JSONL, Excel)
- User mentions a database connection, table name, or SQL query
- User references a HuggingFace dataset (by name, URL, or "HF" mention)
- User mentions "data", "dataset", "records", or "table" without specifying a source — ask clarifying questions to identify the source type before loading
- Need to load data for analysis, cleaning, or transformation
- Need to preview data before full processing
- Need to detect file format or encoding

**When NOT to Use:** Data is already loaded as a DataFrame; use magic-data-profiling for analysis instead.

## Data Processing Expertise

### Thinking

Before loading any file, ask:
- **What format is this really?** — File extensions lie. A `.csv` may be tab-separated, a `.json` may be JSONL, a `.xlsx` may have formulas that resolve to stale cached values. Always detect by content, not extension.
- **How big is this file?** — Files >100MB need chunked loading. >500MB needs streaming. Loading a 2GB CSV into memory crashes silently or produces truncated results with no error.
- **Is row 1 actually the header?** — Government datasets, exported reports, and scientific data often have metadata rows, BOM markers, or multi-line headers before the actual data. Inspect the first 5 rows before assuming header position.
- **What encoding will break?** — UTF-8 is common but not universal. East Asian datasets often use Big5, GB2312, Shift_JIS, or EUC-KR. European exports may be Latin-1 or Windows-1252. Auto-detection can be wrong on large files with mixed content — always validate a sample after loading.
- **How many sources am I merging?** — Multi-source loading requires schema normalization before concatenation. Column names differ across sources (`id` vs `article_id`, `body` vs `content`). Track source provenance per record.
- **Does the user need quality context?** — After loading data successfully, consider whether the user would benefit from an immediate quality overview. If they asked to "analyze", "check", or "understand" the data, run quality_score (from magic-data-profiling) alongside the load results. If they explicitly asked to "just load" or "import", skip profiling and present load results only. The quality baseline saves work later — catching issues early is cheaper than discovering them mid-pipeline.
- **What kind of data source is this?** — Files, databases, and HuggingFace each have different loading patterns. For files: detect format and encoding. For databases: need a connection string and query or table name. For HuggingFace: need dataset name and optional split/config. Identify the source type before attempting to load.

### Rules

- **Format detection before load**: Always detect by content, not extension. Extension + magic bytes + first-line heuristic is the reliable chain (see `detect_format.py`).
- **Encoding fallback chain**: Try detected encoding → UTF-8 → platform default. For CJK data: UTF-8 → Big5 → GB2312 → Shift_JIS. Confidence threshold <0.5 means fall back to UTF-8.
- **Multi-source loading**: Normalize schemas before merging. Map equivalent columns (`id`→`article_id`, `body`→`content`). Track source provenance per record with a `source` field.
- **Row count accuracy**: Multiline quoted CSV → physical lines ≠ records. Always validate post-load with actual DataFrame row count, not line count.
- **Excel multi-sheet**: Default loaders read only Sheet 1. Check `openpyxl.load_workbook(path).sheetnames` and load each sheet explicitly. Formula cells resolve to cached values — may be stale.
- **When to use LLM**: Data loading is deterministic — use code, not LLM. If loaded text needs semantic transformation (HTML→markdown, translation, entity extraction), hand off to `magic-data-synthesis` after loading.

### Constraints

- MUST auto-detect encoding and delimiter before loading
- MUST validate after loading — check row counts, column types, null patterns
- MUST NOT load >500MB into memory without chunking
- MUST NOT modify the source file
- NEVER skip format detection and load with assumed parameters — a `.csv` with tab delimiters loads as a single column with no error; a file with Latin-1 encoding loaded as UTF-8 silently corrupts accented characters into mojibake (`"café"` → `"cafÃ©"`)
- NEVER trust `estimated_rows` from line counting on multiline CSV — a 1000-line file may contain only 200 records when text fields contain newlines
- NEVER load Excel without checking for multiple sheets — if real data is on Sheet2, you get metadata or a summary table instead

## Seed Patterns

### Load single file (any format)
```python
import pandas as pd
from pathlib import Path

def load_file(path: str, format: str = "auto") -> pd.DataFrame:
    p = Path(path)
    if format == "auto":
        format = detect_format(p)  # content-sniff, not extension
    loaders = {
        "csv": lambda f: pd.read_csv(f, encoding=detect_encoding(str(f))),
        "parquet": pd.read_parquet,
        "jsonl": lambda f: pd.read_json(f, lines=True),
        "json": pd.read_json,
        "excel": pd.read_excel,
    }
    return loaders[format](p)
```

### Format detection (extension + content sniffing)
```python
import csv, json
from pathlib import Path

def detect_format(path: Path) -> str:
    with open(path, "rb") as f:
        header = f.read(8)
    if header.startswith(b"PAR1"): return "parquet"
    if header.startswith((b"\xd0\xcf\x11\xe0", b"PK\x03\x04")): return "excel"
    with open(path, "r", errors="replace") as f:
        line = f.readline().strip()
    try:
        json.loads(line)
        second = f.readline().strip()
        if second:
            try:
                json.loads(second)
                return "jsonl"
            except (json.JSONDecodeError, ValueError):
                pass
        return "json"
    except (json.JSONDecodeError, ValueError):
        pass
    return {"csv": "csv", "tsv": "tsv"}.get(path.suffix.lstrip("."), "csv")
```

### Chunked streaming for large files
```python
import pandas as pd

def stream_large_csv(path: str, chunk_size: int = 10_000, encoding: str = "utf-8"):
    for chunk in pd.read_csv(path, chunksize=chunk_size, encoding=encoding,
                              on_bad_lines="skip", engine="python"):
        yield chunk

# Concatenate or process in-flight
chunks = list(stream_large_csv("big.csv", chunk_size=50_000))
df = pd.concat(chunks, ignore_index=True)
```

### Multi-source merge with schema normalization
```python
from pathlib import Path
import pyarrow.parquet as pq

def merge_sources(source_dirs: list[Path], column_map: dict = None) -> list[dict]:
    column_map = column_map or {"id": "article_id", "body": "content",
                                 "subject": "title", "text": "content"}
    records = []
    for source_dir in source_dirs:
        for shard in sorted(source_dir.glob("*.parquet")):
            for row in pq.read_table(shard).to_pylist():
                row["source"] = shard.stem
                for old, new in column_map.items():
                    if old in row and new not in row:
                        row[new] = row.pop(old)
                records.append(row)
    return records
```

### JSONL loading with nested field flattening
```python
import json
import pandas as pd

def load_jsonl_flat(path: str, max_depth: int = 2) -> pd.DataFrame:
    def flatten(d, prefix="", depth=0):
        items = {}
        for k, v in d.items():
            key = f"{prefix}{k}"
            if isinstance(v, dict) and depth < max_depth:
                items.update(flatten(v, key + ".", depth + 1))
            else:
                items[key] = v
        return items

    with open(path) as f:
        records = [flatten(json.loads(line)) for line in f if line.strip()]
    return pd.DataFrame(records)
```

## Database Loading

### Domain Knowledge

When a user provides a database connection or asks to load from a database:

- **Source detection**: Connection string patterns — `postgresql://`, `mysql://`, `sqlite:///`, or env var names like `DATABASE_URL`, `PG_URL`, `MYSQL_URL`
- **Credential pattern**: Always resolve from environment variables, never hardcoded. Lookup order: explicit env var → `DATABASE_URL` → dialect-specific (`PG_URL`, `MYSQL_URL`)
- **Read-only default**: Enforce at connection level (not query level). SQLite: `PRAGMA query_only = ON`. PostgreSQL: `default_transaction_read_only=on`. MySQL: `SET SESSION TRANSACTION READ ONLY`
- **Query safety**: Row limits (default 10,000), parameterized queries only (never string interpolation), chunked reads for large result sets
- **Dual-mode output**: Interactive sessions → checkpoint file (`ckpt_extracted.parquet`). Pipeline mode → `list[dict]` via `query_as_records()`

### Database Code Patterns

#### Connect to database (read-only, from env var)
```python
from sqlalchemy import create_engine, text, event
import os

def connect_db(env_var: str = "DATABASE_URL", read_only: bool = True):
    url = os.environ[env_var]
    engine = create_engine(url)
    if read_only and url.startswith("sqlite"):
        @event.listens_for(engine, "connect")
        def set_sqlite_readonly(dbapi_conn, _):
            dbapi_conn.execute("PRAGMA query_only = ON")
    return engine
```

#### Inspect schema (tables, columns, FKs)
```python
from sqlalchemy import inspect as sa_inspect

def get_schema(engine):
    insp = sa_inspect(engine)
    return [{
        "table": t,
        "columns": [c["name"] for c in insp.get_columns(t)],
        "fks": [fk["referred_table"] for fk in insp.get_foreign_keys(t)],
    } for t in insp.get_table_names()]
```

#### Extract data with row limit
```python
import pandas as pd

def extract(engine, query: str, limit: int = 10000, params: dict = None):
    if "LIMIT" not in query.upper():
        query = f"{query.rstrip(';')} LIMIT {limit}"
    return pd.read_sql(query, engine, params=params)
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Callable tools** -- call directly via CLI:

| Script | Purpose | CLI usage |
|--------|---------|-----------|
| `detect_format.py` | Content-sniffing format detection | `python3 detect_format.py input_file output.json` |
| `inspect_hf_dataset.py` | Inspect HF dataset remotely (no download) | `python3 inspect_hf_dataset.py --dataset org/name [--sample-rows 3]` |
| `download_hf_dataset.py` | Download HF dataset to local directory | `python3 download_hf_dataset.py --dataset org/name --output data/input/hf/ [--patterns "*.parquet"]` |
| `generate_dataset_card.py` | Generate dataset card from data | `python3 generate_dataset_card.py --input data.parquet --repo org/name [--license apache-2.0]` |
| `connect_database.py` | Connect, health check, list tables | `python3 connect_database.py --env-var DATABASE_URL` |
| `inspect_schema.py` | Schema discovery (tables, columns, FKs) | `python3 inspect_schema.py --env-var DATABASE_URL [--table name]` |

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `load_file.py` | A | `python3 load_file.py input.csv output.parquet` | `--nrows 10000` for sampling; `--chunk_size N` for >100MB files; `--flatten-depth 2` for nested JSONL; `--explain` for dry-run; supports `hf://` URIs |
| `validate_load.py` | B | `python3 validate_load.py loaded.csv --original_path raw.csv --output_path report.json` | Always add `--original_path` to catch silent data loss. 1% tolerance threshold for row count |
| `sample_rows.py` | B | `python3 sample_rows.py data.parquet sample.csv --n 100 --method head` | `--method random` for unbiased sample; `--method stratified --stratify_column label` for class-balanced |
| `extract_data.py` | B | `python3 extract_data.py --query "SELECT * FROM table LIMIT 100"` | Always provide `--query`; add `--output path.parquet` to save as checkpoint; `--limit N` for large extracts. Exposes `chunked_read()` generator for large results |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `text_parser.py` | State-machine text parsing | Two distinct modes (template vs raw text); markers/fields/separators always data-specific |

Scripts accept `--input-format` (auto/csv/tsv/jsonl/json/parquet/excel) and `--output-format`.

## HuggingFace Loading

### When to Use
- User mentions a HuggingFace dataset (by name or `hf://datasets/...` URL)
- Need to explore what's in a dataset before deciding to download
- Need to download a dataset (full or selective) for local processing
- Need to generate a dataset card for upload

### Thinking
Before loading from HuggingFace, ask:
- **Do I need the full dataset?** — Inspect first with `inspect_hf_dataset.py` to see schema, splits, and sizes. Only download what you need using `--patterns`.
- **Is this dataset gated?** — Gated datasets require access approval. If you get a GatedRepoError, guide the user to the dataset page to request access.
- **What format are the files?** — Most HF datasets are parquet. After download, use the standard loading skill to load into DataFrame.

### Callable Scripts

These handle standardized HuggingFace operations. Call them directly via CLI — no need to write custom code.

| Script | Purpose | CLI usage |
|--------|---------|-----------|
| `inspect_hf_dataset.py` | Inspect dataset remotely (no download) | `python3 inspect_hf_dataset.py --dataset org/name [--sample-rows 3]` |
| `download_hf_dataset.py` | Download dataset to local directory | `python3 download_hf_dataset.py --dataset org/name --output data/input/hf/ [--patterns "*.parquet"]` |
| `generate_dataset_card.py` | Generate dataset card from data | `python3 generate_dataset_card.py --input data.parquet --repo org/name [--license apache-2.0]` |

### Callable Tool Pipeline Patterns

When writing pipeline inline code (not calling scripts), use these library calls directly:

```python
# download_hf_dataset.py pattern
from huggingface_hub import snapshot_download
snapshot_download("org/name", repo_type="dataset", local_dir="data/input/hf",
                  allow_patterns=["*.parquet"])

# inspect_hf_dataset.py pattern
from huggingface_hub import HfApi
api = HfApi()
info = api.dataset_info("org/name")
files = api.list_repo_tree("org/name", repo_type="dataset")

# detect_format.py pattern — pure heuristic, no library needed
import json
from pathlib import Path
ext = Path(file).suffix.lower()
fmt = {".csv": "csv", ".tsv": "tsv", ".json": "json", ".jsonl": "jsonl",
       ".parquet": "parquet", ".xlsx": "excel"}.get(ext, "unknown")

# generate_dataset_card.py pattern
from huggingface_hub import DatasetCard, DatasetCardData
card_data = DatasetCardData(language="en", license="apache-2.0", task_categories=["text-classification"])
card = DatasetCard.from_template(card_data)
card.push_to_hub("org/name")
```

### Token Resolution

HF scripts resolve authentication automatically:
1. Explicit env var (via `--token-env`)
2. `HF_TOKEN` env var
3. `HUGGING_FACE_HUB_TOKEN` env var (legacy)
4. Cached CLI login (`huggingface-cli login`)

If no token is found, public datasets still work. Private/gated datasets require a token.

### Workflow
1. **Inspect first:** Always run `inspect_hf_dataset.py` before downloading to understand the dataset
2. **Download selectively:** Use `--patterns "*.parquet"` to avoid downloading READMEs, configs, etc.
3. **Load normally:** After download, use the standard file loading patterns (parquet → DataFrame)
4. **Checkpoint:** Save a checkpoint after loading from HF — re-downloading is expensive

### Constraints
- MUST inspect before downloading large datasets (>100MB)
- MUST use `--patterns` for selective download when only specific file types are needed
- MUST NOT hardcode HF tokens — always use env var resolution
- MUST NOT download to inspect — use `inspect_hf_dataset.py` for remote inspection

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**After loading:** The natural next step is `magic-data-profiling` to get a quality score and understand distributions. For database sources, you may want `magic-data-exploration` first to investigate in-place before extracting everything. If loaded text needs semantic transformation (HTML→markdown, entity extraction), hand off to `magic-data-synthesis`.

**For loading specifically:** Loading is typically the cheapest phase to re-run for local files. The judgment call shifts toward "yes, save" when:
- Source is remote (database, HuggingFace Hub) — extraction cost is high
- Multiple shards were merged — re-merging is fragile
- Encoding detection was ambiguous — result may differ on re-run
- The loaded dataset feeds a ≥3-phase pipeline downstream

**Suggested names:** `loaded.parquet`, `corpus_loaded.jsonl`, or pipeline-specific descriptive names.

Include provenance metadata: source file, timestamp, encoding used, row counts.

## Self-Healing

If loading fails:
1. Read error JSON — check `suggestion` field
2. Read script source to understand the failure mode
3. Inspect first 20 rows with `sample_rows.py --n 20`
4. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| UnicodeDecodeError | Non-UTF-8 encoding | Re-run `detect_format.py`, use detected encoding |
| ParserError | Wrong delimiter | Re-run with correct delimiter from detection |
| MemoryError | File too large | Use chunked streaming (see Seed Patterns) |
| EmptyDataError | Empty or corrupt file | Check file, verify path |
| No records parsed | Markers don't match input | Check marker patterns match actual delimiters in text |
| Only first sheet loaded | Multi-sheet Excel file | Use `--sheet` or iterate `openpyxl.load_workbook(path).sheetnames` |
| "Parquet magic bytes not found" | File content doesn't match .parquet extension | Check with `file` command; if "CSV text", re-load with correct output format or convert with `pd.read_csv().to_parquet()` |
| validate_load.py fails on checkpoint | Checkpoint file is corrupted or wrong format | Verify with `file <path>`; delete and re-run load step |

## Format Ambiguity Guide

When format detection is ambiguous, think through these scenarios:

| Situation | What Might Go Wrong | Recommended Approach |
|-----------|--------------------|--------------------|
| `.csv` but tab-separated | Loads as single column | Detect by content; check delimiter field before loading |
| `.json` but actually JSONL | JSON parser fails on multi-object file | Check if file has one JSON object per line → use JSONL loader |
| `.xlsx` with multiple sheets | Only first sheet loaded | Check sheet names; load each separately |
| No file extension | Content detection may guess wrong | Inspect first 20 bytes; specify format explicitly |
| Low detection confidence | Format is unusual or mixed | Read first 5-10 lines raw, identify pattern, specify format |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Format detection | `references/format_detection.md` | Unusual format or detection fails |
| Large files | `references/large_file_patterns.md` | File >100MB or MemoryError |
| Advanced loading | `references/advanced_loading.md` | Chunked loading, schema-on-read, evolving schemas, multi-file assembly |

**Do NOT Load** `references/large_file_patterns.md` for files under 100MB — the default loading path handles these without chunking guidance.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- If unusual format detected (non-standard encoding, ambiguous delimiter, nested structure), present detection results and ask user to confirm load parameters before proceeding.

### Workspace Integration
- Update `workspace_state.md` with load results (format, encoding, row/column counts).
- Log loading decisions in `logs/analysis_journal.md`.
