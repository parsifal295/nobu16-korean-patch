from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


sys.dont_write_bytecode = True
TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
TOOLS_DIR = TEST_PATH.parents[3] / "tools"
sys.path.insert(0, str(WORKSTREAM_DIR))
sys.path.insert(0, str(TOOLS_DIR))

import build_common_message_overlay as common  # noqa: E402
import build_event_dialogue_batch27 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "1166AA776A051407DA2E871B44D7CFA55CA56A5564F943D8E595302E5BD02CB5"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "BB25D7A402CC4AFDF56ADF54E52B8FC486BED0561D3986C082CB068E74BFA09B"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "5776F82D8B17DF7E9EF4CADA6A846D74A9D58E96101783A3CC85474E9FEE620D"
    ),
    batch.VALIDATION_NAME: (
        "68E0525107379E64C5A38472733EE424184C98BA495D8B3BABE1A3E4529F246C"
    ),
}
PREVIOUS_MANIFEST_SHA256 = (
    "E91C9679E3802ECBD7AFAA1889F5B250881C2D1D5B8A782BD33583DFC7B98D47"
)
BOUNDARY_IDS = [6372, 6373, 6389, 6390, 6410, 6411, 6427, 6428, 6443, 6444, 6481, 6482]
TARGET_WRAPPER_SHA256 = (
    "2D10200EA343CC7F273E28C01F59D8DDD875603196AE2E3AB0A16676FBFC9F19"
)
TARGET_RAW_SHA256 = (
    "A7992575BFC452ED00658FDE141B78063F693E2D7CE12DE140DDB05FCDF5C501"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def digest_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest().upper()


class EventDialogueBatch27Tests(unittest.TestCase):
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
        cls.review = json.loads(
            (WORKSTREAM_DIR / "review" / batch.REVIEW_NAME).read_text(
                encoding="utf-8"
            ),
            object_pairs_hook=common.strict_object,
        )
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"),
            object_pairs_hook=common.strict_object,
        )

    def test_scope_is_exactly_109_continuous_nonoverlapping_entries(self) -> None:
        selected = batch.selected_ids()
        self.assertEqual(109, len(selected))
        self.assertEqual(list(range(6373, 6482)), selected)
        self.assertEqual([], list(batch.EXCLUDED_INTERNAL_IDS))
        self.assertEqual(selected, sorted(batch.TRANSLATIONS))
        self.assertEqual(5, len(batch.EVENTS))
        self.assertEqual(
            109, sum(int(event["selected_count"]) for event in batch.EVENTS)
        )
        existing = batch.existing_dialogue_overlay_snapshot()
        self.assertEqual(26, existing["overlay_count"])
        self.assertEqual(0, existing["cross_overlay_duplicate_id_count"])
        self.assertEqual([], existing["selected_overlap_ids"])

    def test_overlay_contains_only_selected_authored_entries(self) -> None:
        resource, _, entries = common.validate_overlay_shape(self.overlay)
        self.assertEqual("MSG_PK/SC/msgev.bin", resource)
        self.assertEqual(batch.BATCH_ID, self.overlay["overlay_id"])
        self.assertEqual(109, self.overlay["entry_count"])
        self.assertEqual(
            batch.TRANSLATIONS,
            {int(entry["id"]): str(entry["ko"]) for entry in entries},
        )

    def test_sc_invariants_and_custom_bracket_placeholders_are_exact(self) -> None:
        stock_sc = (
            WORKSTREAM_DIR.parents[1]
            / "backups"
            / "officer_name_probe_v0_1"
            / "msgev.SC.stock.bin"
        )
        table = batch.source_shared.load_source(stock_sc, "SC")[2]
        for entry_id, replacement in batch.TRANSLATIONS.items():
            with self.subTest(entry_id=entry_id):
                source = table.texts[entry_id]
                self.assertEqual([], common.invariant_mismatches(source, replacement))
                self.assertEqual(
                    batch.BRACKET_TOKEN_RE.findall(source),
                    batch.BRACKET_TOKEN_RE.findall(replacement),
                )

    def test_alignment_evidence_is_four_language_and_source_free(self) -> None:
        self.assertEqual(109, self.evidence["entry_count"])
        self.assertEqual(109, len(self.evidence["entries"]))
        self.assertEqual(5, len(self.evidence["event_groups"]))
        self.assertEqual(
            BOUNDARY_IDS,
            [int(anchor["id"]) for anchor in self.evidence["boundary_anchors"]],
        )
        self.assertEqual(
            {"SC", "JP", "TC", "EN"}, set(self.evidence["source_files"])
        )
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "TC", "EN"}, set(entry["references"]))
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

    def test_all_four_sources_and_sc_target_rebuild_are_byte_exact(self) -> None:
        args = SimpleNamespace(
            stock_sc=(
                WORKSTREAM_DIR.parents[1]
                / "backups"
                / "officer_name_probe_v0_1"
                / "msgev.SC.stock.bin"
            ),
            stock_jp=WORKSTREAM_DIR.parents[2] / "MSG_PK" / "JP" / "msgev.bin",
            stock_tc=WORKSTREAM_DIR.parents[2] / "MSG_PK" / "TC" / "msgev.bin",
            stock_en=WORKSTREAM_DIR.parents[2] / "MSG_PK" / "EN" / "msgev.bin",
        )
        sources = batch.load_sources(args)
        self.assertEqual({"SC", "JP", "TC", "EN"}, set(sources))
        first = batch.reconstruct_sc_target(sources["SC"])
        second = batch.reconstruct_sc_target(sources["SC"])
        self.assertEqual(first["wrapper"], second["wrapper"])
        self.assertEqual(first["raw"], second["raw"])
        self.assertEqual(109, first["changed_entry_count"])
        self.assertEqual(TARGET_WRAPPER_SHA256, digest_bytes(first["wrapper"]))
        self.assertEqual(TARGET_RAW_SHA256, digest_bytes(first["raw"]))

    def test_validation_records_reconstruction_collision_exclusion_and_safety(self) -> None:
        self.assertIs(True, self.validation["passed"])
        alignment = self.validation["source_alignment"]
        self.assertEqual(["SC", "JP", "TC", "EN"], alignment["languages"])
        self.assertEqual(436, alignment["selected_reference_hash_count"])
        self.assertFalse(alignment["pk_or_base_sources_auto_copied"])
        self.assertEqual(109, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            batch.existing_dialogue_overlay_snapshot(),
            self.validation["existing_overlay_exclusion"],
        )
        reconstruction = self.validation["reconstruction"]
        self.assertTrue(reconstruction["sc_overlay_rebuild_a_b_byte_identical"])
        self.assertEqual(109, reconstruction["changed_entry_count"])
        self.assertEqual(TARGET_WRAPPER_SHA256, reconstruction["target"]["wrapper_sha256"])
        self.assertEqual(TARGET_RAW_SHA256, reconstruction["target"]["raw_sha256"])
        self.assertFalse(reconstruction["target"]["complete_target_included"])
        self.assertEqual(
            {"SC": True, "JP": True, "TC": True, "EN": True},
            reconstruction["source_parse_rebuild_byte_identical"],
        )
        integrity = self.validation["preexisting_integrity"]
        self.assertEqual(
            integrity["installed_msgev_before"], integrity["installed_msgev_after"]
        )
        self.assertEqual(batch.installed_resource_snapshot(), integrity["installed_msgev_after"])
        safety = self.validation["safety"]
        for value in safety.values():
            self.assertFalse(value)

    def test_previous_dialogue_artifacts_remain_pinned(self) -> None:
        previous = batch.previous_artifact_snapshot()
        self.assertEqual(104, previous["file_count"])
        self.assertEqual(PREVIOUS_MANIFEST_SHA256, previous["manifest_sha256"])
        self.assertIs(True, previous["all_hashes_match"])
        integrity = self.validation["preexisting_integrity"]
        self.assertEqual(previous, integrity["dialogue_v01_v26_artifacts_before"])
        self.assertEqual(previous, integrity["dialogue_v01_v26_artifacts_after"])


if __name__ == "__main__":
    unittest.main()
