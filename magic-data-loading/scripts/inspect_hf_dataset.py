#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""Inspect a HuggingFace dataset remotely via the Datasets Server REST API.

Callable tool — agents run this directly via CLI. No download needed.

Usage:
    python3 inspect_hf_dataset.py --dataset stanfordnlp/imdb
    python3 inspect_hf_dataset.py --dataset org/name --config default --split train --sample-rows 5
    python3 inspect_hf_dataset.py --dataset org/private-data --token-env MY_HF_TOKEN
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Optional

API_BASE = "https://datasets-server.huggingface.co"
TIMEOUT = 15


def clean_hf_token(token: str | None) -> str | None:
    if token is None:
        return None
    return token.replace("\r", "").replace("\n", "").strip() or None


def resolve_hf_token(env_var: str = "HF_TOKEN") -> str | None:
    for var in [env_var, "HF_TOKEN", "HUGGING_FACE_HUB_TOKEN"]:
        token = clean_hf_token(os.environ.get(var))
        if token:
            return token
    try:
        from huggingface_hub import get_token
        return get_token()
    except Exception:
        return None


def _api_get(endpoint: str, params: dict, token: str | None) -> dict | None:
    """GET request to Datasets Server API. Returns parsed JSON or None."""
    import httpx

    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    try:
        r = httpx.get(f"{API_BASE}{endpoint}", params=params,
                      headers=headers, timeout=TIMEOUT)
        r.raise_for_status()
        return r.json()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return None
        raise
    except httpx.ConnectError:
        return None


def fetch_splits(dataset: str, token: str | None) -> dict | None:
    return _api_get("/splits", {"dataset": dataset}, token)


def fetch_info(dataset: str, config: str, token: str | None) -> dict | None:
    return _api_get("/info", {"dataset": dataset, "config": config}, token)


def fetch_first_rows(
    dataset: str, config: str, split: str, token: str | None
) -> dict | None:
    return _api_get("/first-rows",
                    {"dataset": dataset, "config": config, "split": split},
                    token)


def fetch_parquet_files(dataset: str, token: str | None) -> dict | None:
    return _api_get("/parquet", {"dataset": dataset}, token)


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def inspect_dataset(
    dataset: str,
    config: str | None = None,
    split: str | None = None,
    sample_rows: int = 3,
    token: str | None = None,
) -> str:
    """Inspect dataset via Datasets Server API. Returns markdown report."""
    lines = [f"## Dataset: {dataset}", ""]

    # Splits
    splits_data = fetch_splits(dataset, token)
    if splits_data is None:
        return _fallback_inspect(dataset, token)

    splits_info = splits_data.get("splits", [])
    if not splits_info:
        lines.append("### Status: No splits found")
        return "\n".join(lines)

    lines.append("### Status: ✓ Valid")
    lines.append("")

    # Group by config
    configs: dict[str, list] = {}
    for s in splits_info:
        c = s.get("config", "default")
        configs.setdefault(c, []).append(s)

    # Auto-detect config and split if not specified
    use_config = config or list(configs.keys())[0]
    if split:
        use_split = split
    else:
        config_splits = configs.get(use_config, splits_info)
        use_split = config_splits[0].get("split", "train") if config_splits else "train"

    # Fetch info (has row counts + schema)
    info_data = fetch_info(dataset, use_config, token)

    # Row counts from /info → dataset_info.splits.{name}.num_examples
    split_row_counts: dict[str, int] = {}
    if info_data and "dataset_info" in info_data:
        info_splits = info_data["dataset_info"].get("splits", {})
        for sname, sdata in info_splits.items():
            if isinstance(sdata, dict):
                split_row_counts[sname] = sdata.get("num_examples", 0)

    lines.append("### Configs & Splits")
    for c, slist in configs.items():
        split_strs = []
        for s in slist:
            sname = s["split"]
            rows = split_row_counts.get(sname)
            row_str = f"{rows:,} rows" if rows else "? rows"
            split_strs.append(f"{sname} ({row_str})")
        lines.append(f"- **{c}**: {', '.join(split_strs)}")
    lines.append("")

    if info_data and "dataset_info" in info_data:
        dinfo = info_data["dataset_info"]
        features = dinfo.get("features", {})
        if features:
            lines.append(f"### Schema ({use_config}/{use_split})")
            lines.append("| Column | Type |")
            lines.append("|--------|------|")
            for col_name, col_info in features.items():
                dtype = col_info.get("dtype", col_info.get("_type", "unknown"))
                lines.append(f"| {col_name} | {dtype} |")
            lines.append("")

    # Sample rows
    rows_data = fetch_first_rows(dataset, use_config, use_split, token)
    if rows_data and "rows" in rows_data:
        rows = rows_data["rows"][:sample_rows]
        if rows:
            columns = list(rows[0].get("row", {}).keys())
            lines.append(f"### Sample Rows ({len(rows)})")
            lines.append("| " + " | ".join(columns) + " |")
            lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
            for r in rows:
                vals = []
                for c in columns:
                    v = str(r.get("row", {}).get(c, ""))
                    if len(v) > 60:
                        v = v[:57] + "..."
                    vals.append(v)
                lines.append("| " + " | ".join(vals) + " |")
            lines.append("")

    # Parquet files
    parquet_data = fetch_parquet_files(dataset, token)
    if parquet_data and "parquet_files" in parquet_data:
        files = parquet_data["parquet_files"]
        if files:
            lines.append("### Files")
            lines.append("| File | Size |")
            lines.append("|------|------|")
            total_size = 0
            for f in files[:20]:
                fname = f.get("filename", "unknown")
                size = f.get("size", 0)
                total_size += size
                lines.append(f"| {fname} | {format_size(size)} |")
            if len(files) > 20:
                lines.append(f"| ... and {len(files) - 20} more | |")
            lines.append(f"\n**Total:** {len(files)} files, {format_size(total_size)}")

    return "\n".join(lines)


