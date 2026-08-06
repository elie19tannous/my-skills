---
name: sprint-confluence-doc
description: Generate sprint documentation tables on Confluence pages by pulling JIRA sprint data and formatting with proper JIRA macros. Use when the user mentions sprint doc, sprint documentation, Confluence sprint page, sprint table, or wants to document a sprint on Confluence.
---

# Sprint Confluence Documentation

Generate sprint documentation on Confluence by pulling JIRA sprint data, grouping issues by Epic Link, and rendering with Confluence storage format.

## MCP Tools

All tools are on `user-atlassian-mcp-server`. Read tool schemas before calling.

| Tool | Purpose |
|------|---------|
| `jira_get_agile_boards` | Find board by `project_key` |
| `jira_get_sprints_from_board` | List sprints by state |
| `jira_get_sprint_issues` | Pull sprint issues with epic link field |
| `jira_get_issue` | Fetch epic name from epic key |
| `jira_search` | Search with JQL + `expand: changelog` for Sprint field changes |
| `jira_jira_get_issue_dates` | Get status transition history for carryover status at sprint close |
| `confluence_get_page` | Read target page content + version |
| `confluence_update_page` | Push updated content |

### JIRA Server Limitations

- `jira_batch_get_changelogs` — **Cloud only**, does not work on [Company] JIRA Server
- `sprint was` JQL — **not supported** on Server; cannot query issues removed from a sprint via JQL
- Use `jira_search` with `expand: "changelog"` instead to get Sprint field changelogs for issues currently in the sprint

## Project Defaults

| Setting | Value |
|---------|-------|
| JIRA project | `EXAMPLE-PROJ` |
| Board ID | `{BOARD_ID}` (MP and AppCore Current Sprint) |
| Confluence space | `QUALITY` |
| Production page | `{PROD_PAGE_ID}` |
| Test page | `{TEST_PAGE_ID}` |

## JIRA Custom Fields

| Field | ID | Location |
|-------|----|----------|
| Epic Link | `customfield_XXXXX` | On any issue; returns the epic's issue key |
| Epic Name | `customfield_YYYYY` | On the epic issue itself; returns display name |

## Workflow

1. **Ask for sprint identifier** — ask the user: "What sprint do you want to generate?" The user will reply with the sprint name in `FY__Q_._` format (e.g. `FY26Q3.2`). If the response doesn't match the expected `FY##Q#.#` pattern, ask the user to provide the correct format before proceeding.
2. **Match sprint in JIRA** — use `jira_get_sprints_from_board` on board `{BOARD_ID}` and match the user-provided identifier to a sprint name. Use the matched sprint's ID, start date, and end date.
3. **Pull all issues (paginated)** — call `jira_get_sprint_issues` with fields `summary,status,issuetype,description,customfield_XXXXX`, limit 50. If the response returns 50 issues, call again with `startAt=50`, then `startAt=100`, and so on until fewer than 50 issues are returned. Combine all results.
4. **Fetch epic names** — for each unique `customfield_XXXXX` value, call `jira_get_issue` to get `customfield_YYYYY`
5. **Group by epic** — map issues to their epic name; null epic link → "Bug Fixes / Misc"
6. **Split by platform** — determine platform from summary prefix first (`iOS`/`IOS` → iOS column, `Android` → Android column). If the summary has no recognizable platform prefix, inspect the issue's description or other fields to determine platform.
7. **Determine footer row data** — populate the three footer rows using changelog and resolution date analysis (see **Footer Row Data** section below)
8. **Determine carryover issues** — identify issues not completed at sprint close and their status at that time (see **Carryover Data** section below)
9. **Build storage format HTML** — construct all 4 tables per the template in the **Storage Format Template** section below
10. **Validate output** — before confirming with the user, verify: every JIRA key from the sprint appears exactly once in the tables, every epic group has at least one issue, and the total issue count in the HTML matches the total fetched from JIRA
11. **Confirm with user** — show summary of features and issue counts before pushing
12. **Update page** — `confluence_update_page` with `content_format: "storage"`
13. **Report** — share the Confluence page URL

## Format Rules

