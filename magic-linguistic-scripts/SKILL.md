---
name: magic-linguistic-scripts
description: Decide Unicode normalization policy, detect script confusables, recommend romanization/transliteration, and protect diacritics for the target language. Use whenever the user mentions Unicode, NFC, NFKC, normalization, romanize, transliterate, IAST, Pinyin, Hepburn, IPA, confusable characters, mixed-script text, diacritic restoration, ZWJ/ZWNJ, BOM, or non-Latin script handling. **Use this skill BEFORE any tokenizer training, deduplication, or bitext mining** — silent script issues compound through every downstream step. Routed by magic-linguistic-orchestrator at the start of the Acquire phase and on demand whenever script symptoms appear (garbled output, unknown glyphs, dedup over-merging).
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 1
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - unicode
  - scripts
  - normalization
  - romanization
  - low-resource
  dependencies: []
  scripts:
  - scripts/detect_confusables.py
  - scripts/normalize_text.py
  - scripts/transliterate.py
---

## When to Use

- Setting normalization policy for a target script (NFC vs NFKC).
- Diagnosing garbled output, unknown glyphs, mojibake.
- Pre-deduplication confusable folding (e.g., Cyrillic "а" vs Latin "a").
- Romanization / transliteration table selection.
- Diacritic restoration or preservation for tone languages.
- Multi-script corpus (mixed Devanagari + Latin Hindi, Cantonese in Han + Latin, Kazakh in Cyrillic + Latin).

**When NOT to use:** the script policy is already in `workspace_state.md` and downstream specialists are following it; or the operation is purely byte-level (e.g., gzipping files).

## Decision Tree — Pick The Right Operation

```
Is the user-facing symptom about visible glyphs?
├── YES, characters look wrong / garbled
│   ├── BOM at file start? → strip BOM (UTF-8-SIG handler).
│   ├── Mojibake (Ã©, Ã¢)? → re-decode source with correct charset (latin-1 → utf-8 mismatch).
│   ├── Wrong font / missing glyph? → not your problem (display layer).
│   └── Diacritics dropped? → Restore. NEVER strip from tone languages (Yoruba, Vietnamese).
└── NO, user is asking about a transformation
    ├── About to dedup or mine bitext? → Apply NFC + TR39 confusable folding FIRST.
    ├── About to train tokenizer? → Apply NFC. Decide NFKC per-script (default NO).
    ├── About to evaluate generation against gold? → Match gold's normalization exactly.
    ├── User wants romanized form? → See references/romanization_systems.md per script.
    └── User wants to restore diacritics? → ML model needed (out of scope; flag).
```

## NFC vs NFKC — The Policy Decision

**NFC (Canonical Composition)** is the safe default. It collapses canonically-equivalent forms (e.g., precomposed "é" U+00E9 vs combining "e + ́" U+0065 U+0301). No semantic loss.

**NFKC (Compatibility Composition)** additionally collapses *compatibility* characters: ligatures (ﬁ → fi), superscripts (² → 2), presentation forms, long-s (ſ → s), full-width forms. **NFKC is destructive** — it discards information.

| Script / use case | Recommended | Rationale |
|---|---|---|
| Modern Latin text (English, Spanish, French) | NFC | Safe; no compatibility chars expected |
| Modern Cyrillic (Russian, Ukrainian) | NFC | Same |
| Devanagari, Bengali, Tamil, other Indic | NFC | NEVER NFKC — destroys some conjuncts |
| Arabic / Hebrew | NFC | NEVER NFKC — Arabic presentation forms (FExx) carry rendering info; NFKC collapses |
| CJK ideographic | NFC | NFKC collapses full-width ASCII, traditional ↔ simplified compat forms — usually NOT what you want |
| Historical text (long-s, fi/fl ligatures) | NFC | NFKC destroys long-s distinction |
| Search / dedup ONLY (not training data) | NFKC may be OK | Compatibility-fold for retrieval; keep NFC for storage |