def _fallback_inspect(dataset: str, token: str | None) -> str:
    """Fallback: use HfApi.list_repo_tree when Datasets Server unavailable."""
    try:
        from huggingface_hub import HfApi
        from huggingface_hub.errors import (
            GatedRepoError, RepositoryNotFoundError,
        )
    except ImportError:
        return f"ERROR: Datasets Server unavailable and huggingface_hub not installed."

    api = HfApi(token=token)
    lines = [f"## Dataset: {dataset}", "",
             "### Status: Datasets Server unavailable — using repo file listing", ""]

    try:
        lines.append("### Files")
        lines.append("| File | Size |")
        lines.append("|------|------|")
        total = 0
        for entry in api.list_repo_tree(dataset, repo_type="dataset", recursive=True):
            if hasattr(entry, "size") and entry.size is not None:
                lines.append(f"| {entry.rfilename} | {format_size(entry.size)} |")
                total += entry.size
        lines.append(f"\n**Total size:** {format_size(total)}")
    except GatedRepoError:
        return (f"ERROR: Dataset '{dataset}' is gated. "
                f"Request access at https://huggingface.co/datasets/{dataset}")
    except RepositoryNotFoundError:
        return f"ERROR: Dataset '{dataset}' not found or token lacks access."

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Inspect a HuggingFace dataset remotely (no download)")
    parser.add_argument("--dataset", required=True, help="Dataset ID (org/name)")
    parser.add_argument("--config", default=None, help="Dataset config (default: auto-detect)")
    parser.add_argument("--split", default=None, help="Split name (default: auto-detect)")
    parser.add_argument("--sample-rows", type=int, default=3, help="Number of sample rows")
    parser.add_argument("--token-env", default="HF_TOKEN", help="Env var for HF token")
    args = parser.parse_args()

    token = resolve_hf_token(args.token_env)
    report = inspect_dataset(
        dataset=args.dataset,
        config=args.config,
        split=args.split,
        sample_rows=args.sample_rows,
        token=token,
    )
    print(report)


if __name__ == "__main__":
    main()
