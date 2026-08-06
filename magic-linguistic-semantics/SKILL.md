---
name: magic-linguistic-semantics
description: 'Lexical + frame semantics for the target language: WordNet / Open Multilingual WordNet (OMW) coverage, FrameNet / PropBank-style SRL guidance, multi-word expressions (MWE / PARSEME). Use whenever the user mentions WordNet, OMW, synset, sense disambiguation, FrameNet, PropBank, semantic role labeling, SRL, MWE, idioms, multi-word expressions, light verbs, phrasal verbs, semantic equivalence, or asks how to handle ''kick the bucket'' style mistranslation. Routed by magic-linguistic-orchestrator in the Analyze phase.'
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
  - semantics
  - wordnet
  - framenet
  - srl
  - mwe
  - low-resource
  dependencies: []
  scripts:
  - scripts/srl_frame_advisor.py
  - scripts/wordnet_coverage.py
---

## When to Use

- Need WordNet / OMW coverage for the target language.
- Building / evaluating SRL or frame-semantics annotation.
- Diagnosing MWE-related MT failures (idioms mistranslated literally).
- Sense-equivalence eval for retrieval / RAG grounding.
- Adding semantic-grounded eval to an LLM-quality pipeline.

**When NOT to use:** purely surface-level eval (BLEU, chrF) → `magic-linguistic-eval`. POS / dep parsing → `magic-linguistic-syntax`. For pure annotation methodology around sense → `magic-linguistic-annotate`.

## The Knowledge Engineers Routinely Miss

1. **WordNet OMW per-language coverage varies wildly.** English Princeton WordNet: 117K synsets. Many OMW languages: 5-30K. Don't assume parity. `wordnet_coverage.py` reports per-language gaps.

2. **PropBank-style SRL frames are NOT 1:1 across languages.** English "GIVE" frame ≠ Spanish "DAR" frame structure exactly. Per-language frame inventories drift; alignment via Predicate Matrix or MultiFrameNet is required for cross-lingual SRL.

3. **MWE handling is the dominant low-resource MT failure mode.** "Kick the bucket", "let the cat out of the bag", "raining cats and dogs" — naive MT translates literally. PARSEME shared-task tagging catches these; treat MWEs as units before tokenization.

4. **Sense splitting vs lumping is corpus-design**, not just lexicographic preference. Granular splits enable fine-grained WSD eval; lumped splits are easier to annotate consistently. Choose by use case.

5. **Cross-lingual semantic-equivalence eval** for RAG/retrieval is best done via cross-lingual embedding cosine + COMET-style learned metrics. BLEU/chrF underestimate semantic equivalence on low-resource MT.

6. **WordNet/OMW for low-resource is patchy** — languages like Yoruba have ~5K synsets vs English 117K. RAG grounding queries that depend on synset coverage silently fail in target languages.

7. **Light verbs** ("take a walk", "give a smile") are MWE-adjacent — a verb + noun acting as a single semantic unit. Per-language treatment varies; not all languages have light-verb constructions in the same proportion.

## Workflow

### Step 1 — Identify lexical-semantic resources

**MANDATORY READ** [`references/wordnet_omw.md`](references/wordnet_omw.md).

Use `scripts/wordnet_coverage.py`:
- Per-target: synset count, alignment coverage, OMW project status.
- Surface coverage gaps relative to English Princeton WordNet.

### Step 2 — Frame semantics / SRL

**MANDATORY READ** [`references/framenet_srl.md`](references/framenet_srl.md).

Use `scripts/srl_frame_advisor.py`:
- Per-target: FrameNet availability (Berkeley FrameNet for English; per-language FrameNet projects exist for ~20 languages).
- PropBank-style alignment via Predicate Matrix.
- Recommend SRL tooling (per-language model availability).

### Step 3 — MWE / PARSEME handling

**MANDATORY READ** [`references/mwe_parseme.md`](references/mwe_parseme.md).

For MT / SRL / RAG projects:
- Pre-tokenize MWEs as single units when possible (PARSEME-tagged corpora).
- Build per-target MWE catalog if not available — even small (~500 idioms) helps.
- Treat as semantic-equivalent units in eval.

### Step 4 — Sense-equivalence eval

For RAG / retrieval / cross-lingual semantic similarity:
- COMET-style learned metric > BLEU for semantic equivalence.
- LaBSE / SONAR cross-lingual embedding cosine for retrieval-style eval.
- Per-language COMET coverage varies; check before reporting.

### Step 5 — Output semantics plan + hand off

```markdown
## Semantics Plan: <Language>

**WordNet/OMW:** <synset count + coverage gap %>
**FrameNet:** available | partial | absent (recommend Predicate Matrix for cross-lingual)
**PropBank-style SRL:** <tooling option>
**MWE strategy:** PARSEME-aligned | custom catalog | none
**Semantic-equivalence eval:** COMET / LaBSE / SONAR
**Hand-off:** magic-linguistic-eval (semantic-equivalence metrics); magic-linguistic-annotate (sense annotation if extending)
```

## Anti-patterns (NEVER do)

- **NEVER** assume English WordNet structure transfers to other OMW languages. Coverage varies 10-20×.
- **NEVER** ignore MWE handling in MT — silent literal translation of idioms is a top failure mode.
- **NEVER** use English PropBank frames for non-English SRL without per-language alignment audit.
- **NEVER** report semantic-equivalence with BLEU as primary metric. Use COMET / LaBSE for cross-lingual.
- **NEVER** assume sense-disambiguation eval scales from English to low-resource — sense inventories differ + coverage is sparse.
- **NEVER** treat "kick the bucket" as 3 unrelated content words.
- **NEVER** skip cross-lingual frame alignment when comparing SRL outputs across languages.

## Edge Cases

- **OMW coverage absent for target:** fall back to bilingual lexicon + custom sense inventory; document limitation.
- **FrameNet absent for target:** Predicate Matrix bridges via English; expect coverage gaps.
- **MWE catalog absent:** start with 500-idiom pilot via community contribution.
- **Polysemous English term in cross-lingual sense eval:** annotate per-sense; don't flatten.
- **Honorific-marked semantic distinctions** (Japanese, Korean): some "synonyms" carry register info — sense-split them.
- **Macrolanguage with merged senses** (Quechua varieties): per-subtag sense inventory may differ.

## Output Format

```markdown
## Semantics Analysis: <Language>

**WordNet/OMW status:** N synsets (X% coverage vs Princeton WordNet)
**FrameNet status:** ...
**PropBank-style SRL recommended tool:** ...
**MWE strategy:** ...
**Sense-equivalence eval metric:** ...
**Anti-patterns to avoid for this target:** ...
**Hand-off:** ...
```
