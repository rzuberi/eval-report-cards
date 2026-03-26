"""CLI entrypoint for EvalReportCards."""

from __future__ import annotations

import argparse
import os
from typing import Any

from .io_utils import ensure_dir, load_mapping, load_table, write_json, write_text
from .render import render_html, render_markdown
from .templates import build_summary


def build_report_card(
    template: str,
    predictions_path: str,
    metrics_path: str | None,
    config_path: str | None,
    logs_path: str | None,
    output_dir: str,
) -> dict[str, Any]:
    predictions = load_table(predictions_path)
    metrics = load_mapping(metrics_path)
    config = load_mapping(config_path)
    logs = load_table(logs_path) if logs_path else []

    ensure_dir(output_dir)
    summary = build_summary(template, predictions, metrics, config, logs)

    summary_path = os.path.join(output_dir, "summary.json")
    markdown_path = os.path.join(output_dir, "report.md")
    html_path = os.path.join(output_dir, "report.html")

    write_json(summary_path, summary)
    write_text(markdown_path, render_markdown(summary))
    write_text(html_path, render_html(summary))
    return {
        "summary_path": summary_path,
        "markdown_path": markdown_path,
        "html_path": html_path,
        "summary": summary,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate standardized evaluation reports from run artifacts.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    build = subparsers.add_parser("build", help="Build a report card from predictions, metrics, config, and optional logs.")
    build.add_argument("--template", choices=["classification", "ranking", "agent"], required=True)
    build.add_argument("--predictions", required=True)
    build.add_argument("--metrics")
    build.add_argument("--config")
    build.add_argument("--logs")
    build.add_argument("--output-dir", required=True)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.command == "build":
        result = build_report_card(
            template=args.template,
            predictions_path=args.predictions,
            metrics_path=args.metrics,
            config_path=args.config,
            logs_path=args.logs,
            output_dir=args.output_dir,
        )
        print("EvalReportCards complete.")
        print("Markdown report: %s" % result["markdown_path"])
        print("HTML report: %s" % result["html_path"])
        print("Summary JSON: %s" % result["summary_path"])


if __name__ == "__main__":
    main()

