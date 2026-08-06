#!/usr/bin/env python3
"""new-matter: deterministic matter scaffolder for Lawcal OS.

Fast, no-LLM. Given the interview answers (a JSON spec), it:
  1. Creates the matter folder tree,
  2. Renders AGENTS.md (Hermes project context, auto-loaded) + MATTER.md
     (the presentable human brief) in Hebrew (default) or English,
  3. Registers the matter folder as a Hermes WebUI workspace.

The LLM does the interview + writes the rich MATTER.md body; this script does
the deterministic, repeatable scaffolding so opening a matter is instant.

Usage:
    python new_matter.py --spec spec.json            # scaffold from a spec file
    python new_matter.py --spec -                     # read spec JSON from stdin
    python new_matter.py --print-template he          # dump a blank spec (he|en)

Output: JSON summary on stdout (paths created, workspace registration result).

ponytail: workspaces.json path resolution covers the common tenant layouts
(HERMES_WEBUI_STATE_DIR / HERMES_HOME / ~/.hermes). Add profile-scoped
sub-paths only if a tenant reports the matter not showing in the switcher.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import date
from pathlib import Path

SUBDIRS = ["documents", "correspondence", "drafts", "research", "deliverables"]

BLANK_SPEC = {
    "language": "he",                # "he" (default) or "en"
    "matter_name": "",               # short human name, e.g. "עודד סלע נ' חברת X"
    "matter_type": "",               # e.g. litigation / contract / regulatory / due-diligence
    "client": "",                    # client full name
    "opposing": "",                  # opposing party (optional)
    "other_parties": [],             # ["name — role", ...]
    "jurisdiction": "",              # e.g. "בית משפט השלום תל אביב" / "ISA" / "arbitration"
    "case_number": "",               # court/reference number if any (optional)
    "summary": "",                   # 1-3 sentence plain-language matter summary
    "objectives": [],                # ["...", ...] what the client wants
    "key_dates": [],                 # ["YYYY-MM-DD — event", ...]
    "open_questions": [],            # ["...", ...]
    "base_dir": "",                  # parent dir to create the matter under (default: cwd)
    "register_workspace": True,      # add to the WebUI workspace switcher
}


def _slug(name: str) -> str:
    """Filesystem-safe slug that keeps Hebrew/Unicode letters."""
    s = name.strip().lower()
    s = re.sub(r"[\s/\\]+", "-", s)
    s = re.sub(r"[^\w\-\u0590-\u05FF]", "", s)  # keep word chars + Hebrew block
    s = re.sub(r"-{2,}", "-", s).strip("-")
    return s or "matter"


def _workspaces_file() -> Path:
    """Resolve the WebUI workspaces.json used by the tenant."""
    state = os.environ.get("HERMES_WEBUI_STATE_DIR")
    if state:
        return Path(state).expanduser() / "workspaces.json"
    home = os.environ.get("HERMES_HOME")
    base = Path(home).expanduser() if home else Path.home() / ".hermes"
    return base / "webui" / "workspaces.json"


def register_workspace(path: Path, name: str) -> dict:
    """Append {path, name} to workspaces.json if not already present. Best-effort."""
    ws_file = _workspaces_file()
    entry = {"path": str(path), "name": name}
    try:
        ws_file.parent.mkdir(parents=True, exist_ok=True)
        current = []
        if ws_file.exists():
            try:
                current = json.loads(ws_file.read_text(encoding="utf-8")) or []
            except Exception:
                current = []
        if any(isinstance(w, dict) and w.get("path") == str(path) for w in current):
            return {"registered": True, "already_present": True, "file": str(ws_file)}
        current.append(entry)
        ws_file.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
        return {"registered": True, "already_present": False, "file": str(ws_file)}
    except Exception as e:
        return {"registered": False, "error": str(e), "file": str(ws_file)}


def _bullets(items, empty_he="—", he=True):
    items = [str(i).strip() for i in (items or []) if str(i).strip()]
    if not items:
        return f"- {empty_he if he else '—'}"
    return "\n".join(f"- {i}" for i in items)


def render_agents(spec: dict, he: bool) -> str:
    """AGENTS.md — compact project context Hermes auto-injects for this matter."""
    d = spec
    today = date.today().isoformat()
    if he:
        return f"""# {d.get('matter_name') or 'תיק חדש'}

