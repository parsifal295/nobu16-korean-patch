from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_switch_msgdata_v13_invariant_recovery as batch  # noqa: E402


EXPECTED_ARTIFACT_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "0372E73879BD2E3C927F69375079AA6EE507E2FF2824E9AE8E8525E109CCC982",
    f"evidence/{batch.EVIDENCE_NAME}": "F65806B58AA137252C3C5D5F0183B1ED160A5D35F26CB7D95E69D0859F640F3A",
    f"review/{batch.REVIEW_NAME}": "35984595DA1C93911D15A0B8BBA95F7241820C787A7BB4CA4446A7116F43F99D",
    batch.VALIDATION_NAME: "02DDBC831C6293466A42C7F21014718BA367ADF049586E589993F525B83A81AD",
}

EXPECTED_TARGET = {
    "resource": batch.RESOURCE,
    "entry_count": 145,
    "complete_target_included": False,
    "packed_size": 517_941,
    "packed_sha256": "C833E34C98BF9AB5A3F5816972308401B16FFF19CB4C0BF96C7B1CCC29B4DFB7",
    "raw_size": 515_892,
    "raw_sha256": "2FC746DB14097137C4559A4D0D8613027F963C6B82DEBA10BFAEF73F6C0806F2",
    "parse_rebuild_round_trip": True,
    "wrapper_round_trip": True,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SwitchMsgdataV13InvariantRecoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads(
            (WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8")
        )
        cls.review = json.loads(
            (WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8")
        )
        cls.validation = json.loads(
            (WORKSTREAM_ROOT / batch.VALIDATION_NAME).read_text(encoding="utf-8")
        )

    def build_args(self, out_root: Path) -> Namespace:
        return Namespace(
            switch_zip=batch.REPO_ROOT / batch.SWITCH_ARCHIVE_RELATIVE,
            base_jp_strdata=batch.GAME_ROOT / "MSG" / "JP" / "strdata.bin",
            stock_pk_jp=batch.GAME_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
            stock_pk_sc=batch.GAME_ROOT / batch.STOCK_SC_RELATIVE,
            progress=batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            out_root=out_root,
        )

    def source_paths(self) -> list[Path]:
        args = self.build_args(WORKSTREAM_ROOT)
        return [
            args.switch_zip,
            args.base_jp_strdata,
            args.stock_pk_jp,
            args.stock_pk_sc,
            *(batch.REPO_ROOT / descriptor["path"] for descriptor in batch.OWNER_OVERLAYS),
        ]

    def test_v13_text_is_pinned_byte_identical_to_v11(self) -> None:
        source = self.validation["source_release"]
        self.assertEqual("v1.3", source["tag"])
        self.assertTrue(source["v1_3_text_member_equals_v1_1"])
        self.assertEqual(
            batch.V11_TEXT_IDENTITY["member_packed_sha256"],
            source["member_packed_sha256"],
        )
        self.assertEqual(
            batch.V11_TEXT_IDENTITY["member_raw_sha256"],
            source["member_raw_sha256"],
        )
        self.assertEqual(batch.SWITCH_V13["archive_sha256"], source["archive_sha256"])

    def test_residual_scope_and_honest_exclusions_are_exact(self) -> None:
        scope = self.validation["scope"]
        self.assertEqual(batch.EXPECTED_RESIDUAL_COUNT, scope["residual_candidate_count"])
        self.assertEqual(batch.EXPECTED_VISIBLE_COUNT, scope["stock_visible_candidate_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, scope["selected_entry_count"])
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, scope["selected_ids_sha256"])
        self.assertEqual(list(batch.EXPECTED_EXCLUDED_IDS), scope["excluded_ids"])
        self.assertEqual(batch.EXPECTED_EXCLUDED_IDS_SHA256, scope["excluded_ids_sha256"])
        reasons = {row["id"]: row["reason"] for row in self.review["exclusions"]}
        self.assertEqual("stock_sc_blank_not_translation_target", reasons[18_048])
        self.assertIn("esc_printf", reasons[22_594])
        self.assertEqual("stock_sc_dummy_has_no_printf_contract", reasons[25_546])

    def test_overlay_is_owner_disjoint_stock_visible_and_format_safe(self) -> None:
        args = self.build_args(WORKSTREAM_ROOT)
        owners = batch.load_owner_catalog(batch.REPO_ROOT)
        _, _, stock = batch.upstream._load_pk_msgdata(
            args.stock_pk_sc,
            batch.upstream.PK_SC_MSGDATA_PIN,
            "pristine PK SC msgdata",
        )
        batch.validate_overlay(self.overlay, stock, owners["ids"])
        ids = [entry["id"] for entry in self.overlay["entries"]]
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(len(ids), len(set(ids)))
        self.assertFalse(set(ids) & owners["ids"])
        self.assertFalse(set(batch.EXPECTED_EXCLUDED_IDS) & set(ids))
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.hash_json(ids))

    def test_post_integration_self_registration_is_excluded_from_prior_claims(self) -> None:
        owners = batch.load_owner_catalog(batch.REPO_ROOT)
        current = batch.validate_progress_catalog(
            batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            owners,
        )
        self.assertTrue(current["self_excluded_from_prior_claims"])
        self.assertTrue(current["successors_excluded_from_prior_claims"])
        progress = json.loads(
            (batch.REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        resource = next(row for row in progress["resources"] if row["path"] == batch.RESOURCE)
        expected_successors = [
            pattern
            for pattern in resource["overlay_globs"]
            if pattern
            not in {
                batch.SELF_OVERLAY_LOGICAL_PATH,
                *(str(descriptor["path"]) for descriptor in batch.OWNER_OVERLAYS),
            }
        ]
        self.assertEqual(len(expected_successors), current["successor_overlay_count"])
        self.assertTrue(all(row["source_free"] for row in current["successor_overlays"]))
        resource["overlay_globs"] = [
            pattern
            for pattern in resource["overlay_globs"]
            if pattern != batch.SELF_OVERLAY_LOGICAL_PATH
        ]
        resource["overlay_globs"].append(batch.SELF_OVERLAY_LOGICAL_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            progress_path = Path(temporary) / "translation_progress.json"
            progress_path.write_text(
                json.dumps(progress, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            integrated = batch.validate_progress_catalog(progress_path, owners)
            self.assertTrue(integrated["self_registered"])
            self.assertEqual(1, integrated["self_registration_count"])
            self.assertTrue(integrated["self_registration"]["excluded_from_prior_claims"])
            self.assertEqual(
                batch.EXPECTED_OWNER_UNION_COUNT,
                integrated["prior_owner_effective_id_count"],
            )
            self.assertEqual(
                batch.EXPECTED_OWNER_UNION_IDS_SHA256,
                integrated["prior_owner_effective_ids_sha256"],
            )
            args = self.build_args(Path(temporary) / "rebuilt")
            args.progress = progress_path
            rebuilt = batch.build(args)
            self.assertEqual(batch.EXPECTED_SELECTED_COUNT, rebuilt["entry_count"])
            self.assertEqual(
                (WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME).read_bytes(),
                (args.out_root / "public" / batch.OVERLAY_NAME).read_bytes(),
            )

    def test_repairs_are_source_free_and_special_fragment_cases_are_audited(self) -> None:
        by_id = {entry["id"]: entry for entry in self.overlay["entries"]}
        evidence = {entry["id"]: entry for entry in self.evidence["entries"]}
        for entry in self.overlay["entries"]:
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.source_script_counts(entry["ko"]),
            )
            self.assertTrue(batch.has_meaningful_hangul(entry["ko"]))
            self.assertTrue(evidence[entry["id"]]["pk_sc_invariants_preserved"])
            self.assertTrue(evidence[entry["id"]]["custom_bracket_tokens_preserved"])
        self.assertEqual(2, by_id[18_047]["ko"].count("\n"))
        self.assertEqual([18_048], evidence[18_047]["adjacent_switch_semantic_fragment_ids"])
        self.assertEqual([18_063], evidence[18_062]["adjacent_switch_semantic_fragment_ids"])
        self.assertEqual([18_067], evidence[18_068]["adjacent_switch_semantic_fragment_ids"])
        for entry_id in batch.PUA_IDS:
            self.assertIn("\uE003", by_id[entry_id]["ko"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        for relative_path, expected_hash in EXPECTED_ARTIFACT_HASHES.items():
            path = WORKSTREAM_ROOT / relative_path
            self.assertEqual(expected_hash, digest(path))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.source_script_counts(path.read_text(encoding="utf-8")),
            )
        self.assertTrue(self.validation["passed"])
        self.assertFalse(self.validation["safety"]["complete_game_resource_included"])
        self.assertFalse(self.validation["safety"]["installed_game_files_modified"])

    def test_in_memory_target_is_deterministic_and_pinned(self) -> None:
        if not all(path.is_file() for path in self.source_paths()):
            self.skipTest("pinned external or stock inputs are intentionally absent")
        args = self.build_args(WORKSTREAM_ROOT)
        before = {str(path): digest(path) for path in self.source_paths()}
        packed, _, stock = batch.upstream._load_pk_msgdata(
            args.stock_pk_sc,
            batch.upstream.PK_SC_MSGDATA_PIN,
            "pristine PK SC msgdata",
        )
        target_a = batch.upstream.reconstruct_sc_target(packed, stock, self.overlay["entries"])
        target_b = batch.upstream.reconstruct_sc_target(packed, stock, self.overlay["entries"])
        self.assertEqual(EXPECTED_TARGET, target_a)
        self.assertEqual(target_a, target_b)
        self.assertEqual(EXPECTED_TARGET, self.validation["target_reconstruction"])
        self.assertEqual(before, {str(path): digest(path) for path in self.source_paths()})

    def test_isolated_rebuilds_are_byte_identical(self) -> None:
        if not all(path.is_file() for path in self.source_paths()):
            self.skipTest("pinned external or stock inputs are intentionally absent")
        before = {str(path): digest(path) for path in self.source_paths()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out_a = root / "a"
            out_b = root / "b"
            batch.build(self.build_args(out_a))
            batch.build(self.build_args(out_b))
            for relative_path in EXPECTED_ARTIFACT_HASHES:
                self.assertEqual(
                    (out_a / relative_path).read_bytes(),
                    (out_b / relative_path).read_bytes(),
                )
                self.assertEqual(
                    (WORKSTREAM_ROOT / relative_path).read_bytes(),
                    (out_a / relative_path).read_bytes(),
                )
        self.assertEqual(before, {str(path): digest(path) for path in self.source_paths()})


if __name__ == "__main__":
    unittest.main()
