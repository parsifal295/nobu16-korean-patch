from __future__ import annotations

import hashlib
import json
import re
import unittest
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "public/msggame_ko_msggame_pk_parallel_b10_block17_c_623.v1.json"
VALIDATION = ROOT / "validation.v1.json"
EXPECTED_COUNT = 623
EXPECTED_COORDINATES_SHA256 = (
    "1065BE788BFB31BA6DAE65B2C25C68ACB4ACC0129166FC62A609C029BA466941"
)
EXPECTED_OVERLAY_SHA256 = (
    "BCFBDB9478C0B50677133F6184BD058D271DB7658F6843D94BB953D5F1CAD7C7"
)
CJK_RE = re.compile(r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF]")
KANA_RE = re.compile(r"[\u3040-\u30FF\u31F0-\u31FF]")


def _read(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"JSON root is not an object: {path}")
    return value


def _sha256(blob: bytes) -> str:
    return hashlib.sha256(blob).hexdigest().upper()


def _canonical_hash(value: Any) -> str:
    blob = json.dumps(
        value,
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    return _sha256(blob)


class MsggamePkParallelB10Tests(unittest.TestCase):
    def test_overlay_has_exact_frozen_coordinate_set(self) -> None:
        payload = _read(OVERLAY)
        self.assertEqual(payload["resource"], "MSG_PK/SC/msggame.bin")
        self.assertEqual(payload["entry_count"], EXPECTED_COUNT)
        entries = payload["entries"]
        self.assertEqual(len(entries), EXPECTED_COUNT)
        coordinates = [
            [entry["block_id"], entry["record_id"], entry["literal_id"]]
            for entry in entries
        ]
        self.assertEqual(len({tuple(item) for item in coordinates}), EXPECTED_COUNT)
        self.assertEqual(coordinates, sorted(coordinates))
        self.assertEqual(_canonical_hash(coordinates), EXPECTED_COORDINATES_SHA256)

    def test_overlay_is_source_free_and_has_no_source_script(self) -> None:
        payload = _read(OVERLAY)
        self.assertEqual(
            payload["distribution_policy"],
            {
                "contains_commercial_source_text": False,
                "contains_complete_game_resource": False,
            },
        )
        allowed = {
            "block_id",
            "record_id",
            "literal_id",
            "source_sc_utf16le_sha256",
            "ko",
        }
        for entry in payload["entries"]:
            self.assertEqual(set(entry), allowed)
            self.assertIsInstance(entry["ko"], str)
            self.assertTrue(entry["ko"])
            self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")
        source = OVERLAY.read_text(encoding="utf-8")
        self.assertIsNone(CJK_RE.search(source))
        self.assertIsNone(KANA_RE.search(source))

    def test_validation_passed_and_pins_overlay(self) -> None:
        payload = _read(VALIDATION)
        self.assertIs(payload["passed"], True)
        self.assertEqual(payload["coordinate_count"], EXPECTED_COUNT)
        self.assertEqual(payload["coordinates_sha256"], EXPECTED_COORDINATES_SHA256)
        self.assertEqual(payload["unique_source_hash_count"], 406)
        self.assertEqual(payload["semantic_coordinate_count"], 605)
        self.assertEqual(payload["reviewed_coordinate_count"], 17)
        self.assertIs(payload["duplicate_source_translation_consistent"], True)
        self.assertEqual(payload["invariant_mismatch_count"], 0)
        self.assertEqual(payload["source_script_leak_count"], 0)
        self.assertIs(payload["private_context"]["committed"], False)
        self.assertEqual(payload["overlay"]["sha256"], EXPECTED_OVERLAY_SHA256)
        self.assertEqual(_sha256(OVERLAY.read_bytes()), EXPECTED_OVERLAY_SHA256)

    def test_translation_parts_have_no_cjk_or_kana(self) -> None:
        parts = sorted(ROOT.glob("translations_part*.py"))
        self.assertEqual(len(parts), 5)
        for path in parts:
            source = path.read_text(encoding="utf-8")
            self.assertIsNone(CJK_RE.search(source), path.name)
            self.assertIsNone(KANA_RE.search(source), path.name)


if __name__ == "__main__":
    unittest.main()
