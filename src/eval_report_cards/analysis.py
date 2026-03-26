"""Analysis helpers for EvalReportCards."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any


CORE_COLUMNS = {
    "split",
    "y_true",
    "y_pred",
    "y_score",
    "label",
    "prediction",
    "query_id",
    "item_id",
    "relevance",
    "score",
    "rank",
    "episode_id",
    "success",
    "reward",
    "steps",
    "duration_seconds",
    "confidence",
    "failure_mode",
}


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return sum(values) / float(len(values))


def safe_divide(numerator: float, denominator: float) -> float:
    if not denominator:
        return 0.0
    return numerator / float(denominator)


def infer_split_column(records: list[dict[str, Any]]) -> str:
    if not records:
        return "split"
    for candidate in ("split", "data_split", "partition"):
        if candidate in records[0]:
            return candidate
    return "split"


def infer_group_columns(records: list[dict[str, Any]], reserved: set[str]) -> list[str]:
    if not records:
        return []
    candidates = []
    keys = records[0].keys()
    for key in keys:
        if key in reserved or key in CORE_COLUMNS:
            continue
        values = [row.get(key) for row in records if row.get(key) not in (None, "")]
        if not values:
            continue
        unique_values = sorted(set(values))
        if 1 < len(unique_values) <= 10 and any(isinstance(value, str) for value in unique_values):
            candidates.append(key)
    return candidates[:3]


def split_counts(records: list[dict[str, Any]], split_column: str) -> dict[str, int]:
    counts: dict[str, int] = Counter()
    for row in records:
        counts[str(row.get(split_column, "unspecified"))] += 1
    return dict(sorted(counts.items()))


def tabulate_label_distribution(records: list[dict[str, Any]], label_column: str) -> dict[str, int]:
    counts: dict[str, int] = Counter()
    for row in records:
        counts[str(row.get(label_column, "missing"))] += 1
    return dict(sorted(counts.items()))


def classification_metrics(records: list[dict[str, Any]], y_true_col: str, y_pred_col: str) -> dict[str, Any]:
    labels = sorted({str(row[y_true_col]) for row in records} | {str(row[y_pred_col]) for row in records})
    correct = 0
    confusion: dict[str, dict[str, int]] = {label: {inner: 0 for inner in labels} for label in labels}
    for row in records:
        truth = str(row[y_true_col])
        pred = str(row[y_pred_col])
        confusion[truth][pred] += 1
        if truth == pred:
            correct += 1

    per_label = []
    precision_values = []
    recall_values = []
    f1_values = []
    for label in labels:
        tp = confusion[label][label]
        fp = sum(confusion[other][label] for other in labels if other != label)
        fn = sum(confusion[label][other] for other in labels if other != label)
        precision = safe_divide(tp, tp + fp)
        recall = safe_divide(tp, tp + fn)
        f1 = safe_divide(2 * precision * recall, precision + recall) if precision or recall else 0.0
        precision_values.append(precision)
        recall_values.append(recall)
        f1_values.append(f1)
        per_label.append(
            {
                "label": label,
                "support": sum(confusion[label].values()),
                "precision": round(precision, 4),
                "recall": round(recall, 4),
                "f1": round(f1, 4),
            }
        )

    return {
        "count": len(records),
        "accuracy": round(safe_divide(correct, len(records)), 4),
        "macro_precision": round(mean(precision_values) or 0.0, 4),
        "macro_recall": round(mean(recall_values) or 0.0, 4),
        "macro_f1": round(mean(f1_values) or 0.0, 4),
        "per_label": per_label,
        "confusion": confusion,
    }


def classification_confidence(records: list[dict[str, Any]], y_true_col: str, y_pred_col: str, score_col: str) -> dict[str, Any]:
    values = [float(row[score_col]) for row in records if row.get(score_col) not in (None, "")]
    if not values:
        return {"available": False, "note": "No prediction confidence column was supplied."}

    correct_conf = []
    error_conf = []
    for row in records:
        if row.get(score_col) in (None, ""):
            continue
        confidence = float(row[score_col])
        if str(row[y_true_col]) == str(row[y_pred_col]):
            correct_conf.append(confidence)
        else:
            error_conf.append(confidence)

    high_conf_errors = sum(1 for value in error_conf if value >= 0.8)
    return {
        "available": True,
        "mean_correct_confidence": round(mean(correct_conf) or 0.0, 4),
        "mean_error_confidence": round(mean(error_conf) or 0.0, 4),
        "high_confidence_error_rate": round(safe_divide(high_conf_errors, len(error_conf)), 4) if error_conf else 0.0,
    }


def _dcg(relevances: list[float], k: int) -> float:
    total = 0.0
    for index, rel in enumerate(relevances[:k], start=1):
        total += (2 ** rel - 1) / math.log2(index + 1)
    return total


def ranking_metrics(records: list[dict[str, Any]], query_col: str, rel_col: str, score_col: str) -> dict[str, Any]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        grouped[str(row[query_col])].append(row)

    ndcg3 = []
    ndcg10 = []
    mrr = []
    hit1 = []
    score_gaps = []
    for _, rows in grouped.items():
        ranked = sorted(rows, key=lambda item: float(item[score_col]), reverse=True)
        rels = [float(row[rel_col]) for row in ranked]
        ideal_rels = sorted(rels, reverse=True)
        ndcg3.append(safe_divide(_dcg(rels, 3), _dcg(ideal_rels, 3)))
        ndcg10.append(safe_divide(_dcg(rels, 10), _dcg(ideal_rels, 10)))
        first_rel = 0.0
        reciprocal_rank = 0.0
        for index, rel in enumerate(rels, start=1):
            if rel > 0:
                first_rel = rel
                reciprocal_rank = 1.0 / index
                break
        hit1.append(1.0 if rels and rels[0] > 0 else 0.0)
        mrr.append(reciprocal_rank)
        if len(ranked) >= 2:
            score_gaps.append(float(ranked[0][score_col]) - float(ranked[1][score_col]))

    return {
        "query_count": len(grouped),
        "ndcg_at_3": round(mean(ndcg3) or 0.0, 4),
        "ndcg_at_10": round(mean(ndcg10) or 0.0, 4),
        "mrr": round(mean(mrr) or 0.0, 4),
        "hit_at_1": round(mean(hit1) or 0.0, 4),
        "mean_top_gap": round(mean(score_gaps) or 0.0, 4),
    }


def agent_metrics(records: list[dict[str, Any]]) -> dict[str, Any]:
    success = [int(bool(row.get("success", 0))) for row in records]
    rewards = [float(row["reward"]) for row in records if row.get("reward") not in (None, "")]
    steps = [float(row["steps"]) for row in records if row.get("steps") not in (None, "")]
    durations = [float(row["duration_seconds"]) for row in records if row.get("duration_seconds") not in (None, "")]
    confidences = [float(row["confidence"]) for row in records if row.get("confidence") not in (None, "")]
    return {
        "episode_count": len(records),
        "success_rate": round(mean(success) or 0.0, 4),
        "mean_reward": round(mean(rewards) or 0.0, 4) if rewards else None,
        "mean_steps": round(mean(steps) or 0.0, 4) if steps else None,
        "mean_duration_seconds": round(mean(durations) or 0.0, 4) if durations else None,
        "mean_confidence": round(mean(confidences) or 0.0, 4) if confidences else None,
    }


def slice_summary(
    records: list[dict[str, Any]],
    group_columns: list[str],
    scorer,
) -> list[dict[str, Any]]:
    slices = []
    for column in group_columns:
        grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in records:
            value = row.get(column)
            if value not in (None, ""):
                grouped[str(value)].append(row)
        for value, rows in grouped.items():
            score = scorer(rows)
            slices.append(
                {
                    "column": column,
                    "value": value,
                    "count": len(rows),
                    "score": round(score, 4),
                }
            )
    return sorted(slices, key=lambda item: (item["score"], -item["count"]))[:6]


def top_counter_items(values: list[str], top_k: int = 3) -> list[dict[str, Any]]:
    counts = Counter(values)
    return [{"name": name, "count": count} for name, count in counts.most_common(top_k)]


def summarize_log_actions(log_rows: list[dict[str, Any]], failed_ids: set[str], key: str = "action_type") -> list[dict[str, Any]]:
    values = []
    for row in log_rows:
        episode_id = str(row.get("episode_id", ""))
        if episode_id in failed_ids and row.get(key):
            values.append(str(row[key]))
    return top_counter_items(values)

