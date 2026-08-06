---
name: magic-linguistic-scope
description: Identify a target language precisely and set the strategic direction for any LLM/NLP project on it. Use whenever the user mentions a non-English language by name, asks 'what should I do for [language]', mentions resource class / Joshi / Glottolog / WALS / Grambank / URIEL / typology / transfer source / language vitality, or whenever a workflow needs ISO 639-3 + Glottolog disambiguation. **You should also use this skill whenever the user names a language that is potentially a macrolanguage (Chinese, Arabic, Pashto, Quechua, Sami) — disambiguating early prevents weeks of wasted work.** Routed first by magic-linguistic-orchestrator at the start of every Scope phase.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - language-identification
  - typology
  - low-resource
  - scope
  dependencies: []
  scripts:
  - scripts/language_lookup.py
  - scripts/resource_classifier.py
  - scripts/uriel_distance.py
---

## When to Use

- User names a target language for any NLP/LLM project.
- Workflow needs ISO 639-3 + Glottolog identity before touching data.
- Resource-class assessment (Joshi 0-5) is required to pick a strategy.
- Choosing a transfer source (which related language to bootstrap from).
- Determining vitality status (does this need community engagement?).

**When NOT to use:** the language is already disambiguated, classified, and typology-vector is already in `workspace_state.md` — proceed to the next specialist.

## Thinking Framework — before any data, model, or eval decision

Ask yourself, in order:

1. **What is this language, exactly?** Not "Chinese" — Mandarin (cmn), Cantonese (yue), Wu (wuu), or one of ~20 others. Not "Arabic" — MSA (arb), Egyptian (arz), Levantine (apc), Maghrebi (ary). Macrolanguages silently destroy weeks of work when conflated.
2. **What resource class is it?** Joshi 0-5 changes EVERY downstream choice — tokenizer, eval suite, transfer source, ethics depth.
3. **What's its typological profile?** Word order, morphology type, agreement, tone. These predict what models will get wrong before you measure it.
4. **What's the best transfer source?** Not always English. Often a typologically-closer high-resource language gives 2-5× the transfer gain.
5. **Is the community engaged?** Vitality status (UNESCO/EGIDS) gates how much community involvement is required.

## Workflow

### Step 1 — Disambiguate the language

**MANDATORY READ** [`references/typological_databases.md`](references/typological_databases.md) when the query is unfamiliar.

Use `scripts/language_lookup.py` to resolve the input string to canonical {ISO 639-3, Glottolog ID, family, default script}.

If the result is a **macrolanguage** (e.g., zho, ara, pus, que, smi):
- STOP and present subtags as numbered options.
- Do NOT proceed until the user confirms a specific variant.
- Document the disambiguation in `workspace_state.md`.

If the result is unresolvable: ask the user for ISO 639-3 / Glottolog ID directly.

### Step 2 — Classify resource availability

**MANDATORY READ** [`references/resource_classification.md`](references/resource_classification.md) before assigning a class.

Use `scripts/resource_classifier.py` to compute the Joshi 0-5 class from cached signals (Wikipedia presence, OPUS presence, FLORES-200 inclusion, NLLB inclusion, dataset count on HuggingFace).

| Class | Meaning | Examples | Typical strategy |
|---|---|---|---|
| 0 | "The Left-Behinds" — no labelled data | Dahalo, Yagua | Bootstrap from related language; field documentation |
| 1 | "The Scraping-Bys" — Wiki dump exists | Marathi (low end), Igbo | Continued pretraining + adapter |
| 2 | "Hopefuls" — some labelled, no benchmarks | Yoruba, Khmer, Twi | Vocab extension + LoRA |
| 3 | "Rising Stars" — multiple benchmarks | Swahili, Indonesian (low end) | Standard fine-tune + careful eval |
| 4 | "Underdogs" — many benchmarks | Vietnamese, Turkish, Tamil | Standard fine-tune |
| 5 | "Winners" — benchmark-saturated | English, Mandarin, Spanish | Standard everything |

Record the class in `workspace_state.md` under "Targets > Resource class (Joshi)".

### Step 3 — Pull typological profile

**MANDATORY READ** [`references/typological_databases.md`](references/typological_databases.md) for WALS/Grambank/URIEL coverage gaps.

Look up the URIEL feature vector (or WALS subset) for the target. Surface the **outlier features** that require targeted handling:

