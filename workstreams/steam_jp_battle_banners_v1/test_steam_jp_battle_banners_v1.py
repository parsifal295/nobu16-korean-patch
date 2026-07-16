from __future__ import annotations

import importlib
import json
import sys
import unittest
from pathlib import Path
from unittest import mock


WORKSTREAM = Path(__file__).resolve().parent
if str(WORKSTREAM) not in sys.path:
    sys.path.insert(0, str(WORKSTREAM))
MODULE = importlib.import_module("build_steam_jp_battle_banners_v1")


class BattleBannerTests(unittest.TestCase):
    def test_exact_nine_texture_scope_and_labels(self) -> None:
        self.assertEqual(MODULE.TARGET_TEXTURES, tuple(range(48, 57)))
        self.assertEqual([texture for texture, _ in MODULE.BANNERS], list(MODULE.TARGET_TEXTURES))
        self.assertEqual(len({label for _, label in MODULE.BANNERS}), 9)

    def test_banner_link_identity_rebuild(self) -> None:
        wrapper = b"battle-banner-wrapper"
        blob = bytearray(b"LINK")
        blob.extend((1).to_bytes(4, "little"))
        blob.extend((32).to_bytes(4, "little"))
        blob.extend((MODULE.NESTED_RESOURCE_ID).to_bytes(4, "little"))
        blob.extend((64).to_bytes(4, "little"))
        blob.extend(b"\0" * 12)
        blob.extend((64).to_bytes(4, "little"))
        blob.extend((len(wrapper)).to_bytes(4, "little"))
        blob.extend(b"\0" * 24)
        blob.extend(wrapper)
        link = MODULE.parse_banner_link(bytes(blob))
        self.assertEqual(MODULE.rebuild_banner_link(link, wrapper), bytes(blob))

    def test_measured_three_to_two_coordinate_mapping(self) -> None:
        # This is a half-open source rectangle taken from the first visual
        # diff after a four-pixel guard band; it lands around the PC title.
        source = (403, 0, 878, 110)
        self.assertEqual(MODULE.source_to_pc_rect(source), (604, 0, 1317, 165))

    def test_selected_payload_guard_does_not_allow_header_changes(self) -> None:
        first = MODULE.G1TTexture(48, 10, 30, 14, 30, 2048, 256, 0x5B, 1, 0x10, 12)
        second = MODULE.G1TTexture(49, 30, 50, 34, 50, 2048, 256, 0x5B, 1, 0x10, 12)
        g1t = MODULE.G1T(raw=b"", platform=10, textures=tuple([MODULE.G1TTexture(i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for i in range(48)] + [first, second] + [MODULE.G1TTexture(i, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0) for i in range(50, 57)]))
        before = bytes(range(60))
        identical = bytes(before)
        changed_header = bytearray(before)
        changed_header[5] ^= 1
        self.assertTrue(MODULE.unchanged_outside_selected(before, identical, g1t))
        self.assertFalse(MODULE.unchanged_outside_selected(before, bytes(changed_header), g1t))

    def test_outside_path_is_rejected_before_creating_any_directory(self) -> None:
        probe = MODULE.REPO / "__battle_banners_outside_path_probe__" / "child"
        self.assertFalse(probe.parent.exists())
        with self.assertRaises(MODULE.BannerCandidateError):
            MODULE.ensure_tmp(probe, mkdir=True)
        self.assertFalse(probe.parent.exists())

    def test_tmp_root_reparse_is_rejected_before_resolve(self) -> None:
        target = MODULE.TMP_ROOT / "battle_banners_reparse_probe"
        with (
            mock.patch.object(MODULE, "is_reparse", return_value=True),
            mock.patch.object(Path, "resolve", side_effect=AssertionError("resolve must not run")),
        ):
            with self.assertRaises(MODULE.BannerCandidateError):
                MODULE.ensure_tmp(target)

    def test_public_validation_is_source_free_and_scope_limited(self) -> None:
        validation = json.loads((WORKSTREAM / "validation.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(validation["scope"]["outer_entry"], 13)
        self.assertEqual(validation["scope"]["textures"], list(range(48, 57)))
        self.assertFalse(validation["scope"]["game_install_modified"])
        self.assertFalse(validation["scope"]["raw_switch_payload_copy"])
        rendered = json.dumps(validation, ensure_ascii=False)
        self.assertNotIn(".png", rendered)
        self.assertNotIn("payload_hex", rendered)
        self.assertNotIn("GT1G0600", rendered)


if __name__ == "__main__":
    unittest.main()