1. **Content format = `storage`** — never markdown, never wiki
2. **All `<th>` headers centered** — every `<th>` gets `style="text-align: center;"`
3. **Date format = `DD/Mon/YY`** — e.g. `04/Feb/26`
4. **Sprint header** — always normalize to `Mobile App - Sprint {SPRINT_NAME} - {START_DATE} to {END_DATE}` where `{SPRINT_NAME}` is the user-provided identifier (e.g. `FY26Q3.2`) and dates are in `DD/Mon/YY` format derived from the JIRA sprint's start/end dates
5. **Sprint Goals label** — only `Sprint Goals:` is bold, not the goals text
6. **Pipe not slash** — `Story|Bugs completed outside of this sprint`

## JIRA Issue Rules

7. **Use Confluence JIRA macro** — never plain URLs or keys:

```xml
<ac:structured-macro ac:name="jira" ac:schema-version="1">
  <ac:parameter ac:name="server">Company Jira</ac:parameter>
  <ac:parameter ac:name="serverId">{YOUR_JIRA_SERVER_ID}</ac:parameter>
  <ac:parameter ac:name="key">EXAMPLE-PROJ-XXXX</ac:parameter>
</ac:structured-macro>
```

8. **Multiple issues in one cell** — separated by `<br/>`, not spaces
9. **Feature names from Epic Link** — `customfield_XXXXX` → epic key → `customfield_YYYYY` for name. Never guess from summaries.
10. **No epic link** → group under "Bug Fixes / Misc"
11. **Platform from summary prefix, then fallback** — check summary for `iOS`/`IOS` → iOS column, `Android` → Android column. If the summary has no platform prefix, inspect the issue's description or other available fields (e.g. labels, components) to determine platform. If still ambiguous, flag the issue for the user during confirmation.

## Table Structure Rules

12. **Footer rows = 7 individual cells** — `Issue added to sprint after start time`, `Story|Bugs completed outside of this sprint`, `Issues Removed from this sprint` each get text in first `<td>`, then empty `<td></td>` for columns 2–3, JIRA macros in the iOS column (4th `<td>`) and Android column (5th `<td>`), then empty `<td></td>` for Geo and Comments. Never use `colspan`. Split footer issues by platform just like feature rows.
13. **First data row only** gets "Mobile App" and "[Company]" in Squad Name / App columns. Subsequent rows leave those empty.
14. **Carryover header centered** — same `<th style="text-align: center;">` as all headers.
15. **Carryover grouped by status** — carryover table uses multiple `<tr>` rows, each grouping issues by their status at sprint close. Format: `With QA at end of sprint` followed by JIRA macros, then `Card with DEV at end of sprint` followed by JIRA macros, etc. Each status group gets its own `<tr><td>` row.

## Page Structure

16. **4 tables in order:**
    - Table 1: High level scope + Sprint Goals
    - Table 2: Main sprint table (7 columns) + footer rows
    - Table 3: Carryover (1 column — centered header + status-grouped rows)
    - Table 4: Release updates (3 columns — header + RC rows)

17. **Test Artifacts underline** — `<h1><u>Test Artifacts:</u></h1>` gets the underline, **not** "High level scope". The high level scope header is just `<h3>High level scope</h3>` (no `<u>`).

## Guardrails

18. **Always confirm** before pushing to Confluence
19. **Default to test page** (`{TEST_PAGE_ID}`) unless user explicitly says production
20. **Never overwrite** existing sprint sections — append new ones
21. **Sync Confluence after rule changes** — when a rule or template is updated, proactively offer to update the Confluence page to match the new rules
22. **Paginate all JIRA queries** — never assume a single API call returns all issues. Always paginate until fewer results than the limit are returned.
23. **Validate before pushing** — before confirming with the user, run the validation checks described in workflow step 8. If any check fails, fix the issue and re-validate before proceeding.
24. **Rules take precedence** — if any rule in this file contradicts the storage format template below, the rule takes precedence over the template.
25. **Never guess RC versions** — release candidate version numbers are not available in JIRA data. Always leave RC rows with placeholder text for the user to fill in manually.

---

## Footer Row Data

How to populate the three footer rows in Table 2 using JIRA API data.

### Issues added after sprint start

1. Call `jira_search` with JQL `sprint = {SPRINT_ID}`, fields `summary,status,created,resolutiondate`, limit 50, and `expand: "changelog"`
2. For each issue, find the changelog entry where `field = "Sprint"` and `to_id` contains the sprint ID (e.g. `{SPRINT_ID}`). This is when the issue was added.
3. Compare that changelog `created` timestamp against the sprint `start_date`
4. If the changelog date is **after** the sprint start date → issue was added after start
5. Split these issues by platform (iOS/Android) and place JIRA macros in the appropriate columns

