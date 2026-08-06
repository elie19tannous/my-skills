# G2P (Grapheme-to-Phoneme) and IPA — Reference

Loaded by `magic-linguistic-speech` Step 2.

## What G2P is

Grapheme-to-phoneme conversion: map orthographic word → phonetic transcription (typically IPA).

Example (English):
- "knight" → /naɪt/
- "thought" → /θɔːt/

For ASR (lexicon construction), TTS (pronunciation control), and lexicography (dictionary entries).

## G2P resources (snapshot 2026-04-23)

### WikiPron
- Crowd-sourced pronunciation pairs from Wiktionary.
- ~3M+ entries across ~200+ languages.
- Best free baseline.
- Quality varies; per-language audit recommended.
- https://github.com/CUNY-CL/wikipron

### CMU Dict
- English baseline.
- High quality; well-maintained.
- ARPABET (English-specific phoneme set), not IPA.

### LanguageNet
- Per-language pronunciation lexicons assembled by Univ. of Washington.
- ~150 languages.
- Mixed quality.

### Per-language community lexicons
- Often the best for low-resource if community has built one.
- Check ELDP / DELAMAN partners.

## IPA conventions per language

IPA is the international standard but implementations vary:

| Language | Notes |
|---|---|
| Mandarin | Pinyin tone marks (ā/á/ǎ/à) used + IPA tone diacritics in some traditions |
| Vietnamese | 6-tone system; pre-syllabic + post-syllabic tone marks vary |
| Yoruba | High/low/mid tones marked with acute/grave/(none) — must preserve |
| Hausa | Tone marking optional in some traditions; standardize per-project |
| Arabic | Vowels often unwritten in orthography; G2P needs vocalization first |
| Hebrew | Same; niqqud optional |
| Turkish | Largely phonemic orthography; G2P near-trivial |
| English | Highly opaque orthography; G2P quality matters most |

## IPA validation

Per-language IPA inventory (which phonemes are valid for the language). Validation:
- Reject IPA strings with phonemes outside the inventory.
- Flag invalid characters (e.g., ASCII letters mixed in, malformed combining marks).
- Tone language: require tone diacritic on vowels.

`scripts/ipa_validate.py` provides per-language inventory check + character validation.

## SIGMORPHON G2P shared tasks

SIGMORPHON 2020-2023 G2P shared tasks established cross-lingual baselines:
- Encoder-decoder neural G2P.
- Per-language model files available for ~50 languages.
- Use as baseline; refine with per-language data.

## Common G2P pitfalls

- **Stripping diacritics before G2P** for tone languages: tone information lost.
- **Using English-trained G2P on a non-English language**: produces garbage IPA.
- **Mixing IPA conventions** (some symbols differ across traditions; ɡ vs g, ʤ vs dʒ etc.) — standardize.
- **Skipping vocalization** for Arabic / Hebrew: G2P from un-vowelized orthography is ambiguous.
- **No IPA validation** on community-contributed lexicons: typos enter the pipeline.

## Tone-language G2P

For Yoruba, Vietnamese, Hausa, Mandarin, Igbo, Twi, Thai:
- Preserve diacritics in orthographic input.
- Output IPA must include tone marks (per-tradition format).
- Reject input with stripped diacritics — fail loud, not silent.

## See also

- **Lee, J., et al.** (2020). *Massively Multilingual Pronunciation Modeling with WikiPron*. LREC.
- **Gorman, K., et al.** SIGMORPHON G2P shared task papers (2020-2023).
- IPA chart (official): https://www.internationalphoneticassociation.org/IPAcharts/IPA_chart_orig/IPA_charts_E.html
