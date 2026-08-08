---
type: "Evaluation Review"
title: "Three-slice population migration review"
description: "Local deterministic and real-browser evidence for six migrated family dossiers, narratives, resources and governed relationships."
status: "passed-local"
assertion_status: "normalized"
observed_at: "2026-08-08"
---

# Three-slice population migration review

The six reviewed service families were evaluated locally against the merged
OKF Explorer narrative and typed-source contract at commit
`20654abcf495e659bf6bb822762d32e2b9fa13d0`. This is local acceptance evidence,
not publication or a statement that the remaining 287 dossiers are complete.

## Frozen inputs for this review

| Artifact | SHA-256 |
|---|---|
| `okf-explorer.json` | `14479838603d9a4412d8708eb7835e1570c53637fcb22474a6b304a2b67ebe71` |
| `large/data/records-0.json` | `9134545594e7fbabc669be48c9fd7b5bc8f49830dfc005776ee94da8fc631840` |
| `large/data/resources-0.json` | `cfbbeba1b58a5a6278680018c9fad57233bc730d227d8046ee7c15f9671fedbe` |
| `large/data/relationships-0.json` | `33fc1847eaf1844c0df7d4f201f8978558848904a95da58838b31e5344fcf685` |

## Deterministic acceptance

- 293 service families reconcile within 602 total typed concepts.
- Six dossiers pass the population gate and resolve exactly 53 unique existing
  source assertions.
- The projection contains 53 typed `link` resources, 1,025 governed
  relationships, record-locator and relationship-adjacency shards, JSON-LD,
  YAML-LD and a conformant SHACL-style report.
- Every resource records `response_body_retained: false`; snapshots remain
  zero.
- `make validate` passed all 85 tests using locked `uv` execution.

## Real-browser journeys

The no-cache local overlay at `127.0.0.1:8011` passed:

1. `missed bin` returned **Report a missed rubbish collection** first, showing
   the alias and explanatory-summary match.
2. The selected record hydrated through the sharded record locator without an
   error.
3. Narrative displayed the authored Markdown plus enclosing process, first
   step, later ordinary step, exception episode and four local variants.
4. Narrative source links resolved to browser-rendered handoffs, including
   `generated/browser/services/coventry-missed-bin-collection.html`.
5. Graph displayed 36 selected-record relationships, including governed
   domain, process, episode, actor, jurisdiction, user-need and source edges.
   Material edges displayed the repository-authored authority label,
   assertion status, scope and provenance.
6. Resources displayed all 13 waste references as **Open official source**;
   the GOV.UK and Coventry actions pointed to their exact HTTPS pages.
7. `speeding ticket` returned the legal exception family with nine resources
   and a narrative distinguishing the national court variants.
8. `probate` returned **Administer an estate** within the required first five
   results and exposed its three jurisdictional variants and private dependency
   boundary.
9. The browser console contained no warnings or errors.

No official-source action was followed during this local UI test, so the
browser did not download or retain any source response. Metadata-only live
link checking remains a separate reviewed acquisition activity.

## Publication status

GitHub Pages was not updated; publication remains unchanged until explicitly
requested.
