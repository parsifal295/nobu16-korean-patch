from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
GAME_ROOT = REPO_ROOT.parent
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(REPO_ROOT / "tools"))

import build_common_message_overlay as common  # noqa: E402
import build_small_message_tables as small  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


FORBIDDEN_SOURCE_SCRIPT_RE = re.compile(
    r"[\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\u3040-\u30FF]"
)


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SmallMessageTableTests(unittest.TestCase):
    def test_public_overlays_are_complete_and_source_free(self) -> None:
        allowlist_before = common.ALLOWED_RESOURCES
        summaries = small.validate_public_overlays()
        self.assertEqual(common.ALLOWED_RESOURCES, allowlist_before)
        self.assertEqual(
            [(item["resource"], item["translated_count"]) for item in summaries],
            [
                ("MSG_PK/SC/msgire.bin", 122),
                ("MSG_PK/SC/msgstf.bin", 8),
            ],
        )
        self.assertEqual(
            sum(item["translated_count"] for item in summaries),
            130,
        )
        self.assertEqual(
            sum(item["translation_target_count"] for item in summaries),
            130,
        )

        for overlay_path in small.OVERLAY_PATHS:
            overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
            self.assertEqual(set(overlay), small.ALLOWED_ROOT_KEYS)
            self.assertFalse(
                overlay["distribution_policy"]["contains_commercial_source_text"]
            )
            self.assertFalse(
                overlay["distribution_policy"]["contains_complete_game_resource"]
            )
            for entry in overlay["entries"]:
                self.assertLessEqual(set(entry), small.ALLOWED_ENTRY_KEYS)
                self.assertIsNone(FORBIDDEN_SOURCE_SCRIPT_RE.search(entry["ko"]))
                self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")

    def test_structural_slots_do_not_change_the_denominator(self) -> None:
        summaries = {
            item["resource"]: item for item in small.validate_public_overlays()
        }
        ire = summaries["MSG_PK/SC/msgire.bin"]
        self.assertEqual(ire["total_string_slots"], 122)
        self.assertEqual(ire["translation_target_count"], 122)
        self.assertEqual(ire["structural_empty_ids"], [])

        stf = summaries["MSG_PK/SC/msgstf.bin"]
        self.assertEqual(stf["total_string_slots"], 20)
        self.assertEqual(stf["translation_target_count"], 8)
        self.assertEqual(stf["translated_count"], 8)
        self.assertEqual(stf["structural_empty_ids"], list(range(8, 20)))

    def test_committed_validation_matches_public_overlays(self) -> None:
        validation_path = WORKSTREAM_ROOT / "validation.json"
        report = json.loads(validation_path.read_text(encoding="utf-8"))
        self.assertEqual(
            report["schema"], "nobu16.kr.small-message-validation.v1"
        )
        self.assertTrue(report["file_only"])
        self.assertFalse(report["installed_game_files_modified"])
        self.assertFalse(report["process_memory_access"])
        self.assertFalse(report["registry_modified"])
        self.assertFalse(report["executable_modified"])
        self.assertTrue(report["source_text_free_public_overlays"])
        self.assertEqual(report["han_kana_source_leak_count"], 0)
        self.assertTrue(report["shared_common_message_builder_reused"])
        self.assertTrue(report["ab_build_byte_identical"])
        self.assertEqual(report["translated_count"], 130)
        self.assertEqual(report["translation_target_count"], 130)

        resources = {item["resource"]: item for item in report["resources"]}
        for overlay_path in small.OVERLAY_PATHS:
            overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
            resource = overlay["resource"]
            self.assertEqual(
                resources[resource]["overlay_sha256"], sha256_file(overlay_path)
            )
        for resource in small.SUPPORTED_RESOURCES:
            check = report["source_checks"][resource]
            self.assertEqual(set(check["reference_languages"]), {"SC", "EN", "JP"})
            for language_check in check["reference_languages"].values():
                self.assertEqual(
                    language_check["total_string_slots"],
                    small.EXPECTED[resource]["string_count"],
                )
                self.assertEqual(
                    language_check["display_nonempty_count"],
                    small.EXPECTED[resource]["translation_target_count"],
                )

    @unittest.skipUnless(
        all(
            (GAME_ROOT / f"MSG_PK/{language}/{resource_name}").is_file()
            for language in ("SC", "EN", "JP")
            for resource_name in ("msgire.bin", "msgstf.bin")
        ),
        "pinned retail SC/EN/JP resources are not available",
    )
    def test_live_stock_alignment_and_ab_build_determinism(self) -> None:
        stock_paths = [
            GAME_ROOT / f"MSG_PK/{language}/{resource_name}"
            for language in ("SC", "EN", "JP")
            for resource_name in ("msgire.bin", "msgstf.bin")
        ]
        stock_before = {str(path): sha256_file(path) for path in stock_paths}

        for resource_name, expected_count in (("msgire.bin", 122), ("msgstf.bin", 20)):
            aligned_ids = []
            for language in ("SC", "EN", "JP"):
                packed = (GAME_ROOT / f"MSG_PK/{language}/{resource_name}").read_bytes()
                _, raw = decompress_wrapper(packed)
                table = parse_message_table(raw)
                self.assertEqual(table.string_count, expected_count)
                aligned_ids.append(
                    [entry_id for entry_id, text in enumerate(table.texts) if text]
                )
            self.assertEqual(aligned_ids[0], aligned_ids[1])
            self.assertEqual(aligned_ids[1], aligned_ids[2])

        with tempfile.TemporaryDirectory(prefix="nobu16-small-test-a-") as first:
            with tempfile.TemporaryDirectory(prefix="nobu16-small-test-b-") as second:
                first_root = Path(first)
                second_root = Path(second)
                small.build_all(GAME_ROOT, first_root)
                small.build_all(GAME_ROOT, second_root)
                first_files = small._relative_file_map(first_root)
                second_files = small._relative_file_map(second_root)
                self.assertEqual(first_files, second_files)

                for overlay_path in small.OVERLAY_PATHS:
                    overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
                    target_path = first_root / Path(overlay["resource"])
                    _, raw = decompress_wrapper(target_path.read_bytes())
                    table = parse_message_table(raw)
                    for entry in overlay["entries"]:
                        self.assertEqual(table.texts[entry["id"]], entry["ko"])

        stock_after = {str(path): sha256_file(path) for path in stock_paths}
        self.assertEqual(stock_before, stock_after)


if __name__ == "__main__":
    unittest.main()
