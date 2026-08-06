# Agreement Probes — Reference

Loaded by `magic-linguistic-syntax` Step 5.

## Why agreement probes (not parser F1)

For LLM evaluation, you can't use a parser F1 directly:
- LLMs are autoregressive token models; they don't expose dependency parses.
- Parser-on-LLM-output measures the LLM-output's parsability, not the LLM's grammatical knowledge.

Agreement probes evaluate grammatical knowledge directly: present a minimal pair (one grammatical, one ungrammatical), measure which the model assigns higher likelihood. If the model prefers grammatical, it has learned the agreement.

## Probe construction protocol

For each phenomenon:
1. Identify the agreement (e.g., subject-verb number agreement).
2. Construct N minimal pairs (target ≥ 100 per phenomenon).
3. Each pair: (grammatical, ungrammatical) differing in ONE feature (number, gender, etc.).
4. Compute log-prob assigned by model to each.
5. Score: % pairs where model prefers grammatical.

Per BLiMP convention: > 0.85 accuracy = solid grammatical knowledge; 0.5 = chance.

## Phenomena to probe (per language family)

### Universal
- Subject-verb agreement (number).
- Pronoun-antecedent agreement.
- Negative polarity items.

### Romance / Germanic
- Gender agreement (article-noun, adjective-noun).
- Past participle agreement (Romance).
- Verb-final word order (German subordinate clauses).

### Slavic
- Case agreement (genitive of negation, accusative animate vs nominative inanimate).
- Aspect (perfective vs imperfective).

### Bantu (Swahili, Kinyarwanda, Zulu)
- Noun class agreement (15+ classes; verbs, adjectives, demonstratives all agree).

### Tone languages (Yoruba, Vietnamese, Mandarin pinyin)
- Tone-marked agreement; preserve diacritics.

### Templatic Semitic (Arabic, Hebrew)
- Gender + number agreement; broken plurals.
- Construct state.

### Polysynthetic
- Switch reference (subject continuation across clauses).
- Subject/object encoding within verb.

### Ergative-absolutive (Basque, Tibetan)
- Ergative case marking.
- Subject of intransitive vs transitive.

## Example probe (English subject-verb)

```
grammatical:    "The cat that the dogs chase sleeps."
ungrammatical:  "The cat that the dogs chase sleep."
```

Differ in last verb: singular vs plural. Tests whether model tracks the head ("cat", singular) across the relative clause.

## Example probe (Yoruba tone)

```
grammatical:    "Ọkọ̀ mi ti dé."     (My boat has arrived. — tone marks correct)
ungrammatical:  "Ọkọ mi ti dé."      (Stripped tone — different word/meaning)
```

Tests preservation of tone-marked semantics.

## BLiMP-style benchmarks

The Benchmark of Linguistic Minimal Pairs (BLiMP, 2020) defined 67 paradigms × 1000 pairs for English. Replicated for ~10 other languages (CLAMS, SyntaxGym, etc.).

For low-resource languages: build your own. 100-500 pairs per phenomenon is the floor.

## Per-language probe-set status (snapshot 2026-04-23)

| Language | BLiMP-style available | Notes |
|---|---|---|
| English | YES (BLiMP, SyntaxGym) | 67 paradigms |
| French | YES (CLAMS) | smaller |
| German | YES (CLAMS) | smaller |
| Russian | YES (BLiMP-RU) | partial |
| Mandarin | partial | research |
| Hebrew | partial | research |
| Most others | NO | build your own |

## See also

- **Warstadt, A., et al.** (2020). *BLiMP: The Benchmark of Linguistic Minimal Pairs for English*. TACL.
- **Mueller, A., et al.** (2020). *Cross-Linguistic Syntactic Evaluation of Word Prediction Models* (CLAMS). ACL.
- **Marvin, R., & Linzen, T.** (2018). *Targeted Syntactic Evaluation of Language Models*. EMNLP.
- **Hu, J., et al.** (2020). *A Systematic Assessment of Syntactic Generalization in Neural Language Models* (SyntaxGym). ACL.
