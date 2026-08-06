# Transfer Source Selection (URIEL Distance) — Reference

Loaded by `magic-linguistic-scope` Step 4.

## Why URIEL distance, not "use English"

English is the default transfer source in most ML pipelines because it has the most data. But typologically-distant pairs lose 2-5× the gains a typologically-close pair would deliver. For a low-resource target, the right question is not "how much data does the source have?" but "how much typological structure can transfer?"

Examples (rough magnitudes from published cross-lingual transfer studies):

| Target | Best source by data (English) | Best source by typology | Transfer gain (typology-chosen vs English) |
|---|---|---|---|
| Basque (eus) | English | Spanish (data + contact) or typological-fellow | ~2× on parsing |
| Yoruba (yor) | English | Igbo / Hausa | ~1.5-2× on POS / morphology |
| Mandarin (cmn) | English | Cantonese (data) or typological Sino-Tibetan kin | ~1.5× on syntax probes |
| Turkish (tur) | English | Azerbaijani / Kazakh / Uzbek | ~3× on morphological tasks |
| Finnish (fin) | English | Estonian / Hungarian | ~2-3× on morphology |
| Inuktitut (iku) | English | West Greenlandic / Aleut | ~5× (English is hopeless) |

## URIEL distance methodology

URIEL provides a feature vector per language (~289 dimensions: syntactic, phonological, phonetic, inventory, family). Distance is computed as cosine or weighted euclidean between two vectors.

For LLM transfer-source selection:

```python
distance = w_syntactic * cos_dist(syntactic_vec) \
         + w_phonological * cos_dist(phonological_vec) \
         + w_inventory * cos_dist(inventory_vec) \
         + w_family * tree_distance(family_path)
```

Default weights for **NLP/MT transfer**: syntactic 0.4, phonological 0.1, inventory 0.1, family 0.4.
For **speech/ASR transfer**: phonological 0.5, inventory 0.3, family 0.2.

## Distance interpretation thresholds

| URIEL distance | Interpretation | Recommendation |
|---|---|---|
| 0.00 - 0.20 | Very close (often same family branch) | Continued pretraining; vocab extension optional |
| 0.20 - 0.40 | Close | Continued pretraining; vocab extension recommended |
| 0.40 - 0.60 | Moderate | Adapter approach (MAD-X/BAD-X); vocab extension required |
| 0.60 - 0.80 | Distant | Multilingual base + LoRA; do not use single-source continued pretraining |
| 0.80 - 1.00 | Very distant | Train target representations from scratch; consider multilingual ensemble |

## When no candidate has distance < 0.6

This is common for:
- Polysynthetic Indigenous languages (Inuktitut, Navajo, Cherokee).
- Click languages (Khoisan family).
- Isolates (Basque is borderline; Burushaski, Ainu, Korean all isolates).
- Sign languages (most are family-isolated).

Recommendation: do NOT pick a "best of bad options" English fine-tune. Instead:
1. Start from a multilingual base model (mBART, NLLB, BLOOM) that has at least seen related data.
2. Apply vocab extension (FOCUS / OFA / HyperOfa) for the target's tokens.
3. Use LoRA or adapter approach — don't risk catastrophic forgetting on the multilingual base.
4. Eval against multiple checkpoints; expect higher variance.

## Worked example: Yoruba (yor)

Cached top-5 URIEL distances for Yoruba (excluding self):

| Source | Distance | Notes |
|---|---|---|
| Igbo (ibo) | 0.18 | Same family branch (Niger-Congo > Atlantic-Congo); tone; Latin script; Class 1 |
| Hausa (hau) | 0.34 | Different family (Afro-Asiatic); regional contact; tone; Class 2 |
| Swahili (swa) | 0.41 | Same family > Bantu; Class 3 (good data) |
| Twi (twi) | 0.39 | Same family branch; tone; Class 1 |
| English (eng) | 0.62 | Distant; should NOT be primary transfer source |

Recommendation for Yoruba: **multilingual base (NLLB-200 or AfroLM) + vocab extension + LoRA**. Use Igbo+Hausa+Swahili as auxiliary languages in a small multilingual fine-tune. English provides a *secondary* signal but is not primary.

## Worked example: Inuktitut (iku)

| Source | Distance | Notes |
|---|---|---|
| West Greenlandic (kal) | 0.21 | Closest relative, Class 1 |
| Aleut (ale) | 0.38 | Same family branch (Eskimo-Aleut); Class 0-1 |
| Yupik languages | 0.30-0.45 | Eskimo branch; Class 0-1 |
| English (eng) | 0.78 | Very distant; English is hopeless for polysynthetic morphology |

Recommendation: train representations from scratch + multilingual ensemble; expect to need community-collected data; HEAVY ethics involvement.

## Caveats

- URIEL has **imputed values** for ~30% of features in low-resource entries. Verified-only mode (URIEL flag `--knn=false`) gives more conservative distances. Use cached snapshot's verified-only distances for class 0-1 targets.
- Distance is a **heuristic**, not a guarantee. Empirically validate after a small pilot fine-tune.
- For **speech tasks**, swap to phonological-weighted distance — syntactic distance under-weights phonemic inventory.

## See also

- Littell et al. (2017), *URIEL and lang2vec*
- Lin et al. (2019), *Choosing Transfer Languages for Cross-Lingual Learning* (ACL) — empirical transfer prediction
- Pires et al. (2019), *How Multilingual is Multilingual BERT?* — observed transfer patterns
- de Vries et al. (2022), *Make the Best of Cross-lingual Transfer* — typology-aware source selection
