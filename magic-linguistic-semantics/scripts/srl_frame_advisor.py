"""Advise on SRL / frame-semantics tooling for a target language.

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

# Cached per-language frame/SRL availability (snapshot 2026-04-23).
_FRAME: dict[str, dict] = {
    "eng": {
        "framenet": "Berkeley FrameNet (~1200 frames, mature)",
        "propbank": "Penn PropBank",
        "srl_tool": "AllenNLP BERT-SRL",
        "via_predicate_matrix": "primary anchor",
    },
    "spa": {
        "framenet": "Spanish FrameNet (~150 frames)",
        "propbank": "AnCora SRL",
        "srl_tool": "stanza + custom",
        "via_predicate_matrix": "yes",
    },
    "deu": {
        "framenet": "SALSA (partial)",
        "propbank": "TIGER PropBank",
        "srl_tool": "stanza + custom",
        "via_predicate_matrix": "yes",
    },
    "fra": {
        "framenet": "French FrameNet (research)",
        "propbank": "limited",
        "srl_tool": "stanza",
        "via_predicate_matrix": "yes",
    },
    "ita": {"framenet": "limited", "propbank": "AnCora-style", "srl_tool": "stanza", "via_predicate_matrix": "yes"},
    "jpn": {
        "framenet": "Japanese FrameNet (~700 frames)",
        "propbank": "limited",
        "srl_tool": "ja-LSTM-SRL",
        "via_predicate_matrix": "yes",
    },
    "cmn": {
        "framenet": "Chinese FrameNet (~300 frames)",
        "propbank": "Chinese PropBank",
        "srl_tool": "stanza-zh",
        "via_predicate_matrix": "yes",
    },
    "por": {
        "framenet": "FrameNet Brasil (~600 frames)",
        "propbank": "Propbank.br",
        "srl_tool": "stanza",
        "via_predicate_matrix": "yes",
    },
    "kor": {"framenet": "limited", "propbank": "Korean PropBank", "srl_tool": "stanza", "via_predicate_matrix": "yes"},
    "swe": {
        "framenet": "Swedish FrameNet++",
        "propbank": "limited",
        "srl_tool": "stanza",
        "via_predicate_matrix": "yes",
    },
    "ara": {
        "framenet": "absent",
        "propbank": "Arabic PropBank",
        "srl_tool": "Farasa-SRL",
        "via_predicate_matrix": "indirect",
    },
    "arb": {
        "framenet": "absent",
        "propbank": "Arabic PropBank",
        "srl_tool": "Farasa-SRL",
        "via_predicate_matrix": "indirect",
    },
    "heb": {"framenet": "absent", "propbank": "limited", "srl_tool": "limited", "via_predicate_matrix": "indirect"},
    "hin": {
        "framenet": "Hindi FrameNet (research)",
        "propbank": "Hindi-Urdu PropBank",
        "srl_tool": "stanza-hi",
        "via_predicate_matrix": "yes",
    },
    "tur": {"framenet": "absent", "propbank": "limited", "srl_tool": "stanza-tr", "via_predicate_matrix": "indirect"},
    "vie": {"framenet": "absent", "propbank": "absent", "srl_tool": "limited", "via_predicate_matrix": "indirect"},
    "tha": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "yor": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "khm": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "swa": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "iku": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "que": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "amh": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "indirect"},
    "twi": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "kin": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
    "mri": {"framenet": "absent", "propbank": "absent", "srl_tool": "absent", "via_predicate_matrix": "n/a"},
}


def main() -> int:
    parser = argparse.ArgumentParser(description="SRL / frame-semantics tooling advisor.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    cov = _FRAME.get(rec.iso639_3)
    if cov is None:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": "No cached SRL/frame data; default to Predicate Matrix bridging via English.",
                },
                indent=2,
            )
        )
        return 4

    has_native = cov["framenet"] != "absent" or cov["propbank"] != "absent"
    if has_native:
        approach = "Native SRL / FrameNet resources available — use directly"
    elif cov["via_predicate_matrix"] in ("yes", "indirect"):
        approach = f"No native SRL — use Predicate Matrix bridging via English ({cov['via_predicate_matrix']})"
    else:
        approach = "No SRL infrastructure — fall back to UD parse + manual semantic role inference"

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "framenet": cov["framenet"],
        "propbank": cov["propbank"],
        "srl_tool": cov["srl_tool"],
        "via_predicate_matrix": cov["via_predicate_matrix"],
        "recommended_approach": approach,
        "anti_patterns": [
            "DO NOT use English PropBank frames directly without alignment audit",
            "DO NOT report SRL F1 cross-lingually without specifying alignment scheme",
            "DO NOT assume frames are universal — culture-specific frames absent in low-resource",
        ],
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
