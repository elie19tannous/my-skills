"""Look up OMW WordNet coverage for a target language.

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

# Cached OMW coverage per ISO (snapshot 2026-04-23)
# Princeton WordNet ≈ 117K synsets baseline.
PRINCETON_BASELINE = 117_000

_OMW: dict[str, dict] = {
    "eng": {"synsets": 117_000, "project": "Princeton WordNet (baseline)", "notes": "Reference standard"},
    "spa": {"synsets": 38_000, "project": "Spanish WordNet", "notes": "via OMW"},
    "fra": {"synsets": 33_000, "project": "French WordNet (WOLF)", "notes": "via OMW"},
    "ita": {"synsets": 35_000, "project": "Italian ItalWordNet", "notes": "via OMW"},
    "por": {"synsets": 41_000, "project": "Portuguese OpenWN-PT", "notes": "via OMW"},
    "deu": {"synsets": 22_000, "project": "GermaNet", "notes": "Standalone (commercial license restrictions)"},
    "cmn": {"synsets": 42_000, "project": "Chinese OpenCWN", "notes": "via OMW"},
    "jpn": {"synsets": 56_000, "project": "Japanese WordNet", "notes": "via OMW"},
    "kor": {"synsets": 16_000, "project": "Korean WordNet (KorLex)", "notes": "via OMW"},
    "hin": {"synsets": 28_000, "project": "Hindi WordNet (IIT-Bombay)", "notes": "via IndoWordNet"},
    "ben": {"synsets": 27_000, "project": "Bengali WordNet (IndoWordNet)", "notes": ""},
    "tam": {"synsets": 4_000, "project": "Tamil WordNet (IndoWordNet)", "notes": "Limited"},
    "tel": {"synsets": 12_000, "project": "Telugu (IndoWordNet)", "notes": ""},
    "arb": {"synsets": 9_000, "project": "Arabic WordNet", "notes": "via OMW; sparse"},
    "ara": {"synsets": 9_000, "project": "Arabic WordNet (macro)", "notes": "Macrolang; check subtag"},
    "heb": {"synsets": 8_000, "project": "Hebrew WordNet", "notes": "Sparse"},
    "vie": {"synsets": 10_000, "project": "Vietnamese WordNet", "notes": ""},
    "tha": {"synsets": 8_000, "project": "Thai WordNet (Asian WordNet)", "notes": ""},
    "ind": {"synsets": 14_000, "project": "Indonesian WordNet", "notes": ""},
    "tur": {"synsets": 19_000, "project": "Turkish KeNet (TURKWN)", "notes": ""},
    "fin": {"synsets": 30_000, "project": "FinnWordNet", "notes": ""},
    "rus": {"synsets": 35_000, "project": "RussNet / Russian Wordnet", "notes": ""},
    "yor": {"synsets": 5_000, "project": "Yoruba WordNet (limited)", "notes": "Patchy"},
    "swa": {"synsets": 4_000, "project": "Swahili WordNet (research)", "notes": "Limited"},
    "ibo": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "hau": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "khm": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "twi": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "iku": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "nav": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "chr": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "que": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "mri": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "amh": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
    "kin": {"synsets": None, "project": "absent", "notes": "No OMW entry"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="OMW WordNet coverage lookup.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    cov = _OMW.get(rec.iso639_3)
    if cov is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": f"No cached OMW data for {rec.iso639_3}; consult OMW project.",
                },
                indent=2,
            )
        )
        return 4

    if cov["synsets"] is None:
        coverage_pct = 0.0
        recommendation = "OMW absent — fall back to bilingual lexicon + custom sense inventory; document gap"
    else:
        coverage_pct = round(100 * cov["synsets"] / PRINCETON_BASELINE, 1)
        if coverage_pct >= 30:
            recommendation = "Coverage adequate for most lexical-semantics tasks"
        elif coverage_pct >= 10:
            recommendation = "Coverage partial — viable for common terms; expect gaps in rare/technical vocabulary"
        else:
            recommendation = (
                "Coverage minimal — synset-based query expansion / WSD not viable; use cross-lingual embeddings"
            )

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "synsets_available": cov["synsets"],
        "princeton_baseline": PRINCETON_BASELINE,
        "coverage_pct_vs_princeton": coverage_pct,
        "project": cov["project"],
        "notes": cov.get("notes", ""),
        "recommendation": recommendation,
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
