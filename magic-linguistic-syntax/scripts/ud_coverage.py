"""Look up UD treebank availability for a target language.

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

# Cached UD coverage per ISO (snapshot 2026-04-23)
_UD: dict[str, dict] = {
    "eng": {
        "treebanks": ["EWT", "GUM", "ParTUT", "LinES", "Atis"],
        "total_sentences": 250_000,
        "training_viable": True,
    },
    "spa": {"treebanks": ["AnCora", "GSD", "PUD"], "total_sentences": 60_000, "training_viable": True},
    "fra": {
        "treebanks": ["GSD", "ParTUT", "Sequoia", "Spoken", "PUD"],
        "total_sentences": 50_000,
        "training_viable": True,
    },
    "deu": {"treebanks": ["GSD", "HDT", "PUD"], "total_sentences": 220_000, "training_viable": True},
    "rus": {"treebanks": ["SynTagRus", "GSD", "Taiga", "PUD"], "total_sentences": 110_000, "training_viable": True},
    "cmn": {"treebanks": ["GSD", "GSDsimp", "HK", "PUD", "CFL"], "total_sentences": 35_000, "training_viable": True},
    "jpn": {"treebanks": ["GSD", "BCCWJ", "PUD"], "total_sentences": 30_000, "training_viable": True},
    "vie": {"treebanks": ["VTB"], "total_sentences": 12_000, "training_viable": True},
    "ind": {
        "treebanks": ["GSD", "PUD"],
        "total_sentences": 6_000,
        "training_viable": True,
        "notes": "Indonesian: medium",
    },
    "tam": {"treebanks": ["TTB"], "total_sentences": 7_000, "training_viable": True},
    "tel": {
        "treebanks": ["MTG"],
        "total_sentences": 1_400,
        "training_viable": False,
        "notes": "Telugu: small + PUD-like",
    },
    "hin": {"treebanks": ["HDTB", "PUD"], "total_sentences": 17_000, "training_viable": True},
    "tur": {"treebanks": ["IMST", "PUD", "BOUN"], "total_sentences": 70_000, "training_viable": True},
    "fin": {"treebanks": ["TDT", "PUD", "FTB"], "total_sentences": 30_000, "training_viable": True},
    "hun": {
        "treebanks": ["Szeged"],
        "total_sentences": 1_400,
        "training_viable": False,
        "notes": "Hungarian: only Szeged + small",
    },
    "kor": {"treebanks": ["GSD", "Kaist", "PUD"], "total_sentences": 50_000, "training_viable": True},
    "ara": {"treebanks": ["PADT", "NYUAD", "PUD"], "total_sentences": 30_000, "training_viable": True},
    "heb": {"treebanks": ["HTB", "IAHLTwiki"], "total_sentences": 10_000, "training_viable": True},
    "yor": {
        "treebanks": ["YTB"],
        "total_sentences": 100,
        "training_viable": False,
        "notes": "Yoruba: tiny — eval only",
    },
    "ibo": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "hau": {"treebanks": ["NA"], "total_sentences": 0, "training_viable": False, "notes": "Hausa: no canonical UD"},
    "swa": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "Swahili: in development"},
    "khm": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "twi": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "yue": {"treebanks": ["HK"], "total_sentences": 1_000, "training_viable": False, "notes": "PUD-style — eval only"},
    "iku": {
        "treebanks": ["IUIT"],
        "total_sentences": 1_000,
        "training_viable": False,
        "notes": "PUD-style — eval only",
    },
    "mri": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "nav": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "chr": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
    "que": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "Some experimental"},
    "amh": {"treebanks": ["ATT"], "total_sentences": 1_000, "training_viable": False, "notes": "PUD-style — eval only"},
    "kin": {"treebanks": [], "total_sentences": 0, "training_viable": False, "notes": "No UD treebank"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="UD treebank coverage lookup.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    cov = _UD.get(rec.iso639_3)
    if cov is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": f"No cached UD data for {rec.iso639_3}; consult universaldependencies.org directly.",
                },
                indent=2,
            )
        )
        return 4

    if cov["total_sentences"] >= 10_000:
        approach = "Native fine-tune feasible — use largest treebank for training, others for eval"
    elif cov["total_sentences"] >= 1_000:
        approach = "Marginal — consider cross-lingual transfer + few-shot fine-tune; PUD-style data is EVAL-ONLY"
    elif cov["total_sentences"] > 0:
        approach = "PUD-style treebank — EVAL ONLY (do NOT fine-tune); cross-lingual zero-shot for parsing"
    else:
        approach = "No UD treebank — cross-lingual zero-shot mandatory; document eval limitation"

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "treebanks": cov["treebanks"],
        "total_sentences": cov["total_sentences"],
        "training_viable": cov["training_viable"],
        "notes": cov.get("notes", ""),
        "recommended_approach": approach,
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
