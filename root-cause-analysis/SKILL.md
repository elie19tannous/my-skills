---
name: root-cause-analysis
description: Perform root cause analysis for bugs found in RC builds. Guides through build comparison, PR identification, and generates a shareable RCA document. Use when the user mentions root cause analysis, RCA, what caused a bug, why a bug happened, find the root cause, regression analysis, or wants to trace a bug back to its origin.
---

# Root Cause Analysis

## Context

- User is a **manual QA tester** on the **EXAMPLE-PROJ** team
- Tests RC builds and feature branch builds on physical Android devices
- PRs are linked in JIRA story comments
- Explain everything in **plain, simple language**
- Always ask clarifying questions rather than assuming

## Step 1: Gather Info

Ask the user for (if not already provided):

1. **The RC bug ticket** — JIRA key (e.g., EXAMPLE-PROJ-10444)
2. **The RC version** where the bug was found (e.g., RC 26.19.0)
3. **Any suspected related tickets** — if they already have a theory on what caused it

Example prompt:
> What's the bug ticket, which RC version was it found in, and do you have any suspected related tickets?

If the user provides all info upfront, skip straight to Step 2.

## Step 2: Fetch JIRA Details

Fetch the RC bug ticket:

```
CallMcpTool:
  server: user-atlassian-mcp-server
  toolName: jira_get_issue
  arguments:
    issue_key: <bug key>
    fields: "*all"
    comment_limit: 50
```

From the ticket, extract:
- **Bug description** — what's broken, expected vs actual
- **Linked issues** — look for "Bug Caused By", "Related", "Problem/Incident" links
- **Developer comments** — look for PR links or root cause hints
- **Fix version** — which RC/release

If there are linked issues or suspected related tickets, fetch those too.

## Step 3: Guide Build Comparison

This is the most important step. Help the user figure out **when the bug was introduced**.

Ask the user to test across builds and fill in a comparison table:

| Build | Version | Bug Present? |
|---|---|---|
| Production (current live) | ? | ? |
| Previous RC | ? | ? |
| Current RC (where bug found) | ? | Yes |
| Feature branch (if applicable) | ? | ? |
| RC after revert (if applicable) | ? | ? |

**Questions to ask:**
- "Was this bug present in the previous RC or production build?"
- "Has the bug area been changed by any recent feature branch?"
- "Did you test this on the feature branch build? What was the result?"
- "Which devices did you test on? Did the result vary by device?"

**Key principle:** If the bug exists in the current RC but NOT in the previous RC/production, then something merged between those two builds caused it.

If the user already has build comparison data (e.g., from their own testing or an image), use that instead of asking redundant questions.

## Step 4: Identify the Guilty PR

Use these methods in order (fastest first):

### Method 1: Check JIRA Links
Look at the bug ticket's linked issues. If there's a "Bug Caused By" or "Problem/Incident" link, that's likely the cause.

### Method 2: Check Developer Comments
Scan comments on the bug ticket — devs often identify the cause and drop PR links.

### Method 3: Filter by Area
Match the bug area to recently merged cards:
- What area is the bug in? (e.g., PDP, size tray, cart, checkout)
- Which cards merged into this RC touch that area?
- Narrow from all merged cards to 2-3 suspects

### Method 4: Ask the Dev Team
If methods 1-3 don't give a clear answer, suggest the user ask in Slack:
> "We found [bug description] in RC [version]. Did anyone merge changes to [area] recently?"

### Method 5: Analyze PR Changes
If a suspect PR is identified, use GitHub CLI to check what files it changed:

```bash
gh pr diff <PR_NUMBER> --repo <REPO> --name-only
```

Translate file paths to plain-language app areas. Confirm the PR touches the same area as the bug.

## Step 5: Determine Root Cause Category

Once the guilty PR/change is identified, classify the root cause:

| Category | Description |
|---|---|
| **Code side effect** | Fix for one bug introduced another |
| **Device-specific** | Bug only manifests on certain devices/screen sizes |
| **Logic error** | Incorrect conditional, wrong calculation, missing edge case |
| **Layout/UI regression** | Visual/layout change broke rendering on some configurations |
| **Merge conflict** | Bad merge resolution introduced broken code |
| **Missing requirements** | Story didn't account for a scenario |
| **Dependency change** | Library update changed behavior |
| **Config/environment** | Works in one environment but not another |

## Step 6: Determine Why It Wasn't Caught Earlier

Ask the user:
- "Was this tested on the feature branch? What was the result?"
- "Which devices were used during feature branch testing?"
- "Were there any signs of this during feature testing that were dismissed?"

Common reasons:
- **Device coverage gap** — tested on devices that didn't show the issue
- **Insufficient test scenarios** — the specific flow wasn't covered
- **Intermittent behavior** — bug doesn't reproduce consistently
- **Environment difference** — feature branch vs RC behave differently
- **Passed on partial results** — some devices passed, card moved forward

Present the findings **without blaming anyone**. Focus on process gaps, not people.

## Step 7: Generate the RCA Document

Output a clean, shareable RCA using this template:

```markdown
## Root Cause Analysis: [BUG TICKET KEY]

**Bug:** [Bug summary from JIRA]

**Severity:** [Priority from JIRA]

**Found in:** [RC version and build number]

---

### Timeline

| Build | Version | [Original Bug] | [New Bug] |
|---|---|---|---|
| [Build 1] | [Version] | [Status] | [Status] |
| [Build 2] | [Version] | [Status] | [Status] |
| [Build 3] | [Version] | [Status] | [Status] |

### Root Cause

[1-2 paragraphs explaining what change caused the bug and why]

### Why It Wasn't Caught in Feature Branch Testing

[1 paragraph explaining the gap — focus on process, not people]

### Resolution

[What was done to fix it — revert, hotfix, new ticket created]

### Preventive Action

[1-2 actionable suggestions to prevent similar issues]
```

Adjust the template as needed based on the specific situation. Not all sections may apply.

## Step 8: Help with Ticket Management

After the RCA is complete, guide the user on JIRA housekeeping:

### Where to Post the RCA
1. **On the RC bug ticket** as a comment — this is the primary home
2. **On the follow-up ticket** (if created) as a shorter summary for dev context

### Old Ticket Resolution
If the original fix was reverted and a new ticket was created:
- **Resolution: Duplicate** — the issue is now tracked under the new ticket
- Add a closing comment explaining: what happened, why the fix was reverted, and which new ticket tracks it

### Follow-up Ticket
Ensure a follow-up ticket exists for the proper fix. If not, offer to help create one.

## Important Rules

- **Ask before assuming** — if the timeline, testing details, or device info is unclear, ask the user
- **Never blame individuals** — focus on process gaps, device coverage, and systemic improvements
- **Use plain language** — no technical jargon about code internals unless the user asks
- **Show the build comparison table** — this is the core evidence of any RCA
- **Developer comments are gold** — always check JIRA comments for dev-provided root cause info
- **Don't fabricate PR analysis** — only reference PRs that are confirmed through JIRA links or dev comments
- **RC build is the source of truth** — production/RC comparison is the definitive way to determine when a bug was introduced
