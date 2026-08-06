"""
Harvey Specterbot — Redline Engine (Standalone CLI)
Produces genuine Word tracked changes (w:ins/w:del) from Claude's recommended edits.

Flow:
1. Extract paragraphs from original .docx with their XML structure preserved
2. Send to Claude with instructions to return structured JSON edits
3. Apply edits as Open XML revision marks in the original document
4. Save the modified .docx with tracked changes visible in Word
5. Optionally copy output to a shared exchange directory if HARVEY_EXCHANGE_DIR is set

Usage:
    python redline_engine.py input.docx
    python redline_engine.py input.docx output_redline.docx
    python redline_engine.py input.docx --instructions "focus on IP clauses"
    python redline_engine.py input.docx output_redline.docx --instructions "tighten indemnification"
"""

import argparse
import io
import json
import copy
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree

import anthropic

# Open XML namespaces
NAMESPACES = {
    'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
    'wp': 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing',
    'mc': 'http://schemas.openxmlformats.org/markup-compatibility/2006',
    'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
    'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
}

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

AUTHOR = "Harvey Specterbot"
REVISION_DATE = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

import os
EXCHANGE_DIR = Path(os.environ.get("HARVEY_EXCHANGE_DIR", "")) if os.environ.get("HARVEY_EXCHANGE_DIR") else None


def extract_paragraphs(docx_bytes: bytes) -> list[dict]:
    """Extract numbered paragraphs from a .docx for Claude to reference."""
    import docx
    doc = docx.Document(io.BytesIO(docx_bytes))
    paragraphs = []
    for i, para in enumerate(doc.paragraphs):
        text = para.text.strip()
        if text:
            paragraphs.append({
                "index": i,
                "text": text,
                "style": para.style.name if para.style else "Normal",
            })
    return paragraphs


def get_edit_instructions(paragraphs: list[dict], user_prompt: str) -> list[dict]:
    """
    Ask Claude to analyze the document and return structured edit instructions.
    Returns a list of edits, each with: paragraph_index, old_text, new_text, reason.
    """
    doc_text = "\n".join(
        f"[{p['index']}] ({p['style']}) {p['text']}"
        for p in paragraphs
    )

    system = """You are Harvey Specterbot, an AI legal editor. You review legal documents and produce SPECIFIC TEXT EDITS as structured JSON.

CRITICAL RULES:
- Return ONLY a JSON array of edits. No prose before or after.
- Each edit must specify the exact old text to find and the exact new text to replace it with.
- old_text must be a VERBATIM substring from the paragraph — exact match, including punctuation and capitalization.
- Keep old_text short enough to be unique within its paragraph (a phrase or sentence, not the whole paragraph).
- new_text is what replaces it.
- Include a brief reason for each edit.
- Only make edits that improve the document legally — fix ambiguities, add protections, narrow overbroad language, correct errors, add missing defined terms, and any provisions that are one-sided or potentially unenforceable.
- Do NOT rewrite style preferences. Only make legally meaningful changes.
- Do NOT edit boilerplate that is standard and acceptable.
- Focus on the most impactful 10-25 changes, not every possible tweak.

JSON format:
[
  {
    "paragraph_index": 5,
    "old_text": "exact text to find in the paragraph",
    "new_text": "replacement text",
    "reason": "Brief explanation of why this change matters"
  }
]

Return ONLY the JSON array. No markdown code fences. No explanation text."""

    user_msg = f"""Review this legal document and produce specific tracked-change edits.

{user_prompt}

DOCUMENT PARAGRAPHS (numbered by index):

{doc_text}

Return ONLY the JSON array of edits."""

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=8192,
        system=system,
        messages=[{"role": "user", "content": user_msg}],
    )

    raw = response.content[0].text.strip()

    # Strip markdown code fences if Claude added them despite instructions
    if raw.startswith("```"):
        raw = re.sub(r'^```(?:json)?\n?', '', raw)
        raw = re.sub(r'\n?```$', '', raw)

    try:
        edits = json.loads(raw)
    except json.JSONDecodeError:
        # Try to extract JSON array from the response
        match = re.search(r'\[[\s\S]*\]', raw)
        if match:
            edits = json.loads(match.group())
        else:
            raise ValueError(f"Claude did not return valid JSON edits. Response: {raw[:500]}")

    return edits


