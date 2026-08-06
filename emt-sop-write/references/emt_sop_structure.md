# EMT SOP Structure Reference

Use this reference when drafting a complete EMT SOP. It describes the expected Markdown structure, the purpose of each section, and the main rules to follow. Translate section headings into the requested SOP language while preserving this order and meaning.

## Document Title

**Format:** `# [SOP topic or workflow name]`

**Purpose:** Give the SOP a clear operational name that identifies the workflow.

**Main rules:**

- Use a concise title tied to the action or capability, such as communication setup, triage, referral, pharmacy stock control, or patient registration.
- Do not use a broad title if the SOP covers only one deployment phase or one workflow.
- Keep the title consistent with the SOP ID and related SOP references.

## Metadata Table

**Format:** Markdown table before section 1.

Required fields:

| Field | Expected content |
|---|---|
| SOP ID | Controlled identifier, for example `COM-01` |
| Version | Version number |
| Effective date | Date the SOP enters force |
| Review date or review cycle | Date or cycle for review |
| SOP owner | Role or named owner |
| Approver | Approval authority |
| EMT type or capability package | EMT Type 1 Mobile, Type 1 Fixed, Type 2, Type 3, or specialist cell |
| Deployment phase | Preparedness, setup, operations, maintenance, demobilization, or other defined phase |
| Related SOPs | Linked or named dependent SOPs |
| Related forms and logs | Appendices, forms, checklists, logs, or registers |

**Purpose:** Make document control, authorization, scope, and dependencies visible before the procedure starts.

**Main rules:**

- Do not invent missing metadata. Ask for it, or mark it unresolved only if the user requested a partial draft.
- Keep field names consistent across SOPs in the same team documentation set.
- Include related forms and logs when the procedure depends on evidence artifacts.

## 1. Scope

**Format:** `## 1. Scope` followed by one or more short paragraphs. Use bullets when listing included and excluded services, settings, users, or boundaries.

**Purpose:** Define exactly what the SOP covers, where and when it applies, who must use it, and what it does not authorize.

**Main rules:**

- State the EMT type, operational setting, deployment phase, trigger, users, patient or task groups, included services, and excluded services.
- Use explicit boundary language: `applies to`, `covers`, `does not cover`, `does not authorize`.
- Keep the SOP inside the team capability and local authorization supplied by the user.
- Name interfaces with other teams, authorities, SOPs, forms, or systems when they affect execution.

## 2. Goal

**Format:** `## 2. Goal` with one concise purpose paragraph followed by bullets for operational outcomes when useful.

**Purpose:** State the end state the procedure must achieve for safety, quality, coordination, continuity, documentation, or readiness.

**Main rules:**

- Write outcomes, not background.
- Use active verbs such as `ensure`, `maintain`, `confirm`, `document`, `report`, `refer`, `handover`, or `escalate`.
- Include measurable readiness, reporting, or completion expectations when they are known.
- Avoid goals that exceed the SOP scope.

## 3. Roles And Responsibilities

**Format:** `## 3. Roles and responsibilities` with a Markdown table.

Recommended columns:

| Role | Responsibilities |
|---|---|
| [Role name] | [Role-bound responsibilities] |

**Purpose:** Assign ownership, authority, escalation, documentation, and handover duties.

**Main rules:**

- Use role-action wording. Each safety-critical responsibility must belong to a named role.
- Include alternates, approval authority, escalation authority, and handover responsibility when relevant.
- Use role names consistently in the procedure and terms sections.
- Do not assign responsibility to vague groups such as `the team` when a specific role is required.

## 4. Terms And Definitions

**Format:** `## 4. Terms and definitions` with a Markdown table.

Recommended columns:

| Term | Definition |
|---|---|
| [Term or acronym] | [Operational definition] |

**Purpose:** Standardize terms, acronyms, roles, authorities, systems, forms, patient categories, and operational states that affect interpretation or action.

**Main rules:**

- Define every acronym, locally binding term, role, authority, form, system, and status that affects the procedure.
- Keep definitions short and operational.
- Preserve official acronyms unless the user provides local official equivalents.
- Use translated terms consistently in the requested SOP language.
- Add new terms here if they appear later in the SOP.

## 5. Procedure Description

**Format:** `## 5. Procedure description` with numbered subsections. Use numbered steps for the hot path and tables for resources, escalation thresholds, or decision rules.

**Purpose:** Provide the executable workflow from trigger to completion.

**Main rules:**

