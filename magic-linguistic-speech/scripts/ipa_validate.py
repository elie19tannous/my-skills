"""Validate an IPA transcription against per-language phoneme inventory.

Phase 1: cached per-language IPA inventory; checks for invalid characters +
flags missing tone marks for tone languages.

`--self-test` mode (added 2026-04-23 per 0011) audits every inventory's
codepoint composition against a declared `orthographic_block` allowlist.
Catches the class of defect that broke Yoruba: silent mixing of orthographic
Latin and IPA codepoints in a single set without explicit declaration.
"""

from __future__ import annotations

import argparse
import json
import sys
import unicodedata
from pathlib import Path

def _linguistic_shared_dir() -> str:
    for _p in Path(__file__).resolve().parents:
        _c = _p / "_linguistic_shared"
        if _c.is_dir():
            return str(_c)
    raise RuntimeError("_linguistic_shared bundle not found — run scripts/sync-linguistic-shared.py")
sys.path.insert(0, _linguistic_shared_dir())
from lang_codes import resolve_language  # noqa: E402

_SELF_TEST_DATE = "2026-04-23"

# Allowed Unicode-block tags for the per-language `orthographic_block` field.
_ALLOWED_ORTHO_BLOCKS: set[str] = {
    "latin_extended",
    "latin_extended_additional",
    "cjk_pinyin_extended",
}

# Always-allowed codepoint blocks for ANY inventory (no orthographic_block needed):
# - ipa_extensions (U+0250-02AF)        IPA proper
# - combining_mark (U+0300-036F)        diacritics, tone marks, length marks
# - basic_latin_lower (U+0061-007A)     a-z (English diphthongs, generic Latin)
# - apostrophe (U+0027)                 conventional IPA notation for ejectives
_ALWAYS_ALLOWED_CLASSES: set[str] = {
    "ipa_extensions",
    "combining_mark",
    "basic_latin_lower",
    "apostrophe",
}

