"""Findings presentation for magic-linguistic-* skill suite.

Adapted from magic-agent-skills shared utilities with a
linguistic-domain ISSUE_SKILL_MAP. Standalone copy.

Findings flow: a specialist skill detects an issue, calls render_finding() with
the issue type + evidence + severity, and the orchestrator's findings command
aggregates them via group_findings_by_severity().
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["HIGH", "MEDIUM", "LOW"]


# Maps a finding's `issue_type` to the skill that owns the recommended fix.
# Used by the orchestrator to attribute findings and route auto-fixes.
ISSUE_SKILL_MAP: dict[str, str] = {
    # scripts / orthography
    "confusable_chars": "magic-linguistic-scripts",
    "mixed_script": "magic-linguistic-scripts",
    "missing_diacritics": "magic-linguistic-scripts",
    "nfkc_overcollapse": "magic-linguistic-scripts",
    "encoding_corruption": "magic-linguistic-scripts",
    "byte_order_mark": "magic-linguistic-scripts",
    # tokenize
    "high_fertility": "magic-linguistic-tokenize",
    "vocab_oov_explosion": "magic-linguistic-tokenize",
    "byte_fallback_missing": "magic-linguistic-tokenize",
    "subword_regularization_off": "magic-linguistic-tokenize",
    # corpus
    "register_imbalance": "magic-linguistic-corpus",
    "duplicate_documents": "magic-linguistic-corpus",
    "wrong_language_id": "magic-linguistic-corpus",
    "low_coverage_glotlog": "magic-linguistic-corpus",
    # bitext
    "alignment_below_margin": "magic-linguistic-bitext",
    "bible_only_domain": "magic-linguistic-bitext",
    "translationese": "magic-linguistic-bitext",
    # transfer
    "wrong_transfer_source": "magic-linguistic-transfer",
    "vocab_extension_needed": "magic-linguistic-transfer",
    "lora_rank_too_low": "magic-linguistic-transfer",
    "catastrophic_forgetting": "magic-linguistic-transfer",
    # ethics
    "license_violation": "magic-linguistic-ethics",
    "sacred_text_present": "magic-linguistic-ethics",
    "missing_attribution": "magic-linguistic-ethics",
    "fpic_not_obtained": "magic-linguistic-ethics",
    # eval
    "eval_contamination": "magic-linguistic-eval",
    "bleu_on_mrl": "magic-linguistic-eval",
    "comet_coverage_gap": "magic-linguistic-eval",
    "register_eval_gap": "magic-linguistic-eval",
    # speech
    "ipa_normalization_missing": "magic-linguistic-speech",
    "tone_annotation_missing": "magic-linguistic-speech",
    # annotation
    "iaa_below_threshold": "magic-linguistic-annotate",
    "annotator_drift": "magic-linguistic-annotate",
    "guideline_ambiguity": "magic-linguistic-annotate",
    # syntax / semantics / discourse / morph
    "ud_treebank_missing": "magic-linguistic-syntax",
    "agreement_probe_failure": "magic-linguistic-syntax",
    "wordnet_synset_gap": "magic-linguistic-semantics",
    "frame_coverage_gap": "magic-linguistic-semantics",
    "rst_relation_skew": "magic-linguistic-discourse",
    "zero_anaphora_drop": "magic-linguistic-discourse",
    "morphology_complexity_unhandled": "magic-linguistic-morph",
    "fst_coverage_gap": "magic-linguistic-morph",
    # scope
    "ambiguous_language_name": "magic-linguistic-scope",
    "missing_glotlog_id": "magic-linguistic-scope",
    "wrong_resource_class": "magic-linguistic-scope",
}


@dataclass
class Finding:
    issue_type: str
    severity: Severity
    summary: str
    evidence: str = ""
    recommended_action: str = ""
    auto_fixable: bool = False
    extra: dict = field(default_factory=dict)

    @property
    def owner_skill(self) -> str:
        return ISSUE_SKILL_MAP.get(self.issue_type, "magic-linguistic-orchestrator")


def render_finding(finding: Finding) -> str:
    """Render a Finding as markdown for the findings command."""
    auto = " (auto-fix available)" if finding.auto_fixable else ""
    lines = [
        f"- **[{finding.severity}] {finding.summary}** {auto}",
        f"  - Owner skill: `{finding.owner_skill}` (issue type: `{finding.issue_type}`)",
    ]
    if finding.evidence:
        lines.append(f"  - Evidence: {finding.evidence}")
    if finding.recommended_action:
        lines.append(f"  - Recommended action: {finding.recommended_action}")
    return "\n".join(lines)


def group_findings_by_severity(findings: list[Finding]) -> dict[Severity, list[Finding]]:
    out: dict[Severity, list[Finding]] = {"HIGH": [], "MEDIUM": [], "LOW": []}
    for f in findings:
        out[f.severity].append(f)
    return out


def render_findings_report(findings: list[Finding]) -> str:
    """Render a full findings report (used by /linguistic:findings)."""
    grouped = group_findings_by_severity(findings)
    out: list[str] = ["# Findings", ""]
    for sev in ("HIGH", "MEDIUM", "LOW"):
        items = grouped[sev]
        out.append(f"## {sev} ({len(items)})")
        if not items:
            out.append("_(none)_")
        else:
            out.extend(render_finding(f) for f in items)
        out.append("")
    return "\n".join(out)
