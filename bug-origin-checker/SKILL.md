---
name: bug-origin-checker
description: Determine if a bug found during feature branch testing is pre-existing or introduced by the branch. Analyzes PR code changes and compares against the bug area. Use when the user finds a bug on a feature branch build and wants to know if it was already there or introduced by the branch.
---

# Bug Origin Checker

## Context

- User is a **manual QA tester** on the **EXAMPLE-PROJ** team
- Tests feature branch builds on physical iPhones
- PRs are linked in JIRA story comments
- User has access to RC/main builds for comparison
- Explain everything in **plain, simple language**

## Trigger Phrases

Activate when the user says things like:
- "Is this bug from the branch or was it already there?"
- "Did this branch introduce this bug?"
- "I found a bug while testing [story] — is it pre-existing?"
- "Is this a regression from the feature branch?"
- "Was this bug already in main?"
- "Is this new or existing?"

## Step 1: Gather Info

Ask for two things (if not already provided):

1. **The story being tested** — JIRA key (e.g., EXAMPLE-PROJ-456)
2. **The bug found** — which screen/area, what happens

Example prompt:
> What story were you testing, and what's the bug you found?

## Step 2: Find the PR

Fetch the JIRA story to locate the PR link:

```
CallMcpTool:
  server: user-atlassian-mcp-server
  toolName: jira_get_issue
  arguments:
    issue_key: <story key>
    fields: "*all"
    comment_limit: 50
```

Look for a GitHub PR link in:
- Issue comments
- Description
- Remote links / linked issues

Extract the PR URL (e.g., `https://github.com/your-org/your-mobile-app/pull/1234`).

### If no PR found

Tell the user:
> I couldn't find a linked PR for this story. Without seeing the code changes, I can't determine if the bug is pre-existing.
>
> You can check by installing the latest RC or main build and seeing if the bug happens there too. If it does, it's pre-existing.

Stop here — do not guess.

## Step 3: Analyze the PR Diff

Use the GitHub CLI to get the list of changed files:

```bash
gh pr diff <PR_NUMBER> --repo <REPO> --name-only
```

This returns just the file paths that were changed (no code content needed for the initial check).

If more detail is needed, get the full diff:

```bash
gh pr diff <PR_NUMBER> --repo <REPO>
```

### If gh CLI fails with auth error

Follow the github-auth-recovery skill to resolve, then retry.

## Step 4: Map Files to App Areas

Translate file paths into plain-language app areas the user understands.

Common patterns in the iOS codebase:

| File path contains | App area |
|-------------------|----------|
| `DeepLink` | Deep links / URL handling |
| `Cart` | Cart / bag |
| `Checkout` | Checkout / payment |
| `Home`, `Feed` | Home screen / feed |
| `PDP`, `Product` | Product detail page |
| `Search` | Search |
| `Profile`, `Account` | Profile / account |
| `Favorites`, `Wishlist` | Favorites / saved items |
| `Auth`, `Login`, `Sign` | Login / authentication |
| `Navigation`, `Router`, `Tab` | Navigation / app routing |
| `Network`, `API`, `Service` | Networking / API calls (shared) |
| `Core`, `Common`, `Shared`, `Utils` | Shared utilities (affects many areas) |
| `Launch`, `AppDelegate`, `SceneDelegate` | App startup |
| `Notification`, `Push` | Push notifications |
| `Settings` | Settings |
| `Order` | Orders / order history |
| `Inbox`, `Message` | Inbox / messages |
| `Onboarding` | Onboarding flow |
| `Store`, `Location` | Store locator |

If a file path doesn't match known patterns, use the directory name and file name to infer the area. When unsure, list the raw file paths for the user.

## Step 5: Compare and Give Verdict

Compare the **bug area** (from the user's description) against the **changed areas** (from the PR).

### Verdict A: Very Likely Pre-existing

The branch did NOT change any files related to the bug area.

```
I checked PR #1234 for EXAMPLE-PROJ-456. Here's what the branch changed:

| Area Changed | Files Modified |
|-------------|---------------|
| Checkout / Payment | 4 files |
| Cart | 2 files |

Your bug is on the **profile screen**. The branch **did not change any
profile-related code**.

**Verdict: Very likely pre-existing.**
This bug was probably already there before this branch.

**Recommended next steps:**
1. Check the latest RC build to confirm it happens there too
2. File it as a **separate bug** (not related to EXAMPLE-PROJ-456)

Want me to check for duplicates and file a bug?
```

### Verdict B: Possibly Introduced

The branch DID change files in or near the bug area.

```
I checked PR #1234 for EXAMPLE-PROJ-456. Here's what the branch changed:

| Area Changed | Files Modified |
|-------------|---------------|
| Profile / Account | 3 files |
| Networking | 1 file |

Your bug is on the **profile screen**. The branch **changed 3 files in the
profile area**.

**Verdict: This bug might be introduced by this branch.**
The code changes touch the same area where you found the bug.

**Recommended next steps:**
1. Check the RC build — if the bug does NOT happen there, the branch likely caused it
2. Add a comment on EXAMPLE-PROJ-456 describing the bug
3. Flag it to the developer on the story

Want me to add a comment on the JIRA story?
```

### Verdict C: Inconclusive (Shared Code Changed)

The branch changed shared/common code that could affect many areas.

```
I checked PR #1234 for EXAMPLE-PROJ-456. Here's what the branch changed:

| Area Changed | Files Modified |
|-------------|---------------|
| Checkout | 3 files |
| Networking / API (shared) | 2 files |
| Navigation (shared) | 1 file |

Your bug is on the **profile screen**. The branch didn't directly change
profile code, BUT it changed **shared networking and navigation code** that
the profile screen also uses.

**Verdict: Inconclusive — could go either way.**

**Recommended next step:**
Check the latest RC build. If the bug happens on RC too → pre-existing.
If it only happens on this branch → the shared code change likely caused it.

Want me to help after you check?
```

## Step 6: Chain to Next Action

Based on the verdict, offer the appropriate next step:

| Verdict | Offer |
|---------|-------|
| Pre-existing | Run **duplicate bug checker** → file as separate bug |
| Possibly introduced | Add a comment on the story or file a linked bug |
| Inconclusive | Wait for user to check RC build, then reassess |

Carry forward all context so the user doesn't repeat themselves.

## Important Rules

- **Never guess without PR data** — if there's no PR, say so and suggest testing on RC
- **Always show what changed** — give the user a table of changed areas, not just the verdict
- **Plain language only** — translate file paths to app areas, never show raw code paths unless necessary
- **Connect the dots** — after the verdict, link to duplicate-bug-checker or bug filing
- **RC build is the ultimate proof** — always mention it as the definitive way to confirm, especially for inconclusive cases
- **Don't analyze code logic** — focus on *what areas* were changed, not *how* the code works. Keep it accessible for a non-technical user.
