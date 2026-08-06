# Maintenance Request Tracker — First-Run Setup

This file is loaded by `SKILL.md` on first run, when `setup_complete: false` in the frontmatter. The agent should follow the interview script below, capture the user's configuration, and produce a customized `SKILL.md` for the user to install over the generic one. After that install, `setup_complete: true` is set and this file is never read again.

## Tone & rules

- Warm, brief, oriented around the user's choice — never around the skill's internals.
- **Never** mention sandboxes, frontmatter, `/mnt/skills/`, "read-only", or any substrate-specific reasoning. The user does not need to know any of it.
- **Never** auto-detect runtime — ask once if it matters.
- **Never** write to the live SKILL.md with the Edit tool — output the customized version as a fenced code block and let the user install it.
- Don't loop. If the user changes an answer mid-flow, accept the correction and continue.

## Interview Script

### 1. Greet & branch on intent

Open with:

> 👋 Welcome to **Maintenance Request Tracker**. Looks like a fresh install — let's spend 30 seconds figuring out the right setup for you.
>
> First, the simplest question: are you trying this out, or wiring it up for real?
>
> **A) Quick test** — paste a maintenance request and I'll show you the output. No setup, no install, just see if it does what you need.
>
> **B) Set up for real** — answer a few questions, then I'll hand you a customized version to install. Every run after that is silent and goes straight to logging.

**If they pick A** → skip the rest of this script. Expect a maintenance request paste; run Steps 3–6 of SKILL.md (extract fields, classify urgency, draft acknowledgment); output everything in chat as a markdown table + quoted draft. No file write, no regenerate offer. End cleanly.

**If they pick B** → proceed to Q2.

### 2. Where will the log live?

> Where do you want to keep your maintenance log?
>
> 1. **Local Excel file** on this machine (Claude Code only — needs filesystem access).
> 2. **Cloud spreadsheet** (SharePoint / Google Drive / Dropbox / OneDrive). Works anywhere. I'll generate the row each time; you paste it into your sheet. Live cloud writes coming in a later version.
> 3. **Pasted in chat each time** — no persistence; output the row and you decide what to do with it.

If the user is clearly in a web/cloud environment with no filesystem access, gently note that option 1 needs Claude Code or another local agent and steer them toward 2 or 3.

### 3. Specifics — adapts to Q2

- **Local file** → *"Paste an absolute path to your .xlsx, or hit enter for the default `~/Documents/maintenance-log.xlsx`. I'll create it if it doesn't exist."*
- **Cloud spreadsheet** → *"Paste the share URL or describe where you keep it (e.g., 'SharePoint > Operations > maintenance-log.xlsx'). I'll reference it in the output so you know where to paste each row."*
- **Pasted in chat** → no location needed; skip.

### 4. Property name (optional)

> Property name? I'll use it to sign off on tenant acknowledgment replies. Type "skip" if you'd rather keep replies generic.

### 5. How should I receive maintenance requests?

> Two ways:
>
> 1. **Manual** — you paste them when one comes in. Simplest. Pick this if you want to start using the skill today.
> 2. **Watch your inbox** — I monitor a Gmail or Outlook inbox and process maintenance emails as they land.

If they pick **manual** → set `input_source: manual`, skip 5a and 5b, proceed to Q6.

If they pick **watch inbox** → set `input_source: inbox`, proceed to 5a.

#### 5a. Verify inbox access (only if "watch inbox")

Before asking *anything else* about the inbox, check whether you actually have email access. Probe the available MCP connectors in this session — Gmail MCP, Outlook MCP, Microsoft 365 MCP, etc.

- **If access is available:** confirm with the user. *"I can see your Gmail account `<address>` is connected. Want me to use that one?"* Make the call confidently. Don't enumerate "Zapier vs cron vs Make.com" — that's substrate-leak. The skill uses whatever connector is connected.
- **If no access is available:** tell the user clearly and offer a fallback. *"I don't have inbox access in this session. To enable it, you'll need to connect Gmail (or your email provider) in your Claude settings — it's a one-time auth flow. Want to set that up now and come back, or drop to manual for now?"* If they pick fallback, set `input_source: manual` and proceed to Q6.

#### 5b. Capture filter hints (only if "watch inbox" and access confirmed)

The hardest part of inbox-watching is deciding which messages count. Ask the user for hints in plain language:

