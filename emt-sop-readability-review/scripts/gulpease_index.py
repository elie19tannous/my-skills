#!/usr/bin/env python3
"""Calculate Gulpease Index for Italian text."""

from __future__ import annotations

import argparse

from readability_common import basic_metrics, read_input


def analyze_text(text: str) -> dict[str, float]:
    metrics = basic_metrics(text)
    score = 89 + (((300 * metrics["sentences"]) - (10 * metrics["letters"])) / metrics["words"])
    return {**metrics, "gulpease_index": score}


def interpretation(score: float) -> str:
    if score < 40:
        return "difficult for high-school readers"
    if score < 60:
        return "difficult for lower-secondary readers"
    if score < 80:
        return "difficult for elementary readers"
    return "easy for elementary readers"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Gulpease Index for Italian text.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    score = metrics["gulpease_index"]
    print(f"Gulpease Index: {score:.2f}")
    print(f"Interpretation: {interpretation(score)}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Letters: {int(metrics['letters'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

