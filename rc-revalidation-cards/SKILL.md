---
name: rc-revalidation-cards
description: Find JIRA cards the user tested in a given fix version for RC revalidation. Checks changelogs to identify cards where the user made status transitions, uploaded attachments, or assigned themselves. Use when the user mentions RC revalidation, RC cards, recheck cards, what cards did I work on, my RC list, what do I need to revalidate, or any variation of finding their tested cards for a release candidate build.
---

# RC Revalidation Cards

Find which EXAMPLE-PROJ cards the user personally tested for a given fix version, so they know what to revalidate when the RC build drops.

## Step 1: Get the Fix Version

Ask the user for the fix version if not already provided (e.g., `26.20`).

If the user provides a JIRA filter URL, extract the fix version from the `fixVersion` parameter in the JQL.

## Step 2: Search for Cards

Use the `jira_search` MCP tool:

```
Tool: jira_search
Args: {
  "jql": "fixVersion in (<VERSION>) AND project = \"Mobile App\" AND status not in (Deployed, \"Done Deploy Not Needed\") ORDER BY key DESC",
  "fields": "summary,status,assignee,priority,issuetype,labels",
  "limit": 50
}
```

If there are more than 50 results, paginate using `start_at`.

## Step 3: Check Each Card's Changelog

For each card returned, fetch the changelog to find the user's activity:

```
Tool: jira_get_issue
Args: {
  "issue_key": "<KEY>",
  "fields": "summary",
  "expand": "changelog",
  "comment_limit": 0,
  "update_history": false
}
```

Process up to 4 cards in parallel to save time.

## Step 4: Identify User's Cards

A card counts as "worked on" if **the current user** (email: your.name@yourcompany.com, ID: JIRAUSER-XXXXX) performed any of these actions in the changelog:

- **Status transition** — especially QA → Done or QA → Dev (sent back)
- **Assigned themselves** to the card
- **Uploaded attachments** (screenshots, videos, .chls files)
- **Updated fields** like Fix Version or labels

Ignore cards where the user's only activity was reporting (creating) the card with no QA involvement.

## Step 5: Present Results

Group cards by **platform** (iOS / Android / Both) and present as a numbered list with tappable links.

### Output Format

```
**Your RC <VERSION> revalidation list — <COUNT> cards:**

**iOS:**
1. [EXAMPLE-PROJ-XXXX — Summary](https://your-jira-instance.com/browse/EXAMPLE-PROJ-XXXX)

**Android:**
1. [EXAMPLE-PROJ-YYYY — Summary](https://your-jira-instance.com/browse/EXAMPLE-PROJ-YYYY)
```

Each platform section starts its own numbered list at 1. Do NOT continue numbering across platforms.

Do NOT add notes about what the user did on each card (e.g., "sent back to dev once, then passed"). Just list the cards cleanly.

### Cards NOT Worked On

After the user's list, show the remaining cards they did NOT work on as a numbered list with clickable links (same format as the user's cards) and a short reason (e.g., "tested by Teammate", "labeled Testing_NA — no QA needed"), so the user can quickly open any card if needed.

## Notes

- The user is a QA tester and does not use Xcode/Git — keep output non-technical
- Always use tappable markdown links (not plain URLs or table-only links)
- The `batch_get_changelogs` tool only works on Jira Cloud — [Company] uses Jira Server, so always use `jira_get_issue` with `expand: "changelog"` instead
- If a card has the label `Testing_NA`, it likely doesn't need QA and can be skipped
