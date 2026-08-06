#!/usr/bin/env python3
"""Calculate Flesch-Szigriszt Indice de Perspicuidad for Spanish text."""

from __future__ import annotations

import argparse

from readability_common import basic_metrics, read_input


def analyze_text(text: str) -> dict[str, float]:
    metrics = basic_metrics(text)
    score = 206.835 - (62.3 * metrics["asw"]) - metrics["asl"]
    return {**metrics, "flesch_szigriszt": score}


def interpretation(score: float) -> str:
    if score < 40:
        return "very difficult"
    if score < 55:
        return "difficult"
    if score < 65:
        return "normal"
    if score <= 80:
        return "easy"
    return "very easy"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Flesch-Szigriszt for Spanish text.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    score = metrics["flesch_szigriszt"]
    print(f"Flesch-Szigriszt Indice de Perspicuidad: {score:.2f}")
    print(f"Interpretation: {interpretation(score)}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Syllables: {int(metrics['syllables'])}")
    print(f"Average Sentence Length: {metrics['asl']:.2f}")
    print(f"Average Syllables per Word: {metrics['asw']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

