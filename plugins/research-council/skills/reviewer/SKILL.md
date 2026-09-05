---
name: reviewer
description: Perform adversarial review and assign final claim dispositions.
---

# Research Council Reviewer

Review each claim against evidence and challenges and return explicit dispositions with rationale.

## Input schema

```
{
  "run_id": "string",
  "brief": {},
  "claims": [],
  "evidence": [],
  "challenges": []
}
```

## Output schema

```
{
  "run_id": "string",
  "brief_version": "string",
  "reviews": [
    {
      "claim_id": "claim-1",
      "entailment_check": "unsupported|partially-supported|supported|well-supported",
      "source_quality": "low|medium|high",
      "corroboration": "weak|mixed|strong",
      "contradiction_status": "none|open|resolved",
      "disposition": "Approved|Approved-with-caveat|Contested|Insufficient-evidence|Rejected",
      "confidence_rationale": "string",
      "reviewer_notes": "string"
    }
  ],
  "next_role": "documentation",
  "timestamp": "2026-09-05T00:00:00Z"
}
```

## Rules

- Every input claim must receive one review entry.
- Claims with major unresolved risk should be `Contested` or `Insufficient-evidence`.
- Claims with no contradictions and strong corroboration may be `Approved` or `Approved-with-caveat`.
- Do not downgrade a reviewed claim outside allowed disposition enum.
