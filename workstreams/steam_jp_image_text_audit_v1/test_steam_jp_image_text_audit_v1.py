from __future__ import annotations

import importlib.util
import json
import struct
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location(
    "steam_jp_image_text_audit_v1",
    WORKSTREAM / "build_steam_jp_image_text_audit.py",
)
assert SPEC is not None and SPEC.loader is not None
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def synthetic_g1t() -> bytes:
    directory_offset = 32
    texture_offset = 36
    output = bytearray(texture_offset + 8)
    output[:8] = b"GT1G0600"
    struct.pack_into("<4I", output, 8, len(output), directory_offset, 1, 10)
    struct.pack_into("<I", output, directory_offset, texture_offset - directory_offset)
    # one mip, BC3, 256×128, no extra header, no payload needed for this
    # structural parser fixture.
    output[texture_offset : texture_offset + 8] = bytes((0x10, 0x5B, 0x78, 0, 0, 0, 0, 0))
    return bytes(output)


def synthetic_bundle() -> bytes:
    raw = synthetic_g1t()
    compressed = AUDIT.lz4.raw_lz4_compress_literal_only(raw)
    wrapper = b"fixture!" + struct.pack("<QQ", len(raw), len(compressed)) + compressed
    aligned_table_end = 64
    output = bytearray(aligned_table_end)
    output[:4] = b"LINK"
    struct.pack_into("<4I", output, 4, 2, 32, 77, aligned_table_end)
    struct.pack_into("<II", output, 32, aligned_table_end, len(wrapper))
    # The second slot deliberately models a virtual table entry retained past
    # physical EOF, as found in the Switch boot bundle.
    struct.pack_into("<II", output, 40, aligned_table_end + len(wrapper) + 4, 32)
    output.extend(wrapper)
    return bytes(output)


def walk(value: object):
    if isinstance(value, dict):
        for key, nested in value.items():
            yield key, nested
            yield from walk(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from walk(nested)


class SteamJpImageTextAuditTests(unittest.TestCase):
    def test_target_scope_is_exact(self) -> None:
        self.assertEqual(
            [target["id"] for target in AUDIT.TARGETS],
            [
                "base_boot_warning",
                "base_historical_title_cards",
                "pk_mixed_menu_labels",
                "pk_historical_episode_title",
            ],
        )
        self.assertEqual([target["outer_index"] for target in AUDIT.TARGETS], [1, 4, 18, 21])

    def test_nested_bundle_preserves_virtual_slot_metadata(self) -> None:
        count, resource_id, slots = AUDIT.parse_bundle_slots(synthetic_bundle(), "fixture")
        self.assertEqual((count, resource_id), (2, 77))
        self.assertTrue(slots[0]["physical"])
        self.assertFalse(slots[1]["physical"])
        self.assertEqual(slots[1]["virtual_reason"], "range_outside_physical_bundle")

    def test_g1t_metadata_has_no_payload_bytes(self) -> None:
        count, _, slots = AUDIT.parse_bundle_slots(synthetic_bundle(), "fixture")
        self.assertEqual(count, 2)
        inspected = AUDIT.inspect_nested_slot(slots[0], "fixture/0")
        texture = inspected["g1t"]["textures"][0]
        self.assertEqual(texture["dimensions"], [256, 128])
        self.assertEqual(texture["format_name"], "BC3/DXT5")
        self.assertIn("payload_sha256", texture)
        self.assertNotIn("payload", texture)
        self.assertNotIn("data", inspected)
        self.assertNotIn("raw", inspected)

    def test_committed_audit_validates_and_has_expected_inventory_counts(self) -> None:
        audit = json.loads((WORKSTREAM / "audit.v1.json").read_text(encoding="utf-8"))
        AUDIT.validate_audit(audit)
        targets = {target["id"]: target for target in audit["targets"]}
        self.assertEqual(targets["base_boot_warning"]["pc_jp"]["summary"]["table_slot_count"], 6)
        self.assertEqual(targets["base_historical_title_cards"]["pc_jp"]["summary"]["table_slot_count"], 105)
        self.assertEqual(targets["pk_mixed_menu_labels"]["pc_jp"]["summary"]["table_slot_count"], 43)
        self.assertEqual(targets["pk_historical_episode_title"]["pc_jp"]["summary"]["table_slot_count"], 33)
        self.assertEqual(
            audit["switch_reference_inputs"]["res_jp_pk_member_present"],
            {"v1.3": False, "v2.0": False},
        )
        for archive in audit["pc_inputs"].values():
            self.assertTrue(archive["read_only_identity_preserved"])
            self.assertEqual(archive["sha256_before_read"], archive["sha256_after_read"])

    def test_committed_audit_is_metadata_only(self) -> None:
        audit = json.loads((WORKSTREAM / "audit.v1.json").read_text(encoding="utf-8"))
        self.assertTrue(audit["source_free_guarantees"]["metadata_only"])
        for key, value in walk(audit):
            self.assertNotEqual(key, "data")
            self.assertNotEqual(key, "raw")
            self.assertFalse(isinstance(value, (bytes, bytearray, memoryview)))
        allowed_suffixes = {".json", ".md", ".py"}
        self.assertEqual(
            {path.suffix for path in WORKSTREAM.iterdir() if path.is_file()},
            allowed_suffixes,
        )


if __name__ == "__main__":
    unittest.main()
