---
name: israeli-nda-confidentiality
description: Draft, review, and negotiate Israeli non-disclosure / confidentiality agreements (heskem sodiyut / NDA) between businesses, founders, employees, contractors, and investors. Use when a user needs a one-way (chad-tzedadi) or mutual (hadadi) NDA, wants a confidentiality clause reviewed, asks about trade-secret protection under the Commercial Torts Law, 5759-1999, how confidentiality interacts with the enforceability of employee non-competes in Israel, permitted-use and residual-knowledge clauses, term/survival, governing law and jurisdiction, and remedies. Covers the Israeli-specific angles that generic US templates get wrong (trade-secret standard, over-broad non-compete unenforceability, Privacy Protection Law overlap). Do NOT use for full employment contracts (use israeli-employment-contracts), freelancer service agreements (use israeli-freelancer-service-agreement), or patent/trademark filings.
license: MIT
compatibility: "Knowledge-only skill, no external tools or network required. Produces a Hebrew or English NDA draft; legal review by an Israeli lawyer is recommended before signing. Thresholds and case law evolve — verify load-bearing points against the primary source."
---

# Israeli NDA & Confidentiality Agreements

## Instructions

### Step 1: Legal Framework
An Israeli NDA sits on top of several statutes; a good NDA references and reinforces them rather than reinventing them:

| Law | Hebrew | Year | Relevance |
|-----|--------|------|-----------|
| Commercial Torts Law | חוק עוולות מסחריות | 5759-1999 | Defines and protects "trade secret" (sod mishari); misappropriation is a civil wrong with statutory damages up to 100,000 NIS without proof of damage |
| Contract Law (General Part) | חוק החוזים (חלק כללי) | 1973 | Governs formation, interpretation, and good faith |
| Contracts (Remedies for Breach) Law | חוק החוזים (תרופות בשל הפרת חוזה) | 1970 | Remedies: damages, specific performance, and agreed (liquidated) damages, which a court can reduce if grossly excessive |
| Protection of Privacy Law | חוק הגנת הפרטיות | 1981 | Applies when the confidential information includes personal data (databases, PII) |
| Basic Law: Freedom of Occupation | חוק יסוד: חופש העיסוק | 1994 | The constitutional anchor that makes over-broad post-employment restraints hard to enforce |

**Key Israeli reality:** confidentiality obligations are enforced far more readily than non-competes. Israeli courts (following the Checkpoint / AES line of Supreme Court case law) will generally NOT enforce a bare non-compete that only protects an employer from ordinary competition; they enforce restraints that protect a legitimate interest — most centrally, genuine trade secrets. So a well-drafted confidentiality/trade-secret clause is the strong, enforceable tool; a broad non-compete is the weak one.

### Step 2: One-Way vs. Mutual, and When to Use Each

| Type | Hebrew | Use when |
|------|--------|----------|
| One-way / unilateral | חד-צדדי | Only one side discloses (e.g. a company sharing information with a candidate, contractor, or potential vendor) |
| Mutual / bilateral | הדדי | Both sides will exchange sensitive information (e.g. two companies exploring a partnership, M&A, or integration) |

Default to mutual for genuine two-way business exploration; a one-way NDA offered in a two-way situation is a red flag that the drafter is protecting only themselves.

### Step 3: Core Clauses (the checklist)

| Clause | Hebrew | What to get right |
|--------|--------|-------------------|
| Parties | הצדדים | Full legal names, company numbers (ח.פ.), and whether affiliates/representatives are bound |
| Definition of Confidential Information | הגדרת מידע סודי | Broad but bounded: written, oral, and visual; marked and reasonably-should-be-known-confidential; tie into "trade secret" under the 1999 law |
| Purpose / permitted use | מטרה / שימוש מותר | Information may be used ONLY for the defined purpose (evaluate a deal, perform services) — this limits scope and strengthens enforceability |
| Standard exclusions | חריגים | Already public, already lawfully known, independently developed, lawfully received from a third party, or required to be disclosed by law/court (with notice) |
| Obligations | חובות | Keep secret, limit access to need-to-know, protect with reasonable measures, no copying beyond the purpose |
| Compelled disclosure | גילוי על פי דין | Allow disclosure required by law/regulator/court, with prior notice to the discloser where lawful |
| Return / destruction | השבה / השמדה | On termination or request, return or destroy the information and copies, with written confirmation |
| Term & survival | תקופה והישרדות | Distinguish the disclosure period from the confidentiality survival period; trade secrets can be protected for as long as they remain secret |
| Remedies | סעדים | Injunctive relief (tzav mnia) plus damages; optionally agreed damages, drafted at a genuine pre-estimate, not a penalty |
| No license / no obligation | ללא רישיון / ללא התחייבות | Disclosure grants no IP license and no obligation to proceed with any deal |
| Governing law & jurisdiction | דין וסמכות שיפוט | Israeli law and a specified Israeli court (or arbitration) |

