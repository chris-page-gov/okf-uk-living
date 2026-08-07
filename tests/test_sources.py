from __future__ import annotations

from copy import deepcopy
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_sources import (  # noqa: E402
    EXPECTED_BEREAVEMENT_IDS,
    EXPECTED_DRIVING_SPEEDING_IDS,
    EXPECTED_MISSED_RUBBISH_IDS,
    validate_source_register,
    validate_source_registers,
)


class SourceRegisterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.registers, self.errors = validate_source_registers()
        self.registers_by_slice = {register["slice_id"]: register for register in self.registers}
        self.register = self.registers_by_slice["missed-rubbish-collection"]

    def test_source_register_is_valid(self) -> None:
        self.assertEqual([], self.errors)

    def test_bounded_source_denominator_is_fixed(self) -> None:
        self.assertEqual(EXPECTED_MISSED_RUBBISH_IDS, {source["id"] for source in self.register["sources"]})
        driving = self.registers_by_slice["learning-to-drive-speeding"]
        self.assertEqual(EXPECTED_DRIVING_SPEEDING_IDS, {source["id"] for source in driving["sources"]})
        bereavement = self.registers_by_slice["death-bereavement-estate"]
        self.assertEqual(EXPECTED_BEREAVEMENT_IDS, {source["id"] for source in bereavement["sources"]})

    def test_registered_denominator_has_fifty_three_links(self) -> None:
        self.assertEqual(53, sum(len(register["sources"]) for register in self.registers))

    def test_no_snapshots_or_broad_acquisition(self) -> None:
        self.assertFalse(self.register["acquisition"]["snapshots_acquired"])
        self.assertFalse(self.register["acquisition"]["broad_acquisition"])
        self.assertTrue(all(source["checksum"] == "not_applicable_no_snapshot" for source in self.register["sources"]))

    def test_validator_rejects_snapshot_claim(self) -> None:
        register = deepcopy(self.register)
        register["sources"][0]["checksum"] = "sha256:not-a-real-envelope"
        errors = validate_source_register(register)
        self.assertTrue(any("must not claim a snapshot checksum" in error for error in errors))

    def test_validator_rejects_rights_overclaim(self) -> None:
        register = deepcopy(self.register)
        register["sources"][0]["rights_basis"] = "unrestricted"
        errors = validate_source_register(register)
        self.assertTrue(any("linked-summary limits" in error for error in errors))

    def test_rights_decisions_are_recorded_without_relaxing_use(self) -> None:
        self.assertEqual(
            "link_and_summarize_source_family_decisions_recorded",
            self.register["acquisition"]["rights_policy"],
        )
        self.assertTrue(
            all(
                source["rights_basis"]
                == "linked_reference_summary_only_source_family_decision_recorded"
                for source in self.register["sources"]
            )
        )


if __name__ == "__main__":
    unittest.main()
