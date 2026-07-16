#!/usr/bin/env python3
"""Unit tests for the source-free Steam JP wheel-button audit."""

from __future__ import annotations

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("wheel_audit", ROOT / "build_steam_jp_wheel_button_audit_v1.py")
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


class WheelButtonAuditTests(unittest.TestCase):
    def test_parse_outer_accepts_two_entries(self) -> None:
        blob = bytearray(48)
        blob[:4] = b"LINK"
        struct.pack_into("<III", blob, 4, 2, 1, 0)
        struct.pack_into("<II", blob, 16, 32, 4)
        struct.pack_into("<II", blob, 24, 40, 8)
        blob[32:40] = b"abcd" + b"\0" * 4
        blob[40:48] = b"12345678"
        outer = AUDIT.parse_outer(bytes(blob))
        self.assertEqual(outer.entry_count, 2)
        self.assertEqual(outer.entries[0].data, b"abcd")
        self.assertEqual(outer.entries[1].data, b"12345678")

    def test_parse_outer_rejects_overlap(self) -> None:
        blob = bytearray(48)
        blob[:4] = b"LINK"
        struct.pack_into("<III", blob, 4, 2, 1, 0)
        struct.pack_into("<II", blob, 16, 32, 12)
        struct.pack_into("<II", blob, 24, 40, 8)
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.parse_outer(bytes(blob))

    def test_compare_versions_requires_wheel_change(self) -> None:
        def target(payload: str) -> dict[str, object]:
            return {
                "nested_link": {"resource_id": 474, "table_slot_count": 1},
                "slot": {"g1t": {"textures": [{"dimensions": [1, 1], "format_code": "0x5B", "mip_count": 1, "extra_version": 16, "extra_length": 12, "payload_size": 16, "payload_sha256": payload}]}},
            }

        def outer(marker: bytes) -> object:
            entries = tuple(AUDIT.OuterEntry(index, 0, 1, 1, marker) for index in range(9))
            return AUDIT.OuterTable(9, 1, 0, 9, entries)

        left = outer(b"A")
        right_entries = list(left.entries)
        right_entries[8] = AUDIT.OuterEntry(8, 0, 1, 1, b"B")
        right = AUDIT.OuterTable(9, 1, 0, 9, tuple(right_entries))
        result = AUDIT.compare_versions(left, target("A"), right, target("B"), left_label="a", right_label="b")
        self.assertEqual(result["changed_outer_indices"], [8])
        self.assertTrue(result["wheel_primary_texture_changed"])

    def test_pc_gate_rejects_raw_copy_even_when_format_matches(self) -> None:
        def target(platform: int, dims: list[int]) -> dict[str, object]:
            return {
                "nested_link": {"resource_id": 474, "table_slot_count": 1},
                "slot": {"g1t": {"platform": platform, "textures": [{"format_code": "0x5B", "dimensions": dims, "payload_size": 16}]}},
            }

        result = AUDIT.compare_switch_to_pc(target(16, [2048, 1024]), target(10, [2048, 2048]))
        self.assertFalse(result["raw_or_wrapper_copy_allowed"])
        self.assertTrue(result["pc_only_rebuild_required"])
        self.assertFalse(result["primary_texture"]["dimensions"]["equal"])

    def test_preview_output_must_stay_under_tmp(self) -> None:
        with self.assertRaises(AUDIT.AuditError):
            AUDIT.ensure_private_output_root(Path.cwd())

    def test_public_audit_document_passes_its_own_gate(self) -> None:
        document = json.loads((ROOT / "audit.v1.json").read_text(encoding="utf-8"))
        AUDIT.validate_audit_document(document)


if __name__ == "__main__":
    unittest.main()
