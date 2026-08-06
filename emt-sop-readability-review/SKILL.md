---
name: emt-sop-readability-review
description: Review Emergency Medical Team SOPs or standard operating procedures for readability, plain language, reading level, simplification, and field usability by tired, multilingual, interrupted, and time-pressured staff. Use when Claude needs supported language-specific readability scores, Flesch or Flesch-Kincaid-style readability checks, hard-to-read section findings, or clearer field-ready wording.
---

# EMT SOP Readability Review

## Core Contract

Review SOP readability for field usability. Focus on whether tired, multilingual, interrupted, time-pressured staff can scan and act on the SOP.

Always read `references/language_agnostic_readability_rules.md` before reviewing an SOP for readability. Apply these generic rules for every SOP, regardless of SOP language and regardless of whether a language-specific scoring script is available. Use quantitative scores as supporting signals, not final judgments.

## Reference Loading

Read `references/language_agnostic_readability_rules.md` before every readability review. Use it to assess whether readers can find, understand, and use the SOP content, including purpose, main point placement, audience need, sentence length, paragraph length, headings, vocabulary, jargon control, actionability, cognitive load, terminology consistency, and comprehension checks.

## Review Workflow

1. Read `references/language_agnostic_readability_rules.md`.
2. Identify the SOP language from the user request or SOP text. If the language is unknown, ask only when a score is required; otherwise continue with the generic review.
3. If a quantitative score is requested, choose the matching script from the table below. If the language is unsupported, unknown, or substantially mixed-language, state that no validated script is available and do not calculate a score.
4. Run the selected script using the file path or `--text` input. Keep the raw metrics available for the review.
5. Validate the score before using it: check that the sentence, word, syllable, and letter counts are plausible for the supplied text. If a score is distorted by acronyms, medicine names, role names, legal terms, local place names, tables, or mixed-language content, report that limitation and rely more heavily on the generic rules.
6. Apply the generic readability rules to identify exact problem locations, including section, step, full sentence, phrase, word, acronym, or term when possible.
7. Produce a concise assessment with score results when valid, field-usability findings, and concrete rewrites that preserve legal, safety, clinical, scope, and evidence requirements.

## Language-Specific Scoring Scripts

| SOP language | Script | Algorithm | Score interpretation |
| --- | --- | --- | --- |
| English | `scripts/flesch_reading_ease.py` | Flesch Reading Ease | `0-100`; higher = easier. |
| German | `scripts/wiener_sachtextformel_1.py` | Wiener Sachtextformel 1 | `4-15`; lower = easier. `4-5` very easy, `6-7` easy, `8-10` average, `11-12` difficult, `13-15` very difficult. |
| Spanish | `scripts/flesch_szigriszt.py` | Flesch-Szigriszt / Indice de Perspicuidad | `0-100`; higher = easier. `<40` very difficult, `40-55` difficult, `55-65` normal, `65-80` easy, `>80` very easy. |
| Italian | `scripts/gulpease_index.py` | Gulpease Index | `0-100`; higher = easier. `<40` difficult for high-school readers, `<60` difficult for lower-secondary readers, `<80` difficult for elementary readers. |
| Polish | `scripts/jasnopis_readability.py` | Jasnopis readability class | `1-7`; lower = easier. `1` primary grades 1-3, `2` primary grades 4-6, `3` lower secondary, `4` high school, `5` undergraduate, `6` graduate, `7` expert. |
| French | `scripts/kandel_moles.py` | Kandel-Moles | `0-100`; higher = easier. `90-100` very easy, `60-70` standard, `30-50` difficult, `<30` very difficult. |

All scripts use only the Python standard library and accept the same interface:

Run:

```bash
python3 scripts/<script_name>.py path/to/sop.md
```

Or:

```bash
python3 scripts/<script_name>.py --text "Plain text to score."
```

Each script reports the algorithm score plus the input metrics needed for that formula, such as:

- sentence count;
- word count;
- syllable count;
- letter count, when required;
- average sentence length;
- average syllables per word;
- algorithm-specific percentages, when required.

## Review Rules

- Flag long sentences, dense paragraphs, vague thresholds, passive voice in critical steps, and undefined acronyms.
- Prefer short action statements with responsible role, trigger, action, evidence, escalation path, and completion criterion.
- Suggest concrete simplifications, but do not remove legal, safety, scope, or evidence requirements.
