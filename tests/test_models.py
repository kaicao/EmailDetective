"""Tests for the typed Pydantic configuration models."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from emaildetective.models import (
    LLMConfig,
    PhishingAgentConfig,
    PhishingMCPConfig,
)


class TestLLMConfig:
    def test_defaults_match_project_spec(self) -> None:
        cfg = LLMConfig()
        assert cfg.provider == "ollama"
        assert cfg.model_id == "minimax-m3:cloud"
        assert cfg.host == "http://localhost:11434"
        assert cfg.api_key is None
        assert cfg.markdown is True

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            LLMConfig(unknown_field="x")  # type: ignore[call-arg]

    def test_threshold_bounds(self) -> None:
        with pytest.raises(ValidationError):
            LLMConfig(temperature=-0.1)


class TestPhishingMCPConfig:
    def test_defaults(self) -> None:
        cfg = PhishingMCPConfig()
        assert cfg.enabled is True
        assert cfg.command == "laya-mcp-server"
        assert cfg.timeout_seconds == 30

    def test_extra_fields_forbidden(self) -> None:
        with pytest.raises(ValidationError):
            PhishingMCPConfig(unknown=1)  # type: ignore[call-arg]


class TestPhishingAgentConfig:
    def test_defaults(self) -> None:
        cfg = PhishingAgentConfig()
        assert cfg.name == "EmailDetective"
        assert cfg.phishing_threshold == 0.5
        assert isinstance(cfg.llm, LLMConfig)
        assert isinstance(cfg.mcp, PhishingMCPConfig)
        assert len(cfg.instructions) > 0

    def test_threshold_bounds(self) -> None:
        with pytest.raises(ValidationError):
            PhishingAgentConfig(phishing_threshold=1.5)
        with pytest.raises(ValidationError):
            PhishingAgentConfig(phishing_threshold=-0.1)

    def test_nested_llm_override(self) -> None:
        cfg = PhishingAgentConfig(
            llm=LLMConfig(model_id="llama3.1", host="http://example:9999"),
        )
        assert cfg.llm.model_id == "llama3.1"
        assert cfg.llm.host == "http://example:9999"
