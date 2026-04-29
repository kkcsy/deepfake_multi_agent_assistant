from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from dotenv import load_dotenv


@dataclass
class Settings:
    provider: str
    api_key: Optional[str]
    model: str
    api_mode: str
    base_url: Optional[str]
    temperature: float
    max_output_tokens: int


def load_settings(
    provider: Optional[str] = None,
    model: Optional[str] = None,
    api_mode: Optional[str] = None,
    temperature: Optional[float] = None,
    max_output_tokens: Optional[int] = None,
) -> Settings:
    load_dotenv()

    return Settings(
        provider=provider or os.getenv("LLM_PROVIDER", "openai"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model=model or os.getenv("OPENAI_MODEL", "gpt-5.5"),
        api_mode=api_mode or os.getenv("OPENAI_API_MODE", "responses"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        temperature=temperature if temperature is not None else float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
        max_output_tokens=max_output_tokens if max_output_tokens is not None else int(os.getenv("OPENAI_MAX_OUTPUT_TOKENS", "1800")),
    )
