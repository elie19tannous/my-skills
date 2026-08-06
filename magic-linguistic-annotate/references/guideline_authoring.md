# Guideline Authoring — Reference

Loaded by `magic-linguistic-annotate` Step 2.

## The four-stage loop

1. **Draft v0** (1-2 days)
   - Based on task definition.
   - 20-30 worked examples spanning easy/hard/edge.
   - Draft ≤ 10 pages.
   - One author; doesn't need to be perfect.

2. **Pilot** (1 week)
   - 50 items.
   - 2-3 annotators independently.
   - Compute IAA (low expected; this is calibrating the *guidelines*, not the annotators).
   - Discussion meeting per disagreement.
   - Revise to v1.

3. **Calibration** (1-2 weeks)
   - 100 items.
   - ALL annotators.
   - Per-decision discussion.
   - Edge-case log started.
   - Iterate guideline → v2.

4. **Bulk + ongoing adjudication**
   - Full corpus.
   - 10% double-annotated for IAA monitoring.
   - Curator resolves disagreements.
   - Edge-case log appended whenever new patterns emerge.

## Anatomy of a good guideline document

- **Task statement**: 1-paragraph what + why.
- **Unit definition**: token / span / sentence / document.
- **Label set**: definitions + examples per label.
- **Decision tree** for ambiguous cases.
- **Edge-case log**: living document of resolved-but-tricky cases.
- **Examples**: ≥ 30 worked examples spanning easy / hard / boundary.
- **Tie-breaker rule**: "when in doubt, do X" — must exist.

## Common authoring mistakes

- **Vague labels** ("positive sentiment" without operationalization).
- **Overlapping labels** (when the same item could be labeled two ways).
- **No edge-case discussion**: every annotator invents their own resolutions; drift starts.
- **Examples that all agree on**: the *hard* examples are what the guideline must address.
- **No worked examples for the rare label**: annotators forget; consistency drops.
- **Guideline too long (> 30 pages)**: annotators skim; effective coverage drops.
- **Guideline missing tie-breaker rule**: annotators report uncertainty; bulk slows.

## Per-task-type quick guides

### NER (Named Entity Recognition)
- Span boundary: include determiners? articles? trailing punctuation?
- Nested entities: flat-only or hierarchical?
- Per-class definitions with edge cases (PER vs ORG for ambiguous "Apple"; LOC vs ORG for "Iran")?
- Out-of-class handling: PER for fictional characters?

### Sentiment
- Per-aspect or whole-document?
- Label set: positive / negative / neutral / mixed? Or 5-point Likert?
- Ironic / sarcastic content: explicit policy?
- Multi-sentence: aggregation rule?

### POS / parsing
- Follow UD guidelines? Different conventions for some POS?
- Multi-word expression handling?
- Tokenization decisions?

### Translation eval (MQM)
- Error category definitions (accuracy, fluency, style, terminology, locale).
- Severity levels.
- Penalty rules.

## Iteration cost asymmetry

| Stage | Cost to fix a guideline issue |
|---|---|
| Draft | 1× (revise wording) |
| Pilot | 5× (re-annotate 50 items) |
| Calibration | 20× (re-annotate 100 items + discussion) |
| Bulk | 100× (re-annotate proportional to bulk size) |

This is why calibration is non-negotiable.

## Annotation tool selection

| Tool | Strengths | Best for |
|---|---|---|
| Label Studio | Most flexible; ML loop; community | New projects |
| Prodigy | Polished UI; ML active loop; commercial | Production teams with budget |
| Doccano | Open-source; simple | Lightweight |
| INCEpTION | Linguistic-aware; complex annotations | Linguistic projects |
| brat | Minimalist; configurable | Span annotation |
| WebAnno | Linguistic; deprecated → INCEpTION | Legacy |

For new low-resource projects: Label Studio or Prodigy. For UD/treebank work: INCEpTION.

## See also

- **Pustejovsky, J., & Stubbs, A.** (2012). *Natural Language Annotation for Machine Learning*. O'Reilly.
- **Hovy, E.** (2010). *Annotation*. Tutorial materials.
- **Ide, N., & Pustejovsky, J.** (eds.) (2017). *Handbook of Linguistic Annotation*. Springer.
