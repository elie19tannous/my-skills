---
name: magic-linguistic-morph
description: 'Morphological analysis for the target language: UniMorph paradigm lookup, SIGMORPHON segmenters, FST/HFST analyzer recommendations, morphology-aware data augmentation. Use whenever the user mentions morphology, morpheme segmentation, UniMorph, SIGMORPHON, FST, foma, HFST, agglutinative / polysynthetic / templatic / fusional, paradigm completion, lemma + features, inflection table, morpheme-aware tokenization, or asks why an English-tokenizer-trained model produces ridiculous Turkish/Finnish/Inuktitut/Arabic output. **Use whenever the target language is not Latin/Cyrillic-fusional** — agglutinative + polysynthetic + templatic morphology routinely needs targeted treatment beyond what BPE provides. Routed by magic-linguistic-orchestrator in the Analyze phase.'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 3
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - morphology
  - unimorph
  - sigmorphon
  - fst
  - low-resource
  dependencies: []
  scripts:
  - scripts/paradigm_lookup.py
  - scripts/segmenter_recommend.py
---

## When to Use

- Target language is morphologically complex (agglutinative, polysynthetic, templatic, fusional with rich case).
- Tokenizer fertility audit (`magic-linguistic-tokenize`) shows morpheme-tokenization gap.
- Building gold morphological annotations.
- Augmenting small training data via paradigm completion.
- Choosing between UniMorph paradigms vs ML segmenter vs FST analyzer.

**When NOT to use:** Latin/Cyrillic fusional language with low morphology (English, Spanish, German default fine-tune is enough). Pure tokenizer audit → `magic-linguistic-tokenize`.

## The Knowledge Engineers Routinely Miss

1. **Tokenizer fertility ≠ morphological complexity.** Fertility says "BPE produces too many tokens"; morphology tells you WHY (concatenative vs templatic vs fusional vs polysynthetic). Different mechanisms need different fixes.

2. **UniMorph covers 100+ languages with gold paradigms** — but coverage varies wildly. Turkish/Finnish/Russian deeply covered; Yoruba/Khmer thinly covered; many class 0-1 absent. ALWAYS check before assuming you need self-supervised segmentation.

3. **SIGMORPHON 2022/2023 segmenters** are SOTA for unsupervised morpheme segmentation. Use them, NOT BPE-as-segmenter. BPE is a compression algorithm; it doesn't respect morpheme boundaries.

4. **HFST/foma rule-based FSTs beat ML segmenters when good rules exist** — common case for endangered languages where field linguists have built rules. Look in DELAMAN archives.

5. **Templatic morphology (Arabic, Hebrew, Amharic, Akkadian) needs root-pattern treatment**, not concatenative segmenters. Morpheme-segmenters trained on agglutinative languages produce nonsense for Arabic.

6. **Polysynthesis (Inuktitut, Navajo, Mohawk) compresses sentence-meaning into one word**. Morpheme segmentation is essential — a word can have 8-20+ morphemes. Tokenizer-only will not work.

7. **Paradigm completion as augmentation**: given lemma + features + small paradigm sample, generate inflected forms. 10× small training corpora cheaply. Works extremely well for agglutinative class 1-2.

## Morphology Tier Classification

Per target language, classify into one of four tiers:

| Tier | Examples | Implications |
|---|---|---|
| **lo** (low) | English, Mandarin, Vietnamese, Indonesian | Standard tokenizer fine; morph skill rarely needed |
| **mid** (moderate) | Spanish, French, Russian, Modern Greek | Some inflection; check fertility; BPE usually OK |
| **hi** (high) | Turkish, Finnish, Hungarian, Korean, Tamil, Swahili (Bantu noun class), Arabic (templatic), Hebrew (templatic) | Morphology-aware tokenization helps; UniMorph if available |
| **extreme** (polysynthetic) | Inuktitut, Navajo, Mohawk, West Greenlandic, Cherokee | Morpheme segmentation MANDATORY; UniMorph if available; FST critical |

## Workflow

### Step 1 — Classify morphology tier

**MANDATORY READ** [`references/unimorph_paradigms.md`](references/unimorph_paradigms.md) before recommending paradigms.

Use `scripts/paradigm_lookup.py` to:
- Identify tier (lo/mid/hi/extreme).
- Look up UniMorph + SIGMORPHON coverage for the target.
- Surface known FST analyzers (HFST/foma).

### Step 2 — Decide approach

| Tier | UniMorph available | Recommended approach |
|---|---|---|
| lo / mid | any | Skip morph skill; BPE handles it |
| hi | YES (good coverage) | UniMorph paradigms + paradigm-completion augmentation |
| hi | NO | SIGMORPHON 2022/2023 segmenter + tokenizer audit |
| hi (templatic) | any | Root-pattern handler (root extractor + template applier) — special tooling needed |
| extreme | YES | UniMorph + FST (HFST/foma) + segmenter for OOV |
| extreme | NO | SIGMORPHON segmenter + community-collected paradigm samples |

