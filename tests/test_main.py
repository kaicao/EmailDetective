"""Smoke tests for the CLI entry point."""

from __future__ import annotations

import io
import json
from contextlib import redirect_stdout

import pytest

from emaildetective.main import _build_arg_parser, _read_content, main


class TestCLI:
    def test_parser_has_expected_subcommands(self) -> None:
        parser = _build_arg_parser()
        # The `choices` for the `command` dest are derived from subparsers.
        actions = parser._actions  # noqa: SLF001
        sub_action = next(
            a for a in actions if getattr(a, "dest", None) == "command"
        )
        assert "agent" in sub_action.choices
        assert "detect" in sub_action.choices
        assert "serve" in sub_action.choices
        assert "info" in sub_action.choices

    def test_info_prints_settings(self) -> None:
        buf = io.StringIO()
        with redirect_stdout(buf):
            main(["info"])
        out = buf.getvalue()
        assert "ollama_model" in out
        assert "minimax-m3:cloud" in out

    def test_read_content_from_string(self) -> None:
        assert _read_content("hello") == "hello"

    def test_read_content_from_stdin(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.stdin", io.StringIO("hello stdin"))
        assert _read_content("-") == "hello stdin"
