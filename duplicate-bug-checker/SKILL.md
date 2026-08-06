---
name: duplicate-bug-checker
description: Search JIRA for duplicate bugs and stories before filing a new issue. Searches across all projects, not just EXAMPLE-PROJ. Use when the user describes a bug they found, asks if a bug already exists, mentions duplicate check, or wants to check before filing a bug.
---

# Duplicate Bug Checker

## Context

- User is a **manual QA tester** on the **EXAMPLE-PROJ** team
- Searches **all JIRA projects** (not just EXAMPLE-PROJ) because other teams may have already reported the same issue
- Checks both **Bugs** and **Stories** (a known issue might already have a story to fix it)
- Explain results in **plain, simple language**

## Trigger Phrases

Activate when the user says things like:
- "Is there already a bug for..."
- "Check if this bug exists"
- "I found a bug — check for duplicates"
- "Has anyone reported..."
- "Duplicate check"
- "Before I file this..."

## Step 1: Extract Keywords

From the user's description, identify:
- **Area/screen** (e.g., cart, checkout, home, PDP, favorites, profile, search)
- **Symptom** (e.g., crash, freeze, not loading, blank screen, wrong data, error)
- **Action** (e.g., tap, scroll, add to cart, login, checkout)

Combine these into 2-3 search terms. Prefer short, specific terms over long phrases.

## Step 2: Search JIRA (All Projects)

Run **two searches** using `jira_search` on `user-atlassian-mcp-server`:

### Search A: Broad text search (all projects)

```
jql: "text ~ \"keyword1 keyword2\" AND issuetype in (Bug, Story) AND status != Done AND status != Closed ORDER BY updated DESC"
fields: "summary,status,priority,issuetype,assignee,project,created,updated"
limit: 15
```

Do NOT set `projects_filter` — leave it empty/null so it searches everywhere.

### Search B: Alternate keyword combo (all projects)

Use different keyword phrasing or individual keywords to catch issues worded differently:

```
jql: "summary ~ \"keyword1\" AND summary ~ \"keyword2\" AND issuetype in (Bug, Story) AND status != Done AND status != Closed ORDER BY updated DESC"
fields: "summary,status,priority,issuetype,assignee,project,created,updated"
limit: 15
```

### Search C: Include resolved/closed (EXAMPLE-PROJ only)

Check if it was already found and fixed:

```
jql: "text ~ \"keyword1 keyword2\" AND issuetype in (Bug, Story) AND project = EXAMPLE-PROJ AND status in (Done, Closed) ORDER BY updated DESC"
fields: "summary,status,priority,issuetype,resolution,updated"
limit: 10
```

### If searches return errors

- If JQL fails due to reserved characters in keywords, escape or simplify the keywords
- If `text ~` fails, fall back to `summary ~`
- If no results, try broader keywords (e.g., just the screen name)

## Step 3: Deduplicate & Rank Results

1. Combine results from all searches, removing duplicate issue keys
2. Rank by relevance:
   - **High match**: Summary contains multiple keywords from the user's description
   - **Possible match**: Summary contains at least one keyword and is in a related area
   - **Low match**: Only loosely related

## Step 4: Present Results

### If matches found

Show a table grouped by match strength:

```
I searched across all JIRA projects. Here's what I found:

**Likely matches:**

| # | Ticket | Project | Type | Summary | Status | Priority |
|---|--------|---------|------|---------|--------|----------|
| 1 | EXAMPLE-PROJ-456 | EXAMPLE-PROJ | Bug | Cart crash on checkout tap | Open | High |
| 2 | OTHER-PROJ-789 | OTHER TEAM | Bug | Checkout crash on iOS 17 | In Progress | Medium |

**Possible matches:**

| # | Ticket | Project | Type | Summary | Status | Priority |
|---|--------|---------|------|---------|--------|----------|
| 3 | EXAMPLE-PROJ-321 | EXAMPLE-PROJ | Story | Refactor checkout flow | Open | Medium |

**Already fixed:**

| # | Ticket | Summary | Status | Resolved |
|---|--------|---------|--------|----------|
| 4 | EXAMPLE-PROJ-111 | Cart crash with empty items | Done | Jan 2026 |
```

Then provide a plain-language verdict:

> **#1 looks like a strong match** — it's about the same crash in the same area.
> Check with the team if your issue is the same as EXAMPLE-PROJ-456 before filing a new one.
>
> **#2 is from another team** (OTHER TEAM) — they may be seeing the same thing. Worth checking.
>
> Want me to file a new bug, or do any of these match what you're seeing?

### If no matches found

```
I searched across all JIRA projects for bugs and stories related to
[brief description]. No duplicates found — this looks like a new issue.

Want me to file a bug for it?
```

## Step 5: Offer to File (if no duplicate)

If the user confirms it's not a duplicate, transition to bug filing using the
jira-teamwork skill's bug creation workflow. Carry forward all the details
the user already provided so they don't have to repeat themselves.

## Important Rules

- **Always search all projects first** — never limit to EXAMPLE-PROJ only for the initial search
- **Show the project name** in results so the user can see which team reported it
- **Include both open AND resolved issues** — a fixed bug might have regressed
- **Never auto-file** — always confirm with the user first
- **Keep the verdict simple** — plain language, no jargon
- **If too many results**, show only the top 5 most relevant and mention how many total were found
