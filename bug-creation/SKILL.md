---
name: bug-creation
description: Create EXAMPLE-PROJ JIRA bugs in the user's exact format. Use when the user says create bug, file bug, log bug, report bug, raise bug, open bug, write bug, new bug, create issue, file issue, log issue, report issue, raise issue, create defect, file defect, log defect, raise a ticket, create a ticket, or any variation of wanting to create a bug or issue in JIRA.
---

# Bug Creation (EXAMPLE-PROJ)

Create bugs in JIRA using the user's established format. Always confirm the draft with the user before submitting.

## Summary Format

```
{Platform}| {Module}| {Bug title}
```

- **Platform**: `iOS` or `AOS`
- **Module**: Area of the app (e.g., `Profile`, `Cart`, `Checkout`, `Home`, `PDP`, `Search`, `Favorites`, `Inbox`, `Settings`)
- **Title**: Short description of the bug
- Example: `iOS| Profile| Bio field truncates copy after first line from the Edit Profile Page`

## Description Format (JIRA Wiki Markup)

Use this exact template — fill in values from what the user tells you:

```
Does this happen in PROD? *{Yes/No}*
Does this happen in {other_platform}? *{Yes/No}*
How reproducible? *{X out of 5}*
Limited to specific devices only? *{Yes/No}*
Limited to specific OS versions only? *{Yes/No}*
Locale/ Language Specific? *{Yes/No}*

*{build_label}* : {version} - {build_number}

{*}Steps{*}:
 # Step 1
 # Step 2
 # Step 3

*Expected:*
 * {What should happen}
 
*Actual:*
 * {What actually happens}



{*}Video{*}: [^{filename}]

{additional_notes}
```

### Field rules

- `{other_platform}`: If the bug is on iOS, ask "Does this happen in Android?" — if it's on AOS, ask "Does this happen in iOS?"
- `{build_label}`: Use `*prod version*` if tested on prod, or `*build version*` for test builds
- `{additional_notes}`: Include related tickets (e.g., "also observed in EXAMPLE-PROJ-12279"), older builds tested, or any extra context. Leave blank if none.
- Video/Screenshot line: Use `{*}Video{*}` or `{*}Screenshot{*}` depending on what the user attaches. Omit the line if no attachment.

## JIRA Fields

| Field | Value |
|-------|-------|
| Project | `EXAMPLE-PROJ` |
| Issue type | `Bug` |
| Priority | Always `TBD` (PO sets this) |
| Component | Based on the module/area (e.g., `Profile`, `Cart`) |

## Linking Related Tickets

If the user mentions a related ticket, link it using:

```
Tool: jira_create_issue_link
Args: {
  "link_type": "Relates",
  "inward_issue_key": "{new_bug_key}",
  "outward_issue_key": "{related_ticket_key}"
}
```

## Workflow

1. **Gather info**: From what the user tells you, extract: platform, module, bug title, repro steps, actual/expected, build version, and any related tickets. Ask for anything missing — keep questions short.
2. **Build the draft**: Show the user the full summary + description so they can review and change anything.
3. **Wait for approval**: Do NOT create until the user says go ahead.
4. **Create the bug**: Use `jira_create_issue` on `user-atlassian-mcp-server` with the fields above.
5. **Link related tickets**: If any were mentioned.
6. **Return the ticket key**: So the user can find it.
