---
name: new-matter
description: Open a NEW legal matter/case for Lawcal — runs a short structured intake interview, then scaffolds a durable matter workspace (folder tree + presentable Hebrew MATTER.md brief + AGENTS.md project context that Hermes auto-loads) and registers it in the WebUI workspace switcher. Trigger when the user says "open a new matter/case", "תיק חדש", "start a new file for client X", "new project for [case]", or wants to set up a fresh case workspace. Do NOT use for analyzing an existing folder of documents (that is mapping-legal-cases) or reviewing a single upload (ocr-and-documents).
license: Apache-2.0
metadata:
  author: Chen Friedman / Lawcal AI
  version: "1.0.0"
---

# New Matter

Opens a new legal matter as a durable, well-structured workspace. Inspired by GSD's
`/gsd-new-project` (interview → bootstrap context/state files), adapted to legal matters.

**Two clean parts:**
1. **Interview (you, the agent)** — a short, adaptive intake conversation to capture the essentials.
2. **Scaffold (deterministic script)** — creates the folder tree, renders `MATTER.md` + `AGENTS.md`, and registers the WebUI workspace. Instant, repeatable, no tokens.

This skill is the *entry point* to a matter. It does **not** analyze documents — after source
documents land in `documents/`, escalate to `mapping-legal-cases` for the full case map.

## When to use vs. not

| Situation | Skill |
|---|---|
| "Open a new matter / תיק חדש / start a file for client X" | **new-matter** (this) |
| "Map / analyze this folder of case documents" | `mapping-legal-cases` |
| "Summarize / read this one PDF" | `ocr-and-documents` |

## Language (default Hebrew)

Conduct the interview and render outputs in **Hebrew by default**. Switch to English only if:
- the user is writing to you in English, **or**
- the user's stored preferences / USER.md say English, **or**
- the user explicitly asks for English.

Set `"language": "he"` or `"en"` in the spec accordingly.

## Step 1 — Interview

Ask for the essentials in **one or two compact messages** — do not interrogate one field at a
time. Lead with what you need, mark optionals. Minimum required: **matter name** and **matter type**.
Everything else is optional but valuable. Collect:

- **שם התיק / Matter name** (required) — e.g. `עודד סלע נ' חברת אלפא בע"מ`
- **סוג התיק / Matter type** (required) — litigation / חוזה / רגולציה / due-diligence / ...
- **לקוח / Client** — full name
- **צד שכנגד / Opposing party** — if any
- **צדדים נוספים / Other parties** — list with roles (`name — role`)
- **פורום ומספר הליך / Forum + case number** — court/tribunal/regulator + reference
- **תמצית / Summary** — 1–3 sentences, plain language
- **מטרות הלקוח / Client objectives** — what the client wants
- **מועדים מרכזיים / Key dates** — `YYYY-MM-DD — event`
- **שאלות פתוחות / Open questions**
- **base_dir** — where to create the matter folder. If the user doesn't specify, default to the
  current workspace and tell them where it will live.

If the user gives a messy brief (WhatsApp dump, email), extract the fields yourself and **confirm
the parsed spec back to them briefly** before scaffolding. Don't stall on missing optionals — fill
what you have, leave the rest for `MATTER.md` to mark `_TBD_`.

## Step 2 — Scaffold

Build a spec JSON (see `--print-template`) and run the scaffolder:

```bash
python scripts/new_matter.py --print-template he   # see the blank spec shape
```

Then pass your filled spec (write it to a temp file or pipe via stdin):

```bash
python scripts/new_matter.py --spec /tmp/matter-spec.json
# or:  cat spec.json | python scripts/new_matter.py --spec -
```

The script creates, under `base_dir/<slug>/`:
- `AGENTS.md` — compact project context. **Hermes auto-loads this** for every chat opened in the
  matter folder, so the agent always knows the parties, forum, and working rules.
- `MATTER.md` — the **presentable** matter brief (clean Markdown tables + sections). This is the
  human-facing source of truth for the matter — not a JSON dump.
- `documents/ correspondence/ drafts/ research/ deliverables/` — working subfolders.

It also registers the matter folder in the WebUI workspace switcher
(`workspaces.json`), so the user can jump straight into it. Registration is idempotent.

Parse the script's JSON output for `matter_dir` and `workspace.registered`.

## Step 3 — Enrich MATTER.md (optional but recommended)

The script renders a solid skeleton. If you have enough context, **edit `MATTER.md`** to flesh out
the `## ניתוח משפטי / Legal analysis` section with an initial read (issues, applicable law, strategy
direction) — cite sources if any documents were provided. Keep it in the matter language.

## Step 4 — Summarize to the user

Report concisely (in the matter language):
- ✅ Matter created at `matter_dir`
- Files created: `MATTER.md`, `AGENTS.md`, working folders
- ✅ Added to the workspace switcher (or a note if registration was skipped/failed)
- **Next step:** upload source documents to `documents/`, then run the case map
  (`mapping-legal-cases`) for a full analysis (parties, timeline, claims, evidence, gaps, risks,
  deadlines).

Show the path so they can open it. Attach `MEDIA:<matter_dir>/MATTER.md` if the surface renders it.

## Handoff to mapping-legal-cases

`new-matter` and `mapping-legal-cases` are complementary, not overlapping:

- **new-matter** = fast, deterministic *setup* of an empty, well-structured matter (seconds).
- **mapping-legal-cases** = heavy, thorough *analysis* of documents already in the folder (minutes).

The `.casebase/` map from `mapping-legal-cases` lives alongside `MATTER.md`. `MATTER.md` stays the
human brief; `.casebase/` holds the exhaustive cross-referenced analysis. Point the user from one to
the other; never run the heavy mapper as part of opening a matter.

## Critical rules

1. **Hebrew by default** — outputs and interview in Hebrew unless the user/preferences indicate English.
2. **Required minimum** — never scaffold without at least a matter name and type; ask if missing.
3. **Non-destructive** — the script only creates/appends. It never moves, renames, or deletes
   existing files, and workspace registration is idempotent (safe to re-run).
4. **MATTER.md is the source of truth** — keep it updated as the matter progresses; it is the
   presentable brief, distinct from the internal `.casebase/` analysis cache.
5. **Don't re-invent extraction** — document analysis is `mapping-legal-cases`' job, not this skill's.

## Supporting files

- `scripts/new_matter.py` — deterministic scaffolder (folder tree, AGENTS.md, MATTER.md, workspace
  registration). Run `--print-template he|en` to see the spec shape.
