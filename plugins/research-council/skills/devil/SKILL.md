---
name: devil
description: Inject adversarial counter-arguments and alternate hypotheses for critical claims.
---

# Research Council Devil

Challenge high-importance claims and force adversarial reasoning. Only include claims already present in the researcher output.

## Input schema

```
{
  "run_id": "string",
  "brief": {},
  "claims": [
    {
      "claim_id": "claim-1",
      "exact_text": "string",
      "importance": 0.8
    }
  ],
  "evidence": []
}
```

## Output schema

```
{
  "run_id": "string",
  "brief_version": "string",
  "challenges": [
    {
      "challenge_id": "challenge-1",
      "claim_id": "claim-1",
      "challenge_type": "Counterexample|Contradiction|Coverage|Methodological",
      "alternative_hypothesis": "string",
      "evidence_ids": ["e1", "e2"],
      "severity": "low|medium|high"
    }
  ],
  "notes": "string",
  "next_role": "reviewer",
  "timestamp": "2026-09-05T00:00:00Z"
}
```

## Rules

- Every high-importance claim (>= 0.7) should include at least one challenge unless explicitly unresolved.
- Never invent evidence ids.
- Keep `challenge_type` and `severity` limited to enumerated values.
