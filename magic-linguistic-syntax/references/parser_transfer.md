# Parser Transfer — Reference

Loaded by `magic-linguistic-syntax` Step 3.

## The transfer problem

Most languages don't have UD treebanks large enough for direct training. Cross-lingual transfer from a source treebank-language to a target language is the standard solution.

## Source selection criteria

Pick the source by:
1. **URIEL typological distance** to target (route to `magic-linguistic-scope`). Smaller distance = better transfer.
2. **Treebank size** for the source.
3. **Annotation match**: does the source treebank cover the POS / dep relations you need for the target?

URIEL distance dominates. A typological-fellow with 10K sentences beats a distant language with 100K.

## Empirical transfer pairs

| Target | Best source | Empirical transfer (UAS) |
|---|---|---|
| Yoruba | Igbo / Wolof (if treebank exists; rare) → English fallback | ~50-60 zero-shot from English; +10 from Niger-Congo close |
| Khmer | Vietnamese | ~55-60 zero-shot from Vi; better than zero-shot from En |
| Inuktitut | Greenlandic (not avail) → multilingual model | ~40-50 zero-shot from any single source; multilingual base helps |
| Cantonese | Mandarin | ~75-80 zero-shot from Mandarin (close pair) |
| Quechua | Spanish (loanword influence) or multilingual | ~40-55 zero-shot |
| Twi | Igbo / Yoruba (if treebanks exist) → English fallback | ~50 zero-shot |
| Tamil | Telugu / Kannada (if treebanks exist) → Hindi | ~55-65 |
| Hausa | Arabic (Ajami script) or English (Latin) | varies; Latin-script side gets ~50-60 |

## Tool recommendations

### Trankit (2021)

- XLM-R based; fine-tuned on UD multilingually.
- Best low-resource quality among open-source options.
- Slower than stanza.
- Best default for new low-resource projects.

```python
from trankit import Pipeline
nlp = Pipeline('vietnamese', cache_dir='./cache')
out = nlp('Tôi đi học.')
```

### stanza (Stanford, 2020)

- 70+ languages out of box.
- Fast.
- Slightly weaker than Trankit on low-resource.
- Best for production / speed-priority.

```python
import stanza
stanza.download('vi')
nlp = stanza.Pipeline('vi')
doc = nlp('Tôi đi học.')
```

### UDify (2019)

- Single multilingual model trained on all UD treebanks.
- Older; worse than Trankit.
- Useful as baseline.

### Custom fine-tune

When neither Trankit nor stanza covers your target adequately:
1. Start from XLM-R / mBERT.
2. Fine-tune on chosen source treebank (URIEL-close to target).
3. Eval zero-shot on target's PUD test (if exists).
4. If target has small training treebank: add few-shot fine-tune.

## Eval limitations

- Parser F1 / UAS / LAS reported numbers depend on UD version + treebank choice. Cite both.
- Cross-lingual zero-shot results vary 5-15 points across runs. Report mean + std over 3+ seeds.
- "Parser transfer" results published before 2022 may use older UD versions; not directly comparable.

## See also

- **Nguyen, M. V., et al.** (2021). *Trankit: A Light-Weight Transformer-based Toolkit for Multilingual Natural Language Processing*. EACL demo.
- **Qi, P., et al.** (2020). *Stanza: A Python Natural Language Processing Toolkit for Many Human Languages*. ACL.
- **Kondratyuk, D., & Straka, M.** (2019). *75 Languages, 1 Model: Parsing Universal Dependencies Universally* (UDify). EMNLP.
- **de Vries, W., Wieling, M., Nissim, M.** (2022). *Make the Best of Cross-lingual Transfer: Evidence from POS Tagging with Over 100 Languages*. ACL.
