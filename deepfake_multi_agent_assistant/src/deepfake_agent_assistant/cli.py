from __future__ import annotations

import argparse
from pathlib import Path
from typing import List

from .config import load_settings
from .experiment_analyzer import analyze_result_files
from .file_loader import read_files, read_task
from .llm import build_llm
from .pipeline import MultiAgentPipeline
from .report import ensure_output_dir, save_form_answer, save_markdown_report, save_trace
from .schemas import ProjectInput


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="deepfake-agent",
        description="面向深度伪造检测研究的多 Agent 协作科研助手",
    )
    subparsers = parser.add_subparsers(dest="command")

    run_parser = subparsers.add_parser("run", help="运行完整多 Agent 工作流")
    run_parser.add_argument("--task", type=str, default="", help="直接输入科研任务描述")
    run_parser.add_argument("--task-file", type=str, default="", help="从文件读取科研任务描述")
    run_parser.add_argument("--literature", nargs="*", default=[], help="文献、论文草稿、笔记、PDF 等路径")
    run_parser.add_argument("--code", nargs="*", default=[], help="模型代码、训练脚本、评估脚本路径")
    run_parser.add_argument("--results", nargs="*", default=[], help="实验结果文件路径，支持 CSV/TXT/MD")
    run_parser.add_argument("--extra", nargs="*", default=[], help="其他补充材料路径")
    run_parser.add_argument("--provider", type=str, default=None, choices=["openai", "mock"], help="LLM 后端")
    run_parser.add_argument("--model", type=str, default=None, help="模型名称，默认读取 OPENAI_MODEL")
    run_parser.add_argument("--api-mode", type=str, default=None, choices=["responses", "chat"], help="API 模式")
    run_parser.add_argument("--temperature", type=float, default=None, help="生成温度")
    run_parser.add_argument("--max-output-tokens", type=int, default=None, help="每个 Agent 最大输出 token 数")
    run_parser.add_argument("--output-dir", type=str, default="outputs", help="输出目录")

    return parser


def run(args: argparse.Namespace) -> None:
    task = read_task(task=args.task, task_file=args.task_file)
    literature_context = read_files(args.literature, max_chars_each=30000)
    code_context = read_files(args.code, max_chars_each=30000)
    experiment_context = read_files(args.results, max_chars_each=30000)
    experiment_summary = analyze_result_files(args.results) if args.results else ""
    extra_context = read_files(args.extra, max_chars_each=20000)

    project_input = ProjectInput(
        task=task,
        literature_context=literature_context,
        code_context=code_context,
        experiment_context=experiment_context,
        experiment_summary=experiment_summary,
        extra_context=extra_context,
    )

    settings = load_settings(
        provider=args.provider,
        model=args.model,
        api_mode=args.api_mode,
        temperature=args.temperature,
        max_output_tokens=args.max_output_tokens,
    )
    llm = build_llm(settings)
    pipeline = MultiAgentPipeline(llm)
    results = pipeline.run(project_input)

    out_dir = ensure_output_dir(args.output_dir)
    report_path = save_markdown_report(out_dir, project_input, results)
    trace_path = save_trace(out_dir, project_input, results)
    form_path = save_form_answer(out_dir, results)

    print("\n========== 多 Agent 协作完成 ==========")
    print(f"Markdown 报告：{report_path}")
    print(f"Agent 轨迹：{trace_path}")
    print(f"表格填写文本：{form_path}")


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "run":
        run(args)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
