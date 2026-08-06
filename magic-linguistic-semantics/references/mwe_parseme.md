# Multi-Word Expressions & PARSEME — Reference

Loaded by `magic-linguistic-semantics` Step 3.

## What MWEs are

A multi-word expression is a sequence of words that act as a single semantic unit, where the meaning is NOT compositional from the parts:

- "kick the bucket" (= die; not = kick + bucket).
- "raining cats and dogs" (= raining heavily).
- "let the cat out of the bag" (= reveal a secret).
- "by and large" (= mostly).

Plus light-verb constructions ("take a walk", "give a smile"), phrasal verbs ("put up with"), serial verbs (Yoruba, Akan), idiomatic prepositional phrases.

## Why MWE handling matters

In MT: literal translation produces nonsense. "Kick the bucket" → "patear el cubo" (Spanish) is wrong; should be "estirar la pata" (= "stretch the paw").

Estimates: 30-50% of MT errors on idiomatic text trace to MWE mishandling. For idiomatic-rich text (literature, conversation, news editorials), this is dominant.

## PARSEME shared task

Per-language MWE catalogs + tagged corpora across ~20 languages. Categories:
- Verbal MWEs (light verbs, idioms, inherently reflexive verbs).
- Nominal MWEs.
- Idioms.

Coverage:
- Strong: French, German, Polish, Czech, Slovenian, Bulgarian, Hindi, Turkish, Persian, Romanian, etc.
- Partial: ~10 more.
- Absent: most class 0-2.

## Treatment patterns

### 1. Pre-tokenize MWEs as units

Before BPE / SentencePiece, replace known MWEs with single tokens (e.g., `<mwe_kick_the_bucket>`). Then translate as units.

Tradeoff: closes vocabulary; brittle for variant forms ("kicked the bucket", "kicks the bucket").

### 2. Inline MWE tags during training

Tag MWE spans during training; let model learn to handle them. Less brittle than pre-tokenize; needs PARSEME-tagged training data.

### 3. Post-translation idiom replacement

Translate text; post-process to replace literal-translated MWEs with target-language equivalents. Requires bilingual idiom dictionary.

## Per-language MWE strategies

| Family | MWE type | Treatment |
|---|---|---|
| Indo-European Western | Idioms + light verbs + phrasal | PARSEME shared-task data; pre-tokenize when reliable |
| Slavic | Inherently reflexive verbs + idioms | PARSEME shared task |
| Bantu (Yoruba, Twi, Swahili) | Serial verbs (V+V acting as single unit) | Custom catalog needed; route to community |
| Mandarin | Chengyu (4-character idioms) | Large dedicated chengyu catalogs exist; pre-tokenize |
| Japanese | Yojijukugo (4-character idioms); idioms | Pre-tokenize; use existing dictionaries |
| Indic | Compound verbs + idioms | PARSEME has Hindi/Marathi |
| Templatic Semitic | Construct state + idioms | Per-language; root-pattern interacts |

## Building a low-resource MWE catalog

1. Extract candidate MWEs from corpus via collocation statistics (PMI, t-score).
2. Native-speaker review for idiomaticity.
3. Categorize by type (light verb, idiom, etc.).
4. Add bilingual equivalents for MT.
5. 500 entries is a useful starting size.

## Anti-patterns

- **Treating MWE spans as 3 unrelated content words**: silent translation failure.
- **Building MWE catalog without native-speaker review**: collocations ≠ idioms.
- **Same treatment for all MWE types**: light verbs differ from idioms differ from collocations.
- **Pre-tokenizing variant-friendly MWEs as fixed strings**: brittle.

## See also

- **Sag, I. A., et al.** (2002). *Multiword Expressions: A Pain in the Neck for NLP*. CICLing.
- **Constant, M., et al.** (2017). *Multiword Expression Processing: A Survey*. Computational Linguistics.
- **Savary, A., et al.** (2017). *The PARSEME Shared Task on Automatic Identification of Verbal Multiword Expressions*. MWE Workshop.
- PARSEME: http://parseme-fr.lif.univ-mrs.fr/
- PARSEME GitHub: https://gitlab.com/parseme
