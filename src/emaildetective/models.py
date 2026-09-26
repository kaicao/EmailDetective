"""Pydantic models for the LLM backend and the phishing detection agent."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class LLMConfig(BaseModel):
    """Typed configuration for the LLM the agent talks to (Ollama-backed)."""

    model_config = ConfigDict(frozen=False, extra="forbid")

    provider: Literal["ollama"] = "ollama"
    model_id: str = Field(default="minimax-m3:cloud", description="Ollama model tag.")
    host: str = Field(
        default="http://localhost:11434",
        description="Base URL of the Ollama server.",
    )
    api_key: str | None = Field(
        default=None,
        description="API key. Required for Ollama Cloud; leave None for a local server.",
    )
    timeout: float | None = Field(default=None, ge=0)
    temperature: float | None = Field(default=None, ge=0)
    markdown: bool = True
    request_params: dict[str, Any] = Field(default_factory=dict)


class PhishingMCPConfig(BaseModel):
    """Configuration for connecting the agent to the Laya MCP stdio server."""

    model_config = ConfigDict(extra="forbid")

    enabled: bool = True
    command: str = "laya-mcp-server"
    env: dict[str, str] = Field(default_factory=dict)
    include_tools: list[str] | None = None
    exclude_tools: list[str] | None = None
    tool_name_prefix: str | None = None
    timeout_seconds: int = 30


class PhishingAgentConfig(BaseModel):
    """High-level configuration for the phishing detection agent."""

    model_config = ConfigDict(extra="forbid")

    name: str = "EmailDetective"
    description: str = (
        "Detects whether content (e.g. an email) is a phishing attempt using Laya."
    )
    instructions: list[str] = Field(
        default_factory=lambda: [
            "You are EmailDetective, a phishing-detection agent.",
            "When given content (an email, message, or arbitrary text):",
            "1. Use the Laya MCP tools (`laya_predict`, `laya_route`) to score the "
            "content as phishing vs. legitimate.",
            "2. Report a clear verdict, the calibrated P(phishing), and the routing "
            "decision (which Laya checkpoint was used).",
            "3. Briefly cite the strongest phishing signals you found.",
            "4. If confidence is low, recommend a human review.",
        ]
    )
    markdown: bool = True
    llm: LLMConfig = Field(default_factory=LLMConfig)
    mcp: PhishingMCPConfig = Field(default_factory=PhishingMCPConfig)
    phishing_threshold: float = Field(
        default=0.5,
        ge=0.0,
        le=1.0,
        description="Threshold above which a P(phishing) score counts as phishing.",
    )
