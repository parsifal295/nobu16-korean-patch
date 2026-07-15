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
import build_switch_msgev_v11_cjk_cleanup as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "2A2EE0488CCF6BB70DBBDA2B00A005821DB4CD5C5C8300E4A30F9DF52890295C",
    f"evidence/{batch.EVIDENCE_NAME}": "50A200EEDC46987CCB8DF5C0B1BA8C159730C3F81D6DC4898418973BAAB8E4A8",
    f"review/{batch.REVIEW_NAME}": "757626A2423AAAF092A6D217A9B8CC188558E609D41C4BC607FFD12EC551B515",
    batch.VALIDATION_NAME: "EA7F306FACB528097EE8F3FCEE8E081A24125AD4811EC45E465DF520C6CDE6E9",
}
EXPECTED_TARGET_WRAPPER_SHA256 = (
    "B81BFCF684E62F5CACAA791637B925D97EB89291F887AD4E35B5C939A92DB308"
)
ARCHIVE_PATH = REPO_ROOT / batch.upstream.SWITCH_ARCHIVE_RELATIVE
INPUTS_AVAILABLE = ARCHIVE_PATH.is_file() and all(
    path.is_file()
    for path in (
        GAME_ROOT / batch.upstream.SOURCE_PINS["base_jp"]["logical_path"],
        GAME_ROOT / batch.upstream.SOURCE_PINS["pk_jp"]["logical_path"],
        REPO_ROOT / batch.upstream.SOURCE_PINS["pk_sc_stock"]["logical_path"],
        REPO_ROOT / batch.UPSTREAM_OVERLAY_RELATIVE,
    )
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class _Table:
    def __init__(self, texts: tuple[str, ...]) -> None:
        self.texts = texts
        self.string_count = len(texts)


class SwitchMsgevV11CjkKanaCleanupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_has_exactly_the_reviewed_cleanup_ids(self) -> None:
        resource, stock, entries = common.validate_overlay_shape(self.overlay)
        ids = [int(entry["id"]) for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.upstream.SOURCE_PINS["pk_sc_stock"]["string_count"], stock["string_count"])
        self.assertEqual(list(batch.CANDIDATE_IDS), ids)
        self.assertEqual(batch.EXPECTED_CANDIDATE_IDS_SHA256, batch.hash_json(ids))
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))

    def test_evidence_enforces_source_pins_unique_mapping_and_invariants(self) -> None:
        self.assertEqual(len(batch.CANDIDATE_IDS), self.evidence["entry_count"])
        self.assertEqual(len(batch.CANDIDATE_IDS), len(self.evidence["entries"]))
        selection = self.evidence["selection"]
        self.assertEqual(len(batch.CANDIDATE_IDS), selection["candidate_count"])
        self.assertEqual(batch.EXPECTED_CANDIDATE_IDS_SHA256, selection["candidate_ids_sha256"])
        self.assertEqual(
            batch.EXPECTED_UNIQUE_JP_TO_KO_COUNT,
            selection["strict_unique_jp_to_ko_mapping_count"],
        )
        self.assertEqual(
            batch.EXPECTED_UNIQUE_JP_TO_KO_IDS_SHA256,
            selection["strict_unique_jp_to_ko_mapping_ids_sha256"],
        )
        self.assertEqual(0, selection["bracket_token_mismatch_count"])
        self.assertEqual(0, selection["cleanup_output_forbidden_script_count"])
        self.assertEqual(0, selection["cleanup_output_embedded_nul_count"])
        self.assertEqual(
            batch.UPSTREAM_OVERLAY_SHA256,
            self.evidence["predecessor"]["sha256"],
        )
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertTrue(entry["base_jp_equals_pk_jp"])
                self.assertTrue(entry["switch_ko_differs_from_jp"])
                self.assertTrue(entry["switch_jp_to_ko_is_unique"])
                self.assertEqual(1, entry["switch_semantic_ko_mapping_count"])
                self.assertTrue(entry["upstream_switch_value_has_cjk_or_kana"])
                self.assertFalse(entry["cleanup_value_has_cjk_or_kana"])
                self.assertTrue(entry["pk_sc_invariants_match"])
                self.assertTrue(entry["bracket_tokens_match"])

    def test_effective_catalog_exclusion_and_review_state_are_explicit(self) -> None:
        exclusion = self.evidence["effective_public_catalog_exclusion"]
        self.assertEqual(batch.EXPECTED_EFFECTIVE_OWNER_COUNT, exclusion["unique_id_count"])
        self.assertEqual(
            batch.EXPECTED_EFFECTIVE_OWNER_IDS_SHA256,
            exclusion["ids_sha256"],
        )
        self.assertEqual(0, exclusion["cross_catalog_overlap_count"])
        self.assertEqual(len(batch.CANDIDATE_IDS), len(self.review["entries"]))
        self.assertTrue(all(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertTrue(all(not entry["runtime_reviewed"] for entry in self.review["entries"]))
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(0, self.validation["selection"]["bracket_token_mismatch_count"])
        self.assertEqual(
            batch.EXPECTED_UNIQUE_JP_TO_KO_COUNT,
            self.validation["source_alignment"]["strict_unique_jp_to_ko_mapping_count"],
        )

    def test_ambiguous_jp_to_ko_mapping_fails_closed(self) -> None:
        sources = {
            "base_jp": {"table": _Table(("jp", "jp"))},
            "switch_ko": {"table": _Table(("한글", "다른"))},
        }
        with self.assertRaises(batch.CleanupError):
            batch.unique_switch_jp_to_ko_mapping(sources, (0,))

    def test_public_files_and_workstream_instructions_are_source_free_and_pinned(self) -> None:
        paths = {
            "builder": WORKSTREAM_ROOT / "build_switch_msgev_v11_cjk_cleanup.py",
            "readme": WORKSTREAM_ROOT / "README_KO.md",
            "overlay": WORKSTREAM_ROOT / f"public/{batch.OVERLAY_NAME}",
            "evidence": WORKSTREAM_ROOT / f"evidence/{batch.EVIDENCE_NAME}",
            "review": WORKSTREAM_ROOT / f"review/{batch.REVIEW_NAME}",
            "validation": WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            "test": TEST_PATH,
        }
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
        self.assertEqual(digest(WORKSTREAM_ROOT / "build_switch_msgev_v11_cjk_cleanup.py"), self.validation["generator"]["sha256"])

    @unittest.skipUnless(INPUTS_AVAILABLE, "pinned Switch archive or PC stock input is unavailable")
    def test_rebuild_is_reproducible_and_does_not_modify_inputs(self) -> None:
        before = batch.input_snapshot(GAME_ROOT, REPO_ROOT, ARCHIVE_PATH)
        with tempfile.TemporaryDirectory(prefix="nobu16-switch-msgev-cleanup-test-") as directory:
            result = batch.build_reproducibly(
                GAME_ROOT, REPO_ROOT, ARCHIVE_PATH, Path(directory)
            )
        self.assertEqual(len(batch.CANDIDATE_IDS), result["entry_count"])
        self.assertEqual(batch.EXPECTED_CANDIDATE_IDS_SHA256, result["selected_ids_sha256"])
        self.assertEqual(EXPECTED_TARGET_WRAPPER_SHA256, result["target"]["wrapper_sha256"])
        self.assertEqual(
            EXPECTED_HASHES,
            {
                relative: hashlib.sha256(blob).hexdigest().upper()
                for relative, blob in result["files"].items()
            },
        )
        self.assertEqual(before, batch.input_snapshot(GAME_ROOT, REPO_ROOT, ARCHIVE_PATH))


if __name__ == "__main__":
    unittest.main()
