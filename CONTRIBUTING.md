# Contributing

Begin with [AGENTS.md](AGENTS.md), [the research overview](research/overview.md)
and [the authoring guide](docs/authoring.md).

Use one concept per Markdown file where the concept needs a stable route or
graph identity. Keep section indexes concise and progressive. Every material
claim must identify its authority, jurisdiction and source evidence.

Before requesting review, regenerate and validate the bundle using the commands
in `AGENTS.md`, or run `make validate`.

Repository-authored contributions are made under the repository's
[MIT License](LICENSE). Do not paste source-page or standards content into the
repository. Use browser-compatible links and original summaries, and update
the [rights register](source/rights-decisions.v1.yaml) whenever a new source
host or reuse basis is introduced.

Update implementation and documentation in lockstep using the matrix in
[PLANNING.md](PLANNING.md). Every pull request updates `TRACKING.md` and
`CHANGELOG.md`; changes to scope, gates, authoring or commands update their
governing documents in the same pull request.

Evaluation is local-only unless the owner explicitly requests publication.
Do not enable remote CI, update GitHub Pages or add acquired source snapshots
until the corresponding governance decision is approved. Every pull-request
handoff must state:

> Publication status: local validation only. GitHub Pages was not updated.
> Publication requires an explicit owner request.
