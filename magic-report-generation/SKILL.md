---
name: magic-report-generation
description: Assemble data analysis findings into structured Markdown reports with mandatory sections (Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps). Use when creating the final deliverable report after analysis is complete, generating an executive summary, converting findings JSON into a formatted document, or producing ckpt_07_report.md. Supports standard, executive, and technical templates.
license: Apache-2.0
compatibility: Python 3.12+
metadata:
  domain: data-science
  complexity: low
  requires_llm: true
  phase: 1
  supports_pipeline: true
  supports_generation: true
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - data-science
  - reporting
  - markdown
  - documentation
  scripts:
  - scripts/generate_report.py
  - scripts/format_table.py
  - scripts/validate_report.py
  dependencies:
  - pandas
  - jinja2
  - tabulate
  when_to_use: 'When assembling findings into a structured report. Trigger phrases: report, summary report, generate report, write up findings, executive summary, document results, final deliverable.'
---

## Natural Language Triggers

Activate this skill when the user says things like:
- "generate a report" / "create the final report"
- "write up the findings" / "summarize the analysis"
- "format this as a report" / "make an executive summary"

These produce the SAME behavior as the report generation workflow.

## When to Use

- Need to assemble analysis results into a structured report
- Need to format DataFrames as readable tables
- After magic-statistical-analysis and magic-data-visualization are complete

**When NOT to Use:** Use magic-statistical-analysis for computing results; use magic-data-visualization for creating charts.

## Data Processing Expertise

### Thinking

Before assembling any report, ask:
- **Who is the audience?** -- Technical audience wants methodology detail and statistical backing; executive audience wants the key number and the decision it implies. Choose template accordingly: `technical`, `executive`, or `standard`. Getting this wrong means the report is either unread (too detailed for executives) or untrusted (too shallow for data teams).
- **What decision does this inform?** -- Every report should answer "so what?" If you cannot name the decision, the report is a data dump, not a deliverable. Connect findings to actionable next steps.
- **What is the one key finding?** -- If the reader remembers only one thing, what should it be? That finding goes in the first paragraph. If you cannot identify a single lead finding, the analysis may not be finished.
- **Do the findings contradict each other?** -- Different analyses on the same data can produce conflicting conclusions (e.g., mean suggests growth but median suggests decline). Never hide contradictions. Present both findings side by side with methodology context: "Analysis A (mean-based) suggests X while Analysis B (median-based) suggests Y -- the difference is due to outlier sensitivity."
- **What baseline gives the numbers meaning?** -- "12% churn rate" is meaningless without "up from 8% last quarter" or "industry average is 15%." Every metric needs comparison context. If no baseline exists, say so explicitly.
- **How uncertain are these results?** -- Quantify uncertainty with ranges, confidence intervals, or sample sizes. Never present naked numbers. A finding based on N=50 is qualitatively different from N=50,000.

### Rules

- **Lead with the "so what"**: The key finding goes in the first paragraph. If the reader stops there, they should know the main result and its implication.
- **Baseline comparison for every metric**: Every quantified claim must include comparison context -- prior period, industry benchmark, or expected value. If no baseline exists, state "No historical baseline available."
- **Quantify uncertainty always**: Ranges, confidence intervals, sample sizes. "Revenue grew 15% (95% CI: 12-18%, N=2,400 transactions)" not "Revenue grew 15%."
- **Separate facts from interpretation**: "Revenue increased 15%" is a fact. "Revenue growth indicates market expansion" is interpretation. Label clearly which is which.
- **Findings prioritization**: Order findings by business impact, not by order of discovery. The finding that changes a decision comes first; the confirming detail comes last.
- **6 mandatory sections**: Every standard report must include Summary, Data Provenance, Methodology, Key Findings, Caveats, and Next Steps. Executive template may condense but must not omit Caveats.
- **Contradictory findings handling**: When analyses conflict, present both with methodology context. Do not resolve contradictions by choosing one -- present the evidence and let the reader (or domain expert) decide.
- **When to use LLM**: Report narrative generation is a natural LLM task -- synthesizing findings into readable prose, adapting tone for audience, generating executive summaries from technical detail. But data tables and statistics must come from code. Use both: code produces the numbers, LLM produces the story around them. Hand off to `magic-data-synthesis` only for content transformation (e.g., translating a report to another language).

### Constraints

