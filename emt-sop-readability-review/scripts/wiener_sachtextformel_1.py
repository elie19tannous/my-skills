#!/usr/bin/env python3
"""Calculate Wiener Sachtextformel 1 for German text."""

from __future__ import annotations

import argparse

from readability_common import basic_metrics, count_letters, count_syllables, percentage, read_input, words


def analyze_text(text: str) -> dict[str, float]:
    metrics = basic_metrics(text)
    word_list = words(text)
    word_count = int(metrics["words"])
    syllable_counts = [count_syllables(word) for word in word_list]

    ms = percentage(sum(1 for count in syllable_counts if count >= 3), word_count)
    sl = metrics["asl"]
    iw = percentage(sum(1 for word in word_list if count_letters(word) > 6), word_count)
    es = percentage(sum(1 for count in syllable_counts if count == 1), word_count)
    score = (0.1935 * ms) + (0.1672 * sl) + (0.1297 * iw) - (0.0327 * es) - 0.875

    return {
        **metrics,
        "wiener_sachtextformel_1": score,
        "ms": ms,
        "sl": sl,
        "iw": iw,
        "es": es,
    }


def interpretation(score: float) -> str:
    if score <= 5:
        return "very easy"
    if score <= 7:
        return "easy"
    if score <= 10:
        return "average"
    if score <= 12:
        return "difficult"
    return "very difficult"


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Wiener Sachtextformel 1 for German text.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}")
        return 1

    score = metrics["wiener_sachtextformel_1"]
    print(f"Wiener Sachtextformel 1: {score:.2f}")
    print(f"Interpretation: {interpretation(score)}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Syllables: {int(metrics['syllables'])}")
    print(f"Letters: {int(metrics['letters'])}")
    print(f"MS words with 3+ syllables (%): {metrics['ms']:.2f}")
    print(f"SL average sentence length: {metrics['sl']:.2f}")
    print(f"IW words longer than 6 letters (%): {metrics['iw']:.2f}")
    print(f"ES one-syllable words (%): {metrics['es']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

