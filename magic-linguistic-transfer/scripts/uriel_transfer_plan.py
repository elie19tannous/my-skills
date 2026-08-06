"""Consolidate URIEL distance + Joshi class into a transfer-source recommendation.

Wraps logic from magic-linguistic-scope to produce a Transfer Plan-ready summary.
Phase 1 cached — pulls from magic-linguistic-scope's cached URIEL matrix indirectly
(re-listing close pairs by ISO).
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

# Cached subset of the magic-linguistic-scope URIEL distance matrix
# (mirroring uriel_distance.py snapshot 2026-04-23).
_DIST: dict[str, dict[str, float]] = {
    "yor": {"ibo": 0.18, "twi": 0.21, "hau": 0.34, "swa": 0.41, "wol": 0.39, "eng": 0.62},
    "ibo": {"yor": 0.18, "twi": 0.16, "hau": 0.32, "swa": 0.38, "eng": 0.61},
    "swa": {"zul": 0.18, "kin": 0.22, "yor": 0.41, "eng": 0.56},
    "khm": {"vie": 0.32, "tha": 0.30, "lao": 0.34, "ind": 0.46, "eng": 0.65},
    "vie": {"khm": 0.32, "cmn": 0.38, "ind": 0.42, "eng": 0.58},
    "cmn": {"yue": 0.20, "vie": 0.38, "kor": 0.42, "eng": 0.64},
    "yue": {"cmn": 0.20, "vie": 0.36, "eng": 0.66},
    "tur": {"aze": 0.14, "uzb": 0.18, "kaz": 0.20, "fin": 0.34, "eng": 0.60},
    "fin": {"est": 0.16, "hun": 0.22, "tur": 0.34, "eng": 0.55},
    "iku": {"kal": 0.21, "eng": 0.78},
    "nav": {"chr": 0.55, "eng": 0.74},
    "quz": {"que": 0.05, "aym": 0.34, "spa": 0.55, "eng": 0.66},
    "mri": {"smo": 0.16, "haw": 0.20, "eng": 0.61},
    "tam": {"tel": 0.22, "kan": 0.20, "mal": 0.18, "hin": 0.40, "eng": 0.60},
    "twi": {"ibo": 0.16, "yor": 0.21, "hau": 0.31},
    "kin": {"swa": 0.22, "zul": 0.16, "xho": 0.18, "eng": 0.59},
    "amh": {"hau": 0.38, "arb": 0.40, "heb": 0.36, "eng": 0.62},
}

# Heuristic Joshi class for cached candidates.
_CLASS = {
    "eng": 5,
    "spa": 5,
    "fra": 5,
    "deu": 5,
    "cmn": 5,
    "rus": 5,
    "jpn": 5,
    "vie": 4,
    "tur": 4,
    "tam": 4,
    "fin": 4,
    "hun": 4,
    "ind": 4,
    "ara": 4,
    "arb": 4,
    "heb": 4,
    "fas": 4,
    "swa": 3,
    "ben": 3,
    "hin": 4,
    "tha": 4,
    "kor": 4,
    "ukr": 3,
    "zul": 3,
    "kaz": 3,
    "uzb": 3,
    "yor": 3,
    "ibo": 2,
    "hau": 3,
    "khm": 2,
    "kin": 2,
    "amh": 2,
    "yue": 3,
    "tel": 4,
    "kan": 3,
    "mal": 3,
    "twi": 1,
    "wol": 1,
    "haw": 1,
    "mri": 1,
    "aze": 3,
    "fil": 3,
    "smo": 1,
    "iku": 1,
    "nav": 0,
    "chr": 0,
    "que": 1,
    "quz": 0,
    "aym": 1,
    "kal": 0,
    "est": 4,
}


def recommend(target_iso: str) -> dict:
    if target_iso not in _DIST:
        return {"warning": f"No cached URIEL data for {target_iso}; route to magic-linguistic-scope first"}

    candidates = sorted(_DIST[target_iso].items(), key=lambda kv: kv[1])
    annotated = []
    for src_iso, dist in candidates[:5]:
        cls = _CLASS.get(src_iso, "?")
        annotated.append(
            {
                "source_iso": src_iso,
                "uriel_distance": dist,
                "source_class": cls,
                "interpretation": _interpret(dist),
                "usable_for_single_source_transfer": (dist < 0.6 and isinstance(cls, int) and cls >= 3),
            }
        )

    # Recommend approach
    closest = candidates[0]
    closest_iso, closest_dist = closest
    closest_class = _CLASS.get(closest_iso, 0)
    if closest_dist < 0.4 and closest_class >= 3:
        approach = (
            f"single-source transfer from {closest_iso} (URIEL={closest_dist}); "
            f"continued pretraining viable if you have ≥ 1B target tokens, else OFA + LoRA r=16-32"
        )
        recommended_base = f"closest-language pretrained model (e.g., {closest_iso}-trained Llama / NLLB)"
    elif closest_dist < 0.6:
        approach = (
            f"single-source possible from {closest_iso} (URIEL={closest_dist}) but multilingual base is safer; "
            f"use OFA + LoRA r=32-64"
        )
        recommended_base = "multilingual base (NLLB-200 or BLOOM or Llama-3-multilingual)"
    else:
        approach = (
            f"NO close source (best={closest_iso} at {closest_dist}); "
            f"multilingual base + HyperOfa + LoRA r=64+ is the floor"
        )
        recommended_base = "multilingual base mandatory (NLLB-200 or BLOOM)"

    return {
        "target_iso": target_iso,
        "snapshot_date": "2026-04-23",
        "top_candidates": annotated,
        "recommended_approach": approach,
        "recommended_base": recommended_base,
        "anti_patterns_to_avoid": [
            "DO NOT default to English source for typologically-distant target (URIEL > 0.6)",
            "DO NOT use single-source from a Class 0-1 candidate (its model isn't useful as base)",
            "DO NOT continued-pretrain with < 100M target tokens (overfits + forgets)",
        ],
    }


def _interpret(d: float) -> str:
    if d < 0.20:
        return "very close — continued pretraining viable"
    if d < 0.40:
        return "close — CP + LoRA"
    if d < 0.60:
        return "moderate — OFA + LoRA r=32-64"
    if d < 0.80:
        return "distant — multilingual base + LoRA r=64+; do NOT single-source"
    return "very distant — train target representations from scratch; consider multilingual base only"


def main() -> int:
    parser = argparse.ArgumentParser(description="URIEL-based transfer-source recommendation.")
    parser.add_argument("target", help="Target language (name or ISO 639-3)")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.target)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out = {"target": rec.display, **recommend(rec.iso639_3)}
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
