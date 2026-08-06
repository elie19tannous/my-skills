# Language-Agnostic Readability Assessment Rules for AI Agents

A language-independent readability agent should not rely on one formula. It should assess whether readers can **find, understand, and use** the information.

The core rule:

> A text is easy to read when a target reader can quickly find the relevant part, understand it without re-reading, and know what to do next.

This approach aligns with plain-language principles such as relevance, findability, understandability, and usability.

## Universal readability assessment rules

| # | Assessment rule | What the AI agent should check | Easy-to-read threshold | Hard-to-read warning | Weight |
|---:|---|---|---|---|---:|
| 1 | Purpose is clear immediately | Can the agent summarize the text's purpose in one sentence from the title or intro? | Purpose appears in title, heading, or first paragraph | Reader must infer the purpose after several paragraphs | 8 |
| 2 | Main point comes first | Does the first 10–15% of the text contain the key message or decision? | Main conclusion or action appears early | Long background before the main message | 8 |
| 3 | Audience need is clear | Does the text answer: “Who needs this and why?” | Target reader and their need are explicit or obvious | Text is written from the institution or author perspective only | 7 |
| 4 | Average sentence length is low | Count words per sentence | Average sentence length ≤ `15–20` words | Average sentence length > `25` words | 10 |
| 5 | No very long sentences | Detect sentences above the length threshold | No sentence > `25` words, or only rare exceptions | Multiple sentences > `30` words | 8 |
| 6 | One idea per sentence | Count clauses, commas, semicolons, parentheses, and nested conditions | Most sentences express one main idea | Many sentences contain several conditions, exceptions, or embedded clauses | 8 |
| 7 | Short paragraphs | Count words and sentences per paragraph | Paragraphs usually ≤ `3–4` sentences and cover one topic | Large blocks of text with no clear breaks | 7 |
| 8 | Clear structure and headings | Check headings, bullet points, numbered steps, and whitespace | Sections are clearly labelled; headings explain what follows | No headings, vague headings, or dense continuous prose | 8 |
| 9 | Everyday vocabulary | Estimate common-word ratio using a frequency list for the detected language | Most content words are common for the target audience | High share of rare, formal, bureaucratic, academic, or domain-specific words | 10 |
| 10 | Jargon is controlled | Detect technical terms, acronyms, abbreviations, legal, medical, administrative, or domain-specific terms | Jargon is avoided or explained on first use | Unexplained acronyms and specialist terms | 8 |
| 11 | Concrete wording | Detect abstract nouns, vague references, and generic terms | Text uses concrete nouns, specific actions, and examples | Text relies on abstract concepts without examples | 6 |
| 12 | Active and direct style | Detect passive voice or missing actor where the language supports it | Mostly clear actor + action pattern | Many passive constructions or unclear responsibility | 6 |
| 13 | Verbs instead of nominalisations | Detect noun-heavy phrases such as “implementation of”, “submission of”, or “conducting an assessment” | Actions are expressed as verbs | Bureaucratic noun chains dominate | 5 |
| 14 | Logical flow | Check whether sentences and sections connect with clear transitions | Reader can follow cause, contrast, sequence, and result | Abrupt jumps, unclear references, or missing transitions | 6 |
| 15 | Actionability | Can the agent extract “what to do next”, “when”, “where”, “who”, and “how”? | Required actions are explicit | Reader must infer next steps | 8 |
| 16 | Lists for steps or options | Check whether procedures, requirements, or options are written as lists or tables | Steps, options, and comparisons use lists or tables | Complex procedures hidden in paragraphs | 5 |
| 17 | No avoidable repetition | Detect repeated ideas, duplicated phrases, and circular explanations | Repetition is only used for emphasis or clarity | Same point repeated without adding information | 4 |
| 18 | Low memory load | Count dependencies: references like “this”, “above-mentioned”, “the former/latter”, and long-distance pronouns | References are close and unambiguous | Reader must remember many earlier details | 5 |
| 19 | Terminology is consistent | Check whether the same concept is named the same way | One term per concept | Synonyms used for the same thing without reason | 4 |
| 20 | Reader can verify understanding | Can the agent create 3–5 simple comprehension questions and answer them from the text? | Answers are easy to find | Answers are scattered, implicit, or contradictory | 6 |

