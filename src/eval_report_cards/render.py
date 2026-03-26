"""Render markdown and HTML reports."""

from __future__ import annotations

import html
from typing import Any


def _format_value(value: Any) -> str:
    if isinstance(value, float):
        return "%.4f" % value
    if isinstance(value, dict):
        return ", ".join("%s=%s" % (key, _format_value(val)) for key, val in value.items())
    if isinstance(value, list):
        return ", ".join(_format_value(item) for item in value)
    return str(value)


def _markdown_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "_None_"
    headers = list(rows[0].keys())
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_format_value(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def _html_table(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "<p><em>None</em></p>"
    headers = list(rows[0].keys())
    head = "".join("<th>%s</th>" % html.escape(str(header)) for header in headers)
    body_rows = []
    for row in rows:
        cells = "".join("<td>%s</td>" % html.escape(_format_value(row.get(header, ""))) for header in headers)
        body_rows.append("<tr>%s</tr>" % cells)
    return "<table><thead><tr>%s</tr></thead><tbody>%s</tbody></table>" % (head, "".join(body_rows))


def render_markdown(summary: dict[str, Any]) -> str:
    task = summary["task_setup"]
    lines = [
        "# %s" % summary["title"],
        "",
        "## Task Setup",
        "",
        "- Project: `%s`" % task["project_name"],
        "- Task: %s" % task["task_name"],
        "- Template: `%s`" % summary["template"],
        "- Dataset: %s" % task["dataset"],
        "- Data split: %s" % ", ".join("%s=%s" % (key, value) for key, value in task["data_split"].items()),
        "",
        task["task_description"],
        "",
        "## Assumptions",
        "",
    ]
    if task["assumptions"]:
        lines.extend("- %s" % item for item in task["assumptions"])
    else:
        lines.append("- No assumptions were supplied.")

    lines.extend(
        [
            "",
            "## Chosen Metrics",
            "",
        ]
    )
    chosen_metrics = summary.get("chosen_metrics") or []
    if chosen_metrics:
        lines.extend("- %s" % item for item in chosen_metrics)
    else:
        lines.append("- No metric rationale was supplied; the report lists computed and reported metrics below.")

    lines.extend(
        [
            "",
            "## Main Results",
            "",
            "### Overall",
            "",
            _markdown_table([summary["main_results"]["overall"]]),
            "",
            "### By Split",
            "",
            _markdown_table(
                [{"split": key, **value} for key, value in summary["main_results"]["by_split"].items()]
            ),
            "",
            "## Reported Metrics",
            "",
            _markdown_table([summary.get("reported_metrics", {})] if summary.get("reported_metrics") else []),
            "",
            "## Uncertainty / Confidence",
            "",
            _markdown_table([summary.get("uncertainty", {})]),
            "",
            "## Error Slices",
            "",
            _markdown_table(summary.get("error_slices", [])),
            "",
            "## Likely Failure Modes",
            "",
        ]
    )
    if summary.get("likely_failure_modes"):
        lines.extend("- %s" % item for item in summary["likely_failure_modes"])
    else:
        lines.append("- None identified from the available inputs.")

    lines.extend(
        [
            "",
            "## Key Limitations",
            "",
        ]
    )
    if summary.get("limitations"):
        lines.extend("- %s" % item for item in summary["limitations"])
    else:
        lines.append("- No major limitations were automatically flagged.")
    return "\n".join(lines).strip() + "\n"


def render_html(summary: dict[str, Any]) -> str:
    task = summary["task_setup"]
    assumptions = "".join("<li>%s</li>" % html.escape(str(item)) for item in task["assumptions"]) or "<li>No assumptions were supplied.</li>"
    chosen_metrics = "".join("<li>%s</li>" % html.escape(str(item)) for item in summary.get("chosen_metrics", [])) or "<li>No metric rationale was supplied.</li>"
    failure_modes = "".join("<li>%s</li>" % html.escape(str(item)) for item in summary.get("likely_failure_modes", [])) or "<li>None identified.</li>"
    limitations = "".join("<li>%s</li>" % html.escape(str(item)) for item in summary.get("limitations", [])) or "<li>No major limitations were automatically flagged.</li>"
    return """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>{title}</title>
  <style>
    body {{ font-family: Georgia, 'Times New Roman', serif; margin: 40px auto; max-width: 960px; color: #1f2933; line-height: 1.5; padding: 0 20px; background: #faf8f2; }}
    h1, h2, h3 {{ color: #0b3c49; }}
    .meta {{ background: #eef4f3; border-left: 4px solid #0b3c49; padding: 14px 18px; margin-bottom: 24px; }}
    table {{ border-collapse: collapse; width: 100%; margin: 16px 0 28px 0; background: white; }}
    th, td {{ border: 1px solid #d7e0df; padding: 8px 10px; text-align: left; vertical-align: top; }}
    th {{ background: #e3ecea; }}
    section {{ margin-bottom: 26px; }}
    code {{ background: #edf2f7; padding: 1px 4px; }}
  </style>
</head>
<body>
  <h1>{title}</h1>
  <div class="meta">
    <strong>Project:</strong> {project}<br>
    <strong>Task:</strong> {task_name}<br>
    <strong>Template:</strong> <code>{template}</code><br>
    <strong>Dataset:</strong> {dataset}<br>
    <strong>Data split:</strong> {split_summary}
  </div>
  <section>
    <h2>Task Setup</h2>
    <p>{description}</p>
  </section>
  <section>
    <h2>Assumptions</h2>
    <ul>{assumptions}</ul>
  </section>
  <section>
    <h2>Chosen Metrics</h2>
    <ul>{chosen_metrics}</ul>
  </section>
  <section>
    <h2>Main Results</h2>
    <h3>Overall</h3>
    {overall_table}
    <h3>By Split</h3>
    {split_table}
  </section>
  <section>
    <h2>Reported Metrics</h2>
    {reported_metrics}
  </section>
  <section>
    <h2>Uncertainty / Confidence</h2>
    {uncertainty}
  </section>
  <section>
    <h2>Error Slices</h2>
    {error_slices}
  </section>
  <section>
    <h2>Likely Failure Modes</h2>
    <ul>{failure_modes}</ul>
  </section>
  <section>
    <h2>Key Limitations</h2>
    <ul>{limitations}</ul>
  </section>
</body>
</html>
""".format(
        title=html.escape(summary["title"]),
        project=html.escape(str(task["project_name"])),
        task_name=html.escape(str(task["task_name"])),
        template=html.escape(str(summary["template"])),
        dataset=html.escape(str(task["dataset"])),
        split_summary=html.escape(", ".join("%s=%s" % (key, value) for key, value in task["data_split"].items())),
        description=html.escape(str(task["task_description"])),
        assumptions=assumptions,
        chosen_metrics=chosen_metrics,
        overall_table=_html_table([summary["main_results"]["overall"]]),
        split_table=_html_table([{"split": key, **value} for key, value in summary["main_results"]["by_split"].items()]),
        reported_metrics=_html_table([summary.get("reported_metrics", {})] if summary.get("reported_metrics") else []),
        uncertainty=_html_table([summary.get("uncertainty", {})]),
        error_slices=_html_table(summary.get("error_slices", [])),
        failure_modes=failure_modes,
        limitations=limitations,
    )

