from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
TOOLS_DIR = TEST_PATH.parents[3] / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch15 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "81568BBD13BF61F4CAE83E9F893ECA7DA723ADB76200F25D1D38011FFE3A831A"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "4BA6A777EE108B84E8FE9723A97AF75CD6A8FDDEE9BC9B9908A24D0BAFB5DA6B"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "957C55863EEEBB23E0D36FCBACB2BB630E195F2A2A3039D852D97BFF4B0B1C71"
    ),
    batch.VALIDATION_NAME: (
        "C2298D40384B680FF482DCD63B7E13BFC9FD1236FD83B434A1DBA3DAE09A0BF4"
    ),
}
PREVIOUS_MANIFEST_SHA256 = (
    "CEC31430C4920744C39B9B62F5CCDBD173A89D0EA2A35950D5C5C3FA38578F2C"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class EventDialogueBatch15Tests(unittest.TestCase):
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
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"),
            object_pairs_hook=common.strict_object,
        )

    def test_scope_is_exactly_138_displayed_entries(self) -> None:
        selected = batch.selected_ids()
        self.assertEqual(138, len(selected))
        self.assertEqual(list(range(4839, 4977)), selected)
        self.assertEqual([], list(batch.EXCLUDED_INTERNAL_IDS))
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))
        self.assertEqual(6, len(batch.EVENTS))
        self.assertEqual(
            138, sum(int(event["selected_count"]) for event in batch.EVENTS)
        )
        self.assertEqual(4839, batch.EVENTS[0]["start_id"])
        self.assertEqual(4976, batch.EVENTS[-1]["end_id"])

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(138, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_alignment_evidence_is_three_language_and_source_free(self) -> None:
        self.assertEqual(138, self.evidence["entry_count"])
        self.assertEqual(138, len(self.evidence["entries"]))
        self.assertEqual([], self.evidence["excluded_internal_entries"])
        self.assertEqual(6, len(self.evidence["event_groups"]))
        self.assertEqual(
            [4838, 4839, 4873, 4874, 4887, 4888, 4910,
             4911, 4914, 4915, 4939, 4940, 4976, 4977],
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

    def test_authored_line_length_is_bounded_without_exceptions(self) -> None:
        max_visible = 0
        for entry_id, value in batch.TRANSLATIONS.items():
            visible = [
                len(common.ESC_RE.sub("", line)) for line in value.splitlines()
            ]
            max_visible = max(max_visible, max(visible))
            with self.subTest(entry_id=entry_id):
                self.assertLessEqual(max(visible), 32)
        self.assertEqual(32, max_visible)
        layout = self.validation["layout_heuristic"]
        self.assertEqual([], layout["entries_over_32"])
        self.assertEqual([], layout["source_fixed_linebreak_exceptions"])
        self.assertEqual(32, layout["max_authored_line_codepoints_excluding_esc"])
        self.assertIs(True, layout["runtime_layout_review_required"])

    def test_validation_records_invariants_reproducibility_and_safety(self) -> None:
        self.assertIs(True, self.validation["passed"])
        self.assertEqual(
            414,
            self.validation["source_alignment"]["selected_reference_hash_count"],
        )
        self.assertEqual(
            138,
            self.validation["replacement_invariants"][
                "custom_bracket_placeholder_checks"
            ],
        )
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            ["isolated_a", "isolated_b", "final"],
            self.validation["reproducibility"]["required_runs"],
        )
        self.assertIs(
            True,
            self.validation["reproducibility"][
                "byte_identical_artifacts_required"
            ],
        )
        safety = self.validation["safety"]
        self.assertFalse(safety["installed_game_files_modified"])
        self.assertFalse(safety["font_files_modified"])
        self.assertFalse(safety["installer_modified"])
        self.assertFalse(safety["root_readme_or_progress_modified"])
        self.assertFalse(safety["common_builder_or_other_workstream_modified"])
        self.assertFalse(
            safety[
                "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_artifacts_modified"
            ]
        )

    def test_previous_dialogue_artifacts_and_installed_msgev_are_unchanged(self) -> None:
        current_previous = batch.previous_artifact_snapshot()
        self.assertEqual(56, current_previous["file_count"])
        self.assertEqual(PREVIOUS_MANIFEST_SHA256, current_previous["manifest_sha256"])
        self.assertIs(True, current_previous["all_hashes_match"])
        current_installed = batch.installed_resource_snapshot()

        integrity = self.validation["preexisting_integrity"]
        self.assertEqual(
            current_previous, integrity["dialogue_v01_v14_artifacts_before"]
        )
        self.assertEqual(
            current_previous, integrity["dialogue_v01_v14_artifacts_after"]
        )
        self.assertEqual(current_installed, integrity["installed_msgev_before"])
        self.assertEqual(current_installed, integrity["installed_msgev_after"])


if __name__ == "__main__":
    unittest.main()
