# Review A Life in the UK

This is the public learning route for **A Life in the UK**, an independent
open-knowledge demonstrator built with Open Knowledge Format (OKF). It is for
people reviewing the idea, the implementation or the evidence. You do not need
a background in data, government services or the semantic web.

> Explore OKF covers all 293 service-family records in this project's governed
> denominator. That does not mean every UK public service or every local
> variation is represented. Records vary in depth; none has named specialist
> acceptance. Specialist review remains required for 291 records and is not
> required for 2. Use the linked official source before acting.

## Choose how much time you have

### Ten minutes: understand the concept

1. Open [Explore OKF](../explore/index.html).
2. Search for `missed bin` and choose **Report a missed rubbish collection**.
3. Change **Show official routes for** between England, Scotland, Wales and
   Northern Ireland. The nation control emphasises explicitly authored routes;
   it does not guess from a website address.
4. Compare the **Ordinary** episode with its **Exception** episode.
5. Open **Inspect bundle identity and provenance**. Notice that source,
   authority, evidence, rights and observation time remain visible.
6. Repeat the exercise with `find NHS dentist`.

If you prefer to test the data through an AI, use the
[provider-neutral copy-and-paste prompts](ask-an-ai.md). They point directly to
the public descriptor and governed journey projection and include a safe
download-and-attach fallback.

The point is not that a person follows every journey in the corpus. The model
connects possible life events, needs, services, steps, authorities,
jurisdictions, evidence and redress while keeping alternative and exception
routes separate.

### Thirty minutes: learn the foundations

Read these in order:

1. [The idea and semantic model](../research/overview.md) explains data,
   information, knowledge and ontology through an everyday missed-bin example.