הקשר הפרויקט לתיק משפטי זה. Hermes טוען קובץ זה אוטומטית בכל שיחה שנפתחת בתיקייה.

## סוג התיק
{d.get('matter_type') or '—'}

## צדדים
- **לקוח:** {d.get('client') or '—'}
- **צד שכנגד:** {d.get('opposing') or '—'}
{_bullets([f"**נוסף:** {p}" for p in d.get('other_parties', [])], he=True)}

## פורום / מספר הליך
- **פורום:** {d.get('jurisdiction') or '—'}
- **מספר הליך:** {d.get('case_number') or '—'}

## תמצית
{d.get('summary') or '—'}

## מטרות הלקוח
{_bullets(d.get('objectives'), he=True)}

## מבנה התיקייה
- `MATTER.md` — סקירת התיק המלאה (המסמך המרכזי לקריאה)
- `documents/` — מסמכי מקור (חוזים, כתבי טענות, ראיות)
- `correspondence/` — התכתבויות
- `drafts/` — טיוטות בעבודה
- `research/` — מחקר משפטי
- `deliverables/` — תוצרים ללקוח
- `.casebase/` — מיפוי תיק אוטומטי (נוצר ע"י `mapping-legal-cases` כשיש מסמכי מקור)

## הנחיות עבודה
- שפת ברירת מחדל: **עברית**. עבור לאנגלית רק אם המשתמש כותב באנגלית או ביקש זאת.
- לאחר הוספת מסמכים ל-`documents/`, הרץ את מיפוי התיק (`mapping-legal-cases`) לקבלת ניתוח מלא.
- כל קביעה עובדתית חייבת להפנות לקובץ מקור.

---
*נוצר ע"י new-matter ב-{today}*
"""
    return f"""# {d.get('matter_name') or 'New Matter'}

Project context for this legal matter. Hermes auto-loads this file for any chat opened in this folder.

## Matter type
{d.get('matter_type') or '—'}

## Parties
- **Client:** {d.get('client') or '—'}
- **Opposing:** {d.get('opposing') or '—'}
{_bullets([f"**Other:** {p}" for p in d.get('other_parties', [])], he=False)}

## Forum / case number
- **Forum:** {d.get('jurisdiction') or '—'}
- **Case number:** {d.get('case_number') or '—'}

## Summary
{d.get('summary') or '—'}

## Client objectives
{_bullets(d.get('objectives'), he=False)}

## Folder layout
- `MATTER.md` — full matter brief (primary read)
- `documents/` — source documents (contracts, pleadings, evidence)
- `correspondence/` — correspondence
- `drafts/` — work-in-progress drafts
- `research/` — legal research
- `deliverables/` — client deliverables
- `.casebase/` — auto case map (generated by `mapping-legal-cases` once source docs exist)

## Working rules
- Default language: **English** for this matter. Match the user otherwise.
- After adding files to `documents/`, run the case mapper (`mapping-legal-cases`) for full analysis.
- Every factual assertion must cite a source file.

---
*Created by new-matter on {today}*
"""


def render_matter(spec: dict, he: bool) -> str:
    """MATTER.md — the presentable, human-facing matter brief (Markdown)."""
    d = spec
    today = date.today().isoformat()
    parties = "\n".join(
        f"| {lbl} | {val or '—'} |"
        for lbl, val in (
            (("לקוח" if he else "Client"), d.get("client")),
            (("צד שכנגד" if he else "Opposing"), d.get("opposing")),
            (("פורום" if he else "Forum"), d.get("jurisdiction")),
            (("מספר הליך" if he else "Case no."), d.get("case_number")),
        )
    )
    for p in d.get("other_parties", []):
        parties += f"\n| {'צד נוסף' if he else 'Other party'} | {p} |"
    if he:
        return f"""# {d.get('matter_name') or 'תיק חדש'}

> **סוג:** {d.get('matter_type') or '—'} · **נפתח:** {today} · **סטטוס:** פעיל

## תמצית
{d.get('summary') or '_להשלמה_'}

## צדדים
| תפקיד | שם |
|---|---|
{parties}

## מטרות הלקוח
{_bullets(d.get('objectives'), he=True)}

## מועדים מרכזיים
{_bullets(d.get('key_dates'), he=True)}

## שאלות פתוחות
{_bullets(d.get('open_questions'), he=True)}

## ניתוח משפטי
_להשלמה — הוסף ניתוח לאחר סקירת המסמכים. הרץ `mapping-legal-cases` על `documents/` לקבלת מיפוי מלא (צדדים, ציר זמן, טענות, ראיות, פערים, סיכונים, מועדים)._

## צעדים הבאים
- [ ] העלה מסמכי מקור ל-`documents/`
- [ ] הרץ מיפוי תיק (`mapping-legal-cases`)
- [ ] סקור מועדים וסיכונים

---
*תיק נוצר ע"י new-matter ב-{today}. מסמך זה הוא מקור האמת לתיק — עדכן אותו לאורך העבודה.*
"""
    return f"""# {d.get('matter_name') or 'New Matter'}

> **Type:** {d.get('matter_type') or '—'} · **Opened:** {today} · **Status:** Active

## Summary
{d.get('summary') or '_TBD_'}

## Parties
| Role | Name |
|---|---|
{parties}

## Client objectives
{_bullets(d.get('objectives'), he=False)}

## Key dates
{_bullets(d.get('key_dates'), he=False)}

## Open questions
{_bullets(d.get('open_questions'), he=False)}

## Legal analysis
_TBD — add after reviewing documents. Run `mapping-legal-cases` on `documents/` for a full map (parties, timeline, claims, evidence, gaps, risks, deadlines)._

## Next steps
- [ ] Upload source documents to `documents/`
- [ ] Run the case mapper (`mapping-legal-cases`)
- [ ] Review deadlines and risks

---
*Matter created by new-matter on {today}. This file is the matter's source of truth — keep it updated.*
"""


def scaffold(spec: dict) -> dict:
    he = (spec.get("language") or "he").lower().startswith("he")
    name = spec.get("matter_name") or ("תיק חדש" if he else "New Matter")
    base = Path(spec.get("base_dir") or os.getcwd()).expanduser().resolve()
    matter_dir = base / _slug(name)
    matter_dir.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        (matter_dir / sub).mkdir(exist_ok=True)

    (matter_dir / "AGENTS.md").write_text(render_agents(spec, he), encoding="utf-8")
    (matter_dir / "MATTER.md").write_text(render_matter(spec, he), encoding="utf-8")

    ws = {"registered": False, "skipped": True}
    if spec.get("register_workspace", True):
        ws = register_workspace(matter_dir, name)

    return {
        "success": True,
        "matter_dir": str(matter_dir),
        "language": "he" if he else "en",
        "created": ["AGENTS.md", "MATTER.md"] + [f"{s}/" for s in SUBDIRS],
        "workspace": ws,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold a new legal matter.")
    ap.add_argument("--spec", help="Path to spec JSON, or '-' for stdin.")
    ap.add_argument("--print-template", choices=["he", "en"],
                    help="Print a blank spec template and exit.")
    args = ap.parse_args()

    if args.print_template:
        tmpl = dict(BLANK_SPEC, language=args.print_template)
        print(json.dumps(tmpl, ensure_ascii=False, indent=2))
        return 0

    if not args.spec:
        ap.error("--spec is required (or use --print-template)")

    raw = sys.stdin.read() if args.spec == "-" else Path(args.spec).read_text(encoding="utf-8")
    spec = json.loads(raw)
    if not spec.get("matter_name"):
        print(json.dumps({"success": False, "error": "matter_name is required"}), file=sys.stderr)
        return 2
    print(json.dumps(scaffold(spec), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
