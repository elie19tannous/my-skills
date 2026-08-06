# Coreference Patterns — Reference

Loaded by `magic-linguistic-discourse` for any coreference task.

## What coref is

Identifying which mentions in text refer to the same entity. "The president addressed the nation. He said... Her speech...".

## Genre matters more than people think

| Genre | Coref challenges |
|---|---|
| News / Wikipedia | Cleaner; OntoNotes-trained models work well |
| Dialogue / chat | Speaker tracking (overlapping conversations); colloquial pronouns |
| Literary | Long-range dependencies; first-person narrators |
| Scientific | Citation chains; "the authors", "this work" |
| Legal | Strict referential precision |
| Conversational chat / customer support | First-person + frequent topic shifts |

OntoNotes-trained models trained on news/Wikipedia. They underperform substantially on dialogue. Switch to ConvCoref (CRAC dialogue extension) or fine-tune on genre-matched data.

## Zero anaphora in pro-drop languages

Languages where the subject (or other arguments) can be dropped from the surface form:

| Language | Drop-rate (~) | Notes |
|---|---|---|
| Mandarin | 30-40% | Subject + object commonly dropped |
| Japanese | 30-50% | Topic-prominent; subject often dropped |
| Korean | similar | |
| Spanish | 20-30% | Subject pronoun morphologically marked on verb |
| Italian | 20-30% | Same |
| Portuguese (BR/PT) | 20-30% | Same |
| Slavic (Polish, Russian) | varies | |
| Arabic | 30-40% | Subject often dropped; reflected in verb morphology |

**English-trained coref models miss these silently.** The chain extends across the dropped pronoun, but the coref output doesn't capture it.

### Mitigation

1. Use a pro-drop-aware coref model (e.g., wl-coref with zero-anaphora extension).
2. Pre-process to insert placeholder tokens for dropped subjects (rule-based + morphological tagger).
3. Train your own coref on a pro-drop corpus.

For RAG / extraction: don't trust coref-extracted entity chains in pro-drop language without explicit zero-anaphora handling.

## Cross-document coref

Beyond single-document: identifying same entity across documents (e.g., person mentioned in two news articles). Different problem; uses entity linking + cross-doc resolution. CRAC has cross-doc tracks.

## Bridging anaphora

"The president took the podium. The microphone screeched." — "The microphone" is bridging-anaphoric to the podium scene; not coreferential but contextually linked. Most coref models don't handle bridging. Targeted eval needed.

## Anaphora resolution tools (snapshot 2026-04-23)

| Tool | Languages | Genre coverage |
|---|---|---|
| AllenNLP coref (BERT-based) | English | News/Wikipedia |
| **wl-coref** | Multilingual | Better LR coverage |
| **fast-coref** | English | Production-grade speed |
| HuggingFace `coreference` models | per-language | Variable |
| **stanza coref** (recent additions) | ~10 languages | Genre-mixed |
| **CRAC participants** (e.g., Corefud) | 12+ languages | Shared-task pipeline |

For low-resource: wl-coref + zero-anaphora extension is the typical floor.

## Common coref failures

- **Same gendered pronoun, multiple antecedents**: "Alice told Mary that she had won" — ambiguous; even humans disagree.
- **Long-range over plot/topic shifts**: BERT-context-window cutoff loses references.
- **Bridging vs coref confusion**: model labels bridging as coref.
- **Plural reference**: "the team" vs "they" — singular/plural mismatch.
- **Generic vs specific**: "doctors recommend" vs "the doctor said" — generic shouldn't enter chain.
- **Reported speech**: "She said 'I will'" — embedded "I" must be handled per genre conventions.

## See also

- **Pradhan, S., et al.** (2012). *CoNLL-2012 Shared Task: Modeling Multilingual Unrestricted Coreference in OntoNotes*. CoNLL.
- **Pradhan, S., et al.** (2022). *CRAC 2022 Shared Task on Multilingual Coreference Resolution*. CRAC.
- **Dobrovoljc, K., et al.** (2017). *The Universal Anaphora Annotation Scheme*. Workshop on UA.
- **Liu, J., Wang, Y., Niu, J.** (2023). *Survey of Coreference Resolution*. Computational Linguistics.
