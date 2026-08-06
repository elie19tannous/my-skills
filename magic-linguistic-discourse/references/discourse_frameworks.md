# Discourse Frameworks — Reference

Loaded by `magic-linguistic-discourse` when picking a framework.

## RST — Rhetorical Structure Theory (Mann & Thompson 1988)

**Models:** discourse as a hierarchical tree where each node is either a nucleus (central) or satellite (supporting). Relations: ELABORATION, BACKGROUND, CONTRAST, CAUSE, EVIDENCE, etc.

**Best for:**
- Summarization eval (which units are nuclei?).
- Discourse-aware compression.
- Long-document structure analysis.

**Per-language coverage:**
- English: RST-DT (Rhetorical Structure Treebank).
- German: PCC.
- Spanish: RST-SCT.
- Brazilian Portuguese, Russian, Chinese, ~10 others (varying coverage via DISRPT).

**Limitations:**
- Tree structure forces single-parent — multi-parent discourse moves are unrepresentable.
- Per-annotator variation in tree shape is high.

## PDTB — Penn Discourse Treebank (Prasad et al. 2008)

**Models:** local relations between adjacent discourse units (sentences or arguments), marked by explicit (e.g., "however") or implicit connectives. Relation hierarchy: TEMPORAL, CONTINGENCY, COMPARISON, EXPANSION.

**Best for:**
- Discourse-marker prediction.
- QA where connectives matter ("Why did X happen?" requires CAUSE relation tracking).
- Local discourse coherence.

**Per-language coverage:**
- English: PDTB 3.0 (large; well-annotated).
- Chinese: CDTB.
- Hindi, German, Arabic, others via DISRPT shared task.

**Limitations:**
- Local; doesn't capture document-level structure.
- Implicit relations are subjective.

## SDRT — Segmented Discourse Representation Theory (Asher & Lascarides 2003)

**Models:** discourse as formal-logic structure where each segment carries discourse relations.

**Best for:**
- Formal semantics research.
- Discourse-relation reasoning under entailment.

**Per-language coverage:** primarily research-grade; smaller corpora.

**Limitations:**
- Rare in practice.
- Less tooling than RST/PDTB.

## GUM — Georgetown University Multilayer (Zeldes 2017+)

**Models:** RST + UD + coref + entities + discourse markers + named entities + speech acts in a single corpus. ~12 genres.

**Best for:**
- Multi-layer cross-evaluation in a single source-of-truth.
- Mixed-genre research (academic, news, fiction, dialogue, web).
- Cross-framework comparison.

**Per-language coverage:**
- Original GUM: English.
- DGUM (German), ZGUM (Czech), PGUM (Portuguese), and ~10 more in development.

**Limitations:**
- English-dominant.
- Genre-balanced but per-genre size limited.

## DISRPT — Discourse Representation, Resources and Tools shared task

Annual shared task across multiple frameworks + languages. Source for cross-language discourse data. https://sites.google.com/view/disrpt2025/

## Framework-selection cheat sheet

| Question | Framework |
|---|---|
| Is this summary preserving the main points? | RST |
| Does the model handle "however"/"because"/"although" correctly? | PDTB |
| Does the cited source actually support the claim (RAG faithfulness)? | RST + coref |
| Is the model resolving "it" / "they" correctly? | coref (any framework) |
| Does the long-form generation stay on topic? | RST + topic segmentation |
| Are dropped pronouns recovered correctly? | coref + zero-anaphora |
| Are formal-logic discourse relations preserved? | SDRT (rare) |
| Cross-framework benchmark with single ground truth? | GUM |

## Tooling

| Tool | Framework | Status |
|---|---|---|
| **DPLP** (RST parser) | RST | Mature; English |
| **TwoStage RST parser** | RST | Newer; English |
| **PDTB connective classifier** | PDTB | English; per-language varies |
| **CRAC shared task tools** | Coref (multi-lingual) | Active |
| **wl-coref** | Coref | Multilingual |
| **TextTiling** | Topic segmentation | Classic |
| **GUM accessors** (Python `udapi`, `gum-api`) | GUM | Native Python |

## See also

- **Stede, M.** (2011). *Discourse Processing*. Morgan & Claypool.
- **Mann, W. C., & Thompson, S. A.** (1988). *Rhetorical Structure Theory*. Text.
- **Prasad, R., et al.** (2008). *The Penn Discourse Treebank 2.0*. LREC.
- **Asher, N., & Lascarides, A.** (2003). *Logics of Conversation*. Cambridge.
- **Zeldes, A.** (2017). *The GUM corpus: creating multilayer resources in the classroom*. LREC.
