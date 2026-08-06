---
name: story-refinement-qa
description: Fetch unrefined EXAMPLE-PROJ JIRA stories and prepare QA-focused refinement notes. Use when the user mentions refinement, unrefined stories, unpointed stories, refinement prep, sprint refinement, grooming, or wants to prepare for a refinement meeting.
---

# Story Refinement QA Prep

## Context

- User is a **manual QA tester** (beginner technical level) on the **EXAMPLE-PROJ** team
- Refinement meetings: **[Your team's refinement schedule]**
- Explain everything in **plain, simple language** — avoid jargon

---

## Trigger Phrases

Activate this skill when the user says things like:
- "Show me unrefined stories"
- "What stories need refinement?"
- "Prep me for refinement"
- "What's coming up for refinement?"
- "Unpointed stories"
- "Grooming prep"

---

## Step 1: Fetch Unrefined Stories

Search JIRA for unpointed EXAMPLE-PROJ stories using `jira_search`:

```
CallMcpTool:
  server: user-atlassian-mcp-server
  toolName: jira_search
  arguments:
    jql: "project = EXAMPLE-PROJ AND issuetype = Story AND (storyPoints is EMPTY OR story_points is EMPTY) AND status != Done AND status != Closed ORDER BY priority DESC, created ASC"
    fields: "summary,priority,status,labels,assignee"
    limit: 20
    projects_filter: "EXAMPLE-PROJ"
```

If the above JQL fails due to field names, try alternate field names:
- `"Story Points" is EMPTY`
- `cf[10004] is EMPTY` (common custom field ID for story points)
- `story_points is EMPTY`

### Display Format

Present results as a numbered list sorted by priority (high to low):

```
Here are the unrefined stories in EXAMPLE-PROJ (sorted by priority):

| #  | Story            | Priority | Summary                        |
|----|------------------|----------|--------------------------------|
| 1  | EXAMPLE-PROJ-456   | High     | Add Apple Pay to checkout      |
| 2  | EXAMPLE-PROJ-789   | Medium   | Update order history UI        |
| 3  | EXAMPLE-PROJ-321   | Medium   | Fix size selector on PDP       |
| ...| ...              | ...      | ...                            |

Which story would you like me to explain? You can say "Tell me about #1" or use the story key.
```

---

## Step 2: Explain the Story Simply

When the user picks a story (by number or key), fetch full details:

```
CallMcpTool:
  server: user-atlassian-mcp-server
  toolName: jira_get_issue
  arguments:
    issue_key: <the key>
    fields: "*all"
    comment_limit: 50
```

**First, provide ONLY a plain language explanation.** Do NOT dump AC, scope, questions, and complexity all at once.

### What to include:

1. **What is this story about?** — Explain in plain, everyday language. If the story uses technical terms (API, SDK, deeplink, handler, cache, payload, etc.), define each one simply.
2. **Why is this being done?** — What problem does it solve? What's the benefit to the user or the team?
3. **What will the user see or experience differently?** — If applicable, describe the visible change.

Then ask: **"Would you like me to go deeper — AC review, scope, questions for refinement, or anything else?"**

**Example:**

> **EXAMPLE-PROJ-456 — Add Apple Pay to checkout**
>
> This story adds Apple Pay as a payment option when the user is buying something. Right now users can only pay with credit/debit cards. After this change, they'll see an "Apple Pay" button on the checkout screen and can pay with a single tap using their saved Apple Pay card.
>
> This is being done to make checkout faster and easier — fewer steps means more people complete their purchase.
>
> Would you like me to go deeper — AC review, scope, questions for refinement, or anything else?

---

## Step 3: Go Deeper Only When Asked

Only when the user asks for more details (e.g., "show me AC", "what questions should I ask?", "give me everything"), provide the relevant sections below. You can provide them individually or all together based on what the user asks.

### A. Acceptance Criteria Review

- List the acceptance criteria (AC) if they exist
- If AC are **missing**, flag this clearly: "No acceptance criteria found — you should ask for these in refinement"
- If AC are **vague**, call out which ones need more detail

### B. Scope Assessment

- **In scope:** What this story covers based on the description
- **Not clear / potentially out of scope:** Things that aren't mentioned but might be assumed
- **Flag** if scope is unclear or too broad

### C. Questions to Ask in Refinement

Provide ready-to-use questions grouped by category. Only include categories that are relevant to the story:

**Acceptance Criteria:**
- "What are the acceptance criteria for this story?"
- "How do we know when this is done?"
- "Are there specific scenarios we should cover?"

**Scope:**
- "What's in scope for this story?"
- "What's explicitly out of scope?"
- "Is [specific thing] included or will it be a separate story?"

**QA & Testing:**
- "How should QA test this?"
- "Are there edge cases we need to handle?"
- "Does this need to work on specific iOS/Android versions or devices?"
- "Are there any specific test accounts or test data needed?"
- "Will there be a test build available for QA before merging?"

**Design:**
- "Are there mockups or designs for this?"
- "What happens in error states (no internet, timeout, etc.)?"
- "Is there a loading state?"

**Dependencies:**
- "Does this depend on any backend or API changes?"
- "Are those API changes already done or still in progress?"
- "Does this block or get blocked by any other story?"

**Risk & Regression:**
- "What existing features might be affected by this change?"
- "Is there anything that could break?"
- "Do we need regression testing in any specific area?"

**Accessibility:**
- "Does this need VoiceOver support?"
- "Are there any accessibility requirements?"

### D. QA Complexity Estimate

Suggest a complexity level for QA testing:

| Complexity | Description | Typical Points |
|-----------|-------------|----------------|
| **Low** | Simple change, limited testing needed, 1-2 test scenarios | 1-2 |
| **Medium** | Moderate change, several scenarios, some edge cases | 3-5 |
| **High** | Complex change, many scenarios, multiple edge cases, regression risk | 8-13 |

Explain why you rated it at that level.

---

## Step 3: Batch Prep (Optional)

If the user asks to prep multiple stories (e.g., "prep me for the top 5"), provide a condensed version for each:

```
### 1. EXAMPLE-PROJ-456 — Add Apple Pay to checkout
**What it is:** [1-2 sentence plain language summary]
**AC Status:** ✅ Has AC / ⚠️ Missing AC / ⚠️ Vague AC
**Key questions to ask:**
- [Top 2-3 most important questions for this story]
**QA Complexity:** Medium (3-5 points)

---

### 2. EXAMPLE-PROJ-789 — Update order history UI
...
```

---

## Communication Style

- Use **plain, simple language** — the user is non-technical
- Explain any technical terms (API, backend, regression, edge case, etc.)
- Use tables and bullet points for clarity
- Be encouraging — the user is building confidence in refinement meetings
- Frame questions as things the user can **directly say** in the meeting (conversational tone)
