---
name: intent
description: Generate a versioned brief from a user request, decomposition strategy, and constraints.
---

# Research Council Intent

Turn user intent into a `brief` artifact. Keep sources empty for now; the researcher role will populate them.

## Input schema

```
{
  "run_id": "string",
  "user_problem": "string",
  "constraints": ["string"],
  "previous_brief": {}
}
```

## Output schema

```
{
  "run_id": "string",
  "brief": {
    "brief_id": "string",
    "version": 1,
    "user_problem": "string",
    "intended_use": "string",
    "objective": "string",
    "research_questions": [
      {
        "question_id": "q1",
        "text": "string"
      }
    ],
    "definitions": {},
    "scope": "string",
    "constraints": ["string"],
    "output": "string",
    "success_criteria": ["string"],
    "assumptions": ["string"],
    "unresolved_questions": ["string"]
  },
  "next_role": "researcher",
  "timestamp": "2026-09-05T00:00:00Z"
}
```

## Rules

- Do not fabricate citations or external sources.
- Always include `run_id`, `brief_id`, and `version` in the output.
- Keep `research_questions` to 3–7 questions so the workflow is tractable.
- Always set unresolved questions to an empty list by default unless you are explicitly blocking for missing evidence.
