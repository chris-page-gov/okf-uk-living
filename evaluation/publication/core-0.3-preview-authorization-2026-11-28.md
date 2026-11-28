# Core 0.3 public-review preview authorisation — 28 November 2026

Status: authorised for a focused manual GitHub Pages deployment

Owner: `owner:chris-page-gov`

## Decision

The owner explicitly requested that GIS and UK Living be taken through their
remaining publication gates, including the focused pull-request and manual
publication route. This record applies the UK Living portion of that request
to a public Core 0.3 review preview for the isolated migration candidate. It
covers only the separate `/core-0.3-preview/` route and its hash-bound
candidate Reader assets.

The route may use the canonical Explorer Bundle Wiki v2 profile URI because
its profile files are now published at their canonical location and have been
verified byte-for-byte against pinned Explorer commit
`171efeeb8525691ab6d89f4ddfac2146374e862c`. The profile itself still labels
its implementation as experimental. The producer's Core 0.3 migration status
therefore remains `migration`.

## Publication boundary

- Preserve every target and byte in the existing 1,814-file Core 0.2 Pages
  publication. The candidate route is additive and uses the frozen base's
  large-data assets only where the closure manifest pins their exact hashes.
- Publish the candidate Core 0.3 descriptor, generated YAML-LD and JSON-LD,
  generated browser documents, and a closure manifest under the distinct
  `/core-0.3-preview/` path.
- Keep the Core 0.2 descriptor, product, review warnings and compatibility
  evidence visible and unchanged.
- Do not enable automatic deployment, remote CI, or source acquisition. A
  pull request or merge alone does not update Pages.
- Deploy only the exact protected-main commit through the manual workflow,
  then record exact served identities and real-browser evidence before calling
  any preview URL verified.

This decision does not claim full Bundle Wiki v2 profile acceptance, full
Explorer release support, specialist review, current source observation,
formal release grade, or legal, medical or individual eligibility advice.
Existing scope, rights, privacy and no-source-snapshot boundaries remain in
force.
