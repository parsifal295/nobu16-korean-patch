from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
SCRIPT = HERE / "build_pk_policy_readings_v1.py"
SPEC = importlib.util.spec_from_file_location("pk_policy_readings_test_module", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class PolicyReadingContractTests(unittest.TestCase):
    def test_exact_coordinate_vectors(self) -> None:
        self.assertEqual(25, MODULE.PAIR_COUNT)
        self.assertEqual(tuple(range(21_256, 21_281)), MODULE.DISPLAY_IDS)
        self.assertEqual(tuple(range(21_356, 21_381)), MODULE.READING_IDS)
        self.assertTrue(
            all(
                reading_id - display_id == 100
                for display_id, reading_id in zip(
                    MODULE.DISPLAY_IDS, MODULE.READING_IDS, strict=True
                )
            )
        )

    def test_preimages_are_exactly_ascii(self) -> None:
        self.assertEqual(set(MODULE.READING_IDS), set(MODULE.READING_PREIMAGES))
        self.assertTrue(
            all(
                MODULE.ASCII_ONLY_RE.fullmatch(value) is not None
                for value in MODULE.READING_PREIMAGES.values()
            )
        )

    def test_replacements_are_exactly_hangul(self) -> None:
        self.assertEqual(set(MODULE.READING_IDS), set(MODULE.READING_REPLACEMENTS))
        self.assertTrue(
            all(
                MODULE.HANGUL_ONLY_RE.fullmatch(value) is not None
                for value in MODULE.READING_REPLACEMENTS.values()
            )
        )

    def test_reviewed_anchors(self) -> None:
        self.assertEqual("세이도카이신니", MODULE.READING_REPLACEMENTS[21_356])
        self.assertEqual("조닌노오키테", MODULE.READING_REPLACEMENTS[21_365])
        self.assertEqual("가이센시키모쿠", MODULE.READING_REPLACEMENTS[21_377])
        self.assertEqual("텐마세이", MODULE.READING_REPLACEMENTS[21_379])
        self.assertEqual("군지세이", MODULE.READING_REPLACEMENTS[21_380])

    def test_output_pin_is_locked(self) -> None:
        self.assertEqual(476_860, MODULE.OUTPUT_PIN["packed_size"])
        self.assertEqual(
            "6D7DEA6149FE9B40951B507E7E210A614169D8CB19AEDE3EB85BC8B15EDF2410",
            MODULE.OUTPUT_PIN["packed_sha256"],
        )

    def test_display_names_are_read_only(self) -> None:
        self.assertEqual(set(MODULE.DISPLAY_IDS), set(MODULE.DISPLAY_PREIMAGES))
        self.assertTrue(set(MODULE.DISPLAY_IDS).isdisjoint(MODULE.READING_REPLACEMENTS))


if __name__ == "__main__":
    unittest.main()
