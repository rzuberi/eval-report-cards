from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def run_cli(tmp_path: Path, template: str) -> Path:
    output_dir = tmp_path / template
    command = [
        sys.executable,
        "-m",
        "eval_report_cards.cli",
        "build",
        "--template",
        template,
        "--predictions",
        str(ROOT / "examples" / template / "predictions.csv"),
        "--metrics",
        str(ROOT / "examples" / template / "metrics.json"),
        "--config",
        str(ROOT / "examples" / template / "config.json"),
        "--output-dir",
        str(output_dir),
    ]
    logs_path = ROOT / "examples" / template / "logs.jsonl"
    if logs_path.exists():
        command.extend(["--logs", str(logs_path)])
    subprocess.run(command, check=True)
    return output_dir


def test_cli_generates_all_output_formats(tmp_path: Path) -> None:
    output_dir = run_cli(tmp_path, "classification")
    assert (output_dir / "report.md").exists()
    assert (output_dir / "report.html").exists()
    assert (output_dir / "summary.json").exists()
    payload = json.loads((output_dir / "summary.json").read_text())
    assert payload["template"] == "classification"
    assert "main_results" in payload


def test_agent_template_uses_logs_for_failure_modes(tmp_path: Path) -> None:
    output_dir = run_cli(tmp_path, "agent")
    payload = json.loads((output_dir / "summary.json").read_text())
    assert payload["template"] == "agent"
    assert payload["logs_supplied"] is True
    assert payload["risky_actions_in_failures"]
