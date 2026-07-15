from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
WORKSTREAM = ROOT / "workstreams" / "strdata_pk_shared_manual_b02"
MODULE_PATH = WORKSTREAM / "build_strdata_pk_shared_manual_b02.py"
SPEC = importlib.util.spec_from_file_location("build_strdata_pk_shared_manual_b02_for_tests", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = builder
SPEC.loader.exec_module(builder)
GAME_ROOT = ROOT.parent


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


EXPECTED_ARTIFACT_HASHES = {
    "public/strdata_ko_pk_shared_manual_b02_final_27.v1.json": "E2B6BED15880E27264E3B4B339AF739A29B47E4BFB37B953E66664F7C42D63FD",
    "evidence/strdata_pk_shared_manual_b02_evidence.v1.json": "ED34DE13BF07B728CA2909216772016276CD3DE4A77B94B281A3A69F82082654",
    "review/strdata_pk_shared_manual_b02_review.v1.json": "41F29FF536CE65EBD4422543067B3FF6360EE9F8DECC2709DBE4F138C5E0EFFB",
    "translation_validation.v1.json": "F5101D89E744F0026AFEDF17CC7EC68C542EC125BAF5439E0185BE7F9B4AE9D5",
}


class StrdataPkSharedManualB02Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.inputs = builder.direct.load_inputs(GAME_ROOT, builder.DEFAULT_SWITCH_ZIP)
        cls.classified = builder.direct.classify_direct(cls.inputs)
        cls.models = builder.make_models(cls.inputs, cls.classified, ROOT)
        cls.overlay = json.loads((WORKSTREAM / "public" / builder.OVERLAY_NAME).read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM / "evidence" / builder.EVIDENCE_NAME).read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM / "review" / builder.REVIEW_NAME).read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM / builder.VALIDATION_NAME).read_text(encoding="utf-8"))

    def test_selection_is_disjoint_and_exhausts_general_semantic_remainder(self) -> None:
        selection = self.models["selection"]
        self.assertEqual(24_631, selection["registered_predecessor_coverage"])
        self.assertEqual(100, selection["user_reserved_coordinate_count"])
        self.assertEqual(1_959, selection["remaining_after_user_reservation"])
        self.assertEqual(27, selection["selected_count"])
        self.assertEqual(1_932, selection["structural_exclusion_count"])
        self.assertEqual(0, selection["semantic_remaining_after"])
        selected = {(entry["block_id"], entry["slot_id"]) for entry in self.overlay["entries"]}
        self.assertFalse(selected & set(self.models["predecessor_values"]))
        self.assertFalse(selected & set(self.models["reserved_values"]))
        self.assertEqual(builder.SELECTED_COORDINATES_SHA256, selection["selected_coordinates_sha256"])

    def test_block_slot_scope_and_public_models_are_exact(self) -> None:
        self.assertEqual({"0": 14, "1": 7, "2": 4, "3": 2, "4": 0}, self.models["selection"]["selected_per_block"])
        self.assertEqual(list(builder.SELECTED_COORDINATES), [(entry["block_id"], entry["slot_id"]) for entry in self.overlay["entries"]])
        self.assertEqual(builder.encode_json(self.models["overlay"]), (WORKSTREAM / "public" / builder.OVERLAY_NAME).read_bytes())
        self.assertEqual(builder.encode_json(self.models["evidence"]), (WORKSTREAM / "evidence" / builder.EVIDENCE_NAME).read_bytes())
        self.assertEqual(builder.encode_json(self.models["review"]), (WORKSTREAM / "review" / builder.REVIEW_NAME).read_bytes())

    def test_source_hash_format_control_and_source_free_contracts(self) -> None:
        pc_sc = self.classified["pc_sc"]
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["slot_id"])
            self.assertEqual(builder.text_hash(pc_sc[coordinate]), entry["source_sc_utf16le_sha256"])
            self.assertEqual([], builder.common.invariant_mismatches(pc_sc[coordinate], entry["ko"]))
            self.assertIsNone(builder.HAN_OR_KANA_RE.search(entry["ko"]))
            self.assertNotIn("\x00", entry["ko"])
            self.assertTrue(any(0xAC00 <= ord(character) <= 0xD7A3 for character in entry["ko"]))

    def test_repeated_source_groups_are_consistent(self) -> None:
        groups: dict[str, set[str]] = defaultdict(set)
        for entry in self.overlay["entries"]:
            coordinate = (entry["block_id"], entry["slot_id"])
            groups[self.classified["pc_sc"][coordinate]].add(entry["ko"])
        self.assertTrue(all(len(replacements) == 1 for replacements in groups.values()))

    def test_user_owned_unregistered_overlay_is_read_only_and_candidate_excluded(self) -> None:
        reserved_path = ROOT / builder.USER_RESERVED["path"]
        self.assertEqual(builder.USER_RESERVED["sha256"], digest(reserved_path))
        integrated = {**self.models["predecessor_values"], **self.models["values"]}
        candidate, stats = builder.base.build_candidate(self.inputs, integrated)
        _wrapper, raw = builder.base.decompress_wrapper(candidate)
        rebuilt = builder.base.coordinate_texts(builder.base.parse_strdata(raw))
        pristine = self.classified["pc_sc"]
        for coordinate in self.models["reserved_values"]:
            self.assertEqual(pristine[coordinate], rebuilt[coordinate])
        self.assertEqual(24_658, stats["changed_coordinate_count"])

    def test_candidate_is_deterministic_and_preserves_all_other_coordinates(self) -> None:
        integrated = {**self.models["predecessor_values"], **self.models["values"]}
        first, first_stats = builder.base.build_candidate(self.inputs, integrated)
        second, second_stats = builder.base.build_candidate(self.inputs, integrated)
        self.assertEqual(first, second)
        self.assertEqual(first_stats, second_stats)
        self.assertEqual(self.validation["candidate"], first_stats)
        self.assertTrue(first_stats["block_slot_counts_preserved"])
        self.assertTrue(first_stats["target_outside_preserved"])

    def test_progress_contains_exact_predecessors_and_accepts_self_states(self) -> None:
        targets, _ = builder.base.load_target_catalog(builder.TARGET_CATALOG)
        state = builder.audit_progress_registration(
            builder.PROGRESS, ROOT, self.classified["pc_sc"], targets,
            set(self.models["predecessor_values"]), set(self.models["reserved_values"]), self.models["overlay"],
        )
        self.assertEqual(3, state["predecessor_registration_count"])
        self.assertIn(state["self_registration_count"], (0, 1))
        self.assertEqual(0, state["successor_overlay_count"])
        self.assertTrue(state["user_reserved_excluded_from_all_registration_roles"])

    def test_artifact_hashes_and_validation_contract_are_pinned(self) -> None:
        for relative, expected in EXPECTED_ARTIFACT_HASHES.items():
            self.assertEqual(expected, digest(WORKSTREAM / relative))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(digest(MODULE_PATH), self.validation["generator"]["sha256"])
        self.assertEqual({"target_count": 26_690, "before": 24_631, "added": 27, "after": 24_658, "remaining": 2_032, "semantic_remaining_excluding_reserved": 0}, self.validation["coverage"])
        self.assertTrue(self.validation["safety"]["user_untracked_strdata_workstream_read"])
        self.assertFalse(self.validation["safety"]["user_untracked_strdata_workstream_modified"])

    def test_isolated_full_build_changes_no_inputs(self) -> None:
        watched = [
            GAME_ROOT / "MSG/SC/strdata.bin",
            GAME_ROOT / "MSG/JP/strdata.bin",
            builder.PROGRESS,
            builder.TARGET_CATALOG,
            ROOT / builder.USER_RESERVED["path"],
            *(ROOT / row["path"] for row in builder.PREDECESSORS),
        ]
        before = {path: digest(path) for path in watched}
        with tempfile.TemporaryDirectory(prefix="n16-strdata-b02-") as temporary:
            root = Path(temporary)
            validation = builder.build(
                GAME_ROOT, builder.DEFAULT_SWITCH_ZIP, ROOT, root / "artifacts",
                root / "candidate" / builder.RESOURCE, builder.PROGRESS,
            )
            self.assertEqual(27, validation["selection"]["selected_count"])
            for relative in EXPECTED_ARTIFACT_HASHES:
                if relative == builder.VALIDATION_NAME:
                    continue
                self.assertEqual((WORKSTREAM / relative).read_bytes(), (root / "artifacts" / relative).read_bytes())
        self.assertEqual(before, {path: digest(path) for path in watched})


if __name__ == "__main__":
    unittest.main()
