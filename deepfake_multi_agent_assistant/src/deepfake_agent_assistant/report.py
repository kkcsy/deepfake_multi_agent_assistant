from __future__ import annotations

import datetime as _dt
import json
import re
from pathlib import Path
from typing import Iterable, List

from .schemas import AgentResult, ProjectInput


def ensure_output_dir(path: str) -> Path:
    out_dir = Path(path)
    out_dir.mkdir(parents=True, exist_ok=True)
    return out_dir


def save_markdown_report(output_dir: Path, project_input: ProjectInput, results: List[AgentResult]) -> Path:
    timestamp = _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    report_path = output_dir / "report.md"
    lines: List[str] = []
    lines.append("# 多 Agent 协作科研助手报告\n")
    lines.append(f"生成时间：{timestamp}\n")
    lines.append("## 用户任务\n")
    lines.append(project_input.task)
    lines.append("\n---\n")

    if project_input.experiment_summary:
        lines.append("## 实验结果自动统计摘要\n")
        lines.append(project_input.experiment_summary)
        lines.append("\n---\n")

    for result in results:
        lines.append(f"## {result.name}：{result.role}\n")
        lines.append(result.output)
        lines.append("\n---\n")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path


def save_trace(output_dir: Path, project_input: ProjectInput, results: List[AgentResult]) -> Path:
    trace_path = output_dir / "agent_trace.json"
    payload = {
        "task": project_input.task,
        "results": [r.to_dict() for r in results],
    }
    trace_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return trace_path


def extract_form_answer(results: Iterable[AgentResult]) -> str:
    """Extract a concise form-ready answer from CoordinatorAgent when possible."""

    coordinator_output = ""
    for result in results:
        if result.key == "coordinator":
            coordinator_output = result.output
            break

    if not coordinator_output:
        coordinator_output = "\n\n".join(result.output for result in results)

    patterns = [
        r"可直接填写到表格中的[“\"]?具体成果描述[”\"]?[:：]?\s*(.*)",
        r"成果描述[:：]\s*(.*)",
    ]
    for pattern in patterns:
        match = re.search(pattern, coordinator_output, flags=re.S)
        if match:
            text = match.group(1).strip()
            # Stop at the next markdown section if present.
            text = re.split(r"\n#{1,6}\s+", text)[0].strip()
            return text

    return coordinator_output.strip()


def save_form_answer(output_dir: Path, results: Iterable[AgentResult]) -> Path:
    answer_path = output_dir / "final_form_answer.txt"
    answer_path.write_text(extract_form_answer(results), encoding="utf-8")
    return answer_path
