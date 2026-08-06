"""Look up morphological-paradigm coverage for a target language.

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

# Cached UniMorph + FST coverage per ISO (snapshot 2026-04-23)
# tier: lo / mid / hi / extreme
# unimorph: deep / mid / shallow / absent
# fst: short list of available analyzers; "none" if none
_COVERAGE: dict[str, dict] = {
    "eng": {"tier": "lo", "unimorph": "deep", "fst": "none — not needed", "type": "fusional-low"},
    "spa": {"tier": "mid", "unimorph": "deep", "fst": "Apertium-spa", "type": "fusional-Romance"},
    "fra": {"tier": "mid", "unimorph": "deep", "fst": "Apertium-fra", "type": "fusional-Romance"},
    "deu": {"tier": "mid", "unimorph": "deep", "fst": "Apertium-deu, HFST-deu", "type": "fusional-Germanic"},
    "rus": {"tier": "hi", "unimorph": "deep", "fst": "HFST-rus, Apertium-rus", "type": "fusional-Slavic"},
    "tur": {"tier": "hi", "unimorph": "deep", "fst": "HFST-tur, TRMorph", "type": "agglutinative-Turkic"},
    "fin": {"tier": "hi", "unimorph": "deep", "fst": "HFST-fin (Omorfi)", "type": "agglutinative-Uralic"},
    "hun": {"tier": "hi", "unimorph": "deep", "fst": "HFST-hun", "type": "agglutinative-Uralic"},
    "kaz": {"tier": "hi", "unimorph": "mid", "fst": "Apertium-kaz", "type": "agglutinative-Turkic"},
    "uzb": {"tier": "hi", "unimorph": "mid", "fst": "Apertium-uzb", "type": "agglutinative-Turkic"},
    "kor": {"tier": "hi", "unimorph": "mid", "fst": "KOMA, KKMA", "type": "agglutinative-Koreanic"},
    "swa": {"tier": "hi", "unimorph": "shallow", "fst": "limited", "type": "agglutinative-Bantu"},
    "kin": {"tier": "hi", "unimorph": "shallow", "fst": "none", "type": "agglutinative-Bantu"},
    "yor": {"tier": "mid", "unimorph": "mid", "fst": "limited", "type": "isolating-tone"},
    "ibo": {"tier": "mid", "unimorph": "shallow", "fst": "none", "type": "isolating-tone"},
    "twi": {"tier": "mid", "unimorph": "shallow", "fst": "none", "type": "isolating-tone"},
    "amh": {"tier": "hi", "unimorph": "mid", "fst": "HornMorpho", "type": "templatic-Semitic"},
    "arb": {"tier": "hi", "unimorph": "mid", "fst": "HFST-arb, Farasa, MADAMIRA", "type": "templatic-Semitic"},
    "heb": {"tier": "hi", "unimorph": "mid", "fst": "YAP, MILA-tools", "type": "templatic-Semitic"},
    "fas": {"tier": "hi", "unimorph": "mid", "fst": "HFST-fas", "type": "fusional-Iranian"},
    "hin": {"tier": "mid", "unimorph": "mid", "fst": "stanza-hin", "type": "fusional-Indic"},
    "tam": {"tier": "hi", "unimorph": "mid", "fst": "Apertium-tam", "type": "agglutinative-Dravidian"},
    "mri": {"tier": "mid", "unimorph": "shallow", "fst": "Apertium-mri", "type": "agglutinative-Austronesian"},
    "khm": {"tier": "mid", "unimorph": "shallow", "fst": "none", "type": "isolating"},
    "vie": {"tier": "lo", "unimorph": "shallow", "fst": "none", "type": "isolating-tone"},
    "cmn": {"tier": "lo", "unimorph": "shallow", "fst": "none — analytic", "type": "isolating"},
    "iku": {"tier": "extreme", "unimorph": "shallow", "fst": "HFST-iku (Inuit-FST)", "type": "polysynthetic-Eskimo"},
    "kal": {"tier": "extreme", "unimorph": "shallow", "fst": "HFST-kal (Greenlandic)", "type": "polysynthetic-Eskimo"},
    "nav": {
        "tier": "extreme",
        "unimorph": "absent",
        "fst": "limited (research only)",
        "type": "polysynthetic-Athabaskan",
    },
    "chr": {"tier": "extreme", "unimorph": "absent", "fst": "partial (community)", "type": "polysynthetic-Iroquoian"},
    "que": {"tier": "hi", "unimorph": "shallow", "fst": "Apertium-que", "type": "agglutinative-Quechuan"},
    "quz": {"tier": "hi", "unimorph": "shallow", "fst": "Apertium-quz", "type": "agglutinative-Quechuan"},
    "sme": {"tier": "hi", "unimorph": "deep", "fst": "HFST-sme (UiT)", "type": "agglutinative-Uralic-Sami"},
    "haw": {"tier": "mid", "unimorph": "shallow", "fst": "limited", "type": "agglutinative-Austronesian"},
}


def _approach(cov: dict) -> str:
    tier, unim, ttype = cov["tier"], cov["unimorph"], cov.get("type", "")
    if tier == "lo":
        return "Standard tokenizer fine; morph skill rarely needed for tier=lo"
    if "templatic" in ttype:
        return "TEMPLATIC: do NOT use concatenative segmenter; use root-pattern tools (Farasa/HornMorpho/YAP)"
    if tier == "extreme":
        return "POLYSYNTHETIC: morpheme segmentation MANDATORY; use FST if available, else SIGMORPHON 2023 + community paradigms"  # noqa: E501  # long anti-pattern string
    if tier == "hi" and unim in ("deep", "mid"):
        return "HIGH morphology + UniMorph available: paradigms + paradigm-completion augmentation"
    if tier == "hi":
        return "HIGH morphology, no UniMorph: SIGMORPHON 2023 segmenter + tokenizer audit"
    return "MID morphology: BPE may suffice; check fertility before deciding on segmenter"


def main() -> int:
    parser = argparse.ArgumentParser(description="Morphology coverage lookup.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    cov = _COVERAGE.get(rec.iso639_3)
    if cov is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": f"No cached morphology coverage for {rec.iso639_3}; consult magic-linguistic-morph references.",  # noqa: E501  # long anti-pattern string
                },
                indent=2,
            )
        )
        return 4

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "morphology_tier": cov["tier"],
        "morphology_type": cov.get("type", ""),
        "unimorph_coverage": cov["unimorph"],
        "fst_analyzers": cov["fst"],
        "recommended_approach": _approach(cov),
        "snapshot_date": "2026-04-23",
        "next_step": "Hand off to magic-linguistic-tokenize for fertility re-audit; magic-linguistic-syntax for morphology-aware parsing",  # noqa: E501  # long anti-pattern string
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
