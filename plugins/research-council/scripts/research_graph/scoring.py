"""Source weighting and corroboration helpers."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Mapping

AUTHORITY_WEIGHTS = {
    "peer-reviewed": 1.0,
    "industry-report": 0.75,
    "government": 0.9,
    "news": 0.45,
    "whitepaper": 0.8,
    "blog": 0.35,
    "unknown": 0.5,
}

DIRECTNESS_WEIGHTS = {
    "peer-reviewed": 1.0,
    "government": 0.95,
    "industry-report": 0.7,
    "whitepaper": 0.7,
    "news": 0.55,
    "blog": 0.45,
    "unknown": 0.5,
}

METHOD_WEIGHTS = {
    "randomized": 1.0,
    "controlled": 0.85,
    "case-study": 0.7,
    "modeling": 0.75,
    "descriptive": 0.55,
    "unknown": 0.5,
}

INDEPENDENCE_WEIGHTS = {
    "independent": 1.0,
    "mixed": 0.7,
    "conflicted": 0.2,
    "unknown": 0.5,
}

WEIGHTS = {
    "authority": 25,
    "directness": 20,
    "methodology": 20,
    "independence": 15,
    "relevance": 10,
    "recency": 10,
}


def _parse_date(value: Any) -> datetime | None:
    if not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    try:
        return datetime.fromisoformat(normalized.replace("Z", "+00:00"))
    except ValueError:
        return None


def _recency_score(value: Any) -> float:
    parsed = _parse_date(value)
    if parsed is None:
        return 0.5
    now = datetime.now(timezone.utc) if parsed.tzinfo else datetime.now()
    age_days = max(0, (now - parsed).days)
    if age_days <= 30:
        return 1.0
    if age_days <= 365:
        return 0.75
    if age_days <= 730:
        return 0.5
    return 0.25


def _relevance_score(source: Mapping[str, Any]) -> float:
    if not isinstance(source, Mapping):
        return 0.5
    if source.get("relevance") in {"high", "core", "primary"}:
        return 1.0
    if source.get("relevance") in {"medium"}:
        return 0.7
    if source.get("relevance") in {"low"}:
        return 0.4
    return 0.6


def score_source(source: Mapping[str, Any]) -> int:
    source_type = str(source.get("source_type", "unknown")).lower()
    methodology = str(source.get("methodology", "unknown")).lower()
    independence = str(source.get("independence_group", "unknown")).lower()
    authority = AUTHORITY_WEIGHTS.get(source_type, 0.5)
    directness = DIRECTNESS_WEIGHTS.get(source_type, 0.5)
    methodology_score = METHOD_WEIGHTS.get(methodology, 0.5)
    independence_score = INDEPENDENCE_WEIGHTS.get(independence, 0.5)
    relevance = _relevance_score(source)
    recency = _recency_score(source.get("publication_date"))

    weighted = (
        authority * WEIGHTS["authority"]
        + directness * WEIGHTS["directness"]
        + methodology_score * WEIGHTS["methodology"]
        + independence_score * WEIGHTS["independence"]
        + relevance * WEIGHTS["relevance"]
        + recency * WEIGHTS["recency"]
    )
    return max(0, min(100, int(round(weighted))))


def corroboration_summary(run: Mapping[str, Any]) -> dict[str, Any]:
    claims = run.get("claims", [])
    evidence_map = {str(item.get("evidence_id")): item for item in run.get("evidence", []) if isinstance(item, Mapping)}
    review_by_claim: dict[str, Mapping[str, Any]] = {}
    for review in run.get("reviews", []):
        if isinstance(review, Mapping):
            claim_id = review.get("claim_id")
            if isinstance(claim_id, str):
                review_by_claim[claim_id] = review

    high = []
    medium = []
    low = []
    for claim in claims:
        if not isinstance(claim, Mapping):
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str):
            continue
        support = [str(eid) for eid in claim.get("supporting_evidence_ids", []) if str(eid) in evidence_map]
        contradict = [str(eid) for eid in claim.get("contradicting_evidence_ids", []) if str(eid) in evidence_map]
        score = len(support) - len(contradict)
        item = {
            "claim_id": claim_id,
            "supporting_evidence": support,
            "contradicting_evidence": contradict,
            "support_count": len(support),
            "contradiction_count": len(contradict),
            "disposition": review_by_claim.get(claim_id, {}).get("disposition", "unreviewed"),
        }
        if score >= 2:
            high.append(item)
        elif score >= 1:
            medium.append(item)
        else:
            low.append(item)

    return {"high_confidence": high, "medium_confidence": medium, "low_confidence": low}
