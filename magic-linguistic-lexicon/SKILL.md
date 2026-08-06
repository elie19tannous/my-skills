---
name: magic-linguistic-lexicon
description: 'Lexicography for ML: dictionary-building methodology, sense splitting vs lumping decisions, MWE inventories for RAG glossary injection + MT post-edit, citation-form conventions, variant handling. Use whenever the user mentions lexicography, dictionary-building, sense splitting, sense lumping, lemma, citation form, MWE inventory, glossary, Wiktionary, DBnary, Atkins & Rundell, or asks how to build a target-language lexicon for RAG or MT post-edit. Optional Mindset specialist.'
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
  - lexicography
  - dictionary
  - mwe
  - sense-inventory
  - low-resource
  - optional
  dependencies: []
---

## When to Use

- Building a target-language lexicon for MT post-edit, RAG glossary injection, or technical-domain control.
- Deciding sense-splitting vs sense-lumping policy for WSD eval.
- Designing MWE inventory for low-resource MT.
- Citation-form conventions per script / language family.

**When NOT to use:** sense-disambiguation eval directly → `magic-linguistic-semantics`. Pure morphological paradigms → `magic-linguistic-morph`.

## Stance

Lexicography is the unsexy specialty that quietly determines whether RAG / MT / structured-extraction works. A lexicon with wrong sense splits = bad eval scores; a lexicon without MWEs = silent literal mistranslation. Treat lexicon construction as ML infrastructure, not afterthought.

## What's worth knowing

1. **Sense splitting vs lumping** is a corpus-design decision, not just lexicographic preference. Granular splitting helps WSD eval (you can measure fine distinctions); lumped splitting eases annotation consistency. Choose by use case.

2. **MWE inventories** drive RAG glossary injection + MT post-edit. "Kick the bucket" / "let the cat out of the bag" — without MWE-aware processing, MT silently mistranslates literally. (Cross-reference `magic-linguistic-semantics/references/mwe_parseme.md`.)

3. **Citation-form conventions per script** — lemma form for Latin/Cyrillic; root for Semitic; classifier+noun for some isolating; per-script convention.

4. **Variant handling** — spelling variants, dialect variants, pre-reform vs post-reform spellings. Document policy explicitly; otherwise lexicon noise compounds.

5. **Atkins & Rundell** (*The Oxford Guide to Practical Lexicography*, 2008) is canonical — corpus-based dictionary-making methodology. Read before designing a serious lexicon project.

6. **Cross-lingual lexicon sources** (snapshot 2026-04-23):
   - **Wiktionary** — community-curated, multilingual, varying quality.
   - **DBnary** — Wiktionary as RDF / structured.
   - **PanLex** — meta-lexical resource bridging many bilingual dictionaries.
   - **MUSE** (Facebook) — bilingual lexicons for 110 languages.

7. **For low-resource lexicon construction**: bootstrap via cognate sets (cross-reference `magic-linguistic-historical`) → community refinement → curator pass.

## Anti-patterns (NEVER do)

- **NEVER** ship a lexicon without explicit sense-splitting policy. Inconsistent senses across entries = unreliable WSD.
- **NEVER** lump senses for production WSD eval. The eval becomes trivial.
- **NEVER** skip MWE inventory for RAG glossary work. Literal mistranslation is the dominant failure mode.
- **NEVER** mix citation-form conventions within a single lexicon (lemma for some, root for others). Pick one + document.
- **NEVER** treat Wiktionary as gold for production work. Useful starting source; quality varies wildly.

## See also

- `references/canonical_sources.md`.
- `magic-linguistic-semantics/references/wordnet_omw.md` — sense inventories at scale.
- `magic-linguistic-semantics/references/mwe_parseme.md` — MWE handling.
- `magic-linguistic-historical/references/canonical_sources.md` — cognate-based lexicon bootstrap.
