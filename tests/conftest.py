"""Pytest configuration: ensure `src/` is importable and share fixtures."""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

_SRC = Path(__file__).resolve().parents[1] / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from emaildetective.laya_detector import LayaPhishingDetector  # noqa: E402


@pytest.fixture
def mocked_laya_router() -> MagicMock:
    """Return a MagicMock standing in for `laya.Router`."""

    router = MagicMock()
    router.predict.return_value = {
        "answers": {
            "is_phishing": {
                "noul": 0.92,
                "confidence": 0.81,
            }
        },
        "routing": {
            "model": "english",
            "reason": "Latin script and looks English",
        },
    }
    return router


@pytest.fixture
def detector(mocked_laya_router: MagicMock) -> LayaPhishingDetector:
    """Return a `LayaPhishingDetector` wrapping the mocked Router."""

    return LayaPhishingDetector(router=mocked_laya_router, threshold=0.5)
