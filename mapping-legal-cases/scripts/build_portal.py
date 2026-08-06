#!/usr/bin/env python3
"""Build one offline HTML case portal from a .casebase Markdown map."""

import argparse
import html
import json
import re
import sys
import tempfile
from pathlib import Path

DOCS = (
    ("DOCUMENTS.md", "מסמכים"),
    ("GLOSSARY.md", "מילון מונחים"),
    ("PRIVACY_FLAGS.md", "דגלי פרטיות"),
    ("PARTIES.md", "צדדים"),
    ("TIMELINE.md", "ציר זמן"),
    ("CLAIMS.md", "עילות ותביעות"),
    ("EVIDENCE.md", "ראיות"),
    ("GAPS.md", "פערים"),
    ("RISKS.md", "סיכונים"),
    ("DEADLINES.md", "מועדים"),
    ("MAPPING_LOG.md", "יומן מיפוי"),
)

SVG_ICONS = {
    "MATTER.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 5V3h10v2M5 7h14a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9a2 2 0 0 1 2-2Zm-2 5h18M10 12v2h4v-2"/></svg>',
    "DOCUMENTS.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h9l4 4v11a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2Zm9 0v5h4M3 7v12a2 2 0 0 0 2 2h11"/></svg>',
    "GLOSSARY.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 5.5A3.5 3.5 0 0 1 6.5 2H11v17H6.5A3.5 3.5 0 0 0 3 22V5.5ZM21 5.5A3.5 3.5 0 0 0 17.5 2H13v17h4.5a3.5 3.5 0 0 1 3.5 3V5.5Z"/></svg>',
    "PRIVACY_FLAGS.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 10h12v11H6zM8.5 10V7.5a3.5 3.5 0 0 1 7 0V10M12 14v3"/></svg>',
    "PARTIES.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 11a4 4 0 1 0 0-8 4 4 0 0 0 0 8Zm7-1a3 3 0 1 0 0-6M2 21v-2a6 6 0 0 1 12 0v2m1-7a5 5 0 0 1 7 4.6V21"/></svg>',
    "TIMELINE.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M12 7v5l3.5 2"/></svg>',
    "CLAIMS.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3v18M7 21h10M5 6h14M5 6l-3 7h6L5 6Zm14 0-3 7h6l-3-7ZM3 13a3 3 0 0 0 4 0m10 0a3 3 0 0 0 4 0"/></svg>',
    "EVIDENCE.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="10.5" cy="10.5" r="6.5"/><path d="m15.5 15.5 5 5"/></svg>',
    "GAPS.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><circle cx="12" cy="12" r="9"/><path d="M9.7 9a2.4 2.4 0 1 1 3.4 2.2c-.8.4-1.1 1-1.1 1.8m0 3.5h.01"/></svg>',
    "RISKS.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 3 2.5 20h19L12 3Zm0 6v5m0 3h.01"/></svg>',
    "DEADLINES.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4m10-4v4M3 10h18m-14 4h3m4 0h3m-10 3h3"/></svg>',
    "MAPPING_LOG.md": '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M9 5h12M9 12h12M9 19h12M3 5h2M3 12h2M3 19h2"/></svg>',
}


def inline_md(text):
    """Render compact, escaped inline Markdown."""
    tokens = []

    def token(value):
        tokens.append(value)
        return f"\x00{len(tokens) - 1}\x00"

    def code(match):
        return token(f"<code>{html.escape(match.group(1), quote=False)}</code>")

    text = re.sub(r"`([^`]+)`", code, text)
    escaped = html.escape(text, quote=False)

    def link(match):
        label, url = match.group(1), html.unescape(match.group(2)).strip()
        if re.match(r"(?i)^(?:javascript|data|vbscript):", url):
            return label
        return token(f'<a href="{html.escape(url, quote=True)}">{label}</a>')

    escaped = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", link, escaped)
    escaped = re.sub(r"\*\*(.+?)\*\*|__(.+?)__", lambda m: f"<strong>{m.group(1) or m.group(2)}</strong>", escaped)
    escaped = re.sub(r"(?<!\w)\*([^*\n]+?)\*(?!\w)|(?<!\w)_([^_\n]+?)_(?!\w)", lambda m: f"<em>{m.group(1) or m.group(2)}</em>", escaped)
    for index, value in enumerate(tokens):
        escaped = escaped.replace(f"\x00{index}\x00", value)
    return escaped