### Step 3 — Segmenter recommendation

**MANDATORY READ** [`references/sigmorphon_segmenters.md`](references/sigmorphon_segmenters.md).

Use `scripts/segmenter_recommend.py`:

| Family | Recommended segmenter |
|---|---|
| Agglutinative (Turkic, Uralic, Bantu, Korean) | SIGMORPHON 2023 winners; Morfessor as fallback |
| Polysynthetic (Eskimo, Athabaskan, Iroquoian) | UniMorph + FST if available; otherwise SIGMORPHON 2023 |
| Templatic (Semitic) | Custom root-pattern; do NOT use concatenative segmenters |
| Fusional with case (Slavic, Greek, Sanskrit) | Morfessor or stanza's morphology |

### Step 4 — FST analyzer (when applicable)

**MANDATORY READ** [`references/fst_analyzers.md`](references/fst_analyzers.md).

For languages with documented FSTs:
- HFST: open-source toolkit; ~50 languages with available analyzers.
- foma: alternative; smaller user base but easier syntax.
- Check Apertium repos (https://github.com/apertium) for many under-resourced languages.

When no FST exists: don't build one from scratch unless field-linguist partnership; SIGMORPHON segmenter is faster path.

### Step 5 — Augmentation via paradigm completion

**MANDATORY READ** [`references/morphology_aware_augmentation.md`](references/morphology_aware_augmentation.md).

For class 1-2 agglutinative targets:
1. Pull UniMorph paradigms for target.
2. For each lemma in training corpus, generate 10-30 inflected forms via paradigm.
3. Add as augmented training data with `<morph_aug>` tag.
4. Typical gain: 1-3 BLEU on MT, 2-5% on POS/NER.

### Step 6 — Output morphology plan + hand off

```markdown
## Morphology Plan: <Language>

**Tier:** lo | mid | hi | extreme
**UniMorph coverage:** <available paradigms / total estimate>
**SIGMORPHON segmenter:** <name> | not applicable
**FST analyzer:** <HFST X> | none available
**Augmentation strategy:** paradigm completion <X×> | none
**Hand-off:** magic-linguistic-tokenize for fertility re-audit; magic-linguistic-syntax for morphology-aware parsing
```

## Anti-patterns (NEVER do)

- **NEVER** assume BPE handles agglutinative morphology by itself. Fertility audit → vocab extension is partial; morph segmentation closes the rest.
- **NEVER** ignore UniMorph if it covers the target. Gold paradigms beat any self-supervised method.
- **NEVER** use English-trained / concatenative segmenter for templatic Arabic/Hebrew/Amharic. The root-pattern is non-concatenative; concatenative breaks it.
- **NEVER** build an FST from scratch without field-linguist partnership. Multi-month effort; SIGMORPHON segmenter is faster path for ML-only purposes.
- **NEVER** generate paradigm-completed forms without `<morph_aug>` tag. Model can't learn to weight synthetic vs natural.
- **NEVER** treat polysynthetic-target word boundaries as your training input granularity. Words need decomposition.
- **NEVER** report morphology tier without showing the criteria — a future maintainer needs the rationale.

## Edge Cases

- **Macrolanguage with mixed morphology** (Quechua dialects vary): per-subtag classification.
- **Mixed-language code-switched corpus** (Hinglish): per-language morphology; tokenizer must handle both.
- **Reduplication-heavy languages** (Indonesian, Hawaiian, Tagalog): paradigm completion may double-count; flag in augmentation.
- **Honorifics drive verb morphology** (Japanese, Korean): paradigm tables grow; sample by register.
- **Non-Unicode legacy SIL fonts in field FST** (Apertium repos): convert PUA → Unicode before integrating.

## Output Format

```markdown
## Morphology Analysis: <Language>

**Morphology tier:** lo | mid | hi | extreme — rationale: ...
**Family-specific concerns:** <e.g., templatic non-concatenative; polysynthetic chains; Bantu noun classes>
**UniMorph status:** ~N paradigms available / link
**SIGMORPHON segmenter recommendation:** <name + version>
**FST analyzer:** <HFST/foma module URL or "none">
**Augmentation strategy:** <paradigm completion ×N | rule-based | none>
**Cross-skill cooperation:**
  - magic-linguistic-tokenize: re-audit fertility after morph-aware tokenization
  - magic-linguistic-syntax: morphology-aware parser inputs
**Anti-patterns to avoid for this target:** <e.g., do not concatenative-segment Arabic>
```
