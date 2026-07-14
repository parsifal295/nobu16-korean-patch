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
import build_event_dialogue_batch3 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "482239403E31932E9FD735C4C6F08228F650147B0A9D523431B5F4D17CBBF1FF"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "730FD461C3FD01AAC98DA548F462090261245A001296D8D36FCF57F22E9974F3"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "5C834F7C2D130E3AC1A246CFDFC73A7248C3078F122FA7AEB60230AB3E5B7AAD"
    ),
    batch.VALIDATION_NAME: (
        "2734D895A0D224ECE9BC7BB31DF16BB57534F83BF0219BFF4B046C1EF2710B4B"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class EventDialogueBatch3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay, _ = common.load_json_strict(
            WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME
        )
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"),
            object_pairs_hook=common.strict_object,
        )

    def test_scope_is_exactly_partitioned(self) -> None:
        selected = batch.selected_ids()
        excluded = list(batch.EXCLUDED_INTERNAL_IDS)
        self.assertEqual(114, len(selected))
        self.assertEqual(18, len(excluded))
        self.assertFalse(set(selected) & set(excluded))
        self.assertEqual(
            list(range(batch.SCOPE_START, batch.SCOPE_END + 1)),
            sorted(selected + excluded),
        )
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(114, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )
        self.assertFalse(set(batch.EXCLUDED_INTERNAL_IDS) & set(batch.TRANSLATIONS))

    def test_public_files_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                text = path.read_text(encoding="utf-8")
                self.assertEqual(0, batch.shared.cjk_unified_count(text))
                self.assertEqual(0, batch.shared.kana_count(text))

    def test_authored_line_length_is_bounded(self) -> None:
        for entry_id, text in batch.TRANSLATIONS.items():
            visible = [
                len(common.ESC_RE.sub("", line)) for line in text.splitlines()
            ]
            with self.subTest(entry_id=entry_id):
                self.assertLessEqual(max(visible), 32)

    def test_validation_records_placeholder_and_safety_guards(self) -> None:
        self.assertIs(True, self.validation["passed"])
        self.assertEqual(
            114,
            self.validation["replacement_invariants"][
                "custom_bracket_placeholder_checks"
            ],
        )
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            "deferred_not_computed",
            self.validation["font_integration"]["state"],
        )
        safety = self.validation["safety"]
        self.assertFalse(safety["installed_game_files_modified"])
        self.assertFalse(safety["font_files_modified"])
        self.assertFalse(safety["installer_modified"])
        self.assertFalse(safety["existing_v01_or_v02_artifacts_modified"])


if __name__ == "__main__":
    unittest.main()
