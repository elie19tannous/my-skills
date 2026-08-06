---
name: magic-linguistic-discourse
description: 'Discourse-level analysis for the target language: choosing a discourse framework (RST / PDTB / SDRT / GUM), coreference (incl. zero-anaphora in pro-drop languages), discourse markers, and coherence-aware evaluation for long-context LLMs. Use whenever the user mentions discourse, RST, Rhetorical Structure Theory, PDTB, Penn Discourse Treebank, GUM, SDRT, coreference, anaphora, zero-anaphora, pro-drop, discourse marker, coherence, summarization fidelity, RAG citation, dangling pronoun, topic drift, or asks how to evaluate long-context generation quality. Routed by magic-linguistic-orchestrator in the Analyze phase. Stede (2011) *Discourse Processing* is the canonical textbook.'
license: Apache-2.0
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  test_coverage: advisory  # structurally validated, not behaviorally tested (no executable tests by design)
  phase: 3
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - discourse
  - rst
  - pdtb
  - coreference
  - coherence
  - low-resource
  dependencies: []
---

## When to Use

- Long-context LLM eval where coherence matters (summarization, multi-paragraph QA, RAG).
- Coreference annotation or eval, especially for pro-drop languages.
- Choosing between discourse-annotation frameworks (RST vs PDTB vs SDRT vs GUM).
- Diagnosing model failures: hallucinated references, dangling pronouns, topic drift, broken citation.

**When NOT to use:** purely sentence-level eval → `magic-linguistic-eval`. Syntactic structure → `magic-linguistic-syntax`. Sense-level meaning → `magic-linguistic-semantics`.

## Stance

Discourse is the layer most LLM evals don't touch — and where modern LLMs most often quietly fail. A model can fluently produce a 2,000-word answer with a hallucinated citation, an unreachable referent, or a topic that drifts from question to claim to anecdote without anyone noticing. Discourse-aware analysis catches this.

