"""Classify a language to Joshi 0-5 from cached signals.

Cached signal snapshot: 2026-04-23. Phase 1 ships cached only; --live is
deferred to Phase 2.
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

# Cached signal snapshot (2026-04-23). Hand-curated for the languages the
# magic-linguistic-* suite uses as canonical examples. Refresh procedure in
# references/canonical_sources.md.
#
# Schema per ISO 639-3 code:
#   wiki_articles: int (Wikipedia article count, 0 if no edition)
#   opus_pairs: int (OPUS bitext sentence pairs, summed across direction-symmetric)
#   flores200: bool (in FLORES-200)
#   nllb200: bool (in NLLB-200)
#   hf_datasets: int (HuggingFace dataset count with this language tag)
_SIGNALS: dict[str, dict] = {
    "eng": {
        "wiki_articles": 6_900_000,
        "opus_pairs": 8_000_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 5000,
    },
    "cmn": {
        "wiki_articles": 1_400_000,
        "opus_pairs": 1_500_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 800,
    },
    "spa": {
        "wiki_articles": 1_900_000,
        "opus_pairs": 2_000_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 600,
    },
    "fra": {
        "wiki_articles": 2_600_000,
        "opus_pairs": 2_500_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 700,
    },
    "deu": {
        "wiki_articles": 2_900_000,
        "opus_pairs": 3_000_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 600,
    },
    "jpn": {
        "wiki_articles": 1_400_000,
        "opus_pairs": 800_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 500,
    },
    "tur": {
        "wiki_articles": 590_000,
        "opus_pairs": 200_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 220,
    },
    "vie": {
        "wiki_articles": 1_290_000,
        "opus_pairs": 200_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 180,
    },
    "ind": {
        "wiki_articles": 700_000,
        "opus_pairs": 200_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 200,
    },
    "swa": {"wiki_articles": 80_000, "opus_pairs": 30_000_000, "flores200": True, "nllb200": True, "hf_datasets": 90},
    "tam": {"wiki_articles": 160_000, "opus_pairs": 50_000_000, "flores200": True, "nllb200": True, "hf_datasets": 110},
    "yor": {"wiki_articles": 33_000, "opus_pairs": 1_500_000, "flores200": True, "nllb200": True, "hf_datasets": 25},
    "ibo": {"wiki_articles": 22_000, "opus_pairs": 800_000, "flores200": True, "nllb200": True, "hf_datasets": 18},
    "hau": {"wiki_articles": 12_000, "opus_pairs": 2_000_000, "flores200": True, "nllb200": True, "hf_datasets": 22},
    "twi": {"wiki_articles": 800, "opus_pairs": 200_000, "flores200": False, "nllb200": True, "hf_datasets": 8},
    "khm": {"wiki_articles": 12_000, "opus_pairs": 5_000_000, "flores200": True, "nllb200": True, "hf_datasets": 14},
    "kin": {"wiki_articles": 9_000, "opus_pairs": 500_000, "flores200": True, "nllb200": True, "hf_datasets": 7},
    "iku": {"wiki_articles": 700, "opus_pairs": 100_000, "flores200": False, "nllb200": True, "hf_datasets": 3},
    "nav": {"wiki_articles": 1_200, "opus_pairs": 50_000, "flores200": False, "nllb200": False, "hf_datasets": 2},
    "chr": {"wiki_articles": 900, "opus_pairs": 0, "flores200": False, "nllb200": False, "hf_datasets": 1},
    "que": {"wiki_articles": 23_000, "opus_pairs": 200_000, "flores200": False, "nllb200": True, "hf_datasets": 6},
    "quz": {"wiki_articles": 0, "opus_pairs": 50_000, "flores200": False, "nllb200": True, "hf_datasets": 2},
    "mri": {"wiki_articles": 8_000, "opus_pairs": 500_000, "flores200": True, "nllb200": True, "hf_datasets": 11},
    "haw": {"wiki_articles": 4_500, "opus_pairs": 100_000, "flores200": False, "nllb200": True, "hf_datasets": 4},
    "fin": {
        "wiki_articles": 580_000,
        "opus_pairs": 500_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 200,
    },
    "hun": {
        "wiki_articles": 540_000,
        "opus_pairs": 500_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 180,
    },
    "kaz": {"wiki_articles": 240_000, "opus_pairs": 50_000_000, "flores200": True, "nllb200": True, "hf_datasets": 30},
    "uzb": {"wiki_articles": 240_000, "opus_pairs": 30_000_000, "flores200": True, "nllb200": True, "hf_datasets": 22},
    "amh": {"wiki_articles": 16_000, "opus_pairs": 5_000_000, "flores200": True, "nllb200": True, "hf_datasets": 18},
    "wol": {"wiki_articles": 1_500, "opus_pairs": 300_000, "flores200": True, "nllb200": True, "hf_datasets": 7},
    "sme": {"wiki_articles": 7_500, "opus_pairs": 200_000, "flores200": False, "nllb200": False, "hf_datasets": 4},
    "ara": {
        "wiki_articles": 1_300_000,
        "opus_pairs": 1_000_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 400,
    },  # macro
    "arb": {
        "wiki_articles": 1_300_000,
        "opus_pairs": 1_000_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 350,
    },  # MSA
    "arz": {
        "wiki_articles": 1_700_000,
        "opus_pairs": 5_000_000,
        "flores200": True,
        "nllb200": True,
        "hf_datasets": 22,
    },  # Egyptian
}


def classify(signals: dict) -> tuple[int, list[str]]:
    """Return (Joshi class 0-5, reasons[])."""
    reasons = []
    has_wiki = signals["wiki_articles"] >= 1_000
    has_opus = signals["opus_pairs"] >= 10_000
    in_flores = signals["flores200"]
    in_nllb = signals["nllb200"]
    hf = signals["hf_datasets"]

    reasons.append(f"wiki_articles={signals['wiki_articles']:,} (threshold 1k)")
    reasons.append(f"opus_pairs={signals['opus_pairs']:,} (threshold 10k)")
    reasons.append(f"flores200={in_flores}, nllb200={in_nllb}")
    reasons.append(f"hf_datasets={hf}")

    if not has_wiki and not has_opus:
        return 0, reasons + ["Class 0 — no Wikipedia or OPUS data"]
    if (has_wiki or has_opus) and not (in_flores or in_nllb):
        return 1, reasons + ["Class 1 — some unlabelled data, no benchmarks"]
    if has_wiki and has_opus and hf >= 5 and not in_flores:
        return 2, reasons + ["Class 2 — Wiki+OPUS+labelled, no FLORES"]
    if has_wiki and has_opus and (in_flores or in_nllb) and hf >= 20:
        if hf >= 200:
            return 5, reasons + ["Class 5 — saturated benchmarks"]
        if hf >= 50 and in_flores and in_nllb:
            return 4, reasons + ["Class 4 — many benchmarks"]
        return 3, reasons + ["Class 3 — multiple labelled tasks + benchmarks"]
    return 2, reasons + ["Class 2 (default) — labelled data exists but signals mixed"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Classify language to Joshi 0-5 class.")
    parser.add_argument("query", help="Language name or ISO 639-3 code")
    parser.add_argument("--live", action="store_true", help="(Phase 2+) query live signals")
    args = parser.parse_args()

    if args.live:
        print("ERROR: --live is deferred to Phase 2+. Cached snapshot only in Phase 1.", file=sys.stderr)
        return 2

    try:
        rec = resolve_language(args.query)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    sig = _SIGNALS.get(rec.iso639_3)
    if sig is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "class": None,
                    "warning": f"No cached signals for {rec.iso639_3}; cannot classify. Add to _SIGNALS or use --live (Phase 2+).",  # noqa: E501  # long anti-pattern string
                },
                indent=2,
            )
        )
        return 4

    cls, reasons = classify(sig)
    print(
        json.dumps(
            {
                "language": rec.display,
                "iso639_3": rec.iso639_3,
                "joshi_class": cls,
                "signals": sig,
                "reasoning": reasons,
                "snapshot_date": "2026-04-23",
            },
            indent=2,
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