> What do maintenance requests usually look like in your inbox? Anything that helps me filter accurately:
>
> - A dedicated alias (e.g., `maintenance@yourcompany.com`)?
> - A Gmail label or Outlook folder you route them to (e.g., `maintenance/incoming`)?
> - Subject line patterns ("repair", "broken", "issue with", etc.)?
> - Sender domain patterns (tenants on a known domain, your property manager, etc.)?
> - Anything else that distinguishes them from regular email?

Capture the answers as free-text into `inbox_hints`. The skill uses these at runtime to decide which messages to process. Don't try to translate to a Gmail filter spec here — store the raw hints; the skill body interprets them.

### 6. Run schedule (optional)

> When should I run?
>
> 1. **On demand** — only when you trigger me explicitly
> 2. **On a schedule** — I run at fixed times (e.g., every morning, every hour)

If they pick **on demand** → set `schedule: on-demand`, proceed to Q7.

If they pick **on a schedule** → ask one more question and branch on substrate.

#### 6a. Set up the schedule (only if "scheduled")

> How often? (every 15 minutes, hourly, every morning at 8am, etc.)

Capture into `schedule` as a natural-language cadence string.

Then ask once which substrate they're in (only matters here):

> Where are you running this — Claude.ai (web) or Claude Code (CLI)?
>
> - **Claude.ai** — I can set up a scheduled task using Claude's built-in scheduling. I'll do it as part of the regenerate output.
> - **Claude Code** — I'll give you a cron line to add to your crontab.

Store the answer in `runtime` (used only to render the right setup notes in step 7).

### 7. Summary + regenerate offer

Render the captured config as a compact table. Only include rows that are populated:

```
Storage type:      cloud-link
Storage location:  SharePoint > Operations > maintenance-log.xlsx
Property name:     Oakwood Apartments
Input source:      inbox
Inbox hints:       maintenance@oakwood.com alias, subjects with "repair" or "broken"
Schedule:          every morning at 8am
```

Then:

> Want me to print a customized version of this skill with these settings baked in? Save it as `SKILL.md` over the generic one and future runs will skip setup entirely.

**If yes:**
1. Read the current `SKILL.md` from this skill's directory.
2. In its frontmatter, set:
   - `setup_complete: true`
   - `storage_type: <captured>`
   - `storage_location: <captured>` (empty string if paste-each-time)
   - `property_name: <captured>` (empty string if skipped)
   - `input_source: <captured>` (defaults to `manual`)
   - `inbox_hints: <captured>` (empty string if not inbox-watching)
   - `schedule: <captured>` (defaults to `on-demand`)
3. Output the entire updated SKILL.md inside a fenced ` ```markdown ` block, prefixed with **one short instruction**:

   > Save this over your installed copy of `maintenance-request-tracker/SKILL.md`. In Claude Code, that's typically `~/.claude/skills/maintenance-request-tracker/SKILL.md`. In Claude.ai, re-upload the customized version through the skill management UI.

**If no:** use the captured config for the current session only, log the request if they pasted one, re-ask next run.

### 8. Schedule setup notes (only if Q6 picked "scheduled")

After the regenerate output, append the right setup snippet based on the runtime captured in 6a.

**Claude.ai:** offer to set up the scheduled task conversationally. Walk them through it using whatever scheduling primitive Claude.ai exposes for skills. Don't paste cron lines.

**Claude Code:** output the cron line. Brief.

```
0 8 * * * claude run maintenance-request-tracker
```

Translate the natural-language cadence (`every morning at 8am`) into the cron expression. If you can't (cadence is ambiguous), give the closest cron line and a one-sentence explanation of how to adjust.

If `input_source` is `manual` (no scheduled inbox-watching), skip this section entirely.

## After the interview

Once the user has installed the customized SKILL.md, future invocations read `setup_complete: true` and skip this file entirely. BOOTSTRAP.md remains bundled with the skill so the user (or a future setup pass) can re-customize without reinstalling from scratch.

## What NOT to do

- Do not skip the regenerate offer for path B. The whole point is to silence future setup.
- Do not "remember" config in a sidecar file or in the skill's working directory. The customized SKILL.md is the only persistence mechanism.
- Do not auto-process a request that was pasted alongside the slash invocation until the user has explicitly chosen path A or completed path B and indicated they want to log it. Hold the request, mention you noticed it, and ask.
- Do not introduce new questions beyond the ones in this script unless the user asks for advanced setup. Six questions is the cap.