**The rule:** default to NFC. Use NFKC only when you have an explicit reason and document it in `workspace_state.md`.

## TR39 Confusable Folding — When and Why

Unicode TR39 publishes a "skeleton" mapping that folds visually-confusable characters to a single class. Cyrillic "а" (U+0430), Latin "a" (U+0061), and several others map to the same skeleton.

**Apply confusable folding BEFORE deduplication and bitext alignment.** Without it:
- 5-15% of corpus is duplicated under different scripts (especially in mixed-script web crawls).
- Bitext margin scores inflate spuriously when "identical" sentences differ only by confusables.
- "Cleaned" deduped corpus still trains the model on look-alike noise.

Apply with `scripts/detect_confusables.py`. Two modes:
- **fold**: replace all confusables with the canonical skeleton character (destructive; for dedup keys only).
- **detect**: report confusable hits with positions (preserve original text).

**Anti-pattern:** never *store* fold-output as canonical text. The fold is a dedup key, not a substitute for the source.

## Diacritic Handling — Tone Languages Are Non-Negotiable

For these languages, diacritic stripping is **catastrophic data corruption**, not a "cleanup" step:

| Language | Diacritic role | Stripping cost |
|---|---|---|
| Yoruba | High/low tone (á/à), nasal (ọ̀) | Word-level meaning loss; "ọkọ̀" (boat) ≠ "ọkọ" (husband) ≠ "okọ́" (hoe) |
| Vietnamese | 6 tones (á/à/ả/ã/ạ + base) | Random meaning soup |
| Hausa | High/low tone marking (variant: low-only) | Verb / noun ambiguation |
| Mandarin pinyin | 4 tones (mā/má/mǎ/mà) | Same problem |
| Igbo | Tone marking | Same |
| Twi | Tone marking | Same |

For these, BLOCK any cleanup pipeline that calls `unidecode()` or strips combining marks. Add a guard.

For optional-diacritic scripts (Hebrew niqqud, Arabic harakat), document the chosen policy explicitly — both options are valid for different downstream use cases.

## Romanization — Reversibility Matters

For evaluation, debugging, and search, you often need a reversible round-trip from script to Latin. Recommend the right scheme per script:

| Script | Recommended scheme | Reversible? | Notes |
|---|---|---|---|
| Devanagari | IAST | YES (with diacritics) | ISO 15919 is alternative |
| Bengali | IAST | YES | |
| Tamil | ISO 15919 | YES | |
| Greek | ISO 843 | YES | |
| Cyrillic (Russian) | ISO 9 / GOST 7.79 | YES | BGN/PCGN is non-reversible |
| Arabic | ALA-LC or DIN 31635 | Approx | Un-vowelized → ambiguous |
| Hebrew | ISO 259 | Approx | Un-vowelized → ambiguous |
| Hangul | Revised Romanization (2000) | YES | McCune-Reischauer alternative |
| Han (Mandarin) | Pinyin (with tones) | NO | Ambiguous (homophones) |
| Han (Cantonese) | Jyutping | YES (more or less) | Yale alternative |
| Kana | Hepburn | YES | Kunrei-shiki alternative |

**Anti-pattern:** picking a scheme without checking reversibility for your use case. ALA-LC Arabic is great for catalog entries but unsuitable for round-trip-checking a transliteration system.

## Joiner / Anti-joiner (ZWJ / ZWNJ) Policy

These zero-width characters (U+200D, U+200C) carry semantics in many scripts:

| Script | ZWJ / ZWNJ usage |
|---|---|
| Devanagari, Bengali, Tamil | ZWJ forms ligatures; ZWNJ blocks ligatures (e.g., "क्ष" with vs without) |
| Arabic | ZWNJ separates connected forms (e.g., Persian "می‌خواهم") |
| Emoji (modern) | ZWJ joins sequences (e.g., 👨‍👩‍👧) |

**Detect inconsistent usage** with `scripts/detect_confusables.py --include-joiners`. Normalize at acquire-time, NOT at training-time.

