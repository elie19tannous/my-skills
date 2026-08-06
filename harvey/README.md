# Harvey Specterbot v2 — AI Law Firm for Claude Code

A multi-agent legal analysis skill for [Claude Code](https://claude.ai/code). Invoke `/harvey` and get a full law firm: automatic triage, parallel specialist analysis, managing partner synthesis, case law research, patent search, and document redlining.

## What It Does

- **Contract Review** — Clause-by-clause analysis, risk matrices, negotiation positions
- **Compliance Audits** — HIPAA, privacy, regulatory gap analysis with remediation plans
- **Legal Research** — IRAC-framework memos with live case law from CourtListener (400M+ opinions)
- **Patent Search** — Google Patents integration for patent landscape analysis
- **Document Redlining** — Generates genuine Word tracked changes (w:ins/w:del revision marks)
- **IP & Employment Review** — IP ownership, non-compete enforceability, worker classification
- **Document Drafting** — NDAs, MSAs, employment agreements with proper legal conventions

## The Firm

| Role | What They Do |
|------|-------------|
| **Paralegal** | Intake, triage, routes to the right team |
| **Legal Researcher** | CourtListener API, Google Patents, statute lookup |
| **Contract Specialist** | Contract analysis, risk matrices, negotiation strategy |
| **Compliance Counsel** | HIPAA, privacy, regulatory compliance matrices |
| **Senior Associate** | IRAC analysis, corporate governance, cascade analysis |
| **IP & Employment Specialist** | Patents, trademarks, non-competes, classification |
| **Managing Partner (Harvey)** | Synthesizes everything, prioritizes, delivers |

## Installation

Copy the `harvey/` directory into your Claude Code skills folder:

```bash
# Clone
git clone https://github.com/xkaluv/harvey-specterbot.git

# Copy to Claude Code skills
cp -r harvey-specterbot ~/.claude/skills/harvey
```

Or symlink it:

```bash
git clone https://github.com/xkaluv/harvey-specterbot.git ~/harvey-specterbot
ln -s ~/harvey-specterbot ~/.claude/skills/harvey
```

## Configuration

### CourtListener (case law research)
Get a free API key at [courtlistener.com/help/api](https://www.courtlistener.com/help/api/) and set it:

```bash
export COURTLISTENER_API_TOKEN=your_token_here
# Or add to a .env file in your project directory
```

### Redline Engine (Word tracked changes)
Requires Python packages:

```bash
pip install lxml python-docx anthropic
```

### Output Directory (optional)
Set `HARVEY_EXCHANGE_DIR` to automatically copy output files to a shared folder:

```bash
export HARVEY_EXCHANGE_DIR=/path/to/shared/folder
```

## Usage

```
/harvey "Review this SaaS agreement"
/harvey "What are the non-compete rules in California?"
/harvey "Find cases about HIPAA breach notification for hospitals"
/harvey "Find patents related to telehealth prescription management"
/harvey redline contract.docx
/harvey "Draft an NDA for a software consulting engagement"
```

## Voice Protocol

Harvey operates in two modes:

- **Internal** (status updates to you) — Harvey Specter energy. Confident, sharp, a little dangerous.
- **External** (all deliverables) — Impeccable legal writing. Zero personality. Pure substance.

The snark stays between you and Harvey. Documents are always professional.

## File Structure

```
harvey/
├── SKILL.md                          # Orchestration brain (380+ lines)
├── references/
│   ├── guardrails.md                 # Mandatory rules, ethics, quality standards
│   ├── methodology-irac.md           # IRAC analysis framework
│   ├── methodology-drafting.md       # Document drafting conventions
│   ├── pa-contracts.md               # Contract law knowledge base
│   ├── pa-corporate.md               # Corporate governance
│   ├── pa-healthcare.md              # HIPAA, Stark, AKS, telehealth
│   ├── pa-regulatory.md              # FTC, state consumer protection, industry regs
│   ├── pa-privacy.md                 # CCPA, GDPR, state privacy laws
│   ├── pa-employment.md              # Employment law, non-competes, classification
│   ├── pa-ip.md                      # Patents, trademarks, copyright, trade secrets
│   └── legal-research-sources.md     # Research methodology and data sources
└── scripts/
    ├── legal_research.py             # CourtListener + Google Patents CLI
    └── redline_engine.py             # Word tracked changes generator
```

## Requirements

- [Claude Code](https://claude.ai/code) (CLI, desktop, or web)
- Python 3.10+ (for scripts)
- `lxml`, `python-docx`, `anthropic` (pip packages, for redlining)
- CourtListener API key (free, for case law research)

## License

MIT
