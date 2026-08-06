"""Resolve a language string to canonical {ISO 639-3, Glottolog, family, script}.

Wraps `_linguistic_shared/lang_codes.py` with a CLI surface for the agent.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow running as a standalone script from any cwd
def _linguistic_shared_dir() -> str:
    for _p in Path(__file__).resolve().parents:
        _c = _p / "_linguistic_shared"
        if _c.is_dir():
            return str(_c)
    raise RuntimeError("_linguistic_shared bundle not found — run scripts/sync-linguistic-shared.py")
sys.path.insert(0, _linguistic_shared_dir())
from lang_codes import is_macrolanguage, resolve_language, subtags  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Resolve a language to ISO 639-3 + Glottolog.")
    parser.add_argument("query", help="Language name, ISO code, or alias")
    parser.add_argument("--live", action="store_true", help="(Phase 2+) query Glottolog API directly")
    args = parser.parse_args()

    if args.live:
        print("ERROR: --live is deferred to Phase 2+. Cached snapshot only in Phase 1.", file=sys.stderr)
        return 2

    try:
        rec = resolve_language(args.query)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    out = {
        "iso639_3": rec.iso639_3,
        "glottolog": rec.glottolog,
        "display": rec.display,
        "family": rec.family,
        "script_default": rec.script_default,
        "macrolang": rec.macrolang,
        "notes": rec.notes,
        "is_macrolanguage": is_macrolanguage(args.query),
    }
    if out["is_macrolanguage"]:
        # mypy: out is dict[str, bool|str|None]; subtags-list is wider. Use Any.
        out["subtags"] = [  # type: ignore[assignment]
            {"iso639_3": s.iso639_3, "display": s.display, "glottolog": s.glottolog} for s in subtags(args.query)
        ]
        print(json.dumps(out, indent=2, ensure_ascii=False))
        print(
            f"\nDISAMBIGUATION REQUIRED: {rec.display} is a macrolanguage. Pick a specific subtag before proceeding.",
            file=sys.stderr,
        )
        return 3  # special exit code: needs disambiguation
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
