# Research Council Plugin

Research Council is a Codex plugin that turns a research prompt into:

- A versioned research brief
- A graph of sources, evidence, claims, devil challenges, and reviews
- Validator-issued quality gates (`FR`-coded)
- A DOCX report + JSON evidence package containing only approved claims

## Layout

- `.codex-plugin/plugin.json` — plugin manifest and UI metadata
- `scripts/research_graph/` — runtime library for validation, scoring, and reporting
- `skills/` — role skill contracts (orchestrator, intent, researcher, devil, reviewer, documentation)
- `tests/` — validation and contract tests

## Install

From a local checkout:

```bash
python3 /Users/<you>/path/to/.codex/skills/.system/plugin-creator/scripts/validate_plugin.py plugins/research-council
```

## Run validation

```bash
python3 -m unittest plugins/research-council/tests/unit -v
python3 plugins/research-council/scripts/cli/run_validation.py --run <path-to-run.json>
```

## Distribution

To share on GitHub:

1. Commit `plugins/research-council` and `.agents/plugins/marketplace.json`.
2. Push to your repository.
3. Configure a repository marketplace entry from the repo marketplace JSON so collaborators can add the plugin.

Collaborators can clone or pull the repository and follow their Codex marketplace installation flow.