This is a **framework-application** skill, not a procedural recipe. Different frameworks model different aspects of discourse coherence. Pick the one that matches your question. Apply it as a lens, not as a script. (Stede's textbook captures this stance — it surveys frameworks rather than prescribing one.)

## Frameworks: when to use which

| Framework | Models | Best for |
|---|---|---|
| **RST** (Rhetorical Structure Theory) | Hierarchical tree of nucleus/satellite relations | Summarization (which units are central?); discourse-aware compression |
| **PDTB** (Penn Discourse Treebank) | Local discourse relations between adjacent units, marked by explicit/implicit connectives | Discourse-marker prediction; QA (what does "however" connect to?) |
| **SDRT** (Segmented Discourse Representation Theory) | Formal logical structure with discourse relations | Research; rare in production |
| **GUM** (Georgetown University Multilayer) | RST + UD + coref + entities + discourse markers in one corpus | Multi-layer cross-eval; single-source ground truth |
| **PCC / RST-DT / DISRPT corpora** | Per-language RST annotation | Per-language eval |

For most LLM eval projects:
- **PDTB** for connective-level discourse-marker prediction.
- **RST** for summarization-coherence eval.
- **GUM** when you want multi-layer alignment.
- SDRT only if your project has formal-logic requirements.

## The Knowledge Engineers Routinely Miss

1. **Coreference is genre-specific.** OntoNotes-trained coref models (news/Wikipedia) break on dialogue. Use ConvCoref or genre-matched data for conversational text.

2. **Zero anaphora dominates in pro-drop languages.** ~20-40% of pronoun chains in Mandarin / Japanese / Spanish / Italian are dropped (omitted in surface form). English-trained coref misses these silently.

3. **Discourse-marker lexicons are per-language.** "However" / "therefore" / "moreover" lists don't transfer. Per-language marker classifiers built on PDTB-aligned corpora are the floor; for low-resource you typically need to construct.

4. **Coherence eval ≠ fluency eval.** A model can produce sentences that are individually fluent but discoursively broken (topic drift, references that don't resolve). Targeted probing — coreference accuracy, discourse-relation accuracy, citation faithfulness — catches what perplexity misses.

5. **GUM is underused.** Multi-layer alignment in a single corpus is rare; if your project's target is English (or one of GUM's covered languages), it's the best single-source ground truth.

6. **RAG citation faithfulness is a discourse-coherence problem.** "The model said X according to source Y" is only valid if (a) the cited claim X actually appears in source Y AND (b) the claim X resolves coreferentially to what the user asked. Naive citation-overlap metrics miss the coreference half.

7. **Topic drift in long generation** is detectable via discourse-segment topic tracking — measurable, not just qualitative.

## Working with discourse — the four lenses

### 1. Local connectives (PDTB)
Question: "Does the model handle 'because' / 'although' / 'however' correctly?"
Tool: PDTB-trained classifier; extract connectives + their arguments; check the relation matches.

### 2. Hierarchical structure (RST)
Question: "Does the summary preserve the central nucleus?"
Tool: RST parser (per-language coverage varies); compare nuclei across source and summary.

### 3. Coreference + anaphora
Question: "Do all pronouns resolve to a valid antecedent?"
Tool: Coref resolver. For pro-drop: zero-anaphora extension required.

### 4. Topic continuity
Question: "Does the generation stay on topic across paragraphs?"
Tool: Topic-segment detection (TextTiling, BERT-based); compute topic-coherence across segments.

## Anti-patterns (NEVER do)

- **NEVER** use English-trained coref on pro-drop language without zero-anaphora extension. 20-40% of pronouns are silently lost.
- **NEVER** report parser-style discourse F1 without specifying framework. RST F1 ≠ PDTB F1 ≠ SDRT F1.
- **NEVER** use OntoNotes-trained coref on dialogue text. Genre mismatch.
- **NEVER** treat citation-overlap as a complete RAG faithfulness metric. Coreference resolution is the missing half.
- **NEVER** assume perplexity-low generation is discourse-coherent. Surface fluency ≠ coherence.
- **NEVER** skip discourse eval on long-context LLMs. The dominant failure modes are discourse-level.

## Edge Cases

- **Dialogue + monologue mix** (chat assistant): per-segment framework; switch coref model by genre.
- **Multilingual long-context** (mixed-language threads): paragraph-level LID + per-language discourse processing.
- **Translated text** (MT output as input to discourse eval): MT distortion may break coreference chains; eval before assuming alignment.
- **Code interleaved with prose**: discourse frameworks don't model code structure; segment + handle separately.
- **Liturgical / poetic text**: standard discourse frameworks under-fit; document the limitation.
- **Endangered-language oral narrative**: Western-tradition discourse frameworks may not apply — rhetorical structures differ. Community input mandatory.

## Stede textbook orientation

Stede (2011) *Discourse Processing* (Morgan & Claypool) is the canonical compact reference. Reading order:
1. Chapter 1-2: discourse phenomena overview.
2. Chapter 3 (RST), 4 (PDTB), 5 (SDRT): per-framework deep dives. Pick the one matching your need.
3. Chapter 6 (coreference), 7 (discourse parsing).

Stede surveys; he doesn't prescribe. Treat his book as a framework-comparison guide.

## Output Format

```markdown
## Discourse Analysis: <Use Case>

**Question:** <coreference / coherence / summarization / citation / drift>
**Recommended framework:** RST | PDTB | SDRT | GUM
**Rationale:** ...
**Per-language considerations:** <pro-drop? genre? script? available corpora?>
**Tooling recommended:** ...
**Anti-patterns to avoid:** ...
**Hand-off:** magic-linguistic-eval (probes); magic-linguistic-annotate (if creating discourse gold)
```

## See also

- `references/discourse_frameworks.md`
- `references/coreference_patterns.md`
- `references/coherence_eval.md`
- `references/canonical_sources.md` — Stede + per-framework foundational papers.
