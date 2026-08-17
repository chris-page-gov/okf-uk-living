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

Repository-authored review documents use the additive
`okf-site-document-publication.v1` contract. A document is nominated in its
frontmatter, rendered as safe static HTML and indexed automatically. The
generated `learn/documentation-manifest.json` binds each nominated Markdown
source to its output hash. `BASE_REF=origin/main make
validate-documentation-overlay` is permitted only when its changed-path gate
proves that corpus, semantic, schema and workflow inputs are unaffected. The
manual Pages workflow still transports the complete frozen base plus overlay;
there is no incremental or automatic deployment.

The base transporter resolves each manifest entry from the current checkout
only when its byte count and SHA-256 still match. Otherwise it reads the exact
manifest-bound blob from verified publication commit `736d7dc…`. A changed
repository document therefore cannot mutate a frozen browser handoff or add a
new base file; the new rendered page can enter only through the additive
overlay manifest.

The 2026-08-08 enablement attempt failed before deployment because the current
GitHub plan did not support Pages for the private repository. On 2026-08-09 the
owner explicitly made the existing repository public. Manual run `31297841419`
then deployed the pinned publication successfully, and exact-byte plus
real-browser verification passed. See the
[deployment evidence](../evaluation/publication/pages-deployment-verification-2026-08-09.md).
That evidence applies to the superseded 1,549-file preview. The 1,814-file
rich-runtime correction requires its own exact-merge deployment and
cache-bypassed browser verification before its URLs may be labelled verified.
