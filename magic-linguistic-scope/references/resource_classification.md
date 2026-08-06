# Resource Classification (Joshi 0-5) — Reference

Loaded by `magic-linguistic-scope` Step 2.

## The Joshi 2020 taxonomy

From Joshi et al., *The State and Fate of Linguistic Diversity and Inclusion in the NLP World* (ACL 2020). The canonical resource-class taxonomy.

| Class | Joshi name | Definition | ML implications |
|---|---|---|---|
| 0 | The Left-Behinds | No labelled data; little/no unlabelled | Bootstrap from related language; field linguistics may be required |
| 1 | The Scraping-Bys | Some unlabelled (e.g., Wikipedia dump); no labelled | Continued pretraining + adapter (low parameter count) |
| 2 | Hopefuls | Some labelled in limited tasks; no benchmarks | Vocab extension + LoRA; targeted small-scale eval |
| 3 | Rising Stars | Multiple labelled tasks; some benchmarks | Standard fine-tune; careful eval per benchmark |
| 4 | Underdogs | Many labelled tasks; many benchmarks | Standard fine-tune; broader eval |
| 5 | Winners | Benchmark-saturated | Standard everything; SOTA push |

## Cached signals used by `scripts/resource_classifier.py`

The heuristic combines five signals (each cached as JSON snapshots dated 2026-04-23):

1. **Wikipedia article count** (cached from Wikistats)
2. **OPUS bitext volume** (cached from opus.nlpl.eu)
3. **FLORES-200 inclusion** (binary; flores+ language list)
4. **NLLB inclusion** (binary; NLLB-200 language list)
5. **HuggingFace dataset count** with the language tag (cached count)

Class assignment heuristic (Joshi-aligned):

| Class | Signals required |
|---|---|
| 0 | None of the above |
| 1 | Wikipedia present (>1k articles) OR OPUS present (>10k sentence pairs); no benchmarks |
| 2 | Wiki + OPUS + (HF count >= 5 datasets); no FLORES |
| 3 | All of (Wiki, OPUS, FLORES OR NLLB); HF count >= 20 |
| 4 | All of (Wiki, OPUS, FLORES, NLLB); HF count >= 50 |
| 5 | All of above; HF count >= 200 |

## Class change ML strategy

| Class | Tokenizer | Adapter / fine-tune | Eval suite | Ethics depth |
|---|---|---|---|---|
| 0 | Build from scratch (or borrow from family) | None — bootstrap | Native-speaker spot-check | HEAVY (community partnership) |
| 1 | Vocab extension on multilingual base | LoRA r=8-16 | FLORES if present, else native-speaker | HEAVY |
| 2 | Vocab extension; byte fallback | LoRA r=16-32 + adapter | FLORES + Belebele if present | MEDIUM |
| 3 | Existing tokenizer + extension | LoRA r=32 + full fine-tune | Standard benchmark suite | MEDIUM |
| 4 | Existing tokenizer | Full fine-tune | Standard suite + dialect breakdown | STANDARD |
| 5 | Existing tokenizer | Full fine-tune | Standard suite + adversarial probes | STANDARD |

## Common misclassification traps

- **Wikipedia size ≠ resource class.** Cebuano has 6M articles (mostly bot-generated); it is not a Class 5 language.
- **English-paired benchmarks ≠ general resource availability.** A language can be "well-resourced for translation" but Class 1 for everything else.
- **Recently-released benchmarks may not be in cached data.** Re-check for languages where you suspect recent releases (Belebele added 122 langs in 2024; SEACrowd Phase 2 added ~50 SEA langs in 2025).
- **Dialect data attributed to macrolanguage.** Egyptian Arabic data often counted under "Arabic" → over-classifies MSA.

## Class is not destiny

Joshi class is a starting point, not a ceiling. Many Class 1-2 languages have specific high-quality datasets (e.g., Yoruba has MasakhaNER, Khmer has SEACrowd) that punch above their class. Always check actual dataset availability before strategy.

## See also

- Joshi et al. (2020), ACL — https://aclanthology.org/2020.acl-main.560/
- Adelani et al. (2022, 2024), *MasakhaNER* — Class 2-3 African language NER
- SEACrowd — https://seacrowd.github.io/
- AI4Bharat IndicNLP — https://ai4bharat.org/
