---
name: magic-workspace-init
description: 'Initialize a MAGIC data processing workspace: directory scaffolding, Python environment verification, dependency installation, and LLM configuration. Use when starting a new data project or setting up the MAGIC environment for the first time.'
license: Apache-2.0
metadata:
  domain: data-science
  complexity: low
  requires_llm: false
  test_coverage: advisory  # structurally validated, not behaviorally tested (no executable tests by design)
  phase: 0
  supports_pipeline: false
  supports_generation: false
  eval_prompts: 3
  version: 0.1.0
  author: Votee MAGIC Team
  tags:
  - workspace
  - setup
  - init
  - environment
  - bootstrap
  - install
  dependencies: []
  when_to_use: 'When setting up a new workspace or installing dependencies. Trigger phrases: setup, initialize, create workspace, install dependencies, set up environment, init project.'
---

## When to Use

- Starting a new data processing project
- Setting up environment for MAGIC data skills for the first time
- User asks to "set up", "initialize", "bootstrap", or "install" the data workspace
- User needs help installing Python packages or DataDesigner
- Need to verify the environment is ready for data processing

**When NOT to Use:** Workspace already exists and is initialized. Tier 1 quick tasks (e.g., "clean these nulls") do not need full workspace scaffolding.

## Domain Knowledge

### What This Skill Does

This skill helps agents set up a complete data processing environment:

1. **Workspace scaffolding** — create the standard directory structure
2. **Environment verification** — check Python, required packages, optional tools
3. **Dependency installation** — install missing packages interactively
4. **LLM configuration** — set up API keys for synthesis workflows (optional)
5. **DataDesigner setup** — install and configure for LLM-based data generation (optional)

### Project Types and Workspace Shape

| Project Type | Workspace Shape | Notes |
|-------------|----------------|-------|
| One-off analysis | `data/` + `reports/` | Minimal — don't over-scaffold |
| ETL pipeline | Add `staging/` + `archive/` | For intermediate and archival storage |
| Multi-dataset | Per-dataset subdirs under `data/input/` | Keeps sources separate |
| Existing pipeline (dbt/Airflow) | Use `magic-workspace/` subdirectory | Coexist without conflict |

### Environment Setup

**Preferred method (uv — fast, no system pollution):**
```bash
uv venv .venv --python 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

**Alternative (standard venv):**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Alternative (conda):**
```bash
conda create -n magic python=3.12 -y
conda activate magic
pip install -r requirements.txt
```

**Important:** Always use a virtual environment. Never install into system Python. The workspace venv at `.venv/` is the standard location — all MAGIC skills expect this path.

### Required vs Optional Dependencies

| Package | Required By | Purpose | Tier |
|---------|-----------|---------|------|
| pandas>=2.0 | All skills | DataFrame operations | Required |
| numpy>=1.24 | All skills | Numeric computation | Required |
| scipy>=1.10 | statistical-analysis | Statistical tests | Required |
| matplotlib>=3.7 | visualization | Static charts | Required |
| seaborn>=0.12 | visualization | Statistical plots | Required |
| chardet>=5.0 | loading | Encoding detection | Required |
| openpyxl>=3.1 | loading | Excel file support | Required |
| pyarrow>=14.0 | loading | Parquet file support | Required |
| pyyaml>=6.0 | config | Config parsing | Required |
| plotly>=5.0 | visualization | Interactive charts | Recommended |
| pandera>=0.18 | validation | Schema validation | Recommended |
| jinja2>=3.1 | report-generation | Report templating | Recommended |
| tabulate>=0.9 | report-generation | Table formatting | Recommended |
| data-designer | synthesis | LLM-based generation via DataDesigner | Optional |
| tiktoken>=0.7 | synthesis | Token counting for cost estimation | Optional |
| rapidfuzz>=3.0 | cleaning, validation | Fuzzy column name suggestions | Optional |
| psutil>=5.9 | testing | Memory monitoring for deep evals | Optional |

### Rules

- **Environment verification before scaffolding**: Always verify Python environment before creating directories. A workspace with missing dependencies is worse than no workspace.
- **Idempotent, non-destructive**: Re-running init never overwrites existing content. Create only missing directories.
- **PAUSE before replacing existing environments**: If a virtual environment (.venv, conda env) already exists, show what will be removed (Python version, installed packages count) and ask for explicit confirmation before deleting. Never silently replace an existing environment — the user may have custom packages installed.
- **Never create `.env` files automatically**: Only the user creates these (contains API keys). Guide them to the right location.
- **Never init inside another MAGIC workspace**: Nested workspaces create ambiguous checkpoint paths. Init at the same level or in a sibling directory.
- **Use relative paths only**: Absolute paths break when workspace is moved or shared.
- **Match workspace complexity to task scope**: Quick one-off tasks don't need full scaffolding.

## Code Patterns

### Environment Verification

```python
import importlib
import subprocess
import sys

