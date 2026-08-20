from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE = Path(__file__).with_name("build_navigation_wheel_text_candidates_v1.py")
SPEC = importlib.util.spec_from_file_location("navigation_wheel_text_candidates_v1", MODULE)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)


class TextCandidateContractTests(unittest.TestCase):
    def test_candidate_contract_is_text_only_and_ai_free(self) -> None:
        self.assertEqual(builder.SCHEMA, "nobu16.kr.navigation-wheel-text-candidates.v1")
        self.assertEqual(builder.CELL_SIZE, (100, 95))
        self.assertEqual(builder.TARGET_INK_HEIGHT, 23)
        self.assertEqual(builder.INK_BOTTOM, 91)
        self.assertEqual(len(builder.LABELS), 5)
        self.assertEqual(len(builder.STYLES), 2)

    def test_candidate_ids_are_stable(self) -> None:
        parser = builder.parser()
        args = parser.parse_args(["--output", "unused"])
        self.assertEqual(
            [item.candidate_id for item in builder.candidates(args)],
            [
                "a_noto_serif_900",
                "b_seoul_hangang_eb",
                "c_yydimibang_bold",
                "d_noto_sans_850",
            ],
        )


if __name__ == "__main__":
    unittest.main()
