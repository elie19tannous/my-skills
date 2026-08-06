"""Recommend Lhotse ingest recipe + ASR/TTS approach for a target language.

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

_INPUT_FORMAT_RECIPES: dict[str, dict] = {
    "elan_eaf": {
        "preprocessing": ["Standardize tier names per project", "Convert any SIL PUA chars to Unicode"],
        "lhotse_recipe": "Custom: parse EAF XML → SupervisionSegment per annotation; pair with linked WAV",
        "stub_available": "references/lhotse_pipeline.md (recipe stub 2)",
    },
    "praat_textgrid": {
        "preprocessing": ["Verify interval-tier vs point-tier per use", "Encoding: usually UTF-8 OK"],
        "lhotse_recipe": "Use lhotse.kaldi.load_kaldi_data_dir if available; else custom TextGrid → SupervisionSegment",
        "stub_available": "Custom (no shipped stub)",
    },
    "flex_xml": {
        "preprocessing": ["MANDATORY: PUA → Unicode (SIL legacy fonts)", "Extract IGT to JSONL or CoNLL-U"],
        "lhotse_recipe": "Two-stage: FLEx XML → JSONL → Lhotse SupervisionSegment",
        "stub_available": "Custom (no shipped stub; LingView export for IGT)",
    },
    "saymore_imdi": {
        "preprocessing": ["Extract underlying ELAN/audio from IMDI package", "Map IMDI metadata → Lhotse cut metadata"],
        "lhotse_recipe": "Two-stage: SayMore → ELAN → Lhotse",
        "stub_available": "Custom",
    },
    "custom_csv": {
        "preprocessing": ["Validate timestamp format", "Validate encoding (UTF-8)"],
        "lhotse_recipe": "lhotse.cut.from_csv() if simple format",
        "stub_available": "n/a",
    },
}


_ASR_TTS_PER_CLASS: dict[int, dict] = {
    0: {
        "asr_primary": "MMS (1107-lang coverage)",
        "asr_fallback": "Community-collected audio + custom train",
        "tts": "NOT VIABLE (< 1 hr audio); consider speaker-adaptation or community recording effort",
    },
    1: {
        "asr_primary": "MMS direct",
        "asr_fallback": "Whisper-large fine-tune if audio exists",
        "tts": "MMS-TTS or marginal VITS fine-tune (~1-5 hr); intelligible but unnatural",
    },
    2: {
        "asr_primary": "MMS direct OR Whisper-large fine-tune",
        "asr_fallback": "Custom wav2vec",
        "tts": "VITS or FastSpeech2 fine-tune (≥ 5 hr); usable quality",
    },
    3: {
        "asr_primary": "Whisper-large fine-tune OR MMS",
        "asr_fallback": "Custom NeMo / ESPnet",
        "tts": "VITS or FastSpeech2 (≥ 10 hr); high quality",
    },
    4: {
        "asr_primary": "Whisper-large or commercial",
        "asr_fallback": "NeMo, ESPnet",
        "tts": "VITS or commercial; production quality",
    },
    5: {
        "asr_primary": "Whisper-large or commercial",
        "asr_fallback": "n/a",
        "tts": "Commercial best; VITS if open-source needed",
    },
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Lhotse recipe + ASR/TTS advisor for speech projects.")
    parser.add_argument("language", help="Language name or ISO 639-3")
    parser.add_argument(
        "--input-format", required=True, choices=list(_INPUT_FORMAT_RECIPES.keys()), help="Source annotation format"
    )
    parser.add_argument("--joshi-class", type=int, default=2, help="Joshi class of target")
    parser.add_argument("--audio-hours", type=float, default=None, help="Available audio hours (for TTS feasibility)")
    args = parser.parse_args()

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    fmt = _INPUT_FORMAT_RECIPES[args.input_format]
    cls = _ASR_TTS_PER_CLASS.get(args.joshi_class, _ASR_TTS_PER_CLASS[2])

    # Tone-language preservation flag
    tone_languages = {"yor", "vie", "cmn", "hau", "ibo", "twi", "tha", "lao", "mya", "yue"}
    is_tone = rec.iso639_3 in tone_languages

    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "input_format": args.input_format,
        "snapshot_date": "2026-04-23",
        "preprocessing_required": fmt["preprocessing"],
        "lhotse_recipe": fmt["lhotse_recipe"],
        "stub_available": fmt["stub_available"],
        "asr_recommendation": {
            "primary": cls["asr_primary"],
            "fallback": cls["asr_fallback"],
        },
        "tts_recommendation": cls["tts"],
        "tone_language": is_tone,
        "tone_preservation_required": is_tone,
        "anti_patterns": [
            "DO NOT strip diacritics in transcription pipeline (tone language)" if is_tone else None,
            "DO NOT ingest FLEx XML without PUA → Unicode normalization" if args.input_format == "flex_xml" else None,
            "DO NOT use Whisper for class 0-1 — MMS coverage broader" if args.joshi_class <= 1 else None,
            "DO NOT train TTS on < 1 hour audio (unusable)"
            if args.audio_hours is not None and args.audio_hours < 1
            else None,
        ],
        "next_step": "Route to magic-linguistic-ethics if community-controlled; magic-linguistic-eval for ASR/TTS metrics",
    }
    out["anti_patterns"] = [a for a in out["anti_patterns"] if a]
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
