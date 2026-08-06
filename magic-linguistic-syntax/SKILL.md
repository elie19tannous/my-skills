---
name: magic-linguistic-syntax
description: Universal Dependencies (UD) treebank usage, cross-lingual parser transfer (UDify, Trankit, stanza), and agreement-probe construction for grammatical-correctness evaluation. Use whenever the user mentions UD, Universal Dependencies, treebank, dependency parsing, constituency parsing, parser transfer, agreement probe, subject-verb agreement, gender agreement, case marking, syntactic eval, or asks how to evaluate whether a low-resource LLM has actually learned grammar (not just lexical surface). Routed by magic-linguistic-orchestrator in the Analyze phase.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: linguistics
  complexity: medium
  requires_llm: false
  phase: 3
  supports_pipeline: true
  supports_generation: false
  entry_point: false
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - linguistics
  - syntax
  - ud
  - treebank
  - parser
  - agreement-probe
  - low-resource
  dependencies: []
  scripts:
  - scripts/parser_transfer_advisor.py
  - scripts/ud_coverage.py
---

## When to Use

- Selecting a UD treebank for the target language.
- Cross-lingual parser transfer (no labeled treebank for target).
- Building grammatical-knowledge probes (agreement, case, word order).
- Evaluating whether an LLM has learned target-language syntax (vs surface fluency).
- Annotating new UD data (cross-reference magic-linguistic-annotate).

**When NOT to use:** the target has rich UD coverage and standard parser fine-tune works → use the parser, no advisory needed. For pure annotation methodology → `magic-linguistic-annotate`.

## The Knowledge Engineers Routinely Miss

1. **UD treebank coverage is uneven**. 100+ treebanks exist but vary 100× in size. Many class 0-2 languages have only PUD-style 1K-sentence test treebanks — useful for cross-lingual eval, **NOT** for training.

2. **Cross-lingual parser transfer source is picked by URIEL distance, NOT treebank size.** Closest typological neighbor with adequate data > distant neighbor with massive data. Route via `magic-linguistic-scope` URIEL output.

3. **Agreement probes (subject-verb, gender, case) detect grammatical knowledge directly**. Better than parsing F1 for evaluating LLMs (which don't expose parses). For each phenomenon, construct minimal-pair probes ("the cat *sleeps* / *sleep*") and compute model log-likelihood ratio.

4. **Trankit (2021) is generally better than stanza for low-resource UD parsing**. Stanza wins on speed + coverage. UDify (2019) is older but multilingual-shared.

5. **PUD-style 1K test treebanks are TEST sets**, not training. Fine-tuning a parser on them = leaked eval. Common rookie mistake; some published "parser improvements" are this leak.

6. **Switch-reference, ergative-absolutive, polysynthesis** break English-trained parsers in non-obvious ways. UD's annotation guidelines try to be cross-lingual but some phenomena are under-documented for under-resourced languages.

## Workflow

### Step 1 — Identify UD treebank availability

**MANDATORY READ** [`references/ud_treebanks.md`](references/ud_treebanks.md).

Use `scripts/ud_coverage.py`:
- Per-target: list available UD treebanks + size + register + version.
- Distinguish PUD-style 1K test vs training treebanks (10K+).
- Flag PUD-only as eval-only.

### Step 2 — Decide approach

| Target situation | Recommended approach |
|---|---|
| Native UD treebank, training-size (10K+) | Fine-tune a parser; standard pipeline |
| Only PUD test treebank | Cross-lingual transfer; PUD as eval-only |
| No UD treebank at all | Cross-lingual transfer (zero-shot); flag eval limitation |

### Step 3 — Source treebank selection (cross-lingual transfer)

**MANDATORY READ** [`references/parser_transfer.md`](references/parser_transfer.md).

Use `scripts/parser_transfer_advisor.py`:
- Pull URIEL distances from `magic-linguistic-scope`.
- Recommend top-3 source treebanks weighted by (URIEL distance × treebank size × coverage of needed POS).
- Prefer typological proximity > raw size.

### Step 4 — Parser tool

| Tool | Strengths | Weaknesses | Pick when |
|---|---|---|---|
| Trankit (2021) | Best low-resource UD quality; XLM-R based | Slower than stanza | Quality priority + low-resource |
| stanza (Stanford, 2020) | 70+ languages out of box; fast | Slightly weaker on LR | Speed; broad coverage |
| UDify (2019) | Single multilingual model | Older; worse than Trankit | Legacy / quick baseline |
| spaCy | Fast; production-ready | Limited UD coverage | English / major-language production |

### Step 5 — Agreement-probe construction

**MANDATORY READ** [`references/agreement_probes.md`](references/agreement_probes.md).

Build minimal-pair probes for grammatical phenomena:
- **Subject-verb agreement**: ("la luna brilla" / *"la luna brillan").
- **Gender agreement**: ("el libro" / *"la libro").
- **Case marking**: per-language (e.g., Russian instrumental).
- **Tone-marked agreement** (Yoruba, Mandarin): preserve diacritics.

Target probe set: 100-500 minimal pairs per phenomenon. Compute model log-likelihood difference; > 0 = correct preference.

### Step 6 — Output syntax plan + hand off

```markdown
## Syntax Analysis: <Language>

**UD treebank availability:** <N treebanks total / training-size / PUD-only>
**Recommended training treebank:** <name + size + register>
**Cross-lingual transfer source:** <ISO + rationale>
**Parser tool:** Trankit | stanza | UDify | spaCy
**Agreement-probe phenomena:** <subject-verb / gender / case / ...>
**Probe size target:** N pairs per phenomenon
**Hand-off:** magic-linguistic-eval for benchmark integration; magic-linguistic-annotate if creating UD gold
```

## Anti-patterns (NEVER do)

- **NEVER** fine-tune a parser on PUD-style 1K test treebanks. You've leaked your eval.
- **NEVER** pick parser source treebank by size alone. URIEL typological distance dominates transfer success.
- **NEVER** report parser F1 as a proxy for LLM grammatical knowledge. Use agreement probes — LLMs don't expose dependency parses.
- **NEVER** assume English-trained UD parsers handle ergative-absolutive correctly. Subject/object roles are inverted.
- **NEVER** strip diacritics before tone-language agreement probes. The agreement is in the diacritic.
- **NEVER** use UDify for new low-resource projects when Trankit is available. Trankit is meaningfully better.
- **NEVER** treat "no UD treebank" as "no syntactic eval possible" — agreement probes work without parses.

## Edge Cases

- **Multiple UD treebanks for same language** (UD English has 5+ sources): pick by domain match; document choice.
- **Treebank version drift** (UD 2.x → 2.y annotation changes): pin version in workspace_state.md.
- **Ergative-absolutive language** (Basque, many Caucasian, Tibetan): test stanza/Trankit carefully; F1 may be misleading.
- **Polysynthetic with morpheme-level UD** (some Indigenous Americas): word boundaries differ from "real" UD; handle separately.
- **Mixed-script code-switched** (Hinglish): per-paragraph language; per-language parser.
- **UD gold annotation has known errors**: 1-3% rate is typical; don't over-fit.

## Output Format

```markdown
## Syntax Plan: <Language>

**UD treebank coverage:** ... 
**Approach:** native fine-tune | cross-lingual transfer | zero-shot
**Recommended source treebank:** <name> (URIEL distance <X>; size <N>)
**Parser tool:** Trankit (recommended) | stanza | UDify | spaCy — rationale: ...
**Probe phenomena:** ... (per-phenomenon target N pairs)
**Anti-patterns to avoid:** ...
**Hand-off:** magic-linguistic-eval; magic-linguistic-annotate
```
