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
import build_event_dialogue_batch4 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "31A05234F6E5CCC40BF40E7AE9A19BFE5E3A229A27725B17AA21EB932811C854"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "35EE8A8A3DC5EFF888B32F423884E22F67C8140213EE200A8B30391F3E03C491"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "7650A7831B8F12215AE951049EACAEE08B24119666B1DB7F74EB7ABE07002C9B"
    ),
    batch.VALIDATION_NAME: (
        "35FDFB30F42D4081C0334C793F4E49988D1F1CCDA7FDB05BB40045882F35C936"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class EventDialogueBatch4Tests(unittest.TestCase):
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

    def test_scope_is_exactly_124_displayed_entries(self) -> None:
        selected = batch.selected_ids()
        self.assertEqual(124, len(selected))
        self.assertEqual(list(range(3441, 3565)), selected)
        self.assertEqual([], list(batch.EXCLUDED_INTERNAL_IDS))
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))
        self.assertEqual(124, sum(int(event["selected_count"]) for event in batch.EVENTS))

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(124, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_alignment_evidence_is_three_language_and_source_free(self) -> None:
        self.assertEqual(124, self.evidence["entry_count"])
        self.assertEqual(124, len(self.evidence["entries"]))
        self.assertEqual([], self.evidence["excluded_internal_entries"])
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
                text = path.read_text(encoding="utf-8")
                self.assertEqual(0, batch.shared.shared.cjk_unified_count(text))
                self.assertEqual(0, batch.shared.shared.kana_count(text))

    def test_authored_line_length_is_bounded(self) -> None:
        for entry_id, text in batch.TRANSLATIONS.items():
            visible = [
                len(common.ESC_RE.sub("", line)) for line in text.splitlines()
            ]
            with self.subTest(entry_id=entry_id):
                self.assertLessEqual(max(visible), 32)

    def test_validation_records_invariants_reproducibility_and_safety(self) -> None:
        self.assertIs(True, self.validation["passed"])
        self.assertEqual(
            124,
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
        self.assertEqual([], self.validation["layout_heuristic"]["entries_over_32"])
        safety = self.validation["safety"]
        self.assertFalse(safety["installed_game_files_modified"])
        self.assertFalse(safety["font_files_modified"])
        self.assertFalse(safety["installer_modified"])
        self.assertFalse(safety["existing_v01_v02_v03_artifacts_modified"])


if __name__ == "__main__":
    unittest.main()
