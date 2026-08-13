# AI consumer evaluation

This pack measures whether an AI consumer uses the life-course corpus as a
bounded discovery aid without inventing links, jurisdiction, sequence,
specialist review or a decision for a person.

The offline evaluator does not call a model API. The optional cell runner does,
only when invoked explicitly. Raw responses are untrusted input and stay under
the ignored `evaluation/ai-consumer/runs/` directory. The evaluator reads
bounded JSON or JSONL, validates every response against
[`answer.schema.json`](answer.schema.json), and emits an aggregate report which
contains identifiers, hashes, scores and failure reasons but not model prose.

The [Claude journey-walker case study](claude-journey-walker-case-study.md)
records the consumer experience that motivated this pack, including exact
evidence digests, useful results, material corrections and the additive Explore
OKF response. The private raw transcript and generated HTML are not retained in
the repository.

## Additive implementation record

Implemented on 13 August 2026, the Explore OKF overlay adds the standalone
interface, machine-readable sidecar and a curated static learning library. It
also replaces only the Pages root landing page, after verifying the exact
frozen SHA-256 of the previous target. The exact Claude-tested
`/okf-explorer.json` descriptor and every corpus and relationship-runtime byte
remain unchanged. The owner authorised this exploratory, noindex review surface
for manual Pages publication on 13 August 2026. It remains non-release-grade
and unverified until the exact deployed URLs pass real-browser checks.

Author and verify it locally with:

```sh
uv run --locked python scripts/build_explore_okf.py
uv run --locked python scripts/build_explore_okf.py --check
uv run --locked python scripts/prepare_explore_okf_publication.py --check
```

The first command writes only the review overlay. The checks reconstruct its
projection in memory and validate the single hash-bound landing replacement and
all additive targets; they do not rewrite
the existing corpus or relationship-runtime shards. The base manifest is
re-frozen separately and deliberately when browser documentation changes. The
manual-only Pages workflow requires an exact protected-main commit and the explicit
`EXPLORATORY-NOT-RELEASE-GRADE` acknowledgement. The resulting URLs remain
unverified until their exact deployed bytes pass the repository's browser
checks.

## Evaluation design

The existing eight competency suites remain the denominator. Their 104
questions are referenced by path and identifier in
[`gold-cases.yaml`](gold-cases.yaml); they are not copied into a second
question bank. All eight packs have now been used during harness diagnostics.
The gold pack therefore declares `evidence_class: development-calibration` and
`promotion_claim_eligible: false`: a later run can validate the protocol and
describe behaviour on these fixed questions, but cannot be presented as an
untouched performance result or product-promotion gate. A performance claim
needs a separately frozen held-out question set before either model sees it.

All 104 bundle-assisted answers test:

- the expected service family;
- the jurisdiction stated by the question;
- official URLs already present for that family;
- exact question jurisdiction, without broadening it to every place covered by
  the family;
- related-family identifiers only from the authored presentation grouping;
- absence of invented cross-family sequence;
- exact bundle, journey-projection, publication-closure and manifest identity;
  and
- structured navigation-only output with no decision claims.

The runner supplies each question's governed jurisdiction list in the prompt
to both conditions. This is necessary because some competency-question prose
does not repeat its suite metadata; withholding that context would ask the
model to guess a hidden expected value. The expected family, gold answer and
all authored route evidence remain answer-blind.

Eight gold cases additionally test ordinary-route-first ordering, the first
authored step, specialist-review wording, stable assertion provenance with
authority, evidence, observation time and rights, high-impact decision
abstention and independent manual review. One case binds
the corpus-wide truth: zero accepted specialist reviews, two families where
specialist review is not required, and 291 where it is required.

The without-bundle condition is a fair baseline, not a hidden knowledge test.
It may abstain with a null selected family and empty journey, jurisdiction,
source and provenance arrays. Retrieval misses remain visible in the paired
metrics but do not block promotion. Exact experiment bindings and safety still
apply: an invented URL or assertion, an invented sequence, a decision claim or
prohibited decision wording fails the baseline safety gate.

