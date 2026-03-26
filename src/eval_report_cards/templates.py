"""Template-specific report builders."""

from __future__ import annotations

from typing import Any

from .analysis import (
    agent_metrics,
    classification_confidence,
    classification_metrics,
    infer_group_columns,
    infer_split_column,
    ranking_metrics,
    safe_divide,
    slice_summary,
    split_counts,
    summarize_log_actions,
    tabulate_label_distribution,
    top_counter_items,
)


def _merge_uncertainty(auto_summary: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    merged = dict(auto_summary)
    external = metrics.get("uncertainty")
    if isinstance(external, dict):
        merged.update(external)
    return merged


def _base_summary(template: str, predictions: list[dict[str, Any]], metrics: dict[str, Any], config: dict[str, Any], logs: list[dict[str, Any]]) -> dict[str, Any]:
    split_column = config.get("split_column") or infer_split_column(predictions)
    assumptions = config.get("assumptions", [])
    if isinstance(assumptions, str):
        assumptions = [assumptions]
    return {
        "title": config.get("report_title") or config.get("project_name") or "EvalReportCards Report",
        "template": template,
        "task_setup": {
            "project_name": config.get("project_name", "Unnamed project"),
            "task_name": config.get("task_name", template.title()),
            "task_description": config.get("task_description", "No task description supplied."),
            "dataset": config.get("dataset", "Not specified"),
            "data_split": split_counts(predictions, split_column),
            "assumptions": assumptions,
            "evaluation_notes": config.get("evaluation_notes", []),
        },
        "reported_metrics": metrics.get("reported_metrics", metrics),
        "chosen_metrics": config.get("chosen_metrics", []),
        "logs_supplied": bool(logs),
        "limitations": [],
    }


def build_classification_summary(predictions: list[dict[str, Any]], metrics: dict[str, Any], config: dict[str, Any], logs: list[dict[str, Any]]) -> dict[str, Any]:
    y_true_col = config.get("y_true_column", "y_true")
    y_pred_col = config.get("y_pred_column", "y_pred")
    y_score_col = config.get("score_column", "y_score")
    split_column = config.get("split_column") or infer_split_column(predictions)
    group_columns = infer_group_columns(predictions, {split_column, y_true_col, y_pred_col, y_score_col})

    summary = _base_summary("classification", predictions, metrics, config, logs)
    overall = classification_metrics(predictions, y_true_col, y_pred_col)
    by_split = {}
    for split in sorted({str(row.get(split_column, "unspecified")) for row in predictions}):
        rows = [row for row in predictions if str(row.get(split_column, "unspecified")) == split]
        by_split[split] = classification_metrics(rows, y_true_col, y_pred_col)

    confidence = classification_confidence(predictions, y_true_col, y_pred_col, y_score_col)
    slices = slice_summary(
        predictions,
        group_columns,
        lambda rows: classification_metrics(rows, y_true_col, y_pred_col)["accuracy"],
    )

    failure_modes = []
    if slices:
        worst_slice = slices[0]
        if worst_slice["score"] < overall["accuracy"] - 0.15:
            failure_modes.append(
                "Performance drops on `%s=%s` where accuracy falls to %.2f."
                % (worst_slice["column"], worst_slice["value"], worst_slice["score"])
            )
    if confidence.get("available") and confidence["mean_error_confidence"] >= 0.7:
        failure_modes.append("Wrong predictions are often still made with fairly high confidence.")
    weak_labels = [row for row in overall["per_label"] if row["recall"] < 0.6]
    if weak_labels:
        failure_modes.append(
            "Recall is weakest for labels %s."
            % ", ".join("`%s`" % row["label"] for row in weak_labels[:3])
        )

    if not confidence.get("available"):
        summary["limitations"].append("No prediction confidence column was supplied, so uncertainty is weakly characterized.")
    if not group_columns:
        summary["limitations"].append("No slice columns were detected, so slice analysis is limited.")
    if not metrics:
        summary["limitations"].append("No external metrics file was supplied; the report relies on recomputed metrics only.")

    summary["main_results"] = {"overall": overall, "by_split": by_split}
    summary["uncertainty"] = _merge_uncertainty(confidence, metrics)
    summary["error_slices"] = slices
    summary["likely_failure_modes"] = failure_modes or ["No dominant failure mode stood out from the available inputs."]
    summary["label_distribution"] = tabulate_label_distribution(predictions, y_true_col)
    return summary


def build_ranking_summary(predictions: list[dict[str, Any]], metrics: dict[str, Any], config: dict[str, Any], logs: list[dict[str, Any]]) -> dict[str, Any]:
    query_col = config.get("query_id_column", "query_id")
    rel_col = config.get("relevance_column", "relevance")
    score_col = config.get("score_column", "score")
    split_column = config.get("split_column") or infer_split_column(predictions)
    group_columns = infer_group_columns(predictions, {split_column, query_col, rel_col, score_col, "item_id", "rank"})

    summary = _base_summary("ranking", predictions, metrics, config, logs)
    overall = ranking_metrics(predictions, query_col, rel_col, score_col)
    by_split = {}
    for split in sorted({str(row.get(split_column, "unspecified")) for row in predictions}):
        rows = [row for row in predictions if str(row.get(split_column, "unspecified")) == split]
        by_split[split] = ranking_metrics(rows, query_col, rel_col, score_col)

    slices = slice_summary(
        predictions,
        group_columns,
        lambda rows: ranking_metrics(rows, query_col, rel_col, score_col)["ndcg_at_10"],
    )
    failure_modes = []
    if overall["mean_top_gap"] < 0.08:
        failure_modes.append("Top-ranked items are often separated by only a small score gap, suggesting unstable ordering.")
    if slices:
        worst_slice = slices[0]
        if worst_slice["score"] < overall["ndcg_at_10"] - 0.15:
            failure_modes.append(
                "Ranking quality falls on `%s=%s` where NDCG@10 drops to %.2f."
                % (worst_slice["column"], worst_slice["value"], worst_slice["score"])
            )

    summary["main_results"] = {"overall": overall, "by_split": by_split}
    summary["uncertainty"] = _merge_uncertainty({
        "available": True,
        "mean_top_rank_score_gap": overall["mean_top_gap"],
        "note": "Ranking confidence is approximated from the score gap between the top two items per query.",
    }, metrics)
    summary["error_slices"] = slices
    summary["likely_failure_modes"] = failure_modes or ["The current inputs do not isolate a strong ranking failure pattern."]
    if not group_columns:
        summary["limitations"].append("No query-group slice columns were detected, so slice analysis is limited.")
    if not metrics:
        summary["limitations"].append("No external ranking metrics file was supplied; the report relies on recomputed metrics only.")
    return summary


def build_agent_summary(predictions: list[dict[str, Any]], metrics: dict[str, Any], config: dict[str, Any], logs: list[dict[str, Any]]) -> dict[str, Any]:
    split_column = config.get("split_column") or infer_split_column(predictions)
    group_columns = infer_group_columns(predictions, {split_column, "episode_id", "success", "reward", "steps", "duration_seconds", "confidence", "failure_mode"})

    summary = _base_summary("agent", predictions, metrics, config, logs)
    overall = agent_metrics(predictions)
    by_split = {}
    for split in sorted({str(row.get(split_column, "unspecified")) for row in predictions}):
        rows = [row for row in predictions if str(row.get(split_column, "unspecified")) == split]
        by_split[split] = agent_metrics(rows)

    slices = slice_summary(
        predictions,
        group_columns,
        lambda rows: agent_metrics(rows)["success_rate"],
    )
    failed_rows = [row for row in predictions if not bool(row.get("success", 0))]
    failed_ids = {str(row.get("episode_id")) for row in failed_rows}
    failure_mode_counts = top_counter_items([str(row.get("failure_mode", "unknown")) for row in failed_rows if row.get("failure_mode")])
    risky_actions = summarize_log_actions(logs, failed_ids) if logs else []

    failure_modes = []
    if failure_mode_counts:
        failure_modes.append(
            "Most failed episodes cluster around %s."
            % ", ".join("%s (%d)" % (item["name"], item["count"]) for item in failure_mode_counts)
        )
    if slices:
        worst_slice = slices[0]
        if worst_slice["score"] < overall["success_rate"] - 0.15:
            failure_modes.append(
                "Success rate drops on `%s=%s` where it falls to %.2f."
                % (worst_slice["column"], worst_slice["value"], worst_slice["score"])
            )
    if risky_actions:
        failure_modes.append(
            "Failed episodes often include actions such as %s."
            % ", ".join("%s (%d)" % (item["name"], item["count"]) for item in risky_actions)
        )

    uncertainty = {
        "available": overall["mean_confidence"] is not None,
        "mean_confidence": overall["mean_confidence"],
        "note": "Confidence reflects the agent or controller confidence column when it is available.",
    }
    if overall["mean_confidence"] is None:
        uncertainty["note"] = "No explicit confidence column was supplied."
        summary["limitations"].append("No confidence field was supplied for agent episodes.")
    if not logs:
        summary["limitations"].append("No optional logs were supplied, so failure-mode analysis is weaker.")
    if not group_columns:
        summary["limitations"].append("No environment or task-family slice columns were detected.")
    if not metrics:
        summary["limitations"].append("No external metrics file was supplied; the report relies on recomputed metrics only.")

    summary["main_results"] = {"overall": overall, "by_split": by_split}
    summary["uncertainty"] = _merge_uncertainty(uncertainty, metrics)
    summary["error_slices"] = slices
    summary["likely_failure_modes"] = failure_modes or ["The current inputs do not isolate a dominant agent failure pattern."]
    summary["failure_mode_counts"] = failure_mode_counts
    summary["risky_actions_in_failures"] = risky_actions
    return summary


def build_summary(template: str, predictions: list[dict[str, Any]], metrics: dict[str, Any], config: dict[str, Any], logs: list[dict[str, Any]]) -> dict[str, Any]:
    if template == "classification":
        return build_classification_summary(predictions, metrics, config, logs)
    if template == "ranking":
        return build_ranking_summary(predictions, metrics, config, logs)
    if template == "agent":
        return build_agent_summary(predictions, metrics, config, logs)
    raise ValueError("Unsupported template %s" % template)
