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

import build_msgdata_pk_native_batch01 as batch  # noqa: E402


EXPECTED_ARTIFACT_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "EA6394ADCFF33D2B7737BE098A9637B3545250CE4E9C59EED2237C25DCBEC0AF",
    f"evidence/{batch.EVIDENCE_NAME}": "96376779D2567039971B84D281354A65233AA6AB4687263E4A93D2F699459884",
    f"review/{batch.REVIEW_NAME}": "4A44F7E91571AB05FF03F44AD68B9D8C807F9B45AE0865E8EEC514D5644BD53F",
    batch.VALIDATION_NAME: "BE9191F6A6B8AC4C9FF3FDEB6325D18ADF8ACF7F8881886645F86CE95CFC203A",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgdataPkNativeBatch01Tests(unittest.TestCase):
    @classmethod
    def make_args(cls, out_root: Path, progress: Path | None = None) -> Namespace:
        return Namespace(
            stock_pk_jp=batch.GAME_ROOT / "MSG_PK/JP/msgdata.bin",
            stock_pk_sc=batch.GAME_ROOT / batch.STOCK_SC_RELATIVE,
            stock_pk_en=batch.GAME_ROOT / "MSG_PK/EN/msgdata.bin",
            stock_pk_tc=batch.GAME_ROOT / "MSG_PK/TC/msgdata.bin",
            switch_zip=batch.REPO_ROOT / batch.v13.SWITCH_ARCHIVE_RELATIVE,
            base_jp_strdata=batch.GAME_ROOT / "MSG/JP/strdata.bin",
            target_catalog=batch.REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
            progress=progress or batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            out_root=out_root,
        )

    @classmethod
    def setUpClass(cls) -> None:
        cls.args = cls.make_args(WORKSTREAM_ROOT)
        cls.tables = {}
        for language, path in (
            ("JP", cls.args.stock_pk_jp), ("SC", cls.args.stock_pk_sc),
            ("EN", cls.args.stock_pk_en), ("TC", cls.args.stock_pk_tc),
        ):
            _, _, cls.tables[language] = batch.load_pinned_table(path, batch.OFFICIAL_PINS[language], language)
        batch.initialize_and_validate_context(cls.tables)
        cls.overlay = json.loads((WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM_ROOT / batch.VALIDATION_NAME).read_text(encoding="utf-8"))

    def source_paths(self) -> list[Path]:
        return [
            self.args.stock_pk_jp, self.args.stock_pk_sc, self.args.stock_pk_en, self.args.stock_pk_tc,
            self.args.switch_zip, self.args.base_jp_strdata, self.args.target_catalog,
            *(batch.REPO_ROOT / row[0] for row in batch.OWNER_OVERLAYS),
        ]

    def test_selection_is_exact_ascending_target_prefix_after_honest_exclusions(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        result = batch.validate_selection(targets["ids"], owners["ids"])
        self.assertEqual(100, len(batch.SELECTED_IDS))
        self.assertEqual(139, len(batch.EXCLUDED_IDS))
        self.assertTrue(result["first_100_after_explicit_exclusions"])
        self.assertEqual(15_063, result["first_selected_id"])
        self.assertEqual(18_157, result["last_selected_id"])
        self.assertFalse(set(batch.SELECTED_IDS) & owners["ids"])
        self.assertFalse(set(batch.SELECTED_IDS) - targets["ids"])
        self.assertEqual(set(batch.EXCLUDED_IDS), {entry_id for ids in batch.EXCLUSION_GROUPS.values() for entry_id in ids})

    def test_overlay_preserves_every_pk_sc_contract_and_switch_has_no_reusable_text(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        batch.validate_overlay(self.overlay, self.tables["SC"], owners["ids"], targets["ids"])
        evidence = {entry["id"]: entry for entry in self.evidence["entries"]}
        self.assertEqual(list(batch.SELECTED_IDS), [entry["id"] for entry in self.overlay["entries"]])
        for entry in self.overlay["entries"]:
            entry_id = entry["id"]
            self.assertEqual([], batch.common.invariant_mismatches(self.tables["SC"].texts[entry_id], entry["ko"]))
            self.assertTrue(evidence[entry_id]["pk_sc_invariants_preserved"])
            self.assertTrue(evidence[entry_id]["custom_bracket_tokens_preserved"])
            self.assertTrue(evidence[entry_id]["stock_visible_exact_target"])
        self.assertEqual(0, self.evidence["switch_reuse_audit"]["usable_korean_candidate_count"])

    def test_pre_and_post_self_registration_rebuild_identically(self) -> None:
        owners = batch.load_owner_catalog()
        current = batch.validate_progress_catalog(batch.REPO_ROOT / batch.PROGRESS_RELATIVE, owners["ids"])
        self.assertTrue(current["self_excluded_from_prior_claims"])
        progress = json.loads((batch.REPO_ROOT / batch.PROGRESS_RELATIVE).read_text(encoding="utf-8"))
        resource = next(row for row in progress["resources"] if row["path"] == batch.RESOURCE)
        resource["overlay_globs"] = [path for path in resource["overlay_globs"] if path != batch.SELF_OVERLAY_LOGICAL_PATH]
        resource["overlay_globs"].append(batch.SELF_OVERLAY_LOGICAL_PATH)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            progress_path = root / "progress.json"
            progress_path.write_text(json.dumps(progress, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            state = batch.validate_progress_catalog(progress_path, owners["ids"])
            self.assertTrue(state["self_registered"])
            batch.build(self.make_args(root / "out", progress_path))
            for relative in EXPECTED_ARTIFACT_HASHES:
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (root / "out" / relative).read_bytes())

    def test_public_artifacts_are_source_free_pinned_and_unreviewed_at_runtime(self) -> None:
        for relative, expected_hash in EXPECTED_ARTIFACT_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected_hash, digest(path))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(path.read_text(encoding="utf-8")))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(100, self.review["summary"]["translated_count"])
        self.assertEqual(0, self.review["summary"]["runtime_reviewed_count"])
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
