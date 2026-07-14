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
import build_event_dialogue_batch22 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "AF82BB146540FBD72A14149BD93F8CA37F0F27C080A80E42502803284BBA3029"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "8BFE5C891A6497529B1440512488719446F7FA08E940A7BD117554D4D1788B32"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "FA44B01EFCE5E565D5BDAB875A20CA8633D58D0B44661EE18D7F17C662FB2B76"
    ),
    batch.VALIDATION_NAME: (
        "F76C2B29E9356EEEFDF99356A6451547DD480F55B4C930EF552F943D87F8645C"
    ),
}
PREVIOUS_MANIFEST_SHA256 = (
    "92CDC4C6BA43B8D28F6FD48B3C20AE86525450C47E8A7318CFE162F9968A5355"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class EventDialogueBatch22Tests(unittest.TestCase):
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

    def test_scope_is_exactly_125_displayed_entries(self) -> None:
        selected = batch.selected_ids()
        self.assertEqual(125, len(selected))
        self.assertEqual(list(range(5749, 5874)), selected)
        self.assertEqual([], list(batch.EXCLUDED_INTERNAL_IDS))
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))
        self.assertEqual(6, len(batch.EVENTS))
        self.assertEqual(
            125, sum(int(event["selected_count"]) for event in batch.EVENTS)
        )
        self.assertEqual(5749, batch.EVENTS[0]["start_id"])
        self.assertEqual(5873, batch.EVENTS[-1]["end_id"])

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(125, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_alignment_evidence_is_three_language_and_source_free(self) -> None:
        self.assertEqual(125, self.evidence["entry_count"])
        self.assertEqual(125, len(self.evidence["entries"]))
        self.assertEqual([], self.evidence["excluded_internal_entries"])
        self.assertEqual(6, len(self.evidence["event_groups"]))
        self.assertEqual(
            [5748, 5749, 5776, 5777, 5802, 5803, 5816,
             5817, 5838, 5839, 5855, 5856, 5873, 5874],
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
            375,
            self.validation["source_alignment"]["selected_reference_hash_count"],
        )
        self.assertEqual(
            125,
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
                "existing_v01_v02_v03_v04_v05_v06_v07_v08_v09_v10_v11_v12_v13_v14_v15_v16_v17_v18_v19_v20_v21_artifacts_modified"
            ]
        )

    def test_previous_dialogue_artifacts_and_installed_msgev_are_unchanged(self) -> None:
        current_previous = batch.previous_artifact_snapshot()
        self.assertEqual(84, current_previous["file_count"])
        self.assertEqual(PREVIOUS_MANIFEST_SHA256, current_previous["manifest_sha256"])
        self.assertIs(True, current_previous["all_hashes_match"])
        current_installed = batch.installed_resource_snapshot()

        integrity = self.validation["preexisting_integrity"]
        self.assertEqual(
            current_previous, integrity["dialogue_v01_v21_artifacts_before"]
        )
        self.assertEqual(
            current_previous, integrity["dialogue_v01_v21_artifacts_after"]
        )
        self.assertEqual(current_installed, integrity["installed_msgev_before"])
        self.assertEqual(current_installed, integrity["installed_msgev_after"])


if __name__ == "__main__":
    unittest.main()
