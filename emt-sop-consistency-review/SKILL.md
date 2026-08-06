---
name: emt-sop-consistency-review
description: Review Emergency Medical Team SOP consistency across defined terms, role names, acronyms, glossary usage, translated term mappings, forms, appendices, evidence artifacts, escalation paths, and procedure references. Use when Claude needs to verify that an SOP uses the same language throughout and does not replace defined EMT terms with vague or generic wording.
---

# EMT SOP Consistency Review

## Core Contract

Review the SOP for consistent language. Do not rewrite the whole SOP unless the user asks. Find places where defined terms, roles, acronyms, forms, appendices, evidence artifacts, or escalation paths are omitted, renamed, translated inconsistently, or replaced by generic wording.

Always read `references/emt_glossary.md` before reviewing. Use it as the English source of truth for EMT abbreviations, role-related terms, and preferred official forms.

## Review Workflow

1. Identify the SOP language.
2. Extract all defined terms from the SOP `Terms and definitions` section, role names from `Roles and responsibilities`, and controlled names for forms, logs, appendices, reports, authorities, systems, and escalation recipients.
3. Compare SOP terms against `references/emt_glossary.md`.
4. For non-English SOPs, build a small mapping table from translated SOP terms to the defined English glossary terms where possible.
5. Scan the SOP for inconsistent usage, missing definitions, undefined acronyms, generic substitutes, and conflicting labels.
6. Report findings with exact term, location or section, problem, and recommended correction.

## Checks

- If a term is defined, the SOP must use that term consistently throughout the document.
- Do not let defined role names be replaced by generic words such as `staff`, `team`, `medical personnel`, `coordinator`, or `responsible person` when the defined role should act.
- Do not let defined forms or appendices be renamed casually in procedure steps.
- Acronyms must be expanded or defined before use unless they are already defined in the SOP and used consistently.
- Official EMT terms should follow the glossary where applicable, especially EMT, EMTCC, N-EMT, I-EMT, MDS, SAG, TWG, IPC, PPE, WASH, MoH, and WHO.
- A glossary term must not imply a service capability that is outside the stated EMT type, mandate, or declared scope.
- For translated SOPs, the translated term may differ from English, but it should map back to one stable English source term. Flag cases where one English term has several translations or one translated term maps to multiple English concepts.
- Flag plural/singular, capitalization, hyphenation, abbreviation, and spelling variants when they may cause operational confusion.
- Check that escalation paths, legal authorities, coordination bodies, record names, and evidence artifacts use the same names in all sections.

## Output Format

Return a concise review with these sections:

1. Term mapping: English glossary terms and SOP-language equivalents when the SOP is not in English.
2. Consistency findings: inconsistent or generic term usage.
3. Undefined or under-defined terms: acronyms, roles, forms, authorities, reports, systems, or statuses that need definitions.
4. Cross-reference findings: mismatched appendix, form, log, evidence, escalation, or section references.
5. Recommended corrections: exact preferred term replacements or definition additions.

For each finding include:

- current wording;
- preferred defined term;
- affected section or step if known;
- why it matters operationally;
- correction.

If no issue is found, state that no consistency issues were found and mention any limits caused by missing SOP sections or missing mission terminology.

## Example Output Pattern

For a non-English SOP, start with a compact term mapping table:

| English glossary term | SOP-language term | Notes |
| --- | --- | --- |
| Clinical Lead | Kierownik kliniczny | Use this exact role label in all action steps. |
| Referral Form | Formularz skierowania | Do not shorten to `form` when the specific record is required. |
| EMTCC | EMTCC | Keep the official acronym and define it once. |

Then report findings in the required structure:

- Current wording: `medical personnel complete the referral paper`
- Preferred defined term: `Clinical Lead completes the Referral Form`
- Affected section or step: `Procedure description`, step 6
- Why it matters operationally: the generic wording hides the responsible role and may cause staff to use the wrong record.
- Correction: replace the sentence with `Clinical Lead completes the Referral Form and records the referral number in the Patient Register.`

- Current wording: `Appendix B: Handover checklist` and later `handover form`
- Preferred defined term: `Appendix B: Handover Checklist`
- Affected section or step: `Appendices` and `Procedure description`, step 9
- Why it matters operationally: casual renaming can make staff look for a different document during shift change.
- Correction: use `Appendix B: Handover Checklist` everywhere.