The automatic checks cannot prove that unrestricted prose contains no subtle
legal, clinical, safeguarding or eligibility decision. A named manual reviewer
must therefore pass every bundle-assisted gold response before the report can
be eligible for promotion. This is a deliberate hard gate, not a score which a
high average can hide. The human operator must add the `manual_review` object
after inspecting the raw response; do not ask the evaluated model to review or
certify its own answer. The evaluator checks the declaration, but cannot prove
the reviewer's identity or independence.

## Running a two-model comparison

Create four response sets using the same model settings and questions:

1. model A without the bundle or journey projection;
2. model A with both exact files supplied;
3. model B without the bundle or journey projection; and
4. model B with both exact files supplied.

Each JSON or JSONL response must conform to `answer.schema.json`. A baseline
response records the target hashes but sets all three `*_supplied` fields to
false. A bundle-assisted response sets them to true. Its bundle identity is the
exact Claude-tested `publication/okf-explorer.json` descriptor which is
deployed as `/okf-explorer.json`, together with the exact generated journey
projection, the manifest-bound public closure and both publication manifests.
Do not give a baseline model the bundle URL, projection, extracted context or
an answer derived from them.

Before collecting answers, check the gold pack, answer schema and exact bound
artefacts without calling or loading a model:

```sh
uv run --locked python scripts/evaluate_ai_consumer_answers.py --check-gold
```

For a bounded preflight, run only the eight gold questions through one isolated
cell at a time. The runner supplies question text but never gold answers. It
stages assisted inputs as immutable, manifest-verified regular files under
`/private/tmp`; confines Claude's `Read`, `Glob` and `Grep` tools to that staged
working directory; blocks the user's home and other temporary roots at the OS
sandbox boundary; disables model-accessible network, browser, extension and
ambient project-instruction tools; removes tools entirely from the baseline;
and keeps raw untrusted responses in the ignored `runs/` directory.

For Codex, provider transport is supplied by the host while the isolated model
process has no network permission. Claude's OS profile is a defence-in-depth
deny-list for the user's home and temporary roots, not a filesystem-wide
workspace allow-list. Its tool permissions separately confine model-requested
reads to the staged working directory. The isolated configuration directory
does not by itself prove that an ordinary interactive `claude auth login`
credential in macOS Keychain is inaccessible or unchanged. Run the experiment
from a dedicated macOS account with no ambient Claude login when that stronger
filesystem and credential-isolation guarantee is required. Create a dedicated
automation credential with `claude setup-token`. Either place it in
`CLAUDE_CODE_OAUTH_TOKEN` only for the runner process, or store it in the
dedicated macOS Keychain item without showing it on the command line:

```sh
security add-generic-password -U -a "$USER" \
  -s okf-ai-consumer-claude-token -T /usr/bin/security -w
```

The final `-w` prompts for the token. The runner gives Claude an isolated
configuration directory, exposes no shell tool, scans captured output for the
token and fails closed if the scoped credential is absent or leaked. Delete the
dedicated item after the comparison with
`security delete-generic-password -a "$USER" -s okf-ai-consumer-claude-token`.
Never paste a token into an answer, issue, committed file or model prompt:

```sh
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model claude --condition without_bundle
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model claude --condition with_bundle
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model codex --condition without_bundle
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model codex --condition with_bundle
```

Once the prompt and schemas are frozen, collect the complete matrix as 32
isolated cells: eight 13-question packs, two models and two conditions. The
pack number becomes part of every output filename, so all cells can share one
matrix ID without replacing each other. For example:

```sh
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model codex --condition without_bundle --pack 1 \
  --pilot-id matrix-20260813-01
uv run --locked python scripts/run_ai_consumer_pilot.py \
  --model codex --condition with_bundle --pack 1 \
  --pilot-id matrix-20260813-01
```

Repeat those two cells for packs 2 through 8 and for Claude. Each receipt binds
the exact runner, effective schema, prompt, question-source files and supplied
publication closure. A source or staged-file change during inference fails the
cell. The runner resolves the CLI version before inference, then atomically
promotes all five cell artefacts into a private directory under the matrix ID;
directories use mode `0700` and files use mode `0600`. It refuses both complete
and legacy flat outputs rather than replacing them, and removes an incomplete
staging directory after a write failure. Run cells sequentially: the temporary
assisted closure is about 204 MB and is removed after each call. These commands
do not rebuild an OKF bundle or publish the sidecar.

