# Authored and acquired source

Keep authored inputs and immutable acquired envelopes here. Document source
identity, observation time, rights, freshness and checksums before generation.

The first implemented source set uses a bounded, versioned linked-reference
register: [missed rubbish collection](missed-rubbish-collection.v1.yaml). It
contains no acquired page snapshots. Its `not_applicable_no_snapshot`
checksums and link-and-summary rights limit are intentional.
