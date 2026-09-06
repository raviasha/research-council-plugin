# Research Council for Codex

Research Council runs evidence-backed, adversarial research workflows in Codex. It first clarifies and confirms the research brief with the user, then produces an auditable evidence graph and approved-claim report.

## Install from GitHub

Open a terminal in Codex and run:

```bash
codex plugin marketplace add https://github.com/raviasha/research-council-plugin.git --ref main
codex plugin add research-council@research-council
```

This registers the GitHub repository as a Codex marketplace and installs the plugin; no repository clone is needed. Start a new Codex task after installation.

## Use it

Ask Codex to use Research Council, for example:

```text
Use Research Council to research whether [topic], citing reliable sources and challenging weak claims.
```

For plugin internals, validation, and development instructions, see [plugins/research-council/README.md](plugins/research-council/README.md).
