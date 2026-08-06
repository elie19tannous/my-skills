# Source-Language Selection — Reference

Loaded by `magic-linguistic-transfer` Step 5. Wraps `magic-linguistic-scope/scripts/uriel_distance.py` output with adapter-strategy implications.

## Decision flow

```
1. Run magic-linguistic-scope uriel_distance.py with target language.
2. Get top-3 candidate sources.
3. For each candidate: check (a) URIEL distance, (b) data availability per Joshi class, (c) practical match.
4. Pick the source with best (close + well-resourced + tooling-ready) combo.
5. If no candidate has URIEL < 0.6: pick MULTILINGUAL BASE, not single source.
```

## Multilingual bases as fallback

When no single source is typologically close enough (URIEL ≥ 0.6 to all candidates):

| Multilingual base | Languages | Strengths | Best for |
|---|---|---|---|
| **NLLB-200** (Meta, 2022) | 200 | MT-focused; strong on low-resource | MT tasks |
| **mBART-50 / mBART-cc25** (Facebook) | 50 / 25 | Generative; mature | Generation |
| **BLOOM-176B / smaller** (BigScience) | 46 + 13 programming | Open license; broad | Academic / open |
| **Llama-3 multilingual variants** | varies; 8 official | Strong base; needs vocab extension | Modern LLMs |
| **Qwen-2 multilingual** | 29 | Asian-language-strong | CJK + SEA |
| **Aya** (Cohere) | 101 | Instruction-tuned multilingual | Instruction-following |
| **AfroLM / SeamlessM4T** | regional | Region-specialized | Africa / multimodal MT |

For a target with no close URIEL match: **multilingual base + vocab extension + LoRA** is the floor.

## Examples

### Yoruba (URIEL Igbo=0.18, Twi=0.21, Hausa=0.34, English=0.62)

Choice: **NLLB-200 multilingual base + OFA vocab extension + LoRA r=32**.

Rationale: Igbo/Twi closest but Class 1-2 themselves; multilingual base captures their patterns better than single-source CP.

### Inuktitut (URIEL Kalaallisut=0.21, English=0.78)

Choice: **NLLB-200 + HyperOfa + LoRA r=64**.

Rationale: only one close source (Kalaallisut, also Class 1); not enough for CP; multilingual base + HyperOfa + LoRA is the floor.

### Cantonese (URIEL Mandarin=0.20, Vietnamese=0.36, English=0.66)

Choice: **Mandarin LLM (Qwen-2 zh) + vocab extension + LoRA r=16**.

Rationale: very close to Mandarin; transfer from Mandarin LLM is highly efficient.

### Swahili (URIEL Zulu=0.18, Kinyarwanda=0.22, English=0.56)

Choice: **NLLB-200 or AfroLM + LoRA r=16-32**.

Rationale: Class 3 target; Zulu/Kinyarwanda not as well-resourced as multilingual bases; multilingual base is more cost-effective.

## When to override URIEL

URIEL is a heuristic. Override when:

- **You already have an in-domain pretrained model** for the target (use it).
- **The "close" source is community-restricted** (e.g., AILLA-archive Andean Indigenous data) — pick a more available source.
- **The pair has known empirical transfer success** in published work — empirical > theoretical.
- **The "close" source is itself class 0-1** — its model isn't useful as base; multilingual.

Document the override rationale in workspace_state.md.

## See also

- **Lin, Y.-H., et al.** (2019). *Choosing Transfer Languages for Cross-Lingual Learning*. ACL.
- **de Vries, W., et al.** (2022). *Make the Best of Cross-lingual Transfer*. ACL.
- **Pires, T., Schlinger, E., Garrette, D.** (2019). *How Multilingual is Multilingual BERT?*. ACL.
- **Costa-jussà et al.** (2022). NLLB-200 — multilingual base showcase.
