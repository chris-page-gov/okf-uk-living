# Vertical-slice fixture contracts

These three YAML fixtures define the owner-approved minimum acceptance boundary
for the first implementation slices. They are synthetic, `editorial-example`
contracts, not official service data and not personalized decision rules:

- [`missed-rubbish-collection.v1.yaml`](missed-rubbish-collection.v1.yaml)
- [`learning-to-drive-speeding.v1.yaml`](learning-to-drive-speeding.v1.yaml)
- [`death-bereavement-estate.v1.yaml`](death-bereavement-estate.v1.yaml)

Every fixture must reference `okf-domain-profile.v1`, declare synthetic data,
cover ordinary and exception paths, and exercise evidence, time, jurisdiction,
authority, governing rules, private-sector dependencies, redress and
provenance. Candidate source families are planning inputs only. Bounded source
registration is authorized; all three fixtures now point to their registered
linked-reference denominators. This completes the approved acquisition scope
but does not authorize broad acquisition.

Run `uv run --locked python scripts/check_contracts.py` to validate the profile
and fixtures. Passing validation means the contracts are internally complete;
it does not approve the profile or establish that any anticipated domain fact
is official.
