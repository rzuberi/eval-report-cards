#!/usr/bin/env python3
"""Generate the checked-in example reports."""

from __future__ import annotations

import os
import sys


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "src")

if SRC not in sys.path:
    sys.path.insert(0, SRC)

from eval_report_cards.cli import build_report_card


def main() -> None:
    runs = [
        ("classification", "examples/classification", "sample_reports/classification"),
        ("ranking", "examples/ranking", "sample_reports/ranking"),
        ("agent", "examples/agent", "sample_reports/agent"),
    ]
    for template, input_dir, output_dir in runs:
        build_report_card(
            template=template,
            predictions_path=os.path.join(ROOT, input_dir, "predictions.csv"),
            metrics_path=os.path.join(ROOT, input_dir, "metrics.json"),
            config_path=os.path.join(ROOT, input_dir, "config.json"),
            logs_path=os.path.join(ROOT, input_dir, "logs.jsonl") if os.path.exists(os.path.join(ROOT, input_dir, "logs.jsonl")) else None,
            output_dir=os.path.join(ROOT, output_dir),
        )
        print("Generated %s example." % template)


if __name__ == "__main__":
    main()
