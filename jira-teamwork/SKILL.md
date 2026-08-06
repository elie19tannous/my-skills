---
name: jira-teamwork
description: Manage JIRA issues, sprints, and boards using the Atlassian MCP server for QA testing workflows. Use when the user mentions JIRA, tickets, issues, sprints, backlog, board, standup, bugs, testing, QA, regression, defects, or wants to create, update, search, or track work items.
---

# JIRA Teamwork (QA Focus)

Interact with JIRA via the `user-atlassian-mcp-server` MCP server. The user is a **QA tester** -- prioritize testing workflows, bug management, and QA status tracking. Always read tool schemas from the MCP descriptor files before calling tools.

## Project Context

- Default project key: **EXAMPLE-PROJ**
- If the user references a different project, use that key instead.
- Never guess project keys -- ask if ambiguous.

## QA Workflows

### 1. My QA Queue

Find issues assigned to the user for testing:

```
Tool: jira_search
Args: { "jql": "assignee = currentUser() AND project = EXAMPLE-PROJ AND status != Done ORDER BY priority DESC, updated DESC", "limit": 25 }
```

Find issues ready for QA (adjust status name to match project workflow):

```
Tool: jira_search
Args: { "jql": "project = EXAMPLE-PROJ AND status in ('Ready for QA', 'Ready for Test', 'In QA', 'QA') ORDER BY priority DESC", "limit": 25 }
```

If the above JQL returns errors due to status names, search without status filter and inspect returned statuses to learn the project's actual workflow status names.

### 2. File a Bug Report

When the user describes a bug, create a well-structured defect. Always confirm details with the user before submitting.

```
Tool: jira_create_issue
Args: {
  "project_key": "EXAMPLE-PROJ",
  "summary": "[Brief, specific title]",
  "issue_type": "Bug",
  "description": "## Environment\n- Device: [e.g., iPhone 15 Pro, iOS 17.4]\n- App version: [e.g., 5.2.1 (build 1234)]\n- Network: [Wi-Fi / Cellular / Offline]\n\n## Steps to Reproduce\n1. Step one\n2. Step two\n3. Step three\n\n## Expected Result\n[What should happen]\n\n## Actual Result\n[What actually happens]\n\n## Severity / Impact\n[Who is affected and how badly]\n\n## Additional Notes\n- Frequency: [Always / Intermittent / Once]\n- Screenshots/videos: [attached or described]\n- Related tickets: [if any]",
  "additional_fields": {
    "priority": { "name": "High" },
    "labels": ["ios", "qa"]
  }
}
```

Prompt the user for any missing fields: device, OS version, app version, and repro steps at minimum.

### 3. Sprint Status (QA View)

To see the current sprint from a QA perspective:

1. **Find the board:**
   ```
   Tool: jira_get_agile_boards
   Args: { "project_key": "EXAMPLE-PROJ" }
   ```
2. **Get the active sprint** (use `board_id` from step 1):
   ```
   Tool: jira_get_sprints_from_board
   Args: { "board_id": "<id>", "state": "active" }
   ```
3. **Get sprint issues** (use `sprint_id` from step 2):
   ```
   Tool: jira_get_sprint_issues
   Args: { "sprint_id": "<id>", "limit": 50 }
   ```

When presenting, group issues into QA-relevant buckets:
- **Waiting for QA**: issues in a "ready for test/QA" status
- **Currently in QA**: issues being tested
- **QA Passed**: issues that passed testing
- **QA Failed / Reopened**: issues sent back to dev
- **Not yet ready**: still in development

### 4. Transition Issues (QA Pass/Fail)

To move an issue through QA:

1. Get available transitions:
   ```
   Tool: jira_get_transitions
   Args: { "issue_key": "EXAMPLE-PROJ-123" }
   ```
2. Transition with a QA comment:
   ```
   Tool: jira_transition_issue
   Args: {
     "issue_key": "EXAMPLE-PROJ-123",
     "transition_id": "<id>",
     "comment": "QA Passed - tested on iPhone 15 Pro, iOS 17.4, app v5.2.1"
   }
   ```

