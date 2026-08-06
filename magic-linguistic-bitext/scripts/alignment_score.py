"""Recommend mining + alignment config for a language pair.

Phase 1 cached recommendations; --measure (live mining/alignment) deferred to Phase 2+.
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


def recommend_embedding(target_iso: str, target_family: str) -> tuple[str, str]:
    """Pick embedding model based on target family."""
    fam = target_family.lower()
    if "bantu" in fam or "atlantic-congo" in fam or "niger-congo" in fam:
        return "SONAR", "LASER3 has coverage gaps on Bantu / Niger-Congo; SONAR is preferred"
    if "americas" in fam or "quechu" in fam or "iroquoian" in fam or "athabask" in fam or "eskimo" in fam:
        return "SONAR", "LASER3 has coverage gaps on Indigenous Americas; SONAR is preferred"
    if "tai-kadai" in fam or "austroasiatic" in fam or "sino-tibetan" in fam:
        return "LASER3", "SEA / CJK well-covered by LASER3"
    return "LASER3", "Default — mature and widely supported"


def recommend_margin(source_class: int | None, target_class: int | None) -> tuple[float, str, int]:
    """Return (margin_threshold, rationale, spot-check N)."""
    s = source_class if source_class is not None else 4
    t = target_class if target_class is not None else 1
    min_class = min(s, t)
    if min_class >= 4:
        return 1.06, "NLLB published 'clean' threshold; both sides well-resourced", 30
    if min_class == 3:
        return 1.05, "Slight relaxation for Class 3", 50
    if min_class == 2:
        return 1.04, "Class 2: avoid over-filtering; manual spot-check 50", 50
    if min_class == 1:
        return 1.04, "Class 1: lower threshold + manual spot-check 100", 100
    return 1.03, "Class 0: aggressive; spot-check 100 + length-ratio mandatory", 100


_NIGER_CONGO_ISO = frozenset({"yor", "twi", "ibo", "hau", "lin", "zul", "xho"})
_NIGER_CONGO_TAGS = frozenset({"niger-congo", "atlantic-congo", "bantu", "kwa", "gur", "mande"})


def _is_niger_congo(target_iso: str, target_family: str) -> bool:
    if target_iso in _NIGER_CONGO_ISO:
        return True
    fam = target_family.lower()
    return any(tag in fam for tag in _NIGER_CONGO_TAGS)


def recommend_length_ratio(target_iso: str, target_family: str) -> tuple[tuple[float, float], str]:
    """Return ((lo, hi), rationale)."""
    fam = target_family.lower()
    if "eskimo" in fam or target_iso in ("nav", "iku", "kal", "chr"):
        return (0.2, 1.5), "Polysynthetic target: shorter than source; tight upper bound"
    if "agglutin" in fam or target_iso in ("tur", "fin", "hun", "kaz", "uzb", "kin"):
        return (0.4, 2.5), "Agglutinative: target may be longer-token / shorter-word"
    if "semitic" in fam or target_iso in ("heb", "arb"):
        return (0.4, 2.0), "Root-pattern; moderate range"
    if _is_niger_congo(target_iso, fam):
        return (0.3, 3.0), "Niger-Congo / Bantu / Kwa: distant from English; widen ratio (per SKILL.md L80)"
    return (0.5, 2.0), "Standard range for typologically-similar pairs"


def main() -> int:
    parser = argparse.ArgumentParser(description="Recommend mining + alignment config for a bitext pair.")
    parser.add_argument("source", help="Source language (typically English)")
    parser.add_argument("target", help="Target language")
    parser.add_argument("--source-class", type=int, default=None, help="Joshi class of source (default: 5)")
    parser.add_argument("--target-class", type=int, default=None, help="Joshi class of target (from magic-linguistic-scope)")
    parser.add_argument("--measure", action="store_true", help="(Phase 2+) actually mine + align")
    args = parser.parse_args()

    if args.measure:
        print("ERROR: --measure deferred to Phase 2+.", file=sys.stderr)
        return 2

    try:
        src = resolve_language(args.source)
        tgt = resolve_language(args.target)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    embedding, embed_rationale = recommend_embedding(tgt.iso639_3, tgt.family)
    margin, margin_rationale, spot_n = recommend_margin(args.source_class, args.target_class)
    (lo, hi), len_rationale = recommend_length_ratio(tgt.iso639_3, tgt.family)

    out = {
        "source": src.display,
        "source_iso": src.iso639_3,
        "target": tgt.display,
        "target_iso": tgt.iso639_3,
        "snapshot_date": "2026-04-23",
        "recommendations": {
            "embedding_model": {"choice": embedding, "rationale": embed_rationale},
            "aligner": {"choice": "Vecalign", "rationale": "Default — linear-time + SoTA on Bibles + low-resource"},
            "margin_threshold": {"value": margin, "rationale": margin_rationale, "spot_check_sample_n": spot_n},
            "length_ratio_filter": {"min": lo, "max": hi, "rationale": len_rationale},
            "min_sentence_words_target": 3,
            "max_sentence_words_source": 200,
        },
        "anti_patterns_to_avoid": [
            "DO NOT use NLLB margin 1.06 for class 0-2 pairs",
            "DO NOT skip length-ratio filter after margin filter (~5% misalignments missed)",
            "DO NOT back-translate with T=0 (translationese drift)",
        ],
        "register_balance_target": "Bible ≤ 30%; news ≤ 70%; subtitles ≤ 50%; encyclopedic ≤ 60%",
        "next_step": "After mining: route to magic-linguistic-tokenize for fertility audit on bitext target side, then magic-linguistic-transfer for adapter/LoRA planning",  # noqa: E501  # long anti-pattern string
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
