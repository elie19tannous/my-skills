"""Interaction utilities for magic-linguistic-* skill suite.

Adapted from magic-agent-skills shared utilities.
Standalone copy (no cross-repo import) per ralplan iter-2 Decision 2 (Q5 resolved).

Provides helpers for collaborative-mode user prompts: option formatting,
decision recording, and phase-indicator rendering. Linguistic-domain specific
helpers (e.g. resource-class summary lines) live here, not upstream.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Iterable


@dataclass
class Option:
    """A single user-presentable option."""

    label: str
    description: str = ""
    recommended: bool = False
    metadata: dict = field(default_factory=dict)


def format_options(options: Iterable[Option]) -> str:
    """Render an Option list as numbered markdown."""
    lines: list[str] = []
    for i, opt in enumerate(options, start=1):
        suffix = " (Recommended)" if opt.recommended else ""
        lines.append(f"{i}. **{opt.label}**{suffix}")
        if opt.description:
            lines.append(f"   - {opt.description}")
    return "\n".join(lines)


def phase_indicator(
    phase: str,
    language: str | None = None,
    iso: str | None = None,
    resource_class: int | None = None,
    skills_routed: Iterable[str] | None = None,
) -> str:
    """Render the canonical phase-indicator line.

    Format:
        [Phase: <Scope|Acquire|Analyze|Evaluate|Release> | Language: <name> (<iso>)
         | Resource Class: <n> | Skills routed: <a, b>]
    """
    parts = [f"Phase: {phase}"]
    if language:
        lang_part = f"Language: {language}"
        if iso:
            lang_part += f" ({iso})"
        parts.append(lang_part)
    if resource_class is not None:
        parts.append(f"Resource Class: {resource_class}")
    if skills_routed:
        parts.append(f"Skills routed: {', '.join(skills_routed)}")
    return "[" + " | ".join(parts) + "]"


def record_decision(
    workspace_state_path: str,
    title: str,
    options_considered: Iterable[str],
    chosen: str,
    rationale: str = "",
    follow_up: str = "",
) -> dict:
    """Append a decision entry to workspace_state.md (markdown) AND return the structured form.

    The caller is responsible for the actual file append (this util just shapes the entry
    so multiple specialists produce identical structure).
    """
    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "title": title,
        "options_considered": list(options_considered),
        "chosen": chosen,
        "rationale": rationale,
        "follow_up": follow_up,
    }


def render_decision_md(decision: dict) -> str:
    """Render a decision dict (from record_decision) as markdown for workspace_state.md."""
    lines = [
        f"### Decision: {decision['title']}",
        f"- **Timestamp:** {decision['timestamp']}",
        f"- **Options considered:** {', '.join(decision['options_considered'])}",
        f"- **Chosen:** {decision['chosen']}",
    ]
    if decision.get("rationale"):
        lines.append(f"- **Rationale:** {decision['rationale']}")
    if decision.get("follow_up"):
        lines.append(f"- **Follow-up:** {decision['follow_up']}")
    return "\n".join(lines) + "\n"


def safe_json_dump(obj, path: str) -> None:
    """Write JSON with stable key ordering (for scores.json and other observability artifacts)."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True, ensure_ascii=False)
        f.write("\n")
