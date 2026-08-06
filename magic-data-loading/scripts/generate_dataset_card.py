#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""Generate a HuggingFace dataset card (README.md) from data metadata.

Callable tool — agents run this directly via CLI.

Usage:
    python3 generate_dataset_card.py --input data.parquet --repo org/name
    python3 generate_dataset_card.py --input data.csv --repo org/name --license mit --language en zh
    python3 generate_dataset_card.py --input data.parquet --repo org/name --output README.md
"""
from __future__ import annotations

import argparse
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

PROVENANCE_MARKER = "<!-- magic-generated -->"

CREDENTIAL_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"),
    re.compile(r"Bearer\s+\S{20,}"),
    re.compile(r"://\w+:\w+@"),
]

SIZE_BUCKETS = [
    (1_000, "n<1K"),
    (10_000, "1K<n<10K"),
    (100_000, "10K<n<100K"),
    (1_000_000, "100K<n<1M"),
    (10_000_000, "1M<n<10M"),
    (100_000_000, "10M<n<100M"),
    (1_000_000_000, "100M<n<1B"),
]


def scrub_credentials(text: str) -> str:
    """Strip credential patterns from text."""
    for pattern in CREDENTIAL_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return text


def detect_size_category(row_count: int) -> str:
    for threshold, label in SIZE_BUCKETS:
        if row_count < threshold:
            return label
    return "n>1B"


def read_data_schema(input_path: Path) -> tuple[list[dict], int]:
    """Read schema and row count from input file. Returns (features, row_count)."""
    import pandas as pd

    if input_path.suffix == ".parquet":
        df = pd.read_parquet(input_path)
    elif input_path.suffix == ".csv":
        df = pd.read_csv(input_path)
    elif input_path.suffix in (".jsonl", ".json"):
        df = pd.read_json(input_path, lines=input_path.suffix == ".jsonl")
    else:
        print(f"WARNING: Unknown format {input_path.suffix}, trying CSV",
              file=sys.stderr)
        df = pd.read_csv(input_path)

    features = []
    for col in df.columns:
        dtype = str(df[col].dtype)
        dtype_map = {
            "object": "string", "int64": "int64", "int32": "int32",
            "float64": "float64", "float32": "float32", "bool": "bool",
        }
        features.append({
            "name": col,
            "dtype": dtype_map.get(dtype, dtype),
            "non_null_pct": round((1 - df[col].isna().mean()) * 100, 1),
        })
    return features, len(df)


def render_yaml_frontmatter(
    license: str,
    languages: list[str],
    tags: list[str],
    size_category: str,
    features: list[dict],
) -> str:
    """Render YAML frontmatter block."""
    lang_yaml = "\n".join(f"  - {lang}" for lang in languages)
    tag_yaml = "\n".join(f"  - {tag}" for tag in tags)
    feat_yaml = "\n".join(
        f"    - name: {f['name']}\n      dtype: {f['dtype']}" for f in features)

    return f"""---
license: {license}
language:
{lang_yaml}
tags:
{tag_yaml}
size_categories:
  - {size_category}
dataset_info:
  features:
{feat_yaml}
---"""


def render_card(
    repo: str,
    features: list[dict],
    row_count: int,
    license: str = "apache-2.0",
    languages: list[str] | None = None,
    description: str = "",
) -> str:
    """Render full dataset card content."""
    languages = languages or ["en"]
    tags = ["magic-generated"]
    size_cat = detect_size_category(row_count)
    pretty_name = repo.split("/")[-1] if "/" in repo else repo

    frontmatter = render_yaml_frontmatter(
        license, languages, tags, size_cat, features)

    schema_rows = "\n".join(
        f"| {f['name']} | {f['dtype']} | {f['non_null_pct']}% |"
        for f in features)

    safe_desc = scrub_credentials(description) if description else "Processed via MAGIC data agent."

    return f"""{frontmatter}

{PROVENANCE_MARKER}
# {pretty_name}

## Description

{safe_desc}

## Schema

| Column | Type | Non-null |
|--------|------|----------|
{schema_rows}

## Dataset Summary

- **Rows:** {row_count:,}
- **Columns:** {len(features)}
- **Generated:** {datetime.now().strftime('%Y-%m-%d')}
- **Generator:** MAGIC v2

## License

{license}
"""


def generate_card(
    input_path: str | Path,
    repo: str,
    license: str = "apache-2.0",
    languages: list[str] | None = None,
    output_path: str | Path | None = None,
) -> Path:
    """Generate dataset card and write to file."""
    input_path = Path(input_path)
    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    features, row_count = read_data_schema(input_path)
    card_content = render_card(
        repo=repo, features=features, row_count=row_count,
        license=license, languages=languages)

    out = Path(output_path) if output_path else Path("README.md")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(card_content, encoding="utf-8")
    return out


def main():
    parser = argparse.ArgumentParser(
        description="Generate a HuggingFace dataset card from data metadata")
    parser.add_argument("--input", required=True,
                        help="Input data file (parquet, csv, jsonl)")
    parser.add_argument("--repo", required=True,
                        help="HuggingFace repo ID (org/name)")
    parser.add_argument("--license", default="apache-2.0",
                        help="SPDX license identifier")
    parser.add_argument("--language", nargs="*", default=["en"],
                        help="ISO 639-1 language codes")
    parser.add_argument("--output", default=None,
                        help="Output path (default: README.md)")
    args = parser.parse_args()

    out = generate_card(
        input_path=args.input,
        repo=args.repo,
        license=args.license,
        languages=args.language,
        output_path=args.output,
    )
    print(f"✓ Dataset card written to {out}")
    print(f"  Repo: {args.repo}")
    print(f"  License: {args.license}")
    print(f"  Languages: {', '.join(args.language)}")


if __name__ == "__main__":
    main()
