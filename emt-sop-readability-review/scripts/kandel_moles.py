#!/usr/bin/env python3
"""Calculate Kandel-Moles readability score for French text."""

from __future__ import annotations

import argparse

from readability_common import basic_metrics, read_input


def analyze_text(text: str) -> dict[str, float]:
    metrics = basic_metrics(text)
    score = 207 - (1.015 * metrics["asl"]) - (73.6 * metrics["asw"])
    return {**metrics, "kandel_moles": score}


def interpretation(score: float) -> str:
    if score >= 90:
        return "very easy"
    if score >= 70:
        return "easy"
    if score >= 60:
        return "standard"
    if score >= 50:
        return "fairly difficult"
    if score >= 30:
        return "difficult"
    return "very difficult"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Kandel-Moles score for French text.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    score = metrics["kandel_moles"]
    print(f"Kandel-Moles score: {score:.2f}")
    print(f"Interpretation: {interpretation(score)}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Syllables: {int(metrics['syllables'])}")
    print(f"Average Sentence Length: {metrics['asl']:.2f}")
    print(f"Average Syllables per Word: {metrics['asw']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

