"""Run-level validation enforcing P0/P1 workflow invariants."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from .models import ValidationIssue, assert_list, assert_str, as_float, coerce_bool


_HIGH_IMPORTANCE_THRESHOLD = 0.7


def _issue(code: str, message: str, path: str | None = None, *, details: Mapping[str, Any] | None = None) -> ValidationIssue:
    return ValidationIssue(
        code=code,
        message=message,
        severity="error",
        path=path,
        details=dict(details) if details else None,
    )


def _index_by_id(items: Sequence[Mapping[str, Any]], id_key: str) -> dict[str, Mapping[str, Any]]:
    index: dict[str, Mapping[str, Any]] = {}
    for item in items:
        if not isinstance(item, Mapping):
            continue
        item_id = item.get(id_key)
        if not isinstance(item_id, str) or not item_id.strip():
            continue
        index[item_id] = item
    return index


def validate_run(run: Mapping[str, Any]) -> list[ValidationIssue]:
    """
    Validate a single workflow run artifact.
    """
    issues: list[ValidationIssue] = []

    if not isinstance(run, Mapping):
        return [_issue("FR01_INVALID_RUN_PAYLOAD", "Run payload must be an object.")]

    if not run.get("run_id"):
        issues.append(_issue("FR01_MISSING_RUN_ID", "run_id is required."))

    brief = run.get("brief")
    if not isinstance(brief, Mapping):
        issues.append(_issue("FR02_MISSING_BRIEF", "brief is required and must be an object."))
        return issues

    brief_questions = []
    for question in assert_list(brief.get("research_questions", []), "brief.research_questions"):
        if not isinstance(question, Mapping):
            issues.append(_issue("FR04_BAD_RESEARCH_QUESTION", "research_questions entries must be objects.", "brief.research_questions"))
            continue
        question_id = assert_str(question.get("question_id"), "brief.research_questions[].question_id")
        if question_id:
            brief_questions.append(question_id)
        else:
            issues.append(_issue("FR04_MISSING_QUESTION_ID", "Every research question needs a question_id.", "brief.research_questions"))

    unresolved_questions = assert_list(brief.get("unresolved_questions", []), "brief.unresolved_questions", required=False)
    unresolved_questions = {str(item).strip() for item in unresolved_questions if str(item).strip()}

    sources = assert_list(run.get("sources", []), "sources")
    evidence_items = assert_list(run.get("evidence", []), "evidence")
    claims = assert_list(run.get("claims", []), "claims")
    challenges = assert_list(run.get("challenges", []), "challenges")
    reviews = assert_list(run.get("reviews", []), "reviews")

    source_by_id = _index_by_id(sources, "source_id")
    evidence_by_id = _index_by_id(evidence_items, "evidence_id")
    claim_by_id = _index_by_id(claims, "claim_id")

    if not sources:
        issues.append(_issue("FR06_MISSING_SOURCE", "At least one source is required."))
    if not claims:
        issues.append(_issue("FR04_MISSING_CLAIMS", "At least one claim is required."))

    challenge_by_claim: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for challenge in challenges:
        if not isinstance(challenge, Mapping):
            issues.append(_issue("FR07_BAD_CHALLENGE", "Challenge items must be objects.", "challenges"))
            continue
        challenge_id = assert_str(challenge.get("challenge_id"), "challenges[].challenge_id")
        claim_id = assert_str(challenge.get("claim_id"), "challenges[].claim_id")
        if claim_id and claim_id in claim_by_id:
            challenge_by_claim[claim_id].append(challenge)
        elif claim_id:
            issues.append(_issue("FR07_UNKNOWN_CLAIM", f"Challenge '{challenge_id}' targets unknown claim '{claim_id}'.", "challenges"))

        evidence_ids = assert_list(challenge.get("evidence_ids"), "challenges[].evidence_ids", required=False)
        for evidence_id in evidence_ids:
            if str(evidence_id) not in evidence_by_id:
                issues.append(_issue("FR11_UNKNOWN_EVIDENCE", f"Challenge '{challenge_id}' references unknown evidence '{evidence_id}'.", "challenges"))

    review_by_claim: dict[str, Mapping[str, Any]] = {}
    for review in reviews:
        if not isinstance(review, Mapping):
            issues.append(_issue("FR12_BAD_REVIEW", "Review items must be objects.", "reviews"))
            continue
        claim_id = assert_str(review.get("claim_id"), "reviews[].claim_id")
        if not claim_id:
            continue
        if claim_id not in claim_by_id:
            issues.append(_issue("FR12_UNKNOWN_CLAIM", f"Review for unknown claim '{claim_id}'.", "reviews"))
            continue
        disposition = assert_str(review.get("disposition"), "reviews[].disposition")
        allowed = {"Approved", "Approved-with-caveat", "Contested", "Insufficient-evidence", "Rejected"}
        if disposition and disposition not in allowed:
            issues.append(_issue("FR12_INVALID_DISPOSITION", f"Unknown disposition '{disposition}'.", "reviews"))
        review_by_claim[claim_id] = review

    for evidence in evidence_items:
        if not isinstance(evidence, Mapping):
            issues.append(_issue("FR06_BAD_EVIDENCE", "Evidence items must be objects.", "evidence"))
            continue
        evidence_id = assert_str(evidence.get("evidence_id"), "evidence[].evidence_id")
        locator = assert_str(evidence.get("locator"), "evidence[].locator")
        source_id = assert_str(evidence.get("source_id"), "evidence[].source_id")
        if not locator:
            issues.append(_issue("FR06_MISSING_LOCATOR", f"Evidence '{evidence_id}' must include locator metadata.", "evidence"))
        if source_id and source_id not in source_by_id:
            issues.append(_issue("FR10_UNKNOWN_SOURCE", f"Evidence '{evidence_id}' references unknown source '{source_id}'.", "evidence"))

    answered_questions: set[str] = set()
    for claim in claims:
        if not isinstance(claim, Mapping):
            issues.append(_issue("FR04_BAD_CLAIM", "Claim items must be objects.", "claims"))
            continue
        claim_id = assert_str(claim.get("claim_id"), "claims[].claim_id")
        if not claim_id:
            continue

        question_id = assert_str(claim.get("question_id"), "claims[].question_id")
        if question_id:
            answered_questions.add(question_id)
            if question_id not in brief_questions:
                issues.append(_issue("FR14_UNKNOWN_QUESTION", f"Claim '{claim_id}' references unknown question '{question_id}'.", "claims"))

        importance = as_float(claim.get("importance"))
        if importance is None:
            issues.append(_issue("FR04_BAD_IMPORTANCE", f"Claim '{claim_id}' has invalid importance.", "claims"))
        elif importance < 0 or importance > 1:
            issues.append(_issue("FR04_INVALID_IMPORTANCE", f"Claim '{claim_id}' importance must be 0..1.", "claims"))
        elif importance >= _HIGH_IMPORTANCE_THRESHOLD:
            if not challenge_by_claim.get(claim_id):
                unresolved = coerce_bool(claim.get("unresolved")) or False
                if not unresolved:
                    issues.append(_issue("FR07_MISSING_CHALLENGE", f"High-importance claim '{claim_id}' must have a Devil challenge.", "claims"))

        support_ids = assert_list(claim.get("supporting_evidence_ids", []), "claims[].supporting_evidence_ids", required=False)
        if not support_ids:
            issues.append(_issue("FR10_MISSING_SUPPORT", f"Claim '{claim_id}' has no supporting evidence.", "claims"))
        for evidence_id in support_ids:
            if str(evidence_id) not in evidence_by_id:
                issues.append(_issue("FR10_UNKNOWN_EVIDENCE", f"Claim '{claim_id}' references unknown supporting evidence '{evidence_id}'.", "claims"))

        contradiction_ids = assert_list(claim.get("contradicting_evidence_ids", []), "claims[].contradicting_evidence_ids", required=False)
        for evidence_id in contradiction_ids:
            if str(evidence_id) not in evidence_by_id:
                issues.append(_issue("FR10_UNKNOWN_EVIDENCE", f"Claim '{claim_id}' references unknown contradicting evidence '{evidence_id}'.", "claims"))

        if not coerce_bool(claim.get("unresolved", False)):
            review = review_by_claim.get(claim_id)
            if not review:
                issues.append(_issue("FR15_MISSING_REVIEW", f"Unreviewed claim '{claim_id}' blocks publish.", "reviews"))

    for q in brief_questions:
        if q not in answered_questions and q not in unresolved_questions:
            issues.append(_issue("FR14_UNCOVERED_QUESTION", f"Question '{q}' is not answered by claims.", "claims"))

    for claim_id, c_reviews in challenge_by_claim.items():
        if not c_reviews:
            continue
        review = review_by_claim.get(claim_id)
        for challenge in c_reviews:
            if challenge.get("severity") == "high" and (not review or review.get("disposition") not in {"Contested", "Insufficient-evidence", "Rejected"}):
                issues.append(
                    _issue(
                        "FR11_UNADDRESSED_CHALLENGE",
                        f"High-severity challenge on '{claim_id}' is not addressed as contested/insufficient/rejected.",
                        "reviews",
                    )
                )

    return issues
