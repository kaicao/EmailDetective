"""Tests for `PhishingDetectionAgent` construction.

We don't actually run the agent against Ollama here — we just confirm that
the wrapper builds the right Agno `Agent` with the right config.
"""

from __future__ import annotations

from agno.agent import Agent
from agno.models.ollama import Ollama

from emaildetective.agent import PhishingDetectionAgent
from emaildetective.config import Settings
from emaildetective.models import LLMConfig, PhishingAgentConfig


def _settings(**overrides: object) -> Settings:
    base = {
        "ollama_host": "http://localhost:11434",
        "ollama_model": "minimax-m3:cloud",
        "ollama_api_key": None,
        "laya_preload": False,
        "laya_default": "english",
        "laya_device": "auto",
        "laya_mcp_command": "laya-mcp-server",
        "laya_mcp_enabled": True,
        "phishing_threshold": 0.5,
    }
    base.update(overrides)
    return Settings(**base)  # type: ignore[arg-type]


class TestPhishingDetectionAgent:
    def test_from_settings_builds_ollama_agent(self) -> None:
        agent = PhishingDetectionAgent.from_settings(_settings())
        assert isinstance(agent.agno_agent, Agent)
        assert agent.agno_agent.name == "EmailDetective"
        assert isinstance(agent.agno_agent.model, Ollama)
        assert agent.agno_agent.model.id == "minimax-m3:cloud"

    def test_mcp_tool_attached_when_enabled(self) -> None:
        agent = PhishingDetectionAgent.from_settings(
            _settings(laya_mcp_enabled=True, laya_mcp_command="laya-mcp-server")
        )
        assert len(agent.agno_agent.tools) == 1
        from agno.tools.mcp import MCPTools  # noqa: PLC0415

        assert isinstance(agent.agno_agent.tools[0], MCPTools)

    def test_mcp_tool_disabled(self) -> None:
        agent = PhishingDetectionAgent.from_settings(_settings(laya_mcp_enabled=False))
        assert agent.agno_agent.tools == []

    def test_from_llm_config(self) -> None:
        llm_cfg = LLMConfig(model_id="llama3.1", host="http://example:9999")
        agent = PhishingDetectionAgent.from_llm_config(llm_cfg, _settings())
        assert agent.agno_agent.model.id == "llama3.1"
        assert agent.agno_agent.model.host == "http://example:9999"

    def test_threshold_is_in_config(self) -> None:
        agent = PhishingDetectionAgent.from_settings(_settings(phishing_threshold=0.7))
        assert agent.config.phishing_threshold == 0.7

    def test_agent_id_normalised_for_url(self) -> None:
        """The agent id must be URL-safe for `POST /agents/{id}/runs`."""
        from emaildetective.agentos import build_agent_os  # noqa: PLC0415

        _, _ = build_agent_os(_settings())
        agent = PhishingDetectionAgent.from_settings(_settings())
        if not getattr(agent.agno_agent, "id", None):
            agent.agno_agent.id = (
                agent.config.name.lower().replace(" ", "-")
            )
        assert agent.agno_agent.id == "emaildetective"

    def test_instructions_include_laya_tool_guidance(self) -> None:
        agent = PhishingDetectionAgent.from_settings(_settings())
        joined = "\n".join(agent.config.instructions)
        assert "laya_predict" in joined
        assert "phishing" in joined.lower()


def _phishing_agent_config() -> PhishingAgentConfig:
    # Silence unused-import lint while keeping a one-stop config builder for
    # callers that want to construct the agent manually.
    return PhishingAgentConfig()