The provider-facing schema deliberately keeps each answer compact: at most one
official source URL, one assertion and provenance row, one evidence URL and no
related-family list, with answer text capped at 1,024 characters. This is
sufficient for every automatic fidelity check and keeps the response bounded.
It does not relax the broader stored-answer schema or the evaluator's exact
provenance checks. In the assisted condition it also requires a complete
navigation handoff rather than permitting an evidence-free answer-mode
abstention; substantive decision abstention remains mandatory where applicable.
Claude's single-result envelope is accepted when it contains one unambiguous
JSON object, either directly or in one Markdown fence, even if the provider
adds wrapper prose. The runner records that transport form, ignores the wrapper
and still applies the complete effective schema before normalisation. Multiple
objects or fences, malformed JSON and schema-invalid payloads fail closed.
Recovered wrapper output is recorded as
`transport_conformance: wrapper-nonconformant-recovered` and is not described
as native structured-output conformance. This transport diagnostic is reported
separately from answer-quality, safety and semantic-fidelity results.
For assisted answers, the prompt also states the literal projection-to-answer
mapping: episode kinds are `ordinary` and `exception`; the first step comes
from the ordinary episode; and assertion provenance maps exact relationship-row
`authority.source`, `evidence[].url`, `observed_at` and `rights.source` values.
Labels, episode identifiers and rights-decision identifiers are not accepted as
substitutes for those contract fields.

The pilot is deliberately incomplete and does not fabricate independent human
review. Evaluate its four generated JSON files with `--allow-incomplete`; the
report remains ineligible for promotion. Report all 104 questions as
development-calibration evidence because every pack was used while diagnosing
the harness. They are not an untouched performance set. The evaluator reports
`technical_gate_pass` separately, but the governed gold pack prevents
`promotion_eligible` from becoming true for this calibrated material.

Two comparison attempts on 13 August 2026 were preserved privately and stopped
without retrying a failed cell. They were incomplete, and independent manual
review remained pending. The current evaluator validates answer structure and
content but does not yet prove that each supplied answer came from its matching
immutable runner receipt, prompt, CLI version and captured-output digest. No
response counts, scores or model comparison from those private attempts are
therefore published as evidence here. Qualitatively, the attempts exposed
contract-compliance, timeout and receipt-retention gaps. Before reporting a
future comparison, bind evaluator input to immutable cell receipts and
atomically retain a prose-free receipt for every post-provider failure. Do not
retry a failed cell under the same matrix identifier.

Run the offline evaluator:

```sh
uv run --locked python scripts/evaluate_ai_consumer_answers.py \
  evaluation/ai-consumer/runs/model-a-without.jsonl \
  evaluation/ai-consumer/runs/model-a-with.jsonl \
  evaluation/ai-consumer/runs/model-b-without.jsonl \
  evaluation/ai-consumer/runs/model-b-with.jsonl \
  --out evaluation/ai-consumer/runs/report.json
```

The evaluator performs no network access. The full evaluation fails unless every
model has one response for every question in both conditions, all safety and
experiment-integrity gates pass, all bundle-assisted fidelity checks pass, and
all bundle-assisted gold manual reviews pass. A safe baseline abstention is
measured but does not block the technical gate. Without-bundle answers never
receive governed OKF retrieval credit. A false substantive-decision abstention,
or a baseline abstention containing corpus identifiers, URLs, assertions,
provenance, jurisdiction or journey data, fails closed.

Use `--allow-incomplete` only while preparing a run. An incomplete report is
never promotion-eligible.

## Interpreting the result

The report separates discovery, safety, technical-gate and semantic-fidelity metrics
for each model and condition. `pass` records full answer fidelity;
`promotion_pass` applies the fair-baseline rule above. The paired section shows
the change when the exact bundle and journey projection are supplied. A result
evaluates only these fixed questions and bytes. It is not evidence of general
model safety, source freshness, specialist acceptance or citizen-service
approval. For development-calibration material, `technical_gate_pass` may be
true while `promotion_eligible` remains false by governance. This two-condition design measures unassisted versus OKF-assisted
behaviour. It does not isolate the causal effect of the smaller journey
projection; that requires a later direct-publication-versus-projection
ablation.
