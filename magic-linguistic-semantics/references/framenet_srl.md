# FrameNet & PropBank-style SRL — Reference

Loaded by `magic-linguistic-semantics` Step 2.

## What frame semantics is

A **frame** is a conceptual structure describing a situation, with participants (frame elements) playing semantic roles. Berkeley FrameNet (English) defines ~1,200 frames covering ~13,000 lexical units.

Example: "GIVING" frame — frame elements = Donor, Recipient, Theme. Lexical units: give, donate, hand, etc.

## What SRL is

Semantic Role Labeling: tag predicates + their arguments with semantic roles. Two main schemes:
- **PropBank** (Penn): per-verb argument labels (Arg0=Agent, Arg1=Patient, etc.).
- **FrameNet**: frame-evoking lexical unit + frame-element labels.

For LLM eval / structured extraction: SRL output is a structured representation of "who did what to whom".

## Per-language FrameNet projects

| Language | Project | Status |
|---|---|---|
| English | Berkeley FrameNet | Mature (~1,200 frames) |
| Spanish | Spanish FrameNet | ~150 frames |
| Japanese | Japanese FrameNet | ~700 frames |
| German | SALSA FrameNet | partial |
| Chinese | Chinese FrameNet | ~300 frames |
| Brazilian Portuguese | FrameNet Brasil | ~600 frames |
| Swedish | Swedish FrameNet | partial |
| Most others | Predicate Matrix bridges | indirect |

## Cross-lingual: Predicate Matrix

When per-language FrameNet doesn't exist, **Predicate Matrix** (Lopez de Lacalle et al. 2014) cross-references Princeton WordNet, FrameNet, VerbNet, PropBank. For target language X with WordNet alignment to English, you can lookup approximate frames via the matrix.

Coverage gaps:
- Per-language WordNet thinness propagates to frame coverage gap.
- Frames specific to one language's culture (e.g., honorific frames in Japanese) absent in matrix.

## SRL tooling

| Tool | Coverage | Notes |
|---|---|---|
| **AllenNLP SRL** (BERT-based) | English; ported to others | Mature; English-strong |
| **stanza** | 70+ via UD | POS + parse, not SRL directly |
| **Hugging Face PropBank-trained models** | Per-language | Spotty; per-language fine-tunes available for ~10 languages |
| **Custom fine-tune** | Anywhere with PropBank-aligned data | Effort-heavy |

For low-resource: expect to either (a) use cross-lingual transfer from English SRL with frame alignment via Predicate Matrix, or (b) skip SRL and rely on dependency parsing (`magic-linguistic-syntax`) + sense lookup.

## Frame-level integration with LLM

For LLM grounding:
- Extract frames from generated text → check coverage of expected semantic roles.
- Useful for structured-extraction eval (did the model name the right Donor + Theme + Recipient?).
- Fragile: frame-evoking lexical unit detection in low-resource is itself a challenge.

## Anti-patterns

- **Using English PropBank frames directly on non-English text**: per-language verb frames differ; alignment via Predicate Matrix required.
- **Treating Frame F as universal**: many frames are culture-specific; Japanese honorific frames don't map to English.
- **Reporting "SRL F1" cross-lingually without alignment scheme**: scores aren't comparable.

## See also

- **Fillmore, C. J.** (1982). *Frame Semantics*. Linguistics in the Morning Calm.
- **Baker, C. F., et al.** (1998). *The Berkeley FrameNet Project*. ACL.
- **Palmer, M., Gildea, D., Kingsbury, P.** (2005). *The Proposition Bank*. Computational Linguistics.
- **Lopez de Lacalle, M., et al.** (2014). *Predicate Matrix*. LREC.
- **Lopez de Lacalle, M., Aranzabe, M. J., Aldezabal, I.** (2016). *Predicate Matrix v1.3*. LREC.
- FrameNet: https://framenet.icsi.berkeley.edu/
- Predicate Matrix: http://adimen.si.ehu.eus/web/predicatematrix
