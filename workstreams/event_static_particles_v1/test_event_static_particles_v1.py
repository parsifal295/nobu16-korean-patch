from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_event_static_particles_v1.py")
SPEC = importlib.util.spec_from_file_location("event_static_particles_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)


class EventStaticParticlesV1Tests(unittest.TestCase):
    def test_batchim_and_rieul_direction(self) -> None:
        self.assertEqual(4, MODULE.jongseong_index("산"))
        self.assertEqual(0, MODULE.jongseong_index("라"))
        self.assertEqual(8, MODULE.jongseong_index("길"))
        self.assertEqual("으로", MODULE.select_surface("direction", "로", "산"))
        self.assertEqual("로", MODULE.select_surface("direction", "로", "라"))
        self.assertEqual("로", MODULE.select_surface("direction", "로", "길"))

    def test_name_token_components(self) -> None:
        texts = [""] * 76
        texts[75] = "아시카가 요시테루"
        self.assertEqual("아시카가 요시테루", MODULE.rendered_name(texts, "b", 75))
        self.assertEqual("요시테루", MODULE.rendered_name(texts, "bm", 75))
        self.assertEqual("아시카가", MODULE.rendered_name(texts, "bs", 75))

    def test_numeric_subject_is_found_but_coloured_house_suffix_is_not(self) -> None:
        subject = "\x1bCB[bs1871]\x1bCZ가 손을 뻗었다."
        clan = "\x1bCB[bs1871]\x1bCZ가\x1bCZ의 당주"
        self.assertEqual(1, len(MODULE.find_numeric_boundaries(8444, subject)))
        self.assertEqual(0, len(MODULE.find_numeric_boundaries(4086, clan)))

    def test_ordinary_copula_is_not_mistaken_for_subject_particle(self) -> None:
        text = "그 인물은 \x1bCA[b1221]\x1bCZ이다."
        self.assertEqual((), MODULE.find_numeric_boundaries(8610, text))

    def test_all_particle_families_select_expected_forms(self) -> None:
        cases = (
            ("topic", "는", "도산", "은"),
            ("subject", "이", "가게토라", "가"),
            ("object", "를", "도산", "을"),
            ("comitative", "와의", "도산", "과의"),
            ("optional_i_copula", "라는", "도산", "이라는"),
            ("past_copula", "였다", "도산", "이었다"),
        )
        for family, source, name, expected in cases:
            with self.subTest(family=family, source=source, name=name):
                self.assertEqual(expected, MODULE.select_surface(family, source, name))

    def test_layout_measurement_uses_static_patch_007_scale(self) -> None:
        texts = [""] * 76
        texts[75] = "아시카가 요시테루"
        row = MODULE.changed_row_layout(
            4000, "\x1bCA[bm75]\x1bCZ는 A", texts
        )
        line = row["lines"][0]
        self.assertEqual("요시테루는 A", line["visible_string"])
        self.assertEqual(5, line["fullwidth_character_count"])
        self.assertEqual(2, line["halfwidth_character_count"])
        self.assertEqual(288, line["raw_g1n_width_px"])
        self.assertEqual(180, line["effective_width_px"])
        self.assertFalse(line["exceeds_912px"])


if __name__ == "__main__":
    unittest.main()