### Story|Bugs completed outside of this sprint

1. From the same search results, check each issue's `resolutiondate`
2. If `resolutiondate` is **before** sprint `start_date` → completed before the sprint
3. If `resolutiondate` is **after** sprint `end_date` → completed after the sprint
4. Both cases = "completed outside of this sprint"
5. Split by platform and place in the appropriate columns

### Issues Removed from this sprint

- **Cannot be determined via API** on JIRA Server — the `sprint was` JQL history search is not supported
- Leave this row empty unless the user provides the data manually from the Sprint Retrospective report in the JIRA UI

---

## Carryover Data

How to determine "Stories & Bugs Not Completed" and their status at sprint close.

### Identifying carryover issues

**IMPORTANT: `resolutiondate` alone is NOT sufficient.** Many issues on [Company] JIRA Server use "Deployed" status without setting a formal JIRA resolution. These issues show `resolution = Unresolved` with no `resolutiondate`, even though they are functionally complete.

Use this two-step approach:

1. **Step 1 — Resolution date check:** Issues with `resolutiondate` **after** the sprint `end_date` → definitely carryover
2. **Step 2 — Unresolved status check:** Search for issues with `resolution = Unresolved` using JQL: `sprint = {SPRINT_ID} AND resolution = Unresolved`. For each of these, call `jira_jira_get_issue_dates` with `include_status_changes: true` to determine their status at sprint close:
   - If the issue was in a **Done-category status** at sprint close (e.g. `Done`, `Deployed`, `Done Deploy Not Needed`, `Planned for Next Release`) → **completed** (not carryover)
   - If the issue was in a **non-Done status** at sprint close (e.g. `QA`, `Dev`, `Pull Request`, `Blocked`, `In Definition`) → **carryover**
3. Combine results from both steps = all carryover issues

**Done-category statuses** (treat as completed at sprint close): `Done`, `Deployed`, `Done Deploy Not Needed`, `Planned for Next Release`

### Determining status at sprint close

1. For each carryover issue, call `jira_jira_get_issue_dates` with `include_status_changes: true` (reuse data from Step 2 if already fetched)
2. Look at the `status_changes` array and find which status the issue was in at the sprint `end_date`:
   - Find the status entry where `entered_at` is before sprint end AND (`exited_at` is after sprint end OR `exited_at` is null)
3. Group carryover issues by their status at sprint close

### Carryover status labels

Use these labels based on the status found:

| Status at sprint close | Carryover label |
|----------------------|-----------------|
| `QA` | `With QA at end of sprint` |
| `Dev` / `Dev Ready` | `Card with DEV at end of sprint` |
| `Pull Request` | `Card with PR at end of sprint` |
| `Blocked` | `Blocked at end of sprint` |
| `In Definition` | `Card in Definition at end of sprint` |

---

## Storage Format Template

This is the exact Confluence storage format HTML for a sprint section. Replace placeholders in `{BRACES}` with actual values.

### Placeholders

| Placeholder | Source |
|-------------|--------|
| `{SPRINT_NAME}` | User-provided sprint identifier, e.g. `FY26Q3.5` |
| `{START_DATE}` | Format `DD/Mon/YY`, e.g. `04/Feb/26` |
| `{END_DATE}` | Format `DD/Mon/YY`, e.g. `25/Feb/26` |
| `{SPRINT_GOALS}` | From sprint object `goal` field |
| `{FEATURE_ROWS}` | Generated rows grouped by epic — see below |
| `{ADDED_AFTER_START_IOS}` | JIRA macros for iOS issues added after sprint start |
| `{ADDED_AFTER_START_ANDROID}` | JIRA macros for Android issues added after sprint start |
| `{COMPLETED_OUTSIDE_IOS}` | JIRA macros for iOS issues completed outside sprint |
| `{COMPLETED_OUTSIDE_ANDROID}` | JIRA macros for Android issues completed outside sprint |
| `{CARRYOVER_ROWS}` | Multiple `<tr>` rows grouped by status at sprint close |
| `{NEXT_SPRINT}` | Next sprint name, e.g. `FY26Q3.6` |
| `{RC_ROWS}` | Release candidate rows — left blank for user to fill in |

### JIRA Macro

Each issue reference uses this macro (replace `{KEY}`):

