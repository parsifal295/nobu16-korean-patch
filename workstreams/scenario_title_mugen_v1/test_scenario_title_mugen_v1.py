from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
BUILDER_PATH = Path(__file__).with_name("build_scenario_title_mugen_v1.py")
SPEC = importlib.util.spec_from_file_location("scenario_title_mugen_builder", BUILDER_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ScenarioTitleMugenTests(unittest.TestCase):
    def test_authoritative_overlays_use_literal_title(self) -> None:
        paths = (
            ROOT / "workstreams/switch_msgdata_v11/public/msgdata_ko_switch_v11_strict_transfer.v0.1.json",
            ROOT / "workstreams/steam_jp_common_messages_v1/public/msgdata_ko_steam_jp_native.v1.json",
            ROOT / "workstreams/steam_jp_runtime_skeleton_v1/public/strdata_ko_jp_source_rebased_24524.v1.json",
            ROOT / "workstreams/switch_strdata_v13_direct_transfer/public/strdata_ko_switch_v13_direct_transfer_24424.v1.json",
        )
        for path in paths:
            text = path.read_text(encoding="utf-8")
            self.assertNotIn(BUILDER.BEFORE, text, path)
            self.assertEqual(1, text.count(f'"ko": "{BUILDER.AFTER}"'), path)

    def test_official_language_matrix_is_pinned(self) -> None:
        self.assertEqual("夢幻の如く", BUILDER.OFFICIAL_TITLE_MATRIX["JP"])
        self.assertEqual("Like A Dream", BUILDER.OFFICIAL_TITLE_MATRIX["EN"])
        self.assertEqual("宛如梦幻", BUILDER.OFFICIAL_TITLE_MATRIX["SC"])
        self.assertEqual("如夢似幻", BUILDER.OFFICIAL_TITLE_MATRIX["TC"])
        self.assertEqual((0, 15026), BUILDER.STRDATA_COORDINATE)
        self.assertEqual(15118, BUILDER.MSGDATA_ID)


if __name__ == "__main__":
    unittest.main()
