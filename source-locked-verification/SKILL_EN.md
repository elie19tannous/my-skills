---
name: source-locked-verification
description: Verify that every factual, legal, or quantitative assertion in a document is traceable to a cited, checkable source, and flag any assertion that is unsourced, mis-cited, or unsupported by the source it points to. Use when a user asks you to fact-check a brief, memo, contract recital, due-diligence report, expert report, marketing/regulatory claim, or any document where unsourced statements are a risk; when they want a "source-locked" or "citation-audit" pass; or when they ask which claims lack backing before filing/publishing. Covers claim extraction, citation matching, source-support grading, and an unsourced-assertion report. Do NOT use as a substitute for reading the underlying sources yourself on a high-stakes filing, and do NOT treat a matching citation as proof the source actually supports the claim — always confirm the cited source says what the claim says.
license: MIT
compatibility: No network required for the workflow and the offline claim/citation scanner (Python stdlib only). Fetching live sources to confirm support is optional and separate.
---

# Source-Locked Verification

## Instructions

> **Core rule:** a claim is "source-locked" only when it (1) has a citation AND (2) the cited source actually supports it. A citation alone is NOT verification — many wrong claims carry a real-looking cite to a source that says something different. Never mark a claim verified without confirming support.

### Step 1: Define the Verification Scope
Pin down before scanning:

| Question | Why it matters |
|----------|----------------|
| Which assertion types are in scope? | Factual, legal (statute/case), quantitative (numbers/dates/amounts), quotations — you may audit all or a subset |
| What counts as an acceptable source? | Primary law, record evidence, a Bates-numbered exhibit, a named report, a URL — decide the bar |
| Is "self-evident / argument / opinion" exempt? | Pure argument and legal characterization are not facts; do not flag them as unsourced, but DO flag disguised facts |
| What is the consequence of a miss? | A court filing, an SEC/regulatory claim, and a marketing page have different tolerances |

### Step 2: Extract the Claims
Break the document into atomic assertions. One sentence often contains several claims; split them.

- Prefer **atomic** claims: "The contract was signed on 3 March 2024" and "for $2.4M" are two claims, not one.
- Capture each claim's **type** (fact / law / quantity / quotation) and its **location** (page/paragraph/line).
- Ignore pure argument, rhetorical framing, and legal conclusions — but flag **embedded factual premises** inside them (e.g. "because the defendant never paid" is a factual premise needing support).

The bundled `scripts/claim_scanner.py` gives a first-pass split and flags citation-bearing vs citation-free sentences; treat its output as a worklist, not a verdict.

### Step 3: Match Each Claim to Its Citation
For every extracted claim, find the citation that is supposed to back it.

| Outcome | Meaning |
|---------|---------|
| Cited + adjacent | The claim carries a nearby citation (footnote, parenthetical, exhibit/Bates ref, URL) |
| Cited elsewhere | Support exists but is stated earlier/later, not next to the claim — note the distance |
| Uncited | No citation anywhere for this claim → candidate unsourced assertion |
| Cite mismatch | A citation is present but points to the wrong source or a source that cannot support this claim type |

### Step 4: Grade Source Support
The critical step. For each cited claim, judge whether the source actually supports it:

| Grade | Definition | Action |
|-------|------------|--------|
| Supported | The source directly states the claim | Lock it |
| Partial | The source supports part (e.g. the fact but not the amount, or a weaker version) | Flag; narrow the claim to what the source supports |
| Unsupported | The source does not say this / says something else | Flag as HIGH severity; the cite is misleading |
| Unverifiable | The source can't be checked (dead link, missing exhibit, "on file") | Flag; request the source |
| Misquoted | A direct quotation differs from the source text | Flag as HIGH; quotations must match verbatim |

Confirming support requires reading the source. If you cannot access it, mark **Unverifiable** — never assume support from a plausible-looking cite.

### Step 5: Produce the Unsourced-Assertion Report
Deliver a table sorted by severity (unsupported/misquoted first, then uncited, then partial), each row:

| Field | Content |
|-------|---------|
| Location | Page/paragraph/line of the claim |
| Claim | The atomic assertion, quoted |
| Type | Fact / law / quantity / quotation |
| Status | Uncited / cite-mismatch / unsupported / partial / unverifiable / supported |
| Severity | High (filing-risking) / Medium / Low |
| Fix | Add cite / correct cite / narrow claim / soften to argument / obtain source |

End with a headline count: "X of Y claims are source-locked; Z high-severity gaps." Do not declare a document "clean" unless every in-scope claim is Supported or explicitly exempt.

### Step 6: Anti-Fabrication Discipline
This skill exists to CATCH unsupported claims — so it must never manufacture one.

- If you cannot access a cited source, say "unverifiable — source not checked," never "supported."
- Do not invent a citation to fill an uncited claim; report the gap and let the author supply it.
- Do not soften a genuine "unsupported" to "partial" to be polite — a wrong cite in a filing is a serious problem.

## Examples

