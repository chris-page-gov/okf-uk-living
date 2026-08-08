from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_life_course_dossiers import (  # noqa: E402
    BASELINE_FAMILY_IDS,
    expected_population_family_ids,
    validate_life_course_dossiers,
)
from life_course_dossiers import load_dossiers, resolve_sources  # noqa: E402
from render_life_course_packs import expected_outputs  # noqa: E402


class LifeCourseDossierTests(unittest.TestCase):
    def test_current_population_stage_is_valid(self) -> None:
        self.assertEqual([], validate_life_course_dossiers())

    def test_population_stage_resolves_link_only_sources(self) -> None:
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(expected_population_family_ids(), set(dossiers))
        sources = [source for dossier in dossiers.values() for source in resolve_sources(dossier)[0]]
        baseline_sources = [
            source for family_id, dossier in dossiers.items()
            if family_id in BASELINE_FAMILY_IDS
            for source in resolve_sources(dossier)[0]
        ]
        self.assertEqual(53, len(baseline_sources))
        self.assertEqual(53, len({source["id"] for source in baseline_sources}))
        self.assertTrue(all(source["snapshot"] is False for source in sources))
        self.assertTrue(all(source["resource"].startswith("https://") for source in sources))

    def test_pack_renderer_preserves_the_reviewed_driving_slice(self) -> None:
        outputs = {path.relative_to(ROOT).as_posix() for path in expected_outputs()}
        self.assertNotIn(
            "source/life-course-families/transition-to-adulthood/learn-to-drive-car.v1.yaml",
            outputs,
        )
        self.assertNotIn("services/learn-to-drive-car.md", outputs)
        self.assertIn("life-course/transition-to-adulthood.md", outputs)


if __name__ == "__main__":
    unittest.main()