REQUIRED_PACKAGES = {
    "pandas": "pandas",
    "numpy": "numpy",
    "chardet": "chardet",
    "openpyxl": "openpyxl",
    "pyarrow": "pyarrow",
    "scipy": "scipy",
    "matplotlib": "matplotlib",
    "seaborn": "seaborn",
}

OPTIONAL_PACKAGES = {
    "plotly": "plotly",
    "pandera": "pandera",
    "jinja2": "Jinja2",
    "tabulate": "tabulate",
    "data_designer": "data-designer",
    "rapidfuzz": "rapidfuzz>=3.0.0,<4.0.0",
}

def verify_environment():
    """Check which packages are installed and which are missing."""
    installed, missing_required, missing_optional = [], [], []
    
    for module, pip_name in REQUIRED_PACKAGES.items():
        try:
            importlib.import_module(module)
            installed.append(module)
        except ImportError:
            missing_required.append(pip_name)
    
    for module, pip_name in OPTIONAL_PACKAGES.items():
        try:
            importlib.import_module(module)
            installed.append(module)
        except ImportError:
            missing_optional.append(pip_name)
    
    return {
        "python_version": sys.version,
        "installed": installed,
        "missing_required": missing_required,
        "missing_optional": missing_optional,
        "ready": len(missing_required) == 0,
    }

def install_packages(packages: list[str]):
    """Install packages using pip."""
    subprocess.run(
        [sys.executable, "-m", "pip", "install"] + packages,
        check=True,
    )
```

### Workspace Scaffolding

```python
from pathlib import Path

def init_workspace(workspace_path: str = "./workspace", project_type: str = "analysis"):
    """Create the standard MAGIC workspace directory structure."""
    root = Path(workspace_path)
    
    dirs = [
        "data/input",
        "data/checkpoints",
        "data/output",
        "logs",
        "reports",
        "charts",
    ]
    
    if project_type == "etl":
        dirs.extend(["staging", "archive"])
    
    created = []
    for d in dirs:
        path = root / d
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(str(d))
    
    return {"workspace": str(root), "created": created, "status": "fresh" if created else "complete"}
```

### DataDesigner Availability Check

```python
import importlib.util

def check_datadesigner():
    """Check DataDesigner installation and readiness."""
    spec = importlib.util.find_spec("data_designer")
    if spec is None:
        return {
            "installed": False,
            "install_cmd": "pip install data-designer",
            "required_for": "magic-data-synthesis (LLM-based generation)",
        }
    import data_designer
    return {
        "installed": True,
        "version": getattr(data_designer, "__version__", "unknown"),
    }
```

### LLM Configuration Check

```python
import os

def check_llm_config():
    """Check if LLM API keys are configured for synthesis workflows."""
    configs = {
        "google_api_key": bool(os.environ.get("GOOGLE_API_KEY")),
        "openai_api_key": bool(os.environ.get("OPENAI_API_KEY")),
        "anthropic_api_key": bool(os.environ.get("ANTHROPIC_API_KEY")),
    }
    any_configured = any(configs.values())
    
    return {
        "configured": any_configured,
        "providers": {k: v for k, v in configs.items() if v},
        "guidance": None if any_configured else (
            "Set GOOGLE_API_KEY for Gemini (recommended for synthesis) "
            "or OPENAI_API_KEY for OpenAI models. "
            "Add to shell profile or .env file."
        ),
    }
```

## Procedures [Interactive mode]

### Full Environment Setup (First Time)

Use this when the user is setting up MAGIC skills for the first time.

**Step 1 — Verify Python environment**

```python
env = verify_environment()
print(f"Python: {env['python_version']}")
if env['missing_required']:
    print(f"Missing required packages: {env['missing_required']}")
