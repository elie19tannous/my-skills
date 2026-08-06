# FST Analyzers (HFST / foma / Apertium) — Reference

Loaded by `magic-linguistic-morph` Step 4.

## What FST analyzers are

Finite-state transducers that map between surface form and analyzed form. Fast (microseconds per word), deterministic, exhaustive. Built by linguists; rule-based.

Example (Finnish):
```
Input:  taloissa  (in the houses)
Output: talo+N+Pl+Iness
```

## Toolkits

- **HFST** (Helsinki Finite-State Toolkit). https://hfst.github.io/. Open-source, mature, ~50+ analyzers available.
- **foma**. https://fomafst.github.io/. Alternative with simpler syntax; smaller user base.
- **Xerox XFST** (legacy proprietary).
- **Apertium** repos. https://github.com/apertium. MT-focused; analyzers + transfer rules for ~150 languages.

## Coverage (snapshot 2026-04-23)

Languages with usable FST analyzers via HFST or Apertium:
- **Excellent**: Finnish, Sami (all variants), Karelian, Erzya, Komi, Mari, Udmurt, Faroese, Greenlandic.
- **Good**: Many Turkic (Tatar, Bashkir, Sakha), most Uralic, Quechua varieties via Apertium.
- **Decent**: Arabic via SAMA / HFST-Arabic; Persian; Welsh; Irish.
- **Limited**: Most Indigenous Americas (some Quechua, some Nahuatl); some Bantu.

When you find an FST: use it. Quality is usually high (linguist-built).

## When NOT to build an FST

Building an FST from scratch is:
- 6-12+ months for a competent linguist.
- Requires deep grammar knowledge of the target.
- Maintenance burden ongoing.

For ML-only purposes (tokenization, augmentation), SIGMORPHON segmenter is faster path.

When TO build (or pay to build):
- Endangered language preservation project.
- Long-term commercial deployment.
- Field documentation outputs that will outlast ML projects.

## Integration patterns

1. **Preprocessing**: FST-segment training corpus, then tokenize. Best fertility reduction.
2. **Lemmatization**: FST-lemmatize for morphological tagger training.
3. **Generation**: FST-generate inflected forms (paradigm completion at scale).
4. **Validation**: FST round-trip checks for synthetic data.

## Common pitfalls

- **Legacy SIL PUA fonts**: many Apertium analyzers use PUA characters from older SIL fonts. Convert to Unicode before integration.
- **Encoding mismatches**: HFST + foma both expect UTF-8; some legacy data is Windows-1252 or similar.
- **Coverage holes**: FSTs handle in-vocabulary forms; OOV needs fallback (SIGMORPHON segmenter).
- **Ambiguity**: FSTs return ALL valid analyses; downstream needs disambiguation (HMM tagger, morphological context model).

## Refresh

- HFST releases ~quarterly; Apertium continuously.
- New endangered-language FSTs added by community; check ELDP / DELAMAN partnerships.

## See also

- **Lindén, K., et al.** (2009). *HFST Tools for Morphology*.
- **Hulden, M.** (2009). *Foma: a finite-state compiler and library*. EACL demo.
- **Forcada, M. L., et al.** (2011). *Apertium: a free/open-source platform for rule-based machine translation*. Machine Translation.
- Apertium GitHub: https://github.com/apertium