## Workflow

### Step 1 — Identify the script(s)
Use Unicode block detection. For multi-script corpora, report per-block percentages.

### Step 2 — Set policy in workspace_state.md

```markdown
## Script Policy: <Language>
- Primary script(s): <Unicode block(s)>
- Normalization: NFC (default) | NFKC (justify) | NFD (rare)
- Diacritics: PRESERVE (tone language) | OPTIONAL | STRIPPABLE
- Romanization scheme: <name> (reversible: yes/no)
- ZWJ/ZWNJ policy: NORMALIZE | PRESERVE
- Confusable folding: FOLD-FOR-DEDUP-ONLY (default) | NONE | FOLD-FOR-STORAGE (rare)
```

### Step 3 — Apply per phase

**MANDATORY READ** [`references/unicode_normalization.md`](references/unicode_normalization.md) before applying NFKC.

| Phase | Apply |
|---|---|
| Acquire (raw → cleaned) | NFC + ZWJ/ZWNJ normalize + BOM strip |
| Pre-dedup | NFC + TR39 confusable fold (fold mode, dedup key only) |
| Pre-tokenize | NFC (already done at Acquire); verify with hash |
| Pre-eval | Match gold's normalization exactly (often NFC; verify with hash) |

### Step 4 — Validate
Hash the canonical text after each phase. Mismatched hashes = silent normalization drift.

## Anti-patterns (NEVER do)

- **NEVER** apply NFKC without script-policy review. NFKC collapses long-s, ligatures, presentation forms, full-width — usually destructive for training data.
- **NEVER** strip diacritics from tone languages (Yoruba, Vietnamese, Hausa, Mandarin pinyin, Igbo, Twi). This is catastrophic data corruption.
- **NEVER** dedup before TR39 confusable folding when corpus is mixed-script. You'll keep look-alike duplicates.
- **NEVER** assume one normalization policy works for an entire multilingual corpus. Per-script policy is the rule.
- **NEVER** call `unidecode()` on training text without explicit per-language sign-off. It strips diacritics + transliterates non-Latin → silent disaster.
- **NEVER** store TR39-folded text as canonical. Folding is a dedup key, not a substitute.
- **NEVER** trust a pipeline that doesn't BOM-strip on file load. UTF-8-SIG → ZWNBSP at column 0 → invisible header mismatches.

## Edge Cases

- **Multi-script corpus** (Indic + English code-switching): per-block policy; report ratios in `workspace_state.md`.
- **Encoding-detected-as-utf8 but actually latin-1**: re-decode; check for "Ã" sequences before accepting.
- **Right-to-left + left-to-right mixed** (Arabic + English in same paragraph): respect bidi marks (U+202A-U+202E); don't strip.
- **Macrolanguage with multiple scripts** (Kazakh: Cyrillic + Latin + Arabic): pick one for training; document conversion if mixing.
- **Text with PUA (Private Use Area) characters** (legacy SIL fonts, pre-Unicode endangered-language docs): convert via known PUA → Unicode mapping; flag if no mapping available.
- **Emoji-heavy text**: normalize via NFC; preserve ZWJ sequences (skin tones, family compositions).

## Output Format

When producing a script-policy recommendation, structure as:

```markdown
## Script Policy Recommendation: <Language>

**Primary script:** <name> (Unicode block <U+xxxx-U+yyyy>)
**Secondary scripts** (if any): <list with %>
**Normalization:** <NFC|NFKC|NFD> — rationale: ...
**Diacritics:** <PRESERVE|OPTIONAL|STRIPPABLE> — reason: ...
**Romanization (if needed):** <scheme>; reversible: <yes|no>
**Confusable risk:** <LOW|MEDIUM|HIGH> — examples: ...
**ZWJ/ZWNJ:** <NORMALIZE|PRESERVE>

**Apply order at Acquire-phase:**
1. <step>
2. <step>
...
```
