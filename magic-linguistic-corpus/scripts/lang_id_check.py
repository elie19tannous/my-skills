"""Look up cached corpus catalog coverage for a target language.

Phase 1: cached snapshot (2026-04-23) lookups only. --live (real LID model run)
deferred to Phase 2+.
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

# Cached corpus coverage per ISO 639-3 (snapshot 2026-04-23).
# Format: {iso: [{catalog, est_size_tokens, license, register_skew, notes}, ...]}
_CATALOG: dict[str, list[dict]] = {
    "yor": [
        {
            "catalog": "MADLAD-400",
            "est_size_tokens": 30_000_000,
            "license": "per-source",
            "register_skew": "web-dominated",
            "notes": "Class 2 baseline",
        },
        {
            "catalog": "CulturaX",
            "est_size_tokens": 25_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "overlaps MADLAD heavily",
        },
        {
            "catalog": "Glot500-c",
            "est_size_tokens": 60_000_000,
            "license": "per-source",
            "register_skew": "Bible 50%+",
            "notes": "high Bible %",
        },
        {
            "catalog": "Wikipedia (yor)",
            "est_size_tokens": 10_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "Class 2; quality OK",
        },
        {
            "catalog": "MasakhaNER 2.0",
            "est_size_tokens": 500_000,
            "license": "CC-BY-4.0",
            "register_skew": "news",
            "notes": "Labeled NER + monolingual",
        },
        {
            "catalog": "AfroLM corpus",
            "est_size_tokens": 8_000_000,
            "license": "per-source",
            "register_skew": "mixed",
            "notes": "Community-led",
        },
        {
            "catalog": "Bible-NLP (yor)",
            "est_size_tokens": 1_500_000,
            "license": "open per-translation",
            "register_skew": "liturgical",
            "notes": "ALWAYS flag % in mix",
        },
    ],
    "khm": [
        {
            "catalog": "MADLAD-400",
            "est_size_tokens": 800_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "Class 2-3",
        },
        {
            "catalog": "CulturaX",
            "est_size_tokens": 600_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "overlaps MADLAD",
        },
        {
            "catalog": "Wikipedia (km)",
            "est_size_tokens": 18_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "",
        },
        {
            "catalog": "SEACrowd",
            "est_size_tokens": 50_000_000,
            "license": "per-source",
            "register_skew": "mixed",
            "notes": "Curated",
        },
        {
            "catalog": "Bible-NLP (khm)",
            "est_size_tokens": 1_200_000,
            "license": "open",
            "register_skew": "liturgical",
            "notes": "",
        },
    ],
    "iku": [
        {
            "catalog": "Wikipedia (iku)",
            "est_size_tokens": 200_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "Tiny",
        },
        {
            "catalog": "NWT Hansard EN-IU",
            "est_size_tokens": 8_000_000,
            "license": "per-source",
            "register_skew": "parliamentary",
            "notes": "Major source; very narrow domain",
        },
        {
            "catalog": "AILLA archive",
            "est_size_tokens": "varies",
            "license": "community-gated",
            "register_skew": "field recordings",
            "notes": "FPIC required",
        },
        {
            "catalog": "Bible-NLP (iku)",
            "est_size_tokens": 800_000,
            "license": "open",
            "register_skew": "liturgical",
            "notes": "Often only general text",
        },
    ],
    "que": [
        {
            "catalog": "AmericasNLP shared task data",
            "est_size_tokens": 2_000_000,
            "license": "per-source",
            "register_skew": "mixed",
            "notes": "Macrolang — disambiguate first",
        },
        {
            "catalog": "Wikipedia (qu)",
            "est_size_tokens": 7_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "Macrolang Wiki",
        },
        {
            "catalog": "AILLA archive",
            "est_size_tokens": "varies",
            "license": "community-gated",
            "register_skew": "field",
            "notes": "FPIC required",
        },
    ],
    "yue": [
        {
            "catalog": "Wikipedia (yue)",
            "est_size_tokens": 8_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "Many entries actually written-Mandarin — audit",
        },
        {
            "catalog": "LIHKG (community-scraped)",
            "est_size_tokens": 50_000_000,
            "license": "uncertain",
            "register_skew": "internet forum",
            "notes": "License audit critical",
        },
        {
            "catalog": "Common Crawl HK subset",
            "est_size_tokens": 200_000_000,
            "license": "per-page",
            "register_skew": "web",
            "notes": "Heavy Mandarin contamination",
        },
    ],
    "swa": [
        {
            "catalog": "MADLAD-400",
            "est_size_tokens": 1_500_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "Class 3 baseline",
        },
        {
            "catalog": "CulturaX",
            "est_size_tokens": 1_200_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "overlaps MADLAD",
        },
        {
            "catalog": "Wikipedia (sw)",
            "est_size_tokens": 60_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "",
        },
        {
            "catalog": "MasakhaNER",
            "est_size_tokens": 800_000,
            "license": "CC-BY",
            "register_skew": "news",
            "notes": "Labeled",
        },
    ],
    "twi": [
        {
            "catalog": "MADLAD-400",
            "est_size_tokens": 12_000_000,
            "license": "per-source",
            "register_skew": "web",
            "notes": "Class 1-2",
        },
        {
            "catalog": "AfroLM",
            "est_size_tokens": 5_000_000,
            "license": "per-source",
            "register_skew": "mixed",
            "notes": "",
        },
        {
            "catalog": "Bible-NLP (twi)",
            "est_size_tokens": 1_400_000,
            "license": "open",
            "register_skew": "liturgical",
            "notes": "",
        },
    ],
    "mri": [
        {
            "catalog": "Wikipedia (mi)",
            "est_size_tokens": 2_000_000,
            "license": "CC-BY-SA",
            "register_skew": "encyclopedic",
            "notes": "",
        },
        {
            "catalog": "Te Hiku Media (community-gated)",
            "est_size_tokens": "varies",
            "license": "Kaitiakitanga",
            "register_skew": "spoken/oral",
            "notes": "Community partnership required",
        },
    ],
}


def main() -> int:
    parser = argparse.ArgumentParser(description="List cached corpus catalog coverage for a language.")
    parser.add_argument("language", help="Language name or ISO 639-3 code")
    parser.add_argument("--live", action="store_true", help="(Phase 2+) probe live LID + corpus catalogs")
    args = parser.parse_args()

    if args.live:
        print("ERROR: --live deferred to Phase 2+. Cached snapshot only.", file=sys.stderr)
        return 2

    try:
        rec = resolve_language(args.language)
    except KeyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1

    catalogs = _CATALOG.get(rec.iso639_3, [])
    if not catalogs:
        print(
            json.dumps(
                {
                    "language": rec.display,
                    "iso639_3": rec.iso639_3,
                    "warning": f"No cached catalog data for {rec.iso639_3}; consult magic-linguistic-corpus references for general guidance.",  # noqa: E501  # long anti-pattern string
                },
                indent=2,
            )
        )
        return 4

    bible_pct = sum(
        1 for c in catalogs if "Bible" in c.get("catalog", "") or "liturgical" in c.get("register_skew", "")
    )
    out = {
        "language": rec.display,
        "iso639_3": rec.iso639_3,
        "snapshot_date": "2026-04-23",
        "n_candidate_catalogs": len(catalogs),
        "catalogs": catalogs,
        "ethics_routing_required": True,
        "register_balance_warning": (
            f"{bible_pct} of {len(catalogs)} entries are Bible/liturgical — "
            "flag % in final manifest if Bible > 30% of total mix"
        )
        if bible_pct >= 1
        else None,
        "next_step": "route each catalog through magic-linguistic-ethics for license + CARE check before adding to mix",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
