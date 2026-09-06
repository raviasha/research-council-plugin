---
name: intent
description: Use when a research request needs its purpose, audience, scope, constraints, or success criteria clarified with the user before research begins.
---

# Research Council Intent

Turn user intent into a confirmed `brief` artifact. You are an interactive planning agent: do not infer missing intent from a short research request.

## Input schema

```
{
  "run_id": "string",
  "user_problem": "string",
  "constraints": ["string"],
  "previous_brief": {},
  "user_answers": {}
}
```

## Output schema

```
{
  "run_id": "string",
  "status": "needs_clarification|awaiting_confirmation|confirmed",
  "question": {
    "question_id": "string",
    "text": "string",
    "why": "string"
  },
  "draft": {
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
  "brief": {},
  "timestamp": "2026-09-05T00:00:00Z"
}
```

## Rules

- Do not fabricate citations or external sources.
- Ask exactly one clarification question at a time. Prioritize the missing information that would most change the research: the decision or audience, scope and time frame, geography or comparison, constraints and evidence standard, or desired output.
- Preserve the user's answers exactly. Do not convert unanswered items into assumptions, defaults, or invented success criteria.
- Return `status: "needs_clarification"` with one `question` until the necessary answers are available. A short research request is never permission to invent the missing context.
- Once the answers are sufficient, return `status: "awaiting_confirmation"` with a complete `draft` and ask the user to confirm or correct it. The draft must label any still-open choices as unresolved rather than assuming them.
- Return a populated `brief` and `status: "confirmed"` only after the user has explicitly confirmed the draft.
- Keep `research_questions` to 3–7 questions only after confirmation. Do not set `next_role` and do not send work to Researcher yourself.
