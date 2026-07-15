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
import build_switch_msgev_v13_jp_hash_recovery as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "BE5D7147E24573775713E4D4C3F31BE0029C41885FFB0DD3507BBA17610FD62D",
    f"evidence/{batch.EVIDENCE_NAME}": "145D41185066C3ED2CEFB69BEC77E5581AC2ADA2D65D9436E9B311D8450BD784",
    f"review/{batch.REVIEW_NAME}": "AA375F5E88C0972B1A13E5729161A57E928E6DA7B7212E34F794341A480F4323",
    batch.VALIDATION_NAME: "76769B86D186B2848B05B8B0EC70C62466C4E8ED2CC1361F4AD6140E9963E829",
}
EXPECTED_TARGET_WRAPPER_SHA256 = (
    "F4E5C4AFC990F2C00E83C29AE0E78C7BFD3DB9E2E63803CA6CFA1201E37B751D"
)
EXPECTED_TARGET_RAW_SHA256 = (
    "3A24EBECFD882738775501E7AD7DFBFE4B6F7519D2B974D9551CD8B79FADA1CB"
)

ARCHIVE_PATH = REPO_ROOT / batch.SWITCH_ARCHIVE_RELATIVE
INPUTS_AVAILABLE = ARCHIVE_PATH.is_file() and all(
    path.is_file()
    for path in (
        GAME_ROOT / batch.upstream.SOURCE_PINS["base_jp"]["logical_path"],
        GAME_ROOT / batch.upstream.SOURCE_PINS["pk_jp"]["logical_path"],
        REPO_ROOT / batch.upstream.SOURCE_PINS["pk_sc_stock"]["logical_path"],
        *(REPO_ROOT / descriptor["path"] for descriptor in batch.OWNER_OVERLAYS),
    )
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class SwitchMsgevV13JpHashRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_overlay_is_the_exact_sorted_source_free_245_set(self) -> None:
        resource, stock, entries = common.validate_overlay_shape(self.overlay)
        ids = [int(entry["id"]) for entry in entries]
        self.assertEqual(batch.RESOURCE, resource)
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(ids))
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.hash_json(ids))
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(
            batch.upstream.SOURCE_PINS["pk_sc_stock"]["string_count"],
            stock["string_count"],
        )
        for entry in entries:
            with self.subTest(entry_id=entry["id"]):
                self.assertTrue(batch.upstream.has_meaningful_hangul(entry["ko"]))
                self.assertFalse(batch.upstream.contains_cjk_or_kana(entry["ko"]))

    def test_evidence_proves_hash_exact_equality_uniqueness_and_invariants(self) -> None:
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, self.evidence["entry_count"])
        self.assertEqual(
            batch.EXPECTED_SELECTED_IDS_SHA256,
            self.evidence["selected_ids_sha256"],
        )
        self.assertTrue(self.evidence["selected_within_stock_visible_target"])
        self.assertEqual(0, self.evidence["selected_activated_jp_only_overlap_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(self.evidence["entries"]))
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual(
                    entry["pk_jp_utf16le_sha256"],
                    entry["base_jp_utf16le_sha256"],
                )
                self.assertTrue(entry["jp_hash_matches"])
                self.assertTrue(entry["jp_exact_in_memory_equality"])
                self.assertTrue(entry["unique_meaningful_switch_ko"])
                self.assertFalse(entry["switch_ko_contains_cjk_or_kana"])
                self.assertTrue(entry["pk_sc_invariants_match"])
                self.assertTrue(entry["custom_bracket_tokens_match"])
                self.assertTrue(entry["stock_visible_target"])
                self.assertFalse(entry["activated_jp_only_slot"])

    def test_selection_stages_visible_target_and_activated_range_are_pinned(self) -> None:
        selection = self.validation["selection"]
        stages = selection["stages"]
        expected = {
            "stock_visible_target_count": batch.EXPECTED_STOCK_VISIBLE_COUNT,
            "effective_owner_count": batch.EXPECTED_EFFECTIVE_OWNER_COUNT,
            "effective_visible_owner_count": batch.EXPECTED_EFFECTIVE_VISIBLE_OWNER_COUNT,
            "activated_jp_only_claimed_count": batch.EXPECTED_ACTIVATED_JP_ONLY_COUNT,
            "unclaimed_stock_visible_count": batch.EXPECTED_UNCLAIMED_VISIBLE_COUNT,
            "jp_hash_bucket_match_count": batch.EXPECTED_JP_HASH_BUCKET_MATCH_COUNT,
            "jp_exact_in_memory_match_count": batch.EXPECTED_JP_EXACT_MATCH_COUNT,
            "unique_meaningful_switch_ko_count": batch.EXPECTED_UNIQUE_MEANINGFUL_KO_COUNT,
            "source_script_free_count": batch.EXPECTED_SOURCE_SCRIPT_FREE_COUNT,
            "sc_invariant_match_count": batch.EXPECTED_SC_INVARIANT_MATCH_COUNT,
            "custom_bracket_token_match_count": batch.EXPECTED_BRACKET_TOKEN_MATCH_COUNT,
            "selected_count": batch.EXPECTED_SELECTED_COUNT,
        }
        for key, value in expected.items():
            with self.subTest(stage=key):
                self.assertEqual(value, stages[key])
        activated = selection["activated_jp_only_range"]
        self.assertEqual(batch.ACTIVATED_JP_ONLY_START, activated["start"])
        self.assertEqual(batch.ACTIVATED_JP_ONLY_END, activated["end"])
        self.assertEqual(batch.EXPECTED_ACTIVATED_JP_ONLY_COUNT, activated["count"])
        self.assertEqual(0, activated["pristine_sc_visible_count"])
        self.assertTrue(selection["selected_within_stock_visible_target"])
        self.assertEqual(0, selection["selected_activated_jp_only_overlap_count"])

    def test_existing_owners_and_all_exclusion_sets_are_pinned(self) -> None:
        owners = self.validation["effective_public_catalog_exclusion"]
        self.assertEqual(batch.EXPECTED_EFFECTIVE_OWNER_COUNT, owners["existing_unique_id_count"])
        self.assertEqual(
            batch.EXPECTED_EFFECTIVE_OWNER_IDS_SHA256,
            owners["existing_ids_sha256"],
        )
        self.assertEqual(0, owners["selected_overlap_count"])
        exclusions = self.validation["selection"]["exclusions"]
        expected = {
            "no_jp_match": (
                batch.EXPECTED_NO_JP_MATCH_COUNT,
                batch.EXPECTED_NO_JP_MATCH_IDS_SHA256,
            ),
            "nonunique_meaningful_ko": (
                batch.EXPECTED_NONUNIQUE_KO_COUNT,
                batch.EXPECTED_NONUNIQUE_KO_IDS_SHA256,
            ),
            "source_script": (
                batch.EXPECTED_SOURCE_SCRIPT_EXCLUDED_COUNT,
                batch.EXPECTED_SOURCE_SCRIPT_EXCLUDED_IDS_SHA256,
            ),
            "sc_invariant": (
                batch.EXPECTED_INVARIANT_EXCLUDED_COUNT,
                batch.EXPECTED_INVARIANT_EXCLUDED_IDS_SHA256,
            ),
            "bracket_token": (0, batch.EMPTY_LIST_SHA256),
        }
        for label, (count, ids_hash) in expected.items():
            with self.subTest(exclusion=label):
                self.assertEqual(count, exclusions[label]["count"])
                self.assertEqual(ids_hash, exclusions[label]["ids_sha256"])

    def test_v13_event_text_is_pinned_byte_identical_to_v11(self) -> None:
        identity = self.validation["switch_text_identity"]
        self.assertTrue(identity["v13_is_byte_identical_to_v11"])
        self.assertEqual(
            identity["v13_member_packed_sha256"],
            identity["v11_member_packed_sha256"],
        )
        self.assertEqual(
            identity["v13_member_raw_sha256"],
            identity["v11_member_raw_sha256"],
        )
        self.assertEqual("v1.3", self.validation["source_release"]["release_tag"])
        self.assertEqual(
            batch.SWITCH_RELEASE["archive_sha256"],
            self.validation["source_release"]["archive_sha256"],
        )

    def test_unique_meaningful_value_gate_rejects_ambiguity(self) -> None:
        same = [
            {"ko": "한국어"},
            {"ko": "한국어"},
            {"ko": "source"},
        ]
        ambiguous = [{"ko": "한국어"}, {"ko": "다른값"}]
        absent = [{"ko": "source"}, {"ko": ""}]
        self.assertEqual("한국어", batch.resolve_unique_meaningful_ko(same, "source"))
        self.assertIsNone(batch.resolve_unique_meaningful_ko(ambiguous, "source"))
        self.assertIsNone(batch.resolve_unique_meaningful_ko(absent, "source"))

    def test_public_artifacts_instructions_and_generator_are_source_free_and_pinned(self) -> None:
        paths = {
            "builder": WORKSTREAM_ROOT / "build_switch_msgev_v13_jp_hash_recovery.py",
            "overlay": WORKSTREAM_ROOT / f"public/{batch.OVERLAY_NAME}",
            "evidence": WORKSTREAM_ROOT / f"evidence/{batch.EVIDENCE_NAME}",
            "review": WORKSTREAM_ROOT / f"review/{batch.REVIEW_NAME}",
            "validation": WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            "test": TEST_PATH,
        }
        expected_scan = {"han_or_kana_count": 0, "embedded_nul_count": 0}
        for label, path in paths.items():
            with self.subTest(label=label):
                self.assertTrue(path.is_file())
                self.assertEqual(expected_scan, batch.source_free_counts(path.read_bytes()))
        for relative, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(WORKSTREAM_ROOT / relative))
        self.assertEqual(
            digest(WORKSTREAM_ROOT / "build_switch_msgev_v13_jp_hash_recovery.py"),
            self.validation["generator"]["sha256"],
        )
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(self.review["entries"]))
        self.assertTrue(all(row["human_review_required"] for row in self.review["entries"]))
        self.assertTrue(all(not row["runtime_reviewed"] for row in self.review["entries"]))

    @unittest.skipUnless(INPUTS_AVAILABLE, "pinned Switch archive or PC input is unavailable")
    def test_rebuild_is_reproducible_and_does_not_modify_inputs(self) -> None:
        before = batch.input_snapshot(GAME_ROOT, REPO_ROOT, ARCHIVE_PATH)
        with tempfile.TemporaryDirectory(prefix="nobu16-msgev-v13-hash-test-") as directory:
            result = batch.build_reproducibly(
                GAME_ROOT, REPO_ROOT, ARCHIVE_PATH, Path(directory)
            )
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, result["entry_count"])
        self.assertEqual(
            batch.EXPECTED_SELECTED_IDS_SHA256, result["selected_ids_sha256"]
        )
        self.assertEqual(
            EXPECTED_TARGET_WRAPPER_SHA256, result["target"]["wrapper_sha256"]
        )
        self.assertEqual(EXPECTED_TARGET_RAW_SHA256, result["target"]["raw_sha256"])
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
