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

import build_msgdata_pk_native_completion as batch  # noqa: E402


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgdataPkNativeCompletionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads((WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM_ROOT / batch.VALIDATION_NAME).read_text(encoding="utf-8"))

    def args(self, out_root: Path, progress: Path | None = None) -> Namespace:
        return Namespace(
            stock_pk_jp=batch.GAME_ROOT / "MSG_PK/JP/msgdata.bin",
            stock_pk_sc=batch.GAME_ROOT / batch.STOCK_SC_RELATIVE,
            stock_pk_en=batch.GAME_ROOT / "MSG_PK/EN/msgdata.bin",
            stock_pk_tc=batch.GAME_ROOT / "MSG_PK/TC/msgdata.bin",
            progress=progress or batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
            out_root=out_root,
        )

    def source_paths(self) -> list[Path]:
        args = self.args(WORKSTREAM_ROOT)
        return [args.stock_pk_jp, args.stock_pk_sc, args.stock_pk_en, args.stock_pk_tc, *(batch.REPO_ROOT / row[0] for row in batch.OWNER_OVERLAYS)]

    def test_exact_scope_owner_disjoint_and_stock_contract_safe(self) -> None:
        owners = batch.load_owner_catalog()
        _, _, stock = batch.load_pinned_table(self.args(WORKSTREAM_ROOT).stock_pk_sc, batch.OFFICIAL_PINS["SC"], "PK SC")
        batch.validate_overlay(self.overlay, stock, owners["ids"])
        ids = [entry["id"] for entry in self.overlay["entries"]]
        self.assertEqual(list(batch.EXPECTED_IDS), ids)
        self.assertFalse(set(ids) & owners["ids"])
        self.assertTrue(all(batch.common.has_semantic_text(stock.texts[entry_id]) for entry_id in ids))

    def test_multilingual_decisions_are_explicit_and_conservative(self) -> None:
        evidence = {entry["id"]: entry for entry in self.evidence["entries"]}
        self.assertEqual(["SC", "TC"], evidence[22_594]["semantic_basis_languages"])
        self.assertTrue(evidence[22_594]["sc_esc_printf_contract_preserved"])
        self.assertEqual(["%s", "%+d"], evidence[22_594]["official_format_contracts"]["SC"]["printf"])
        self.assertTrue(evidence[25_546]["unproved_printf_token_intentionally_omitted"])
        self.assertEqual([], evidence[25_546]["official_format_contracts"]["SC"]["printf"])
        self.assertEqual(["%d"], evidence[25_546]["official_format_contracts"]["JP"]["printf"])
        self.assertNotIn("%", next(entry["ko"] for entry in self.overlay["entries"] if entry["id"] == 25_546))

    def test_pre_and_post_integration_rebuilds_are_identical(self) -> None:
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
            result = batch.build(self.args(root / "out", progress_path))
            self.assertEqual(2, result["entry_count"])
            for relative in (f"public/{batch.OVERLAY_NAME}", f"evidence/{batch.EVIDENCE_NAME}", f"review/{batch.REVIEW_NAME}", batch.VALIDATION_NAME):
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (root / "out" / relative).read_bytes())

    def test_artifacts_are_source_free_and_runtime_unreviewed(self) -> None:
        for relative in (f"public/{batch.OVERLAY_NAME}", f"evidence/{batch.EVIDENCE_NAME}", f"review/{batch.REVIEW_NAME}", batch.VALIDATION_NAME):
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts((WORKSTREAM_ROOT / relative).read_text(encoding="utf-8")))
        self.assertTrue(self.validation["passed"])
        self.assertFalse(self.validation["safety"]["complete_game_resource_included"])
        self.assertFalse(self.validation["safety"]["installed_game_files_modified"])
        self.assertEqual(0, self.review["summary"]["runtime_reviewed_count"])

    def test_isolated_builds_are_deterministic_and_inputs_unchanged(self) -> None:
        paths = self.source_paths()
        if not all(path.is_file() for path in paths):
            self.skipTest("pinned official inputs are intentionally absent")
        before = {str(path): digest(path) for path in paths}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            batch.build(self.args(root / "a"))
            batch.build(self.args(root / "b"))
            for relative in (f"public/{batch.OVERLAY_NAME}", f"evidence/{batch.EVIDENCE_NAME}", f"review/{batch.REVIEW_NAME}", batch.VALIDATION_NAME):
                self.assertEqual((root / "a" / relative).read_bytes(), (root / "b" / relative).read_bytes())
                self.assertEqual((WORKSTREAM_ROOT / relative).read_bytes(), (root / "a" / relative).read_bytes())
        self.assertEqual(before, {str(path): digest(path) for path in paths})


if __name__ == "__main__":
    unittest.main()
