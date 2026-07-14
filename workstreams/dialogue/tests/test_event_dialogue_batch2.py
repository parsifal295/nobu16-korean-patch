from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
TOOLS_DIR = TEST_PATH.parents[3] / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch2 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "2EF36C22207A8B9A1CBFDB1212A8DBA2A8C49EDAF2D68BF95DDFB07404CDA637"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "73A2B18423C1E7A6081F2500218A260EA04A0411F07729BF5344443F9ADAD033"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "F90BDE5F561C489D2251A0EB6CF81FA5B4B04E4C8030682AFEC77A7B86073B7A"
    ),
    batch.VALIDATION_NAME: (
        "D235D88BADEAC9159F1E3684BAA0F3FED35E1F4E2C3FCEA499C1E2AD85685F31"
    ),
    batch.VERIFICATION_NAME: (
        "B46D67212D2B00B5DEABF1A60627ABE1EF6AB70D16B9EEC94C284D638987739B"
    ),
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class EventDialogueBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay_path = WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME
        cls.overlay, _ = common.load_json_strict(cls.overlay_path)
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"),
            object_pairs_hook=common.strict_object,
        )

    def test_ids_are_one_exact_contiguous_range(self) -> None:
        ids = batch.selected_ids()
        self.assertEqual(list(range(3230, 3309)), ids)
        self.assertEqual(ids, sorted(batch.TRANSLATIONS))
        self.assertEqual(79, len(ids))

    def test_five_event_ranges_cover_every_id_once(self) -> None:
        covered = [
            entry_id
            for event in batch.EVENTS
            for entry_id in range(event["start_id"], event["end_id"] + 1)
        ]
        self.assertEqual(batch.selected_ids(), covered)
        self.assertEqual(5, len(batch.EVENTS))

    def test_overlay_is_exactly_the_authored_korean(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(79, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_authored_text_is_nfc_source_free_and_layout_bounded(self) -> None:
        for entry_id, text in batch.TRANSLATIONS.items():
            with self.subTest(entry_id=entry_id):
                self.assertEqual(unicodedata.normalize("NFC", text), text)
                self.assertEqual(0, batch.cjk_unified_count(text))
                self.assertEqual(0, batch.kana_count(text))
                self.assertTrue(text.strip())
                visible = [
                    len(common.ESC_RE.sub("", line)) for line in text.splitlines()
                ]
                self.assertLessEqual(max(visible), 32)

    def test_all_public_artifacts_are_pinned_and_source_free(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                text = path.read_text(encoding="utf-8")
                self.assertEqual(0, batch.cjk_unified_count(text))
                self.assertEqual(0, batch.kana_count(text))

    def test_font_followup_is_deferred_and_pinned(self) -> None:
        followup = self.validation["font_followup"]
        self.assertEqual("deferred_to_later_font_revision", followup["integration_state"])
        self.assertIs(True, followup["must_not_enter_current_font_v6_or_installer"])
        self.assertEqual(442, followup["renderable_character_count"])
        self.assertEqual(423, followup["hangul_syllable_count"])
        self.assertEqual(86, followup["font_v5_missing_hangul_count"])
        self.assertEqual(
            "C4253D1F677195C068C0837FE066EDF2471D706435EF8440CD1E6229D520A029",
            followup["font_v5_missing_hangul_sha256"],
        )

    def test_strict_json_rejects_duplicate_and_case_colliding_keys(self) -> None:
        with self.assertRaises(common.CommonMessageOverlayError):
            json.loads('{"id": 1, "ID": 2}', object_pairs_hook=common.strict_object)


if __name__ == "__main__":
    unittest.main()
