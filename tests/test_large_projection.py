from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_large_corpus import build_outputs  # noqa: E402
from check_large_projection import validate_large_projection  # noqa: E402


class LargeProjectionTests(unittest.TestCase):
    def test_projection_is_valid(self) -> None:
        self.assertEqual([], validate_large_projection())

    def test_projection_is_deterministic(self) -> None:
        self.assertEqual(build_outputs(), build_outputs())

    def test_projection_contains_only_planning_metadata(self) -> None:
        rows = json.loads(build_outputs()[Path("large/data/records-0.json")])
        self.assertEqual(293, len(rows))
        self.assertTrue(all(row["assertion_status"] == "normalized" for row in rows))
        self.assertTrue(all(row["resource_count"] == 0 for row in rows))
        self.assertTrue(all("upstream-link-only-not-acquired" in row["rights_state"] for row in rows))

    def test_static_search_indexes_all_planning_families(self) -> None:
        outputs = build_outputs()
        rows = json.loads(outputs[Path("large/data/records-0.json")])
        search = json.loads(outputs[Path("large/data/search/manifest.json")])
        postings = json.loads(outputs[Path("large/data/search/postings.json")])["tokens"]
        ordinal = next(index for index, row in enumerate(rows) if row["name"] == "report-missed-rubbish-collection")
        self.assertEqual(293, search["counts"]["documents"])
        self.assertIn(ordinal, {item[0] for item in postings["missed"]})
        self.assertIn(ordinal, {item[0] for item in postings["rubbish"]})
        wave_filters = json.loads(outputs[Path("large/data/search/filters/acquisition_wave.json")])
        self.assertEqual(101, len(wave_filters["values"]["wave-3"]))


if __name__ == "__main__":
    unittest.main()
