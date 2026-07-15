from __future__ import annotations

import copy
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

import build_msgdata_pk_native_batch03 as batch  # noqa: E402


EXPECTED_ARTIFACT_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "FAD7242A909EE205F1AF5D1D555208534E8A345095C94F386583CF2E59A22460",
    f"evidence/{batch.EVIDENCE_NAME}": "66D3BDF8875077D66C936782F8F93A66B3E6B99B00B3AF5E322F8A52CF470829",
    f"review/{batch.REVIEW_NAME}": "679D34739BC04771FB33527E6CB39EE81A3481120755552C7D3797D991550C73",
    batch.VALIDATION_NAME: "9DD844512ACA6261F5E53F5BBC7FF0C74FAE788B743E191A4726793C2C0BBFC6",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgdataPkNativeBatch03Tests(unittest.TestCase):
    @classmethod
    def make_args(
        cls,
        out_root: Path,
        progress: Path | None = None,
        registration_root: Path | None = None,
        target_catalog: Path | None = None,
    ) -> Namespace:
        return Namespace(
            stock_pk_jp=batch.GAME_ROOT / "MSG_PK/JP/msgdata.bin",
            stock_pk_sc=batch.GAME_ROOT / batch.STOCK_SC_RELATIVE,
            stock_pk_en=batch.GAME_ROOT / "MSG_PK/EN/msgdata.bin",
            stock_pk_tc=batch.GAME_ROOT / "MSG_PK/TC/msgdata.bin",
            switch_zip=batch.REPO_ROOT / batch.v13.SWITCH_ARCHIVE_RELATIVE,
            base_jp_strdata=batch.GAME_ROOT / "MSG/JP/strdata.bin",
            target_catalog=target_catalog or batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
            progress=progress or batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            registration_root=registration_root or batch.REPO_ROOT,
            out_root=out_root,
        )

    @classmethod
    def setUpClass(cls) -> None:
        cls.args = cls.make_args(WORKSTREAM_ROOT)
        cls.tables = {}
        for language, path in (
            ("JP", cls.args.stock_pk_jp),
            ("SC", cls.args.stock_pk_sc),
            ("EN", cls.args.stock_pk_en),
            ("TC", cls.args.stock_pk_tc),
        ):
            _, _, cls.tables[language] = batch.load_pinned_table(
                path, batch.OFFICIAL_PINS[language], language
            )
        batch.initialize_and_validate_context(cls.tables)
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

    def source_paths(self) -> list[Path]:
        return [
            self.args.stock_pk_jp,
            self.args.stock_pk_sc,
            self.args.stock_pk_en,
            self.args.stock_pk_tc,
            self.args.switch_zip,
            self.args.base_jp_strdata,
            self.args.target_catalog,
            *(batch.REPO_ROOT / row[0] for row in batch.OWNER_OVERLAYS),
        ]

    def test_selection_is_next_250_semantic_targets_with_complete_fixed_prefix(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        structural = batch.classify_structural_prefix(self.tables, targets["ids"], owners["ids"])
        result = batch.validate_selection(targets["ids"], owners["ids"], structural)
        self.assertEqual(250, len(batch.SELECTED_IDS))
        self.assertEqual(203, sum(len(ids) for ids in structural.values()))
        self.assertEqual(
            23, len(structural["placeholder_dummy_not_a_translatable_display_message"])
        )
        self.assertEqual(164, len(structural["romanized_or_phonetic_lookup_key"]))
        self.assertEqual(16, len(structural["format_or_control_only_token"]))
        self.assertTrue(result["next_250_semantic_after_batch02_boundary"])
        self.assertEqual(22_644, result["fixed_prefix_first_id"])
        self.assertEqual(25_004, result["fixed_prefix_last_id"])
        self.assertEqual(453, result["fixed_prefix_untranslated_count"])
        self.assertFalse(set(batch.SELECTED_IDS) & owners["ids"])
        self.assertFalse(set(batch.SELECTED_IDS) - targets["ids"])

    def test_target_catalog_pins_only_the_semantic_msgdata_row(self) -> None:
        baseline = batch.load_target_catalog(self.args.target_catalog)
        catalog = json.loads(self.args.target_catalog.read_text(encoding="utf-8"))
        unrelated = next(row for row in catalog["resources"] if row["path"] != batch.RESOURCE)
        unrelated["batch03_unrelated_test_marker"] = True
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "catalog.json"
            path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            changed = batch.load_target_catalog(path)
            self.assertEqual(baseline["ids"], changed["ids"])
            self.assertEqual(baseline["snapshot"], changed["snapshot"])
            output = Path(temporary) / "unrelated_catalog_build"
            batch.build(self.make_args(output, target_catalog=path))
            for relative in EXPECTED_ARTIFACT_HASHES:
                self.assertEqual(
                    (WORKSTREAM_ROOT / relative).read_bytes(),
                    (output / relative).read_bytes(),
                )
            msgdata = next(row for row in catalog["resources"] if row["path"] == batch.RESOURCE)
            msgdata["target_count"] -= 1
            path.write_text(
                json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
            )
            with self.assertRaises(batch.BatchError):
                batch.load_target_catalog(path)

    def test_overlay_preserves_every_sc_contract_and_aligned_context(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        batch.validate_overlay(self.overlay, self.tables["SC"], owners["ids"], targets["ids"])
        evidence = {entry["id"]: entry for entry in self.evidence["entries"]}
        self.assertEqual(list(batch.SELECTED_IDS), [entry["id"] for entry in self.overlay["entries"]])
        for entry in self.overlay["entries"]:
            entry_id = entry["id"]
            self.assertEqual(
                [],
                batch.common.invariant_mismatches(self.tables["SC"].texts[entry_id], entry["ko"]),
            )
            self.assertTrue(evidence[entry_id]["pk_sc_invariants_preserved"])
            self.assertTrue(evidence[entry_id]["stock_visible_exact_target"])
        self.assertEqual(
            "EN_omits_sequence_number_while_JP_SC_TC_identify_part_2",
            evidence[23_652]["official_cross_language_conflict"],
        )
        self.assertEqual(["JP", "SC", "TC"], evidence[23_888]["semantic_basis_languages"])
        self.assertEqual(0, self.evidence["switch_reuse_audit"]["usable_korean_candidate_count"])

    def write_registration_fixture(
        self,
        root: Path,
        include_self: bool,
        include_successor: bool,
        owners: dict[str, object],
        targets: dict[str, object],
    ) -> Path:
        self_path = root.joinpath(*Path(batch.SELF_OVERLAY_LOGICAL_PATH).parts)
        self_path.parent.mkdir(parents=True, exist_ok=True)
        self_path.write_bytes(batch.encode_json(batch.make_overlay()))

        successor_id = next(
            entry_id
            for entry_id in sorted(targets["ids"] - owners["ids"] - set(batch.SELECTED_IDS))
            if entry_id > batch.SELECTED_IDS[-1]
            and batch.common.message_invariants(self.tables["SC"].texts[entry_id])
            == {
                "printf": [],
                "unknown_percent_count": 0,
                "leading_whitespace": "",
                "trailing_whitespace": "",
                "esc": [],
                "controls": [],
                "line_breaks": [],
                "pua": [],
            }
        )
        successor = copy.deepcopy(batch.make_overlay())
        successor["overlay_id"] = "pk_msgdata_native_batch04_test_successor.v1"
        successor["entry_count"] = 1
        successor["entries"] = [
            {
                "id": successor_id,
                "source_sc_utf16le_sha256": batch.common.text_hash(
                    self.tables["SC"].texts[successor_id]
                ),
                "ko": "후속 등록 검증",
            }
        ]
        successor_logical = "workstreams/msgdata_pk_native_batch04/public/test_successor.json"
        successor_path = root.joinpath(*Path(successor_logical).parts)
        successor_path.parent.mkdir(parents=True, exist_ok=True)
        successor_path.write_bytes(batch.encode_json(successor))

        progress = json.loads(
            (batch.REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8")
        )
        resource = next(row for row in progress["resources"] if row["path"] == batch.RESOURCE)
        resource["overlay_globs"] = [row[0] for row in batch.OWNER_OVERLAYS]
        if include_self:
            resource["overlay_globs"].append(batch.SELF_OVERLAY_LOGICAL_PATH)
        if include_successor:
            resource["overlay_globs"].append(successor_logical)
        progress_path = root / f"progress_{include_self}_{include_successor}.json"
        progress_path.write_bytes(batch.encode_json(progress))
        return progress_path

    def test_pre_post_self_and_successor_registration_build_identically(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        current = batch.validate_progress_catalog(
            batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            owners["ids"],
            targets["ids"],
        )
        self.assertTrue(current["self_excluded_from_prior_claims"])
        self.assertTrue(current["successors_excluded_from_prior_claims"])
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for include_self, include_successor in (
                (False, False),
                (True, False),
                (False, True),
                (True, True),
            ):
                progress = self.write_registration_fixture(
                    root, include_self, include_successor, owners, targets
                )
                state = batch.validate_progress_catalog(
                    progress, owners["ids"], targets["ids"], root
                )
                self.assertEqual(include_self, state["self_registered"])
                self.assertEqual(int(include_successor), state["successor_registration_count"])
                output = root / f"out_{include_self}_{include_successor}"
                batch.build(self.make_args(output, progress, root))
                for relative in EXPECTED_ARTIFACT_HASHES:
                    self.assertEqual(
                        (WORKSTREAM_ROOT / relative).read_bytes(),
                        (output / relative).read_bytes(),
                    )

    def test_public_artifacts_are_source_free_pinned_and_unreviewed_at_runtime(self) -> None:
        for relative, expected_hash in EXPECTED_ARTIFACT_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected_hash, digest(path))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.script_counts(path.read_text(encoding="utf-8")),
            )
        self.assertTrue(self.validation["passed"])
        self.assertEqual(250, self.review["summary"]["translated_count"])
        self.assertEqual(203, self.review["summary"]["explicit_structural_exclusion_count"])
        self.assertEqual(0, self.review["summary"]["runtime_reviewed_count"])
        self.assertFalse(self.validation["target_catalog"]["whole_catalog_hash_pinned"])
        self.assertFalse(self.validation["safety"]["complete_game_resource_included"])
        self.assertFalse(self.validation["safety"]["installed_game_files_modified"])

    def test_isolated_builds_are_deterministic_and_inputs_unchanged(self) -> None:
        paths = self.source_paths()
        if not all(path.is_file() for path in paths):
            self.skipTest("pinned official inputs are intentionally absent")
        before = {str(path): digest(path) for path in paths}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch.build(self.make_args(root / "a"))
            batch.build(self.make_args(root / "b"))
            for relative in EXPECTED_ARTIFACT_HASHES:
                self.assertEqual((root / "a" / relative).read_bytes(), (root / "b" / relative).read_bytes())
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (root / "a" / relative).read_bytes())
        self.assertEqual(before, {str(path): digest(path) for path in paths})


if __name__ == "__main__":
    unittest.main()
