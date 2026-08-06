---
name: magic-linguistic-bitext
description: Mine, align, filter, and synthesize parallel corpora for low-resource MT. Use whenever the user mentions parallel data, bitext, sentence alignment, LASER3, SONAR, Vecalign, hunalign, Bleualign, NLLB mining, CCMatrix, CCAligned, FLORES, OPUS, back-translation, dictionary substitution, MT pivoting, synthetic parallel, or asks about translation between English and a low-resource language. **Use BEFORE training any MT model on a low-resource pair** — alignment threshold + register balance choices made here cascade through every downstream eval. Routed by magic-linguistic-orchestrator in the Acquire phase.
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
  - bitext
  - parallel-data
  - mt
  - alignment
  - low-resource
  dependencies: []
  scripts:
  - scripts/alignment_score.py
  - scripts/synthetic_bitext_recipes.py
---

## When to Use

- Building MT data for any low-resource pair.
- Mining parallel sentences from comparable corpora.
- Choosing alignment tool (Vecalign vs hunalign vs Bleualign).
- Generating synthetic bitext via back-translation, dictionary substitution, or pivoting.
- Auditing existing parallel data quality (margin scores, register skew, length filtering).

**When NOT to use:** for monolingual corpus → `magic-linguistic-corpus`. For tokenizer fertility on the bitext output → `magic-linguistic-tokenize`. For ethics/license per source → `magic-linguistic-ethics`.

## The Knowledge Engineers Routinely Miss

1. **Vecalign beats hunalign for low-resource.** Linear-time + state-of-the-art on Bible-parallel data. Use hunalign only when retrofitting an existing pipeline.

2. **Margin threshold 1.06 (NLLB published "clean") over-filters Class 0-1.** Use 1.04 + manual spot-check of 50 pairs. The published threshold optimizes for high-resource pairs; low-resource needs gentler filtering or you lose half your usable data.

3. **LASER3 has coverage gaps on Bantu and Indigenous Americas.** SONAR (Meta 2024) is better for those families. Don't default to LASER3 for everything.

4. **Back-translation temperature matters.** T=0 produces translationese drift (model parrots English source structure into target); T=0.7-1.0 introduces useful diversity. Always > 0.

5. **Bible-only bitext = archaic/liturgical MT register.** Even with high-quality Bible parallel, the resulting MT will sound 17th-century. Mix ≥ 10% non-Bible parallel for general-purpose MT. This is the dominant low-resource MT failure mode.

6. **Synthetic pivoting** (English → German → Yoruba via high-quality En→De + decent De→Yor) often beats direct En→Yor when the intermediate pair is dramatically better-resourced.

7. **Length-ratio filtering** (target/source word ratio) catches alignment errors that margin filtering misses. Outside [0.5, 2.0] ratio = likely misaligned. Catches ~5% of false matches.

## Workflow

### Step 1 — Identify the language pair + resource class
Route to `magic-linguistic-scope` if not already done. Pair-level resource class (per-direction) determines the recipe.

### Step 2 — Choose mining pipeline

**MANDATORY READ** [`references/mining_recipes.md`](references/mining_recipes.md).

| Source family | Recommended embedding | Recommended aligner |
|---|---|---|
| European Latin/Cyrillic | LASER3 | Vecalign |
| Indic | LASER3 / SONAR | Vecalign |
| African (Bantu, Niger-Congo) | **SONAR** (LASER3 has gaps) | Vecalign |
| Indigenous Americas | **SONAR** | Vecalign |
| SEA (Khmer/Lao/Burmese/etc.) | LASER3 | Vecalign |
| CJK | LASER3 | Vecalign |
| Mixed-script source | SONAR (handles better) | Vecalign |

### Step 3 — Choose / adjust margin threshold

**MANDATORY READ** [`references/alignment_tools.md`](references/alignment_tools.md).

| Pair type | Margin threshold |
|---|---|
| Class 4-5 ↔ Class 4-5 | 1.06 (NLLB standard) |
| Class 3 ↔ Class 4-5 | 1.05 |
| Class 1-2 ↔ Class 4-5 | **1.04** + manual spot-check |
| Class 0-1 ↔ anything | **1.03** + manual spot-check + length-ratio filter |

