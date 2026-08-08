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

    def test_projection_distinguishes_families_from_supporting_concepts(self) -> None:
        rows = json.loads(build_outputs()[Path("large/data/records-0.json")])
        families = [row for row in rows if row["record_type"] == "Service Family"]
        self.assertEqual(293, len(families))
        self.assertGreater(len(rows), len(families))
        self.assertEqual(6, sum(row["implementation_status"] == "population-complete-three-slice" for row in families))
        self.assertTrue(all("upstream-link-only-not-acquired" in row["rights_state"] for row in rows))

    def test_three_slices_project_narratives_sources_and_provenance(self) -> None:
        outputs = build_outputs()
        rows = json.loads(outputs[Path("large/data/records-0.json")])
        resources = json.loads(outputs[Path("large/data/resources-0.json")])
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        migrated = [
            row for row in rows
            if row.get("record_type") == "Service Family"
            and row.get("implementation_status") == "population-complete-three-slice"
        ]
        self.assertEqual(6, len(migrated))
        self.assertTrue(all(row.get("narrative", {}).get("body") for row in migrated))
        self.assertEqual(53, len(resources))
        self.assertTrue(all(resource["source_access"]["display_mode"] == "link" for resource in resources))
        self.assertTrue(all(resource["provenance"]["response_body_retained"] is False for resource in resources))
        for relationship in relationships:
            self.assertTrue({"assertion_status", "authority", "derivation", "evidence", "rights"} <= set(relationship))

    def test_static_search_indexes_all_planning_families(self) -> None:
        outputs = build_outputs()
        rows = json.loads(outputs[Path("large/data/records-0.json")])
        search = json.loads(outputs[Path("large/data/search/manifest.json")])
        postings = json.loads(outputs[Path("large/data/search/postings.json")])["tokens"]
        ordinal = next(index for index, row in enumerate(rows) if row["name"] == "report-missed-rubbish-collection")
        self.assertEqual(len(rows), search["counts"]["documents"])
        self.assertIn(ordinal, {item[0] for item in postings["missed"]})
        self.assertIn(ordinal, {item[0] for item in postings["rubbish"]})
        wave_filters = json.loads(outputs[Path("large/data/search/filters/acquisition_wave.json")])
        self.assertEqual(101, len(wave_filters["values"]["wave-3"]))


if __name__ == "__main__":
    unittest.main()
