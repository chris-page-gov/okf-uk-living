# GitHub Pages publication unit

This directory contains the authored landing page and publication descriptor
for the population-complete preview. `pages-file-manifest.json` is generated
from the exact files served by GitHub Pages and must not be edited by hand.

The original base-only Pages workflow is retained as a historical record but
has no event trigger and cannot be manually dispatched. The additive Explore
OKF workflow is the only manual Pages deployment route. It verifies every
source file against the manifests and copies those bytes into the deployment
artefact; it does not rebuild the corpus or acquire source content.

The current publication manifest freezes 1,814 files whose corpus and rich
relationship-runtime bytes come from reviewed main commit
`c38f927944dedc56b6454dba4d4463d419f85ee8`. Permitted transport-only
differences are the descriptor's owner-authorised publication envelope and the
named browser documentation handoffs already allowed by the validator. These
must be explicitly re-pinned in this manifest; corpus, semantic, assurance and
relationship-runtime drift remains prohibited. Local validation uses `uv run --locked python
scripts/prepare_pages_publication.py --frozen` to verify the pinned manifest
identity, every source hash and the absence of data-plane drift from that
commit.

The manual workflow requires the exact protected-main merge commit as an
input, checks it against both the workflow event and the checked-out revision,
then transports only the frozen bytes. A pull request or merge does not deploy
the site.

The owner authorised the Explore OKF public-review overlay on 13 August 2026.
Its v2 manifest preserves every frozen target except `index.html`, which may be
replaced only after its old SHA-256 matches the frozen base manifest. The
standalone interface, machine sidecar and curated learning library are
hash-pinned additions. The manual workflow also requires the explicit
`EXPLORATORY-NOT-RELEASE-GRADE` acknowledgement and reconstructs the overlay in
check mode before transporting it. This authorisation does not make the preview
release grade or make a URL verified.

The preview is not release-grade. Its descriptor and landing page retain the
291 specialist-review warnings and direct readers to current official sources.

The 2026-08-08 enablement attempt failed before deployment because the current
GitHub plan did not support Pages for the private repository. On 2026-08-09 the
owner explicitly made the existing repository public. Manual run `31297841419`
then deployed the pinned publication successfully, and exact-byte plus
real-browser verification passed. See the
[deployment evidence](../evaluation/publication/pages-deployment-verification-2026-08-09.md).
That evidence applies to the superseded 1,549-file preview. The 1,814-file
rich-runtime correction requires its own exact-merge deployment and
cache-bypassed browser verification before its URLs may be labelled verified.
