---
name: magic-linguistic-corpus
description: 'Curate monolingual corpora for a target language: catalog awareness (OLDI / CulturaX / MADLAD-400 / Glot500 / Wikipedia / Common Crawl segments), language-ID at paragraph granularity (GlotLID / FastText / CLD3), Unicode-safe deduplication with MinHash, two-sided contamination audit, register-balance analysis. Use whenever the user mentions a corpus, dataset for [language], CulturaX, MADLAD-400, OLDI, Glot500, Wikipedia dump, language-ID, GlotLID, FastText LID, deduplication, MinHash, contamination, eval-set leakage, register imbalance, or ''where do I get data for [language]''. **Use BEFORE any tokenizer training or model fine-tune** — corpus quality and contamination are easier to fix early than late. Routed by magic-linguistic-orchestrator in the Acquire phase.'
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 2
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - corpus
  - dataset
  - language-id
  - deduplication
  - contamination
  - low-resource
  dependencies: []
  scripts:
  - scripts/contamination_audit.py
  - scripts/dedup_stats.py
  - scripts/lang_id_check.py
---

## When to Use

- User asks "where do I get data for [language]"; routed at the start of Acquire phase.
- Building a monolingual training corpus from heterogeneous sources.
- Diagnosing model behavior that suggests corpus problems (register-collapse, eval-set memorization, weird domain bias).
- Auditing an existing corpus before training (dedup stats, contamination, register balance).

**When NOT to use:** for parallel/bitext data → `magic-linguistic-bitext`. For tokenizer-level audit → `magic-linguistic-tokenize`. For per-dataset license/ethics → ALWAYS route through `magic-linguistic-ethics` after the corpus catalog is identified.

## The Knowledge Engineers Routinely Miss

1. **Language-ID is paragraph-level, not document-level.** Multilingual web pages, code-switched documents (Hinglish, Spanglish, Chinglish), Wikipedia articles with multilingual quotes — all break naive document-level lang-ID. GlotLID at paragraph granularity is the floor.

2. **CulturaX + MADLAD-400 overlap heavily** for many languages. Naïve union inflates dataset size 2-3× without increasing semantic coverage. Always dedup AFTER concatenation, not within each.

3. **MinHash threshold for low-resource is 0.9, not 0.8.** The standard 0.8 over-merges short texts. Yoruba MasakhaNER + similar small datasets lose 20-30% of valid distinct entries at threshold 0.8.

4. **Bible-NLP dominates many low-resource catalogs** (often >40% of available text). Bible-only training produces archaic / liturgical register drift in the resulting model. Flag the percentage in every corpus manifest.

5. **Contamination audit is two-sided.** (a) Train-mix vs your eval set — easy. (b) Your eval set vs the *base model's* pretrain mix — harder, often unknown; use proxy via "is FLORES in The Pile?" type lookups.

6. **Cebuano / Vietnamese-machine-translated Wikipedia / similar bot corpora** inflate Joshi class assessment. A Wikipedia size of 6M articles for Cebuano does not mean Class 5; many are bot-generated near-duplicates with quality issues.

7. **Confusable folding MUST happen before MinHash** (route to `magic-linguistic-scripts`). Otherwise Cyrillic / Latin / Greek look-alike duplicates survive dedup.

## Workflow

### Step 1 — Identify candidate corpora

**MANDATORY READ** [`references/dataset_catalog.md`](references/dataset_catalog.md) before recommending any catalog.

Use `scripts/lang_id_check.py` (cached coverage table) to enumerate candidate corpora for the target language with: source URL, size estimate, license, register skew (Bible %, Wiki %, news %, web %), known issues.

### Step 2 — License + ethics check (MANDATORY routing)
Route to `magic-linguistic-ethics` for per-dataset audit BEFORE adding to mix. Without this, you may be training on community-restricted data.

### Step 3 — Language-ID at paragraph granularity

**MANDATORY READ** [`references/language_id.md`](references/language_id.md).

