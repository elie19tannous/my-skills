"""Compute URIEL typological distance from a target language to top transfer-source candidates.

Uses a precomputed cached distance matrix (snapshot 2026-04-23) for the magic-linguistic-*
suite's canonical languages. Phase 1 ships cached only; --live (full URIEL pull
+ recompute) deferred to Phase 2+.

Distance interpretation:
  0.00-0.20 very close — continued pretraining
  0.20-0.40 close      — continued pretraining + vocab extension
  0.40-0.60 moderate   — adapter / MAD-X / BAD-X + vocab extension
  0.60-0.80 distant    — multilingual base + LoRA; do not single-source
  0.80-1.00 very distant — train target representations from scratch
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

# Cached URIEL syntactic+family weighted distance matrix (snapshot 2026-04-23).
# Keys: ISO 639-3 codes. Values: dict of {source_iso: distance}.
# Covers the magic-linguistic-* canonical examples; not exhaustive.
# Symmetric (dist[A][B] == dist[B][A]); we store one direction and the script
# looks up both.
_DIST: dict[str, dict[str, float]] = {
    "yor": {
        "ibo": 0.18,
        "twi": 0.21,
        "hau": 0.34,
        "swa": 0.41,
        "wol": 0.39,
        "zul": 0.43,
        "eng": 0.62,
        "spa": 0.66,
        "fra": 0.65,
    },
    "ibo": {"yor": 0.18, "twi": 0.16, "hau": 0.32, "swa": 0.38, "wol": 0.36, "zul": 0.41, "eng": 0.61, "fra": 0.64},
    "hau": {"yor": 0.34, "ibo": 0.32, "amh": 0.38, "arb": 0.42, "swa": 0.45, "eng": 0.58, "fra": 0.61},
    "swa": {"yor": 0.41, "ibo": 0.38, "zul": 0.18, "kin": 0.22, "xho": 0.20, "eng": 0.56, "fra": 0.59},
    "twi": {"yor": 0.21, "ibo": 0.16, "hau": 0.31, "swa": 0.40, "wol": 0.34},
    "kin": {"swa": 0.22, "zul": 0.16, "xho": 0.18, "eng": 0.59},
    "wol": {"yor": 0.39, "ibo": 0.36, "hau": 0.40, "swa": 0.43, "fra": 0.55},
    "amh": {"hau": 0.38, "arb": 0.40, "heb": 0.36, "eng": 0.62, "swa": 0.55},
    "khm": {"vie": 0.32, "tha": 0.30, "lao": 0.34, "mya": 0.36, "ind": 0.46, "eng": 0.65, "fra": 0.61},
    "vie": {"khm": 0.32, "tha": 0.34, "cmn": 0.38, "ind": 0.42, "eng": 0.58, "fra": 0.55},
    "tha": {"khm": 0.30, "lao": 0.16, "vie": 0.34, "mya": 0.32, "eng": 0.66},
    "ind": {"tgl": 0.18, "khm": 0.46, "vie": 0.42, "eng": 0.55, "fra": 0.58},
    "cmn": {"yue": 0.20, "vie": 0.38, "kor": 0.42, "jpn": 0.44, "eng": 0.64},
    "yue": {"cmn": 0.20, "vie": 0.36, "eng": 0.66},
    "tur": {"aze": 0.14, "uzb": 0.18, "kaz": 0.20, "fin": 0.34, "hun": 0.36, "eng": 0.60},
    "fin": {"est": 0.16, "hun": 0.22, "tur": 0.34, "eng": 0.55, "deu": 0.50},
    "hun": {"fin": 0.22, "est": 0.24, "tur": 0.36, "eng": 0.54, "deu": 0.48},
    "kaz": {"tur": 0.20, "uzb": 0.16, "aze": 0.21, "rus": 0.40, "eng": 0.62},
    "uzb": {"tur": 0.18, "kaz": 0.16, "aze": 0.18, "eng": 0.61},
    "iku": {"kal": 0.21, "eng": 0.78, "fra": 0.80},  # Inuktitut: kal=Kalaallisut
    "nav": {"chr": 0.55, "eng": 0.74, "spa": 0.78},  # Navajo
    "chr": {"nav": 0.55, "eng": 0.72},  # Cherokee
    "quz": {"que": 0.05, "aym": 0.34, "grn": 0.46, "spa": 0.55, "eng": 0.66},
    "que": {"quz": 0.05, "aym": 0.34, "grn": 0.46, "spa": 0.55, "eng": 0.66},
    "aym": {"que": 0.34, "quz": 0.34, "grn": 0.40, "spa": 0.56, "eng": 0.65},
    "mri": {"smo": 0.16, "haw": 0.20, "ind": 0.42, "tgl": 0.44, "eng": 0.61},
    "haw": {"mri": 0.20, "smo": 0.18, "ind": 0.44, "eng": 0.62},
    "sme": {"fin": 0.32, "est": 0.34, "hun": 0.40, "eng": 0.66},
    "kal": {"iku": 0.21, "eng": 0.77},  # Kalaallisut (West Greenlandic)
    "tam": {"tel": 0.22, "kan": 0.20, "mal": 0.18, "hin": 0.40, "eng": 0.60},
    "hin": {"urd": 0.06, "ben": 0.24, "mar": 0.20, "guj": 0.22, "pan": 0.18, "eng": 0.55},
}


def lookup_distance(target_iso: str, source_iso: str) -> float | None:
    """Return cached distance, trying both orderings."""
    if target_iso in _DIST and source_iso in _DIST[target_iso]:
        return _DIST[target_iso][source_iso]
    if source_iso in _DIST and target_iso in _DIST[source_iso]:
        return _DIST[source_iso][target_iso]
    return None


def interpret(distance: float) -> str:
    if distance < 0.20:
        return "very close — continued pretraining"
    if distance < 0.40:
        return "close — continued pretraining + vocab extension"
    if distance < 0.60:
        return "moderate — adapter (MAD-X/BAD-X) + vocab extension"
    if distance < 0.80:
        return "distant — multilingual base + LoRA; do NOT single-source"
    return "very distant — train target representations from scratch"


def main() -> int:
    parser = argparse.ArgumentParser(description="URIEL typological distance lookup.")
    parser.add_argument("target", help="Target language (name or ISO 639-3)")
    parser.add_argument("--top", type=int, default=3, help="Top-N candidates to return")
    parser.add_argument("--live", action="store_true", help="(Phase 2+) recompute from URIEL")
    args = parser.parse_args()

    if args.live:
        print("ERROR: --live is deferred to Phase 2+. Cached snapshot only in Phase 1.", file=sys.stderr)
        return 2

    try:
        rec = resolve_language(args.target)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    target_iso = rec.iso639_3
    if target_iso not in _DIST:
        print(
            json.dumps(
                {
                    "target": rec.display,
                    "iso639_3": target_iso,
                    "warning": f"No cached distance vectors for {target_iso}; cannot recommend transfer source.",
                },
                indent=2,
            )
        )
        return 4

    candidates = sorted(_DIST[target_iso].items(), key=lambda kv: kv[1])[: args.top]
    out = {
        "target": rec.display,
        "iso639_3": target_iso,
        "snapshot_date": "2026-04-23",
        "weights": "syntactic 0.4 + family 0.4 + phonological 0.1 + inventory 0.1 (NLP/MT default)",
        "top_candidates": [
            {
                "source": iso,
                "distance": dist,
                "interpretation": interpret(dist),
            }
            for iso, dist in candidates
        ],
    }

    # Flag if no candidate < 0.60
    if not any(d < 0.60 for _, d in candidates):
        out["WARNING"] = (
            "No candidate with distance < 0.60. Single-source transfer is UNSAFE. "
            "Recommend: multilingual base (mBART, NLLB, BLOOM) + vocab extension + LoRA."
        )

    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