def table_cells(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [cell.strip() for cell in re.split(r"(?<!\\)\|", line)]


def is_table_separator(line):
    cells = table_cells(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.replace(" ", "")) for cell in cells)


def markdown_to_html(markdown):
    """Render project template Markdown subset without dependencies."""
    lines = markdown.replace("\r\n", "\n").replace("\r", "\n").split("\n")
    output = []
    i = 0
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()
        if not stripped:
            i += 1
            continue

        fence = re.match(r"^\s*```([^`]*)$", line)
        if fence:
            language = fence.group(1).strip()
            code_lines = []
            i += 1
            while i < len(lines) and not re.match(r"^\s*```\s*$", lines[i]):
                code_lines.append(lines[i])
                i += 1
            i += i < len(lines)
            class_attr = f' class="language-{html.escape(language, quote=True)}"' if language else ""
            output.append(f"<pre><code{class_attr}>{html.escape(chr(10).join(code_lines), quote=False)}</code></pre>")
            continue

        heading = re.match(r"^\s{0,3}(#{1,4})\s+(.+?)\s*#*\s*$", line)
        if heading:
            level = len(heading.group(1))
            output.append(f"<h{level}>{inline_md(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", line):
            output.append("<hr>")
            i += 1
            continue

        if i + 1 < len(lines) and "|" in line and is_table_separator(lines[i + 1]):
            headers = table_cells(line)
            i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(table_cells(lines[i]))
                i += 1
            head = "".join(f"<th>{inline_md(cell)}</th>" for cell in headers)
            body = "".join("<tr>" + "".join(f"<td>{inline_md(cell)}</td>" for cell in row) + "</tr>" for row in rows)
            output.append(f'<div class="table-wrap"><table><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table></div>')
            continue

        list_match = re.match(r"^\s*([-+*]|\d+[.)])\s+(.+)$", line)
        if list_match:
            ordered = list_match.group(1)[0].isdigit()
            tag = "ol" if ordered else "ul"
            items = []
            while i < len(lines):
                item_match = re.match(r"^\s*([-+*]|\d+[.)])\s+(.+)$", lines[i])
                if not item_match or item_match.group(1)[0].isdigit() != ordered:
                    break
                content = item_match.group(2)
                task = re.match(r"^\[([ xX])\]\s*(.*)$", content)
                if task:
                    checked = " checked" if task.group(1).lower() == "x" else ""
                    rendered = f'<label class="task"><input type="checkbox" disabled{checked}> {inline_md(task.group(2))}</label>'
                else:
                    rendered = inline_md(content)
                items.append(f"<li>{rendered}</li>")
                i += 1
            output.append(f"<{tag}>" + "".join(items) + f"</{tag}>")
            continue

        if re.match(r"^\s*>\s?", line):
            quoted = []
            while i < len(lines) and re.match(r"^\s*>\s?", lines[i]):
                quoted.append(re.sub(r"^\s*>\s?", "", lines[i]))
                i += 1
            output.append(f"<blockquote>{markdown_to_html(chr(10).join(quoted))}</blockquote>")
            continue

        paragraph = [stripped]
        i += 1
        while i < len(lines) and lines[i].strip():
            candidate = lines[i]
            if (re.match(r"^\s*(?:```|#{1,4}\s|>|[-+*]\s+|\d+[.)]\s+)", candidate)
                    or re.fullmatch(r"\s*(?:-{3,}|\*{3,}|_{3,})\s*", candidate)
                    or (i + 1 < len(lines) and "|" in candidate and is_table_separator(lines[i + 1]))):
                break
            paragraph.append(candidate.strip())
            i += 1
        output.append(f"<p>{inline_md(' '.join(paragraph))}</p>")
    return "\n".join(output)


