"""Environment-driven settings loaded via python-dotenv + pydantic-settings."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env once at import time so every Settings instance picks it up.
_PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(_PROJECT_ROOT / ".env", override=False)


class Settings(BaseSettings):
    """Runtime configuration loaded from `.env` (and the process environment)."""

    model_config = SettingsConfigDict(
        env_file=str(_PROJECT_ROOT / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Ollama / LLM -------------------------------------------------------
    ollama_host: str = "http://localhost:11434"
    ollama_model: str = "minimax-m3:cloud"
    ollama_api_key: str | None = None
    ollama_timeout: float | None = None

    # --- Laya (local Router) ------------------------------------------------
    laya_preload: bool = False
    laya_default: Literal["english", "multilingual"] = "english"
    laya_device: Literal["auto", "cpu", "cuda", "mps", "xpu"] = "auto"

    # --- Laya MCP server (stdio) --------------------------------------------
    laya_mcp_command: str = "laya-mcp-server"
    laya_mcp_enabled: bool = True

    # --- LLM runtime --------------------------------------------------------
    llm_temperature: float | None = None
    llm_markdown: bool = True

    # --- Detection thresholds -----------------------------------------------
    phishing_threshold: float = 0.5

    # --- AgentOS server -----------------------------------------------------
    agentos_host: str = "0.0.0.0"
    agentos_port: int = 7777
    agentos_db_path: str = ".data/emaildetective.db"
    agentos_reload: bool = False

    @property
    def project_root(self) -> Path:
        return _PROJECT_ROOT


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""

    return Settings()
