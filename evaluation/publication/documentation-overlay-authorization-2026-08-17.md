# Static-document overlay authorisation

Decision date: 17 August 2026

Owner: `owner:chris-page-gov`

The owner authorised implementation of the governed documentation-only
publication path and publication of the draft product requirements through
that path. This is an additive review-site decision. It does not change the
frozen corpus, semantic authority, release grade, source-use boundary or
specialist-review status.

The authorised public targets are:

- `learn/library/product-requirements.html`;
- `learn/library/index.html`; and
- `learn/documentation-manifest.json`.

The existing learning page may change only to link to the generated document
index and product requirements. The Explore manifest may change only to bind
those exact rendered bytes and the documentation changes already carried by
the same pull request.

Pull-request creation and merge do not deploy GitHub Pages. After merge, the
manual workflow must name the exact protected-main commit, retain the
`EXPLORATORY-NOT-RELEASE-GRADE` acknowledgement and pass its manifest checks.
The product-requirements URL may be labelled verified only after a
cache-bypassed real-browser check confirms site identity, navigation, draft
status and the MIT notice boundary.

## Bounded verification correction

The first exact-head deployment passed the site-identity, navigation, draft
status and document-content checks. Microsoft Edge blocked the footer's
extensionless `/LICENSE` target before the MIT boundary could be verified, so
the document URL remained unverified.

On 17 August 2026 the owner approved the bounded correction. Generated review
documents now link to the existing browser-rendered
`generated/browser/NOTICE.html` page, which exposes the repository MIT grant
and the source-family attribution terms. This changes no corpus, semantic,
source, workflow or frozen-base byte. The corrected URL remains unverified
until an exact-head manual deployment and cache-bypassed browser journey pass.