When failing QA, add a comment describing what failed:
```
Tool: jira_add_comment
Args: {
  "issue_key": "EXAMPLE-PROJ-123",
  "comment": "## QA Failed\n\n**Tested on:** iPhone 15 Pro, iOS 17.4\n**Build:** 5.2.1 (1234)\n\n### Issue found\n[Description of the failure]\n\n### Steps to reproduce\n1. ...\n2. ...\n\n### Expected vs Actual\n- Expected: ...\n- Actual: ..."
}
```

### 5. Search Issues

Use JQL via `jira_search`. QA-relevant patterns:

| Intent | JQL |
|--------|-----|
| Open bugs | `issuetype = Bug AND project = EXAMPLE-PROJ AND status != Done ORDER BY priority DESC` |
| Bugs I filed | `issuetype = Bug AND project = EXAMPLE-PROJ AND reporter = currentUser() ORDER BY created DESC` |
| Critical/blocker bugs | `issuetype = Bug AND priority in (Highest, High) AND project = EXAMPLE-PROJ AND status != Done` |
| Recently resolved (for regression) | `project = EXAMPLE-PROJ AND status changed to Done AFTER -7d ORDER BY updated DESC` |
| Reopened issues | `project = EXAMPLE-PROJ AND status changed to (Open, Reopened) AFTER -7d` |
| Issues by label | `labels = "ios" AND project = EXAMPLE-PROJ` |
| Unassigned bugs | `issuetype = Bug AND assignee is EMPTY AND project = EXAMPLE-PROJ AND status != Done` |
| Text search | `text ~ "search term" AND project = EXAMPLE-PROJ` |
| Epics | `issuetype = Epic AND project = EXAMPLE-PROJ` |
| Children of epic | `parent = EXAMPLE-PROJ-<id>` |

### 6. Get Issue Details

```
Tool: jira_get_issue
Args: { "issue_key": "EXAMPLE-PROJ-123", "comment_limit": 10 }
```

To see available status transitions: set `"expand": "transitions"`.

### 7. Update Issues

**Update fields:**
```
Tool: jira_update_issue
Args: {
  "issue_key": "EXAMPLE-PROJ-123",
  "fields": { "labels": ["ios", "regression"], "priority": { "name": "Highest" } }
}
```

**Add a comment:**
```
Tool: jira_add_comment
Args: { "issue_key": "EXAMPLE-PROJ-123", "comment": "Comment in Markdown" }
```

### 8. QA Standup Summary

When the user asks for a standup or daily summary:

1. **Tested yesterday** -- issues updated by the user recently:
   ```
   jql: "assignee = currentUser() AND project = EXAMPLE-PROJ AND updated >= -1d ORDER BY updated DESC"
   ```
2. **Testing today** -- issues currently in QA/test status:
   ```
   jql: "assignee = currentUser() AND project = EXAMPLE-PROJ AND status in ('In QA', 'In Progress', 'Ready for QA', 'Ready for Test') ORDER BY priority DESC"
   ```
3. **Bugs filed recently**:
   ```
   jql: "reporter = currentUser() AND issuetype = Bug AND project = EXAMPLE-PROJ AND created >= -1d"
   ```
4. Present as:
   - **Yesterday**: what was tested, any bugs filed
   - **Today**: what's next in the QA queue
   - **Blockers**: blocked items, environment issues, missing builds

### 9. Regression Check

When the user asks about regression or a new build:

1. Find recently resolved issues to retest:
   ```
   jql: "project = EXAMPLE-PROJ AND status changed to Done AFTER -14d AND issuetype = Bug ORDER BY priority DESC"
   ```
2. Find issues that were reopened:
   ```
   jql: "project = EXAMPLE-PROJ AND status changed FROM Done AFTER -14d"
   ```

## Presentation Guidelines

- Always show the **issue key** (e.g., EXAMPLE-PROJ-123) so the user can reference it.
- Show **summary**, **status**, **assignee**, and **priority** at minimum.
- For bugs, also show **reporter** and **created date**.
- Use tables for lists of issues.
- When showing a single issue, include the full description and recent comments.

## Error Handling

- If a tool returns an auth error, tell the user to check their Atlassian MCP server configuration.
- If a JQL query fails due to unknown status names, retry without the status filter, then inspect the returned issues to learn the project's actual status names.
- If a transition fails, re-fetch available transitions -- the issue may already be in the target status.
