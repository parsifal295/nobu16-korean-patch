from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from collections import Counter
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
GAME_ROOT = REPO_ROOT.parent
MODULE_PATH = WORKSTREAM_ROOT / "build_switch_strdata_v13_direct_transfer.py"
SPEC = importlib.util.spec_from_file_location("build_switch_strdata_v13_direct_transfer", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)

EXPECTED_ARTIFACT_HASHES = {
    f"public/{builder.OVERLAY_NAME}": "2C4B1F7C52D5B04EE915693C20D4662011E18A3B6535212905609B3ABBA9FE98",
    f"evidence/{builder.EVIDENCE_NAME}": "E260EA4DEDD0C124B1E784FDEB6D6470C2596C33AE1127CB076681EC41268E9B",
    f"review/{builder.REVIEW_NAME}": "2F7F45E963A843D80ABC771DACC718589ED86224151B9C677E7383D91977857A",
    builder.VALIDATION_NAME: "95899A50E0CEC2A9234A86C28200E68719BB0341BA392765E2F7843DC54B0196",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=builder.common.strict_object,
    )


class SwitchStrdataV13DirectTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{builder.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{builder.EVIDENCE_NAME}")
        cls.review = load(f"review/{builder.REVIEW_NAME}")
        cls.validation = load(builder.VALIDATION_NAME)