```

If packages are missing, ask the user how they want to install:
- `pip install <packages>` (default)
- `conda install <packages>` (if conda environment detected)
- `uv pip install <packages>` (if uv detected)

**PAUSE**: Show missing packages and ask user to confirm installation method.

**Step 2 — Install missing required packages**

```bash
pip install pandas numpy chardet openpyxl pyarrow scipy matplotlib seaborn
```

**Step 3 — Install recommended optional packages**

```bash
pip install plotly pandera jinja2 tabulate
```

**PAUSE**: Ask if user wants optional packages. Explain what each enables.

**Step 4 — DataDesigner setup (if user needs synthesis)**

```bash
pip install data-designer
```

Then verify:
```python
python -c "from data_designer import DataDesigner; print('DataDesigner ready')"
```

**Step 5 — LLM API key configuration (if user needs synthesis)**

Guide user to set up API keys:
```bash
# For Gemini (recommended — fast and cost-effective)
export GOOGLE_API_KEY="your-key-here"

# Or for OpenAI
export OPENAI_API_KEY="your-key-here"
```

Suggest adding to shell profile (`~/.zshrc`, `~/.bashrc`) for persistence.

**Step 6 — Create workspace**

```python
workspace = init_workspace("./workspace")
```

**Step 7 — Verify everything works**

Run a quick smoke test:
```python
import pandas as pd
df = pd.DataFrame({"test": [1, 2, 3]})
df.to_csv("workspace/data/input/test.csv", index=False)
loaded = pd.read_csv("workspace/data/input/test.csv")
assert len(loaded) == 3
print("Environment ready!")
```

### Quick Workspace Init (Existing Environment)

For users who already have packages installed:

1. Run `verify_environment()` — confirm all required packages present
2. Run `init_workspace()` with appropriate project type
3. Report status to user

### Adding DataDesigner Later

If user starts with basic skills and later wants synthesis:

1. `pip install data-designer`
2. Set `GOOGLE_API_KEY` or `OPENAI_API_KEY`
3. Verify: `data-designer validate` on a template
4. Synthesis skill is now available

## Workspace Directory Convention

```
workspace/                          <- Root (user-configurable)
├── data/
│   ├── input/                      <- Original input files
│   ├── checkpoints/                <- Intermediate results (ckpt_NN_*.csv)
│   └── output/                     <- Final processed data
├── logs/                           <- Profiling results, validation reports
├── reports/                        <- Generated reports (markdown)
├── charts/                         <- Generated visualizations (PNG, SVG)
└── configs/                        <- Agent configs, synthesis configs (if needed)
```

## Default Output Paths by Skill

| Skill | Default Output Path |
|-------|-------------------|
| magic-data-loading | `data/input/` (loaded files) |
| magic-data-profiling | `logs/` (quality scores, distributions) |
| magic-data-cleaning | `data/checkpoints/` (cleaned data) |
| magic-data-transformation | `data/checkpoints/` (transformed data) |
| magic-data-validation | `logs/` (validation reports) |
| magic-data-exploration | `logs/` (pattern detection results) |
| magic-statistical-analysis | `logs/` (stats results) |
| magic-data-synthesis | `data/output/` (synthesized data) |
| magic-data-visualization | `charts/` (PNG, SVG) |
| magic-report-generation | `reports/` (markdown reports) |

## Self-Healing

| Error | Likely Cause | Fix |
|-------|-------------|-----|
| `ModuleNotFoundError: pandas` | Required packages not installed | `pip install pandas numpy chardet openpyxl pyarrow scipy matplotlib seaborn` |
| `ModuleNotFoundError: data_designer` | DataDesigner not installed | `pip install data-designer` (only needed for synthesis) |
| Permission denied | Directory not writable | Check permissions on target path |
| Nested workspace detected | Init inside another workspace | Move to sibling directory or parent level |
| `GOOGLE_API_KEY` not set | LLM not configured | Set API key in shell profile or .env |

## Reference Guides

| Topic | File | Load When |
|-------|------|-----------|
| Project patterns | `references/project_patterns.md` | Setting up workspace for a specific project type |
