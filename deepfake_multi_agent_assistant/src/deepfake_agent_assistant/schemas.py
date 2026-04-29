from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional


@dataclass
class AgentConfig:
    """Configuration for a single research agent."""

    key: str
    name: str
    role: str
    system_prompt: str
    depends_on: List[str] = field(default_factory=list)


@dataclass
class AgentResult:
    """Output produced by one agent."""

    key: str
    name: str
    role: str
    output: str

    def to_dict(self) -> Dict[str, str]:
        return asdict(self)


@dataclass
class ProjectInput:
    """All user-provided materials and automatically computed context."""

    task: str
    literature_context: str = ""
    code_context: str = ""
    experiment_context: str = ""
    experiment_summary: str = ""
    extra_context: str = ""


@dataclass
class RunConfig:
    provider: str = "openai"
    model: Optional[str] = None
    api_mode: str = "responses"
    output_dir: str = "outputs"
    temperature: float = 0.2
    max_output_tokens: int = 1800
    save_trace: bool = True
