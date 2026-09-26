"""LLM factory — builds an `agno.models.ollama.Ollama` instance from config."""

from __future__ import annotations

from agno.models.ollama import Ollama

from emaildetective.models import LLMConfig


def build_llm(config: LLMConfig) -> Ollama:
    """Construct an Ollama-backed Agno model from an `LLMConfig`."""

    if config.provider != "ollama":
        raise ValueError(
            f"Unsupported LLM provider '{config.provider}'. Only 'ollama' is wired up."
        )

    return Ollama(
        id=config.model_id,
        host=config.host,
        api_key=config.api_key,
        timeout=config.timeout,
    )
