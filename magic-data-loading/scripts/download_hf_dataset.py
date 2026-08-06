#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""Download a HuggingFace dataset to a local directory.

Callable tool — agents run this directly via CLI.

Usage:
    python3 download_hf_dataset.py --dataset stanfordnlp/imdb --output data/input/hf/
    python3 download_hf_dataset.py --dataset org/name --patterns "*.parquet" --revision v1.0
    python3 download_hf_dataset.py --dataset org/private --token-env MY_TOKEN
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Optional


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


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def download_dataset(
    dataset: str,
    output: str | Path,
    patterns: list[str] | None = None,
    revision: str = "main",
    token: str | None = None,
) -> Path:
    """Download HF dataset repo to local directory. Returns local path."""
    from huggingface_hub import snapshot_download
    from huggingface_hub.errors import GatedRepoError, RepositoryNotFoundError

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)

    kwargs: dict = dict(
        repo_id=dataset,
        repo_type="dataset",
        revision=revision,
        local_dir=str(output),
        token=token,
    )
    if patterns:
        kwargs["allow_patterns"] = patterns

    try:
        path = snapshot_download(**kwargs)
    except GatedRepoError:
        print(f"ERROR: Dataset '{dataset}' is gated.", file=sys.stderr)
        print(f"  Request access at: https://huggingface.co/datasets/{dataset}",
              file=sys.stderr)
        sys.exit(1)
    except RepositoryNotFoundError:
        print(f"ERROR: Dataset '{dataset}' not found or token lacks access.",
              file=sys.stderr)
        sys.exit(1)

    return Path(path)


def scan_downloaded_files(local_path: Path) -> list[dict]:
    """Scan downloaded files: count rows for parquet/csv, get sizes."""
    files = []
    for f in sorted(local_path.rglob("*")):
        if f.is_dir() or f.name.startswith("."):
            continue
        info: dict = {
            "path": str(f.relative_to(local_path)),
            "size": f.stat().st_size,
            "rows": None,
        }
        try:
            if f.suffix == ".parquet":
                import pandas as pd
                df = pd.read_parquet(f)
                info["rows"] = len(df)
                info["columns"] = list(df.columns)
                info["dtypes"] = {c: str(df[c].dtype) for c in df.columns}
            elif f.suffix == ".csv":
                import pandas as pd
                df = pd.read_csv(f, nrows=0)
                info["columns"] = list(df.columns)
                row_count = sum(1 for _ in open(f)) - 1
                info["rows"] = max(0, row_count)
        except Exception:
            pass
        files.append(info)
    return files


def format_report(dataset: str, output: Path, files: list[dict]) -> str:
    """Format download report as markdown."""
    lines = [f"## Downloaded: {dataset} → {output}", ""]

    data_files = [f for f in files if f["rows"] is not None]
    other_files = [f for f in files if f["rows"] is None]

    if data_files:
        lines.append(f"### Data Files ({len(data_files)})")
        lines.append("| File | Size | Rows |")
        lines.append("|------|------|------|")
        for f in data_files:
            lines.append(
                f"| {f['path']} | {format_size(f['size'])} | {f['rows']:,} |")
        lines.append("")

    if other_files:
        lines.append(f"### Other Files ({len(other_files)})")
        lines.append("| File | Size |")
        lines.append("|------|------|")
        for f in other_files:
            lines.append(f"| {f['path']} | {format_size(f['size'])} |")
        lines.append("")

    total_size = sum(f["size"] for f in files)
    total_rows = sum(f["rows"] for f in files if f["rows"] is not None)
    lines.append("### Summary")
    lines.append(f"- **Total:** {len(files)} files, {format_size(total_size)}")
    if total_rows:
        lines.append(f"- **Rows:** {total_rows:,}")

    # Show schema from first data file
    if data_files and "columns" in data_files[0]:
        cols = data_files[0]["columns"]
        dtypes = data_files[0].get("dtypes", {})
        lines.append(f"- **Columns:** {', '.join(cols)}")
        if dtypes:
            dtype_strs = [f"{c} ({dtypes[c]})" for c in cols[:10]]
            lines.append(f"- **Schema:** {', '.join(dtype_strs)}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Download a HuggingFace dataset to local directory")
    parser.add_argument("--dataset", required=True, help="Dataset ID (org/name)")
    parser.add_argument("--output", default="data/input/hf/",
                        help="Local output directory")
    parser.add_argument("--patterns", nargs="*",
                        help="File patterns to download (e.g., '*.parquet')")
    parser.add_argument("--revision", default="main", help="Branch/tag/commit")
    parser.add_argument("--token-env", default="HF_TOKEN",
                        help="Env var for HF token")
    args = parser.parse_args()

    token = resolve_hf_token(args.token_env)
    local_path = download_dataset(
        dataset=args.dataset,
        output=args.output,
        patterns=args.patterns,
        revision=args.revision,
        token=token,
    )
    files = scan_downloaded_files(local_path)
    report = format_report(args.dataset, local_path, files)
    print(report)


if __name__ == "__main__":
    main()
