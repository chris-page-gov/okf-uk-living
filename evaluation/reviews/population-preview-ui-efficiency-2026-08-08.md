# Population-preview publication and UI-efficiency review — 2026-08-08

## Result

The frozen 293-family population preview is internally coherent and the exact
publication unit is reproducible. Keyword-led discovery is efficient: all six
representative terms returned the intended family within the first two results,
and one local-service journey reached an original narrative, a 36-relationship
graph, 13 official links and a live GOV.UK handoff.

Conversational question answering is not yet efficient. Three deliberately
natural questions returned no results because the static search requires every
meaningful query term to match. The zero-result state then reduced every facet
to zero values instead of offering the required life-course-domain fallback.
These are Explorer/search acceptance findings, not missing corpus records.

Public deployment did not occur. GitHub rejected workflow-based Pages
enablement for the private repository with HTTP 422: `Your current plan does
not support GitHub Pages for this repository.` Repository visibility was not
changed. No public bundle URL is verified or shareable.

## Reviewed identities

- Living repository merge: `980c7a9ec19ddd4161cefa348de689d179d1992b`
- Explorer `main`: `20654abcf495e659bf6bb822762d32e2b9fa13d0`
- Explorer deterministic build tree:
  `cc72e9aba2f0f87c3ae78df751d3c87626b8fdf7ff7481a81100f678fd93ebd7`
- Frozen candidate: `life-course-population-complete-2026-08-08`
- Candidate manifest SHA-256:
  `0b1df05a4eb440b9193d0906fbe2c071c6463bbe457f9a791472fee7f949b62e`
- Publication unit: 1,549 allow-listed files, 178,842,389 bytes, zero source
  bodies or snapshots

The publication landing and descriptor were served from the exact `_site`
staging copy. The UI journey used the same frozen candidate data plane through
the current merged Explorer build in a temporary checkout; the user's existing
Explorer worktree was not changed.

## Question efficiency

The following governed keyword or short-phrase queries passed visibly:

| Query | Intended family | Rank / results |
|---|---|---:|
| `get tax back from HMRC` | Claim a tax refund | 1 / 1 |
| `death registration` | Register a death | 1 / 51 |
| `missed bin collection` | Report a missed rubbish collection | 1 / 4 |
| `NHS 111` | Use urgent and emergency health services | 2 / 12 |
| `legal aid` | Get legal aid | 1 / 30 |
| `private parking ticket` | Challenge a private parking charge | 1 / 1 |

The following ordinary-language questions failed visibly with zero matches:

- `what happens after someone dies and how do I deal with estate debts`
- `how do I challenge a private parking charge`
- `what if my council misses my rubbish collection`

The UI explained that all meaningful terms are required and identified an
unmatched term, which is useful diagnostic feedback. It did not relax the
query, suggest a shorter governed phrase or restore domain browsing.

## Representative journey

`missed bin collection` gave a clear first result. From that result:

1. Reader supplied the original summary and identified 13 resources.
2. Narrative placed the family in `Manage household waste collections`, showed
   what comes before and after, exposed the exception episode, and listed the
   Coventry, Edinburgh, Cardiff and Belfast variants.
3. Graph centred the family and exposed 37 directly related nodes and 36
   relationships, including domain, process, user need, episodes,
   jurisdictions, provider roles, redress and source support.
4. Resources listed the 13 official link-only references with labels, formats
   and hosts.
5. `https://www.gov.uk/missed-bin-collection` opened successfully in the real
   browser as `Report a missed bin collection - GOV.UK`.

This is a five-action path after entering the query: select the result, choose
Narrative, choose Graph, choose Resources, and open an official source. The
route and current selection persist across views.

## UI findings

### `UI-001` — conversational queries are over-constrained

Severity: high for the stated question-answering objective.

Search treats every non-stopword as mandatory. Conversational scaffolding and
simple inflections such as `misses` therefore turn otherwise exact topic
questions into zero results. The six concise terms show that the underlying
index and corpus identities are present.

Required follow-up: Explorer should provide a bounded query relaxation or
governed suggestion that never fabricates a result, with browser acceptance for
the competency-question form users will actually type.

### `UI-002` — zero-result browsing fallback is absent

Severity: high against the approved acceptance contract.

With an unmatched query, all seven facets display zero values and the centre
only says `No static-search matches.` The approved requirement says an
unmatched query must offer life-course-domain browsing.

Required follow-up: preserve or explicitly restore the 24-domain browse entry
point and provide a one-action way to remove or relax the unmatched term.

### `UI-003` — jurisdiction facet identities are visually duplicated

Severity: medium.

The whole-corpus jurisdiction facet separately displays values such as
`england` and `England`, `scotland` and `Scotland`, and equivalent Wales and
Northern Ireland forms. These are distinguishable source/model identifiers but
not distinguishable user choices at the facet surface.

Required follow-up: group display-equivalent jurisdiction identifiers while
retaining their governed identities and provenance underneath.

### `UI-004` — graph evidence is complete but expensive to interpret

Severity: medium.

The representative graph exposes the expected journey and source edges, but
the relationships panel presents 36 rows dominated by generated identifiers.
Normalized edges show the repository-authored model and assertion status, yet
the final authority/evidence field is frequently `unknown`; Explorer-derived
metadata edges say `Authority not declared · unknown`.

Required follow-up: prioritize ordinary/exception journey edges, replace raw
identifiers with titles, and distinguish `not applicable to derived metadata`
from genuinely missing authority or evidence.

### `UI-005` — dense panels reduce usable reading width

Severity: medium.

The left panel begins with seven large facet cards even after a precise search,
while the selected-record panel remains open on the right. The centre still
works, but the main narrative and graph receive less width than the question
and evidence require.

Required follow-up: make Results the default panel for active searches and
collapse non-discriminating facets; preserve the existing resizable panels for
analytical use.

### `UI-006` — publication envelope and frozen overview disagree

Severity: medium.

The exact candidate was frozen before publication authorization, so its
embedded overview still says publication was not authorized. The later public
descriptor and authorization receipt correctly record authorization. Changing
the embedded overview would change the owner-authorized candidate hash.

Required follow-up: Explorer should give the descriptor's publication envelope
precedence in the visible status area while retaining the frozen historical
notice as provenance.

## Publication disposition

- Population-preview authorization: recorded in the publication descriptor and
  dated owner receipt; the frozen candidate retains its historical
  pre-authorization overview to preserve exact bytes.
- Release grade: false; 291 specialist-review warnings remain.
- GitHub Pages deployment: blocked by the plan/private-repository combination.
- Public-browser verification: not started because no deployment exists.
- Public URL: withheld.

The owner must explicitly choose either public visibility for the existing
repository or a separate public publication repository containing only the
allow-listed publication unit. The latter preserves the private authored
repository and is the safer default.
