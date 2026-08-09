# GitHub Pages publication unit

This directory contains the authored landing page and publication descriptor
for the population-complete preview. `pages-file-manifest.json` is generated
from the exact files served by GitHub Pages and must not be edited by hand.

The Pages workflow is manual-only. It verifies every source file against the
manifest and copies those bytes into the deployment artifact; it does not
rebuild the corpus or acquire source content.

The workflow checks out publication merge
`980c7a9ec19ddd4161cefa348de689d179d1992b` before transport. This keeps later
documentation and evaluation commits from changing the 1,549 authorized files.
Local validation uses `uv run --locked python
scripts/prepare_pages_publication.py --frozen` to verify the pinned manifest
identity.

The preview is not release-grade. Its descriptor and landing page retain the
291 specialist-review warnings and direct readers to current official sources.

The 2026-08-08 enablement attempt failed before deployment because the current
GitHub plan did not support Pages for the private repository. On 2026-08-09 the
owner explicitly made the existing repository public. Manual run `31297841419`
then deployed the pinned publication successfully, and exact-byte plus
real-browser verification passed. See the
[deployment evidence](../evaluation/publication/pages-deployment-verification-2026-08-09.md).