Always document threshold + sample-size of spot check in workspace_state.md.

### Step 4 — Length-ratio + sentence-length filtering

Apply after margin filter:
- Length ratio (target_words / source_words): keep [0.5, 2.0] for typologically-similar; widen to [0.3, 3.0] for distant pairs (English-Inuktitut polysynthesis can push 0.3).
- Min sentence length: 3 words target.
- Max sentence length: 200 source words (tokenizer / model context limits).

### Step 5 — Synthetic bitext (if needed)

**MANDATORY READ** [`references/synthetic_bitext.md`](references/synthetic_bitext.md).

When real parallel < 100K pairs:
1. **Back-translation**: train target→source on real pairs; back-translate target monolingual → synthetic source. Use T=0.7-1.0.
2. **Dictionary substitution**: glossary-constrained word/phrase swap on source; target left as-is.
3. **Pivot MT**: route through better-resourced intermediate (En → De → Yor when En-De is much stronger than En-Yor).

### Step 6 — Register-balance audit

| Source register | % of mix | Action |
|---|---|---|
| Bible-NLP / liturgical | > 30% | Flag archaic-register risk; reduce or supplement |
| News only | > 70% | Flag event-bias; supplement with general |
| Subtitles only | > 50% | Flag conversational-skew; supplement |
| Wikipedia / encyclopedic | > 60% | Flag domain-narrow; OK for many uses |
| Mixed (Bible 20% / news 30% / web 40% / Wiki 10%) | balanced | Acceptable |

### Step 7 — Output bitext manifest + hand off

Hand off to `magic-linguistic-tokenize` for fertility audit on the bitext target side, and `magic-linguistic-transfer` for adapter/LoRA planning.

## Anti-patterns (NEVER do)

- **NEVER** use NLLB margin 1.06 uncritically for class 0-1 pairs. You'll discard half your usable data.
- **NEVER** back-translate with T=0. Translationese drift collapses output diversity.
- **NEVER** assume LASER3 covers all languages. Bantu and Indigenous Americas need SONAR.
- **NEVER** skip length-ratio filtering after margin filter. Margin alone misses ~5% of misalignments.
- **NEVER** train MT on Bible-only bitext for general-purpose MT. The register drift is severe.
- **NEVER** use hunalign for new low-resource projects. Vecalign is better; hunalign is legacy-only.
- **NEVER** report alignment recall without pairing it with manual spot-check sample size.

## Edge Cases

- **Polysynthetic target** (Inuktitut from English): length ratio 0.3-0.5 is normal; don't filter as misalignment.
- **No usable real parallel** (Class 0): synthetic-only is acceptable for prototyping; document as "synthetic baseline" in eval.
- **Cross-script pair** (Devanagari ↔ Latin): sentence aligner handles it; tokenizer downstream needs care.
- **Document-aligned but not sentence-aligned** (parallel Wikipedia articles): use Vecalign in document-mode; report alignment-recall separately.
- **Right-to-left ↔ Left-to-right** (Arabic ↔ English): aligners handle it; downstream visualization may need bidi handling.
- **Heavy code-switching** (Hinglish chat data): paragraph-level alignment first; sentence-level may not be meaningful.

## Output Format

```markdown
## Bitext Plan: <Source> ↔ <Target>

**Source pair class:** Class <N> ↔ Class <M>
**Recommended embedding:** LASER3 | SONAR — rationale: ...
**Recommended aligner:** Vecalign — rationale: standard for LR
**Margin threshold:** <X> + manual spot-check (N samples)
**Length-ratio filter:** [<min>, <max>]
**Min/max sentence length:** [<min>, <max>] words
**Synthetic bitext needed?** YES | NO — strategy: ...
**Register balance target:** Bible <X%>, news <Y%>, ...
**Estimated final pairs:** ~N
**Hand-off:** magic-linguistic-tokenize for fertility audit; magic-linguistic-transfer for adapter strategy
```
