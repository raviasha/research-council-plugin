"""Canonical models and shared helpers for Research Council."""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any, Mapping, Optional, Sequence


class Disposition(str, Enum):
    APPROVED = "Approved"
    APPROVED_WITH_CAUTION = "Approved-with-caveat"
    CONTESTED = "Contested"
    INSUFFICIENT = "Insufficient-evidence"
    REJECTED = "Rejected"


class ClaimType(str, Enum):
    FACT = "FACT"
    INFERENCE = "INFERENCE"
    ESTIMATE = "ESTIMATE"
    ATTRIBUTION = "ATTRIBUTION"
    UNKNOWN = "UNKNOWN"


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"
    path: Optional[str] = None
    details: Optional[dict[str, Any]] = None

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"code": self.code, "message": self.message}
        if self.severity:
            payload["severity"] = self.severity
        if self.path is not None:
            payload["path"] = self.path
        if self.details is not None:
            payload["details"] = self.details
        return payload


def utc_now() -> str:
    """Return an ISO UTC timestamp in RFC3339 style with `Z` suffix."""
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def canonical_json(payload: Any) -> str:
    """
    Return a deterministic JSON string used for artifact hashing and offline verification.
    """
    return json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open("r", encoding="utf-8") as handle:
        data = json.load(handle)
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return data


def assert_str(value: object, path: str, *, required: bool = True) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        return None if required else ""
    trimmed = value.strip()
    if trimmed:
        return trimmed
    return "" if not required else None


def assert_list(
    value: object,
    path: str,
    *,
    required: bool = True,
) -> list[Any]:
    if required and not isinstance(value, list):
        return []
    if not required and value is None:
        return []
    if not isinstance(value, list):
        return []
    return value


def as_float(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return float(value)
    if isinstance(value, float):
        return value
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def coerce_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    return None


def is_mapping(value: Any) -> bool:
    return isinstance(value, Mapping)


def get_required_mapping(mapping: Mapping[str, Any], key: str, default: Mapping[str, Any] | None = None) -> Mapping[str, Any]:
    value = mapping.get(key)
    if is_mapping(value):
        return value
    if default is not None:
        return default
    raise TypeError(f"{key} must be an object.")
