# Attribution Registry Schema — Reference

Loaded by `magic-linguistic-ethics` whenever a dataset enters the project.

## Why a registry

Attribution and lineage tracking lets you:
- Honor CC-BY attribution requirements at release time.
- Trace SA-propagation obligations through dataset merges.
- Respond to "where did this data come from" audits.
- Process opt-out requests from communities or individuals.
- Re-license downstream models accurately.

Without a registry, attribution is impossible to recover after even a single merge.

## Schema (JSON-Lines, one entry per source dataset)

`workspace_state/attribution_registry.jsonl` — append-only.

```json
{
  "id": "yoruba-masakhane-2024",
  "added_date": "2026-04-23",
  "added_by": "magic-linguistic-corpus",
  "source": {
    "name": "MasakhaNER 2.0 — Yoruba split",
    "url": "https://huggingface.co/datasets/masakhane/masakhaner2",
    "citation": "Adelani, D. I., et al. (2022). MasakhaNER: Named Entity Recognition for African Languages. TACL 10.",
    "version": "v2.0",
    "snapshot_date": "2024-09-15"
  },
  "license": {
    "spdx": "CC-BY-4.0",
    "version": "4.0",
    "url": "https://creativecommons.org/licenses/by/4.0/",
    "attribution_string": "Adelani et al. (2022) — MasakhaNER 2.0",
    "non_commercial": false,
    "share_alike": false,
    "no_derivatives": false
  },
  "fpic": {
    "required": false,
    "rationale": "Community-sourced via Masakhane open contribution; permissive license + community-led release"
  },
  "community": {
    "partner_org": "Masakhane",
    "contact_url": "https://www.masakhane.io/",
    "opt_out_path": "GitHub issue at masakhane/masakhane-ner"
  },
  "lineage": {
    "derived_from": [],
    "merged_with": []
  },
  "use_intent": {
    "training": true,
    "evaluation": true,
    "release_mode": "OPEN",
    "commercial": "to-be-decided"
  },
  "notes": "Standard Yoruba NER; class-2 language. Diacritics preserved (tone language)."
}
```

## Required fields per entry

| Field | Required? | Why |
|---|---|---|
| `id` | YES | Stable identifier |
| `added_date` | YES | When the dataset entered the project |
| `source.name` | YES | Human-readable name |
| `source.url` | YES (or citation) | Where to find / cite |
| `source.version` | YES | Pinning |
| `license.spdx` | YES | SPDX identifier (machine-readable) |
| `license.attribution_string` | YES if CC-BY family | What to put in model card |
| `fpic.required` | YES | YES/NO/UNKNOWN |
| `lineage.derived_from` | YES | List of upstream entry IDs |
| `use_intent.release_mode` | YES | OPEN / COMMUNITY-GATED / RESTRICTED |

Missing any required field → BLOCK on the dataset until filled.

## Lineage tracking on merges

When you merge datasets A + B → C:

```json
{
  "id": "yoruba-merged-train-2026-04-23",
  "added_date": "2026-04-23",
  "added_by": "magic-linguistic-corpus",
  "source": {
    "name": "Yoruba merged training set (2026-04-23)",
    "url": null,
    "citation": "Internal — see lineage"
  },
  "license": {
    "spdx": "CC-BY-SA-4.0",
    "version": "4.0",
    "attribution_string": "...all parents listed in lineage..."
  },
  "lineage": {
    "derived_from": ["yoruba-masakhane-2024", "yoruba-flores-200-v1", "yoruba-bible-nlp-2023"],
    "merged_with": ["yoruba-masakhane-2024", "yoruba-flores-200-v1", "yoruba-bible-nlp-2023"]
  },
  "use_intent": {
    "release_mode": "OPEN"
  },
  "notes": "Bible-NLP triggers most-restrictive=SA; downstream model carries SA obligation."
}
```

The license field on the merged entry MUST be derived from the most-restrictive of all parents. The orchestrator's model-card generator pulls per-parent attribution from the registry.

## Opt-out handling

If a community or individual requests removal of their contribution:

1. Look up the entry by source.
2. Mark the entry with `"opt_out": {"date": "...", "requester": "...", "reason": "..."}`.
3. Identify all derived-from descendants (transitively) via lineage.
4. For each affected model: remove the source from training data; retrain or document the limitation in the model card.
5. Update model card with opt-out record.

The registry makes this possible; without it, you can't trace impact.

## Anti-patterns

- **NEVER** delete entries to "clean up". Append-only.
- **NEVER** modify license fields on existing entries — add a new entry if license clarifies.
- **NEVER** merge datasets without recording lineage.
- **NEVER** skip the registry for "small" datasets. Small datasets often turn out to be community-sensitive.
- **NEVER** store the registry only in code; it should be a data artifact reviewable by non-engineers.

## Tooling (Phase 2+)

A simple Python helper to maintain the registry will ship in Phase 2 (`scripts/registry_add.py`, `registry_audit.py`). Phase 1 is manual JSON-Lines editing — keep entries small and consistent.

## See also

- **SPDX License List**: https://spdx.org/licenses/
- **Carroll, S. R., et al.** (2021). *Operationalizing the CARE and FAIR Principles*. Data Intelligence.
- **Datasheets for Datasets** (Gebru et al. 2021) — broader documentation framework that complements the attribution registry.
