"""Tests for `LayaPhishingDetector`.

These tests use a mocked `Router` so they don't require the Laya
checkpoint download or a torch-enabled environment.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from emaildetective.laya_detector import (
    LayaPhishingDetector,
    PhishingVerdict,
)


class TestPhishingVerdict:
    def test_construction(self) -> None:
        verdict = PhishingVerdict(
            is_phishing=True,
            probability=0.9,
            threshold=0.5,
            confidence=0.8,
            routed_model="english",
            routing_reason="Latin script",
            raw={},
        )
        assert verdict.is_phishing is True
        assert verdict.probability == 0.9


class TestLayaPhishingDetector:
    def test_invalid_threshold_rejected(self) -> None:
        with pytest.raises(ValueError):
            LayaPhishingDetector(router=MagicMock(), threshold=1.5)

    def test_classify_calls_router_with_noul_question(
        self, detector: LayaPhishingDetector, mocked_laya_router: MagicMock
    ) -> None:
        verdict = detector.classify("Click here to verify your account")
        mocked_laya_router.predict.assert_called_once()
        state, questions = mocked_laya_router.predict.call_args.args
        assert "body" in state
        assert "is_phishing" in questions
        assert questions["is_phishing"]["type"] == "noul"
        assert verdict.is_phishing is True
        assert verdict.probability == pytest.approx(0.92)
        assert verdict.routed_model == "english"

    def test_classify_with_dict_state(
        self, detector: LayaPhishingDetector, mocked_laya_router: MagicMock
    ) -> None:
        verdict = detector.classify({"from": "a@b.com", "body": "hello"})
        state = mocked_laya_router.predict.call_args.args[0]
        assert state == {"from": "a@b.com", "body": "hello"}
        assert isinstance(verdict, PhishingVerdict)

    def test_threshold_decision(self, mocked_laya_router: MagicMock) -> None:
        # 0.4 < 0.5 threshold → is_phishing False
        mocked_laya_router.predict.return_value["answers"]["is_phishing"]["noul"] = 0.4
        detector = LayaPhishingDetector(router=mocked_laya_router, threshold=0.5)
        verdict = detector.classify("anything")
        assert verdict.is_phishing is False
        assert verdict.probability == pytest.approx(0.4)

    def test_labels_avoid_boolean_words(self) -> None:
        """The `noul` question must use semantic `A`/`B` labels per Laya guidance."""
        detector = LayaPhishingDetector(router=MagicMock())
        # Build the question by mirroring what `classify` sends.
        from emaildetective.laya_detector import (  # noqa: PLC0415
            LayaPhishingDetector as _D,
        )

        # Reach into the private helper to inspect the question schema.
        # It's a module-level constant; just assert its shape.
        from emaildetective import laya_detector as mod  # noqa: PLC0415

        q = mod._PHISHING_QUESTION
        assert q["labels"]["true"] == "A"
        assert q["labels"]["false"] == "B"
        assert q["criteria"]["true"] != "true"  # not the literal word
        assert q["criteria"]["false"] != "false"
