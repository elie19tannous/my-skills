#!/usr/bin/env python3
"""Calculate Jasnopis readability class for Polish text."""

from __future__ import annotations

import argparse

from readability_common import basic_metrics, count_syllables, percentage, read_input, words


def analyze_text(text: str) -> dict[str, float]:
    metrics = basic_metrics(text)
    word_list = words(text)
    word_count = int(metrics["words"])
    phw = percentage(sum(1 for word in word_list if count_syllables(word) >= 4), word_count)
    score = -0.01413 + (0.0857 * metrics["asl"]) + (0.2949 * phw)
    rounded_class = min(max(round(score), 1), 7)
    return {**metrics, "jasnopis_score": score, "jasnopis_class": rounded_class, "phw": phw}


def interpretation(readability_class: float) -> str:
    labels = {
        1: "primary grades 1-3",
        2: "primary grades 4-6",
        3: "lower secondary",
        4: "high school",
        5: "undergraduate",
        6: "graduate",
        7: "expert",
    }
    return labels.get(int(readability_class), "outside class scale")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Jasnopis readability class for Polish text.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    readability_class = metrics["jasnopis_class"]
    print(f"Jasnopis readability score: {metrics['jasnopis_score']:.2f}")
    print(f"Jasnopis readability class: {int(readability_class)}")
    print(f"Interpretation: {interpretation(readability_class)}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Syllables: {int(metrics['syllables'])}")
    print(f"Average Sentence Length: {metrics['asl']:.2f}")
    print(f"Polish hard words with 4+ syllables (%): {metrics['phw']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

