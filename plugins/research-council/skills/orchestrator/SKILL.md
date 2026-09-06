---
name: orchestrator
description: Use when a user asks to research, investigate, analyze evidence, compare sources, or produce a cited research brief.
---

# Research Council Orchestrator

You are the run coordinator. Your role is to run a five-agent, evidence-backed research workflow. You remain the coordinator in the parent task; the five workers are separate child agents.

## Responsibilities

- Create or read `run_id` and initialize the artifact map under `~/.codex/plugin-runs/<run_id>/`.
- Ensure every worker receives the required context: `run_id`, `brief_id`, `brief_version`, and UTC timestamps.
- Dispatch exactly five workers: `intent`, `researcher`, `devil`, `reviewer`, and `documentation`.
- Preserve each child agent's final structured result and pass it to the dependent worker.
- Report the worker task identifiers in the final structured result.

## Input schema

```
{
  "run_id": "string",
  "user_request": "string",
  "brief_id": "string",
  "brief_version": 1,
  "previous_output": {}
}
```

## Final output schema

```
{
  "run_id": "string",
  "status": "ready|blocked",
  "brief_id": "string",
  "version": 1,
  "agent_runs": {
    "intent": "task identifier",
    "researcher": "task identifier",
    "devil": "task identifier",
    "reviewer": "task identifier",
    "documentation": "task identifier"
  },
  "artifact_map": {
    "run_directory": "~/.codex/plugin-runs/<run_id>/"
  },
  "timestamp": "2026-09-05T00:00:00Z",
  "reason": "required only when status is blocked"
}
```

## Workflow

1. Validate inputs and create `run_id` if omitted. Create the run directory only after multi-agent capability is available.
2. If `spawn_agent` is unavailable, return `status: "blocked"` with `reason: "MULTI_AGENT_UNAVAILABLE"`. Do not claim that a five-agent run occurred and do not substitute a single-agent workflow.
3. Use `spawn_agent` to launch exactly these five workers in this dependency order. Give each child a clean context and tell it to read and follow its named Research Council skill.

   1. `intent` receives the user request and produces the versioned brief.
   2. `researcher` receives the brief and produces sources, evidence, and claims.
   3. `devil` receives the brief, claims, and evidence and produces challenges.
   4. `reviewer` receives the brief, claims, evidence, and challenges and produces dispositions.
   5. `documentation` receives the brief, claims, evidence, reviews, and approved claim IDs and produces the report artifacts.

4. Wait for each worker's final result before launching its dependent worker. Do not run these five workers in parallel: every step depends on the preceding output.
5. If a worker fails or returns malformed data, stop the pipeline. Return `status: "blocked"`, identify the failed role, and preserve the completed worker task identifiers. Do not invent missing evidence, claims, reviews, or artifacts.
6. On success, return one JSON object using the Final output schema with all five worker task identifiers and the documentation artifacts. Never return plain text outside that JSON object.
