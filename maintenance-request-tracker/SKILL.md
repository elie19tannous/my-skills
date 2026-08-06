---
name: maintenance-request-tracker
description: >-
  Logs an incoming maintenance request (forwarded email, ticket text, or
  freeform message) into a maintenance log — local Excel, cloud spreadsheet, or
  chat output. Extracts unit, sender, condition, and urgency tier; appends a
  row; drafts an acknowledgment reply. On first run, walks the user through a
  short setup interview (storage location, property name, optional
  email/scheduled invocation), then offers a customized version of the skill
  with all settings baked in so future runs are silent. Triggers on 'log this
  maintenance request', 'track this WO', 'add this to the maintenance log', 'new
  tenant complaint just came in', or any forwarded maintenance email needing
  intake and tracking.
license: Apache-2.0
author: MPL
setup_complete: false
storage_type: ''
storage_location: ''
property_name: ''
input_source: ''
inbox_hints: ''
schedule: ''
metadata:
  mpl_catalog_url: >-
    https://skills.metaproplabs.com/leasing-operations/property-operations-maintenance/maintenance-request-tracker
  mpl_version: 0.3.0
---

# Maintenance Request Tracker

Forward a maintenance email or paste a tenant complaint and get a tracked row in your maintenance log, an urgency tier (EMERGENCY through NON-URGENT, with HABITABILITY as a distinct legal-risk tier), and a draft acknowledgment reply — in one pass.

On the very first run, the skill runs a short setup interview to learn where you want the log kept and a few other preferences, then offers you a customized version of itself with everything baked in. Install that customized version once and every run after is silent.

## When to Activate

- "Log this maintenance request"
- "Track this WO"
- "Add this to the maintenance log"
- "New tenant complaint just came in — record it"
- A user forwards a maintenance email and asks for it to be filed
- A user pastes a tenant message describing a unit issue

Do NOT trigger for: ranking an existing backlog of open work orders; reviewing items past their target response windows; drafting a formal habitability response or legal letter.

## Input Schema

| Field | Required | Default if Missing |
|---|:---:|---|
| `request_text` | Yes | — Pasted email body, ticket text, or freeform description of the issue. |
| `received_at` | No | Current timestamp — Used as the row's date if the source has no header. |
| `sender` | No | Inferred from the email headers if pasted; otherwise asked. |
| `unit` | No | Extracted from the body if present; otherwise left blank with a flag. |

## Process

### Step 0: First-run setup gate

Read `setup_complete` from this file's frontmatter.

- **If `setup_complete: true`** → skip this step entirely. The skill is configured. Proceed to Step 1.
- **If `setup_complete: false` (or absent)** → read `BOOTSTRAP.md` from this skill's directory and follow its interview script in full. BOOTSTRAP.md owns the welcome experience, configuration capture, and customized-SKILL.md regeneration.

If the user pasted a maintenance request along with the invocation while setup is incomplete, **note its presence and hold it** — don't process it yet. After the interview completes (or after the user picks the "Quick test" path in BOOTSTRAP.md), ask the user whether to log the held request now or wait until they install the customized version.

After this step, all subsequent steps assume `setup_complete: true` and read config from frontmatter.

### Step 1: Locate the tracker

Branch on `storage_type`:

- **`local-file`** → use the absolute path in `storage_location`. If the file exists, proceed to Step 2. If missing, create it (Step 2 covers the schema). If the path itself is unreachable (permissions, missing parent directory), surface the error and ask the user for an alternative for this session.
- **`cloud-link`** → no local file write. The row produced in Step 5 will be output for the user to paste into the cloud spreadsheet at `storage_location`. Skip Step 2.
- **`paste-each-time`** → no file write at all. Skip to Step 3.

### Step 2: Verify or create the file (only when storage_type is local-file)

If the file exists, open it with openpyxl (or equivalent) and read the header row. Match incoming fields to the existing column order — the user may have customized the schema, so do not assume defaults.

If the file does not exist, create it with a worksheet named `Requests` and this default header row:

| Date Received | Sender | Unit | Description | Urgency | Status | Suggested Action | Notes |

Tell the user: *"Created a new tracker at `<path>` with default columns. Edit the header row anytime — the skill reads it on each run."*

### Step 3: Extract fields from the request text

Parse `request_text` and pull:

- **Date Received**: from email header `Date:` or use the current timestamp.
- **Sender**: from `From:` header or signature line; ask if not derivable.
- **Unit**: search for patterns like "Unit 3B", "Apt 204", "Suite 410". Leave blank and flag if absent.
- **Description**: a one- to two-sentence summary of the condition. Strip pleasantries.
- **Urgency**: classify into one of four tiers (see Step 4).
- **Status**: `New` for every freshly logged row.
- **Suggested Action**: one short line — e.g., "Dispatch HVAC vendor today", "Schedule routine repair within 7 days".
- **Notes**: anything notable that doesn't fit elsewhere (repeat issue, after-hours, photo attached).

### Step 4: Classify urgency

Apply tiers in this priority order. EMERGENCY criteria win — never downgrade.

- **EMERGENCY** — life-safety or active damage requiring same-day dispatch. Active electrical sparks, gas smell, active water intrusion, lock-out, CO alarm, elevator entrapment, structural failure.
- **HABITABILITY** — breach of warranty of habitability, residential. No heat in heating season, no hot water, sewage backup, severe verified pest infestation, visible mold, structural hazard, elevator outage in a multi-story residential building.
- **STANDARD** — comfort or function impaired but not unsafe. Appliance failure, minor plumbing or electrical, broken non-safety window, lock issue with access still possible.
- **NON-URGENT** — cosmetic, preventive, or scheduling. Paint, carpet, landscaping, scheduled filter changes.

If the description is too vague to classify (e.g., "something is wrong with the bathroom"), default to STANDARD and add a note: *"Description ambiguous — inspector should reclassify on site."*

### Step 5: Persist the row

Branch on `storage_type`:

- **`local-file`** → append one row to the worksheet matched to the existing header order. Save the file. If the file is locked (someone has it open in Excel), tell the user: *"The tracker is open in Excel. Close it and re-run, or paste the row below into it manually:"* and output the row as a tab-separated line.
- **`cloud-link`** → output the row as a markdown table the user can copy into the cloud spreadsheet at `storage_location`. Lead with: *"Copy the row below into your cloud sheet at `<storage_location>`:"*.
- **`paste-each-time`** → output the row as a markdown table inline in the response. No persistence.

### Step 6: Draft acknowledgment

Generate a short reply the user can send back to the tenant. Keep it under 80 words. Confirm receipt, restate the issue in one line, give a realistic response window based on urgency tier (same day for EMERGENCY, 24 hours for HABITABILITY, 3 business days for STANDARD, 1–2 weeks for NON-URGENT), and sign with `property_name` if set, otherwise sign with "Property Management".

Output the draft as a quoted block in the response. Do not auto-send — leave that to the user or a follow-up integration.

### Step 7: Surface the result

Return:

1. **Urgency banner** — only if EMERGENCY or HABITABILITY. One line, prominent. Example: *"⚠️ HABITABILITY — no heat reported. State law may require a response within hours."*
2. **Logged confirmation** — adapts to `storage_type`:
   - local-file: *"Logged to `<storage_location>` — Unit 3B · No heat · HABITABILITY · 2026-05-07 09:14"*
   - cloud-link: *"Row generated for `<storage_location>` — paste it in when you're at your sheet."*
   - paste-each-time: *"Today's log entry — Unit 3B · No heat · HABITABILITY · 2026-05-07 09:14"*
3. **The row itself** (markdown table) — only when storage_type is `cloud-link` or `paste-each-time`; for `local-file`, the row was already written and listing it here is redundant.
4. **Acknowledgment draft** — quoted block, ready to send.

## Output Format

A short markdown response composed from Step 7's pieces.

### 1. Urgency banner (only if EMERGENCY or HABITABILITY)

One line, prominent. Example: *"⚠️ HABITABILITY — no heat reported."*

### 2. Logged confirmation

One line, adapts to storage_type as above.

### 3. Row to paste (only if storage_type is cloud-link or paste-each-time)

A markdown table with the row.

### 4. Acknowledgment draft

Quoted block, ready to send.

## Red Flags & Failure Modes

