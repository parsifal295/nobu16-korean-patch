from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_current_state_textfit_rebase_v1_under_test",
    ROOT / "build_steam_jp_current_state_textfit_rebase_v1.py",
)
assert SPEC is not None and SPEC.loader is not None
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class CurrentStateTextfitRebaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        try:
            cls.contract, cls.validation = BUILD.load_frozen_contract()
            BUILD.verify_live_baseline(BUILD.DEFAULT_STEAM_ROOT, cls.contract)
        except BUILD.RebaseError as exc:
            raise unittest.SkipTest(str(exc)) from exc

    def test_01_frozen_public_artifacts_are_source_free_and_current_based(self) -> None:
        self.assertTrue(BUILD.source_free(self.contract))
        self.assertTrue(BUILD.source_free(self.validation))
        safety = self.contract["safety"]
        self.assertTrue(safety["current_steam_jp_is_the_only_resource_baseline"])
        self.assertFalse(safety["v09_full_text_archive_read"])
        self.assertFalse(safety["existing_nonlogo_composite_read"])
        self.assertFalse(safety["logo_or_logo_like_images_touched"])

    def test_02_current_text_rebase_is_deterministic(self) -> None:
        external = BUILD.load_external_inputs()
        first, line_first, text_first, _fonts, fullwidth_first = BUILD.build_current_candidate(BUILD.DEFAULT_STEAM_ROOT, external)
        second, line_second, text_second, _fonts_second, fullwidth_second = BUILD.build_current_candidate(BUILD.DEFAULT_STEAM_ROOT, external)
        self.assertEqual(first, second)
        self.assertEqual(line_first, line_second)
        self.assertEqual(text_first, text_second)
        self.assertEqual(fullwidth_first, fullwidth_second)
        BUILD.assert_expected_text_candidates(first, self.contract)
        self.assertEqual(line_first, self.contract["operations"]["linebreak"])
        self.assertEqual(fullwidth_first, self.contract["operations"]["fullwidth"])

    def test_03_res_jp_font_graft_preserves_3_and_24_without_using_them(self) -> None:
        external = BUILD.load_external_inputs()
        candidate, report = BUILD.rebase_one_font(BUILD.DEFAULT_STEAM_ROOT, BUILD.RES_JP, external)
        self.assertEqual({"packed": BUILD.spec(candidate)}, self.contract["expected_candidates"][BUILD.RES_JP])
        self.assertFalse(report["res_jp_3_24_replacement_sources_used"])
        self.assertEqual([entry["outer_entry"] for entry in report["res_jp_protected_entries"]], [3, 24])
        self.assertTrue(all(entry["byte_identical_to_current_base"] for entry in report["res_jp_protected_entries"]))

    def test_04_private_output_root_is_enforced(self) -> None:
        with self.assertRaises(BUILD.RebaseError):
            BUILD.safe_tmp_root(BUILD.WORKSTREAM / "candidate")
        with tempfile.TemporaryDirectory(dir=BUILD.TMP_ROOT) as temporary:
            root = BUILD.safe_tmp_root(Path(temporary))
            self.assertTrue(root.is_relative_to(BUILD.TMP_ROOT.resolve()))


if __name__ == "__main__":
    unittest.main(verbosity=2)
