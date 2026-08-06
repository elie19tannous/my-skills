---
name: magic-linguistic-historical
description: 'Historical / comparative linguistics primitives for ML data augmentation: cognate sets across related languages, Swadesh lists for cheap bilingual-lexicon bootstrapping, regular sound-correspondence rules. Use whenever the user mentions cognates, Swadesh, comparative method, sound correspondence, proto-language, language family, LingPy, NorthEuraLex, IE-CoR, BDPROTO, CogNet, or asks ''are languages X and Y close enough that I can bootstrap data via cognates?''. Optional Mindset specialist.'
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
  - historical
  - comparative
  - cognates
  - swadesh
  - low-resource
  - optional
  dependencies: []
---

## When to Use

- Class 0-1 target language; need bilingual lexicon from related-language cognates.
- Bootstrapping bitext from Swadesh-list pairs.
- Validating typological-distance recommendations from `magic-linguistic-scope`.
- Cognate-based data augmentation between related-language pairs.

**When NOT to use:** Class 3+ language → standard data ample; cognate bootstrap not needed. Pure typology lookup → `magic-linguistic-scope`.

## Stance

Comparative-historical linguistics is decades-mature. For low-resource ML, the operationalizable primitives are: **cognate sets, Swadesh lists, sound correspondences**. Use them as cheap data-augmentation tools when you have a related higher-resource language to draw from.

## What's worth knowing

1. **Cognate sets** — etymologically-related word pairs across related languages. Spanish "noche" ↔ Italian "notte" ↔ French "nuit" ↔ Portuguese "noite" — same Latin source, predictable sound shifts. For class 0-1, cognate sets bootstrap bilingual lexicons cheaply.

2. **Swadesh lists** — 100-word / 200-word core-vocabulary lists. Standard starting point for class 0 bilingual-lexicon work. NOT a complete lexicon; a starting bootstrap.

3. **Regular sound correspondences** — Grimm's Law (Germanic), Proto-Bantu reflexes, etc. Encode as rewrite rules → automatic cognate detection or augmentation between related-language pairs.

4. **Data sources** (snapshot 2026-04-23):
   - **LingPy** — Python comparative-linguistics toolkit; cognate-detection algorithms.
   - **NorthEuraLex** — large cognate database for Eurasian languages.
   - **IE-CoR** — Indo-European Cognate Relationships database.
   - **BDPROTO** — proto-language phoneme inventories.
   - **CogNet** — multilingual cognate database.

5. **"Related" ≠ "mutually intelligible"** — Italian and Romanian are both Romance, but speakers don't understand each other. Typological proximity ≠ usable bilingual-lexicon directly.

6. **Cognate-based augmentation** is highest-value when (a) target is class 0-1, (b) source is class 3+, (c) URIEL distance < 0.3 (cross-reference `magic-linguistic-scope`).

## Anti-patterns (NEVER do)

- **NEVER** assume "related" languages are mutually intelligible. Proximity ≠ overlap.
- **NEVER** use Swadesh list as production lexicon — it's a starting bootstrap.
- **NEVER** apply sound-correspondence rules across unrelated language families. Garbage out.
- **NEVER** over-rely on cognate-bootstrap for cultural / technical / modern-life vocabulary — Swadesh covers core; modern terms diverge.

## See also

- `references/canonical_sources.md`.
- `magic-linguistic-scope/references/transfer_source_selection.md` for URIEL-based source picking.
- `magic-linguistic-bitext` for cognate-based bitext synthesis.