2. [The complete beginner guide to OKF Explorer](https://chris-page-gov.github.io/okf-explorer/docs/beginners/)
   is a 22-chapter curriculum, beginning with the product in plain language and
   progressing through browsers, Markdown, graphs, provenance, responsible AI,
   building, testing and release governance.
3. [The missed-rubbish journey](../journeys/missed-rubbish-collection.md) shows
   a locally delivered service and complaint boundary.
4. [The learning-to-drive and speeding journey](../journeys/learning-to-drive-speeding.md)
   separates Great Britain and Northern Ireland routes and an enforcement
   exception.
5. [The death, bereavement and estate journey](../journeys/death-bereavement-estate.md)
   shows national differences, notification boundaries and private
   dependencies.

### Ninety minutes: review the evidence and controls

Continue through these layers:

1. [Ontology](../ontology/index.md) — the concepts and governed relationship
   types.
2. [Jurisdictions](../jurisdictions/index.md) — why UK, national and local
   applicability cannot safely be collapsed.
3. [Evidence](../evidence/index.md) and
   [licensing and attribution](../evidence/licensing-and-attribution.md) — what
   is linked, what is retained and what may be reused.
4. [Evaluation](../evaluation/README.md) — the competency questions, visible
   journeys and assurance boundary.
5. [The Claude journey-walker case study](../evaluation/ai-consumer/claude-journey-walker-case-study.md)
   — what another AI recovered well, what it misinterpreted and why the
   governed projection was added.
6. [AI-consumer evaluation](../evaluation/ai-consumer/README.md) — the isolated
   comparison method and why its incomplete private attempts do not support a
   published quantitative result,
   not a performance claim.
7. [Publication governance](review-and-publication-plan.md) — exact-byte,
   manual deployment and real-browser verification gates.

## What the public concept contains

The frozen project denominator contains:

- 293 authored service-family records across 24 life-course domains;
- 48 enclosing-process groupings;
- 586 authored ordinary and exception episodes with 881 ordered steps;
- 879 observed official-source links;
- governed aliases and explicit jurisdiction routes;
- stable relationship assertion identifiers, authority, evidence, rights and
  observation time; and
- machine-readable manifests and SHA-256 identities for the publication.

The `/explore/` interface is a presentation projection of that governed
material. It does not invent a cross-family sequence from display grouping,
upgrade a normalised assertion to official authority or turn a confidence
label into specialist acceptance.

## What it deliberately does not claim

This is not:

- an official government service or current service directory;
- evidence that every UK public service, local variation or user circumstance
  is covered;
- personalised eligibility, legal, medical, safeguarding or operational
  advice;
- a released data product or a specialist-approved service;
- proof that an AI has human-like understanding; or
- a complete or held-out comparison of OpenAI Codex and Anthropic Claude.

Source pages were observed at the corpus date. Their content can change, and
departmental network policy can block either GitHub Pages or a linked source.
Follow the current official source before making a decision.

## Designed for managed laptops

Explore OKF is deliberately low-dependency:

- one self-contained HTML file, about 5.4 MB before transfer compression;
- no runtime fetch or API call;
- no analytics, cookies or persistent browser storage;
- no service worker, third-party font, remote image or installation; and
- search across 293 family records in the browser.

It needs JavaScript. The hosted version needs access to `github.io`, and
official links need access to their destination. This makes it suitable for
testing on managed laptops, but it is not a promise that every Cabinet Office,
HMRC, GDS, Treasury or other departmental configuration will permit it. A
department-specific browser and network check remains necessary.

## How this was built

The Innovator established the problem, intent, risk boundaries and publication
choices. Codex carried out the research, authoring, data modelling, generation,
implementation, testing, failure analysis and documentation within those
constraints. The work was iterated when security, semantics, accessibility or
evaluation evidence exposed a weakness.

That division matters. The demonstrator shows how much disciplined work Codex
can complete with light strategic guidance. It does not present AI output as a
substitute for publication authority, service-owner judgement, specialist
acceptance, accessibility testing or independent evaluation.

## Detailed documentation library

### Orientation and worked examples

- [Repository guide and current status](../README.md)
- [Research origin and semantic model](../research/overview.md)
- [Missed-rubbish collection](../journeys/missed-rubbish-collection.md)
- [Learning to drive and speeding](../journeys/learning-to-drive-speeding.md)
- [Death, bereavement and estate administration](../journeys/death-bereavement-estate.md)

### Meaning, evidence and trust

- [Ontology](../ontology/index.md)
- [Jurisdictions](../jurisdictions/index.md)
- [Evidence](../evidence/index.md)
- [Licensing and attribution](../evidence/licensing-and-attribution.md)
- [Repository status](../REPOSITORY_STATUS.md)

### Evaluation and learning from other AI consumers

- [Evaluation overview](../evaluation/README.md)
- [Claude journey-walker case study](../evaluation/ai-consumer/claude-journey-walker-case-study.md)
- [AI-consumer evaluation method](../evaluation/ai-consumer/README.md)
- [Copy-and-paste prompts for using the bundle with an AI](ask-an-ai.md)

The AI comparison stopped after two different provider failures and did not
complete the planned matrix. Its answers are not yet bound to immutable runner
receipts, so no behavioural or comparative result is published. All 104
questions were used while developing the harness, leaving no untouched test set
and no promotion-grade performance claim.

### Build, reproduce and publish

- [Authoring guide](authoring.md)
- [Review and publication plan](review-and-publication-plan.md)
- [Pages publication unit](../publication/README.md)
- [Delivery tracking](../TRACKING.md)
- [Change log](../CHANGELOG.md)

The repository remains the canonical source and review history. Generated
Explorer JSON, relationship shards, adjacency, search indexes and manifests are
projections of authored sources and must not be hand-edited.

## Useful terms

**Service family**
: A stable, understandable grouping such as reporting a missed rubbish
  collection. It is not necessarily one transaction or one provider.

**Episode**
: An authored ordinary or exception route within one family.

**Assertion**
: A stated relationship with its identity, source, authority, evidence,
  status, scope, observation time and rights.

**Projection**
: A deterministic view generated from governed source material for a specific
  consumer. It is not a second semantic authority.

**Population-complete**
: Reconciled against this project's declared 293-family denominator. It does
  not mean exhaustive coverage of all real-world UK services.

**Release grade**
: A later gate requiring named specialist acceptance and other evidence. This
  demonstrator is not release grade.
