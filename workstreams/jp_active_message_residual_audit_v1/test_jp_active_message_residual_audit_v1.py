from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("build_jp_active_message_residual_audit_v1.py")
SPEC = importlib.util.spec_from_file_location("jp_active_message_residual_audit", MODULE_PATH)
assert SPEC and SPEC.loader
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class ClassificationTests(unittest.TestCase):
    def test_only_kana_without_hangul_is_high_confidence_japanese(self) -> None:
        self.assertEqual(
            AUDIT.classify_text("\u3053\u308c\u306f\u65e5\u672c\u8a9e\u3067\u3059"),
            "japanese_kana_no_hangul",
        )

    def test_hangul_and_kana_is_review_not_false_translation_backlog(self) -> None:
        self.assertEqual(
            AUDIT.classify_text("\ud55c\uad6d\uc5b4(\u304b\u306a)"),
            "mixed_hangul_kana_review",
        )

    def test_cjk_only_is_review_not_definite_japanese(self) -> None:
        self.assertEqual(
            AUDIT.classify_text("\u7e54\u7530"),
            "hanja_only_no_hangul_review",
        )

    def test_coordinate_contract_has_no_text_field(self) -> None:
        coordinate = AUDIT.coordinate_object("msggame", (13, 217, 0))
        self.assertEqual(coordinate, {"block_id": 13, "record_id": 217, "literal_id": 0})
        self.assertNotIn("text", coordinate)


class OutputSafetyTests(unittest.TestCase):
    def test_outside_workstream_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                AUDIT.assert_safe_output_dir(Path(directory), Path(directory) / "steam")

    def test_workstream_subdirectory_is_allowed(self) -> None:
        result = AUDIT.assert_safe_output_dir(AUDIT.WORKSTREAM / "test-output", Path("C:/steam-not-real"))
        self.assertTrue(result.is_relative_to(AUDIT.WORKSTREAM.resolve()))


if __name__ == "__main__":
    unittest.main()
