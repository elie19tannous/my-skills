# Canonical Sources — magic-linguistic-scripts

Maintainer-facing reading list. Snapshot 2026-04-23.

## Unicode standards (always-current authoritative source)

- **The Unicode Consortium**. *The Unicode Standard, Version 15.1* (2023, with errata through 2026). https://www.unicode.org/versions/Unicode15.1.0/
- **Unicode Standard Annex #15** (Normalization Forms): https://unicode.org/reports/tr15/
- **Unicode Technical Standard #39** (Confusables): https://unicode.org/reports/tr39/
- **Unicode Technical Standard #46** (IDNA Compatibility Processing): https://unicode.org/reports/tr46/

## Scripts and writing systems

- **Daniels, P. T., & Bright, W.** (eds.) (1996). *The World's Writing Systems*. Oxford University Press. (2nd edition forthcoming.)
- **Coulmas, F.** (2003). *Writing Systems: An Introduction to Their Linguistic Analysis*. Cambridge University Press.
- **Rogers, H.** (2005). *Writing Systems: A Linguistic Approach*. Wiley-Blackwell.

## Practical Unicode for engineers

- **Gillam, R.** (2002). *Unicode Demystified: A Practical Programmer's Guide*. Addison-Wesley.
- **Allen, J. D., et al.** *The Unicode Standard, Version X — Code Charts*. (Always reference current version.)

## Romanization references

- **ALA-LC Romanization Tables**, Library of Congress. https://www.loc.gov/catdir/cpso/roman.html
- **ISO 9** (Cyrillic), **ISO 15919** (Indic), **ISO 259** (Hebrew), **ISO 843** (Greek), **ISO 233** (Arabic).
- **Aksharamukha documentation**: https://github.com/virtualvinodh/aksharamukha-python
- **Hepburn romanization** (Japanese), Library of Congress version: https://www.loc.gov/catdir/cpso/romanization/japanese.pdf

## Tools and libraries

- **PyICU** (Python wrapper for ICU): https://pyicu.org/
- **Aksharamukha**: https://github.com/virtualvinodh/aksharamukha-python (best Indic-script transliteration)
- **confusable_homoglyphs**: https://github.com/vhf/confusable_homoglyphs
- **unicodedata** (Python stdlib): always available; covers NFC/NFD/NFKC/NFKD.
- **Lhotse** (audio + text pipeline): https://github.com/lhotse-speech/lhotse (handles BOM correctly)

## Specific script references

- **Indic**: Salomon, R. (1998). *Indian Epigraphy*. Oxford. + the Aksharamukha documentation for practical transliteration.
- **Arabic**: Versteegh, K. (2014). *The Arabic Language* (2nd ed.). Edinburgh.
- **CJK**: DeFrancis, J. (1989). *Visible Speech: The Diverse Oneness of Writing Systems*. Hawaii.
- **Korean Hangul**: Lee, I., & Ramsey, S. R. (2000). *The Korean Language*. SUNY Press.

## Refresh procedure

- Pinned Unicode version: 15.1 (cached behavior in scripts).
- Confusables snapshot: TR39 cached 2026-04-23.
- Update annually when new Unicode versions release (typical: September).
- Aksharamukha + ICU follow Unicode releases; refresh after major upgrades.
