"""Recommend segmenter + integration pattern for a target language.

Phase 1 cached snapshot 2026-04-23.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

def _linguistic_shared_dir() -> str:
    for _p in Path(__file__).resolve().parents:
        _c = _p / "_linguistic_shared"
        if _c.is_dir():
            return str(_c)
    raise RuntimeError("_linguistic_shared bundle not found — run scripts/sync-linguistic-shared.py")
sys.path.insert(0, _linguistic_shared_dir())
from lang_codes import resolve_language  # noqa: E402

# Per-family segmenter recommendations.
_FAMILY_REC: dict[str, dict] = {
    "agglutinative-Turkic": {
        "primary": "SIGMORPHON 2023 winner (Turkic submodel) or TRMorph for Turkish",
        "fallback": "Morfessor 2.0",
        "integration": "pre-tokenize → BPE; vocab extension recommended for class 1-2 Turkic",
    },
    "agglutinative-Uralic": {
        "primary": "HFST-fin (Omorfi) for Finnish; Apertium for others",
        "fallback": "Morfessor 2.0",
        "integration": "FST when available; Morfessor for OOV",
    },
    "agglutinative-Bantu": {
        "primary": "SIGMORPHON 2023 (Bantu submodel); UniMorph if available",
        "fallback": "Morfessor 2.0",
        "integration": "noun-class-aware tokenizer prep",
    },
    "agglutinative-Koreanic": {
        "primary": "KOMA / KKMA",
        "fallback": "stanza-kor",
        "integration": "syllable-aware; jamo-level optional",
    },
    "agglutinative-Dravidian": {
        "primary": "Apertium for Tamil; stanza for others",
        "fallback": "Morfessor",
        "integration": "agglutinative tokenizer prep",
    },
    "agglutinative-Quechuan": {
        "primary": "Apertium-quz",
        "fallback": "Morfessor + community paradigms",
        "integration": "FST + segmenter; community partnership for paradigm refinement",
    },
    "agglutinative-Austronesian": {
        "primary": "Apertium-mri (Maori)",
        "fallback": "Morfessor",
        "integration": "reduplication-aware filter recommended",
    },
    "agglutinative-Uralic-Sami": {
        "primary": "HFST-sme (UiT-built)",
        "fallback": "Apertium-sme",
        "integration": "FST integration; community + UiT partnership",
    },
    "templatic-Semitic": {
        "primary": "Farasa / MADAMIRA (Arabic); HornMorpho (Amharic); YAP (Hebrew)",
        "fallback": "do NOT use concatenative",
        "integration": "root-pattern preprocessing BEFORE BPE; vocab includes root + pattern markers",
    },
    "fusional-Iranian": {
        "primary": "HFST-fas",
        "fallback": "stanza-fas",
        "integration": "moderate; Persian Latin script transliteration aware",
    },
    "fusional-Slavic": {
        "primary": "stanza or HFST",
        "fallback": "Morfessor",
        "integration": "case-aware tokenizer prep",
    },
    "fusional-Romance": {
        "primary": "stanza",
        "fallback": "spaCy",
        "integration": "minimal — BPE handles fusional Romance",
    },
    "fusional-Germanic": {
        "primary": "stanza or HFST",
        "fallback": "spaCy",
        "integration": "minimal for English; compounds for German",
    },
    "fusional-Indic": {
        "primary": "stanza-hin / IndicNLP",
        "fallback": "Morfessor",
        "integration": "Devanagari + Latin transliteration coverage",
    },
    "fusional-low": {
        "primary": "stanza or spaCy (English baseline)",
        "fallback": "BPE",
        "integration": "BPE sufficient",
    },
    "polysynthetic-Eskimo": {
        "primary": "HFST-iku / HFST-kal",
        "fallback": "SIGMORPHON 2023 + community paradigms",
        "integration": "MANDATORY morpheme segmentation BEFORE BPE; vocab extension critical",
    },
    "polysynthetic-Athabaskan": {
        "primary": "research-grade FSTs (limited); SIGMORPHON 2023",
        "fallback": "community-collected paradigms; tokenizer-only is insufficient",
        "integration": "MANDATORY segmentation; community partnership needed",
    },
    "polysynthetic-Iroquoian": {
        "primary": "partial community-built FST (Cherokee)",
        "fallback": "SIGMORPHON 2023; manual paradigm collection",
        "integration": "MANDATORY; community partnership essential",
    },
    "isolating": {
        "primary": "tokenizer with byte fallback (BPE/SentencePiece)",
        "fallback": "n/a",
        "integration": "morpheme segmentation rarely useful for isolating languages",
    },
    "isolating-tone": {
        "primary": "tokenizer with byte fallback + diacritic preservation",
        "fallback": "n/a",
        "integration": "tone marks are semantic — preserve via magic-linguistic-scripts",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend segmenter + integration pattern.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Pull the type from paradigm_lookup's coverage
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from paradigm_lookup import _COVERAGE  # noqa: E402

    cov = _COVERAGE.get(rec.iso639_3)
    if cov is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": "No cached morphology data; consult magic-linguistic-morph references for general recipes.",
                },
                indent=2,
            )
        )
        return 4

    family_type = cov.get("type", "")
    family_rec = _FAMILY_REC.get(
        family_type,
        {
            "primary": "Morfessor 2.0 (general fallback)",
            "fallback": "BPE alone",
            "integration": "default",
        },
    )

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "morphology_type": family_type,
        "morphology_tier": cov.get("tier"),
        "segmenter_recommendation": family_rec,
        "anti_patterns": [
            "DO NOT use concatenative segmenter for templatic Semitic languages",
            "DO NOT skip morpheme segmentation for polysynthetic targets",
            "DO NOT generate paradigm-completed forms without `<morph_aug>` tag",
        ],
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
