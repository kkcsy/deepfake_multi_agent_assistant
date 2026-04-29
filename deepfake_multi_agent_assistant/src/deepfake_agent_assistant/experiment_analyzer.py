from __future__ import annotations

import csv
import math
from pathlib import Path
from statistics import mean
from typing import Dict, Iterable, List, Optional, Tuple

NUMERIC_HINTS = {"auc", "ap", "eer", "acc", "accuracy", "f1", "precision", "recall"}
DATASET_HINTS = {"dataset", "test", "target", "benchmark", "domain"}
METHOD_HINTS = {"method", "model", "approach", "name"}


def _to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    value = str(value).strip().replace("%", "")
    if value == "":
        return None
    try:
        return float(value)
    except ValueError:
        return None


def _is_metric_column(name: str) -> bool:
    lower = name.lower()
    return any(hint in lower for hint in NUMERIC_HINTS)


def _find_column(headers: List[str], hints: Iterable[str]) -> Optional[str]:
    for header in headers:
        lower = header.lower()
        if any(hint in lower for hint in hints):
            return header
    return None


def load_csv_rows(path: Path) -> Tuple[List[str], List[Dict[str, str]]]:
    with path.open("r", encoding="utf-8", errors="ignore", newline="") as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames or []
        rows = list(reader)
    return headers, rows


def analyze_csv(path: Path) -> str:
    """Create a lightweight statistical summary for experiment CSV files.

    Expected flexible format:
    - columns may include method/model, dataset/benchmark and metric columns such as AUC/AP/EER.
    - numeric metrics are detected by column names.
    """

    if not path.exists():
        return f"[实验文件不存在] {path}"

    try:
        headers, rows = load_csv_rows(path)
    except Exception as exc:
        return f"[实验文件读取失败] {path.name}: {exc}"

    if not headers:
        return f"[实验文件为空或没有表头] {path.name}"

    method_col = _find_column(headers, METHOD_HINTS)
    dataset_col = _find_column(headers, DATASET_HINTS)
    metric_cols = [h for h in headers if _is_metric_column(h)]

    lines: List[str] = []
    lines.append(f"===== 实验结果自动摘要：{path.name} =====")
    lines.append(f"行数：{len(rows)}")
    lines.append(f"检测到的方法列：{method_col or '未识别'}")
    lines.append(f"检测到的数据集列：{dataset_col or '未识别'}")
    lines.append(f"检测到的指标列：{metric_cols or '未识别'}")

    if not rows or not metric_cols:
        lines.append("未能识别可统计的指标列，建议使用包含 AUC/AP/EER 等字段的 CSV。")
        return "\n".join(lines)

    # Overall metric statistics.
    for metric in metric_cols:
        values = [_to_float(row.get(metric, "")) for row in rows]
        values = [v for v in values if v is not None]
        if not values:
            continue
        lines.append(
            f"指标 {metric}: mean={mean(values):.4f}, min={min(values):.4f}, max={max(values):.4f}, n={len(values)}"
        )

    # Method-level averages.
    if method_col:
        method_to_values: Dict[str, Dict[str, List[float]]] = {}
        for row in rows:
            method = row.get(method_col, "Unknown") or "Unknown"
            method_to_values.setdefault(method, {m: [] for m in metric_cols})
            for metric in metric_cols:
                v = _to_float(row.get(metric, ""))
                if v is not None:
                    method_to_values[method][metric].append(v)

        lines.append("\n按方法聚合的平均指标：")
        for method, metric_values in method_to_values.items():
            parts = []
            for metric, values in metric_values.items():
                if values:
                    parts.append(f"{metric}={mean(values):.4f}")
            lines.append(f"- {method}: " + (", ".join(parts) if parts else "无可用数值"))

    # Dataset-level best methods.
    if method_col and dataset_col:
        lines.append("\n按数据集识别的最佳方法（AUC/AP/ACC/F1 越高越好，EER 越低越好）：")
        datasets = sorted({row.get(dataset_col, "Unknown") or "Unknown" for row in rows})
        for dataset in datasets:
            dataset_rows = [row for row in rows if (row.get(dataset_col, "Unknown") or "Unknown") == dataset]
            lines.append(f"- 数据集 {dataset}:")
            for metric in metric_cols:
                scored = []
                for row in dataset_rows:
                    v = _to_float(row.get(metric, ""))
                    if v is not None:
                        scored.append((row.get(method_col, "Unknown") or "Unknown", v))
                if not scored:
                    continue
                reverse = "eer" not in metric.lower()
                best_method, best_value = sorted(scored, key=lambda x: x[1], reverse=reverse)[0]
                direction = "最高" if reverse else "最低"
                lines.append(f"  - {metric} {direction}: {best_method} ({best_value:.4f})")

    lines.append("\n提示：自动摘要只做统计归纳，论文中的最终 claim 仍需结合训练协议、显著性检验和人工复核。")
    return "\n".join(lines)


def analyze_result_files(paths: Iterable[str]) -> str:
    summaries = []
    for raw_path in paths:
        path = Path(raw_path)
        if path.suffix.lower() == ".csv":
            summaries.append(analyze_csv(path))
        else:
            try:
                text = path.read_text(encoding="utf-8", errors="ignore")
                if len(text) > 20000:
                    text = text[:20000] + "\n\n[内容过长，已截断]"
                summaries.append(f"===== 实验结果文本：{path.name} =====\n{text}")
            except Exception as exc:
                summaries.append(f"[实验结果读取失败] {path}: {exc}")
    return "\n\n".join(summaries)
