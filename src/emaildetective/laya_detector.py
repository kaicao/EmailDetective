"""Laya-backed phishing detector.

Wraps Laya's `Router` so a piece of content (an email or arbitrary text)
can be scored for phishing intent as a typed `noul` decision.
"""

from __future__ import annotations

from typing import Any, Mapping

from pydantic import BaseModel, Field

# `noul` returns P(true) given two semantic slots: `false` and `true`.
# Per the Laya docs, the model renders these slots verbatim, so we use
# semantic (non-boolean-word) labels to avoid label-bias issues.
_PHISHING_QUESTION: dict[str, Any] = {
    "type": "noul",
    "instructions": (
        "Is this content a phishing attempt — i.e. does it try to trick the "
        "reader into revealing credentials, sending money, installing malware, "
        "or clicking a malicious link by impersonating a trusted party?"
    ),
    "criteria": {
        "true": "yes, this is a phishing attempt",
        "false": "no, this is a legitimate message",
    },
    "labels": {"true": "A", "false": "B"},
}


class PhishingVerdict(BaseModel):
    """Structured result from a single phishing classification."""

    is_phishing: bool
    probability: float = Field(ge=0.0, le=1.0, description="P(phishing).")
    threshold: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    routed_model: str
    routing_reason: str
    raw: dict[str, Any]


class LayaPhishingDetector:
    """Use a Laya `Router` to classify content as phishing or legitimate."""

    def __init__(
        self,
        router: Any | None = None,
        threshold: float = 0.5,
    ) -> None:
        if not 0.0 <= threshold <= 1.0:
            raise ValueError("threshold must be in [0.0, 1.0]")
        # Lazy import: `laya` is heavy (torch, transformers) and we want
        # `emaildetective` to import cheaply for type-checking and tests.
        from laya import Router

        self._router = router or Router()
        self._threshold = threshold

    @classmethod
    def from_settings(cls, settings: Any) -> "LayaPhishingDetector":
        """Build a detector from `emaildetective.config.Settings`."""

        from laya import Router

        router = Router(
            preload=settings.laya_preload,
            default=settings.laya_default,
        )
        return cls(router=router, threshold=settings.phishing_threshold)

    def classify(self, content: str | Mapping[str, Any]) -> PhishingVerdict:
        """Score arbitrary content. `content` can be a plain string or a state dict."""

        state = content if isinstance(content, Mapping) else {"body": content}

        result = self._router.predict(state, {"is_phishing": _PHISHING_QUESTION})
        answer = result["answers"]["is_phishing"]
        probability = float(answer["noul"])
        confidence = float(answer.get("confidence", 0.0))

        routing = result.get("routing", {})
        return PhishingVerdict(
            is_phishing=probability >= self._threshold,
            probability=probability,
            threshold=self._threshold,
            confidence=confidence,
            routed_model=str(routing.get("model", "unknown")),
            routing_reason=str(routing.get("reason", "")),
            raw=result,
        )


def build_laya_detector(settings: Any | None = None) -> LayaPhishingDetector:
    """Convenience builder; loads default settings when none are supplied."""

    if settings is None:
        from emaildetective.config import get_settings

        settings = get_settings()

    return LayaPhishingDetector.from_settings(settings)