def first_h1(text):
    match = re.search(r"^#\s+(.+?)\s*#*\s*$", text, re.MULTILINE)
    return re.sub(r"[*_`]", "", match.group(1)).strip() if match else ""


def resolve_casebase(value):
    path = Path(value).expanduser()
    if path.is_dir() and path.name != ".casebase" and (path / ".casebase").is_dir():
        path = path / ".casebase"
    if not path.is_dir() or path.name != ".casebase":
        raise ValueError(f".casebase directory not found: {path}")
    return path.resolve()


def is_hebrew_bulk(text):
    hebrew = len(re.findall(r"[\u0590-\u05ff]", text))
    latin = len(re.findall(r"[A-Za-z]", text))
    return hebrew > latin


def build_portal(casebase_value, matter_value=None, out_value=None):
    casebase = resolve_casebase(casebase_value)
    cache = (casebase / ".cache").resolve()
    documents = []

    matter = Path(matter_value).expanduser() if matter_value else casebase.parent / "MATTER.md"
    if matter.is_file():
        resolved_matter = matter.resolve()
        if not resolved_matter.is_relative_to(cache):
            text = resolved_matter.read_text(encoding="utf-8", errors="replace")
            documents.append({"name": "MATTER.md", "label": "תקציר התיק", "text": text})

    for filename, label in DOCS:
        path = casebase / filename
        if path.is_file() and not path.resolve().is_relative_to(cache):
            documents.append({"name": filename, "label": label, "text": path.read_text(encoding="utf-8", errors="replace")})

    combined = "\n".join(doc["text"] for doc in documents)
    rtl = is_hebrew_bulk(combined)
    matter_doc = next((doc for doc in documents if doc["name"] == "MATTER.md"), None)
    title = first_h1(matter_doc["text"]) if matter_doc else ""
    title = title or casebase.parent.name or "פורטל תיק"
    direction, language = ("rtl", "he") if rtl else ("ltr", "en")

    nav = []
    sections = []
    for index, doc in enumerate(documents):
        doc_id = f"doc-{index}"
        badges = ""
        if doc["name"] == "DEADLINES.md":
            urgent = bool(re.search(r"\b(?:OVERDUE|URGENT)\b", doc["text"], re.IGNORECASE))
            badges = '<span class="badge deadline">מועד</span>' + ('<span class="alert-dot" title="דחוף או באיחור"></span>' if urgent else "")
        elif doc["name"] == "PRIVACY_FLAGS.md":
            badges = '<span class="badge privacy">חיסיון</span>'
        active = " active" if index == 0 else ""
        nav.append(f'<button class="nav-item{active}" data-target="{doc_id}" type="button"><span class="nav-icon">{SVG_ICONS[doc["name"]]}</span><span class="nav-label">{html.escape(doc["label"])}</span>{badges}</button>')
        hidden = "" if index == 0 else " hidden"
        sections.append(f'<article id="{doc_id}" class="document{hidden}" data-name="{html.escape(doc["name"], quote=True)}">{markdown_to_html(doc["text"])}</article>')

    empty = '<article class="document empty"><h1>לא נמצאו מסמכי מיפוי</h1><p>הפעילו את מיפוי התיק כדי להפיק את מסמכי הניתוח.</p></article>' if not documents else ""
    page = f'''<!doctype html>
<html lang="{language}" dir="{direction}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)} · פורטל תיק</title>
<style>
:root{{--navy:#0a1e3f;--teal:#14b8a6;--paper:#fff;--ink:#182230;--muted:#667085;--line:#e4e9f0;--soft:#f5f7fa}}
*{{box-sizing:border-box}}html,body{{margin:0;min-height:100%;background:var(--soft);color:var(--ink);font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Arial,sans-serif;line-height:1.7}}body{{display:grid;grid-template-columns:276px minmax(0,1fr);grid-template-rows:78px minmax(calc(100vh - 78px),auto)}}
.sidebar{{grid-row:1/3;background:var(--navy);color:#fff;padding:30px 18px;position:sticky;top:0;height:100vh;overflow:auto}}.brand{{font-size:13px;font-weight:700;color:#e6edf7;margin:0 10px 20px;padding:0 2px 17px;border-bottom:1px solid var(--teal)}}.nav{{display:grid;gap:4px}}.nav-item{{width:100%;min-width:0;border:0;background:transparent;color:#b9c6d8;border-radius:7px;padding:11px 12px;display:flex;flex-direction:row-reverse;direction:ltr;align-items:center;gap:10px;text-align:start;font:inherit;cursor:pointer;transition:background-color 120ms,color 120ms}}.nav-item:hover,.nav-item:focus-visible{{background:#102b54;color:#f8fafc;outline:none}}.nav-item:focus-visible{{box-shadow:0 0 0 2px var(--teal)}}.nav-item.active{{background:#112c54;color:#fff;box-shadow:inset 3px 0 0 var(--teal)}}[dir=rtl] .nav-item.active{{box-shadow:inset -3px 0 0 var(--teal)}}.nav-icon{{width:22px;height:22px;display:inline-flex;flex:0 0 22px}}.nav-icon svg{{width:22px;height:22px;stroke:currentColor;fill:none;stroke-width:1.7;stroke-linecap:round;stroke-linejoin:round}}.nav-label{{flex:1;font-size:14px;font-weight:600}}.badge{{font-size:10px;line-height:1;padding:4px 7px;border-radius:20px;font-weight:700}}.badge.deadline{{background:#fef3c7;color:#854d0e}}.badge.privacy{{background:#ccfbf1;color:#115e59}}.alert-dot{{width:7px;height:7px;border-radius:50%;background:#ef4444;box-shadow:0 0 0 2px #ef44442b;flex:0 0 auto}}
.topbar{{grid-column:2;background:var(--navy);color:#fff;padding:15px clamp(24px,5vw,68px);display:flex;align-items:center;gap:32px;position:sticky;top:0;z-index:2;border-bottom:1px solid #ffffff14}}.matter-title{{font-size:20px;font-weight:700;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1}}.search-wrap{{position:relative;width:min(360px,42vw)}}.search{{width:100%;border:1px solid #ffffff30;border-radius:8px;background:#ffffff0d;color:#fff;padding:10px 14px;font:inherit;outline:none;text-align:start;transition:border-color 120ms,background-color 120ms}}.search::placeholder{{color:#b8c4d5}}.search:focus{{border-color:var(--teal);background:#ffffff14;box-shadow:0 0 0 3px #14b8a62b}}
main{{grid-column:2;padding:44px clamp(24px,6vw,90px) 80px;min-width:0}}.document{{max-width:1040px;margin:0 auto;background:var(--paper);border:1px solid var(--line);border-radius:14px;padding:clamp(30px,5vw,64px);box-shadow:0 4px 18px #0a1e3f0a;font-family:"Noto Sans Hebrew","Segoe UI",Arial,sans-serif}}.document.hidden{{display:none}}h1,h2,h3,h4{{color:var(--navy);line-height:1.25;margin:1.7em 0 .65em}}h1{{font-size:clamp(28px,4vw,38px);font-weight:750;margin-top:0;padding-bottom:18px;border-bottom:1px solid var(--line)}}h2{{font-size:25px;font-weight:700}}h3{{font-size:20px;font-weight:700}}h4{{font-size:16px;font-weight:700}}p,li{{font-size:16px}}p{{margin:0 0 1.15em}}a{{color:#087f75;text-underline-offset:3px}}strong{{color:#101828}}code{{font-family:"SFMono-Regular",Consolas,monospace;background:#eef2f6;color:#27364a;padding:.15em .4em;border:1px solid #e1e6ed;border-radius:5px;font-size:.9em;direction:ltr;unicode-bidi:embed}}pre{{background:#07162f;color:#dce8f7;border-radius:9px;padding:20px;overflow:auto;direction:ltr;text-align:left}}pre code{{background:transparent;padding:0;color:inherit;border:0}}blockquote{{margin:26px 0;padding:12px 22px;border-inline-start:3px solid var(--teal);background:#f7fafb;color:#344054}}blockquote p:last-child{{margin-bottom:0}}hr{{border:0;border-top:1px solid var(--line);margin:36px 0}}ul,ol{{padding-inline-start:27px}}li{{margin:8px 0}}.task{{display:inline-flex;align-items:center;gap:8px}}input[type=checkbox]{{appearance:none;width:16px;height:16px;margin:0;border:1.5px solid #98a2b3;border-radius:4px;background:#f2f4f7;position:relative;opacity:1}}input[type=checkbox]:checked{{background:var(--teal);border-color:var(--teal)}}input[type=checkbox]:checked::after{{content:"✓";position:absolute;color:#fff;font-size:12px;line-height:14px;inset-inline-start:2px;top:0}}.table-wrap{{overflow-x:auto;margin:27px 0;border:1px solid var(--line);border-radius:10px}}table{{width:100%;border-collapse:collapse;font-size:14px}}th{{background:#f2f5f8;color:var(--navy);font-weight:700}}th,td{{padding:13px 16px;text-align:start;border-bottom:1px solid var(--line);vertical-align:top}}tbody tr:last-child td{{border-bottom:0}}mark{{background:#fef08a;color:#172033;border-radius:2px;padding:0 1px}}.no-results{{display:none;color:var(--muted);text-align:center;margin:25px}}.empty{{color:var(--muted)}}
@media(max-width:760px){{body{{display:block}}.sidebar{{position:static;height:auto;padding:14px;overflow-x:auto}}.brand{{display:none}}.nav{{display:flex;min-width:max-content}}.nav-item{{width:auto}}.badge{{display:none}}.topbar{{position:sticky;padding:13px 16px;gap:12px}}.matter-title{{font-size:15px}}.search-wrap{{width:45vw}}main{{padding:20px 12px 50px}}.document{{padding:25px 20px;border-radius:10px}}}}
@media print{{body{{display:block;background:#fff}}.sidebar,.topbar,.no-results{{display:none!important}}main{{display:block;padding:0}}.document,.document.hidden{{display:block!important;max-width:none;border:0;box-shadow:none;padding:18mm 12mm;break-after:page}}a{{color:inherit}}}}
</style>
</head>
<body>
<aside class="sidebar" dir="rtl"><div class="brand">פורטל תיק</div><nav class="nav" aria-label="מסמכי התיק">{''.join(nav)}</nav></aside>
<header class="topbar" dir="rtl"><div class="matter-title">{html.escape(title)}</div><div class="search-wrap"><input id="search" class="search" type="search" placeholder="חיפוש במסמך הנוכחי…" aria-label="חיפוש במסמך הנוכחי…"></div></header>
<main dir="{direction}">{''.join(sections)}{empty}<p id="no-results" class="no-results">לא נמצאו התאמות במסמך זה.</p></main>
<script>
(()=>{{
 const docs=[...document.querySelectorAll('article.document[data-name]')], originals=new Map(docs.map(d=>[d.id,d.innerHTML]));
 const search=document.getElementById('search'), noResults=document.getElementById('no-results');
 function activeDoc(){{return docs.find(d=>!d.classList.contains('hidden'))}}
 function highlight(root,q){{
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT),nodes=[]; while(walker.nextNode())nodes.push(walker.currentNode);
  nodes.forEach(node=>{{if(!node.data.toLocaleLowerCase().includes(q))return; const frag=document.createDocumentFragment(); let text=node.data,pos=0,lower=text.toLocaleLowerCase(),at;
   while((at=lower.indexOf(q,pos))!==-1){{frag.append(text.slice(pos,at));const mark=document.createElement('mark');mark.textContent=text.slice(at,at+q.length);frag.append(mark);pos=at+q.length}}frag.append(text.slice(pos));node.replaceWith(frag)}})
 }}
 function runSearch(){{const doc=activeDoc();if(!doc)return;doc.innerHTML=originals.get(doc.id);const q=search.value.trim().toLocaleLowerCase();[...doc.children].forEach(el=>el.style.display='');noResults.style.display='none';if(!q)return;let shown=0;[...doc.children].forEach(el=>{{const hit=el.textContent.toLocaleLowerCase().includes(q);el.style.display=hit?'':'none';if(hit){{shown++;highlight(el,q)}}}});noResults.style.display=shown?'none':'block'}}
 document.querySelectorAll('.nav-item').forEach(button=>button.addEventListener('click',()=>{{document.querySelectorAll('.nav-item').forEach(b=>b.classList.remove('active'));button.classList.add('active');docs.forEach(d=>d.classList.toggle('hidden',d.id!==button.dataset.target));runSearch();window.scrollTo({{top:0,behavior:'auto'}})}}));
 search.addEventListener('input',runSearch);
}})();
</script>
</body>
</html>'''
    output = Path(out_value).expanduser() if out_value else casebase / "case-portal.html"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(page, encoding="utf-8")
    return {"out": str(output.resolve()), "docs_included": [doc["name"] for doc in documents], "rtl": rtl, "bytes": output.stat().st_size}


