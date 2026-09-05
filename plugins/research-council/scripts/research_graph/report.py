"""Build machine-readable evidence packages and minimal DOCX output."""

from __future__ import annotations

import json
import re
import zipfile
from pathlib import Path
from typing import Any, Mapping

from .models import canonical_json, utc_now
from .report_guard import validate_publishable_claims


def build_audit(run: Mapping[str, Any]) -> dict[str, Any]:
    claims = run.get("claims", [])
    reviews = run.get("reviews", [])
    review_by_claim: dict[str, Mapping[str, Any]] = {}
    for review in reviews:
        if isinstance(review, Mapping):
            claim_id = review.get("claim_id")
            if isinstance(claim_id, str):
                review_by_claim[claim_id] = review

    approved = 0
    caveat = 0
    contested = 0
    insufficient = 0
    rejected = 0
    unresolved = 0

    for claim in claims:
        if not isinstance(claim, Mapping):
            continue
        review = review_by_claim.get(claim.get("claim_id", ""))
        if not review:
            unresolved += 1
            continue
        disposition = review.get("disposition")
        if disposition == "Approved":
            approved += 1
        elif disposition == "Approved-with-caveat":
            caveat += 1
        elif disposition == "Contested":
            contested += 1
        elif disposition == "Insufficient-evidence":
            insufficient += 1
        elif disposition == "Rejected":
            rejected += 1
        else:
            unresolved += 1

    return {
        "run_id": run.get("run_id"),
        "brief_version": run.get("brief_version"),
        "generated_at": utc_now(),
        "counts": {
            "claims_total": len(claims),
            "approved": approved,
            "approved_with_caveat": caveat,
            "contested": contested,
            "insufficient": insufficient,
            "rejected": rejected,
            "unresolved": unresolved,
        },
    }


def _escape_text(text: Any) -> str:
    s = str(text if text is not None else "")
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return re.sub(r"\s+", " ", s).strip()


def _document_xml(audit: Mapping[str, Any], report_claims: list[Mapping[str, Any]]) -> str:
    rows = [
        (
            "<w:p><w:r><w:t>Research Council Report</w:t></w:r></w:p>"
            "<w:p><w:r><w:t>Generated: {timestamp}</w:t></w:r></w:p>"
        ).format(timestamp=_escape_text(audit.get("generated_at")))
    ]

    summary = (
        "Approved: {approved}, Caveat: {caveat}, Contested: {contested}, "
        "Insufficient: {insufficient}, Rejected: {rejected}, Unreviewed: {unresolved}"
    ).format(
        approved=_escape_text(audit.get("counts", {}).get("approved")),
        caveat=_escape_text(audit.get("counts", {}).get("approved_with_caveat")),
        contested=_escape_text(audit.get("counts", {}).get("contested")),
        insufficient=_escape_text(audit.get("counts", {}).get("insufficient")),
        rejected=_escape_text(audit.get("counts", {}).get("rejected")),
        unresolved=_escape_text(audit.get("counts", {}).get("unresolved")),
    )
    rows.append(f"<w:p><w:r><w:t>{summary}</w:t></w:r></w:p>")

    for claim in report_claims:
        claim_text = _escape_text(claim.get("exact_text"))
        source = _escape_text(claim.get("claim_id"))
        rows.append(f"<w:p><w:r><w:t>Claim {source}: {claim_text}</w:t></w:r></w:p>")

    body = "".join(rows)
    return (
        "<?xml version='1.0' encoding='UTF-8' standalone='yes'?>"
        "<w:document xmlns:wpc='http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas' "
        "xmlns:mc='http://schemas.openxmlformats.org/markup-compatibility/2006' "
        "xmlns:o='urn:schemas-microsoft-com:office:office' "
        "xmlns:r='http://schemas.openxmlformats.org/officeDocument/2006/relationships' "
        "xmlns:m='http://schemas.openxmlformats.org/officeDocument/2006/math' "
        "xmlns:v='urn:schemas-microsoft-com:vml' "
        "xmlns:wp='http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing' "
        "xmlns:w='http://schemas.openxmlformats.org/wordprocessingml/2006/main' "
        "xmlns:w10='urn:schemas-microsoft-com:office:word' "
        "xmlns:wne='http://schemas.microsoft.com/office/2006/word'>"
        "<w:body>"
        f"{body}"
        "<w:sectPr><w:pgSz w:w='12240' w:h='15840'/><w:pgMar w:top='1440' w:right='1440' w:bottom='1440' w:left='1440' w:header='708' w:footer='708' w:gutter='0'/><w:cols w:space='708'/><w:docGrid w:linePitch='360'/></w:sectPr>"
        "</w:body></w:document>"
    )


def _write_docx(path: Path, document_xml: str) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", _content_types_xml())
        archive.writestr(
            "_rels/.rels",
            _rels_xml(),
        )
        archive.writestr("word/document.xml", document_xml)
        archive.writestr("word/_rels/document.xml.rels", _document_rels_xml())


def _content_types_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/word/document.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
        "</Types>"
    )


def _rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
        "</Relationships>"
    )


def _document_rels_xml() -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'
    )


def write_package(
    run: Mapping[str, Any],
    output_dir: str | Path,
    *,
    report_claim_ids: list[str] | None = None,
) -> dict[str, str]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    issues = validate_publishable_claims(run, report_claim_ids=report_claim_ids)
    if issues:
        return {"error": "; ".join(issue.message for issue in issues)}

    audit = build_audit(run)
    claim_map: dict[str, Mapping[str, Any]] = {
        str(claim.get("claim_id")): claim
        for claim in run.get("claims", [])
        if isinstance(claim, Mapping) and isinstance(claim.get("claim_id"), str)
    }

    selected_claim_ids = (
        report_claim_ids
        if report_claim_ids is not None
        else [
            claim_id
            for claim_id in claim_map.keys()
            if claim_id
            in {
                str(review.get("claim_id"))
                for review in run.get("reviews", [])
                if isinstance(review, Mapping) and review.get("disposition") in {"Approved", "Approved-with-caveat"}
            }
        ]
    )
    selected_claims = [claim_map[claim_id] for claim_id in selected_claim_ids if claim_id in claim_map]

    docx_path = output_dir / "research-council-report.docx"
    json_path = output_dir / "research-evidence-package.json"
    audit_path = output_dir / "research-audit.json"

    _write_docx(docx_path, _document_xml(audit, selected_claims))
    json_payload = {
        "run_id": run.get("run_id"),
        "brief_version": run.get("brief_version"),
        "claims": selected_claims,
        "evidence": run.get("evidence", []),
        "reviews": [
            item
            for item in run.get("reviews", [])
            if isinstance(item, Mapping) and item.get("claim_id") in selected_claim_ids
        ],
        "generated_at": audit["generated_at"],
    }
    json_path.write_text(canonical_json(json_payload) + "\n", encoding="utf-8")
    audit_path.write_text(canonical_json(audit) + "\n", encoding="utf-8")

    return {
        "docx": str(docx_path),
        "evidence_json": str(json_path),
        "audit_json": str(audit_path),
    }