## Suggested scoring model

| Final score | Assessment | Meaning |
|---:|---|---|
| `85–100` | Very easy to read | Most readers should understand it quickly |
| `70–84` | Easy / acceptable | Generally clear, minor improvements possible |
| `55–69` | Borderline | Understandable, but likely tiring or unclear for some readers |
| `40–54` | Difficult | Needs rewriting before broad public use |
| `<40` | Very difficult | Too dense, technical, or poorly structured |

## Recommended assessment dimensions

| Dimension | What it measures | Example checks |
|---|---|---|
| Findability | Can the reader quickly locate the relevant part? | Headings, lists, paragraph breaks, topic order |
| Understandability | Can the reader understand the message without re-reading? | Sentence length, vocabulary, jargon, logical flow |
| Cognitive load | How much must the reader remember or infer? | Long references, nested conditions, multiple ideas per sentence |
| Usability | Can the reader act on the text? | Clear next steps, deadlines, responsibilities, examples |

## Implementation guidance for multilingual AI agents

Use **relative checks**, not only fixed thresholds. Word length and sentence structure behave differently across languages. For example, German compounds, Polish inflection, and Romance-language morphology can make words longer without always making the text harder.

A better multilingual readability agent should combine the following signals:

| Signal type | Recommended method |
|---|---|
| Sentence length | Universal word-per-sentence threshold |
| Word difficulty | Language-specific frequency list or language model probability |
| Jargon | Domain glossary and acronym detection |
| Structure | Headings, paragraphs, lists, and tables |
| Cognitive load | Clause count, nested conditions, and unclear references |
| Usability | Extractable actions, deadlines, responsibilities, and examples |

## Practical scoring approach

The AI agent can calculate a final readability score as follows:

1. Evaluate each rule from `0` to `1`:
   - `1` = rule fully satisfied
   - `0.5` = partially satisfied
   - `0` = not satisfied
2. Multiply each rule score by its weight.
3. Sum all weighted scores.
4. Divide by the maximum possible score.
5. Multiply by `100`.

### Formula

```text
Final readability score = (sum(rule_score × rule_weight) / sum(all_rule_weights)) × 100
```

## Example agent output format

```markdown
## Readability assessment

Final score: 74/100
Assessment: Easy / acceptable

### Strengths
- The purpose is clear in the first paragraph.
- Paragraphs are short and well structured.
- The text gives clear next steps.

### Problems
- Several sentences exceed 30 words.
  - Location: Procedure description, step 4.
  - Text: "Full sentence that creates the readability problem."
- Some acronyms are not explained on first use.
  - Location: Scope.
  - Text: "MDS"
- The text contains bureaucratic nominalisations.
  - Location: Roles and responsibilities.
  - Text: "implementation of the handover process"

### Recommended improvements
- Split long sentences.
- Explain acronyms on first use.
- Replace noun-heavy phrases with direct verbs.
```

When reporting problems, explicitly point to the issue whenever possible. Include the section, paragraph, step, table row, appendix, full sentence, full phrase, full word, acronym, or term that caused the finding. If the exact location is not available, state the closest known location and say that the location is approximate.

Do not apply simplification rules to medical terms, defined terms, official role names, legal terms, technical terms, form names, medicine names, diagnosis names, procedure names, authority names, or other terms that cannot be rephrased without losing precision or changing meaning. These terms may still need a definition, expansion on first use, or glossary entry, but they should not be marked as readability problems merely because they are specialized or long.

## References

- International Plain Language Federation — ISO plain language standard: https://www.iplfederation.org/iso-standard/
- European Commission — Clear writing / plain language guidance: https://translation.ec.europa.eu/languages-and-translation-european-commission/plain-language-making-european-commission-texts-clear_en
