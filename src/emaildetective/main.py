"""Console entry point for EmailDetective."""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from emaildetective.agent import PhishingDetectionAgent, build_phishing_agent
from emaildetective.config import get_settings
from emaildetective.laya_detector import build_laya_detector


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="emaildetective",
        description="Detect phishing content using an Agno agent + Laya + Ollama.",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_agent = sub.add_parser("agent", help="Run the Agno agent on given text.")
    p_agent.add_argument(
        "--no-stream",
        action="store_true",
        help="Disable streaming output from the Agno agent.",
    )
    p_agent.add_argument(
        "content",
        nargs="?",
        default="-",
        help="Content to classify. Use '-' (default) to read from stdin.",
    )

    p_detect = sub.add_parser(
        "detect",
        help="Run the local Laya Router directly (no LLM).",
    )
    p_detect.add_argument(
        "content",
        nargs="?",
        default="-",
        help="Content to classify. Use '-' (default) to read from stdin.",
    )

    p_serve = sub.add_parser(
        "serve",
        help="Run the AgentOS REST API (FastAPI/Uvicorn).",
    )
    p_serve.add_argument(
        "--host",
        default=None,
        help="Override AGENTOS_HOST (default: from .env, 0.0.0.0).",
    )
    p_serve.add_argument(
        "--port",
        type=int,
        default=None,
        help="Override AGENTOS_PORT (default: from .env, 7777).",
    )
    p_serve.add_argument(
        "--reload",
        action="store_true",
        help="Auto-reload on code changes (dev only).",
    )
    p_serve.add_argument(
        "--db-path",
        default=None,
        help="Override AGENTOS_DB_PATH (default: from .env).",
    )

    p_info = sub.add_parser("info", help="Print current settings.")
    return parser


def _run_serve(
    host: str | None,
    port: int | None,
    reload: bool,
    db_path: str | None,
) -> None:
    from agno.os import AgentOS

    from emaildetective.agentos import build_agent_os

    settings = get_settings()
    agent_os, _ = build_agent_os(
        settings=settings,
        db_path=db_path or settings.agentos_db_path,
    )
    agent_os.serve(
        app="emaildetective.agentos:app",
        host=host or settings.agentos_host,
        port=port or settings.agentos_port,
        reload=reload or settings.agentos_reload,
    )


def _read_content(value: str) -> str:
    if value == "-":
        return sys.stdin.read()
    if "\n" in value or Path(value).is_file():
        path = Path(value)
        if path.is_file():
            return path.read_text(encoding="utf-8")
    return value


async def _run_agent(content: str, stream: bool) -> None:
    agent: PhishingDetectionAgent = build_phishing_agent()
    await agent.aprint_response(input=content, stream=stream)

def _run_detect(content: str) -> None:
    detector = build_laya_detector()
    verdict = detector.classify(content)
    print(f"is_phishing     : {verdict.is_phishing}")
    print(f"probability     : {verdict.probability:.4f}")
    print(f"confidence      : {verdict.confidence:.4f}")
    print(f"threshold       : {verdict.threshold:.2f}")
    print(f"routed_model    : {verdict.routed_model}")
    print(f"routing_reason  : {verdict.routing_reason}")


def _run_info() -> None:
    settings = get_settings()
    print(f"ollama_host       : {settings.ollama_host}")
    print(f"ollama_model      : {settings.ollama_model}")
    print(f"ollama_api_key    : {'set' if settings.ollama_api_key else 'unset'}")
    print(f"laya_preload      : {settings.laya_preload}")
    print(f"laya_default      : {settings.laya_default}")
    print(f"laya_device       : {settings.laya_device}")
    print(f"laya_mcp_enabled  : {settings.laya_mcp_enabled}")
    print(f"laya_mcp_command  : {settings.laya_mcp_command}")
    print(f"phishing_threshold: {settings.phishing_threshold}")


def main(argv: list[str] | None = None) -> None:
    parser = _build_arg_parser()
    args = parser.parse_args(argv)

    if args.command in {"agent", "detect"}:
        content = _read_content(args.content)
        if args.command == "agent":
            asyncio.run(_run_agent(content, stream=not args.no_stream))
        else:
            _run_detect(content)
    elif args.command == "serve":
        _run_serve(args.host, args.port, args.reload, args.db_path)
    elif args.command == "info":
        _run_info()
    else:  # pragma: no cover - argparse enforces choices
        parser.error(f"unknown command: {args.command}")


if __name__ == "__main__":
    main()