def apply_tracked_changes(docx_bytes: bytes, edits: list[dict]) -> tuple[bytes, int]:
    """
    Apply edits as genuine Word tracked changes in the .docx XML.
    Returns the modified .docx as bytes and the count of applied edits.
    """
    # Read the docx as a zip
    zin = ZipFile(io.BytesIO(docx_bytes), 'r')
    doc_xml = zin.read('word/document.xml')

    # Parse the XML
    tree = etree.fromstring(doc_xml)

    # Register namespaces to avoid ns0/ns1 prefix pollution
    for prefix, uri in NAMESPACES.items():
        etree.register_namespace(prefix, uri)

    # Find all paragraphs in document order
    body = tree.find(f'{W}body')
    all_paragraphs = body.findall(f'.//{W}p')

    # Track revision ID
    rev_id = 1000

    # Index paragraphs by their text content for matching
    para_text_map = {}
    for i, para in enumerate(all_paragraphs):
        runs = para.findall(f'.//{W}r')
        full_text = ''
        for run in runs:
            t = run.find(f'{W}t')
            if t is not None and t.text:
                full_text += t.text
        para_text_map[i] = full_text

    edits_applied = 0

    for edit in edits:
        para_idx = edit.get("paragraph_index")
        old_text = edit.get("old_text", "")
        new_text = edit.get("new_text", "")

        if not old_text or para_idx is None:
            continue

        # Find the target paragraph
        if para_idx >= len(all_paragraphs):
            continue

        para = all_paragraphs[para_idx]
        runs = para.findall(f'{W}r')

        # Reconstruct the paragraph text to find the old_text position
        full_text = ""
        run_map = []  # [(start_pos, end_pos, run_element)]

        for run in runs:
            t = run.find(f'{W}t')
            if t is not None and t.text:
                start = len(full_text)
                full_text += t.text
                run_map.append((start, len(full_text), run))

        # Find the old_text in the full paragraph text
        match_start = full_text.find(old_text)
        if match_start == -1:
            # Try case-insensitive
            match_start = full_text.lower().find(old_text.lower())
            if match_start == -1:
                continue

        match_end = match_start + len(old_text)

        # Find which runs contain the matched text
        # and replace them with del + ins revision marks
        affected_runs = []
        for start, end, run in run_map:
            if start < match_end and end > match_start:
                affected_runs.append((start, end, run))

        if not affected_runs:
            continue

        # Get the run properties from the first affected run (preserve formatting)
        first_run = affected_runs[0][2]
        rpr = first_run.find(f'{W}rPr')
        rpr_copy = copy.deepcopy(rpr) if rpr is not None else None

        # Find the insertion point in the paragraph (before the first affected run)
        insert_before = affected_runs[0][2]
        parent = insert_before.getparent()
        insert_idx = list(parent).index(insert_before)

        # Build the deletion element
        del_elem = etree.SubElement(parent, f'{W}del')
        del_elem.set(f'{W}id', str(rev_id))
        del_elem.set(f'{W}author', AUTHOR)
        del_elem.set(f'{W}date', REVISION_DATE)
        rev_id += 1

        del_run = etree.SubElement(del_elem, f'{W}r')
        if rpr_copy is not None:
            del_run.append(copy.deepcopy(rpr_copy))
        del_text = etree.SubElement(del_run, f'{W}delText')
        del_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        del_text.text = old_text

        # Build the insertion element
        ins_elem = etree.SubElement(parent, f'{W}ins')
        ins_elem.set(f'{W}id', str(rev_id))
        ins_elem.set(f'{W}author', AUTHOR)
        ins_elem.set(f'{W}date', REVISION_DATE)
        rev_id += 1

        ins_run = etree.SubElement(ins_elem, f'{W}r')
        if rpr_copy is not None:
            ins_run.append(copy.deepcopy(rpr_copy))
        ins_text = etree.SubElement(ins_run, f'{W}t')
        ins_text.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')
        ins_text.text = new_text

        # Handle the actual runs: split runs that partially overlap the match region
        # and remove the ones that are fully within it
        for start, end, run in affected_runs:
            t = run.find(f'{W}t')
            if t is None or t.text is None:
                continue

            run_text = t.text
            run_start = start
            run_end = end

            overlap_start = max(match_start, run_start) - run_start
            overlap_end = min(match_end, run_end) - run_start

            text_before = run_text[:overlap_start]
            text_after = run_text[overlap_end:]

            if text_before and text_after:
                # Run is split — keep before text in original run, create new run for after
                t.text = text_before
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

                after_run = copy.deepcopy(run)
                after_t = after_run.find(f'{W}t')
                after_t.text = text_after
                after_t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

                run_idx = list(parent).index(run)
                parent.insert(run_idx + 1, after_run)

            elif text_before:
                t.text = text_before
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

            elif text_after:
                t.text = text_after
                t.set('{http://www.w3.org/XML/1998/namespace}space', 'preserve')

            else:
                # Entire run is within the match — remove it
                parent.remove(run)

        # Move del and ins elements to the correct position
        parent.remove(del_elem)
        parent.remove(ins_elem)
        parent.insert(insert_idx, ins_elem)
        parent.insert(insert_idx, del_elem)

        edits_applied += 1

    # Serialize the modified XML
    modified_xml = etree.tostring(tree, xml_declaration=True, encoding='UTF-8', standalone=True)

    # Rebuild the docx zip with the modified document.xml
    output = io.BytesIO()
    with ZipFile(output, 'w', ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            if item.filename == 'word/document.xml':
                zout.writestr(item, modified_xml)
            else:
                zout.writestr(item, zin.read(item.filename))

    zin.close()
    output.seek(0)
    return output.read(), edits_applied


def generate_redline(docx_bytes: bytes, user_prompt: str = "") -> tuple[bytes, list[dict], int]:
    """
    Full pipeline: analyze document, get edit instructions from Claude,
    apply as tracked changes, return the redlined .docx.

    Returns: (redlined_docx_bytes, edits_list, edits_applied_count)
    """
    if not user_prompt:
        user_prompt = "Review this legal document. Identify and fix: ambiguous language, missing protections, overbroad clauses, legal errors, missing defined terms, and any provisions that are one-sided or potentially unenforceable. Focus on the most impactful changes."

    paragraphs = extract_paragraphs(docx_bytes)

    if not paragraphs:
        raise ValueError("No text content found in the document.")

    edits = get_edit_instructions(paragraphs, user_prompt)
    redlined_bytes, applied = apply_tracked_changes(docx_bytes, edits)

    return redlined_bytes, edits, applied


def main():
    parser = argparse.ArgumentParser(
        description="Harvey Specterbot — AI-powered legal redline engine. "
                    "Produces Word tracked changes (w:ins/w:del) from Claude's edits."
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to the input .docx file",
    )
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        default=None,
        help="Path for the redlined output .docx (default: {input_name}_REDLINE.docx)",
    )
    parser.add_argument(
        "--instructions",
        type=str,
        default="",
        help='Custom review instructions, e.g. "focus on IP and indemnification clauses"',
    )

    args = parser.parse_args()

    input_path: Path = args.input.resolve()
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)
    if input_path.suffix.lower() != ".docx":
        print(f"Error: Input must be a .docx file, got: {input_path.suffix}", file=sys.stderr)
        sys.exit(1)

    # Determine output path
    if args.output:
        output_path: Path = args.output.resolve()
    else:
        output_path = input_path.parent / f"{input_path.stem}_REDLINE.docx"

    print(f"Reading: {input_path}")
    docx_bytes = input_path.read_bytes()

    print("Sending to Claude for legal review...")
    redlined_bytes, edits, applied = generate_redline(docx_bytes, args.instructions)

    # Write the redlined file
    output_path.write_bytes(redlined_bytes)

    # Copy to exchange dir for Mac access
    exchange_copy = None
    if EXCHANGE_DIR.exists():
        exchange_copy = EXCHANGE_DIR / output_path.name
        shutil.copy2(output_path, exchange_copy)

    # Print summary
    print()
    print("=" * 60)
    print("REDLINE SUMMARY")
    print("=" * 60)
    print(f"Edits requested by Claude : {len(edits)}")
    print(f"Edits applied (matched)   : {applied}")
    print(f"Edits skipped (no match)  : {len(edits) - applied}")
    print(f"Output saved to           : {output_path}")
    if exchange_copy:
        print(f"Copied to exchange        : {exchange_copy}")
    print("=" * 60)

    if edits:
        print()
        print("EDIT LOG:")
        for i, edit in enumerate(edits, 1):
            para = edit.get("paragraph_index", "?")
            reason = edit.get("reason", "")
            old = edit.get("old_text", "")[:60]
            new = edit.get("new_text", "")[:60]
            if len(edit.get("old_text", "")) > 60:
                old += "..."
            if len(edit.get("new_text", "")) > 60:
                new += "..."
            print(f"  [{i:2d}] Para {para}: \"{old}\" → \"{new}\"")
            if reason:
                print(f"        Reason: {reason}")


if __name__ == "__main__":
    main()
