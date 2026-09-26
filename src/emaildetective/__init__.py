"""EmailDetective — phishing detection agent powered by Agno, Laya, and Ollama."""

from emaildetective.agent import PhishingDetectionAgent, build_phishing_agent
from emaildetective.agentos import build_agent_os, build_app
from emaildetective.config import Settings, get_settings
from emaildetective.llm import build_llm
from emaildetective.laya_detector import (
    LayaPhishingDetector,
    PhishingVerdict,
    build_laya_detector,
)
from emaildetective.models import (
    LLMConfig,
    PhishingAgentConfig,
    PhishingMCPConfig,
)

__all__ = [
    "LLMConfig",
    "LayaPhishingDetector",
    "PhishingAgentConfig",
    "PhishingDetectionAgent",
    "PhishingMCPConfig",
    "PhishingVerdict",
    "Settings",
    "build_agent_os",
    "build_app",
    "build_laya_detector",
    "build_llm",
    "build_phishing_agent",
    "get_settings",
]
