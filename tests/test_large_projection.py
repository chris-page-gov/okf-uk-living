from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from build_large_corpus import build_outputs, remove_generated_tree  # noqa: E402
from check_large_projection import validate_large_projection  # noqa: E402
from life_course_dossiers import load_dossiers, resolve_sources  # noqa: E402


def projected_rows(outputs: dict[Path, str]) -> list[dict[str, object]]:
    manifest = json.loads(outputs[Path("large/data/manifest.json")])
    return [
        row
        for path in manifest["chunks"]["datasets"]
        for row in json.loads(outputs[Path(path)])
    ]


class LargeProjectionTests(unittest.TestCase):
    def test_generated_tree_cleanup_ignores_finder_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "large-data"
            root.mkdir()
            (root / ".DS_Store").write_bytes(b"finder metadata")
            remove_generated_tree(root)
            self.assertFalse(root.exists())

    def test_projection_is_valid(self) -> None:
        self.assertEqual([], validate_large_projection())

    def test_projection_is_deterministic(self) -> None:
        self.assertEqual(build_outputs(), build_outputs())

    def test_projection_distinguishes_families_from_supporting_concepts(self) -> None:
        rows = projected_rows(build_outputs())
        families = [row for row in rows if row["record_type"] == "Service Family"]
        self.assertEqual(293, len(families))
        self.assertGreater(len(rows), len(families))
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(len(dossiers), sum(row["implementation_status"] == "population-complete" for row in families))
        self.assertTrue(all("upstream-link-only-not-acquired" in row["rights_state"] for row in rows))

    def test_population_stage_projects_narratives_sources_and_provenance(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
        resources = json.loads(outputs[Path("large/data/resources-0.json")])
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        migrated = [
            row for row in rows
            if row.get("record_type") == "Service Family"
            and row.get("implementation_status") == "population-complete"
        ]
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(len(dossiers), len(migrated))
        self.assertTrue(all(row.get("narrative", {}).get("body") for row in migrated))
        expected_resources = sum(len(resolve_sources(dossier)[0]) for dossier in dossiers.values())
        self.assertEqual(expected_resources, len(resources))
        self.assertTrue(all(resource["source_access"]["display_mode"] == "link" for resource in resources))
        self.assertTrue(all(resource["provenance"]["response_body_retained"] is False for resource in resources))
        for relationship in relationships:
            self.assertTrue({"assertion_status", "authority", "derivation", "evidence", "rights"} <= set(relationship))

    def test_shared_authority_infrastructure_is_searchable_and_reused(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
        relationships = json.loads(outputs[Path("large/data/relationships-0.json")])
        geographies = [row for row in rows if row["record_type"] == "Administrative Geography"]
        organisations = [row for row in rows if row["record_type"] == "Organisation"]
        self.assertEqual(397, len(geographies))
        self.assertEqual(438, len(organisations))
        hmcts = next(row for row in organisations if row["title"] == "HM Courts & Tribunals Service")
        self.assertTrue(any(edge["target"] == hmcts["route"] and edge["predicate"] == "offered-by" for edge in relationships))
        postings = json.loads(outputs[Path("large/data/search/postings.json")])["tokens"]
        ordinal = rows.index(next(row for row in organisations if row["title"] == "Financial Conduct Authority"))
        self.assertIn(ordinal, {item[0] for item in postings["financial"]})
        anglesey = rows.index(next(row for row in geographies if row["title"] == "Isle of Anglesey"))
        self.assertIn(anglesey, {item[0] for item in postings["mon"]})

    def test_static_search_indexes_all_planning_families(self) -> None:
        outputs = build_outputs()
        rows = projected_rows(outputs)
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
