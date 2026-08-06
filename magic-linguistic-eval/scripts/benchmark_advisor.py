"""Recommend benchmark suite for a (language, task) pair.

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

# Cached benchmark coverage per task (snapshot 2026-04-23).
_BENCHMARKS: dict[str, dict] = {
    "mt": {
        "broad": {
            "FLORES+": {"langs": 200, "release": "2022-07", "contamination_risk": "high"},
            "NTREX-128": {"langs": 128, "release": "2022-11", "contamination_risk": "medium"},
        },
        "africa": {
            "AfroBench": {"langs": 64, "release": "2024-12", "contamination_risk": "low"},
            "MAFAND-MT": {"langs": 21, "release": "2022", "contamination_risk": "medium"},
        },
        "indic": {"IN22": {"langs": 22, "release": "2023", "contamination_risk": "medium"}},
        "sea": {"SEACrowd MT": {"langs": "many", "release": "2025", "contamination_risk": "low"}},
        "americas": {"AmericasNLP": {"langs": 10, "release": "annual", "contamination_risk": "low"}},
    },
    "reading": {
        "broad": {"Belebele": {"langs": 122, "release": "2023-08", "contamination_risk": "medium"}},
    },
    "ner": {
        "africa": {"MasakhaNER 2.0": {"langs": 21, "release": "2024", "contamination_risk": "medium"}},
        "broad": {"WikiAnn": {"langs": 280, "release": "2017", "contamination_risk": "high (older)"}},
        "english": {
            "OntoNotes": {"langs": 3, "release": "2013", "contamination_risk": "high"},
            "CoNLL-2003": {"langs": 4, "release": "2003", "contamination_risk": "very high"},
        },
    },
    "sentiment": {
        "africa": {"AfriSenti": {"langs": 14, "release": "2023", "contamination_risk": "medium"}},
    },
    "qa": {
        "broad": {
            "TyDi-QA": {"langs": 11, "release": "2020", "contamination_risk": "high"},
            "XQuAD": {"langs": 10, "release": "2019", "contamination_risk": "high"},
        },
    },
    "general": {
        "broad": {
            "XNLI": {"langs": 15, "release": "2018", "contamination_risk": "high"},
            "BIG-bench": {"langs": "varies", "release": "2022", "contamination_risk": "high"},
            "BUFFET": {"langs": 56, "release": "2023", "contamination_risk": "medium"},
        },
    },
    "speech_asr": {
        "broad": {
            "Common Voice": {"langs": 100, "release": "rolling", "contamination_risk": "low"},
            "OpenSLR": {"langs": 200, "release": "rolling", "contamination_risk": "low"},
        },
        "mms": {"MMS-FLEURS": {"langs": 102, "release": "2024", "contamination_risk": "low"}},
    },
}


def region_for_lang(iso: str) -> list[str]:
    africa = {"yor", "ibo", "hau", "swa", "kin", "twi", "wol", "amh", "zul", "xho"}
    indic = {"hin", "ben", "tam", "tel", "kan", "mal", "guj", "pan", "mar", "urd"}
    sea = {"vie", "khm", "tha", "ind", "tgl", "mya", "lao"}
    americas = {"que", "quz", "aym", "grn", "nav", "chr", "iku"}
    if iso in africa:
        return ["africa", "broad"]
    if iso in indic:
        return ["indic", "broad"]
    if iso in sea:
        return ["sea", "broad"]
    if iso in americas:
        return ["americas", "broad"]
    return ["broad"]


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark advisor for (language, task) pair.")
    parser.add_argument("language", help="Target language name or ISO 639-3")
    parser.add_argument("--task", required=True, choices=list(_BENCHMARKS.keys()), help="Task type")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    task_benchmarks = _BENCHMARKS[args.task]
    regions = region_for_lang(rec.iso639_3)

    selected = []
    for region in regions:
        if region in task_benchmarks:
            for bm_name, info in task_benchmarks[region].items():
                selected.append({"name": bm_name, "region": region, **info})

    if not selected:
        out = {
            "language": rec.display,
            "iso639_3": rec.iso639_3,
            "task": args.task,
            "warning": f"No cached benchmark for ({rec.iso639_3}, {args.task}); recommend custom held-out.",
        }
        print(json.dumps(out, indent=2, ensure_ascii=False))
        return 4

    # Recommend lowest-contamination-risk first
    risk_order = {"low": 0, "medium": 1, "high": 2, "very high": 3, "high (older)": 3}
    selected.sort(key=lambda b: risk_order.get(b.get("contamination_risk", "high"), 2))

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "task": args.task,
        "snapshot_date": "2026-04-23",
        "recommended_primary": selected[0],
        "alternatives": selected[1:],
        "anti_patterns": [
            "DO NOT use FLORES-200 without contamination check (high pretrain inclusion)",
            "DO NOT use single benchmark — cross-validate with at least one other",
            "DO NOT report aggregate without per-stratum (dialect/register/direction) breakdown",
        ],
        "next_step": "Run scripts/contamination_check.py against your base model's training cutoff",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
