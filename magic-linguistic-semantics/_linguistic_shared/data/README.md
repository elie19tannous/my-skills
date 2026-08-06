# `_linguistic_shared/data/`

Bundled cached data shared across skills. Each file is **date-locked** and refreshed manually; runtime code never fetches over the network.

## `iso_639_3_snapshot.tsv`

SIL ISO 639-3 official current set. Source: <https://iso639-3.sil.org/sites/iso639-3/files/downloads/iso-639-3.tab>.

- Snapshot date: `2026-04-23` (see `# snapshot_date:` header line in the file)
- ~7900 entries; ~178 KB
- Used by: `tests/unit/test_lang_codes_iso_validity.py` to assert every `LangRecord.iso639_3` in `lang_codes.py` exists in the official SIL set
- Refresh policy: **annually**. To refresh:
  1. Download the current TSV from the SIL URL above.
  2. Prepend the three header comment lines (preserve `# snapshot_date: YYYY-MM-DD`, `# source:`, `# refresh policy:`).
  3. Diff against the previous snapshot for unexpected removals (rare but possible when SIL deprecates codes).
  4. Bump `snapshot_date` to today's date.
  5. Run `pytest tests/unit/test_lang_codes_iso_validity.py` — all records still pass.

If SIL deprecates a code that `lang_codes.py` references, the validity test fails on the next pre-merge run; the contributor must either find a replacement code or remove the affected `LangRecord` (and audit downstream callers).