### Example 1: Auditing a Legal Brief
**Input:** "Fact-check this motion's statement of facts before we file."
**Output:** Extracted 34 atomic factual claims across the statement of facts. 28 carry a record citation (Ex./Bates or deposition line). Of those, 25 are Supported, 2 are Partial (the cite supports the event but not the date asserted — narrow or add a date source), 1 is Misquoted (the brief's quotation of the email drops a "not" that reverses meaning — HIGH severity, fix before filing). 6 claims are Uncited, of which 4 are true factual premises needing a record cite and 2 are argument that should be reworded so they don't read as facts. Headline: 25/34 source-locked; 1 high-severity misquote, 4 uncited facts. I could not open Exhibit 12 (referenced "on file"), so claim #19 is Unverifiable — obtain the exhibit.

### Example 2: Regulatory / Marketing Claims
**Input:** "Which claims on this product page need a substantiation source before legal sign-off?"
**Output:** 11 performance/comparative claims flagged. 3 are Supported by the cited study. 2 are Partial — the study shows the effect in a subgroup, so the claim must be narrowed to that population or dropped. 4 are Uncited superlatives ("the safest," "clinically proven") that require a named, on-file substantiation source before they can run. 2 are puffery ("loved by customers") and are exempt as non-factual. Recommend obtaining substantiation for the 4 uncited claims and narrowing the 2 partials before sign-off.

### Example 3: Due-Diligence Memo
**Input:** "Make sure every figure in this DD memo traces to a data-room document."
**Output:** Ran the claim scanner over the memo; isolated 47 quantitative assertions (amounts, dates, percentages, counts). 41 carry a data-room reference. 39 are Supported, 2 are Cite-mismatch (the referenced document is a different version — reconcile). 6 figures are Uncited and must be tied to a source file. Delivered the report sorted with the 2 mismatches and 6 uncited figures at the top, each with the exact location and the fix (attach the correct data-room reference).

## Bundled Resources

### References
- `references/verification-workflow.md` -- Step-by-step field workflow: scoping, atomic-claim extraction, citation matching, the support-grading rubric (Supported / Partial / Unsupported / Unverifiable / Misquoted), and the report format. Consult when running a source-lock pass end to end.
- `references/claim-types.md` -- Taxonomy of assertion types (factual, legal, quantitative, quotation, embedded premise vs pure argument/opinion) with rules for what needs a source and what is exempt. Consult when deciding whether a sentence must be sourced.

### Scripts
- `scripts/claim_scanner.py` -- Offline first-pass scanner (Python stdlib only, no network). Splits a plaintext document into candidate sentences/claims, detects citation markers (footnote refs, parentheticals, Bates/exhibit patterns, URLs, statute/section patterns), and outputs a worklist separating citation-bearing from citation-free sentences plus a rough type guess. It flags candidates for human grading; it does NOT judge whether a source supports a claim. Run: `python scripts/claim_scanner.py --help`

## Gotchas

- A citation is NOT verification. The single biggest failure is marking a claim "sourced" because a cite exists, without checking that the cited source actually says it. Always grade support (Step 4).
- Uncited does not always mean wrong, and cited does not always mean right. Treat both as candidates that still need judgment.
- One sentence often hides several claims. If you verify a sentence as a whole you can pass a false sub-claim (e.g. the event is real but the date or amount is wrong). Split into atomic claims.
- Argument and legal conclusions are not facts and should not be flagged as unsourced — but factual premises embedded inside argument ("because they never delivered") DO need support. Don't let a factual claim hide inside a rhetorical clause.
- Direct quotations must match the source verbatim. A dropped "not," an added qualifier, or an ellipsis that changes meaning is a HIGH-severity defect even if the cite is correct.
- "On file," "data on record," or a dead URL means Unverifiable, not Supported. Do not upgrade it because the claim seems plausible.
- Do not fabricate a citation to close a gap. Report the uncited claim and let the author supply the source; inventing a cite is worse than the gap.
- The scanner's citation detection is pattern-based and will miss unusual citation styles and over-flag numbers that aren't claims. Use it as a worklist, then apply human judgment.

## Reference Links

| Source | URL | What to Check |
|--------|-----|---------------|
| The Bluebook (legal citation) | https://www.legalbluebook.com/ | Whether a legal citation is well-formed and points to a checkable source |
| ABA Model Rule 3.3 (candor toward the tribunal) | https://www.americanbar.org/groups/professional_responsibility/publications/model_rules_of_professional_conduct/rule_3_3_candor_toward_the_tribunal/ | The duty not to make false statements of fact/law to a court — the ethical backdrop for source-locking |
| FTC guidance on substantiation of advertising claims | https://www.ftc.gov/business-guidance/advertising-marketing | The requirement that objective product claims have prior substantiation |

## Recommended MCP Servers

These Model Context Protocol servers pair well with this skill:

- **fetch / web-fetch**: retrieve a cited URL so you can confirm the source actually supports the claim rather than assuming from the cite.
- **filesystem**: open exhibits, data-room files, and record documents referenced by a claim so support can be graded against the actual text.

Confirming support requires the source itself. Where a source cannot be retrieved, grade the claim Unverifiable rather than Supported.

## Troubleshooting

### Error: "The report marks everything 'unverifiable'"
Cause: No sources were accessible, so support could not be graded — the scanner only detects citation markers, it does not open sources.
Solution: Provide the cited sources (attach exhibits, supply data-room files, allow URL fetching). Then grade support against the actual text. Unverifiable is the correct status when a source is genuinely unavailable; it should shrink once sources are provided.

### Error: "A true statement got flagged as unsourced"
Cause: The claim is true but carries no citation, or the scanner missed a nonstandard citation format.
Solution: Uncited is a status, not an accusation of falsity — it means "needs a source to be locked." Either add the citation, or if the statement is argument/opinion rather than fact, reword it so it does not read as a factual assertion. Re-run against the claim-types taxonomy to confirm it truly needs a source.

### Error: "Two reviewers disagree on whether a source supports a claim"
Cause: The claim is broader than the source, or the source supports a weaker version (a Partial, not a Supported).
Solution: Narrow the claim to exactly what the source states, or add a second source for the remainder. When in doubt grade DOWN (Partial/Unsupported), never up — over-claiming support is the failure mode this skill exists to prevent.
