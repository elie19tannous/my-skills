# Romanization Systems — Reference

Loaded by `magic-linguistic-scripts` when picking or auditing a romanization scheme.

## Selection criteria

For each romanization need, ask:

1. **Reversible?** Can I get back to the original script without information loss? (Critical for round-trip eval and ML pipelines that may need to reverse.)
2. **Standard compliance?** Is there a national/international standard? (Affects sharing data.)
3. **Tone preservation?** For tone languages, does the scheme keep tone marks? (Critical.)
4. **Vowels?** For abjads (Arabic, Hebrew), are short vowels preserved? (Often not — accept ambiguity or use a fully-vocalized variant.)
5. **Existing tooling?** Does ICU / Aksharamukha / uroman support it well? (Saves implementation time.)

## Per-script recommendations

### Devanagari (Hindi, Marathi, Sanskrit, Nepali)
- **IAST** (International Alphabet of Sanskrit Transliteration): scholarly standard; reversible with diacritics (ā, ī, ū, ṛ, ṃ, ḥ, etc.). Best for ML pipelines.
- **ISO 15919**: closely related to IAST; broader script coverage. Recommend for ISO-compliance needs.
- **ITRANS**: ASCII-only (uses combinations like "aa" for ā). Good for plain-text input methods, less good for downstream ML.
- **Avoid**: Hunterian (UK colonial-era; lossy), HK transliteration (mixes scripts).

### Bengali, Tamil, Telugu, Kannada, Malayalam, Gujarati, Punjabi (other Indic)
- **ISO 15919** is the consistent choice across all Indic scripts. Reversible.
- **IAST** also works for most.
- **Tooling**: Aksharamukha is the best Python library covering 30+ Indic scripts.

### Arabic
- **ALA-LC** (Library of Congress): library standard; mostly reversible with vocalization marks; widely understood.
- **DIN 31635**: German DIN standard; cleaner than ALA-LC for some letters.
- **Buckwalter**: 1-to-1 ASCII transliteration; reversible; ugly but unambiguous; standard in NLP research.
- **Without harakat (vowel marks)**: any transliteration is ambiguous (3-5 valid readings per word). Note this in workspace_state.md.

### Hebrew
- **ISO 259**: scholarly; reversible with niqqud.
- **SBL Academic**: biblical-studies-flavored; widely cited.
- **Without niqqud**: same ambiguity problem as un-vowelized Arabic.

### Mandarin (Han)
- **Pinyin** with tone marks (mā má mǎ mà): standard. Reversible *for pronunciation* but NOT for character (homophones: 媽妈麻 all are mā).
- **Hanyu Pinyin** without tones: easier to type but loses information. Avoid for ML.
- **Wade-Giles**: legacy; Tang-era spellings; do not use for new work.

### Cantonese (Han)
- **Jyutping**: LSHK-standard; numeric tones (1-6); cleanly reversible from pronunciation.
- **Yale**: older; uses diacritics; cleaner-looking.
- **Avoid**: Cantonese Pinyin (Catholic-school variant; not widely used).

### Kana / Hiragana / Katakana (Japanese)
- **Hepburn** (modified): standard outside Japan; reversible.
- **Kunrei-shiki**: Japanese national standard; reversible.
- **Wapuro**: typing-method (uses "tu" for つ); not reversible without context.

### Hangul (Korean)
- **Revised Romanization (2000)**: South Korean national standard; reversible from pronunciation; preferred for new work.
- **McCune-Reischauer**: scholarly; preserves more phonological distinctions; uses diacritics.
- **Yale Romanization**: linguistics-research-focused; preserves morphology; bookish.

### Greek
- **ISO 843**: standard; reversible.
- **ELOT 743**: Greek national standard; very similar to ISO 843.

### Cyrillic
- **ISO 9** (1995): one-to-one with diacritics; fully reversible.
- **GOST 7.79**: Russian national standard; one-to-one variant available.
- **BGN/PCGN**: US/UK government standard; *non-reversible* (some letters merge); widely used for English-language news.
- **Scientific transliteration** (Slavonic-flavored): used in linguistics papers.

### Cherokee, Inuktitut Syllabics, Canadian Aboriginal Syllabics
- **Romanizations exist** (Cherokee uses transliterations; Inuktitut has dual ortho — syllabics + Roman). For ML, consider whether you want to train on syllabics directly (preferred for community data) or romanized (easier for cross-lingual transfer). Document the choice.

## Common pitfalls

- **Using a non-reversible scheme for round-trip eval.** If your pipeline needs to verify "model output ↔ gold" by transliteration, you must use a reversible scheme.
- **Mixing schemes within the same dataset.** "Beijing" (Hanyu Pinyin) vs "Peking" (Wade-Giles) → both refer to the same place. Consistent normalization required.
- **Stripping tone marks "for simplicity"** in Pinyin / Vietnamese / Yoruba romanization. Information loss.
- **Treating IAST diacritics as ASCII (\bar{a} → "a")** in storage. Loss again.
- **Assuming Aksharamukha defaults are right for your script.** Check the source/target scheme; library defaults differ.

## Tooling

| Tool | Coverage | Notes |
|---|---|---|
| `aksharamukha` (Python) | 100+ Indic scripts + many others | Best Indic; round-trip support |
| `pykakasi` (Python) | Japanese kana ↔ romaji | Hepburn standard |
| `pinyin` (Python) | Mandarin Han → Pinyin | Tone-numeric or tone-mark |
| `ICU` (cross-lang) | Most ISO standards | Use via `PyICU` |
| `uroman` (Perl) | 100+ scripts | One-to-many uniqueness; NOT reversible |
| `xeger`, `transliterate` | various | Smaller; check coverage per script |

For most ML pipelines targeting low-resource languages, **Aksharamukha (Indic) + ICU (everything else)** is the go-to combination.
