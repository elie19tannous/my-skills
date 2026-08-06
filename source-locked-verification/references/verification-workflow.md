# Source-Lock Verification Workflow

A repeatable pass for confirming every in-scope assertion traces to a real,
supporting source. The failure mode this guards against is a confident wrong
claim carrying a legitimate-looking citation.

## 0. Scope

Decide before you start:
- Assertion types in scope (fact / law / quantity / quotation / all).
- Acceptable source bar (primary law, record evidence, named report, live URL).
- Whether argument/opinion is exempt (usually yes; embedded facts are not).
- Consequence of a miss (court filing > regulatory claim > internal memo).

## 1. Extract atomic claims

- Split compound sentences into one-fact-each claims.
- Record type + location (page/para/line) for each.
- Keep quotations exact and mark them as quotation-type (verbatim match required).
- Do NOT flag pure argument, but DO pull out factual premises hiding inside it.

## 2. Match citations

For each claim classify the citation state:
- Cited + adjacent
- Cited elsewhere (note distance)
- Uncited (candidate unsourced assertion)
- Cite-mismatch (points to wrong / incapable source)

## 3. Grade support (the load-bearing step)

Read the cited source and grade:

| Grade | Rule |
|-------|------|
| Supported | Source directly states the claim |
| Partial | Source supports a weaker/narrower version |
| Unsupported | Source doesn't say it / says otherwise (HIGH) |
| Unverifiable | Source not accessible (dead link, missing exhibit) |
| Misquoted | Quotation differs from source text (HIGH) |

Rules:
- No source access → Unverifiable, never Supported.
- When unsure between two grades, grade DOWN.
- Quotations must match verbatim; a changed negation is HIGH severity.

## 4. Report

Table sorted by severity: unsupported/misquoted → uncited → partial → verified.
Columns: Location | Claim | Type | Status | Severity | Fix.
Headline count: "X/Y source-locked; Z high-severity gaps."

Fix column vocabulary: add cite / correct cite / narrow claim / soften to
argument / obtain source.

## 5. Anti-fabrication

- Never invent a citation to close a gap.
- Never upgrade Unverifiable/Unsupported to Supported for tidiness.
- Report gaps plainly; the author supplies the missing source.
