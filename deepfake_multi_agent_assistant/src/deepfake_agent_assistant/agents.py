from __future__ import annotations

from typing import Dict, List

from .prompts import (
    PLANNER_PROMPT,
    LITERATURE_PROMPT,
    METHOD_PROMPT,
    CODE_PROMPT,
    EXPERIMENT_PROMPT,
    WRITING_PROMPT,
    CRITIC_PROMPT,
    COORDINATOR_PROMPT,
)
from .schemas import AgentConfig


def build_agents() -> Dict[str, AgentConfig]:
    """Build the complete multi-agent workflow."""

    return {
        "planner": AgentConfig(
            key="planner",
            name="PlannerAgent",
            role="科研任务规划 Agent",
            system_prompt=PLANNER_PROMPT,
        ),
        "literature": AgentConfig(
            key="literature",
            name="LiteratureAgent",
            role="文献分析 Agent",
            system_prompt=LITERATURE_PROMPT,
            depends_on=["planner"],
        ),
        "method": AgentConfig(
            key="method",
            name="MethodAgent",
            role="方法设计 Agent",
            system_prompt=METHOD_PROMPT,
            depends_on=["planner", "literature"],
        ),
        "code": AgentConfig(
            key="code",
            name="CodeAgent",
            role="代码与实验实现 Agent",
            system_prompt=CODE_PROMPT,
            depends_on=["planner", "method"],
        ),
        "experiment": AgentConfig(
            key="experiment",
            name="ExperimentAgent",
            role="实验分析 Agent",
            system_prompt=EXPERIMENT_PROMPT,
            depends_on=["planner", "method", "code"],
        ),
        "writing": AgentConfig(
            key="writing",
            name="WritingAgent",
            role="论文写作 Agent",
            system_prompt=WRITING_PROMPT,
            depends_on=["literature", "method", "experiment"],
        ),
        "critic": AgentConfig(
            key="critic",
            name="CriticAgent",
            role="审稿式检查 Agent",
            system_prompt=CRITIC_PROMPT,
            depends_on=["literature", "method", "code", "experiment", "writing"],
        ),
        "coordinator": AgentConfig(
            key="coordinator",
            name="CoordinatorAgent",
            role="最终汇总 Agent",
            system_prompt=COORDINATOR_PROMPT,
            depends_on=["planner", "literature", "method", "code", "experiment", "writing", "critic"],
        ),
    }


def default_agent_sequence() -> List[str]:
    return [
        "planner",
        "literature",
        "method",
        "code",
        "experiment",
        "writing",
        "critic",
        "coordinator",
    ]
