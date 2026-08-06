# Metric Guide — Reference

Loaded by `magic-linguistic-eval` Step 3.

## MT metrics

### chrF / chrF++ / chrF3 (Popović 2015, 2017)
- Character n-gram F-score.
- ROBUST for morphologically-rich languages.
- chrF++ (default β=2 + word n-grams) is the standard reporting choice.
- spBLEU (sacreBLEU + sentencepiece tokenizer) is the tokenizer-agnostic alternative.

### COMET family
- **COMET-22** (Rei et al. 2022): trained metric; correlates well with human judgment for high-resource pairs.
- **COMET-Kiwi** (reference-free): for QE without reference.
- **xCOMET / xCOMET-XL** (Guerreiro et al. 2024): error-span detection + score.
- **MetricX-23**: Google trained metric; competitive with COMET.

Per-language coverage **varies**. Bantu / Indigenous Americas often missing. Check before reporting.

### GEMBA-MQM (Kocmi & Federmann 2023)
- LLM-judge with MQM error rubric.
- Best for languages COMET doesn't cover well.
- Cite version + judge model used.

### BLEU (Papineni et al. 2002) — DEPRECATED as primary for MRL
- Sentence-level n-gram precision with brevity penalty.
- Pathological for morphologically-rich languages.
- Report only as supplementary on agglutinative / polysynthetic / templatic targets.
- For high-resource European pairs: still acceptable as one of several.

### Choice matrix (MT)

| Target type | Primary | Secondary | Avoid as primary |
|---|---|---|---|
| Latin/Romance, high-resource | chrF++ + COMET-22 | spBLEU + BLEU | n/a |
| Slavic | chrF++ + COMET-22 | spBLEU | BLEU |
| Agglutinative (Turkish, Finnish, Swahili, Korean) | chrF++ + COMET-22 | spBLEU | **BLEU** |
| Templatic (Arabic, Hebrew) | chrF++ + COMET-22 | spBLEU | **BLEU** |
| Polysynthetic (Inuktitut, Navajo) | chrF++ + GEMBA-MQM | spBLEU | **BLEU** |
| Bantu (Swahili, Yoruba via family) | chrF++ + GEMBA-MQM | spBLEU | **BLEU** + COMET if low coverage |
| Tone (Yoruba, Vietnamese, Mandarin) | chrF++ + COMET if available | spBLEU | BLEU |
| Indigenous Americas | chrF++ + GEMBA-MQM | spBLEU | BLEU |

## Reading comprehension / QA

- **Accuracy** (multiple choice): primary.
- **F1** (extractive QA): primary.
- **EM** (exact match): supplementary.
- Per-question-type breakdown ALWAYS.

## NER

- **F1 (per-tag)**: primary. Aggregate masks per-tag failures.
- **Exact match**: supplementary.
- Span-based F1 (gamma): for span-task IAA.

## Sentiment / classification

- **F1 (per-class)**: primary on imbalanced datasets.
- Accuracy: only when classes balanced.
- Macro-F1: when reporting cross-class fairness.

## Speech

### ASR
- **WER** (Word Error Rate): standard for space-segmented languages.
- **CER** (Character Error Rate): MANDATORY for space-less (Mandarin, Khmer, Thai, Lao, Burmese).
- Per-dialect / per-domain breakdown.

### TTS
- **MOS** (Mean Opinion Score): human-rated naturalness; gold.
- **PESQ / STOI**: signal-quality; weak naturalness correlation.
- **Speaker similarity** (verification network) for voice cloning.

## Per-stratum reporting (MANDATORY)

Aggregate hides failures. Always report:
- Per-direction (MT En→X vs X→En).
- Per-dialect (Egyptian vs MSA Arabic; Cantonese vs Mandarin).
- Per-register (Bible vs news vs web vs conversation).
- Per-class (NER tag; sentiment class).
- Per-genre (where applicable).

## Bootstrap CIs

For small eval sets (< 1000 items): report 95% bootstrap CI. Single-number scores on small samples are unreliable.

## See also

- **Popović, M.** (2015). *chrF: character n-gram F-score for automatic MT evaluation*. WMT.
- **Rei, R., et al.** (2022). *COMET-22: Unbabel-IST 2022 Submission for the Metrics Shared Task*. WMT.
- **Guerreiro, N. M., et al.** (2024). *xCOMET: Transparent Machine Translation Evaluation through Fine-grained Error Detection*. TACL.
- **Kocmi, T., & Federmann, C.** (2023). *Large Language Models Are State-of-the-Art Evaluators of Translation Quality* (GEMBA / GEMBA-MQM).
- **Papineni, K., et al.** (2002). *BLEU: a Method for Automatic Evaluation of Machine Translation*. ACL.
- **Freitag, M., et al.** (2021). *Experts, Errors, and Context: A Large-Scale Study of Human Evaluation for Machine Translation* (MQM).
