from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_life_course_dossiers import validate_life_course_dossiers  # noqa: E402
from life_course_dossiers import load_dossiers, resolve_sources  # noqa: E402


class LifeCourseDossierTests(unittest.TestCase):
    def test_three_slice_dossiers_are_valid(self) -> None:
        self.assertEqual([], validate_life_course_dossiers())

    def test_six_families_resolve_all_53_reference_records(self) -> None:
        dossiers, errors = load_dossiers()
        self.assertEqual([], errors)
        self.assertEqual(6, len(dossiers))
        sources = [source for dossier in dossiers.values() for source in resolve_sources(dossier)[0]]
        self.assertEqual(53, len(sources))
        self.assertEqual(53, len({source["id"] for source in sources}))
        self.assertTrue(all(source["snapshot"] is False for source in sources))
        self.assertTrue(all(source["resource"].startswith("https://") for source in sources))


if __name__ == "__main__":
    unittest.main()
