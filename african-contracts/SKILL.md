---
name: african-contracts
description: Draft and review commercial contracts governed by African law — OHADA (17 states), UEMOA/BCEAO and CEMAC payments regulation, African data protection regimes. Use when drafting or reviewing a services agreement, NDA, partnership, freelance/consultant contract, distribution or mobile-money agent contract for a company in Africa; when a contract names Burkina Faso, Senegal, Côte d'Ivoire, Cameroon, Nigeria, Kenya, Ghana or another African jurisdiction; when asked about OHADA Actes uniformes, RCCM, CCJA arbitration, electronic money agents, XOF/XAF currency clauses, or African startup legal structuring. Answers only from a verified fact corpus and cites its sources.
---

# African commercial contracts

Support for drafting and reviewing commercial contracts under African law.

**This is not legal advice.** It helps produce a first draft and flags points
requiring attention. Every contract must be reviewed by a lawyer qualified in the
relevant jurisdiction before signature — especially for electronic money,
employment and data protection, which are regulated fields.

## The one rule that matters

**Never state an African legal fact that is not in `data/*.yaml`.**

No "generally under OHADA…", no article numbers from memory, no amounts,
ceilings, notice periods or tax rates that are not in the corpus. Model recall on
African law is unreliable and confidently wrong — that is precisely why this
corpus exists.

When the corpus does not cover something, say so explicitly:

> Not covered by the verified corpus. This needs confirmation from a lawyer
> qualified in <jurisdiction>.

An honest gap is useful. An invented article number in a signed contract is not.

## Citing

Every legal statement carries its provenance, always — not on request:

> Electronic-money holdings are capped at **2 000 000 FCFA** per identified
> customer per issuer.
> — BCEAO Instruction 008-05-2015, art. 31 · verified 2026-08-01 · https://www.bceao.int/
> > « Les avoirs en monnaie électronique détenus par un même client identifié
> > auprès d'un établissement émetteur ne peuvent excéder deux millions FCFA,
> > sauf autorisation expresse de la Banque Centrale. »

Quotes are reproduced in their original language and never translated. A
translation may accompany them, clearly marked as such.

Confidence levels must be surfaced, not smoothed over:

- `verified` — cite plainly.
- `unverified` — cite **with its `note`**, and say it is unconfirmed.
- `disputed` — present the disagreement; never arbitrate it.

## Using the corpus

Facts live in `data/*.yaml`, one entry per (country, topic). Read the entries
relevant to the jurisdiction and subject at hand; do not load the whole corpus.

```bash
grep -l "country: UEMOA" data/*.yaml
grep -A 12 "topic: principal_liability_for_agents" data/*.yaml
```

Regional blocs: `OHADA`, `UEMOA`, `CEMAC`, `AU`. A country may be covered both by
its bloc and by its own entries — the country entry wins where both exist.

**Regenerate tables from the data; never copy a summary table from a reference
file.** Summary tables drop the caveats attached to the facts, which is exactly
how a hedged statement becomes a false certainty.

## Scope

Covered: services agreements, NDAs, commercial partnerships, freelance and
consultant contracts, distribution and mobile-money agent contracts, and the
cross-cutting clauses — data protection, force majeure, dispute resolution,
currency and payment.

**Not covered, and out of scope by design:** company formation documents and
shareholder agreements; investment instruments (SAFE, convertible notes);
employment contracts; any instrument requiring a notarial deed; real estate;
litigation. These carry too much exposure, or require an authenticated act.
Decline and refer to local counsel.

Depth by bloc — OHADA and UEMOA are the primary coverage; CEMAC is secondary;
Nigeria, Kenya, Ghana, South Africa, the Maghreb and Egypt are orientation only,
meaning enough to identify the applicable text, not enough to draft.

## Known risk areas

Places where a contract template written for Europe or the US tends to go wrong
in Africa. **These are questions to raise, not statements of law.** Except where
a corpus entry is named below, none of them is backed by a verified fact yet —
so raise the question, then say the corpus does not settle it and local counsel
must.

Stating any of these as legal fact would break the rule at the top of this file.

- **A principal's liability for its agents.** Backed by the corpus for UEMOA:
  see `principal_liability_for_agents` — it is mandatory there, and a clause
  shifting it towards third parties is void. Cite that entry; do not generalise
  it to other blocs.
- **Currency clauses.** XOF and XAF are not free-floating currencies, so an
  indexation clause modelled on a floating currency may be pointless or
  misdirected. Ask what the real exposure is before drafting one.
- **Force majeure.** Power and connectivity outages are frequent in several
  markets, which raises a genuine question about whether they are
  "unforeseeable" at all. A generic clause may leave the affected party
  unprotected on the most likely risk.
- **Independent-contractor status.** Jurisdictions in the region generally look
  at how the relationship actually runs rather than at how the contract
  describes it. Treat a clause that merely declares the contract non-employment
  as weak, and examine the facts — hours, direction, exclusivity.
- **Choice of dispute resolution.** Arbitration and the OHADA simplified
  recovery procedures involve a trade-off: what helps cross-border enforcement
  may hinder routine debt collection. Surface the trade-off; do not pick for the
  client.
- **Electronic signature.** Legal effect and the applicable technical standard
  vary, and national law often carries the standard. Do not assume a mainstream
  e-signature tool meets the local requirement.

## Adding a fact

A fact enters the corpus only with a source and a verification date. If it
quotes a primary text, the quote must appear word for word in an archived,
SHA-256-sealed copy under `sources/` — `scripts/check_quotes.py` enforces this,
and it is the only check that tests substance rather than form.

```bash
python3 scripts/validate.py       # schema conformance
python3 scripts/check_quotes.py   # quotes against the primary texts
```

Uncertain? Mark it `unverified` with a `note` explaining the doubt. Never invent
a plausible-looking number.
