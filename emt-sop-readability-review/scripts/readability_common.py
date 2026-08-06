#!/usr/bin/env python3
"""Shared text metrics for readability scripts."""

from __future__ import annotations

import re
import sys
from pathlib import Path


WORD_RE = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)?", re.UNICODE)
SENTENCE_RE = re.compile(r"[.!?]+(?:\s+|$)")

VOWELS = {
    "a",
    "e",
    "i",
    "o",
    "u",
    "y",
    "á",
    "à",
    "â",
    "ä",
    "ã",
    "å",
    "ą",
    "æ",
    "é",
    "è",
    "ê",
    "ë",
    "ę",
    "í",
    "ì",
    "î",
    "ï",
    "ó",
    "ò",
    "ô",
    "ö",
    "õ",
    "ø",
    "ú",
    "ù",
    "û",
    "ü",
    "ý",
    "ÿ",
}


def read_input(path: str | None, text: str | None) -> str:
    if text is not None:
        return text
    if path:
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()


def count_sentences(text: str) -> int:
    count = len(SENTENCE_RE.findall(text))
    return max(count, 1) if text.strip() else 0


def words(text: str) -> list[str]:
    return WORD_RE.findall(text)


def count_letters(word: str) -> int:
    return sum(1 for char in word if char.isalpha())


def count_syllables(word: str) -> int:
    clean = "".join(char.lower() for char in word if char.isalpha())
    if not clean:
        return 0

    count = 0
    previous_was_vowel = False
    for char in clean:
        is_vowel = char in VOWELS
        if is_vowel and not previous_was_vowel:
            count += 1
        previous_was_vowel = is_vowel

    return max(count, 1)


def basic_metrics(text: str) -> dict[str, float]:
    word_list = words(text)
    sentence_count = count_sentences(text)
    word_count = len(word_list)
    syllable_count = sum(count_syllables(word) for word in word_list)
    letter_count = sum(count_letters(word) for word in word_list)

    if sentence_count == 0 or word_count == 0:
        raise ValueError("Text must contain at least one sentence and one word.")

    return {
        "sentences": sentence_count,
        "words": word_count,
        "syllables": syllable_count,
        "letters": letter_count,
        "asl": word_count / sentence_count,
        "asw": syllable_count / word_count,
    }


def percentage(part: int, total: int) -> float:
    if total == 0:
        return 0.0
    return (part / total) * 100

