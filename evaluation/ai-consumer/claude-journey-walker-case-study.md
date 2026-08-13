# Claude journey-walker consumer evaluation — 13 August 2026

## Result

The test is useful evidence that a general-purpose AI can hydrate the public
OKF descriptor, recover the population shape and rapidly make a portable
journey-discovery prototype. It is not evidence that the generated product
fully understood the governed bundle or is safe to offer as citizen guidance.

The output preserved the important high-level boundary that it was a discovery
aid rather than an official service. It also demonstrated a promising
interaction pattern. However, it discarded semantic and assurance fields that
are needed to interpret journeys correctly. The resulting errors are material:
review status was overstated, exception routes were often presented first,
related families were described as ordered steps, and jurisdiction was inferred
from labels and host names.

This evaluation therefore treats the supplied result as a consumer case study,
not as a publication artefact. Its useful interaction pattern informs the
additive Explore OKF reference product under `/explore/`. The tested public
`okf-explorer.json` descriptor remains the canonical entrypoint and is not
replaced or rewritten by that work.

## Test and evidence boundary

The supplied task asked Claude to use the verified public
[`okf-explorer.json` descriptor](https://chris-page-gov.github.io/okf-uk-living/okf-explorer.json),
assess what it contained and produce a standalone HTML journey walker. The
exact model version, model settings, tool transcript and fetched source bytes
were not recorded. The test cannot therefore be reproduced as a controlled
model benchmark.

The two user-supplied files were inspected locally. They have not been copied
into this repository because they are private raw evaluation material. Their
identities are recorded so that the exact inputs can be recognised without
redistributing them.

| Supplied evidence | Bytes | Lines | SHA-256 | Repository retention |
|---|---:|---:|---|---|
| `okf-journey-walker.html` | 2,107,344 | 457 | `7457f5b035276888e6115c8522847393b1207461633d7b95c5d274f5ebac6179` | Digest and findings only |
| Claude task transcript, supplied as `pasted-text.txt` | 13,214 | 101 | `bedc34a495bf460318299aa48a8576bad54fa8fcdc78f4fe7cc3273d370dcdbc` | Digest and findings only |

The digests identify the supplied bytes. They do not prove authorship,
correctness or the model configuration used to create them.

## Which bundle Claude found

There is not a second, hidden monolithic “full bundle”. The 2,898-byte public
`okf-explorer.json` file is a descriptor: it points to the sharded publication
containing 9,757 records and 15,810 governed relationships. Claude followed
those entrypoints and distilled the journey fields it selected into the
2,107,344-byte standalone HTML file.

The separate 1,920,910-byte `okf-bundle.json` contains 392 Markdown nodes and
318 authored-link edges. It is the compact OKF and legacy-viewer compatibility
bundle, not the richer semantic population that Claude used. Explore OKF should
therefore remain a new consumer of the descriptor-backed publication, with a
small governed projection of its own. It should not replace either existing
entrypoint or require clients to download the whole published tree.

## What worked

- Claude followed the small descriptor into the sharded publication and
  recovered the headline population: 293 families, 24 domains and 48 enclosing
  processes.
- The generated file embedded 586 episodes, 881 steps and 879 official-source
  links in about 2.1 MB, with no runtime fetch, browser storage or telemetry.
- The interaction joined search, domain and nation filters, journey episodes,
  official links and related-family discovery in one portable page.
- The transcript and interface retained a visible non-official, discovery-aid
  boundary.

These are strong signs of machine readability and rapid prototyping value. They
do not establish semantic fidelity, security, accessibility or citizen
readiness.

## Material findings

| Finding | Supplied result | Governed interpretation and correction |
|---|---|---|
| Specialist review | The footer described two families as specialist-reviewed. | The review report records zero named specialist acceptances, 291 families requiring specialist review and two for which it is not required. Population-complete does not mean specialist-reviewed or release-grade. |
| Episode order | Exception routes appear first for 145 families; ordinary routes appear first for 148. | The extraction discarded the authored `episode_kind` and order. The ordinary route must be identified explicitly and shown separately from exceptions. |
| Related families | Families sharing an enclosing process were presented as other steps in a journey. | They are related families within the same process. The graph does not assert that they form one cross-family sequence. |
| Journey inference | The analysis inferred cross-family chains and likely bottlenecks. | `follows` and `precedes` order steps inside an authored episode. They do not justify an invented cross-family route or operational bottleneck. |
| Jurisdiction | Nation filtering used label substrings; source jurisdiction was inferred from host names. | Jurisdiction and source applicability must come from explicit authored fields. `Great Britain`, `United Kingdom`, `England and Wales` and local applicability cannot be reduced safely to a nation-name substring or a GOV.UK host. |
| Filter state | Changing nation after selecting a dossier could leave a result selected without safely rerendering it. | Filter state and selected-record state must be reconciled deterministically. |
| Search | Search used a reduced text index and omitted authored aliases. | The governed aliases must be searchable. Representative acceptance terms include `missed bin` and `find NHS dentist`. |
| Provenance | The embedded family objects omitted bundle identity, stable IRIs, relationship assertion IDs, authority, evidence, rights, observation time and review status. | A reference projection must preserve the minimum evidence-bearing semantic fields and bind itself to an exact source snapshot. |
| Standalone security | The file made no runtime request or persistent write, but it had no content security policy, declared `lang="en"`, and used HTML-string insertion and inline event-handler patterns. | A publishable file needs `en-GB`, a restrictive content security policy, safe DOM construction, validated HTTPS links and no unsafe inline execution. Offline behaviour alone does not remove injection or integrity risk. |

## Effectiveness assessment

| Dimension | Assessment |
|---|---|
| Finding and loading the corpus | Strong |
| Recovering headline structure | Strong |
| Preserving governed semantics | Mixed |
| Provenance and auditability | Weak |
| Rapid interaction prototyping | Strong |
| Secure, accessible standalone delivery | Not demonstrated |
| Citizen-facing readiness | Not suitable |

The most useful conclusion is that OKF enabled a capable consumer to get from a
small public entrypoint to a rich working prototype quickly. The principal gap
is not access to more data. It is a smaller, governed consumer projection that
makes the correct interpretation difficult to lose.

## Corrected Explore OKF reference product

The lean next move has been implemented locally as an additive
`/explore/index.html` standalone view and root
`explore-okf.json` descriptor, generated from the same authored source as the
existing publication. The sidecar also publishes the exact
`/explore/journey-projection.json`, `/explore/endpoint-labels.json` and
`/explore/data-manifest.json` inputs used by the standalone view. These files
must not change the already tested `okf-explorer.json` descriptor or the
existing Explorer routes.

The sidecar provides:

- an exact snapshot and digest binding;
- stable family, process, episode, step, source and assertion identities;
- explicit aliases, jurisdiction and primary-source mappings;
- graph-derived episode ordering with ordinary and exception routes separated;
- evidence, rights, observation time, authority and review state;
- wording that distinguishes a related family from an ordered journey step;
- a secure standalone `en-GB` HTML reference view with no runtime fetch,
  storage or telemetry, restrictive content security policy and safe DOM
  rendering; and
- a persistent warning that it is a research and service-design aid, not a
  personalised, legal, medical or official decision service.

“Reference product” means a conforming interpretation of the governed bundle.
It is not a claim that an AI or interface has human-like understanding. The
local sidecar is not a public product until its exact deployed URL passes the
repository's real-browser identity and journey checks.

## Acceptance and next evaluation

The reference projection and standalone view pass local deterministic checks
covering:

- all 293 families, 24 domains, 48 enclosing processes and 104 competency
  questions;
- ordinary and exception episode order, explicit jurisdiction, review status,
  provenance and rights;
- representative alias searches, including `missed bin` and
  `find NHS dentist`;
- exact source-snapshot and projection digests;
- no background requests, browser storage or telemetry;
- content security policy, safe outbound URLs, keyboard operation and visible
  focus; and
- preservation of the existing descriptor and published Explorer behaviour.

The controlled follow-up recorded model settings, bundle snapshot, publication
closure, prompt, output schema, question sources and private raw output. Two
no-retry attempts remained incomplete, and independent review was not
fabricated. The current offline evaluator does not yet bind each supplied
answer to its matching immutable runner receipt, so this public case study does
not report response counts, scores, behavioural results or a model comparison
from those private attempts. The attempts identified areas for further harness
investigation, including contract compliance, timeouts, family selection,
evidence and receipt binding.

All 104 questions were used while diagnosing the harness. They are therefore
development-calibration evidence, not an untouched performance set. A later
ablation must compare direct publication access with projection-assisted
access before making a causal claim, and any performance claim needs a newly
frozen held-out question set. The offline pack at
`evaluation/ai-consumer/README.md` defines these boundaries without retaining
model prose in its aggregate report.
