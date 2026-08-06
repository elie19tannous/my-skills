#!/usr/bin/env python3
"""Project pipeline orchestrator template.

Copy this file to workspace/pipelines/<name>/pipeline.py and customize:
  1. Fill in the STEPS list with your step modules
  2. Set CONFIG values for your pipeline
  3. Import your step modules at the top

Usage:
  python3 pipeline.py                     # run all, skip completed
  python3 pipeline.py --from-step clean   # resume from 'clean'
  python3 pipeline.py --steps clean deliver  # only these steps
  python3 pipeline.py --force             # ignore checkpoints, re-run all
  python3 pipeline.py --status            # show what's done/pending
  python3 pipeline.py --config config_v2.py  # use alternate config
"""
import argparse
import importlib
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# AGENT: customize this section
# ---------------------------------------------------------------------------

# Import your step modules here:
# from steps import step_01_download, step_02_profile, step_03_clean

# Each entry: (step_name, step_module_run_fn, output_filename, input_filename)
# - output_filename: checkpoint file this step produces (None if no file output)
# - input_filename: checkpoint file this step reads (None if first step or no file input)
STEPS = [
    # ("download",  step_01_download.run,  "01_downloaded.parquet", None),
    # ("profile",   step_02_profile.run,   "02_quality.json",       "01_downloaded.parquet"),
    # ("clean",     step_03_clean.run,     "03_cleaned.parquet",    "01_downloaded.parquet"),
    # ("validate",  step_04_validate.run,  "04_validated.json",     "03_cleaned.parquet"),
    # ("deliver",   step_05_deliver.run,   None,                    "03_cleaned.parquet"),
]

# Pipeline configuration — edit for different runs
CONFIG = {
    "checkpoint_dir": Path(__file__).parent / "../../data/checkpoints",
    # Add your pipeline-specific config here:
    # "dataset": "org/name",
    # "output_repo": "org/output",
}

# ---------------------------------------------------------------------------
# Orchestration logic — do not modify unless extending
# ---------------------------------------------------------------------------


def parse_args():
    parser = argparse.ArgumentParser(description="Pipeline orchestrator")
    parser.add_argument("--from-step", type=str, help="Resume from this step (skip earlier steps)")
    parser.add_argument("--steps", nargs="+", help="Run only these steps")
    parser.add_argument("--force", action="store_true", help="Ignore checkpoints, re-run everything")
    parser.add_argument("--status", action="store_true", help="Show step completion status and exit")
    parser.add_argument("--config", type=str, help="Path to alternate config module")
    return parser.parse_args()


def load_config(config_path: str | None) -> dict:
    if config_path:
        spec = importlib.util.spec_from_file_location("config", config_path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return {k: getattr(mod, k) for k in dir(mod) if not k.startswith("_")}
    return CONFIG


def get_checkpoint_path(config: dict, filename: str | None) -> Path | None:
    if filename is None:
        return None
    ckpt_dir = Path(config.get("checkpoint_dir", "data/checkpoints"))
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    return ckpt_dir / filename


def step_is_done(config: dict, output_filename: str | None) -> bool:
    # Steps with output_file=None (e.g., delivery) always re-run by design
    if output_filename is None:
        return False
    path = get_checkpoint_path(config, output_filename)
    return path is not None and path.exists()


def show_status(config: dict):
    print("Pipeline status:")
    for name, _, output_file, _ in STEPS:
        done = step_is_done(config, output_file)
        mark = "done" if done else "pending"
        path = get_checkpoint_path(config, output_file)
        size = ""
        if done and path and path.exists():
            size = f" ({path.stat().st_size / 1024:.0f} KB)"
        print(f"  {'[x]' if done else '[ ]'} {name}{size}")


def run_pipeline(args):
    config = load_config(args.config)

    if args.status:
        show_status(config)
        return

    step_names = [s[0] for s in STEPS]

    if args.from_step:
        if args.from_step not in step_names:
            print(f"Error: unknown step '{args.from_step}'. Available: {step_names}")
            sys.exit(1)

    if args.steps:
        for s in args.steps:
            if s not in step_names:
                print(f"Error: unknown step '{s}'. Available: {step_names}")
                sys.exit(1)

    started = not bool(args.from_step)
    run_log = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "steps_run": [],
        "steps_skipped": [],
        "row_counts": {},
        "duration_seconds": 0,
        "outcome": "in_progress",
    }
    t0 = time.time()

    for name, run_fn, output_file, input_file in STEPS:
        if args.from_step and name == args.from_step:
            started = True
        if not started:
            run_log["steps_skipped"].append(name)
            print(f"[{name}] skip — before --from-step")
            continue

        if args.steps and name not in args.steps:
            run_log["steps_skipped"].append(name)
            continue

        if not args.force and step_is_done(config, output_file):
            run_log["steps_skipped"].append(name)
            print(f"[{name}] skip — checkpoint exists")
            continue

        input_path = get_checkpoint_path(config, input_file)
        output_path = get_checkpoint_path(config, output_file)

        try:
            print(f"[{name}] running...")
            result = run_fn(
                str(input_path) if input_path else None,
                str(output_path) if output_path else None,
                config,
            )
            run_log["steps_run"].append(name)
            if isinstance(result, dict):
                for k in ("rows_out", "row_count", "rows"):
                    if k in result:
                        run_log["row_counts"][name] = result[k]
                        break
            print(f"[{name}] done — {result}")
        except Exception as exc:
            run_log["steps_run"].append(name)
            run_log["outcome"] = "error"
            run_log["error"] = f"step '{name}': {type(exc).__name__}: {exc}"
            run_log["duration_seconds"] = round(time.time() - t0, 1)
            _save_log(config, run_log)
            print(f"\n[{name}] ERROR: {exc}")
            print(f"\nPipeline stopped at step '{name}'. Previous checkpoints preserved.")
            sys.exit(1)

    run_log["outcome"] = "success"
    run_log["duration_seconds"] = round(time.time() - t0, 1)
    _save_log(config, run_log)
    print(f"\n=== Pipeline complete ({run_log['duration_seconds']}s) ===")


def _save_log(config: dict, entry: dict):
    log_path = Path(config.get("checkpoint_dir", "data/checkpoints")) / "pipeline_log.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
        except (json.JSONDecodeError, ValueError):
            existing = []
    existing.append(entry)
    log_path.write_text(json.dumps(existing, indent=2))


if __name__ == "__main__":
    run_pipeline(parse_args())
