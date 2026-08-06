---
name: jira-story-context
description: Fetch and internalize JIRA story/bug details for context-driven follow-up. Use ONLY when the user mentions a EXAMPLE-PROJ JIRA ticket, story, bug, card, or issue key (e.g., EXAMPLE-PROJ-123), or asks to look at, check, or review a EXAMPLE-PROJ JIRA item.
---

# JIRA Story Context

## Scope — EXAMPLE-PROJ Only

This skill applies **only** to JIRA issues from the **EXAMPLE-PROJ** project (keys like `EXAMPLE-PROJ-1234`).

If the user mentions a ticket from any other project (e.g., `OTHER-456`, `XYZ-789`), do **NOT** follow this skill. Instead, just fetch and display the issue details normally as you would without this skill.

## Step 1: Fetch & Internalize

Use the Atlassian MCP tool `jira_get_issue` to fetch the full story:

```
CallMcpTool:
  server: user-atlassian-mcp-server
  toolName: jira_get_issue
  arguments:
    issue_key: <the key>
    fields: "*all"
    comment_limit: 50
```

Read and internalize everything: description, acceptance criteria, comments, linked PRs (from comments), status, assignee, labels, priority, subtasks — all of it.

## Step 2: Auto-find PR (from comments only)

After fetching the issue, scan comments for a GitHub PR link. Do NOT ask the user for the PR link upfront.

1. Scan comments from **newest to oldest**, focusing on **developer comments** (skip QA/tester comments like pushbacks, retests, etc.)
2. Look for a **GitHub PR URL** in the comment text (e.g., `github.com/.../pull/123`)
3. If found, use it as the PR for this story
4. If **no PR link found** in any comment, ask the user:
   > "I couldn't find a PR link in the comments. Could you share it?"

### Important nuances

- QA may push back the card multiple times. There could be several rounds of developer comments. Always use the **latest** developer comment that contains a PR link.
- A "developer comment" typically contains a link (PR or build URL). QA comments typically contain text about test results, bugs found, or pushback reasons.
- Do NOT try to open/fetch build links — they require login and will fail.

## Step 3: Explain the Card in Simple Terms

After fetching the issue and finding the PR, **always start by explaining the card in plain, non-technical language**. Do NOT jump to test scenarios. The user needs to understand the card first.

Include the following:

1. **What is this card about?** — Explain in plain, everyday language that anyone can understand — as if explaining to a non-technical person. Avoid developer jargon entirely. If the card uses technical terms (e.g., GUID, deeplink, handler, parse, SharedPreferences, callback), define each one in simple words.
2. **Why does it matter?** — What problem does it solve? What's the benefit to the team or the customer?
3. **Current status** — Status, assignee, PR if found, builds if available in comments.

Then ask: **"What would you like me to do?"**

**Example:**

> **EXAMPLE-PROJ-4442** — This card adds a beta testing link to the Android app.
>
> A special link that internal employees can click to join a beta test group. When they click it, the app saves a test group ID (a long unique number called a GUID), shows a confirmation popup, and restarts. After that, the app shows them whatever experimental feature is being tested. It only works for @yourcompany.com email accounts and the test group ID expires after 7 days.
>
> This helps internal teams test new features internally with real employees before releasing to customers. Customers benefit because features are more polished when they finally go live.
>
> Currently in **QA**. Developer: Jane Developer. PR: #1234.
>
> What would you like me to do?

## Step 4: Elaborate Only When Asked

If the user asks for specifics (AC, description, comments, PR details), then provide that information. Otherwise, keep it internalized as context for follow-up questions.

---

## Language Rule — Always Use Simple, Non-Technical Language

Throughout the entire conversation (not just Step 3), **always use simple, everyday language**. The user is a QA tester, not a developer.

- If a technical term is unavoidable, **immediately explain it in plain words** in the same sentence.
- Never assume the user knows developer terminology.

**Examples of what to avoid vs. what to say:**

| Avoid | Say instead |
|---|---|
| MainActivityV2.onResume | When the main screen of the app becomes visible |
| Cold start | App opens from a fully closed state |
| SharedPreferences | App's internal storage on the phone |
| Race condition | A timing issue where two things happen at the same time and conflict |
| Non-main activity | Any screen before the main app screen (like splash/loading) |
| Process restart | The app closes and opens again |
| Handler | Code that catches and processes something |
| Parse | Read and extract specific pieces of information |
| GUID | A long unique ID (like a unique ticket number) |
| Callback | When the app responds back after something happens |

This applies to test scenario descriptions, bug explanations, step instructions — everything.

---

## Testing Scenarios (When Asked)

When the user asks "what do I have to test?", "test scenarios", or similar:

### Phase 1: High-Level Scenarios Only

First, provide **only** the scenario name and expected result in a simple table. Do NOT include detailed steps, commands, or instructions yet.

**Format:**

> **From story/AC:**
>
> | # | Scenario | Expected Result |
> |---|---|---|
> | 1 | Valid deeplink with @yourcompany.com account | Dialog shows, app restarts |
> | 2 | Empty tag rejected | No dialog, no crash |
> | 3 | Non-[Company] email rejected | No dialog, no crash |
>
> **From PR code changes (+ potential impact):**
>
> | # | Scenario | Expected Result |
> |---|---|---|
> | 4 | App restart after pressing OK | App fully restarts, no crash |
> | 5 | Other deeplinks still work | No regression |

Then ask: **"Which one do you want to start with?"** or **"Ready to start testing?"**

### Phase 2: Detailed Steps on Demand

Only when the user asks to test a specific scenario (e.g., "let's test #3", "how to test the expiry one", "give me steps for test 2"), **then** provide the detailed steps for that ONE scenario:

- Step-by-step instructions
- Exact commands (ADB, deeplink URLs, etc.)
- What to verify at each step
- Expected output

**NEVER dump all detailed steps for all scenarios at once.** One scenario at a time, only when asked.

**Format for detailed steps:**

> **Test #3 — Non-[Company] email rejected**
>
> 1. Sign in with a non-@yourcompany.com email (e.g., personal Gmail)
> 2. Trigger the deeplink: `myapp://x-callback-url/exte?tag=test-guid-123`
> 3. Observe the app
>
> Expected: No dialog, no crash. Nothing visible happens.
>
> Let me know what happens!

### From PR Code Changes

If a PR or commit is linked (found in comments, linked issues, or provided by the user):

1. **Actually attempt to access and review the PR diff / code changes** — do not guess or assume
2. If accessible, provide **additional test scenarios** covering:
   - Areas directly touched by the code changes
   - Areas that **might be affected** (regression/impact zones)
3. Clearly separate these from the story-based scenarios so the user knows which are from AC vs. code impact

**If the PR is not accessible** (auth issues, private repo, etc.), explicitly tell the user:
> "I couldn't access the PR — unable to provide PR-based test scenarios."

**If the PR is accessible but no additional testing areas are found**, explicitly tell the user:
> "Reviewed the PR — no additional affected areas or extra test scenarios beyond the story/AC coverage."

**NEVER fabricate or assume PR-based scenarios.** Only provide them if you have actually reviewed the code diff.

---

## Deeplink / Universal Link / Singular Link Testing

When test scenarios involve any type of deeplink (universal links, Singular links, deferred deeplinks, or any custom scheme links):

Provide **step-by-step instructions** so the user can execute immediately without having to look up how to trigger or test them. Include:

- The exact link/URL format to use
- How to trigger it (e.g., Notes app, Safari, terminal command, Singular dashboard)
- What to verify at each step (expected screen, expected behavior)
- Any preconditions (logged in/out, app installed/not installed, first launch)