1. **Tracker file missing at the configured path.** Do not silently recreate — surface the problem and offer to create a fresh file at the configured location, use a different path for this session, or skip persistence and output the row in chat.
2. **Excel file locked.** Output the row as tab-separated text the user can paste manually rather than crashing.
3. **Schema drift.** Always read the existing header row before mapping fields. The customer's columns are the source of truth, not the defaults.
4. **Vague descriptions.** Default to STANDARD and flag for inspection rather than guessing into HABITABILITY or EMERGENCY. The aging reviewer will surface it if it sits.
5. **Repeat issue.** If the description matches an open row in the same unit, append a note ("possible duplicate of row N") rather than silently double-logging. v1 uses simple text matching; v2 can do fuzzier dedupe.
6. **User declines the regenerate offer in BOOTSTRAP.md.** Each subsequent run will re-trigger the welcome interview until the user installs a customized version. The skill never silently writes config back to its own SKILL.md — the regenerate offer is the only persistence mechanism.
7. **Email body has no clear sender or unit.** Log the row with blanks and flag in Notes. Don't refuse intake — partial information is still better than a missed request.
8. **Multiple requests in one paste.** If the input contains 2+ distinct issues, ask the user whether to log them as separate rows or one combined row before writing. In unattended mode (`input_source: inbox` or `schedule` is anything other than `on-demand`), default to logging all items as separate rows and flagging the batch in Notes for human review rather than blocking on a user prompt.

## Customization Points

These are the knobs the skill exposes through frontmatter. The first-run interview in BOOTSTRAP.md captures all of them; you can also edit the customized SKILL.md directly to change values later.

- **`setup_complete`** — boolean gate. `true` skips the welcome interview; `false` triggers it on next run.
- **`storage_type`** — `local-file` | `cloud-link` | `paste-each-time`. Determines where Step 5 writes (or doesn't).
- **`storage_location`** — absolute path (for local-file), share URL or descriptive location (for cloud-link), empty (for paste-each-time).
- **`property_name`** — used to sign acknowledgment replies. Empty = generic "Property Management" sign-off.
- **`input_source`** — `manual` (user pastes requests) or `inbox` (skill reads from a connected email account using the available MCP). Inbox-watching captures filter hints in `inbox_hints` and uses them at runtime to decide which messages count.
- **`inbox_hints`** — free-text filter hints used when `input_source: inbox`. Examples: "alias maintenance@oakwood.com", "subject contains repair / broken / leak", "label maintenance/incoming". Skill interprets these at runtime.
- **`schedule`** — `on-demand` (only when triggered) or a natural-language cadence (`"every hour"`, `"8am daily"`). When set to a cadence, the skill expects to be invoked by an external scheduler (Claude.ai's scheduled task or a cron entry) and runs in unattended mode.
- **Header row in the .xlsx** — the customer's columns win; edit the file, not the skill.
- **Urgency tiers (Step 4)** — add categories like `gym_equipment` or vendor-routing tags by inserting bullets in this section.
- **Suggested Action language (Step 3)** — adjust per property type or vendor list.
- **Acknowledgment tone (Step 6)** — rewrite the prompt to match brand voice.

## Example

**Input (forwarded tenant email):**

> From: Maria Torres <mtorres@example.com>
> Date: Mon, 07 May 2026 07:42:00 -0500
> Subject: No heat — Unit 3B
>
> Hi, the heat has been out since Friday night. It was 58°F in my apartment this morning. Please send someone as soon as possible.

**Extracted row logged to tracker:**

| Date Received | Sender | Unit | Description | Urgency | Status | Suggested Action | Notes |
|---|---|---|---|---|---|---|---|
| 2026-05-07 07:42 | Maria Torres | 3B | No heat since Friday; interior temp 58°F | HABITABILITY | New | Contact HVAC vendor immediately; confirm response window per state law | Heating season — warranty of habitability applies |

**Draft acknowledgment:**

> Hi Maria,
>
> Thank you for letting us know. We've received your report of no heat in Unit 3B and have classified it as a habitability issue requiring urgent attention. We are contacting our HVAC vendor now and will have someone out to your unit within 24 hours. We'll follow up with a confirmed appointment time shortly.
>
> — Oakwood Apartments Management

---

## Chain Notes

This skill is a workflow entry point. It runs standalone on user-pasted input and is the natural front door for incoming maintenance requests.

**Output can feed into (downstream):**
- `work-order-triage-prioritizer` — when the tracker has accumulated a backlog and the user wants it ranked with state habitability deadlines.
- `work-order-aging-reviewer` — scans the tracker for items past their target windows.
- `habitability-response-drafter` — when a logged HABITABILITY row needs a formal legal letter, not just an acknowledgment.

**Session note:** Typically runs unattended on inbox events once the customized version is installed and `input_source: inbox` plus `schedule` are set. The first interactive run conducts the setup interview from BOOTSTRAP.md and offers a customized SKILL.md to install; every run after that reads `setup_complete: true` and goes straight to logging.
