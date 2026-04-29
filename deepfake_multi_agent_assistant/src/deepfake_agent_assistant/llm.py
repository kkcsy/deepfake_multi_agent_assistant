from __future__ import annotations

import hashlib
import textwrap
from abc import ABC, abstractmethod
from typing import Optional

from .config import Settings


class BaseLLM(ABC):
    """Abstract LLM interface used by all agents."""

    @abstractmethod
    def generate(self, system_prompt: str, user_prompt: str, agent_name: str = "") -> str:
        raise NotImplementedError


class OpenAILLM(BaseLLM):
    """OpenAI / OpenAI-compatible LLM backend.

    It supports two modes:
    - responses: client.responses.create(...)
    - chat: client.chat.completions.create(...)
    """

    def __init__(self, settings: Settings):
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise RuntimeError("请先安装 openai：pip install openai") from exc

        if not settings.api_key:
            raise RuntimeError("没有检测到 OPENAI_API_KEY。请在 .env 或系统环境变量中配置。")

        kwargs = {"api_key": settings.api_key}
        if settings.base_url:
            kwargs["base_url"] = settings.base_url

        self.client = OpenAI(**kwargs)
        self.settings = settings

    def generate(self, system_prompt: str, user_prompt: str, agent_name: str = "") -> str:
        if self.settings.api_mode == "responses":
            try:
                return self._responses(system_prompt, user_prompt)
            except Exception as exc:
                # Some OpenAI-compatible endpoints do not implement Responses API.
                # We fall back to Chat Completions so that the project remains usable.
                print(f"[Warning] Responses API 调用失败，自动切换到 chat 模式。错误：{exc}")
                return self._chat(system_prompt, user_prompt)

        if self.settings.api_mode == "chat":
            return self._chat(system_prompt, user_prompt)

        raise ValueError("api_mode 只能是 responses 或 chat。")

    def _responses(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.responses.create(
            model=self.settings.model,
            instructions=system_prompt,
            input=user_prompt,
            temperature=self.settings.temperature,
            max_output_tokens=self.settings.max_output_tokens,
        )
        text = getattr(response, "output_text", None)
        if text:
            return text.strip()
        return self._extract_response_text(response).strip()

    def _chat(self, system_prompt: str, user_prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.settings.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.settings.temperature,
            max_tokens=self.settings.max_output_tokens,
        )
        return (response.choices[0].message.content or "").strip()

    @staticmethod
    def _extract_response_text(response) -> str:
        chunks = []
        for item in getattr(response, "output", []) or []:
            for content in getattr(item, "content", []) or []:
                text = getattr(content, "text", None)
                if text:
                    chunks.append(text)
        return "\n".join(chunks)


class MockLLM(BaseLLM):
    """A deterministic mock backend for demos and offline tests."""

    def generate(self, system_prompt: str, user_prompt: str, agent_name: str = "") -> str:
        digest = hashlib.md5((agent_name + user_prompt).encode("utf-8")).hexdigest()[:8]
        role_hint = self._infer_role(agent_name)
        return textwrap.dedent(
            f"""
            【Mock 输出｜{agent_name or 'Agent'}｜ID={digest}】

            {role_hint}

            1. 该模块围绕深度伪造检测研究流程进行分析，重点关注跨数据集泛化、实验可复现性和论文表达质量。
            2. 从输入材料看，系统应优先处理文献逻辑、方法设计、代码风险、实验结论和最终写作整合五类问题。
            3. 建议在最终报告中明确说明：该多 Agent 工作流能够减少重复性文献整理和实验分析工作，并降低论文结论与实验表格不一致的风险。
            4. 对于深度伪造检测任务，报告应重点突出 FF++ 训练、跨数据集测试、AUC/AP/EER 指标、消融实验和鲁棒性验证。

            可填写表格的简短成果描述：
            我构建了一个面向深度伪造检测研究的多 Agent 协作科研助手，通过任务规划、文献分析、方法设计、代码检查、实验分析、论文写作和审稿式检查等多个 Agent 协同工作，辅助完成科研材料整理、实验结果归纳和论文表达优化，提高了研究流程的系统性与效率。
            """
        ).strip()

    @staticmethod
    def _infer_role(agent_name: str) -> str:
        mapping = {
            "PlannerAgent": "负责将科研任务拆解为文献、方法、代码、实验和写作子任务。",
            "LiteratureAgent": "负责梳理深度伪造检测相关工作和研究痛点。",
            "MethodAgent": "负责凝练方法动机、模块设计和创新点。",
            "CodeAgent": "负责检查代码结构、训练流程、评估流程和常见实现风险。",
            "ExperimentAgent": "负责分析跨数据集实验、消融实验和鲁棒性测试。",
            "WritingAgent": "负责生成论文级中文总结和英文表达。",
            "CriticAgent": "负责从审稿人视角指出逻辑漏洞和过度 claim 风险。",
            "CoordinatorAgent": "负责整合所有 Agent 输出并生成最终报告。",
        }
        return mapping.get(agent_name, "负责完成对应的科研辅助任务。")


def build_llm(settings: Settings) -> BaseLLM:
    provider = settings.provider.lower()
    if provider == "mock":
        return MockLLM()
    if provider == "openai":
        return OpenAILLM(settings)
    raise ValueError("provider 只能是 openai 或 mock。")
