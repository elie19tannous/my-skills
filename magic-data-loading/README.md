# Magic Data Loading

Load and ingest data from any source — files, databases, or HuggingFace Hub — with automatic format, encoding, and delimiter detection.

## What This Skill Does

- Reads CSV, TSV, Parquet, JSON, JSONL, and Excel files with auto-detected encoding and delimiters
- Connects to SQLite, PostgreSQL, and MySQL databases via connection string, and inspects schemas
- Downloads and inspects HuggingFace Hub datasets, including generating dataset cards

## Files

- `SKILL.md` — Agent knowledge document and frontmatter
- `scripts/` — `detect_format.py`, `load_file.py`, `sample_rows.py`, `validate_load.py`, `text_parser.py`, `connect_database.py`, `inspect_schema.py`, `extract_data.py`, `inspect_hf_dataset.py`, `download_hf_dataset.py`, `generate_dataset_card.py`

## Related Skills

- `magic-data-lifecycle` — loading is the first active phase of every pipeline
- `magic-data-profiling` — profile immediately after loading to assess quality
- `magic-data-validation` — validate schema and types after loading
