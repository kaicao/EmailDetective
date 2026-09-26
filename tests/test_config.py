"""Tests for the env-driven `Settings` object."""

from __future__ import annotations

import pytest

from emaildetective.config import Settings


class TestSettingsDefaults:
    def test_defaults_match_documented_values(self, monkeypatch: pytest.MonkeyPatch) -> None:
        # Clear any host env so .env defaults aren't masked by the shell.
        for key in (
            "OLLAMA_HOST",
            "OLLAMA_MODEL",
            "OLLAMA_API_KEY",
            "LAYA_DEFAULT",
            "LAYA_DEVICE",
            "LAYA_MCP_COMMAND",
            "LAYA_MCP_ENABLED",
            "PHISHING_THRESHOLD",
            "AGENTOS_HOST",
            "AGENTOS_PORT",
        ):
            monkeypatch.delenv(key, raising=False)

        s = Settings()
        assert s.ollama_host == "http://localhost:11434"
        assert s.ollama_model == "minimax-m3:cloud"
        assert s.laya_default == "english"
        assert s.laya_device == "auto"
        assert s.laya_mcp_command == "laya-mcp-server"
        assert s.laya_mcp_enabled is True
        assert s.phishing_threshold == 0.5
        assert s.agentos_host == "0.0.0.0"
        assert s.agentos_port == 7777

    def test_env_overrides(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("OLLAMA_MODEL", "llama3.1")
        monkeypatch.setenv("AGENTOS_PORT", "9000")
        s = Settings()
        assert s.ollama_model == "llama3.1"
        assert s.agentos_port == 9000
