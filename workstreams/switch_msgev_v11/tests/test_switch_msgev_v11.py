from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_switch_msgev_v11 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "71652CACEB757BFFF47FB119789150BD841DD9FF6B6AC180D5B2AA1B06231703",
    f"evidence/{batch.EVIDENCE_NAME}": "9F2B633308D18C8A9475A6DB7413C6ABF602E3AC01DCD153920C134A7DC4DCA5",
    f"review/{batch.REVIEW_NAME}": "EFDEBA53A039892805F7818EF99EE1277DD52BE9AEE972CEBF630DE078E46525",
    batch.VALIDATION_NAME: "5695B19EB8294D9BAB9688424B53B1331C5FBCBA3B4C86B91AD060E5AA1B9C64",
}
EXPECTED_TARGET_WRAPPER_SHA256 = (
    "452BB33E584351D33EC90F5303A51552A5AC766D79DC0D8BFF97EADC4C8E693A"
)
ARCHIVE_PATH = REPO_ROOT / batch.SWITCH_ARCHIVE_RELATIVE
INPUTS_AVAILABLE = ARCHIVE_PATH.is_file() and all(
    path.is_file()
    for path in (
        GAME_ROOT / batch.SOURCE_PINS["base_jp"]["logical_path"],
        GAME_ROOT / batch.SOURCE_PINS["pk_jp"]["logical_path"],
        REPO_ROOT / batch.SOURCE_PINS["pk_sc_stock"]["logical_path"],
    )
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class SwitchMsgevV11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_has_the_reviewed_source_free_7025_id_set(self) -> None:
        resource, stock, entries = common.validate_overlay_shape(self.overlay)
        ids = [int(entry["id"]) for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.SOURCE_PINS["pk_sc_stock"]["string_count"], stock["string_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(entries))
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.hash_json(ids))
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_records_all_compatibility_gates_and_cjk_kana_exclusion(self) -> None:
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, self.evidence["entry_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(self.evidence["entries"]))
        selection = self.evidence["selection"]
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, selection["selected_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, selection["selected_ids_sha256"])
        source_script = selection["source_script_filter"]
        self.assertEqual(batch.EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT, source_script["excluded_count"])
        self.assertEqual(
            batch.EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256,
            source_script["excluded_ids_sha256"],
        )
        self.assertEqual("snake7594", self.evidence["source_release"]["author_account"])
        self.assertEqual(
            "https://github.com/snake7594/nobunaga-shinsei-korean-patch/releases/tag/v1.1",
            self.evidence["source_release"]["release_url"],
        )
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertTrue(entry["base_jp_equals_pk_jp"])
                self.assertTrue(entry["switch_ko_differs_from_jp"])
                self.assertTrue(entry["pk_sc_invariants_match"])

    def test_existing_catalog_and_runtime_review_metadata_are_explicit(self) -> None:
        exclusion = self.evidence["existing_public_catalog_exclusion"]
        self.assertEqual(batch.EXPECTED_EXISTING_ID_COUNT, exclusion["unique_id_count"])
        self.assertEqual(batch.EXPECTED_EXISTING_IDS_SHA256, exclusion["ids_sha256"])
        self.assertEqual(0, exclusion["cross_catalog_overlap_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(self.review["entries"]))
        bracket_flags = [
            entry
            for entry in self.review["entries"]
            if "custom_bracket_token_difference_review" in entry["uncertainty_flags"]
        ]
        self.assertEqual(8, len(bracket_flags))
        self.assertTrue(self.validation["custom_bracket_token_review"]["runtime_review_required"])
        self.assertEqual(
            batch.EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT,
            self.validation["source_script_exclusion"]["excluded_count"],
        )

    def test_public_files_and_workstream_instructions_are_source_free_and_pinned(self) -> None:
        paths = {
            "builder": WORKSTREAM_ROOT / "build_switch_msgev_v11.py",
            "readme": WORKSTREAM_ROOT / "README_KO.md",
            "overlay": WORKSTREAM_ROOT / f"public/{batch.OVERLAY_NAME}",
            "evidence": WORKSTREAM_ROOT / f"evidence/{batch.EVIDENCE_NAME}",
            "review": WORKSTREAM_ROOT / f"review/{batch.REVIEW_NAME}",
            "validation": WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            "test": TEST_PATH,
        }
        self.assertEqual(7, len(paths))
        for label, path in paths.items():
            with self.subTest(label=label):
                self.assertTrue(path.is_file())
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    batch.source_free_counts(path.read_bytes()),
                )
        for relative, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(WORKSTREAM_ROOT / relative))

    @unittest.skipUnless(INPUTS_AVAILABLE, "pinned Switch archive or PC stock input is unavailable")
    def test_rebuild_is_reproducible_and_does_not_modify_inputs(self) -> None:
        before = batch.input_snapshot(GAME_ROOT, REPO_ROOT, ARCHIVE_PATH)
        with tempfile.TemporaryDirectory(prefix="nobu16-switch-msgev-test-") as directory:
            result = batch.build_reproducibly(
                GAME_ROOT, REPO_ROOT, ARCHIVE_PATH, Path(directory)
            )
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, result["entry_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, result["selected_ids_sha256"])
        self.assertEqual(EXPECTED_TARGET_WRAPPER_SHA256, result["target"]["wrapper_sha256"])
        self.assertEqual(
            EXPECTED_HASHES,
            {relative: hashlib.sha256(blob).hexdigest().upper() for relative, blob in result["files"].items()},
        )
        self.assertEqual(before, batch.input_snapshot(GAME_ROOT, REPO_ROOT, ARCHIVE_PATH))


if __name__ == "__main__":
    unittest.main()