- MUST include all 6 mandatory sections: Summary, Data Provenance, Methodology, Key Findings, Caveats, Next Steps
- MUST use uncertainty language in findings ("suggests", "appears to", "may indicate") unless backed by strong statistical evidence (p < 0.05 with adequate sample size)
- MUST embed charts with Markdown image syntax and descriptive captions
- MUST include at least one caveat even for clean data -- "Analysis is limited to the provided dataset" at minimum
- MUST NOT use certainty language ("proves", "definitively", "always") for observational data
- MUST NOT omit Data Provenance -- readers need to know what data backs the claims
- MUST NOT present raw statistical output without narrative interpretation
- NEVER skip Caveats even for "clean" data -- stakeholders treat caveat-free reports as overconfident. When findings are later challenged, the absence of caveats destroys credibility retroactively.
- NEVER lead with methodology for executive audiences -- executives who encounter methodology in paragraph 1 stop reading. The decision and the number that drives it must be the first sentence. Use the `executive` template.
- NEVER present a single number without a baseline -- "12% churn rate" is meaningless without comparison context. Every metric needs a reference point.
- NEVER hide contradictory findings -- cherry-picking results that support a narrative while suppressing conflicting evidence is the fastest way to lose trust. Present all findings.

## Seed Patterns

### Report assembly from findings JSON
```python
import json
from pathlib import Path
from datetime import datetime

def assemble_report(findings_path: str, template: str = "standard") -> str:
    with open(findings_path) as f:
        findings = json.load(f)

    sections = []
    sections.append(f"# {findings.get('title', 'Data Analysis Report')}\n")
    sections.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d')}\n")

    # Lead with key finding in summary
    lead = findings["key_findings"][0]
    sections.append(f"## Summary\n\n{lead['description']}\n")

    # Data Provenance
    ds = findings["data_source"]
    sections.append(f"## Data Provenance\n\n"
                    f"**Source:** {ds['file']}  \n"
                    f"**Rows:** {ds['rows']} | **Columns:** {ds['columns']}\n")

    # Methodology
    sections.append(f"## Methodology\n\n{findings.get('methodology', 'See analysis scripts.')}\n")

    # Key Findings -- ordered by impact
    sections.append("## Key Findings\n")
    for i, f_ in enumerate(findings["key_findings"], 1):
        evidence = f"  *Evidence:* {f_['evidence']}" if f_.get("evidence") else ""
        sections.append(f"{i}. **{f_['title']}**\n   {f_['description']}\n{evidence}\n")

    # Caveats -- always at least one
    caveats = findings.get("caveats", ["Analysis is limited to the provided dataset."])
    sections.append("## Caveats and Limitations\n")
    for c in caveats:
        sections.append(f"- {c}")

    # Next Steps
    sections.append("\n## Next Steps\n")
    for s in findings.get("next_steps", ["Validate findings with domain experts."]):
        sections.append(f"- {s}")

    return "\n\n".join(sections)
```

### Table formatting with truncation and number formatting
```python
import pandas as pd

def format_table(df: pd.DataFrame, max_rows: int = 20, max_cols: int = 10) -> str:
    display = df.head(max_rows).iloc[:, :max_cols].copy()
    for col in display.columns:
        if pd.api.types.is_numeric_dtype(display[col]):
            display[col] = display[col].apply(
                lambda v: f"{v:,.2f}" if isinstance(v, float) else f"{v:,}" if isinstance(v, int) and abs(v) >= 1000 else str(v)
            )
        else:
            display[col] = display[col].astype(str).str[:50]

    lines = ["| " + " | ".join(str(c) for c in display.columns) + " |"]
    lines.append("| " + " | ".join(["---"] * len(display.columns)) + " |")
    for _, row in display.iterrows():
        lines.append("| " + " | ".join(str(v) for v in row) + " |")
    if len(df) > max_rows:
        lines.append(f"\n*... and {len(df) - max_rows} more rows*")
    return "\n".join(lines)
```

### Section generation with audience adaptation
```python
def generate_section(section_name: str, content: dict, template: str) -> str:
    """Generate a single report section adapted to the template audience."""
    if template == "executive" and section_name == "methodology":
        # Executives get one-line methodology, not the full detail
        return f"## Methodology\n\n{content.get('one_liner', 'Standard statistical analysis.')}\n"

    if template == "technical" and section_name == "findings":
        # Technical gets evidence blocks with statistics
        lines = [f"## {content['title']}\n"]
        for f in content["items"]:
            lines.append(f"### {f['title']}\n\n{f['description']}\n")
            if f.get("statistics"):
                lines.append(f"```\n{f['statistics']}\n```\n")
            if f.get("evidence"):
                lines.append(f"**Evidence:** {f['evidence']}\n")
        return "\n".join(lines)

    # Standard: balanced detail
    lines = [f"## {content.get('heading', section_name.title())}\n"]
    for item in content.get("items", []):
        lines.append(f"- {item}")
    return "\n".join(lines)
```

## Reference Scripts

> Scripts fall into three categories: **callable tools** (call directly via CLI),
> **scriptable tools** (call directly for standard use, or read + adapt for advanced use),
> and **reference implementations** (always read + adapt).

**Scriptable tools** -- call directly for standard use, read + adapt for advanced:

| Script | Tier | Standard CLI usage | When to customize |
|--------|------|-------------------|-------------------|
| `format_table.py` | A | `python3 format_table.py stats.csv table.md` | `--format html\|latex` for non-Markdown; `--max_rows 50`, `--max_cols 15` to adjust truncation |
| `validate_report.py` | B | `python3 validate_report.py report.md validation.json --template standard` | `--template` MUST match generation template (default is `technical` which may mismatch) |

**Reference implementations** -- read patterns, write custom code:

| Script | Demonstrates | Key pattern |
|--------|-------------|-------------|
| `generate_report.py` | Jinja2 template rendering for structured findings | Requires findings JSON with specific schema (`summary`, `key_findings`, `data_source`, `caveats`); agents must read source to construct valid input |

Scripts accept positional arguments (`input_file output_file`), not `--input` flags.

## Checkpointing

Checkpointing is a judgment call — save intermediate results when the cost of re-running the preceding step justifies persisting the result.

**For report generation specifically:** The report IS the final deliverable — always save it.

| Signal | Checkpoint? | Reasoning |
|--------|-------------|-----------|
| After report assembly | **Always** | Report is the final pipeline deliverable |
| After findings JSON compilation | **Yes** | Structured findings feed multiple report templates |
| After executive summary generation | **Yes** | Summary may be needed independently |

**Suggested names:** `analysis_report.md`, `executive_summary.md`, `findings.json`, `ckpt_07_report.md`

Include provenance metadata: source data file, analysis timestamp, template used, section count.

**Save pattern:**
```python
import json, datetime
from pathlib import Path

def save_checkpoint(df, path: str, metadata: dict = None) -> str:
    """Save data + provenance metadata. Use at phase boundaries."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix == ".parquet":
        df.to_parquet(p, index=False)
    elif p.suffix == ".jsonl":
        df.to_json(p, orient="records", lines=True, force_ascii=False)
    else:
        df.to_csv(p, index=False)
    meta = {
        "rows": len(df), "cols": list(df.columns),
        "saved_at": datetime.datetime.utcnow().isoformat(),
        **(metadata or {}),
    }
    p.with_suffix(".meta.json").write_text(
        json.dumps(meta, indent=2, ensure_ascii=False)
    )
    return str(p)
```

## Self-Healing

If report generation fails:
1. Read error JSON -- check `suggestion` field
2. Read script source to understand the failure mode
3. Inspect the findings JSON structure
4. Common fixes below

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| Missing findings fields | Incomplete findings JSON | Add missing sections with defaults; at minimum: `summary`, `key_findings`, `data_source`, `caveats` |
| Chart path not found | Charts not generated yet | Run magic-data-visualization first, or remove chart references |
| Contradictory findings | Different methods produce conflicting conclusions | Present BOTH findings with methodology context. Note: "Analysis A suggests X while Analysis B suggests Y -- the difference may be due to [methodology/scope/assumptions]." |
| Insufficient data | Too few rows or incomplete analyses | Generate a "Preliminary Findings" report using the `executive` template. Clearly state limitations. |
| Validation fails | Missing mandatory sections | Check `validate_report.py` output for `sections_missing` and add them |
| Word count out of range | Report too short or verbose | Adjust detail level; executive template condenses, technical expands |

## Format Ambiguity Guide

When report structure is ambiguous, think through these scenarios:

| Situation | What Might Go Wrong | Recommended Approach |
|-----------|--------------------|--------------------|
| No explicit audience specified | Wrong template choice, wrong detail level | Default to `standard` template; ask if interactive |
| Findings from multiple analysis phases | Inconsistent terminology, duplicated findings | Consolidate findings; use consistent metric names across sections |
| Missing baseline data | Numbers without context appear meaningless | State "No historical baseline available" rather than presenting naked metrics |
| Very few findings (1-2) | Report feels thin, lacks substance | Focus on depth over breadth; expand evidence and caveats for each finding |
| Contradictory statistical results | Cherry-picking risk, credibility loss | Present all results with methodology explanation for the divergence |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Documentation standards | `references/documentation_standards.md` | MANDATORY -- before writing report content |
| Storytelling patterns | `references/storytelling_patterns.md` | MANDATORY -- before planning report structure and presentation |

**Do NOT Load** reference guides if generating a simple table format or checkpoint -- they are for full report assembly only.

## Interactive Mode [Optional]

_For agents working interactively with a user. Pipeline code generation skips this section._

### PAUSE Gates
- **PAUSE** after assembling the report outline: present template choice (standard/executive/technical), sections to include, key findings to highlight, charts to embed, and proposed caveats. Ask user to confirm structure before generating the full report.

### Workspace Integration
- Update `workspace_state.md` with report generation results (template used, word count, sections included).
- Log report decisions in `logs/analysis_journal.md`.