- Put the responsible role before each safety-critical action.
- Each critical step should include action, output or evidence, form or appendix, escalation path, and completion criterion when applicable.
- Use `If...then...` for decisions and exceptions.
- Use `Do not...unless...` for hard boundaries.
- Keep long explanations out of the hot path. Put supporting detail in notes or appendices.
- Avoid vague timing, ownership, and thresholds.

### 5.1 Trigger Or Activation

**Format:** Short paragraph or numbered steps.

**Purpose:** State who starts the SOP and under what condition.

**Main rules:**

- Name the activating role or authority.
- State the activation event, deployment phase, or operational condition.
- Identify the first documentation action or checklist when relevant.

### 5.2 Preconditions

**Format:** Bullet list or table.

**Purpose:** Define what must be confirmed before the workflow starts.

**Main rules:**

- Include minimum staffing, equipment, location, safety, authorization, forms, systems, and coordination prerequisites.
- Do not let the SOP proceed silently when a prerequisite is missing. Define escalation or degraded operation.

### 5.3 Required Resources

**Format:** Table or direct reference to an appendix.

Recommended columns:

| Resource type | Required resource | Minimum condition | Responsible role | Evidence |
|---|---|---|---|---|

**Purpose:** Make people, equipment, supplies, systems, forms, and records needed for the procedure visible and auditable.

**Main rules:**

- Use an appendix for long lists.
- Include minimum quantity, readiness state, location, responsible role, and evidence when known.
- Keep resources aligned with EMT type capability and local authorization.

### 5.4 Workflow Steps

**Format:** Numbered subsections and numbered steps. Split complex procedures into logical phases.

**Purpose:** Describe how the work is performed.

**Main rules:**

- Use one action per step when timing, safety, or accountability matters.
- Start steps with the responsible role.
- Link required forms, logs, checklists, reports, or appendices at the point of use.
- Include documentation and reporting duties in the workflow, not only at the end.

### Escalation

**Format:** Table inside section 5 unless the SOP needs several escalation tables.

Recommended columns:

| Event | Threshold | Action |
|---|---|---|

**Purpose:** Define when normal procedure is no longer enough and who must act.

**Main rules:**

- Use concrete thresholds.
- Name the responsible role and recipient of escalation.
- Include safety, capacity, legal, data, communication, supply, referral, security, and service-continuity triggers when relevant.
- Include degraded operation or stop-work conditions where needed.

### Completion Criteria

**Format:** Bullet list near the end of section 5.

**Purpose:** Define when the procedure is complete.

**Main rules:**

- Link completion to verified outputs, submitted reports, completed forms, handover, or leadership confirmation.
- Include unresolved limitations or degraded status if they affect readiness or service delivery.
- Do not use subjective completion statements such as `everything is ready` without evidence.

## 6. Appendices

**Format:** `## 6. Appendices` with a Markdown table.

Recommended columns:

| Appendix | Name | File or location |
|---|---|---|

**Purpose:** List controlled supporting tools that make the SOP usable in the field.

**Main rules:**

- Include checklists, forms, logs, contact trees, resource lists, diagrams, decision records, reporting templates, and handover tools where useful.
- Reference appendices inside the procedure where staff must use them.
- Do not hide mandatory operational steps only in appendices.
- Keep appendix names and file names consistent.

## 7. Legal And Regulatory Requirements

**Format:** `## 7. Legal and regulatory requirements` with a Markdown table.

Recommended columns:

| Requirement or source | Operational implication | Responsible role | Required evidence |
|---|---|---|---|

**Purpose:** Convert legal, regulatory, authorization, and policy requirements into field actions and evidence.

**Main rules:**

- Ask the user for SOP-specific legal and regulatory sources when they matter.
- Include host-country authorization, clinical scope, credential recognition, import/customs, medicines, telecoms, data protection, confidentiality, waste, liability, and record retention when relevant.
- State operational implications rather than copying long legal text.
- Assign each requirement to a responsible role and evidence artifact.
- If no SOP-specific legal controls are identified, state that explicitly and reference baseline authorization if provided.

## Structure Checklist

Before finalizing a complete SOP, verify:

- Title and metadata are present.
- Sections 1-7 are present, translated consistently, and in order.
- Scope, goal, roles, terms, procedure, appendices, and legal requirements do not contradict each other.
- Procedure steps are role-bound, evidence-backed, and inside approved EMT capability.
- Defined roles and terms are used consistently.
- Appendices are listed and referenced where used.
- Legal requirements are mapped to action, responsible role, and evidence when applicable.
