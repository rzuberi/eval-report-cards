# EvalReportCards for Structured Evaluation Reporting

*A lightweight but highly usable CLI for turning messy run outputs into clean, standardized evaluation reports.*

> [!NOTE]
> **In plain language**
> Most model and agent evaluations end up scattered across notebooks, screenshots, ad hoc JSON files, and half-finished markdown notes. EvalReportCards takes the basic outputs you already have — predictions, metrics, configuration, and optional logs — and turns them into a readable report plus a machine-readable summary. The goal is simple: make evaluation look structured, reproducible, and professionally serious by default.

## Overview

EvalReportCards is a small CLI tool for generating standardized evaluation reports from the outputs of a model or agent run. It supports plug-and-play templates for common cases such as classification, ranking, and agent tasks, and writes three artifacts in one pass:

- `report.md` for human-readable review
- `report.html` for easy sharing
- `summary.json` for downstream pipelines and dashboards

The tool is intentionally lightweight. It assumes you already have run outputs and focuses on turning them into something organized: task setup, data split, assumptions, chosen metrics, uncertainty or confidence, main results, error slices, likely failure modes, and key limitations.

## Status

This is a working first release with three built-in templates and checked-in example runs. The examples ship with generated reports under [`sample_reports/`](sample_reports), so the repository demonstrates the full output format rather than only the code path.

## Why This Project Exists

Good evaluation is often less limited by metrics than by structure. Teams can compute scores, but still struggle to answer basic questions later:

- what exactly was evaluated
- which split the result came from
- what assumptions were made
- whether confidence or uncertainty was tracked
- which slices failed
- what the likely limitations were

EvalReportCards exists to make that structure automatic and repeatable. It is useful for ordinary model work, but it is especially valuable for research and safety infrastructure because it treats evaluation as a first-class artifact rather than an afterthought.

## What This Tool Currently Does

- ingests predictions from CSV, TSV, JSON, or JSONL
- ingests metrics and config from JSON, TOML, or simple metric/value CSV
- supports built-in templates for classification, ranking, and agent tasks
- recomputes lightweight template-specific metrics from predictions
- merges in reported metrics from external files
- summarizes task setup, data split, assumptions, and metric rationale
- surfaces confidence or uncertainty information when available
- auto-detects slice columns and reports the weakest slices
- highlights likely failure modes from slices, confidences, and optional logs
- writes synchronized markdown, HTML, and JSON outputs

## What It Explicitly Does Not Do

- train or evaluate a model for you
- replace careful statistical analysis
- guarantee calibrated uncertainty estimates
- infer rich causal explanations from minimal inputs
- claim that one report format is enough for every deployment decision

## Supported Templates

| Template | Expected inputs | Built-in analysis |
| --- | --- | --- |
| `classification` | Labels, predictions, optional confidence, slice columns | Accuracy, macro precision/recall/F1, confusion summary, slice failures, confidence diagnostics |
| `ranking` | Query-item relevance and scores, optional slice columns | NDCG@3, NDCG@10, MRR, Hit@1, score-gap uncertainty proxy, weak query-group slices |
| `agent` | Episode success, reward, steps, duration, optional logs | Success rate, efficiency summaries, environment/task-family slices, failure-mode clustering from logs |

## CLI Usage

```bash
eval-report-cards build \
  --template classification \
  --predictions examples/classification/predictions.csv \
  --metrics examples/classification/metrics.json \
  --config examples/classification/config.json \
  --output-dir sample_reports/classification
```

For agent tasks with logs:

```bash
eval-report-cards build \
  --template agent \
  --predictions examples/agent/predictions.csv \
  --metrics examples/agent/metrics.json \
  --config examples/agent/config.json \
  --logs examples/agent/logs.jsonl \
  --output-dir sample_reports/agent
```

## Example Outputs

The repository includes three complete sample runs:

- classification: [`sample_reports/classification/report.md`](sample_reports/classification/report.md)
- ranking: [`sample_reports/ranking/report.md`](sample_reports/ranking/report.md)
- agent: [`sample_reports/agent/report.md`](sample_reports/agent/report.md)

A few concrete highlights from the checked-in examples:

- classification example: overall accuracy `0.7778`, macro F1 `0.7778`, and the report correctly flags `source=email` as the weakest slice with `0.00` accuracy
- ranking example: overall NDCG@10 `0.7534`, with the `support` query group flagged as the weakest slice at `0.50`
- agent example: overall success rate `0.50`, with browser tasks dropping to `0.3333` success and failure logs pointing to `read_secret` and `copy_to_notes` patterns

## Quickstart

```bash
/home/zuberi01/miniforge3/bin/python3.12 -m venv .venv
.venv/bin/pip install -e . pytest
.venv/bin/python scripts/run_examples.py
.venv/bin/python -m pytest
```

Or with the small Make targets:

```bash
make run-examples
make test
```

## Repository Structure

```text
eval-report-cards/
├── examples/
│   ├── agent/
│   ├── classification/
│   └── ranking/
├── sample_reports/
│   ├── agent/
│   ├── classification/
│   └── ranking/
├── scripts/
│   └── run_examples.py
├── src/eval_report_cards/
│   ├── analysis.py
│   ├── cli.py
│   ├── io_utils.py
│   ├── render.py
│   └── templates.py
├── tests/
│   └── test_cli.py
├── LICENSE
├── Makefile
├── README.md
└── pyproject.toml
```

## Why It Looks Good Professionally

This project is strong because it turns evaluation from a messy side effect into a reproducible artifact. That signals the right instincts: robust reporting, infrastructure thinking, careful assumptions, and enough standardization that results can actually be inspected later.

## Roadmap

- add regression and calibration-focused templates
- support richer uncertainty sections from externally supplied bootstrap or Bayesian summaries
- add more configurable slice policies and minimum support thresholds
- export a compact badge or scorecard view for dashboards
- support optional report branding for labs or teams
