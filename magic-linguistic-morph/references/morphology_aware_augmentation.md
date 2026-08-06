# Morphology-Aware Data Augmentation — Reference

Loaded by `magic-linguistic-morph` Step 5.

## Why morphology-aware augmentation

For class 1-2 agglutinative targets with small training corpora, paradigm completion is the cheapest data multiplier:

- Pull UniMorph paradigms for target language.
- For each lemma in training data, generate 10-30 inflected forms.
- 10K lemmas → 100-300K augmented forms.
- Add to training mix with `<morph_aug>` tag.

Typical gain: 1-3 BLEU on MT; 2-5% on POS/NER tagging.

## Augmentation strategies

### 1. Paradigm completion (UniMorph)

Easiest. Requires UniMorph paradigm for target.

```
Lemma: talo (Finnish "house")
Paradigm features: N;Sg;Nom; N;Pl;Nom; N;Sg;Iness; N;Pl;Iness; ...
Generated: talo, talot, talossa, taloissa, talojen, talolla, taloilla, ...
```

### 2. Rule-based generation (FST)

When FST exists, use FST generation mode:

```
foma:
> echo "talo+N+Pl+Iness" | flookup -i finnish.fomabin
taloissa
```

More expressive than UniMorph paradigms (handles edge cases, allomorphy).

### 3. Inflection-prediction model (SIGMORPHON shared task)

When neither UniMorph nor FST exists but SIGMORPHON has shared-task models:
- Use shared-task winner's model to predict inflections from lemma + features.
- Quality lower than gold; usable for low-cost augmentation.

### 4. Code-switch + paradigm

For Hinglish / Spanglish style: paradigm-complete the morphology of one side; leave the other code-switched.

## What NOT to do

- **Pure word-substitution augmentation** (synonym swap from a lexicon): doesn't add morphological variety; can introduce semantic noise.
- **Untagged synthetic mixed with real**: model can't downweight; results usually worse than pure real.
- **Over-augmentation** (>10× synthetic / real): ratio peaks around 3-5×.
- **Generating forms outside the paradigm**: occasional FST/UniMorph errors produce ill-formed words; round-trip-validate.

## Tagging convention

```
<morph_aug> talossa <morph_aug>      # paradigm-completed Finnish form
<morph_aug> taloissa <morph_aug>
talo                                  # original lemma (no tag)
```

The tag is hyperparameter-tunable: at training, model can learn to weight tagged vs untagged.

## Validation

- **Round-trip**: parse generated form back via FST/morphological tagger; verify features match.
- **Native-speaker spot-check**: 100 samples; flag oddities.
- **Downstream eval**: compare model trained with augmentation vs without on held-out test.

## Concrete recipe (class 2 Yoruba example)

1. Pull UniMorph Yoruba (~8K paradigms).
2. For each Yoruba lemma in MasakhaNER + AfroLM, generate available inflected forms.
3. Tag with `<morph_aug>`.
4. Add to training data at 3-5× ratio synthetic / real.
5. Train; eval on FLORES + MasakhaNER held-out.
6. Compare BLEU + F1 vs no-aug baseline.

Expected gain: 1-2 BLEU + 2-4% NER F1.

## See also

- **Bergmanis, T., et al.** (2017). *Training Data Augmentation for Low-Resource Morphological Inflection*. SIGMORPHON.
- **Anastasopoulos, A., & Neubig, G.** (2019). *Pushing the Limits of Low-Resource Morphological Inflection*. EMNLP.
- SIGMORPHON 2022/2023/2024 shared task papers.
