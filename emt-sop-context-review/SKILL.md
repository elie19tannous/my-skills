---
name: emt-sop-context-review
description: Review Emergency Medical Team SOPs or standard operating procedures against EMT type, WHO EMT classification, mission context, humanitarian deployment, disaster response, medical mission planning, available resources, unreliable field conditions, coordination constraints, international law, host-country authorization, and cultural fit. Use when Claude needs to critique whether an SOP is realistic, lawful, culturally aware, and operationally safe for a specific EMT deployment context.
---

# EMT SOP Context Review

## Core Contract

Review the SOP as a critical context reviewer. Do not rewrite the SOP unless the user asks. Identify gaps, unsafe assumptions, unrealistic dependencies, and places where the SOP may fail in an EMT deployment.

When possible, suggest running this review in a subagent with clean context. Give the subagent only the SOP, stated EMT type or capability package, mission context, and relevant reference files. Ask it to critique the SOP artifact, not to justify the current draft.

## Reference Loading

Load references only when needed:

- Read `references/emt_high_level_context.md` when the SOP depends on general EMT principles, coordination, records, reporting, operating constraints, terminology, or abbreviations.
- Read the EMT type reference only when the SOP names that type or the type is needed to check scope:
  - `references/emt_type_1_mobile_context.md`
  - `references/emt_type_1_fixed_context.md`
  - `references/emt_type_2_context.md`
  - `references/emt_type_3_context.md`
  - `references/emt_specialized_care_teams_context.md`

If the EMT type, specialist mandate, mission country, operating model, or team capability statement is missing, flag the missing context before making firm conclusions.

## Review Checks

Check the SOP against these lenses:

1. EMT scope and capability: Does it exceed the stated EMT type, specialist mandate, staffing, equipment, medicines, diagnostics, transport, referral access, or assigned tasking?
2. Resources and logistics: Does it assume reliable power, water, oxygen, communications, cold chain, stock, transport, security, staff availability, printing, internet, or local procurement without contingency?
3. Mission conditions: Does it work during surge, infrastructure damage, supply disruption, insecurity, weather exposure, language barriers, fatigue, interrupted work, and unreliable referral pathways?
4. Coordination and authority: Are EMTCC, MoH, PHEOC/EOC, referral facilities, security coordination, cluster systems, and team command roles clear where needed?
5. Legal and regulatory fit: Does it depend on host-country authorization, licensing, credential recognition, import/customs, medicines, controlled drugs, data protection, telecoms, waste, liability, consent, death reporting, or record retention without naming the authority or evidence?
6. Culture and protection: Does it account for local language, cultural norms, gender, age, disability, privacy, dignity, safeguarding, SGBV risk, community acceptance, and safe access?
7. Evidence and accountability: Are critical decisions, exceptions, referrals, incidents, handovers, reports, and legal checks tied to records or logs?

## Output Format

Return a concise review with these sections:

1. Context gaps: missing inputs that limit the review.
2. High-risk findings: issues that could make the SOP unsafe, unlawful, or unusable.
3. Operational realism findings: assumptions likely to fail in field conditions.
4. Legal, coordination, and cultural findings: authority, law, coordination, language, culture, or protection gaps.
5. Suggested fixes: practical changes, phrased as recommendations.

For each finding, include:

- issue;
- why it matters in EMT operations;
- affected SOP section or step if known;
- recommended correction.

Do not overstate uncertainty. If a problem depends on missing mission data, label it as a question or conditional risk.
