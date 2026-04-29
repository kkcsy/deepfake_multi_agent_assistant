# Deepfake Multi-Agent Research Assistant

面向**深度伪造检测研究**的多 Agent 协作科研助手。该项目将科研流程拆解为多个专业 Agent：科研任务规划、文献分析、方法设计、代码实现检查、实验结果分析、论文写作、审稿式检查和最终汇总，适合用于论文写作、实验分析、项目申报材料撰写和研究工作流展示。

## 1. 项目能做什么

该系统围绕深度伪造检测常见任务设计，尤其适合以下场景：

- 阅读和总结 deepfake detection 相关文献；
- 梳理方法动机、模块设计和创新点；
- 检查模型代码、训练流程和评估流程；
- 分析 FF++、CDFv1、CDFv2、DFDC、DFD、DFDCP、DF40 等数据集上的实验结果；
- 自动生成论文实验分析、方法概述、贡献描述和项目表格内容；
- 从审稿人视角检查逻辑漏洞、过度 claim 和实验支撑不足的问题。

## 2. 项目结构

```text
deepfake_multi_agent_assistant/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .env.example
├── examples/
│   ├── sample_task.md
│   ├── sample_paper_notes.md
│   ├── sample_results.csv
│   └── sample_model_code.py
├── scripts/
│   ├── run_example_linux.sh
│   └── run_example_windows.bat
├── src/
│   └── deepfake_agent_assistant/
│       ├── __init__.py
│       ├── agents.py
│       ├── cli.py
│       ├── config.py
│       ├── experiment_analyzer.py
│       ├── file_loader.py
│       ├── llm.py
│       ├── pipeline.py
│       ├── prompts.py
│       ├── report.py
│       └── schemas.py
└── tests/
    └── test_experiment_analyzer.py
```

## 3. 安装环境

建议使用 Python 3.9 或更高版本。

```bash
cd deepfake_multi_agent_assistant
python -m venv .venv
```

Windows：

```bash
.venv\Scripts\activate
```

Linux / macOS：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
pip install -r requirements.txt
pip install -e .
```

## 4. 配置 API

复制环境变量模板：

```bash
cp .env.example .env
```

然后在 `.env` 中填写：

```bash
OPENAI_API_KEY=你的_API_KEY
OPENAI_MODEL=gpt-5.5
LLM_PROVIDER=openai
```

本项目默认支持 OpenAI Python SDK，也支持 OpenAI-compatible 的 Chat Completions 接口。OpenAI 官方 Python SDK 提供 `OpenAI` 客户端访问 OpenAI REST API，Responses API 可通过 `client.responses.create(...)` 调用；如果你的兼容接口不支持 Responses API，可以将 `OPENAI_API_MODE` 改为 `chat`。

## 5. 不配置 API 也能跑：mock 模式

如果只是展示项目流程，不想真实调用模型，可以使用 mock 模式：

```bash
python -m deepfake_agent_assistant.cli run ^
  --task-file examples/sample_task.md ^
  --literature examples/sample_paper_notes.md ^
  --code examples/sample_model_code.py ^
  --results examples/sample_results.csv ^
  --provider mock
```

Linux / macOS：

```bash
python -m deepfake_agent_assistant.cli run \
  --task-file examples/sample_task.md \
  --literature examples/sample_paper_notes.md \
  --code examples/sample_model_code.py \
  --results examples/sample_results.csv \
  --provider mock
```

## 6. 使用真实模型运行

```bash
python -m deepfake_agent_assistant.cli run \
  --task-file examples/sample_task.md \
  --literature examples/sample_paper_notes.md \
  --code examples/sample_model_code.py \
  --results examples/sample_results.csv \
  --provider openai
```

输出会自动保存到 `outputs/` 目录，包括：

- `report.md`：最终 Markdown 报告；
- `agent_trace.json`：每个 Agent 的输入输出记录；
- `final_form_answer.txt`：可直接填写到表格中的成果描述。

## 7. 命令行参数说明

```bash
python -m deepfake_agent_assistant.cli run --help
```

常用参数：

- `--task`：直接输入任务描述；
- `--task-file`：从文件读取任务描述；
- `--literature`：论文笔记、related work、LaTeX 草稿、PDF 文献等；
- `--code`：模型代码、训练脚本、评估脚本；
- `--results`：实验结果文件，推荐 CSV / TXT / Markdown；
- `--extra`：其他补充材料；
- `--provider`：`openai` 或 `mock`；
- `--output-dir`：输出目录，默认为 `outputs`。

## 8. 示例：把你的深伪检测论文材料接入

```bash
python -m deepfake_agent_assistant.cli run \
  --task "请基于我的 PRD 深度伪造检测方法，生成方法分析、实验分析和可填写到项目表格中的成果描述。" \
  --literature paper/introduction.tex paper/method.tex paper/related_work.tex \
  --code src/model.py src/train.py src/eval.py \
  --results results/cross_dataset.csv results/ablation.csv \
  --provider openai
```

## 9. 适合填写到表格中的成果描述示例

项目运行后会自动生成这一类文本：

> 我构建了一个面向深度伪造检测研究的多 Agent 协作科研助手，用于解决科研过程中任务分散、文献整理耗时、实验分析重复以及论文表达修改成本高等问题。系统由科研任务规划、文献分析、方法设计、代码实现检查、实验结果分析、论文写作、审稿式检查和最终汇总等多个 Agent 组成，能够围绕深度伪造检测中的跨数据集泛化、重构差异建模、鲁棒性评估和消融实验分析等核心问题进行协同处理。通过该系统，文献总结、实验结论归纳和论文段落初稿生成等环节可以形成自动化工作流，减少重复性整理工作，并降低实验结论与表格数据不一致的风险。

## 10. 注意事项

- 系统输出是科研辅助结果，不应替代真实实验、人工复核和论文最终审校。
- 如果输入实验结果表格存在错误，Agent 的分析也可能继承错误，因此建议保留人工核验环节。
- 对论文中的定量 claim，应以真实实验数据为准，避免夸大模型性能。
