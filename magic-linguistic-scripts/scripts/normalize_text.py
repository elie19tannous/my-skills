"""Apply Unicode normalization with policy guard.

Defaults to NFC (safe). NFKC requires --form=NFKC AND --i-understand-nfkc-is-destructive
to make the destructive choice explicit at call time.

Detects and warns on:
- BOM (UTF-8 BOM at file start).
- Mojibake patterns ("Ã©", "Ã¢", "â€™" — common latin-1 → utf-8 mis-decode).
- Mixed forms in input (some NFC, some NFD code points).
"""

from __future__ import annotations

import argparse
import sys
import unicodedata
from typing import Literal, cast

_BOM = "﻿"
_MOJIBAKE_HINTS = ("Ã©", "Ã¢", "â€™", "â€œ", "â€\x9d", "Â", "â€“", "â€”")


def detect_issues(text: str) -> list[str]:
    issues = []
    if text.startswith(_BOM):
        issues.append("BOM (U+FEFF) at start — strip with .lstrip('\\ufeff') or open with utf-8-sig")
    for hint in _MOJIBAKE_HINTS:
        if hint in text:
            issues.append(f"Mojibake pattern detected: {hint!r} (likely latin-1 → utf-8 mis-decode)")
            break
    # Mixed-form check: NFC of NFD-form != NFD-form
    nfc = unicodedata.normalize("NFC", text)
    nfd = unicodedata.normalize("NFD", text)
    if text != nfc and text != nfd:
        issues.append("Input has mixed normalization forms (some NFC, some NFD)")
    return issues


def normalize(text: str, form: str) -> str:
    # argparse upstream constrains `form` to {NFC, NFD, NFKC, NFKD} via choices=;
    # `cast` documents that for mypy.
    return unicodedata.normalize(cast(Literal["NFC", "NFD", "NFKC", "NFKD"], form), text)


def main() -> int:
    parser = argparse.ArgumentParser(description="Normalize text with policy guard. NFC is the safe default.")
    parser.add_argument("input", help="Path to input file or '-' for stdin")
    parser.add_argument("-o", "--output", default="-", help="Output path or '-' for stdout")
    parser.add_argument("--form", default="NFC", choices=["NFC", "NFD", "NFKC", "NFKD"])
    parser.add_argument(
        "--strip-bom",
        action="store_true",
        help="Strip UTF-8 BOM (U+FEFF) at start if present",
    )
    parser.add_argument(
        "--i-understand-nfkc-is-destructive",
        action="store_true",
        help="REQUIRED to use NFKC or NFKD. Confirms operator knows long-s, ligatures, fullwidth, "
        "Arabic presentation forms, and other compatibility characters will be irreversibly collapsed.",
    )
    parser.add_argument(
        "--report-only",
        action="store_true",
        help="Detect issues only; do not transform",
    )
    args = parser.parse_args()

    if args.form in ("NFKC", "NFKD") and not args.i_understand_nfkc_is_destructive:
        print(
            f"ERROR: --form={args.form} is destructive. "
            "It collapses long-s, ligatures, fullwidth, Arabic presentation forms, and more. "
            "Re-run with --i-understand-nfkc-is-destructive to confirm intent.",
            file=sys.stderr,
        )
        return 2

    raw = (
        sys.stdin.read()
        if args.input == "-"
        else open(args.input, encoding="utf-8-sig" if args.strip_bom else "utf-8").read()
    )

    issues = detect_issues(raw)
    if issues:
        print("[WARN] Pre-normalization issues:", file=sys.stderr)
        for i in issues:
            print(f"  - {i}", file=sys.stderr)

    if args.report_only:
        return 0 if not issues else 1

    if args.strip_bom and raw.startswith(_BOM):
        raw = raw[len(_BOM) :]

    out = normalize(raw, args.form)
    if args.output == "-":
        sys.stdout.write(out)
    else:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
