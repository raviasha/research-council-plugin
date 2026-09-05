"""Guardrail checks for reportability and leak safety."""

from __future__ import annotations

from typing import Any, Mapping

from .models import ValidationIssue


def validate_publishable_claims(
    run: Mapping[str, Any],
    report_claim_ids: list[str] | None = None,
) -> list[ValidationIssue]:
    issues: list[ValidationIssue] = []
    claims = run.get("claims", [])
    reviews = run.get("reviews", [])

    if not isinstance(claims, list):
        issues.append(
            ValidationIssue(
                code="FR01_BAD_CLAIMS",
                message="claims must be an array to build a report.",
                path="claims",
            )
        )
        return issues

    claim_by_id: dict[str, Mapping[str, Any]] = {}
    for claim in claims:
        if isinstance(claim, Mapping) and isinstance(claim.get("claim_id"), str):
            claim_by_id[claim["claim_id"]] = claim

    review_by_claim: dict[str, Mapping[str, Any]] = {}
    for review in reviews:
        if isinstance(review, Mapping):
            claim_id = review.get("claim_id")
            if isinstance(claim_id, str):
                review_by_claim[claim_id] = review

    if report_claim_ids is None:
        report_claim_ids = [
            claim_id
            for claim_id, review in review_by_claim.items()
            if isinstance(review.get("disposition"), str)
            and review["disposition"] in {"Approved", "Approved-with-caveat"}
            and claim_id in claim_by_id
        ]

    for claim_id in report_claim_ids:
        claim = claim_by_id.get(claim_id)
        if claim is None:
            issues.append(
                ValidationIssue(
                    code="REPORT_UNRESOLVED_REFERENCE",
                    message=f"Report references unknown claim '{claim_id}'.",
                    path="report_claim_ids",
                    details={"claim_id": claim_id},
                )
            )
            continue

        review = review_by_claim.get(claim_id)
        if review is None:
            issues.append(
                ValidationIssue(
                    code="FR15_UNREVIEWED_REPORT_CLAIM",
                    message=f"Report includes claim '{claim_id}' without review.",
                    path=f"review:{claim_id}",
                )
            )
            continue

        if review.get("disposition") not in {"Approved", "Approved-with-caveat"}:
            issues.append(
                ValidationIssue(
                    code="FR15_REPORT_CLAIM_DISPOSITION",
                    message=f"Report includes non-approved claim '{claim_id}' with disposition '{review.get('disposition')}'.",
                    path=f"review:{claim_id}",
                    details={"disposition": review.get("disposition")},
                )
            )

    return issues
