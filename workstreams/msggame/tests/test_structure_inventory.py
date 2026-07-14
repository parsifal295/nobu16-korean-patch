from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
sys.path.insert(0, str(WORKSTREAM_ROOT))

from msggame_format import (  # noqa: E402
    is_visible_translation_candidate,
    iter_literals,
    parse_packed_msggame,
    rebuild_packed_with_literals,
    structural_summary,
)


INVENTORY_PATH = WORKSTREAM_ROOT / "public" / "structure_inventory.v0.1.json"
VALIDATION_PATH = WORKSTREAM_ROOT / "validation.v0.1.json"
SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)


class StructureInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inventory_blob = INVENTORY_PATH.read_bytes()
        cls.inventory = json.loads(cls.inventory_blob.decode("utf-8"))
        cls.validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

    def test_public_inventory_is_source_free(self) -> None:
        text = self.inventory_blob.decode("utf-8")
        self.assertIsNone(SOURCE_SCRIPT_RE.search(text))
        self.assertNotIn("\x00", text)
        self.assertFalse(
            self.inventory["distribution_policy"]["contains_commercial_source_text"]
        )

    def test_sc_translation_denominators_are_pinned(self) -> None:
        by_path = {row["relative_path"]: row for row in self.inventory["files"]}
        pk = by_path["MSG_PK/SC/msggame.bin"]
        base = by_path["MSG/SC/msggame.bin"]
        self.assertEqual((pk["record_count"], pk["literal_slot_count"]), (21581, 25598))
        self.assertEqual(pk["visible_translation_candidate_count"], 16482)
        self.assertEqual((base["record_count"], base["literal_slot_count"]), (19152, 21225))
        self.assertEqual(base["visible_translation_candidate_count"], 12268)

    def test_all_pinned_sources_passed_structural_checks(self) -> None:
        self.assertEqual(len(self.inventory["files"]), 7)
        for row in self.inventory["files"]:
            self.assertEqual(row["block_count"], 18)
            self.assertEqual(set(row["checks"].values()), {"OK"})
        self.assertTrue(self.validation["passed"])
        self.assertEqual(self.validation["verified_source_count"], 7)

    @unittest.skipUnless(
        (REPO_ROOT.parent / "MSG_PK" / "SC" / "msggame.bin").exists(),
        "installed game resource is not available",
    )
    def test_installed_pk_sc_still_matches_inventory(self) -> None:
        path = REPO_ROOT.parent / "MSG_PK" / "SC" / "msggame.bin"
        summary = structural_summary(path.read_bytes())
        self.assertEqual(summary["record_count"], 21581)
        self.assertEqual(summary["literal_slot_count"], 25598)
        self.assertEqual(summary["visible_translation_candidate_count"], 16482)
        self.assertTrue(summary["raw_parse_rebuild_byte_exact"])

    @unittest.skipUnless(
        (REPO_ROOT.parent / "MSG_PK" / "SC" / "msggame.bin").exists(),
        "installed game resource is not available",
    )
    def test_real_pk_sc_variable_length_overlay_is_read_only(self) -> None:
        path = REPO_ROOT.parent / "MSG_PK" / "SC" / "msggame.bin"
        packed_before = path.read_bytes()
        parsed = parse_packed_msggame(packed_before)
        replacement = "실파일 구조 검증용 가변 길이 문자열"
        target = next(
            literal
            for literal in iter_literals(parsed.archive)
            if is_visible_translation_candidate(literal.text)
            and len(literal.text.encode("utf-16-le"))
            < len(replacement.encode("utf-16-le"))
        )
        coordinate = (target.block_id, target.record_id, target.literal_id)
        self.assertGreater(
            len(replacement.encode("utf-16-le")),
            len(target.text.encode("utf-16-le")),
        )
        rebuilt = rebuild_packed_with_literals(packed_before, {coordinate: replacement})
        reparsed = parse_packed_msggame(rebuilt)
        by_coordinate = {
            (literal.block_id, literal.record_id, literal.literal_id): literal.text
            for literal in iter_literals(reparsed.archive)
        }
        self.assertEqual(by_coordinate[coordinate], replacement)
        self.assertEqual(reparsed.archive.record_count, parsed.archive.record_count)
        self.assertEqual(path.read_bytes(), packed_before)


if __name__ == "__main__":
    unittest.main()