def selftest():
    with tempfile.TemporaryDirectory(prefix="case-portal-selftest-") as temp:
        root = Path(temp) / "עניין"
        casebase = root / ".casebase"
        casebase.mkdir(parents=True)
        (root / "MATTER.md").write_text("# תיק בדיקה\n\nתיאור מפורט בעברית של העניין המשפטי והצדדים המעורבים.\n", encoding="utf-8")
        (casebase / "DOCUMENTS.md").write_text("# מסמכים\n\n| מסמך | עמוד |\n|---|---|\n| כתב תביעה | `claim.pdf:p3` |\n", encoding="utf-8")
        (casebase / "DEADLINES.md").write_text("# מועדים\n\n- [ ] להגיש תגובה לבית המשפט\n- [x] לבדוק את המועד האחרון\n", encoding="utf-8")
        result = build_portal(casebase)
        page = Path(result["out"]).read_text(encoding="utf-8")
        assert 'dir="rtl"' in page
        assert "תיק בדיקה" in page and "מסמכים" in page and "מועדים" in page
        assert "<table>" in page and 'type="checkbox"' in page
        assert "<svg" in page and not any(icon in page for icon in ("📄", "📇", "🔐", "👥", "📅", "⚖️", "🔎", "❓", "⚠️", "⏰", "🗂", "📋"))
        assert "פורטל תיק" in page and "חיפוש במסמך" in page
        assert not re.search(r"<(?:script|link)\b[^>]*(?:src|href)=[\"']https?://", page, re.IGNORECASE)
        assert not re.search(r"@import\s+(?:url\()?['\"]?https?://", page, re.IGNORECASE)
        print(json.dumps({"selftest": "passed", **result}, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--casebase", help=".casebase directory or its matter folder")
    parser.add_argument("--matter", help="optional MATTER.md path")
    parser.add_argument("--out", help="output HTML path (default: .casebase/case-portal.html)")
    parser.add_argument("--selftest", action="store_true", help="run isolated assert-based self-check")
    args = parser.parse_args()
    if args.selftest:
        selftest()
        return 0
    if not args.casebase:
        parser.error("--casebase is required unless --selftest is used")
    try:
        result = build_portal(args.casebase, args.matter, args.out)
    except (OSError, ValueError) as error:
        print(json.dumps({"error": str(error)}, ensure_ascii=False), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
