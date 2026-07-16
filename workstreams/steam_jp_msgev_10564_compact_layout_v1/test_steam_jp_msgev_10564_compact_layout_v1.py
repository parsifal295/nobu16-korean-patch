from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_msgev_10564_compact_layout", WORKSTREAM / "build_steam_jp_msgev_10564_compact_layout_v1.py"
)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)


SOURCE_TEXT = (
    "\x1bCB도쿠가와\x1bCZ에게 적의가 없다고 전해진 이상, "
    "\x1bCB도쿠가와\x1bCZ를 따라야\n한다고 제안한 "
    "\x1bCA가쓰모토\x1bCZ는 \x1bCB도쿠가와\x1bCZ에 아첨하는\n"
    "역신으로 여겨져 \x1bCB도요토미 가문\x1bCZ 안에서 더욱 고립된다."
)


class CompactLayoutTests(unittest.TestCase):
    def test_overlay_is_hash_pinned_and_preserves_the_token_profile(self) -> None:
        entry = builder.load_entry()
        self.assertEqual(entry["id"], 10564)
        self.assertEqual(builder.text_hash(SOURCE_TEXT), entry["preimage_utf16le_sha256"])
        builder.validate_entry(SOURCE_TEXT, entry)

        target = builder.message_profile(entry["ko"])
        self.assertEqual(target["line_breaks"], ["\n", "\n"])
        for key, expected in entry["preserved"].items():
            self.assertEqual(target[key], expected)

    def test_target_fits_three_measured_48px_lines(self) -> None:
        entry = builder.load_entry()

        def metric(char: str) -> int:
            return 24 if char in " ,." else 48

        widths = builder.visual_line_widths(entry["ko"], metric)
        self.assertEqual(widths, [816, 888, 768])
        self.assertEqual(len(widths), 3)
        self.assertTrue(all(width <= entry["layout"]["max_line_px"] for width in widths))

    def test_contract_accepts_only_the_two_known_msgev_preimages(self) -> None:
        contract = builder.load_contract()
        profiles = {profile["name"]: profile for profile in contract["source_profiles"]}
        self.assertEqual(set(profiles), {"current_game_rebased", "release_v0_10_0"})
        self.assertEqual(profiles["current_game_rebased"]["string_count"], 17910)
        self.assertEqual(profiles["release_v0_10_0"]["string_count"], 17916)
        self.assertEqual(
            profiles["release_v0_10_0"]["packed"]["sha256"],
            "2CA183DA690D45A75702EA0F35C70966786B59E9440B8B8F49BE9652342F81AC",
        )

    def test_output_must_remain_in_tmp(self) -> None:
        allowed = builder.output_root(builder.REPO / "tmp" / "unit_msgev_10564")
        self.assertTrue(allowed.is_relative_to((builder.REPO / "tmp").resolve()))
        with self.assertRaises(builder.LayoutError):
            builder.output_root(builder.REPO / "workstreams" / "unsafe_output")

    def test_public_json_is_not_reformatted_by_loader(self) -> None:
        raw = json.loads(builder.OVERLAY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(raw["entries"][0]["target_utf16le_sha256"], builder.text_hash(builder.load_entry()["ko"]))


if __name__ == "__main__":
    unittest.main()
