# Alignment Tools — Reference

Loaded by `magic-linguistic-bitext` Step 3.

## Tool comparison

| Tool | Method | Speed | Best for | Avoid for |
|---|---|---|---|---|
| **Vecalign** | Embedding DP-overlap | O(n) per doc | New low-resource projects | nothing — current SoTA |
| **hunalign** | Length-based | O(n²) | Legacy pipelines | New work |
| **Bleualign** | MT-translate + BLEU-align | O(n²) | When MT baseline exists | Class 0-1 |
| **GMA** (Gale-Church) | Length-based DP | O(n) | Historical / academic | New low-resource |
| **awesome-align** | Word-level alignment | varies | Word alignment within pairs | Sentence alignment |

For sentence alignment in new projects: **Vecalign by default**.

## Margin threshold guide (with reasoning)

The published "clean" threshold from NLLB 2022 is 1.06. This was tuned for high-resource pairs where you have abundant data and want to throw away anything questionable.

For low-resource, this is wrong — you don't have data to spare. Lower thresholds + manual spot-check produce more usable data with controlled false-positive rate:

| Pair description | Margin | Rationale |
|---|---|---|
| Both sides Class 4-5 (e.g., En-Fr) | 1.06 | NLLB default |
| One side Class 3 (e.g., En-Sw) | 1.05 | Slight relaxation |
| One side Class 1-2 (e.g., En-Yor) | 1.04 | Most pairs found this way still good; spot-check 50 |
| One side Class 0-1 (e.g., En-Iku) | 1.03 | Aggressive; spot-check 100 + length-ratio mandatory |

**Always document the chosen threshold + spot-check sample size in workspace_state.md.** Without these, your bitext quality is unreproducible.

## Manual spot-check protocol

After mining N pairs at margin T:

1. Random-sample 50-100 pairs.
2. Native-speaker (or yourself if competent) reviews: is each pair a valid translation?
3. Compute precision: valid / total. Threshold for go/no-go: ≥ 90% precision.
4. If precision < 90%, raise margin or filter further.
5. Document precision % in manifest.

## Length-ratio filter (post-alignment)

Apply AFTER margin filter:

```python
def length_ratio_ok(source: str, target: str, lang_pair: str) -> bool:
    s_words = len(source.split())
    t_words = len(target.split())  # NOTE: not meaningful for space-less scripts; use char count
    if s_words == 0 or t_words == 0:
        return False
    ratio = t_words / s_words
    # Default range; adjust for distant typology
    DEFAULTS = {"close": (0.5, 2.0), "moderate": (0.4, 2.5), "distant": (0.3, 3.0), "polysynthetic": (0.2, 1.5)}
    bracket = pair_typology(lang_pair)  # close / moderate / distant / polysynthetic
    lo, hi = DEFAULTS[bracket]
    return lo <= ratio <= hi
```

Polysynthetic targets (Inuktitut, Navajo) routinely have ratio 0.3 from English — this is correct, not misalignment.

## Vecalign output interpretation

Vecalign returns alignments + scores (lower = better; not normalized).

- Score 0 → exact 1-1 perfect match.
- Score 0-0.3 → high-confidence alignment.
- Score 0.3-0.6 → moderate; usable.
- Score > 0.6 → low confidence; review or discard.

For low-resource, accept up to 0.6 with downstream length-ratio + LID filters.

## Common alignment failures

| Failure | Symptom | Fix |
|---|---|---|
| Document misalignment cascade | Sentences shift by 1-2 throughout | Check document boundaries; re-sentence-segment |
| Header/footer pollution | Boilerplate pairs (page numbers, dates) | Strip per-document headers/footers before alignment |
| Embedded HTML / formatting | Tags appear in source but not target | Pre-strip HTML; preserve sentence boundaries |
| Insertion/deletion-heavy pair | Source has paragraph absent in target | Vecalign handles 1-2 / 2-1 alignments natively |
| OCR errors on one side | Garbled chars in one stream | Pre-clean OCR before alignment |

## See also

- **Thompson, B., & Koehn, P.** (2019). *Vecalign: Improved Sentence Alignment in Linear Time and Space*. EMNLP.
- **Sennrich, R., & Volk, M.** (2010). hunalign successor work.
- **Moore, R. C.** (2002). *Fast and accurate sentence alignment of bilingual corpora*. AMTA.
- Vecalign repo: https://github.com/thompsonb/vecalign
