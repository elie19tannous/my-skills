"""Recommend annotation project structure: IAA metric, calibration, AL strategy.

Phase 1 cached recommendations.
"""

from __future__ import annotations

import argparse
import json
import sys


def recommend_iaa(task_type: str, n_annotators: int, has_skewed: bool, has_missing: bool, is_span: bool) -> dict:
    if is_span:
        return {"metric": "γ (gamma)", "rationale": "Span/unitized task — κ doesn't model boundaries"}
    if has_missing:
        return {"metric": "Krippendorff α", "rationale": "Missing data — α handles partial annotation"}
    if has_skewed:
        return {"metric": "PABAK or F1-complement", "rationale": "Skewed prevalence — Cohen κ misleads"}
    if n_annotators >= 3:
        return {"metric": "Fleiss κ (or α)", "rationale": "≥ 3 annotators; κ generalized to N raters"}
    return {"metric": "Cohen κ", "rationale": "Standard 2-annotator nominal task"}


def recommend_al(target_class: int, has_model: bool, budget: int) -> dict:
    if not has_model:
        return {
            "strategy": "diversity (clustering-based)",
            "rationale": "No model — can't compute uncertainty; cluster pool by sentence embedding for diverse coverage",  # noqa: E501  # long anti-pattern string
            "batch_size": min(100, max(20, budget // 10)),
        }
    if target_class <= 1:
        return {
            "strategy": "hybrid (diversity-dominant + uncertainty)",
            "rationale": "Low-resource — diversity ensures coverage; uncertainty adds model-blind-spot awareness",
            "batch_size": min(200, budget // 20),
        }
    if target_class <= 3:
        return {
            "strategy": "uncertainty (entropy or margin)",
            "rationale": "Some model exists; trust uncertainty signal",
            "batch_size": min(500, budget // 10),
        }
    return {
        "strategy": "random + occasional uncertainty",
        "rationale": "High-resource model; gains from AL are smaller; baseline matters",
        "batch_size": min(1000, budget // 10),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Annotation project plan advisor.")
    parser.add_argument(
        "--task", required=True, help="Task description (NER / sentiment / POS / parsing / MQM / other)"
    )
    parser.add_argument("--n-annotators", type=int, default=2)
    parser.add_argument("--skewed-classes", action="store_true", help="Class distribution is highly skewed")
    parser.add_argument("--missing-data", action="store_true", help="Some annotators may not annotate all items")
    parser.add_argument("--span-task", action="store_true", help="Task involves span boundaries (NER, coref)")
    parser.add_argument("--target-class", type=int, default=2, help="Joshi class of target language")
    parser.add_argument("--has-model", action="store_true", help="A model exists for active learning uncertainty")
    parser.add_argument("--budget", type=int, default=1000, help="Total annotation budget (items)")
    args = parser.parse_args()

    iaa = recommend_iaa(args.task, args.n_annotators, args.skewed_classes, args.missing_data, args.span_task)
    al = recommend_al(args.target_class, args.has_model, args.budget)

    out = {
        "task": args.task,
        "n_annotators": args.n_annotators,
        "iaa_recommendation": iaa,
        "shipping_threshold": "κ/α ≥ 0.8 (or specified); 0.67-0.8 = tentative; report bootstrap CI for n < 200",
        "calibration_protocol": {
            "draft_size_items": 30,
            "pilot_size_items": 50,
            "calibration_size_items": 100,
            "bulk_double_annotated_pct": 10,
            "rationale": "Skipping calibration → 10-20% bulk re-annotation cost",
        },
        "active_learning": al,
        "anti_patterns": [
            "DO NOT use Cohen κ on highly skewed classes",
            "DO NOT ship single-annotator gold without subjectivity disclaimer",
            "DO NOT skip calibration rounds",
            "DO NOT report κ without bootstrap CI when N < 200",
            "DO NOT use κ for span tasks (use γ)",
        ],
        "tool_recommendations": {
            "general": "Label Studio (open-source, ML loop) or Prodigy (commercial polish)",
            "linguistic_specific": "INCEpTION (UD/treebank), brat (span minimalist)",
        },
        "snapshot_date": "2026-04-23",
    }
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