# Cached per-language IPA inventory + tone requirement (snapshot 2026-04-23).
# Per-language `orthographic_block` declares intentional non-IPA codepoint usage.
# Allowed values: see _ALLOWED_ORTHO_BLOCKS above.
# Absence == IPA-only (only _ALWAYS_ALLOWED_CLASSES codepoints permitted).
_IPA_INVENTORY: dict[str, dict] = {
    "eng": {
        "phonemes": set("pbtdkɡfvθðszʃʒhmnŋlɹjwiɪeɛæɑɔoʊuʌəɝɚaeiouːˈˌ"),
        "tone_required": False,
    },
    "yor": {
        # Yoruba phonemes: stops, fricatives, nasals, liquids, glides + 7 oral vowels (i e ɛ a ɔ o u)
        # plus 5 nasal vowels. Includes BOTH IPA forms (ɔ ɛ ʃ ŋ ɲ ɡ) AND Yoruba orthography
        # (ọ ẹ ṣ for ɔ ɛ ʃ) so transcriptions in either system validate.
        "phonemes": set(
            # Consonants (IPA): p b t d k ɡ kp gb f s ʃ h m n ɲ ŋ l r j w
            "pbtdkɡfshmnɲŋlrjw"
            # Yoruba-orthographic consonant equivalents
            "ṣ"
            # 7 base oral vowels (IPA) + Yoruba-orthographic equivalents
            "ieaouɛɔ"
            "ọẹ"
            # Nasal-vowel diacritic combinations are handled via combining marks at runtime
        ),
        "tone_required": True,
        # Combining marks: U+0301 acute (high), U+0300 grave (low); mid is unmarked.
        # U+0304 macron occasionally seen in some literary corpora for mid emphasis.
        "tone_marks": set("́̀̄"),
        "tone_note": "High (combining acute U+0301) / low (combining grave U+0300) / mid (unmarked) — preserve",
        "orthographic_block": "latin_extended_additional",
    },
    "vie": {
        "phonemes": set("pbtdkɡfvszʂʐɕʑhmnɲŋlrwjiɛaɔuáàảãạăâêôơư"),
        "tone_required": True,
        "tone_marks": set("̣́̀̉̃"),  # 5 distinct + bare = 6 tones
        "tone_note": "6-tone system; ALL diacritics semantically meaningful",
        # Vietnamese uses both blocks: most diacritics in U+00C0-024F (latin_extended);
        # underdot vowels (ạ ả) in U+1EA0-1EFF (latin_extended_additional).
        "orthographic_block": ("latin_extended", "latin_extended_additional"),
    },
    "cmn": {
        "phonemes": set("pbtdkɡfsʂɕxmnŋlɹjwiɛaɔuəɤyāáǎàēéěèīíǐìōóǒò"),
        "tone_required": True,
        "tone_marks": set("̄́̌̀"),  # 4 tones in pinyin notation
        "tone_note": "4 tones in pinyin (mā/má/mǎ/mà) plus neutral",
        "orthographic_block": "latin_extended",
    },
    "hau": {
        "phonemes": set("pbtdcɟkɡʔɓɗƙfsʃzhmnɲŋlɽɽrjwieaouīēāōūíéáóú"),
        "tone_required": True,
        "tone_marks": set("́̀"),
        "tone_note": "Hausa: high (acute) / low (grave) — sometimes only low marked",
        "orthographic_block": "latin_extended",
    },
    "ibo": {
        "phonemes": set("pbtdkɡkpgbfsʃvzhmnɲŋlrjwieaouiọụ"),
        "tone_required": True,
        "tone_marks": set("́̀"),
        "tone_note": "High (acute) / low (grave or none); downstep complications",
        "orthographic_block": "latin_extended_additional",
    },
    "twi": {
        "phonemes": set("pbtdkɡfshmnɲŋlrjwiɛaɔuɪʊ"),
        "tone_required": True,
        "tone_marks": set("́̀"),
        "tone_note": "High / low; downstep marked separately",
    },
    "khm": {
        "phonemes": set("pbtdcɟkɡʔɓɗmnɲŋlrjwiɨuoɔaɛeáăâ"),
        "tone_required": False,
        "tone_note": "Register language (no tone); two voice qualities (clear/breathy)",
        "orthographic_block": "latin_extended",
    },
    "tha": {
        "phonemes": set("pbtdkɡʔbdlmnŋjwiɯuoɔɛaeə̄́̌̀̂"),
        "tone_required": True,
        "tone_marks": set("̄́̌̀̂"),
        "tone_note": "5 phonemic tones — preserve diacritics",
    },
    "lao": {
        "phonemes": set("pbtdkɡʔbdlmnŋjwiuɛaɔeoɯāáǎàâ"),
        "tone_required": True,
        "tone_marks": set("̄́̌̀̂"),
        "tone_note": "6 phonemic tones",
        "orthographic_block": "latin_extended",
    },
    "mya": {
        "phonemes": set("pbtdkɡʔbdmnɲŋŋ̊θðszʃhlrjwieaouə"),
        "tone_required": True,
        "tone_note": "3-4 tones depending on analysis",
    },
    "swa": {
        "phonemes": set("pbtdkɡvfszʃhmnɲŋlrjwieaouɛɔ"),
        "tone_required": False,
        "tone_note": "Generally no lexical tone (with limited exceptions)",
    },
    "amh": {
        "phonemes": set("pbtdkɡʔp'ts'tʃ'tʃʤfsʃʒzhmnɲŋlrjwiɨəæaouɛ"),
        "tone_required": False,
        "tone_note": "Stress-based; ejectives marked with apostrophe",
        # Apostrophe (U+0027) is in _ALWAYS_ALLOWED_CLASSES; no orthographic_block needed.
    },
    "arb": {
        # ĭ U+012D, ŭ U+016D — Latin Extended-A short-vowel diacritics for harakat transliteration.
        "phonemes": set("pbtdkɡqʔɣxħʕfsθðzʃʒhmnlrjwiueaĭŭ"),
        "tone_required": False,
        "tone_note": "Vowels often unwritten in orthography; ensure vocalization for G2P",
        "orthographic_block": "latin_extended",
    },
}


# IPA codepoints living OUTSIDE the IPA Extensions block (U+0250-02AF).
# These are conventional IPA characters that Unicode happens to place elsewhere.
_IPA_CONVENTIONAL_OUTSIDE_BLOCK: frozenset[int] = frozenset(
    {
        0x014B,  # ŋ — voiced velar nasal (Latin Extended-A)
        0x00E6,  # æ — near-open front unrounded (Latin-1 Supplement)
        0x00F0,  # ð — voiced dental fricative (Latin-1 Supplement)
        0x03B8,  # θ — voiceless dental fricative (Greek block)
    }
)


def _classify_codepoint(ch: str) -> str:
    """Classify a single codepoint by Unicode block for self-test auditing.

    'ipa_extensions' is used as the bucket for ALL conventional IPA codepoints,
    including those that live outside U+0250-02AF (suprasegmentals U+02B0-02FF
    and named exceptions like ŋ ð θ æ).
    """
    cp = ord(ch)
    if cp in _IPA_CONVENTIONAL_OUTSIDE_BLOCK:
        return "ipa_extensions"
    if 0x0250 <= cp <= 0x02FF:
        # Combines IPA Extensions (U+0250-02AF) + Spacing Modifier Letters
        # (U+02B0-02FF) — both are standard IPA territory (suprasegmentals).
        return "ipa_extensions"
    if 0x0300 <= cp <= 0x036F:
        return "combining_mark"
    if 0x0061 <= cp <= 0x007A:
        return "basic_latin_lower"
    if cp == 0x0027:
        return "apostrophe"
    if 0x1E00 <= cp <= 0x1EFF:
        return "latin_extended_additional"
    if 0x0100 <= cp <= 0x017F:
        return "latin_extended"  # Latin Extended-A
    if 0x0180 <= cp <= 0x024F:
        return "latin_extended"  # Latin Extended-B
    if 0x00C0 <= cp <= 0x00FF:
        return "latin_extended"  # Latin-1 supplement (above ASCII)
    if cp <= 0x007F:
        return "ascii"
    return "other"