```xml
<ac:structured-macro ac:name="jira" ac:schema-version="1"><ac:parameter ac:name="server">Company Jira</ac:parameter><ac:parameter ac:name="serverId">{YOUR_JIRA_SERVER_ID}</ac:parameter><ac:parameter ac:name="key">{KEY}</ac:parameter></ac:structured-macro>
```

Multiple macros in one cell: separate with `<br/>`.

### Full Template

```xml
<h1>Mobile App - Sprint {SPRINT_NAME} - {START_DATE} to {END_DATE}</h1>

<h1><u>Test Artifacts:</u></h1>

<!-- TABLE 1: High Level Scope -->
<table><tbody>
  <tr>
    <th style="text-align: center;"><h3>High level scope</h3></th>
  </tr>
  <tr>
    <td><strong>Sprint Goals:</strong> {SPRINT_GOALS}</td>
  </tr>
</tbody></table>

<!-- TABLE 2: Main Sprint Table -->
<table><tbody>
  <tr>
    <th style="text-align: center;">Squad Name</th>
    <th style="text-align: center;">App</th>
    <th style="text-align: center;">Features assigned</th>
    <th style="text-align: center;">iOS</th>
    <th style="text-align: center;">Android</th>
    <th style="text-align: center;">Geo</th>
    <th style="text-align: center;">Comments</th>
  </tr>

  {FEATURE_ROWS}

  <!-- Empty spacer row -->
  <tr>
    <td></td><td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>

  <!-- Footer rows — always 7 individual cells, never colspan -->
  <!-- Issues split by platform in iOS (col 4) and Android (col 5) columns -->
  <tr>
    <td>Issue added to sprint after start time</td>
    <td></td><td></td><td>{ADDED_AFTER_START_IOS}</td><td>{ADDED_AFTER_START_ANDROID}</td><td></td><td></td>
  </tr>
  <tr>
    <td>Story|Bugs completed outside of this sprint</td>
    <td></td><td></td><td>{COMPLETED_OUTSIDE_IOS}</td><td>{COMPLETED_OUTSIDE_ANDROID}</td><td></td><td></td>
  </tr>
  <tr>
    <td>Issues Removed from this sprint</td>
    <td></td><td></td><td></td><td></td><td></td><td></td>
  </tr>
</tbody></table>

<!-- TABLE 3: Carryover — one row per status group -->
<table><tbody>
  <tr>
    <th style="text-align: center;">Stories &amp; Bugs Not Completed and carried over to - Sprint {NEXT_SPRINT}</th>
  </tr>
  {CARRYOVER_ROWS}
</tbody></table>

<!-- TABLE 4: Release Updates -->
<table><tbody>
  <tr>
    <th style="text-align: center;"><strong>Release updates in Sprint {SPRINT_NAME}</strong></th>
    <th style="text-align: center;">PRT Defects</th>
    <th style="text-align: center;">Release Scope tickets</th>
  </tr>
  {RC_ROWS}
</tbody></table>
```

### Feature Row Format

The first feature row includes Squad Name and App. All subsequent rows leave those empty.

**First row:**
```xml
<tr>
  <td>Mobile App</td>
  <td>[Company]</td>
  <td>{EPIC_NAME}</td>
  <td>{IOS_JIRA_MACROS separated by <br/>}</td>
  <td>{ANDROID_JIRA_MACROS separated by <br/>}</td>
  <td></td>
  <td></td>
</tr>
```

**Subsequent rows:**
```xml
<tr>
  <td></td>
  <td></td>
  <td>{EPIC_NAME}</td>
  <td>{IOS_JIRA_MACROS separated by <br/>}</td>
  <td>{ANDROID_JIRA_MACROS separated by <br/>}</td>
  <td></td>
  <td></td>
</tr>
```

### Carryover Row Format

Each status group gets its own row. The label text and JIRA macros go in the same `<td>`, separated by `<br/>`.

```xml
<tr>
  <td>With QA at end of sprint<br/>{JIRA_MACROS separated by <br/>}</td>
</tr>
<tr>
  <td>Card with DEV at end of sprint<br/>{JIRA_MACROS separated by <br/>}</td>
</tr>
```

### RC Row Format

RC version numbers are **not derived from JIRA** — leave them as placeholder text for the user to fill in manually. Do not guess or assume version numbers.

```xml
<tr>
  <td>Wednesday RC cut</td>
  <td></td>
  <td></td>
</tr>
```
