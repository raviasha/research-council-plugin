"""Core library for the Research Council plugin."""

from .models import (
  Disposition,
  ClaimType,
  ValidationIssue,
  canonical_json,
  utc_now,
  load_json,
)

from .validate import validate_run
from .scoring import score_source, corroboration_summary
from .report import build_audit, write_package
from .report_guard import validate_publishable_claims

__all__ = [
  "Disposition",
  "ClaimType",
  "ValidationIssue",
  "canonical_json",
  "utc_now",
  "load_json",
  "validate_run",
  "score_source",
  "corroboration_summary",
  "build_audit",
  "write_package",
  "validate_publishable_claims",
]
