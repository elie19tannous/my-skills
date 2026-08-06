# BLiMP-style Probe Construction — Reference

Loaded by `magic-linguistic-eval` Step 5. Cross-reference `magic-linguistic-syntax/references/agreement_probes.md` for syntax-specific phenomena + per-language probe-set status.

## Why probes

LLMs don't expose parse trees. To eval grammatical knowledge:
- Construct minimal pairs: (grammatical, ungrammatical).
- Compute model log-likelihood difference per pair.
- Score: % pairs where model assigns higher likelihood to grammatical.

BLiMP convention: > 0.85 accuracy = solid grammatical knowledge; 0.5 = chance.

## Per-language probe phenomena (planning)

For each target, identify phenomena to probe by typology (cross-reference `magic-linguistic-scope`):

| Typology feature | Phenomenon to probe |
|---|---|
| Subject-verb agreement (most IE) | "The cat is" / "The cat are" |
| Gender agreement (Romance, Slavic, German, Arabic, Bantu) | "El libro" / "La libro" |
| Case marking (Slavic, Uralic, Turkic) | per-case minimal pairs |
| Tone (Yoruba, Vietnamese, Mandarin pinyin) | tone-substitution minimal pairs |
| Word order constraints | reorder probes |
| Honorifics (Japanese, Korean) | level-mismatch probes |
| Long-distance dependencies | center-embedding probes |

## Construction protocol

1. Identify phenomenon (consult `magic-linguistic-scope` typology output).
2. Construct N minimal pairs (target ≥ 100 per phenomenon; 200+ for high-stakes).
3. Validate with native speakers (uncontroversial grammaticality only).
4. Compute model log-likelihoods per pair.
5. Report per-phenomenon accuracy (NOT aggregate).

## What NOT to do

- Lift English BLiMP probes verbatim — phenomena differ.
- Single-pair tests — need ≥ 100.
- "Acceptable but unusual" probes — grammaticality must be uncontroversial.
- Aggregate score across phenomena — hides where model fails.

## Existing per-language sets

| Language | Probe set | Notes |
|---|---|---|
| English | BLiMP, SyntaxGym | Mature |
| French, German | CLAMS | Smaller |
| Russian | RuBLiMP | Partial |
| Mandarin | CLiMP | Partial |
| Most low-resource | None | Build per-language |

## See also

- See `magic-linguistic-syntax/references/agreement_probes.md` for full per-language probe-set status + protocols.
- **Warstadt, A., et al.** (2020). *BLiMP*. TACL.
- **Marvin, R., & Linzen, T.** (2018). *Targeted Syntactic Evaluation*. EMNLP.