- **Polysynthesis** (Inuktitut, Navajo) → expect tokenizer fertility 4-7×; vocab extension mandatory.
- **Tone** (Yoruba, Vietnamese, Hausa, Mandarin) → diacritic preservation is non-negotiable; G2P needed.
- **Agglutination** (Turkish, Finnish, Swahili) → fertility 2-4×; morpheme-aware augmentation helps.
- **Root-and-pattern** (Arabic, Hebrew) → BPE captures roots poorly; treat with morphological pre-processing.
- **Evidentiality** (Quechua, Tibetan) → translation systems silently drop; eval needs targeted probes.
- **Classifier system** (Mandarin, Thai) → numeral handling is fragile.
- **Switch reference** (many Indigenous Americas) → coreference systems will fail.

### Step 4 — Recommend a transfer source

**MANDATORY READ** [`references/transfer_source_selection.md`](references/transfer_source_selection.md) for URIEL distance methodology.

Use `scripts/uriel_distance.py` to compute typological distance to top-100 candidate sources. Recommend top-3 with bounded justifications:

```
Top transfer-source candidates for Yoruba (yor):
1. Igbo (ibo) — distance 0.18 — same family branch + tone + Latin script + Class 1 data
2. Hausa (hau) — distance 0.34 — regional contact + Class 2 data + tone (different family)
3. Swahili (swa) — distance 0.41 — same family > Bantu + Class 3 data + Latin script
English distance 0.62 — typologically distant; NOT recommended as primary source.
```

If no candidate has distance < 0.6: flag transfer is **unsafe**; recommend vocab extension + LoRA from a multilingual base (mBART, NLLB, BLOOM) instead of continued pretraining from a single-source.

### Step 5 — Vitality assessment

Look up UNESCO/EGIDS vitality status for the target. Gate ethics-engagement depth:

| EGIDS | Status | Ethics depth required |
|---|---|---|
| 0-3 | International / National / Provincial | Standard FPIC + license check |
| 4-6a | Educational / Wider Communication / Vigorous | Standard FPIC |
| 6b-7 | Threatened / Shifting | Mandatory community pre-engagement; route to `magic-linguistic-ethics` BEFORE any data acquisition |
| 8a-10 | Moribund / Nearly Extinct / Dormant / Extinct | Archive-only; route to DELAMAN/ELAR; FPIC from descendant community |

### Step 6 — Update workspace_state.md and hand off

Write the structured scope record (see Output Format below) to `workspace_state.md`. Notify the orchestrator that scope is complete and recommend next phase (typically `magic-linguistic-scripts` for normalization policy, then `magic-linguistic-corpus` or `magic-linguistic-bitext`).

## Output Format

```markdown
## Scope: <Language Name>

- **ISO 639-3**: <code>
- **Glottolog**: <id>
- **Family**: <family path>
- **Default script(s)**: <Unicode block name(s)>
- **Resource class (Joshi 0-5)**: <n> — <interpretation>
- **Vitality (EGIDS)**: <code> — <ethics-depth implication>
- **Typological outliers**: <comma-separated features>
- **Top transfer source(s)**: 1) <lang> (URIEL=<x>); 2) ...; 3) ...
- **Strategic recommendation**: <2-3 sentence summary>
```

## Anti-patterns (NEVER do)

- **NEVER** skip ISO 639-3 + Glottolog resolution. Naming a language by display name only ("Pashto", "Chinese", "Sami") loses critical information.
- **NEVER** assume English is a good transfer source without computing URIEL distance. Typologically-distant pairs (English→Basque, English→Mandarin syntax-tagging) underperform 2-5× vs typologically-close pairs.
- **NEVER** treat macrolanguages as monolithic. "Train a Chinese model" without specifying Mandarin vs Cantonese is a real cost in production.
- **NEVER** recommend Joshi-class-based workflows without showing the class number — the recipient may disagree with your classification, and the heuristics should be transparent.
- **NEVER** classify a language as Class 5 (English-like) just because Wikipedia is large. Class is multi-dimensional (data + benchmarks + tooling).
- **NEVER** present typology vectors as deterministic predictions. URIEL distances are *heuristics* — they predict transfer success but with high variance; always note uncertainty.
- **NEVER** skip vitality assessment. Endangered-language work without community engagement is harm regardless of intent.

## Edge Cases

- **Language has no Glottolog ID** (extinct or recently documented): use ISO 639-3 + family path; flag for `magic-linguistic-ethics` review.
- **User wants to train on multiple languages simultaneously** (multilingual model): run scope for each, surface joint typological diversity, recommend sampling-weight strategy in handoff to `magic-linguistic-transfer`.
- **Cached snapshot is stale** (script reports last-update date > 12 months): warn user, recommend `--live` flag (Phase 2+); proceed with cached for now.
- **Resource class assessment ambiguous** (Wikipedia exists but no labelled benchmarks): present range (e.g., "Class 1-2") with the deciding factor; defer to user.
- **Language is a constructed language** (Esperanto, Klingon, toki pona): note this; user may proceed but linguist-typology heuristics may not apply.
