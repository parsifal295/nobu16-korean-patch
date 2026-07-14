from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
TOOLS_DIR = TEST_PATH.parents[3] / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_msgdata_faction_labels_batch1 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "A277CC298262A46683CDB81273487BB5EF4AAD25FE361C1977251B52A1BF7244"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "71FAF284FE09C3B55D898093629E9135FBEEC1FED92AA62EE207EE2DAB68F79E"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "81B52D24386BD24CD1782E77C9929882308D72946C5004BC37507D0BC4532384"
    ),
    batch.VALIDATION_NAME: (
        "DF367C02D02BAD8D08186CB1115391E1EA4172A73767DE6BA4582E5A0AF93F6B"
    ),
}
BOUNDARY_IDS = [3031, 3032, 3212, 3213, 3214, 3215, 3221, 3222]
TARGET_WRAPPER_SHA256 = (
    "8884EE8CE45475DC5ED4574B2A56956CE0882D3A266A6AE4B23B82509C54460C"
)
TARGET_RAW_SHA256 = (
    "92EA8395637C2028BBA11CF605801FC32B2D1E9702F5BB48197401F43FBDB5C8"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgdataFactionLabelsBatch1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay, _ = common.load_json_strict(
            WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME
        )
        cls.evidence = json.loads(
            (WORKSTREAM_DIR / "evidence" / batch.EVIDENCE_NAME).read_text(
                encoding="utf-8"
            ),
            object_pairs_hook=common.strict_object,
        )
        cls.review = json.loads(
            (WORKSTREAM_DIR / "review" / batch.REVIEW_NAME).read_text(
                encoding="utf-8"
            ),
            object_pairs_hook=common.strict_object,
        )
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"),
            object_pairs_hook=common.strict_object,
        )

    def test_scope_is_exactly_190_unique_nonoverlapping_entries(self) -> None:
        selected = batch.selected_ids()
        self.assertEqual(190, len(selected))
        self.assertEqual(list(range(3032, 3222)), selected)
        self.assertEqual([], list(batch.EXCLUDED_INTERNAL_IDS))
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))
        self.assertEqual(1, len(batch.GROUPS))
        self.assertEqual(190, int(batch.GROUPS[0]["selected_count"]))
        existing = batch.existing_overlay_snapshot()
        self.assertEqual([], existing["selected_overlap_ids"])

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgdata.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(190, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_sc_format_invariants_are_exact(self) -> None:
        stock_sc = (
            batch.PATCH_ROOT
            / "backups"
            / "officer_name_probe_v0_1"
            / "msgdata.SC.stock.bin"
        )
        table = batch.load_stock(stock_sc, "SC")["table"]
        for entry_id, replacement in batch.TRANSLATIONS.items():
            with self.subTest(entry_id=entry_id):
                self.assertEqual(
                    [],
                    common.invariant_mismatches(table.texts[entry_id], replacement),
                )

    def test_alignment_evidence_is_three_language_and_source_free(self) -> None:
        self.assertEqual(190, self.evidence["entry_count"])
        self.assertEqual(190, len(self.evidence["entries"]))
        self.assertEqual(1, len(self.evidence["groups"]))
        self.assertEqual(
            BOUNDARY_IDS,
            [int(anchor["id"]) for anchor in self.evidence["boundary_anchors"]],
        )
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "EN"}, set(entry["references"]))
                self.assertIs(True, entry["manual_semantic_crosscheck"])
        self.assertFalse(self.evidence["contains_commercial_source_text"])

    def test_public_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"cjk_unified_count": 0, "kana_count": 0},
                    batch.public_script_counts(path.read_text(encoding="utf-8")),
                )

    def test_all_three_sources_roundtrip_and_sc_target_is_deterministic(self) -> None:
        paths = {
            "SC": batch.PATCH_ROOT
            / "backups"
            / "officer_name_probe_v0_1"
            / "msgdata.SC.stock.bin",
            "JP": batch.WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
            "EN": batch.WORKSPACE_ROOT / "MSG_PK" / "EN" / "msgdata.bin",
        }
        sources = {
            language: batch.load_stock(path, language)
            for language, path in paths.items()
        }
        self.assertEqual({"SC", "JP", "EN"}, set(sources))
        first = batch.reconstruct_sc_target(sources["SC"])
        second = batch.reconstruct_sc_target(sources["SC"])
        self.assertEqual(first["wrapper"], second["wrapper"])
        self.assertEqual(first["raw"], second["raw"])
        self.assertEqual(190, first["changed_count"])
        self.assertEqual(TARGET_WRAPPER_SHA256, digest_bytes(first["wrapper"]))
        self.assertEqual(TARGET_RAW_SHA256, digest_bytes(first["raw"]))

    def test_validation_records_exclusion_reconstruction_and_safety(self) -> None:
        self.assertIs(True, self.validation["passed"])
        self.assertEqual(570, self.validation["source_alignment"]["selected_reference_hash_count"])
        self.assertEqual(190, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            batch.existing_overlay_snapshot(),
            self.validation["existing_overlay_exclusion"],
        )
        reconstruction = self.validation["reconstruction"]
        self.assertTrue(reconstruction["sc_overlay_rebuild_a_b_byte_identical"])
        self.assertEqual(190, reconstruction["changed_entry_count"])
        self.assertEqual(TARGET_WRAPPER_SHA256, reconstruction["target"]["wrapper_sha256"])
        self.assertEqual(TARGET_RAW_SHA256, reconstruction["target"]["raw_sha256"])
        self.assertFalse(reconstruction["target"]["complete_target_included"])
        self.assertEqual(
            {"SC": True, "JP": True, "EN": True},
            reconstruction["source_parse_rebuild_byte_identical"],
        )
        self.assertEqual(
            self.validation["installed_msgdata_before"],
            self.validation["installed_msgdata_after"],
        )
        self.assertEqual(
            batch.installed_resource_snapshot(),
            self.validation["installed_msgdata_after"],
        )
        for value in self.validation["safety"].values():
            self.assertFalse(value)


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


if __name__ == "__main__":
    unittest.main()
