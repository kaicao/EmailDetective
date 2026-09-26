"""AgentOS wiring — exposes the phishing agent over FastAPI/REST.

The resulting app can be served via:

    python -m emaildetective.main serve --reload
    # or
    uvicorn emaildetective.agentos:app --reload

It registers the Laya MCP server as a tool on the agent and mounts all of
AgentOS's default routes (`/info`, `/config`, `/agents/{id}/runs`, sessions,
memory, knowledge, traces, schedules, etc.).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from fastapi import FastAPI

from emaildetective.agent import PhishingDetectionAgent
from emaildetective.config import Settings, get_settings


def _default_db_path() -> Path:
    return Path(".data/emaildetective.db")


def build_agent_os(
    settings: Settings | None = None,
    db_path: Path | str | None = None,
) -> tuple[Any, FastAPI]:
    """Build (and return) an `AgentOS` instance + its FastAPI app.

    Parameters
    ----------
    settings:
        Optional pre-loaded settings. When `None`, defaults from `.env` are used.
    db_path:
        Filesystem path for the SQLite database that stores sessions, traces,
        and the default AgentOS state. When `None`, defaults to
        `.data/emaildetective.db` (auto-created).
    """

    from agno.db.sqlite import SqliteDb
    from agno.os import AgentOS

    settings = settings or get_settings()
    db_file = Path(db_path) if db_path else _default_db_path()
    db_file.parent.mkdir(parents=True, exist_ok=True)

    agent_wrapper = PhishingDetectionAgent.from_settings(settings)
    # `AgentOS` consumes the underlying agno `Agent`, not our wrapper.
    agno_agent = agent_wrapper.agno_agent
    # A stable id is what callers will hit at `POST /agents/{id}/runs`.
    if not getattr(agno_agent, "id", None):
        agno_agent.id = agent_wrapper.config.name.lower().replace(" ", "-")

    db = SqliteDb(db_file=str(db_file))

    agent_os = AgentOS(
        id="emaildetective-os",
        agents=[agno_agent],
        db=db,
        tracing=True,
    )
    return agent_os, agent_os.get_app()


def build_app(
    settings: Settings | None = None,
    db_path: Path | str | None = None,
) -> FastAPI:
    """Return the configured FastAPI app for `uvicorn emaildetective.agentos:app`."""

    _, app = build_agent_os(settings=settings, db_path=db_path)
    return app


# Module-level handle for `uvicorn emaildetective.agentos:app`.
app = build_app()


if __name__ == "__main__":  # pragma: no cover
    from agno.os import AgentOS

    agent_os, _ = build_agent_os()
    settings = get_settings()
    agent_os.serve(
        app="emaildetective.agentos:app",
        host=settings.agentos_host,
        port=settings.agentos_port,
        reload=settings.agentos_reload,
    )
