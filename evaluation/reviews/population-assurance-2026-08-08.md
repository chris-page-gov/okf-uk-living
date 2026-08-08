# Population assurance review — 2026-08-08

## Result

`ASSURE-001` passes locally. The candidate identified as
`life-course-population-complete-2026-08-08` freezes the full static discovery
corpus at data-plane basis commit
`b65ed03545f78b261b5d6c9e49061424dc69b7dc` (PR #21).

Population completion is true. Release grade and publication readiness are
false. No source response body or snapshot was acquired or retained.

## Reconciliation

| Measure | Result |
|---|---:|
| Service families | 293 |
| Life-course domains | 24 |
| Enclosing processes | 48 |
| Competency questions | 104 |
| Searchable concepts | 9,757 |
| Typed source resources | 879 |
| Governed relationships | 15,810 |
| Blocking omissions | 0 |
| Visible browser journeys | 6 |

The deterministic reports under `generated/assurance/` reconcile denominator
membership, dossier completeness, process reachability, source resolution,
link receipts, rights decisions, specialist-review status, predicate
governance and material-edge provenance. The omission report contains no
blocking item. The candidate manifest records the exact byte size and SHA-256
identity of every frozen data-plane artifact.

## Link and rights boundary

- 359 current pack source-link receipts are active and body-free.
- The 53 reviewed vertical-slice references and seven authority-infrastructure
  receipts remain resolved.
- All 879 generated resource assertions are typed links to authoritative source
  material; they contain repository-authored summaries, facts and links only.
- The rights ledger covers all 29 registered source hosts and 498 linked
  references.
- No source response body, acquired page or redistributed snapshot is present.
- Live link auditing remains a reviewed, metadata-only acquisition check and is
  not part of deterministic offline validation.

## Browser acceptance

OKF Explorer 0.5.7 loaded the exact local descriptor at
`http://127.0.0.1:8011/okf-explorer.json`. Each case passed search → details →
Narrative → Graph → Resources → Open official source:

| Boundary | Query | Expected family | Result |
|---|---|---|---|
| National | `get tax back from HMRC` | Claim a tax refund | Passed |
| Devolved | `death registration` | Register a death | Passed |
| Local | `missed bin collection` | Report a missed rubbish collection | Passed |
| Health | `NHS 111` | Use urgent and emergency health services | Passed |
| Legal | `legal aid` | Get legal aid | Passed |
| Private dependency | `private parking ticket` | Challenge a private parking charge | Passed |

The official-source action was checked as a typed external handoff. Explorer
did not fetch or retain the source response while this evidence was recorded.

## Gap dispositions

All twelve historical reference gaps have an explicit population-gate
disposition in the candidate and source inventory. The approved local
authority/archetype/material-exception model, dated GSS/ODS/source-native
registry, Welsh discovery handoffs, manual health links, regulator-first
dependency maps, governed redress, explicit bilingual pairing and manual
freshness receipts satisfy population discovery without claiming uniform
leaf-service rules.

`GAP-LEGAL-PROCEDURE-REVIEW` remains deliberately non-blocking only for the
population gate. Named legal, clinical and high-impact-deadline reviewer
acceptance is still required for release grade.

## Remaining gates

The review-status report records 291 dossiers as
`specialist_review_required`, two as review not required and zero with named
specialist acceptance. Those warnings remain visible in the completed
discovery corpus. Release grade requires named reviewer acceptance and current
source re-observation for applicable claims. Publication requires a separate
owner request naming a frozen candidate, identical-byte promotion and a real
browser check of the exact deployed URLs.

## Local checks

The following locked commands pass:

```sh
uv run --locked python scripts/build_population_assurance.py
uv run --locked python scripts/build_population_assurance.py --check
uv run --locked python scripts/check_population_assurance.py
uv run --locked python -m unittest tests.test_population_assurance
make validate
```

GitHub Pages was not updated; publication remains unchanged until explicitly requested.
