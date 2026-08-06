# Coherence-Aware Evaluation — Reference

Loaded by `magic-linguistic-discourse` for any long-context LLM eval.

## Why coherence matters for LLMs

Modern LLMs produce surface-fluent text. The dominant failure modes in long-context generation are discourse-level:
- Hallucinated references ("...as discussed earlier" when it wasn't).
- Dangling pronouns (no antecedent).
- Topic drift (smooth-sounding but semantically off-target).
- Citation faithfulness gaps (cited source doesn't actually support the claim).

These don't show up in perplexity or BLEU. Targeted discourse-aware probing catches them.

## Four discourse-aware eval categories

### 1. Coreference accuracy
For each pronoun in generated text: does it have a valid antecedent? Does it resolve to the correct entity?

Tool: coref resolver + manual spot-check.
Score: % pronouns with valid resolution; % errors per chain.

### 2. Discourse-relation accuracy (PDTB-style)
For each connective ("however", "therefore", "moreover"): does the relation hold between the connected units?

Tool: PDTB-trained classifier on generated text + human spot-check.
Score: % connectives with semantically-valid relation.

### 3. RST-style nucleus preservation (summarization)
For summary generation: are the nuclei from source preserved? Are satellites correctly compressed?

Tool: RST parser on source + summary; align nuclei; check compression.
Score: nucleus-preservation precision/recall; satellite-compression rate.

### 4. Citation faithfulness (RAG)
For each citation in generated text: (a) does the cited source contain the claim? (b) does the claim coreferentially match the user's question?

Tool: NLI model for (a); coref + question-answer overlap for (b).
Score: % citations passing both.

## Coherence probes for long-context LLMs

Targeted probes for specific failure modes:

| Probe | Failure detected | Construction |
|---|---|---|
| Pronoun-resolution probe | Dangling pronouns, wrong antecedent | Generate with pronouns; check resolution |
| Topic-segment probe | Topic drift | Segment generation by topic; compute topic-shift entropy |
| Citation-faithfulness probe | RAG hallucination | Generate with citations; check against source |
| Coreference-chain probe | Broken referential chains | Track entity through generation; check chain consistency |
| Connective-faithfulness probe | Misused discourse markers | Extract connectives; check relation validity |

## Probe construction protocol

1. Identify failure mode of interest (e.g., dangling pronouns).
2. Construct N test prompts (50-200) likely to trigger the failure.
3. Run model; capture generation.
4. Apply automated detector + human spot-check.
5. Report % failures + qualitative examples.

## What perplexity / BLEU misses

| Metric | Catches | Misses |
|---|---|---|
| Perplexity | Surface fluency | Coherence; faithfulness |
| BLEU / chrF | Lexical overlap | Coherence; faithfulness; semantic equivalence |
| BERTScore | Semantic similarity per-sentence | Cross-sentence coherence |
| COMET / MetricX | Translation quality | Long-context discourse |
| RAG-faithfulness metrics | Surface citation overlap | Coreferential validity of citation |

Discourse-aware metrics complement these — never replace.

## Per-language coherence eval

For low-resource:
- Coref tools may not exist; manual spot-check.
- Discourse-marker lexicons may be absent; can't automate connective probes.
- Topic-segmentation works language-agnostically (TextTiling).
- Manual eval is the floor; flag in workspace_state.md.

## Long-context-specific failure patterns

| Length | Dominant failure |
|---|---|
| < 500 tokens | Surface fluency dominates |
| 500-2000 | Pronoun-resolution starts breaking |
| 2000-8000 | Topic drift begins; citation faithfulness drops |
| > 8000 | All discourse failures common; coherence drops sharply |

For LLMs claimed to handle 128K+ context: discourse-aware eval IS the eval. Standard metrics will pass even when generation is incoherent.

## See also

- **Karpinska, M., Akoury, N., Iyyer, M.** (2024). *One Thousand and One Pairs: A "novel" challenge for long-context language models*. EMNLP.
- **Li, T., et al.** (2024). *Loogle / LongEval / NocheL benchmarks*. Various.
- **Webber, B., et al.** (2019). *The Penn Discourse Treebank 3.0*. Annotation manual.
- **Stede, M.** (2011). *Discourse Processing*. Morgan & Claypool.
