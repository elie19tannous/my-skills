---
name: nda-reviewer
description: Review a non-disclosure / confidentiality agreement (general, cross-jurisdiction — NOT Israeli-specific) for one-sided terms, an unreasonable or missing term length, missing standard carve-outs, and IP-assignment traps that quietly convert a confidentiality deal into an assignment of rights. Use when a user asks you to review, redline, or sanity-check an NDA, MNDA, CDA, or confidentiality clause before signing; when they ask "is this NDA fair / mutual / too broad?"; when they want to know what to push back on; or when they suspect the NDA is doing more than protecting secrets. Covers mutuality analysis, definition-of-Confidential-Information scope, term/survival length, the standard five carve-outs, permitted-use and residuals, IP/assignment and feedback traps, remedies, and a prioritized redline list. Do NOT give jurisdiction-specific enforceability opinions or treat this as a substitute for counsel on a high-value deal; flag issues and propose balanced language, but the parties' lawyers own the final call.
license: MIT
compatibility: No network required for the workflow or the offline clause-flagging scanner (Python stdlib only). Jurisdiction-specific enforceability (e.g. non-compete or liquidated-damages validity) is out of scope and must be checked against local law separately.
---

# NDA Reviewer

## Instructions

> **Core rule:** an NDA is a *confidentiality* instrument. The moment a clause assigns ownership of IP, grants a licence beyond the stated purpose, or binds one side to obligations the other escapes, it has stopped being a mutual secrecy deal and become a one-sided transfer. Read every NDA for what it *does*, not what it is called.

### Step 1: Establish the Deal Context
Pin down before redlining — the same clause is fair or abusive depending on these:

| Question | Why it matters |
|----------|----------------|
| Who is your client — discloser, recipient, or both? | A one-way NDA favouring the discloser is fine if your client discloses; dangerous if your client receives |
| Is it mutual (MNDA) or one-way? | One-way obligations on a two-way exchange are the most common unfairness |
| What is the purpose / relationship? | Evaluation, vendor eval, employment, M&A, partnership — the permitted use must match, no broader |
| What is actually being shared? | Trade secrets vs routine business info sets how strong the terms should be |
| Deal value & leverage | High-value or take-it-or-leave-it deals change what is worth fighting for |

### Step 2: Test Mutuality & Balance
Read obligations from *both* sides and flag asymmetry:

- **Obligations**: do confidentiality duties, standard of care, and return/destruction apply equally, or only to one party?
- **Definitions**: is "Confidential Information" defined the same for both, or broad for one and narrow for the other?
- **Remedies**: does only one side get injunctive relief, indemnity, or fee-shifting?
- **Term**: does the confidentiality obligation bind one party longer than the other?
- **Exit**: can only one party terminate, or does return/destruction bind only one side?

A one-way NDA is legitimate when disclosure genuinely flows one way. Flag it as an issue only when the exchange is actually mutual.

### Step 3: Scope the Definition of Confidential Information
This definition is the whole deal — everything else hangs on it.

| Problem | What to look for | Fix |
|---------|------------------|-----|
| Over-broad | "all information disclosed" with no limit, or "whether or not marked" | Require marking/identification, or limit to info a reasonable person would treat as confidential |
| Retroactive / perpetual | Captures info disclosed before the NDA, or with no end | Bound to the engagement window; add a term |
| Swallows public info | No carve-outs (see Step 4) | Add the standard exclusions |
| Vague derivatives | "and all information derived therefrom" unbounded | Tie derivatives to the same purpose and carve-outs |

### Step 4: Confirm the Standard Carve-Outs
A fair NDA excludes information that is:

1. **Already public** (or becomes public through no fault of the recipient);
2. **Already known** to the recipient before disclosure (with evidence);
3. **Independently developed** without use of the confidential information;
4. **Rightfully received** from a third party without a duty of confidence;
5. **Required to be disclosed by law / court order** (with notice + cooperation to seek protection).

Missing carve-outs are a red flag — without them the recipient can be liable for "disclosing" something already in the newspaper. The legal-compulsion carve-out should preserve the info's confidential status and give the disclosing party a chance to seek a protective order.

### Step 5: Check Term, Survival & Return
- **Term of the agreement** vs **survival of the confidentiality obligation** are different clocks — a 1-year NDA can carry a 5-year confidentiality survival.
- Typical survival: **2–5 years** for ordinary business info; **indefinite** only for genuine trade secrets (and even then, scope it to trade secrets, not "all Confidential Information forever").
- Flag **perpetual** obligations over ordinary (non-trade-secret) information as unreasonable.
- Confirm a **return-or-destroy** obligation on termination, and whether the recipient may keep one archival copy / backups (common and reasonable if still bound by confidentiality).

