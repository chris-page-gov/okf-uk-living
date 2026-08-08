from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from check_search_acceptance import validate_search_acceptance  # noqa: E402


class SearchAcceptanceTests(unittest.TestCase):
    def test_current_population_stage_search_acceptance(self) -> None:
        self.assertEqual([], validate_search_acceptance())


if __name__ == "__main__":
    unittest.main()
