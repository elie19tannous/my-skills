#!/usr/bin/env python3
"""
List git version ranges for changelog generation.

Given a git repository, outputs tag-to-tag ranges (plus Unreleased) with commit
counts. Used by the make-changelog skill to plan which version sections to generate.

Usage:
  list_ranges.py [repo-path] [--since-tag TAG] [--output text|json]

Exit codes:
  0  success
  1  usage error
  2  runtime error (not a git repo, no commits, or --since-tag not found)

Examples:
  list_ranges.py                                  # all ranges in current directory
  list_ranges.py /path/to/repo --output json      # structured output for skill
  list_ranges.py --since-tag v1.2.0 --output json # fill mode: only newer ranges
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import date


def git(args: list[str], cwd: str) -> tuple[str, int]:
    result = subprocess.run(
        ["git"] + args, capture_output=True, text=True, cwd=cwd
    )
    return result.stdout.strip(), result.returncode


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "repo_path", nargs="?", default=".",
        help="Path to git repository (default: current directory)",
    )
    parser.add_argument(
        "--since-tag", metavar="TAG",
        help="Only include ranges newer than this tag (fill mode)",
    )
    parser.add_argument(
        "--output", choices=["text", "json"], default="text",
        help="Output format (default: text)",
    )
    args = parser.parse_args()

    repo = os.path.abspath(args.repo_path)

    # Validate: must be a git repo
    _, rc = git(["rev-parse", "--git-dir"], repo)
    if rc != 0:
        print(f"Error: {repo} is not a git repository", file=sys.stderr)
        sys.exit(2)

    # Validate: must have at least one commit
    count_out, rc = git(["rev-list", "--count", "HEAD"], repo)
    if rc != 0 or not count_out.isdigit() or int(count_out) == 0:
        print("Error: repository has no commits", file=sys.stderr)
        sys.exit(2)

    # Collect all tags, oldest to newest
    tags_out, _ = git(
        ["tag", "--sort=version:refname",
         "--format=%(refname:short)\t%(creatordate:short)"],
        repo,
    )
    all_tags: list[dict] = []
    if tags_out:
        for line in tags_out.splitlines():
            parts = line.split("\t", 1)
            if len(parts) == 2 and parts[0]:
                all_tags.append({"tag": parts[0], "date": parts[1]})

    # Apply --since-tag: drop tags up to and including the anchor
    if args.since_tag:
        tag_names = [t["tag"] for t in all_tags]
        if args.since_tag not in tag_names:
            print(
                f"Error: --since-tag '{args.since_tag}' not found in repository tags",
                file=sys.stderr,
            )
            sys.exit(2)
        idx = tag_names.index(args.since_tag)
        all_tags = all_tags[idx + 1:]

    # Build one range per tag (oldest-to-newest order, reversed at end)
    ranges: list[dict] = []
    for i, tag_info in enumerate(all_tags):
        from_ref = all_tags[i - 1]["tag"] if i > 0 else ""
        to_ref = tag_info["tag"]

        if from_ref:
            count_cmd = ["rev-list", "--count", f"{from_ref}..{to_ref}"]
        else:
            count_cmd = ["rev-list", "--count", to_ref]

        c_out, _ = git(count_cmd, repo)
        commit_count = int(c_out) if c_out.isdigit() else 0

        ranges.append({
            "label": tag_info["tag"].lstrip("v"),
            "from_ref": from_ref,
            "to_ref": to_ref,
            "date": tag_info["date"],
            "commit_count": commit_count,
        })

    # Unreleased section (commits after latest tag, or all commits if no tags)
    if all_tags:
        latest_tag = all_tags[-1]["tag"]
        u_out, _ = git(["rev-list", "--count", f"{latest_tag}..HEAD"], repo)
        unreleased_count = int(u_out) if u_out.isdigit() else 0
        if unreleased_count > 0:
            ranges.append({
                "label": "Unreleased",
                "from_ref": latest_tag,
                "to_ref": "HEAD",
                "date": str(date.today()),
                "commit_count": unreleased_count,
            })
    else:
        total_out, _ = git(["rev-list", "--count", "HEAD"], repo)
        total = int(total_out) if total_out.isdigit() else 0
        ranges.append({
            "label": "Unreleased",
            "from_ref": "",
            "to_ref": "HEAD",
            "date": str(date.today()),
            "commit_count": total,
        })

    # Reverse to newest-first (standard changelog order)
    ranges = list(reversed(ranges))

    if args.output == "json":
        print(json.dumps(ranges, indent=2))
    else:
        for r in ranges:
            from_display = r["from_ref"] or "(initial)"
            print(
                f"[{r['label']}]  {r['date']}  "
                f"{from_display}..{r['to_ref']}  "
                f"({r['commit_count']} commits)"
            )

    sys.exit(0)


if __name__ == "__main__":
    main()
