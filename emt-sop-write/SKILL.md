---
name: emt-sop-write
description: Generate and revise Standard Operating Procedures for WHO Emergency Medical Teams of any EMT type, including Type 1 Mobile, Type 1 Fixed, Type 2, Type 3, and specialist care teams or cells. Use when Claude needs to draft field-ready EMT SOPs, adapt SOP content to mission data and team capability, ask for missing required SOP inputs, enforce mandatory SOP sections in the requested output language, maintain defined terms and roles, or enforce EMT capability limits from user-provided team scope.
---

# EMT SOP Write

## Core Contract

Generate Standard Operating Procedures for Emergency Medical Team deployments across EMT types. Default to Markdown output. Do not assume the SOP language: always ask the user to specify the SOP language before drafting a complete SOP.

Use English in internal reasoning, reference names, and skill-maintained terminology. Translate SOP section headings, role labels, terms, and definitions into the user-specified SOP language for the final output. Preserve official acronyms such as EMT, EMTCC, MoH, PHEOC, MDS, IPC, PPE, and SitRep unless the user provides local equivalents.

Treat the seven main SOP sections as nonnegotiable. Use these English canonical section names internally:

1. Scope
2. Goal
3. Roles and responsibilities
4. Terms and definitions
5. Procedure description
6. Appendices
7. Legal and regulatory requirements

In the SOP output, translate these seven headings into the requested language and keep their meaning, order, and separation. Create subsections when they improve clarity. Do not remove, merge, or reorder the main sections.

## Reference Loading

Read `references/emt_high_level_context.md` before drafting, revising, or reviewing a complete SOP. Use it for EMT domain context, EMT types, guiding principles, operating logic, coordination, records, reporting, operational requirements, public health role, operating constraints, terminology, and abbreviations.

Read `references/emt_sop_structure.md` before drafting, revising, or reviewing a complete SOP. Use it for document structure, section format, section purpose, and section-level rules.

Read `references/emt_sop_drafting_rules.md` before drafting a complete SOP or substantial revision. Use it for capability boundaries, role-bound procedure patterns, terminology discipline, appendices, coordination, contacts, ICT, data, and security rules.

For narrow edits, read only the relevant reference headings instead of loading whole files.

## Intake Workflow

Before drafting a complete SOP, ask for missing required data instead of inventing it. Collect:

- language, metadata, owner, approver, deployment phase, related SOPs, and related forms;
- EMT type or capability package, operating site/model/hours, staff groups, and patient groups;
- SOP topic, activation trigger, completion point, required records, deadlines, and record locations;
- named roles, alternates, command line, approval authority, handover responsibility, and coordination recipients;
- relevant legal or regulatory sources, including host-country authorization, clinical scope, medicines, customs, waste, data protection, liability, and retention rules.

If data is incomplete, ask concise follow-up questions grouped by section. Continue drafting only the parts supported by available data, and mark unresolved items as `To be completed:` only when the user explicitly wants a partial draft.

## Drafting Rules

Apply `references/emt_sop_drafting_rules.md` while drafting. Keep the SOP to one primary workflow and deployment phase, stay inside the approved capability boundary, write role-bound and evidence-backed procedure steps, keep terms consistent, move detailed supporting material into appendices, and make coordination, contacts, ICT, data, and security requirements operational.

## Review Before Final Output

Before finishing a complete SOP, use independent subagents when available to review the SOP artifact with three lenses: clarity, structure, and readability. Ask reviewers to flag EMT-type scope issues and missing legal-operational evidence. Summarize improvements before finalizing; if subagents are unavailable, do the three reviews yourself and state that they were not independent.

## Finalization Checklist

Before delivering a complete SOP, verify format, metadata, unresolved inputs, seven-section order, drafting rules, definitions, appendices, escalation, legal controls, and review findings.
