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
MODULE = importlib.import_module("build_steam_jp_wheel_toprows_v1")


class WheelTopRowsTests(unittest.TestCase):
    def test_mapping_has_exactly_five_labels_and_thirty_states(self) -> None:
        MODULE.require_mapping_contract()
        self.assertEqual(len(MODULE.SPRITES), 30)
        labels: dict[str, int] = {}
        for item in MODULE.SPRITES:
            labels[item["label"]] = labels.get(item["label"], 0) + 1
        self.assertEqual(labels, {"평정": 6, "임명": 6, "군사": 6, "내정": 6, "외교": 6})

    def test_free_pack_holes_are_explicit_not_a_row_offset(self) -> None:
        by_label_state = {(item["label"], item["state"]): item for item in MODULE.SPRITES}
        self.assertEqual(by_label_state[("군사", 4)]["source"], (0, 17))
        self.assertEqual(by_label_state[("군사", 4)]["target"], (1, 2))
        self.assertEqual(by_label_state[("내정", 6)]["source"], (1, 2))
        self.assertEqual(by_label_state[("내정", 6)]["target"], (1, 10))
        self.assertEqual(by_label_state[("외교", 1)]["source"], (1, 3))
        self.assertEqual(by_label_state[("외교", 1)]["target"], (1, 11))

    def test_wheel_link_identity_rebuild(self) -> None:
        wrapper = b"wheel-wrapper"
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
        link = MODULE.parse_wheel_link(bytes(blob))
        self.assertEqual(MODULE.rebuild_wheel_link(link, wrapper), bytes(blob))

    def test_changed_bbox_rejects_empty_and_finds_delta(self) -> None:
        before = b"\0" * (4 * 4 * 4)
        after = bytearray(before)
        after[(2 * 4 + 1) * 4 : (2 * 4 + 1) * 4 + 4] = b"\xFF\0\0\xFF"
        self.assertEqual(MODULE.changed_bbox(before, bytes(after), 4, 4), (1, 2, 1, 2))
        with self.assertRaises(MODULE.WheelCandidateError):
            MODULE.changed_bbox(before, before, 4, 4)

    def test_outside_path_is_rejected_before_creating_any_directory(self) -> None:
        probe = MODULE.REPO / "__wheel_toprows_outside_path_probe__" / "child"
        self.assertFalse(probe.parent.exists())
        with self.assertRaises(MODULE.WheelCandidateError):
            MODULE.ensure_tmp(probe, mkdir=True)
        self.assertFalse(probe.parent.exists())

    def test_tmp_root_reparse_is_rejected_before_resolve(self) -> None:
        """A tmp junction must not be followed merely to perform its guard."""

        target = MODULE.TMP_ROOT / "wheel_toprows_reparse_probe"
        with (
            mock.patch.object(MODULE, "is_reparse", return_value=True),
            mock.patch.object(Path, "resolve", side_effect=AssertionError("resolve must not run")),
        ):
            with self.assertRaises(MODULE.WheelCandidateError):
                MODULE.ensure_tmp(target)

    def test_validation_is_source_free_and_matches_contract(self) -> None:
        validation = json.loads((WORKSTREAM / "validation.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(validation["scope"]["outer_entry"], 8)
        self.assertFalse(validation["scope"]["game_install_modified"])
        self.assertFalse(validation["scope"]["raw_switch_payload_copy"])
        self.assertEqual(validation["labels"], {"평정": 6, "임명": 6, "군사": 6, "내정": 6, "외교": 6})
        rendered = json.dumps(validation, ensure_ascii=False)
        self.assertNotIn("RES_SC", rendered)
        self.assertNotIn(".bin/", rendered)


if __name__ == "__main__":
    unittest.main()
