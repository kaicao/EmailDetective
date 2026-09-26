"""Agno agent wiring Ollama + the Laya MCP server together."""

from __future__ import annotations

import asyncio
from typing import Any

from agno.agent import Agent

from emaildetective.config import Settings, get_settings
from emaildetective.llm import build_llm
from emaildetective.models import LLMConfig, PhishingAgentConfig


def _to_agent_config(llm: LLMConfig, settings: Settings) -> PhishingAgentConfig:
    return PhishingAgentConfig(
        llm=llm,
        mcp=type(  # type: ignore[call-arg]
            PhishingAgentConfig.model_fields["mcp"].default_factory()
        )(
            enabled=settings.laya_mcp_enabled,
            command=settings.laya_mcp_command,
            env={
                "LAYA_DEVICE": settings.laya_device,
                "LAYA_PRELOAD": "1" if settings.laya_preload else "0",
                "LAYA_DEFAULT": settings.laya_default,
            },
        ),
        markdown=settings.llm_markdown,
        phishing_threshold=settings.phishing_threshold,
    )


class PhishingDetectionAgent:
    """Thin wrapper around an `agno.Agent` that owns its own async lifecycle."""

    def __init__(self, agent: Agent, config: PhishingAgentConfig) -> None:
        self._agent = agent
        self._config = config
        self._mcp_tools: list[Any] = []

    @classmethod
    def from_settings(cls, settings: Settings | None = None) -> "PhishingDetectionAgent":
        settings = settings or get_settings()
        llm_cfg = LLMConfig(
            model_id=settings.ollama_model,
            host=settings.ollama_host,
            api_key=settings.ollama_api_key,
            timeout=settings.ollama_timeout,
            temperature=settings.llm_temperature,
            markdown=settings.llm_markdown,
        )
        return cls.from_llm_config(llm_cfg, settings)

    @classmethod
    def from_llm_config(
        cls,
        llm_cfg: LLMConfig,
        settings: Settings | None = None,
    ) -> "PhishingDetectionAgent":
        settings = settings or get_settings()
        agent_cfg = _to_agent_config(llm_cfg, settings)

        model = build_llm(agent_cfg.llm)

        tools: list[Any] = []
        if agent_cfg.mcp.enabled:
            from agno.tools.mcp import MCPTools

            mcp_kwargs: dict[str, Any] = {
                "command": agent_cfg.mcp.command,
                "env": agent_cfg.mcp.env or None,
                "timeout_seconds": agent_cfg.mcp.timeout_seconds,
            }
            if agent_cfg.mcp.include_tools is not None:
                mcp_kwargs["include_tools"] = agent_cfg.mcp.include_tools
            if agent_cfg.mcp.exclude_tools is not None:
                mcp_kwargs["exclude_tools"] = agent_cfg.mcp.exclude_tools
            if agent_cfg.mcp.tool_name_prefix is not None:
                mcp_kwargs["tool_name_prefix"] = agent_cfg.mcp.tool_name_prefix

            tools.append(MCPTools(**mcp_kwargs))

        agent = Agent(
            name=agent_cfg.name,
            description=agent_cfg.description,
            instructions=agent_cfg.instructions,
            model=model,
            tools=tools,
            markdown=agent_cfg.markdown,
        )
        return cls(agent, agent_cfg)

    @property
    def agno_agent(self) -> Agent:
        return self._agent

    @property
    def config(self) -> PhishingAgentConfig:
        return self._config

    async def aprint_response(
        self,
        input: str,
        *,
        stream: bool = True,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        await self._agent.aprint_response(
            input=input,
            stream=stream,
            session_id=session_id,
            user_id=user_id,
        )

    def print_response(
        self,
        input: str,
        *,
        stream: bool = True,
        session_id: str | None = None,
        user_id: str | None = None,
    ) -> None:
        self._agent.print_response(
            input=input,
            stream=stream,
            session_id=session_id,
            user_id=user_id,
        )


def build_phishing_agent(
    settings: Settings | None = None,
) -> PhishingDetectionAgent:
    """Convenience builder mirroring the other `build_*` factories."""

    return PhishingDetectionAgent.from_settings(settings)


async def _amain() -> None:  # pragma: no cover - manual smoke test
    agent = build_phishing_agent()
    await agent.aprint_response(
        "Analyze this email and tell me if it's a phishing attempt:\n\n"
        "Subject: URGENT - Your account will be suspended\n"
        "From: support@paypa1-security.com\n"
        "Body: Click http://paypa1-login.example/verify to keep your account active.",
        stream=True,
    )


if __name__ == "__main__":  # pragma: no cover
    asyncio.run(_amain())