### Step 4: Term and Survival — Get This Right
Two different clocks that drafters conflate:

| Clock | Meaning |
|-------|---------|
| Disclosure period | The window during which information is exchanged (e.g. the duration of the negotiation or engagement) |
| Confidentiality survival | How long the duty to keep it secret lasts after the relationship ends |

For ordinary business information, a fixed survival (e.g. 3-5 years) is common and reasonable. For genuine trade secrets (sod mishari), the obligation can survive for as long as the information remains secret and derives value from secrecy — an indefinite survival tied to the information's secret status is legitimate and often preferable to an arbitrary short cut-off.

### Step 5: The Non-Compete Trap (Israel-specific)
NDAs are frequently bundled with non-compete and non-solicit clauses. In Israel these are treated very differently:

| Restraint | Enforceability posture |
|-----------|------------------------|
| Confidentiality / trade-secret protection | Strong — protects a legitimate interest; readily enforced |
| Non-solicitation of employees/customers | Enforceable if reasonable in scope, time, and geography and protects a legitimate interest |
| Bare non-compete (blocking ordinary competition) | Weak — Israeli courts (Checkpoint/AES line) usually will NOT enforce a restraint whose only purpose is to prevent competition, absent a protected interest such as trade secrets, special training, or consideration paid for the restraint |

**Practical drafting advice:** rely on the confidentiality/trade-secret clause as the load-bearing protection. Keep any non-compete narrow, time-limited, tied to a legitimate interest, and ideally supported by separate consideration; assume a broad one will be read down or struck.

### Step 6: Personal Data Overlap
If the confidential information includes personal data (customer databases, employee records, PII), the Protection of Privacy Law, 1981 and Israel's database-registration and data-security regulations apply on top of the NDA. Add a data-protection clause: process personal data only per the purpose and applicable law, apply the required security measures, and address cross-border transfer if relevant.

## Examples

### Example 1: Mutual NDA for a Partnership Talk
**Input:** "Two Israeli startups want to explore integrating products. Draft an NDA."
**Output:** Produce a mutual (hadadi) NDA: both parties as discloser/recipient; broad-but-bounded definition of Confidential Information covering written, oral, and visual disclosures tied to the trade-secret concept; a narrow purpose ("evaluating a potential product integration"); the standard exclusions; need-to-know access with reasonable safeguards; compelled-disclosure carve-out with notice; return/destruction on request; survival of 3-5 years for ordinary information and indefinite for trade secrets while they remain secret; injunctive relief plus damages; no IP license and no obligation to proceed; Israeli law and a named Israeli court. Recommend an Israeli lawyer review before signing.

### Example 2: Reviewing an NDA Presented to a Contractor
**Input:** "A client sent me a one-way NDA to sign before a consulting gig. What should I watch for?"
**Output:** Flag: (1) Is it appropriately one-way? If you'll also expose your own methods/know-how, push for mutual or a residual-knowledge/skills carve-out so your general expertise isn't captured. (2) Is the definition of Confidential Information unbounded (e.g. everything, forever)? Ask for the standard exclusions and a reasonable survival period. (3) Is there a hidden non-compete? In Israel a broad non-compete is likely unenforceable, but strike or narrow it anyway. (4) Are the agreed damages a genuine estimate or a penalty a court would cut? (5) Governing law and forum — confirm Israeli law and a convenient court. Recommend legal review before signing.

### Example 3: Trade-Secret Survival Term
**Input:** "How long should the confidentiality last — the other side wants 2 years, I have a secret algorithm."
**Output:** Separate the two clocks. For ordinary business information a 2-year survival may be fine. But your secret algorithm is a trade secret (sod mishari) under the Commercial Torts Law, 5759-1999 — its protection should survive for as long as it remains secret and valuable, not an arbitrary 2 years. Draft dual survival: a fixed term (e.g. 3 years) for general Confidential Information, and an indefinite obligation for information that qualifies as a trade secret, lasting while it stays secret. A 2-year cap that releases your algorithm to the world is a bad deal.

### Example 4: NDA Bundled With a Non-Compete
**Input:** "The NDA also says I can't work for any competitor for 2 years anywhere. Enforceable?"
**Output:** In Israel, probably not as written. Following the Checkpoint/AES Supreme Court line, courts do not enforce a bare non-compete whose only purpose is to block ordinary competition; they require a legitimate protected interest (genuine trade secrets, unique training, or consideration paid for the restraint) and reasonable scope in time and geography. A 2-year, unlimited-geography, any-competitor clause is very likely to be struck or read down. The enforceable protection here is the confidentiality/trade-secret obligation. Negotiate the non-compete out or narrow it drastically; don't rely on it either way.

## Bundled Resources

