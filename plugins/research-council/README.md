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

## Install from GitHub

In a Codex terminal, run:

```bash
codex plugin marketplace add https://github.com/raviasha/research-council-plugin.git --ref main
codex plugin add research-council@research-council
```

This installs the plugin directly from GitHub; no repository clone is needed. Start a new Codex task after installation.

## Run validation

```bash
python3 -m unittest plugins/research-council/tests/unit -v
python3 plugins/research-council/scripts/cli/run_validation.py --run <path-to-run.json>
```

## Distribution

To share on GitHub:

1. Commit `plugins/research-council` and `.agents/plugins/marketplace.json`.
2. Push to your repository.
3. Collaborators add the GitHub repository as the `research-council` marketplace, then install `research-council` from it with the commands above.
