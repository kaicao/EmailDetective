# Contributing

Thanks for your interest in EmailDetective. This guide covers how to set up
a dev environment, run the tests, and submit changes.

## Development setup

```bash
# Clone your fork
git clone <your-fork-url> EmailDetective
cd EmailDetective

# Use the same Python version as the project
uv python install 3.12
uv venv --python 3.12
source .venv/bin/activate

# Install the package + every extra
uv pip install -e ".[mcp,dev]"
```

The `[dev]` extra pulls in `pytest` and `pytest-asyncio`. The `[mcp]`
extra installs `laya[mcp]` so the `laya-mcp-server` stdio binary is on
PATH for the agent to spawn.

## Running the tests

```bash
pytest
```

Tests are organised by module under `tests/`:

- `tests/test_config.py` — env-driven `Settings` defaults and overrides.
- `tests/test_models.py` — Pydantic `LLMConfig`, `PhishingMCPConfig`,
  `PhishingAgentConfig` validation and bounds.
- `tests/test_laya_detector.py` — `LayaPhishingDetector` against a
  mocked `laya.Router` (no checkpoint download required).
- `tests/test_agent.py` — `PhishingDetectionAgent` construction and the
  MCPTools wiring.
- `tests/test_main.py` — CLI subcommand parsing and `info` output.

`tests/conftest.py` adds `src/` to `sys.path` and provides shared
fixtures (`mocked_laya_router`, `detector`).

## Project conventions

- Python 3.12, type hints everywhere. Public APIs use Pydantic models
  (`models.py`) and `pydantic-settings` (`config.py`).
- LLM construction lives in `llm.py`; the Agno agent in `agent.py`;
  the FastAPI surface in `agentos.py`.
- New env vars go in `config.py` and `.env.example`. The default values
  in `.env.example` should match the defaults in code.

## Lint & format

This repo doesn't currently enforce a linter. The recommended setup is
`ruff`:

```bash
uv pip install ruff
ruff check src tests
ruff format src tests
```

If you add a `pyproject.toml` `[tool.ruff]` block, the formatter and
linter will run from there.

## Pull requests

1. Fork the repo and create a feature branch (`git switch -c feature/foo`).
2. Make your change, add tests, run `pytest`.
3. Open a PR that explains the problem and the approach.
4. If your change touches the public API, update the README and the
   `__init__.py` re-exports.

## Reporting bugs

Open a GitHub issue with:

- Python version (`python --version`)
- Output of `emaildetective info`
- The smallest repro that fails
- Any stack traces

## License

By contributing you agree that your contributions will be licensed under
the Apache License 2.0 (see [LICENSE](LICENSE)).