### References
- `references/nda-clause-library.md` -- A clause-by-clause library (definition, purpose, exclusions, obligations, compelled disclosure, return/destruction, term/survival, remedies, non-compete caveat, governing law) with drafting notes and Israeli-specific pitfalls. Consult when drafting or reviewing an NDA.
- `references/review-red-flags.md` -- A red-flag checklist for reviewing an NDA someone else drafted (one-way where mutual is due, unbounded definition, missing exclusions, hidden/over-broad non-compete, penalty-style damages, foreign forum). Consult when a user is asked to sign an NDA.

### Templates
- `templates/mutual-nda-he.md` -- A mutual NDA template in Hebrew (RTL) with placeholders, suitable as a starting draft for two Israeli businesses. Adapt and have a lawyer review.

## Gotchas

- In Israel, a confidentiality/trade-secret clause is strong and readily enforced, but a bare non-compete is weak. Agents applying US instincts (where non-competes vary by state but are often enforceable) overstate the enforceability of Israeli non-competes. The Checkpoint/AES line is the governing reality.
- The Commercial Torts Law, 5759-1999 gives statutory damages up to 100,000 NIS for trade-secret misappropriation without proof of actual damage — a genuinely useful remedy an NDA should preserve and reference. Agents often omit this Israeli-specific lever.
- Term and survival are two different clocks. Conflating "we'll talk for 6 months" with "keep it secret for 6 months" underprotects trade secrets, which should survive as long as they remain secret. Do not cap a trade-secret obligation at an arbitrary short term.
- Agreed (liquidated) damages are enforceable but a court can reduce them under the 1970 Remedies Law if they are grossly disproportionate to the anticipated harm. Draft them as a genuine pre-estimate, not a punitive number.
- If the confidential information includes personal data, the Protection of Privacy Law, 1981 and Israel's data-security regulations apply on top of the NDA. A pure trade-secret NDA that ignores PII can miss real obligations.
- A one-way NDA in a genuinely two-way situation protects only the drafter. Agents should flag the mismatch and propose mutual terms rather than passively producing a one-way draft.
- Missing standard exclusions (public domain, prior knowledge, independent development, compelled disclosure) makes an NDA over-broad and less enforceable, and exposes the recipient to unfair claims. Always include them.
- Governing law/forum matters. An NDA between Israeli parties should specify Israeli law and an Israeli court (or arbitration); a stray foreign-forum clause copied from a template creates needless cost and uncertainty.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| Commercial Torts Law text | https://www.nevo.co.il | Chok Avolot Mishariyot, 5759-1999 — trade-secret definition and statutory damages |
| Protection of Privacy Law | https://www.gov.il/he/departments/the_privacy_protection_authority | When confidential info includes personal data |
| Contracts (Remedies) Law text | https://www.nevo.co.il | Agreed damages and their reduction; injunctions |
| Kol Zchut: Trade secrets / non-compete | https://www.kolzchut.org.il | Plain-language on confidentiality and restraint-of-trade enforceability |

## Recommended MCP Servers

These Model Context Protocol servers, available in the skills-il directory, pair well with this skill:

- **israel-law**: programmatic access to Israeli primary legislation. Use it to pull the current text of the Commercial Torts Law, 5759-1999 (trade-secret definition and the statutory-damages figure), the Contracts (Remedies) Law, 1970, and the Protection of Privacy Law, 1981 when drafting or citing.
- **kolzchut**: access to Kol Zchut's plain-language portal for current guidance on how Israeli courts treat confidentiality obligations versus non-competes.

Always confirm load-bearing points (the statutory-damages figure, the current state of non-compete case law, privacy-law obligations) against the primary source, since figures and doctrine evolve.

## Troubleshooting

### Error: "The other side insists on a 2-year, all-competitor non-compete"
Cause: A drafter treating an Israeli non-compete like an enforceable US one.
Solution: Explain that Israeli courts (Checkpoint/AES line) generally will not enforce a bare non-compete lacking a legitimate protected interest and reasonable scope. Move the protection into a robust confidentiality/trade-secret clause (which IS enforceable), and either strike the non-compete or narrow it to a short term, defined role, and genuine interest, ideally with separate consideration.

### Error: "The NDA has no exclusions — it covers literally everything forever"
Cause: An over-broad, unbalanced first draft.
Solution: Insist on the standard exclusions (public domain, prior lawful knowledge, independent development, third-party receipt, compelled disclosure with notice) and a sensible survival structure (fixed term for general info, indefinite for trade secrets while secret). An unbounded definition is both unfair and harder to enforce.

### Error: "The agreed-damages number is huge — will it hold up?"
Cause: A penalty-style liquidated-damages clause.
Solution: Under the 1970 Remedies Law a court can reduce agreed damages that are grossly disproportionate to the foreseeable harm. Re-draft the figure as a reasonable pre-estimate of likely loss, and keep injunctive relief and actual-damages (including the 1999 law's statutory damages) as the primary remedies.
