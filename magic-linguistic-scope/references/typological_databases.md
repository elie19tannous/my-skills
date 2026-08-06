# Typological Databases — Reference

Loaded by `magic-linguistic-scope` when the workflow needs typological depth (Step 1 + Step 3).

## The three canonical databases

| Database | Coverage | Best for | URL |
|---|---|---|---|
| **WALS** (World Atlas of Language Structures) | ~2,679 languages, 192 features | Hand-curated typology, classic reference | https://wals.info/ |
| **Grambank** | ~2,400 languages, 195 features (denser per-language than WALS) | Computational use; better completeness per language | https://grambank.clld.org/ |
| **URIEL + lang2vec** | ~3,800 languages, ~289 features (binary + valued) | Distance metrics for transfer learning | http://www.cs.cmu.edu/~dmortens/uriel.html |

**Default for transfer-source selection**: URIEL (because it's optimised for distance metrics).
**Default for typological description**: Grambank (denser coverage; recent publication 2023).
**Default for citation in proposals**: WALS (canonical, peer-reviewed).

## URIEL feature classes

URIEL groups features into 5 classes; distance metrics weight them differently per task:

| Class | Examples | Use for |
|---|---|---|
| **Syntactic** | word order (S/V/O), case alignment, head-marking | parser transfer, MT |
| **Phonological** | vowel inventory, tone, stress | TTS/ASR transfer |
| **Phonetic** | place/manner of articulation features | phoneme inventory design |
| **Inventory** | presence of specific phonemes | G2P |
| **Family** | genetic-tree distance | sanity check |

For LLM transfer source selection, weight syntactic + family equally (both predict transfer well; family alone is too coarse).

## Outlier features that require targeted handling

These features routinely break naive multilingual models:

| Feature | Languages | Failure mode | Mitigation |
|---|---|---|---|
| **Polysynthesis** | Inuktitut, Navajo, Mohawk | Tokenizer fertility 4-7×; OOV explosion | Vocab extension MANDATORY; morpheme segmenter |
| **Tone (lexical)** | Yoruba, Vietnamese, Hausa, Mandarin | Diacritic stripping = catastrophic loss | Preserve diacritics; tone-aware G2P |
| **Agglutination** | Turkish, Finnish, Swahili, Korean | Fertility 2-4× | Vocab extension; morpheme-aware augmentation |
| **Root-and-pattern (templatic)** | Arabic, Hebrew, Amharic | BPE captures roots poorly | Morphological pre-processing; root-aware tokenizer |
| **Evidentiality marking** | Quechua, Tibetan, Tariana | MT silently drops; eval blind to it | Targeted eval probes; preserve in training data |
| **Classifier systems** | Mandarin, Thai, Khmer | Numeral handling fragile | Augment training with numeral+classifier examples |
| **Switch reference** | many Indigenous Americas | Coreference fails | Custom annotation; do NOT use UD coref-trained models |
| **Reduplication (productive)** | Indonesian, Hawaiian, Tagalog | Tokenizer creates double entries | Pre-process or use morpheme segmenter |
| **Honorific systems** | Japanese, Korean, Javanese | Politeness register collapse | Register-stratified training; eval per register |
| **Ergative-absolutive alignment** | Basque, Tibetan, ~25% of languages | Subject/object roles inverted vs nominative-accusative | Caution with English-trained role-labelers |

## Coverage gaps to be aware of

- **WALS is sparse**: most languages have only 30-50 features filled; many have <10. Don't infer features from family.
- **URIEL has imputed values**: features marked "imputed" are typology-tree predictions, not observations. Trust verified > imputed.
- **Grambank has best per-language depth** but covers fewer languages.
- **None cover dialects well**: working on Egyptian Arabic vs MSA? URIEL likely has only one Arabic vector.

## Citation

When recording a scope decision in `workspace_state.md`, cite the database + version:

```
Typology source: URIEL v0.4 (snapshot 2026-04-23) + WALS v2020.3
```

## Refresh procedure

The cached URIEL distance matrix lives in `scripts/data/uriel_top100_distances.json` (snapshot 2026-04-23). To refresh:

1. Pull the latest URIEL feature vectors from CMU.
2. Recompute pairwise distances for top-100 high-resource source candidates.
3. Update the snapshot date in `_linguistic_shared/lang_codes.py`.

(Refresh is a Phase 2+ task; Phase 1 ships cached only.)

## See also

- Croft, *Typology and Universals* (2nd ed., Cambridge 2003)
- Dryer & Haspelmath (eds.), *WALS Online* — https://wals.info/
- Skirgård et al. (2023), *Grambank reveals the importance of genealogical constraints on linguistic diversity* — Science Advances
- Littell et al. (2017), *URIEL and lang2vec* — EACL
