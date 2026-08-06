"""Recommend metric for a (language, task) pair.

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


def is_morphologically_rich(iso: str, family: str) -> bool:
    fam = family.lower()
    if "agglutin" in fam or "polysynth" in fam:
        return True
    if iso in ("tur", "fin", "hun", "kaz", "uzb", "swa", "kin", "kor", "tam", "tel"):
        return True
    if iso in ("iku", "nav", "chr"):
        return True
    if "semitic" in fam or iso in ("arb", "heb", "amh"):
        return True
    return False


def is_tone_language(iso: str) -> bool:
    return iso in {"yor", "ibo", "hau", "twi", "vie", "cmn", "yue", "tha", "lao", "mya"}


def is_space_less(iso: str) -> bool:
    return iso in {"cmn", "yue", "jpn", "khm", "lao", "mya", "tha", "tib"}


def comet_coverage(iso: str) -> str:
    """Approximate per-language COMET coverage."""
    high = {
        "eng",
        "spa",
        "fra",
        "deu",
        "ita",
        "por",
        "rus",
        "cmn",
        "jpn",
        "kor",
        "ara",
        "arb",
        "vie",
        "ind",
        "tha",
        "tur",
        "fin",
        "hin",
        "ben",
        "tam",
    }
    medium = {"yor", "swa", "amh", "khm", "fas", "heb", "ukr", "pol", "ces", "nld", "ron"}
    if iso in high:
        return "high"
    if iso in medium:
        return "medium"
    return "low"


def main() -> int:
    parser = argparse.ArgumentParser(description="Metric advisor for (language, task) pair.")
    parser.add_argument("language", help="Target language name or ISO 639-3")
    parser.add_argument("--task", required=True, choices=["mt", "reading", "ner", "sentiment", "qa", "asr", "tts"])
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    iso = rec.iso639_3
    fam = rec.family
    out = {"language": rec.display, "iso639_3": iso, "task": args.task, "snapshot_date": "2026-04-23"}

    if args.task == "mt":
        morph_rich = is_morphologically_rich(iso, fam)
        comet = comet_coverage(iso)
        if morph_rich and comet == "low":
            out["primary"] = "chrF++"
            out["secondary"] = "GEMBA-MQM (LLM-judge)"
            out["never_primary"] = "BLEU (pathological for MRL)"
            out["rationale"] = "Morphologically-rich + low COMET coverage; chrF++ + GEMBA-MQM is the recommended combo"
        elif morph_rich:
            out["primary"] = "chrF++ + COMET-22"
            out["secondary"] = "spBLEU"
            out["never_primary"] = "BLEU"
            out["rationale"] = "Morphologically-rich; chrF++ robust + COMET available for this language"
        else:
            out["primary"] = "chrF++ + COMET-22"
            out["secondary"] = "spBLEU + BLEU"
            out["rationale"] = "High-resource language family; full metric stack viable"
    elif args.task == "asr":
        out["primary"] = "CER" if is_space_less(iso) else "WER"
        out["secondary"] = "WER" if is_space_less(iso) else "CER"
        out["rationale"] = (
            "Space-less script — CER mandatory"
            if is_space_less(iso)
            else "Space-segmented — WER standard, also report CER"
        )
        if is_tone_language(iso):
            out["warning"] = (
                "Tone language — verify ASR pipeline preserves diacritics; use magic-linguistic-speech IPA validator"
            )
    elif args.task == "tts":
        out["primary"] = "MOS (human panel)"
        out["secondary"] = "PESQ / STOI (signal quality, weak naturalness correlation)"
        out["rationale"] = "TTS quality is fundamentally human-judged; signal-only metrics are supplementary"
    elif args.task == "ner":
        out["primary"] = "F1 (per-tag)"
        out["secondary"] = "exact-match"
        out["rationale"] = "Per-tag F1 mandatory; aggregate hides per-class failures"
    elif args.task == "sentiment":
        out["primary"] = "F1 (per-class)"
        out["secondary"] = "Macro-F1 + accuracy"
        out["rationale"] = "Per-class F1; accuracy alone misleading on imbalanced classes"
    elif args.task == "qa":
        out["primary"] = "F1 + EM"
        out["secondary"] = "per-question-type breakdown"
        out["rationale"] = "F1 + EM standard; stratify by question type"
    elif args.task == "reading":
        out["primary"] = "accuracy"
        out["secondary"] = "per-question breakdown"
        out["rationale"] = "Multi-choice reading comprehension"

    out["per_stratum_breakdown_required"] = ["per-direction (MT)", "per-dialect", "per-register", "per-class"]
    out["anti_patterns"] = [
        "DO NOT use BLEU on morphologically-rich languages",
        "DO NOT report COMET without per-language coverage check",
        "DO NOT use WER on space-less scripts (use CER)",
        "DO NOT report aggregate without per-stratum breakdown",
    ]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
