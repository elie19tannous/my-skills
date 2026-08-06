#!/usr/bin/env python3
# CALLABLE TOOL — Call directly via CLI. No custom mode needed.
"""Deliver a local data folder to HuggingFace Hub dataset repository.

Callable tool — agents run this directly via CLI. Built-in PAUSE gate.

Usage:
    python3 deliver_to_hf.py --input data/output/ --repo org/name --private
    python3 deliver_to_hf.py --input data/output/ --repo org/name --public --yes
    python3 deliver_to_hf.py --input data/output/ --repo org/name --create-pr
    python3 deliver_to_hf.py --input data/output/ --repo org/name --incremental
"""
from __future__ import annotations

import argparse
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

CREDENTIAL_PATTERNS = [
    re.compile(r"hf_[A-Za-z0-9]{20,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"sk-ant-[A-Za-z0-9-]{20,}"),
    re.compile(r"Bearer\s+\S{20,}"),
    re.compile(r"://\w+:\w+@"),
]


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


def scan_input_folder(folder: Path) -> tuple[list[Path], int]:
    """Scan folder for uploadable files. Returns (files, total_size)."""
    files = [f for f in sorted(folder.rglob("*"))
             if f.is_file() and not f.name.startswith(".")]
    total_size = sum(f.stat().st_size for f in files)
    return files, total_size


def check_credentials_in_files(files: list[Path]) -> list[str]:
    """Scan text files for credential patterns. Returns warnings."""
    warnings = []
    text_exts = {".md", ".txt", ".csv", ".json", ".jsonl", ".yaml", ".yml"}
    for f in files:
        if f.suffix not in text_exts:
            continue
        try:
            content = f.read_text(errors="replace")
            for pattern in CREDENTIAL_PATTERNS:
                if pattern.search(content):
                    warnings.append(f"WARNING: Possible credential in {f.name}")
                    break
        except Exception:
            pass
    return warnings


def upload_with_retry(fn, max_retries: int = 3):
    """Execute fn with exponential backoff on 429/503."""
    for attempt in range(max_retries + 1):
        try:
            return fn()
        except Exception as e:
            status = getattr(getattr(e, "response", None), "status_code", None)
            if status in (429, 503) and attempt < max_retries:
                wait = 2 ** attempt
                print(f"  Retrying in {wait}s (HTTP {status})...")
                time.sleep(wait)
                continue
            raise


def deliver_batch(
    api, folder: Path, repo_id: str, commit_message: str, create_pr: bool,
) -> str:
    """Batch upload via upload_folder (atomic commit)."""
    def do_upload():
        return api.upload_folder(
            folder_path=str(folder),
            repo_id=repo_id,
            repo_type="dataset",
            commit_message=commit_message,
            create_pr=create_pr,
        )

    result = upload_with_retry(do_upload)
    if hasattr(result, "commit_url"):
        return result.commit_url
    return f"https://huggingface.co/datasets/{repo_id}"


def deliver_incremental(
    api, files: list[Path], folder: Path, repo_id: str,
    commit_message: str, create_pr: bool,
) -> str:
    """Incremental upload via upload_file per file."""
    for f in files:
        rel_path = str(f.relative_to(folder))
        print(f"  Uploading {rel_path}...")

        def do_upload(path=str(f), repo_path=rel_path):
            return api.upload_file(
                path_or_fileobj=path,
                path_in_repo=repo_path,
                repo_id=repo_id,
                repo_type="dataset",
                commit_message=f"{commit_message}: {repo_path}",
                create_pr=create_pr,
            )

        upload_with_retry(do_upload)

    return f"https://huggingface.co/datasets/{repo_id}"


def deliver(
    input_folder: str | Path,
    repo: str,
    private: bool = True,
    gated: bool = False,
    create_pr: bool = False,
    incremental: bool = False,
    commit_message: str = "MAGIC delivery",
    auto_yes: bool = False,
    token: str | None = None,
) -> str:
    """Upload local folder to HF Hub. Returns URL."""
    from huggingface_hub import HfApi

    folder = Path(input_folder)
    if not folder.is_dir():
        print(f"ERROR: Input folder not found: {folder}", file=sys.stderr)
        sys.exit(1)

    api = HfApi(token=token)
    files, total_size = scan_input_folder(folder)
    if not files:
        print(f"ERROR: No files found in {folder}", file=sys.stderr)
        sys.exit(1)

    visibility = "gated" if gated else ("public" if not private else "private")
    mode = "incremental" if incremental else "batch (atomic commit)"

    # Print plan
    print("## Delivering to HuggingFace Hub")
    print()
    print("### Plan")
    print(f"- Source: {folder} ({len(files)} files, {format_size(total_size)})")
    print(f"- Destination: {repo} (dataset repo)")
    print(f"- Visibility: {visibility}")
    print(f"- Mode: {mode}")
    if create_pr:
        print("- Strategy: Pull request (draft)")
    print()

    # Check for credentials
    cred_warnings = check_credentials_in_files(files)
    for w in cred_warnings:
        print(f"  ⚠ {w}")
    if cred_warnings:
        print()

    # PAUSE gate
    if not auto_yes:
        answer = input(f"Upload {len(files)} files ({format_size(total_size)}) to {repo}? [y/N]: ")
        if answer.strip().lower() not in ("y", "yes"):
            print("Aborted.")
            sys.exit(0)

    # Create repo
    print("### Progress")
    print(f"  Creating repo {repo}...")
    api.create_repo(
        repo_id=repo,
        repo_type="dataset",
        private=private,
        exist_ok=True,
    )

    # Upload
    if incremental:
        url = deliver_incremental(
            api, files, folder, repo, commit_message, create_pr)
    else:
        print(f"  Uploading {len(files)} files...")
        url = deliver_batch(api, folder, repo, commit_message, create_pr)

    print()
    print("### Result")
    print(f"✓ Uploaded to {url}")
    print(f"  Files: {len(files)}")
    print(f"  Size: {format_size(total_size)}")

    return url


def main():
    parser = argparse.ArgumentParser(
        description="Upload local data folder to HuggingFace Hub")
    parser.add_argument("--input", required=True,
                        help="Local folder to upload")
    parser.add_argument("--repo", required=True,
                        help="HuggingFace repo ID (org/name)")

    vis_group = parser.add_mutually_exclusive_group()
    vis_group.add_argument("--private", action="store_true", default=True,
                           help="Private repo (default)")
    vis_group.add_argument("--public", action="store_true",
                           help="Public repo")
    vis_group.add_argument("--gated", action="store_true",
                           help="Gated repo (requires access approval)")

    parser.add_argument("--create-pr", action="store_true",
                        help="Create draft PR instead of direct push")
    parser.add_argument("--incremental", action="store_true",
                        help="Upload file-by-file instead of atomic folder")
    parser.add_argument("--commit-message", default="MAGIC delivery",
                        help="Commit message")
    parser.add_argument("--yes", action="store_true",
                        help="Skip confirmation prompt")
    parser.add_argument("--token-env", default="HF_TOKEN",
                        help="Env var for HF token")
    args = parser.parse_args()

    token = resolve_hf_token(args.token_env)
    if not token:
        print("ERROR: No HF token found.", file=sys.stderr)
        print("  Set HF_TOKEN env var or run `huggingface-cli login`",
              file=sys.stderr)
        sys.exit(1)

    is_private = not args.public and not args.gated

    deliver(
        input_folder=args.input,
        repo=args.repo,
        private=is_private,
        gated=args.gated,
        create_pr=args.create_pr,
        incremental=args.incremental,
        commit_message=args.commit_message,
        auto_yes=args.yes,
        token=token,
    )


if __name__ == "__main__":
    main()