### Step 6: Hunt the IP-Assignment & Licence Traps
The highest-severity failure. An NDA should grant **no ownership and no licence** beyond the narrow purpose. Flag any of:

| Trap | Language pattern | Why it's dangerous |
|------|------------------|--------------------|
| IP assignment | "recipient hereby assigns / all IP created shall be owned by discloser" | Turns a secrecy deal into an assignment of your work product |
| Feedback clause | "all feedback/suggestions become discloser's property, royalty-free, perpetual" | You lose rights to your own ideas about their product |
| Broad licence | "grants a licence to use Confidential Information for any purpose" | Use should be limited to the stated purpose only |
| Residuals abuse | one-sided "residuals" clause letting only one party use unaided-memory ideas | Can gut the protection for the other side |
| Non-compete / non-solicit smuggled in | restraint clauses buried in an NDA | Often unrelated to confidentiality; may be unenforceable and should be negotiated separately |
| No-improvements grab | "any improvement to discloser's IP belongs to discloser" | Sweeps in your independent innovation |

The correct default: the NDA states expressly that **no licence or ownership of IP is granted** except the limited right to use the information for the defined purpose.

### Step 7: Produce the Prioritized Redline
Deliver a table sorted by severity (IP/assignment traps and one-sided remedies first, then scope/term, then cleanup), each row:

| Field | Content |
|-------|---------|
| Clause | Section/heading reference |
| Issue | The problem, in one line |
| Severity | High (walk-away / must-fix) / Medium (negotiate) / Low (nice-to-have) |
| Whose favour | Which party the current language favours |
| Suggested edit | Concrete balanced language or a redline direction |

End with a headline: "X high-severity issues; recommend [sign / sign-with-edits / do-not-sign]." Never bless an NDA as "fine to sign" if an IP-assignment or licence trap survives.

### Step 8: Anti-Overreach Discipline
- Do **not** invent problems to look thorough — a clean, mutual NDA with standard carve-outs is common; say so.
- Do **not** give a jurisdiction-specific enforceability opinion (e.g. whether a liquidated-damages or non-compete clause is valid in a given country) — flag it and route to local counsel.
- Distinguish **unfair** (negotiate) from **unenforceable** (legal question) from **unusual-but-acceptable**.
- Propose balanced language, not language that flips the imbalance to the other side.

## Examples

### Example 1: The "NDA" That Assigns IP
**Input:** "Vendor sent this MNDA before a product demo — anything I should worry about?"
**Output:** The mutuality and carve-outs are standard, but Section 6 is not a confidentiality clause — it says "all feedback, suggestions, and improvements provided by Recipient become the sole property of Discloser, royalty-free and perpetual." That is an IP-assignment trap: during a demo you'd give feedback and silently hand them ownership of your ideas. HIGH severity. Also Section 8 grants a licence to use Confidential Information "for any business purpose," broader than the demo. Recommend: strike the feedback-assignment (replace with "no rights in feedback are transferred"), narrow the licence to "solely to evaluate the potential relationship," and add an express "no IP or licence is granted except as stated." Headline: 2 high-severity IP traps; sign-with-edits only.

### Example 2: One-Way Terms on a Two-Way Deal
**Input:** "We're exploring a partnership and both sides will share roadmaps. Is this NDA balanced?"
**Output:** It is styled as mutual but the obligations are one-way: "Confidential Information" is defined only as information disclosed *by Company*, the return/destroy and injunctive-relief clauses bind only *Recipient*, and only Company can terminate. Since both sides are sharing roadmaps, this leaves your disclosures unprotected. Medium-High. Fix: make the definition and every obligation reciprocal ("each party, as Discloser/Recipient…"), mutual injunctive relief, mutual return/destroy. Term is fine (3-year survival, ordinary business info). Headline: mutuality defect across 4 clauses; negotiate to mutual before signing.

