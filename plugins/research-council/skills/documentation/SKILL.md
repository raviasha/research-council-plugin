---
name: documentation
description: Assemble DOCX and JSON artifacts for reviewed, publishable claims only.
---

# Research Council Documentation

Create final report artifacts from approved claims and write machine-readable outputs.

## Input schema

```
{
  "run_id": "string",
  "brief": {},
  "claims": [],
  "evidence": [],
  "reviews": [],
  "artifacts": {
    "output_directory": "~/.codex/plugin-runs/<run_id>/"
  },
  "report_claim_ids": ["claim-1"]
}
```

## Output schema

```
{
  "run_id": "string",
  "brief_version": "string",
  "status": "ready",
  "artifacts": {
    "docx": "~/.codex/plugin-runs/<run_id>/research-council-report.docx",
    "evidence_json": "~/.codex/plugin-runs/<run_id>/research-evidence-package.json",
    "audit_json": "~/.codex/plugin-runs/<run_id>/research-audit.json"
  },
  "audit": {}
}
```

## Workflow

- Validate reportability before writing output:
  - only approved or approved-with-caveat claims are eligible.
  - do not include unknown claim IDs in `report_claim_ids`.
- Write an audit artifact that includes claim disposition counts and run metadata.
- Return only JSON, and include both `run_id` and `brief_version`.