    def test_artifacts_are_pinned_source_free_and_distribution_safe(self) -> None:
        for relative, expected_hash in EXPECTED_ARTIFACT_HASHES.items():
            with self.subTest(relative=relative):
                path = WORKSTREAM_ROOT / relative
                self.assertEqual(expected_hash, digest(path))
                value = load(relative)
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    builder.validate_source_free(value, relative),
                )
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_commercial_source_text"]
        )
        self.assertFalse(
            self.overlay["distribution_policy"]["contains_complete_game_resource"]
        )
        self.assertFalse(self.overlay["provenance"]["whole_switch_file_copied"])

    def test_overlay_scope_is_sorted_unique_and_deduplicated(self) -> None:
        entries = self.overlay["entries"]
        coordinates = [(entry["block_id"], entry["slot_id"]) for entry in entries]
        self.assertEqual(builder.EXPECTED["net_new"], len(entries))
        self.assertEqual(len(coordinates), len(set(coordinates)))
        self.assertEqual(sorted(coordinates), coordinates)
        self.assertEqual(
            builder.EXPECTED["net_new_coordinates_sha256"],
            builder.canonical_hash([list(value) for value in coordinates]),
        )
        self.assertEqual(
            builder.EXPECTED["net_new_per_block"],
            {str(block): Counter(value[0] for value in coordinates)[block] for block in range(5)},
        )
        existing = {(0, slot_id) for slot_id in range(100)} | {(1, 22)}
        self.assertEqual(101, len(existing))
        self.assertFalse(existing & set(coordinates))

    def test_evidence_and_review_cover_the_exact_overlay_membership(self) -> None:
        overlay_coordinates = [
            (item["block_id"], item["slot_id"]) for item in self.overlay["entries"]
        ]
        evidence_coordinates = [
            (item["block_id"], item["slot_id"]) for item in self.evidence["entries"]
        ]
        review_coordinates = [
            (item["block_id"], item["slot_id"]) for item in self.review["entries"]
        ]
        self.assertEqual(overlay_coordinates, evidence_coordinates)
        self.assertEqual(overlay_coordinates, review_coordinates)
        self.assertTrue(
            all(
                item["classification"] == "direct"
                and item["same_block_slot_coordinate"]
                and item["invariant_mismatch_count"] == 0
                and item["bracket_placeholder_sequence_equal"]
                and item["source_script_free"]
                for item in self.evidence["entries"]
            )
        )
        self.assertTrue(
            all(
                item["automatic_contract_review_passed"]
                and item["human_review_required"]
                and not item["runtime_reviewed"]
                for item in self.review["entries"]
            )
        )

    def test_committed_validation_records_required_binary_proofs(self) -> None:
        validation = self.validation
        self.assertTrue(validation["passed"])
        self.assertEqual(24_525, validation["classification"]["counts"]["direct"])
        self.assertEqual(0, validation["classification"]["counts"]["semantic-aligned"])
        self.assertEqual(1_431, validation["classification"]["counts"]["manual"])
        self.assertEqual(6_355, validation["classification"]["counts"]["unusable"])
        self.assertEqual(0, validation["deduplication"]["duplicate_coordinate_count"])
        self.assertEqual(0, validation["overlay_validation"]["target_membership_failure_count"])
        self.assertEqual(0, validation["overlay_validation"]["replacement_contract_failure_count"])
        self.assertTrue(validation["candidate"]["all_other_coordinates_preserved"])
        self.assertTrue(validation["candidate"]["existing_overlay_values_preserved"])
        self.assertTrue(validation["candidate"]["block_slot_counts_preserved"])
        self.assertTrue(validation["deterministic_builds_identical"])
        self.assertFalse(validation["candidate"]["whole_switch_file_copied"])
        self.assertEqual(builder.PC_SC_PIN["packed_sha256"], validation["inputs"]["pc_sc_pristine_original"]["packed_sha256"])
        self.assertEqual(builder.EXPECTED["candidate_packed_sha256"], validation["candidate"]["packed_sha256"])
        self.assertNotEqual(builder.SWITCH_PIN["packed_sha256"], validation["candidate"]["packed_sha256"])

    def test_recomputed_classification_and_candidate_match_pins_without_live_write(self) -> None:
        watched = [
            GAME_ROOT / builder.PC_JP_RELATIVE,
            GAME_ROOT / builder.PC_SC_RELATIVE,
            builder.DEFAULT_SWITCH_ZIP,
        ]
        before = {path: digest(path) for path in watched}
        inputs = builder.load_inputs(GAME_ROOT, builder.DEFAULT_SWITCH_ZIP)
        classified = builder.classify_direct(inputs)
        original_b00 = builder.EXISTING_B00
        original_shared = builder.EXISTING_SHARED_UI
        try:
            builder.EXISTING_B00 = Path("missing-user-workstream-b00.json")
            builder.EXISTING_SHARED_UI = Path("missing-user-workstream-shared-ui.json")
            models = builder.build_artifact_models(inputs, classified)
        finally:
            builder.EXISTING_B00 = original_b00
            builder.EXISTING_SHARED_UI = original_shared
        self.assertEqual(
            {(0, slot_id) for slot_id in range(100)} | {(1, 22)},
            set(models["existing_values"]),
        )
        self.assertTrue(
            all(
                models["existing_values"][coordinate] == replacement
                for coordinate, replacement in builder.B00_CONFLICT_OVERRIDES.items()
            )
        )
        overlay_validation = builder.validate_overlay(models["overlay"], classified)
        first, first_raw, first_stats = builder.build_candidate(inputs, models)
        second, second_raw, second_stats = builder.build_candidate(inputs, models)
        self.assertEqual(first, second)
        self.assertEqual(first_raw, second_raw)
        self.assertEqual(first_stats, second_stats)
        self.assertEqual(builder.EXPECTED["candidate_packed_sha256"], builder.sha256(first))
        self.assertEqual(builder.EXPECTED["candidate_raw_sha256"], builder.sha256(first_raw))
        self.assertEqual(24_525, first_stats["changed_coordinate_count"])
        self.assertEqual(7_786, first_stats["unchanged_coordinate_count"])
        self.assertEqual(0, overlay_validation["duplicate_coordinate_count"])
        self.assertEqual(before, {path: digest(path) for path in watched})

    def test_full_reproducible_build_matches_committed_artifacts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n16-switch-strdata-v13-") as temporary:
            root = Path(temporary)
            validation = builder.build(
                GAME_ROOT,
                builder.DEFAULT_SWITCH_ZIP,
                root / "artifacts",
                root / builder.RESOURCE,
            )
            rebuilt = {
                artifact["path"]: artifact["sha256"]
                for artifact in validation["artifacts"].values()
            }
            self.assertEqual(
                {key: value for key, value in EXPECTED_ARTIFACT_HASHES.items() if key != builder.VALIDATION_NAME},
                rebuilt,
            )
            self.assertEqual(
                EXPECTED_ARTIFACT_HASHES[builder.VALIDATION_NAME],
                digest(root / "artifacts" / builder.VALIDATION_NAME),
            )
            self.assertEqual(
                builder.EXPECTED["candidate_packed_sha256"],
                digest(root / builder.RESOURCE),
            )


if __name__ == "__main__":
    unittest.main()