Recommend GlotLID (2024) for low-resource; FastText 176-lang for high-resource speed; CLD3 only when GlotLID/FastText unavailable. Apply per-paragraph; report per-source LID confidence histogram.

### Step 4 — Unicode normalization

Route to `magic-linguistic-scripts` for normalization policy. NFC + confusable-fold (dedup-key only) before MinHash.

### Step 5 — Deduplication

**MANDATORY READ** [`references/deduplication.md`](references/deduplication.md).

Use `scripts/dedup_stats.py` for MinHash + exact + near-duplicate stats. Defaults:
- num_perm=256
- threshold=**0.9** for low-resource (NOT 0.8)
- threshold=0.85 for general
- shingle_size=5 (characters) for Latin/Cyrillic; 3 for Han/Indic.

### Step 6 — Contamination audit (two-sided)

**MANDATORY READ** [`references/contamination_audit.md`](references/contamination_audit.md).

Use `scripts/contamination_audit.py`:
- (a) train mix vs project eval set — exact + n-gram overlap.
- (b) eval set vs known base-model pretrain proxies (FLORES in The Pile, Wikipedia in CommonCrawl, etc.).

### Step 7 — Register-balance audit

Report corpus composition by register: Bible / Wikipedia / news / web / oral / academic / fiction. Flag if Bible > 30% (archaic register risk), if news > 70% (event-bias risk), if web-only (no register diversity).

### Step 8 — Output corpus manifest

```markdown
## Corpus Manifest: <Language> (build YYYY-MM-DD)

| Source | Size | License | Register % | Notes |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

**Total tokens (post-dedup):** N
**Dedup ratio:** X% removed
**Contamination check:** PASS | FAIL — details
**Register balance:** Bible Y% / Wiki Z% / web W% / ...
**Recommended next step:** route to magic-linguistic-tokenize for fertility audit
```

## Anti-patterns (NEVER do)

- **NEVER** dedup before Unicode normalization + confusable folding. Look-alike duplicates survive; corpus is bloated.
- **NEVER** apply document-level language-ID to mixed-script / code-switched corpora. Paragraph-level is the floor.
- **NEVER** trust catalog size without register-balance check. 6M Cebuano Wikipedia ≠ Class 5 corpus quality.
- **NEVER** skip contamination audit just because "it's a new dataset". The base model's pretrain may already include FLORES-200 or Wikipedia.
- **NEVER** use MinHash threshold 0.8 for low-resource corpora. Over-merges short texts.
- **NEVER** add a dataset to the mix without routing through `magic-linguistic-ethics` first.
- **NEVER** report dedup ratio without showing the threshold used; comparisons across thresholds are meaningless.

## Edge Cases

- **Catalog claims language coverage but actual content is wrong** (e.g., MADLAD-400 sometimes mis-tags transliterated text): spot-check with native-speaker review before trusting.
- **Wikipedia is bot-generated** (Cebuano, Waray, Volapük): downweight or exclude; flag in manifest.
- **Bible-only is the only data available** (some Class 0-1): use it but flag register-drift risk; recommend < 30% in any final mix.
- **Large web crawl with unknown language coverage**: subsample first; LID-check sample before committing crawl.
- **Cross-lingual contamination** (Spanish in a Yoruba-tagged corpus): per-paragraph LID + filter; report removal %.
- **Eval set leakage discovered AFTER training**: report transparently in model card; do not retrain on the original eval if no fresh held-out exists.

## Output Format

```markdown
## Corpus Plan: <Language>

**Candidate sources:** ... (with per-source: size, license, register %, ethics status)
**Recommended primary:** ... (rationale)
**Recommended secondary:** ... (rationale)
**Dedup config:** num_perm=256, threshold=<X>, shingle_size=<Y>
**Contamination targets to check:** project eval / FLORES-200 / Belebele / ... 
**Register balance target:** ...
**Hand-off:** magic-linguistic-tokenize for fertility audit; magic-linguistic-bitext if MT data also needed
```