def _normalize_declared(declared) -> tuple[str, ...]:
    """Normalize the orthographic_block field to a tuple of block names. Accepts None, str, or iterable."""
    if declared is None:
        return ()
    if isinstance(declared, str):
        return (declared,)
    return tuple(declared)


def _run_self_test() -> dict:
    """Audit every inventory's codepoint composition against orthographic_block declaration."""
    languages: list[dict] = []
    overall_passed = True
    for iso, inv in _IPA_INVENTORY.items():
        declared_raw = inv.get("orthographic_block")
        declared = _normalize_declared(declared_raw)
        bad_decls = [d for d in declared if d not in _ALLOWED_ORTHO_BLOCKS]
        if bad_decls:
            overall_passed = False
            languages.append(
                {
                    "iso": iso,
                    "phoneme_count": len(inv["phonemes"]),
                    "block_breakdown": {},
                    "orthographic_block_declared": declared_raw,
                    "issues": [f"orthographic_block declarations {bad_decls!r} not in {_ALLOWED_ORTHO_BLOCKS}"],
                }
            )
            continue
        breakdown: dict[str, int] = {}
        issues: list[str] = []
        for ch in inv["phonemes"]:
            cls = _classify_codepoint(ch)
            breakdown[cls] = breakdown.get(cls, 0) + 1
            if cls in _ALWAYS_ALLOWED_CLASSES:
                continue
            if cls in declared:
                continue
            # Class not always-allowed AND not declared
            issues.append(
                f"codepoint U+{ord(ch):04X} ({ch!r}) classified as {cls!r} "
                f"but orthographic_block_declared={declared_raw!r}"
            )
        if issues:
            overall_passed = False
        languages.append(
            {
                "iso": iso,
                "phoneme_count": len(inv["phonemes"]),
                "block_breakdown": breakdown,
                "orthographic_block_declared": declared_raw,
                "issues": issues,
            }
        )
    return {
        "snapshot_date": _SELF_TEST_DATE,
        "all_passed": overall_passed,
        "languages": languages,
    }


def validate(ipa: str, lang_iso: str) -> dict:
    """Validate IPA string against per-language inventory."""
    if lang_iso not in _IPA_INVENTORY:
        return {
            "valid": None,
            "warning": f"No cached IPA inventory for {lang_iso}; cannot validate.",
        }

    inv = _IPA_INVENTORY[lang_iso]
    phonemes = inv["phonemes"]
    tone_required = inv["tone_required"]
    tone_marks = inv.get("tone_marks", set())

    # Check for invalid characters: iterate NFC; allow whitespace, stress marks,
    # phonemes (precomposed or base form), and per-language tone marks.
    # Combining tone marks may appear as standalone chars in NFC when no precomposed
    # form exists (e.g., Yoruba "ọ̀" stays as ọ + U+0300 because no precomposed glyph).
    nfc = unicodedata.normalize("NFC", ipa)
    invalid_chars = set()
    for ch in nfc:
        if ch.isspace() or ch in "ˈˌ.[]/()":
            continue
        if ch in tone_marks:
            continue  # combining tone mark — valid for tone-required languages
        # Phoneme check: accept either the precomposed char or its NFD base
        nfd = unicodedata.normalize("NFD", ch)
        base = nfd[0] if nfd else ch
        if ch in phonemes or base in phonemes:
            continue
        invalid_chars.add(ch)

    # Check tone marks present if required
    has_tone_mark = False
    if tone_required:
        nfd_full = unicodedata.normalize("NFD", ipa)
        for ch in nfd_full:
            if ch in tone_marks:
                has_tone_mark = True
                break

    out = {
        "ipa": ipa,
        "language": lang_iso,
        "snapshot_date": "2026-04-23",
        "tone_required": tone_required,
        "tone_marks_present": has_tone_mark if tone_required else None,
        "invalid_characters": sorted(invalid_chars),
        "valid": (not invalid_chars) and (has_tone_mark or not tone_required),
    }
    if tone_required and not has_tone_mark:
        out["warning"] = inv.get("tone_note", "Tone language: tone marks required but missing")
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate IPA transcription against per-language inventory.")
    parser.add_argument("language", nargs="?", help="Language name or ISO 639-3")
    parser.add_argument("ipa", nargs="?", help="IPA transcription string")
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Audit every cached inventory's codepoint composition (no other args).",
    )
    args = parser.parse_args()

    if args.self_test:
        report = _run_self_test()
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["all_passed"] else 1

    if not args.language or not args.ipa:
        parser.error("language and ipa are required (or use --self-test)")

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    result = validate(args.ipa, rec.iso639_3)
    result["language_display"] = rec.display
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result.get("valid") else 1


if __name__ == "__main__":
    sys.exit(main())
