---
name: magic-linguistic-eval
description: 'Honest evaluation for low-resource LLMs: benchmark choice (FLORES+ / NTREX / Belebele / AfroBench / IndicXTREME / SEACrowd), metric choice (chrF++ / spBLEU / COMET / MetricX / GEMBA-MQM), BLiMP-style grammatical-knowledge probes, contamination check. Use whenever the user mentions evaluation, benchmark, FLORES, NTREX, Belebele, AfroBench, IndicXTREME, SEACrowd, MasakhaNER, AfriSenti, BLEU, chrF, chrF++, spBLEU, COMET, MetricX, GEMBA-MQM, BLiMP, agreement probes, contamination, train-test leakage, or asks ''how do I report quality numbers for [language]''. **The orchestrator''s pipeline doesn''t close without this — always routed at the Evaluate phase.** A-tier; weak content here cascades into all release decisions.'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: high
  requires_llm: false
  phase: 4
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - evaluation
  - benchmark
  - metric
  - low-resource
  dependencies: []
  scripts:
  - scripts/benchmark_advisor.py
  - scripts/contamination_check.py
  - scripts/metric_advisor.py
---

## When to Use

- Reporting quality numbers for any non-English LLM.
- Choosing benchmark + metric for a language pair / task.
- Building grammatical-knowledge probes (BLiMP-style).
- Contamination audit (cross-reference magic-linguistic-corpus).
- Adding fairness eval (per-dialect / per-register breakdown).

**When NOT to use:** purely qualitative review → human review pipeline. Per-dataset license check → `magic-linguistic-ethics`. Tokenizer fertility audit → `magic-linguistic-tokenize`.

## Why this is A-tier

The Evaluate phase is the orchestrator's last specialist. Eval results drive release decisions. Picking BLEU over chrF for a morphologically-rich language doesn't just produce one bad number — it produces a misleading number that drives wrong investment decisions for months. Eval is leverage; weak eval cascades.

## The Knowledge Engineers Routinely Miss

1. **BLEU is pathological for morphologically-rich languages.** Single-morpheme edits wreck it as harshly as full mistranslations. For Turkish / Finnish / Swahili / Yoruba / Inuktitut: chrF / chrF++ / spBLEU are primary. Report BLEU as supplementary if at all — never as the headline.

2. **COMET coverage varies wildly.** COMET-22 has good European + Indic coverage; spotty Bantu / Indigenous Americas. xCOMET-XL extends but still has gaps. ALWAYS check per-language coverage before reporting; a "missing" language gets random numbers.

3. **GEMBA-MQM (Kocmi & Federmann 2023)** is the strongest cheap alternative when COMET doesn't cover. LLM-judge with structured MQM error rubric. Use as supplement or fallback.

4. **FLORES-200 is in many pretrain mixes.** Llama-3 (cutoff March 2024) has likely seen it. NTREX-128, Belebele, custom held-out are alternatives. Report FLORES as a *lower bound* on quality (the model has memorized chunks of it).

5. **Per-dialect / per-register / per-direction breakdowns** are the only way to catch systematic failures. Aggregate scores hide that the model fails on Egyptian Arabic but succeeds on MSA. Report stratified.

6. **English BLiMP-style probes don't transfer.** Subject-verb agreement in English ≠ subject-verb agreement in Yoruba (tone-marked) ≠ no agreement in Mandarin. Per-language probe construction is mandatory.

7. **Cross-direction MT scores aren't comparable.** En→Yoruba ≠ Yoruba→En in difficulty. Report per-direction; don't aggregate.

## Workflow

### Step 1 — Identify task + language pair

For each (target language, task) pair, decide benchmark + metric.

### Step 2 — Benchmark choice

**MANDATORY READ** [`references/benchmark_catalog.md`](references/benchmark_catalog.md).

Use `scripts/benchmark_advisor.py`:

| Task | Benchmark options |
|---|---|
| MT (En ↔ X) | FLORES+ (broad); NTREX-128 (cleaner re contamination); per-region (AfroBench, IndicXTREME, SEACrowd) |
| Reading comprehension | Belebele (122 langs) |
| NER | MasakhaNER 2.0 (Africa); WikiAnn (broad); AfricaNER |
| Sentiment | AfriSenti (Africa); IndicSenti; SemEval per-language |
| QA | TyDi-QA, XQuAD, MLQA |
| General | XNLI, BIG-bench, BUFFET |

### Step 3 — Metric choice

**MANDATORY READ** [`references/metric_guide.md`](references/metric_guide.md).

Use `scripts/metric_advisor.py`:

| Task | Primary | Secondary | NEVER as primary |
|---|---|---|---|
| MT (general) | chrF++ + COMET-22 | spBLEU | BLEU on MRL |
| MT (low COMET coverage) | chrF++ + GEMBA-MQM | spBLEU | BLEU on MRL |
| Reading comprehension | accuracy | per-Q breakdown | n/a |
| NER | F1 (per-tag breakdown) | exact-match | accuracy |
| Sentiment | F1 (per-class) | accuracy | accuracy alone |
| QA | F1 + EM | per-question-type | accuracy |
| Speech ASR | CER (preferred) | WER | WER on space-less script |
| Speech TTS | MOS (human) | PESQ / STOI | metric-only |

### Step 4 — Contamination check

**MANDATORY READ** [`references/contamination_detection.md`](references/contamination_detection.md).

Cross-reference `magic-linguistic-corpus/references/contamination_audit.md`. Two-sided:
- (a) train mix vs eval set.
- (b) eval set vs base-model pretrain (proxy via release dates + known inclusions).

Use `scripts/contamination_check.py` for the side-(b) proxy.

### Step 5 — Probe construction (grammatical-knowledge eval)

**MANDATORY READ** [`references/probe_construction.md`](references/probe_construction.md).

Custom BLiMP-style probes per language:
- Subject-verb agreement (where applicable).
- Gender agreement.
- Case marking.
- Tone (lexical) preservation.
- Word order.
- Honorifics.

Target ≥ 100 minimal pairs per phenomenon.

### Step 6 — Per-stratum breakdown

ALWAYS report:
- Per-dialect (Egyptian Arabic vs MSA; Mandarin vs Cantonese; Cusco vs Ayacucho Quechua).
- Per-register (Bible vs news vs web vs conversation).
- Per-direction (En→X vs X→En for MT).
- Per-class (NER per-tag; sentiment per-class).

Aggregate-only reporting hides systematic failures.

### Step 7 — Output eval report + hand off

```markdown
## Evaluation Report: <Model> on <Language Pair>

**Task:** ...
**Benchmark(s):** ... (with version + release date for contamination check)
**Primary metric:** chrF++ = X | accuracy = X | F1 = X | ...
**Supplementary metrics:** ...
**Contamination assessment:** PASS | FLAG (eval-side-b risk; cite likely inclusions)
**Per-stratum breakdown:** ...
**BLiMP-style probe results:** ... (per-phenomenon)
**Caveats:** known coverage gaps; per-language metric reliability
**Hand-off:** magic-linguistic-ethics for release-mode decision
```

## Anti-patterns (NEVER do)

- **NEVER** report BLEU as primary on morphologically-rich languages. Single-morpheme edits wreck BLEU; chrF++ / COMET are robust.
- **NEVER** report COMET without checking per-language coverage. Missing language = random number.
- **NEVER** use FLORES-200 without contamination check. It's in many pretrain mixes; report as lower bound.
- **NEVER** lift English BLiMP probes verbatim to other languages. Phenomena differ.
- **NEVER** report aggregate scores without per-dialect / per-register / per-direction stratification. Hides systematic failures.
- **NEVER** report cross-direction scores as comparable. En→X and X→En differ in difficulty.
- **NEVER** report parser F1 as a proxy for LLM grammatical knowledge — use agreement probes (cross-reference magic-linguistic-syntax).
- **NEVER** use WER for space-less scripts (Mandarin / Khmer / Thai) — use CER.

## Edge Cases

- **Custom held-out for high-stakes**: build a 200-500 sample held-out set post-2025 to bypass contamination of public benchmarks.
- **No published benchmark for target**: native-speaker spot-check + custom evaluation; document subjectivity.
- **Multi-direction MT model**: per-direction scoring; weighted average if needed; never single-number.
- **TTS without MOS panel budget**: CER on ASR-of-TTS as fallback (lossy proxy).
- **Per-dialect data sparse**: report per-dialect for what you have; flag uncovered.
- **Instruction-following eval for low-resource**: very few benchmarks; native-speaker review until benchmark exists.
- **Long-context eval for low-resource**: cross-reference magic-linguistic-discourse for coherence-aware probes.

## Cross-skill cooperation

- `magic-linguistic-corpus` for contamination check details.
- `magic-linguistic-discourse` for long-context coherence probes.
- `magic-linguistic-syntax` for agreement-probe construction.
- `magic-linguistic-ethics` for release-mode decision after eval.

## Output Format

```markdown
## Eval Plan: <Target Language>

**Tasks:** ... 
**Benchmark per task:** ... (with versions + contamination assessment)
**Primary metric per task:** ...
**Per-stratum breakdown plan:** ...
**Probe construction needed:** YES | NO — phenomena
**Cross-skill routing:** magic-linguistic-corpus (contamination); magic-linguistic-discourse (coherence probes); magic-linguistic-syntax (agreement probes); magic-linguistic-ethics (release-mode)
**Anti-patterns to avoid:** ...
```
