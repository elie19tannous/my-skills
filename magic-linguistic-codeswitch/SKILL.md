---
name: magic-linguistic-codeswitch
description: 'Code-switching awareness for ML pipelines: Hinglish, Spanglish, Singlish, MSA + dialect Arabic, Mandarin + Cantonese alternation, and other bilingual / multilingual mixing. Use whenever the user mentions code-switching, code-switch, code-mixing, Hinglish, Spanglish, Singlish, Chinglish, Konglish, mixed-script chat, MADAR, GLUECoS, LinCE, Matrix Language Frame, or asks how to handle bilingual / multilingual user-generated text. Optional Mindset specialist — code-switching is the norm for many bilingual users, NOT noise to filter out.'
license: Apache-2.0
metadata:
  domain: linguistics
  complexity: low
  requires_llm: false
  test_coverage: advisory  # structurally validated, not behaviorally tested (no executable tests by design)
  phase: 4
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - code-switching
  - multilingual
  - low-resource
  - optional
  dependencies: []
---

## When to Use

- User-generated text from bilingual / multilingual communities.
- Building a chatbot for code-switching-prevalent communities.
- Diagnosing model failures on Hinglish / Spanglish / etc.

**When NOT to use:** monolingual data → no code-switching to handle. For language-ID at paragraph granularity → `magic-linguistic-corpus`.

## Stance

Code-switching is the **norm**, not noise. ~50% of the world's population is multilingual; their conversational text routinely mixes languages. Filtering CS as data-quality issue is a category error: you're filtering the user's natural way of speaking. Treat CS as first-class.

## What's worth knowing

1. **Matrix Language Frame model (Myers-Scotton 1993)** — one language is the matrix (grammatical structure), the other is embedded (insertions). Detection methods exist; useful for tokenizer + corpus stratification.

2. **Per-paragraph LID is the floor** for CS-prevalent corpora. Document-level LID averages over CS and gets it wrong. (Cross-reference `magic-linguistic-corpus/references/language_id.md`.)

3. **CS data sources** (snapshot 2026-04-23):
   - **LinCE** — Linguistic Code-switching Evaluation (Hinglish, Spanglish, Modern Standard Arabic + Egyptian, etc.).
   - **GLUECoS** — Code-switching benchmark suite (Hindi-English, Spanish-English, etc.).
   - **MADAR** — MSA + 25 Arabic dialects.
   - **DART** — Dialect Annotation in Tweets.

4. **CS-aware tokenizer** preserves code-switched tokens; per-script policy preserved (don't strip diacritics from one side just because the other is Latin).

5. **MT models trained on monolingual data fail at CS in characteristic ways** — language-ID confusion, partial-translation hallucination. Targeted CS eval needed.

6. **CS in low-resource contexts** is often the only natural data — Twi-English chat, Yoruba-English social media. Filtering it out leaves no usable training data.

## Anti-patterns (NEVER do)

- **NEVER** filter code-switched data as "noise" without checking community usage patterns. You may be filtering 60% of conversational data.
- **NEVER** use document-level LID for CS-prevalent corpora — paragraph-level minimum.
- **NEVER** assume English-trained models handle CS well — domain mismatch.
- **NEVER** strip one language's diacritics just because they're not in the other.

## See also

- `references/canonical_sources.md`.
- `magic-linguistic-corpus/references/language_id.md` for paragraph-level LID.
- `magic-linguistic-tokenize` for CS-aware tokenizer training.
