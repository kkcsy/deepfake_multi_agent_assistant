from __future__ import annotations

from typing import Dict, List

from .agents import build_agents, default_agent_sequence
from .llm import BaseLLM
from .schemas import AgentConfig, AgentResult, ProjectInput


class MultiAgentPipeline:
    """Sequential multi-agent workflow for deepfake detection research."""

    def __init__(self, llm: BaseLLM):
        self.llm = llm
        self.agents: Dict[str, AgentConfig] = build_agents()
        self.sequence: List[str] = default_agent_sequence()

    def run(self, project_input: ProjectInput) -> List[AgentResult]:
        results: List[AgentResult] = []
        result_map: Dict[str, AgentResult] = {}

        for key in self.sequence:
            agent = self.agents[key]
            print(f"\n========== 运行 {agent.name}：{agent.role} ==========")
            user_prompt = self._build_user_prompt(agent, project_input, result_map)
            output = self.llm.generate(agent.system_prompt, user_prompt, agent_name=agent.name)
            result = AgentResult(key=key, name=agent.name, role=agent.role, output=output)
            results.append(result)
            result_map[key] = result
        return results

    def _build_user_prompt(
        self,
        agent: AgentConfig,
        project_input: ProjectInput,
        result_map: Dict[str, AgentResult],
    ) -> str:
        previous_outputs = []
        dependency_keys = agent.depends_on or []
        for dep_key in dependency_keys:
            if dep_key in result_map:
                dep = result_map[dep_key]
                previous_outputs.append(
                    f"===== {dep.name} / {dep.role} 输出 =====\n{dep.output}\n"
                )

        previous_text = "\n".join(previous_outputs) if previous_outputs else "[无前序 Agent 输出]"

        return f"""
# 当前 Agent
{agent.name}：{agent.role}

# 用户任务
{project_input.task}

# 文献 / 论文 / 笔记材料
{project_input.literature_context or '[未提供文献材料]'}

# 代码材料
{project_input.code_context or '[未提供代码材料]'}

# 实验结果材料
{project_input.experiment_context or '[未提供实验结果文件内容]'}

# 实验结果自动统计摘要
{project_input.experiment_summary or '[未提供或未能生成实验统计摘要]'}

# 其他补充材料
{project_input.extra_context or '[无]'}

# 前序 Agent 输出
{previous_text}

请严格基于以上材料和你的角色完成任务。若材料不足，请明确说明，不要编造实验结果。
""".strip()
