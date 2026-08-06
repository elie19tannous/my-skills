# WordNet / Open Multilingual WordNet (OMW) — Reference

Loaded by `magic-linguistic-semantics` Step 1.

## What WordNet is

Princeton WordNet (English) — lexical database where words are grouped into synsets (sets of synonyms representing one meaning). Each synset has POS, definition, examples, hypernyms, hyponyms, etc.

Open Multilingual WordNet (OMW) extends this to ~100+ languages with per-language synset alignment to English Princeton WordNet. Coverage is uneven.

## Princeton WordNet stats
- ~117,000 synsets.
- ~155,000 lemmas.
- 4 POS (n, v, adj, adv).
- Decades-mature, foundational for English NLP semantics.

## OMW per-language coverage (snapshot 2026-04-23)

Coverage is reported as % of Princeton synsets aligned. Uneven across languages.

| Language | Synsets | % vs Princeton |
|---|---|---|
| Spanish | 38,000 | 32% |
| French | 33,000 | 28% |
| Italian | 35,000 | 30% |
| Portuguese | 41,000 | 35% |
| Mandarin | 42,000 | 36% |
| Japanese | 56,000 | 48% |
| Hindi | 28,000 | 24% |
| Bengali | 27,000 | 23% |
| Arabic | 9,000 | 8% |
| Hebrew | 8,000 | 7% |
| Korean | 16,000 | 14% |
| Vietnamese | 10,000 | 9% |
| Thai | 8,000 | 7% |
| Indonesian | 14,000 | 12% |
| Tamil | 4,000 | 3% |
| Yoruba | 5,000 | 4% |
| Swahili | 4,000 | 3% |
| Khmer | absent | 0% |
| Twi | absent | 0% |
| Inuktitut | absent | 0% |
| Cherokee | absent | 0% |

## Coverage gaps

Don't assume English WordNet downstream tasks (WSD, hypernym retrieval, taxonomy-based reasoning) work for low-resource languages. The lookup will silently return None for missing synsets.

## When OMW is absent

Options:
1. **Bilingual lexicon + manual sense annotation**: cheapest; build a 1-5K sense inventory.
2. **Cross-lingual embedding-based "sense" approximation**: use LaBSE or sentence-transformers to cluster usages.
3. **MultiWordNet** (smaller alternative project): may have coverage Princeton OMW lacks.
4. **Community-contributed sense inventories** via projects like Masakhane (African languages).

## RAG / retrieval implications

If your RAG pipeline uses synset-based query expansion (e.g., look up synonyms via WordNet to broaden retrieval), your low-resource queries fail silently. Either:
- Restrict synset-based expansion to high-coverage languages.
- Use cross-lingual embedding similarity instead.

## Tooling

- **NLTK WordNet API** (Python): `nltk.corpus.wordnet`. Includes OMW.
- **WN-Multi** (Bond & Foster 2013): aggregator.
- **MultiWordNet**: alternative project.

## Refresh

OMW receives updates ~annually but slowly; many low-resource entries unchanged for years. Check before assuming current coverage.

## See also

- **Fellbaum, C.** (ed.) (1998). *WordNet: An Electronic Lexical Database*. MIT Press.
- **Bond, F., & Foster, R.** (2013). *Linking and Extending an Open Multilingual Wordnet*. ACL.
- Princeton WordNet: https://wordnet.princeton.edu/
- OMW: http://compling.hss.ntu.edu.sg/omw/
