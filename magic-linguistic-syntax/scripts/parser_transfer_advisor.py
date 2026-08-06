"""Recommend a parser tool + cross-lingual transfer source for a target language.

Phase 1 cached: combines UD coverage + URIEL distance + parser tool defaults.
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

# Cached recommended parser source per target (when target lacks UD training data).
# Format: {target_iso: [(source_iso, rationale)]}
_TRANSFER_SOURCES: dict[str, list[tuple[str, str]]] = {
    "yor": [
        ("ibo", "Same Niger-Congo family branch; close URIEL — but Igbo has no UD itself"),
        ("eng", "English Latin script; URIEL ~0.62 — distant; expect ~50-60 UAS zero-shot"),
    ],
    "twi": [("ibo", "Same family branch — no Igbo UD; fall back"), ("eng", "Latin script; distant URIEL")],
    "khm": [
        ("vie", "Geographic + tone-language proximity; Vietnamese has ~12K UD"),
        ("tha", "Tai-Kadai SEA neighbor (no Thai UD however)"),
        ("eng", "fallback distant"),
    ],
    "yue": [("cmn", "Mandarin closest URIEL (~0.20) + 35K UD; native Han script overlap")],
    "iku": [("eng", "no close source has UD; multilingual base + zero-shot; expect low UAS")],
    "mri": [("ind", "Austronesian neighbor with 6K UD"), ("eng", "Latin-script fallback")],
    "nav": [("eng", "no close source; multilingual base; expect very low UAS — agreement probes preferred")],
    "amh": [
        ("ara", "Semitic neighbor — both templatic; Arabic has 30K UD"),
        ("eng", "Latin-script transliteration distant fallback"),
    ],
    "que": [("spa", "Spanish loanword influence + 60K UD; URIEL distance moderate"), ("eng", "fallback")],
    "swa": [("eng", "no close Bantu UD; multilingual base zero-shot")],
    "kin": [("eng", "no close Bantu UD; multilingual base zero-shot")],
    "tam": [("hin", "Indic neighbor; Hindi UD 17K; URIEL moderate")],
    "tel": [("hin", "Indic; Hindi UD 17K"), ("tam", "Dravidian sister — Tamil UD 7K")],
    "hau": [
        ("eng", "Latin script; English UD large; expect moderate"),
        ("ara", "Ajami script alternative; Arabic UD 30K"),
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Parser tool + cross-lingual transfer source recommendation.")
    parser.add_argument("language", help="Target language name or ISO 639-3")
    parser.add_argument("--prefer-tool", choices=["trankit", "stanza", "udify", "spacy", "auto"], default="auto")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    # Cross-skill: pull UD coverage from sibling script
    sys.path.insert(0, str(Path(__file__).resolve().parents[0]))
    from ud_coverage import _UD  # noqa: E402

    cov = _UD.get(rec.iso639_3)

    sources = _TRANSFER_SOURCES.get(rec.iso639_3, [])

    # Tool recommendation
    if args.prefer_tool == "auto":
        if cov and cov.get("training_viable"):
            tool = {
                "primary": "Trankit (best LR quality) or stanza (speed)",
                "rationale": "Native UD treebank exists; either tool fine-tunes well",
            }
        else:
            tool = {
                "primary": "Trankit",
                "rationale": "Cross-lingual transfer; Trankit beats stanza on low-resource quality",
            }
    else:
        tool = {"primary": args.prefer_tool, "rationale": "user-specified"}

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "ud_coverage": cov if cov else "absent",
        "approach": (
            "native fine-tune"
            if (cov and cov.get("training_viable"))
            else "cross-lingual zero-shot"
            if (cov and cov.get("total_sentences", 0) > 0)
            else "cross-lingual zero-shot (no UD available — eval limited)"
        ),
        "transfer_source_candidates": [{"iso": iso, "rationale": rat} for iso, rat in sources],
        "parser_tool": tool,
        "agreement_probes_recommended": True,
        "agreement_probes_rationale": "LLMs don't expose parses; agreement probes evaluate grammatical knowledge directly",  # noqa: E501  # long anti-pattern string
        "anti_patterns": [
            "DO NOT fine-tune on PUD-style 1K test treebanks (eval leak)",
            "DO NOT pick source by treebank size alone — URIEL typological distance dominates",
            "DO NOT report parser F1 as proxy for LLM grammatical knowledge",
        ],
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
