from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
WORKSPACE_ROOT = WORKSTREAM_DIR.parents[2]
TOOLS_DIR = WORKSPACE_ROOT / "KR_PATCH_WORK" / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_msgdata_name_components_batch2 as batch  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402
from nobu16_msg_table import parse_message_table  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "9B887DE854B6ADE847036F1D757925AFFA9BD84FD041ADAB0CE23DA0D3DAC09A",
    f"evidence/{batch.EVIDENCE_NAME}": "0C67CBDB78C1095E4C2367D44A37E1BEC2792E72F296D5F35F158ECC165B28CB",
    f"review/{batch.REVIEW_NAME}": "690BE9C971B0ECD1ACFEF361DDD821960E9046B0C3FF7E82BAE48E9D18109937",
    batch.VALIDATION_NAME: "69491C0518FA653DEDBD06DCA1D468EE748E0747705E1B5B4CA99A0AD9DD9155",
}
TARGET_PACKED_SHA256 = "64B0A687EBFF7EF3C74051376C9E7F5EB424F2EF0F6485502DD80F136ED6620F"
STOCK_AVAILABLE = all(
    (WORKSPACE_ROOT / pin["logical_path"]).is_file()
    for pin in batch.RESOURCE_PINS.values()
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_DIR / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class MsgdataNameComponentsBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay, _ = common.load_json_strict(WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME)
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_scope_is_next_conflict_free_contiguous_range(self) -> None:
        ids = batch.selected_ids()
        self.assertEqual(list(range(3222, 3316)), ids)
        self.assertEqual(94, len(ids))
        self.assertEqual(94, self.overlay["entry_count"])
        self.assertEqual(3316, self.validation["scope"]["next_contiguous_id"])
        self.assertTrue(self.validation["scope"]["next_contiguous_id_blocked_by_existing_overlay"])
        self.assertEqual(
            "personal_name_components",
            batch.group_for(3222),
        )
        self.assertEqual(
            "regional_groups_and_religious_labels",
            batch.group_for(3244),
        )

    def test_all_named_existing_overlays_are_pinned_and_nonoverlapping(self) -> None:
        snapshot, _records = batch.existing_overlay_snapshot(WORKSPACE_ROOT)
        self.assertEqual([], snapshot["selected_overlap_ids"])
        self.assertEqual(4, len(snapshot["overlays"]))
        self.assertEqual(4485, snapshot["total_authored_entry_count"])
        self.assertEqual(4413, snapshot["effective_unique_coordinate_count"])
        self.assertEqual(72, snapshot["cross_overlay_duplicate_coordinate_count"])
        self.assertTrue(snapshot["next_contiguous_id_conflicts_with_existing_overlay"])
        self.assertEqual(snapshot, self.validation["existing_overlay_coordinate_exclusion"])

    def test_overlay_is_exact_and_source_free(self) -> None:
        batch.validate_overlay_shape(self.overlay)
        resource, _stock, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.selected_ids(), [int(entry["id"]) for entry in entries])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/EN/TC PK msgdata resources are unavailable")
    def test_all_four_sources_parse_rebuild_byte_exactly(self) -> None:
        before = batch.source_snapshot(WORKSPACE_ROOT)
        loaded = {
            language: batch.load_resource(WORKSPACE_ROOT, language)
            for language in batch.LANGUAGES
        }
        for entry_id in batch.selected_ids():
            with self.subTest(entry_id=entry_id):
                self.assertTrue(all(loaded[language]["table"].texts[entry_id].strip() for language in batch.LANGUAGES))
        self.assertEqual(before, batch.source_snapshot(WORKSPACE_ROOT))

    def test_four_language_alignment_and_translation_memory_policy(self) -> None:
        self.assertEqual(94, self.evidence["entry_count"])
        self.assertEqual(["SC", "JP", "EN", "TC"], self.validation["source_alignment"]["languages"])
        self.assertEqual(376, self.validation["source_alignment"]["selected_reference_hash_count"])
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "EN", "TC"}, set(entry["references"]))
                self.assertTrue(entry["manual_semantic_crosscheck"])
        memory = self.validation["cross_resource_translation_memory_review"]
        self.assertTrue(memory["policy"]["matching_source_hash_is_translation_memory_only"])
        self.assertFalse(memory["policy"]["automatic_reuse_permitted"])
        self.assertTrue(memory["policy"]["independent_sc_jp_en_tc_coordinate_context_reviewed"])
        self.assertEqual(3, memory["summary"]["matching_source_hash_coordinate_count"])
        self.assertEqual(0, memory["summary"]["automatic_reuse_count"])

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/EN/TC PK msgdata resources are unavailable")
    def test_sc_overlay_rebuild_changes_only_selected_entries(self) -> None:
        source = batch.load_resource(WORKSPACE_ROOT, "SC")
        rebuilt, info = batch.apply_overlay_blob(source["packed"], self.overlay)
        self.assertEqual(TARGET_PACKED_SHA256, hashlib.sha256(rebuilt).hexdigest().upper())
        self.assertEqual(94, info["changed_entry_count"])
        target = parse_message_table(decompress_wrapper(rebuilt)[1])
        selected = set(batch.selected_ids())
        for entry_id, source_text in enumerate(source["table"].texts):
            with self.subTest(entry_id=entry_id):
                self.assertEqual(
                    batch.TRANSLATIONS[entry_id] if entry_id in selected else source_text,
                    target.texts[entry_id],
                )

    def test_review_validation_and_artifacts_are_source_free(self) -> None:
        self.assertEqual(94, self.review["entry_count"])
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["automatic_cross_resource_reuse"] for entry in self.review["entries"]))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(94, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertTrue(self.validation["reconstruction"]["unselected_entries_preserved"])
        self.assertFalse(self.validation["reconstruction"]["target"]["complete_target_included"])
        for value in self.validation["safety"].values():
            self.assertFalse(value)
        for relative, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(relative=relative):
                path = WORKSTREAM_DIR / relative
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"cjk_unified_count": 0, "kana_count": 0, "embedded_nul_count": 0},
                    batch.public_script_counts(path.read_bytes()),
                )

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/EN/TC PK msgdata resources are unavailable")
    def test_reproducible_build_preserves_installed_pk_sources(self) -> None:
        before = batch.source_snapshot(WORKSPACE_ROOT)
        with tempfile.TemporaryDirectory(prefix="nobu16-msgdata-b02-test-") as temporary:
            result = batch.build_reproducibly(WORKSPACE_ROOT, Path(temporary))
        self.assertEqual(94, result["entry_count"])
        self.assertEqual(3316, result["next_contiguous_id"])
        self.assertEqual(TARGET_PACKED_SHA256, result["target_packed_sha256"])
        self.assertEqual(
            EXPECTED_HASHES,
            {
                artifact["path"]: artifact["sha256"]
                for artifact in result["artifacts"].values()
            },
        )
        self.assertEqual(before, batch.source_snapshot(WORKSPACE_ROOT))


if __name__ == "__main__":
    unittest.main()