### Example 3: Perpetual & Over-Broad Definition
**Input:** "This NDA has a 'perpetual' confidentiality term — normal?"
**Output:** Perpetual is only reasonable for genuine trade secrets. Here the definition is "any and all information disclosed, whether or not marked, and all information derived therefrom," with a perpetual survival — so it locks up ordinary business information forever, which is unreasonable and hard to comply with. Medium. Fix: (a) narrow the definition to information marked confidential or that a reasonable person would treat as confidential; (b) split the term — a fixed survival (e.g. 3–5 years) for Confidential Information generally, and indefinite protection limited to information that qualifies as a trade secret; (c) confirm the five standard carve-outs are present (here #2 "already known" and #3 "independently developed" are missing — add them). Headline: over-broad + perpetual scope; sign-with-edits.

## Bundled Resources

### References
- `references/nda-review-checklist.md` -- The full field checklist: mutuality tests, definition-scope tests, the five standard carve-outs, term/survival guidance, the IP/licence/feedback trap catalogue, remedies, and the severity-ranked redline format. Consult when running a review end to end.
- `references/standard-clauses.md` -- Model balanced language for the common clauses (mutual definition, carve-outs, permitted use, no-IP-granted, term & survival, return/destroy, remedies) plus the red-flag patterns each one neutralizes. Consult when writing the suggested-edit column.

### Scripts
- `scripts/nda_scanner.py` -- Offline first-pass NDA clause flagger (Python stdlib only, no network). Scans NDA plaintext and flags: one-way vs mutual signals, missing standard carve-outs, perpetual/over-long term language, and IP-assignment / feedback / broad-licence / non-compete trap patterns. Outputs a worklist of candidate issues by category. It flags for human review; it does NOT decide fairness or enforceability. Run: `python scripts/nda_scanner.py --help`

## Gotchas

- The name "NDA" is not a promise of narrow scope. The dangerous clauses (IP assignment, feedback grabs, broad licences, smuggled non-competes) hide inside documents titled "Mutual Non-Disclosure Agreement." Read the operative words, not the title.
- Term of the agreement ≠ survival of the confidentiality obligation. Confirm both; a short agreement term with a long survival is normal and fine.
- Missing carve-outs are as dangerous as bad clauses. An NDA with no "already public / independently developed" exclusions can make the recipient liable for public information.
- "Feedback becomes our property" is an IP assignment wearing a friendly label. It is a HIGH-severity trap in evaluation/demo NDAs specifically.
- A one-way NDA is not automatically unfair — it is unfair only when the actual exchange is mutual. Check who really discloses before flagging.
- Residuals clauses cut both ways. A one-sided residuals clause can quietly gut the other party's protection; a mutual, narrow one can be acceptable.
- Enforceability is a separate question from fairness. Do not tell a user a non-compete or liquidated-damages clause is "void" — that is jurisdiction-specific; flag it and route to counsel.
- The scanner is pattern-based: it will miss creatively worded traps and over-flag benign clauses. Use it as a worklist, then read the clauses yourself.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| WIPO — trade secrets & NDAs | https://www.wipo.int/tradesecrets/en/ | What qualifies as a trade secret and why NDAs are the primary protection mechanism |
| Uniform Trade Secrets Act (US model) | https://www.uniformlaws.org/committees/community-home?CommunityKey=3a2538fb-e030-4e2d-a9e2-90373dc05792 | The definition of "trade secret" and misappropriation the NDA's survival term should track |
| DisputesRegister / general NDA drafting guidance (IACCM/World Commerce & Contracting) | https://www.worldcc.com/ | Market-standard NDA terms, mutuality norms, and typical survival periods |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **filesystem**: open the NDA and any referenced schedules/exhibits so every clause is read against the actual text, not a summary.
- **fetch / web-fetch**: pull a counterparty's standard-form NDA or a cited statute to compare the presented draft against a known baseline.

Confidentiality and IP terms turn on exact wording. Where a clause or schedule cannot be read, flag it as unreviewed rather than assuming it is standard.

## Troubleshooting

### Error: "The review says the NDA is fine but the client still got burned"
Cause: A trap was worded unusually and slipped past a title-based read, or a schedule/exhibit was not reviewed.
Solution: Re-read the operative verbs of every clause (assigns / grants / licenses / owns), not the headings. Confirm every referenced schedule and exhibit was actually read. Run the scanner to surface trap patterns, then grade each by hand.

### Error: "Reviewer flagged a one-way NDA as unfair but the deal is genuinely one-directional"
Cause: Mutuality was judged from the document style rather than the actual disclosure direction.
Solution: Confirm who really discloses. If disclosure flows one way, one-way obligations are appropriate — remove the mutuality flag and focus on scope, term, and carve-outs instead.

### Error: "Client asks whether a non-compete inside the NDA is enforceable"
Cause: Enforceability is jurisdiction-specific and outside this skill's scope.
Solution: Flag that the restraint is unusual inside an NDA and should be negotiated as a separate, clearly scoped clause, and route the enforceability question to local counsel. Do not give a validity opinion.
