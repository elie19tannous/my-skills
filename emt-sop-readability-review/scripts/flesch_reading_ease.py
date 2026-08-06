#!/usr/bin/env python3
"""Calculate Flesch Reading Ease for plain text or a text file."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


WORD_RE = re.compile(r"[A-Za-z]+(?:['-][A-Za-z]+)?")
SENTENCE_RE = re.compile(r"[.!?]+(?:\s+|$)")
VOWEL_GROUP_RE = re.compile(r"[aeiouy]+", re.IGNORECASE)


def count_sentences(text: str) -> int:
    count = len(SENTENCE_RE.findall(text))
    return max(count, 1) if text.strip() else 0


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def count_syllables(word: str) -> int:
    clean = re.sub(r"[^A-Za-z]", "", word).lower()
    if not clean:
        return 0

    groups = VOWEL_GROUP_RE.findall(clean)
    count = len(groups)

    if clean.endswith("e") and not clean.endswith(("le", "ye")) and count > 1:
        count -= 1

    return max(count, 1)


def analyze_text(text: str) -> dict[str, float]:
    word_list = words(text)
    sentence_count = count_sentences(text)
    word_count = len(word_list)
    syllable_count = sum(count_syllables(word) for word in word_list)

    if sentence_count == 0 or word_count == 0:
        raise ValueError("Text must contain at least one sentence and one word.")

    asl = word_count / sentence_count
    asw = syllable_count / word_count
    score = 206.835 - (1.015 * asl) - (84.6 * asw)

    return {
        "flesch_reading_ease": score,
        "sentences": sentence_count,
        "words": word_count,
        "syllables": syllable_count,
        "asl": asl,
        "asw": asw,
    }


def read_input(path: str | None, text: str | None) -> str:
    if text is not None:
        return text
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate Flesch Reading Ease.")
    parser.add_argument("path", nargs="?", help="Text or Markdown file to analyze. Reads stdin if omitted.")
    parser.add_argument("--text", help="Text to analyze instead of reading a file.")
    args = parser.parse_args()

    try:
        metrics = analyze_text(read_input(args.path, args.text))
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(f"Flesch Reading Ease: {metrics['flesch_reading_ease']:.2f}")
    print(f"Sentences: {int(metrics['sentences'])}")
    print(f"Words: {int(metrics['words'])}")
    print(f"Syllables: {int(metrics['syllables'])}")
    print(f"Average Sentence Length: {metrics['asl']:.2f}")
    print(f"Average Syllables per Word: {metrics['asw']:.2f}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
