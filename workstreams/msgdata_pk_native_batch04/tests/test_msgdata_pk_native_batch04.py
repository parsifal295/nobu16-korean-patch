from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
GAME_ROOT = REPO_ROOT.parent
BUILDER_PATH = WORKSTREAM_ROOT / "build_msgdata_pk_native_batch04.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("test_msgdata_pk_native_batch04_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load batch04 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


batch = load_builder()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


EXPECTED_ARTIFACT_HASHES = {
    "public/msgdata_ko_pk_native_batch04_300.v1.json": "9AA64137BF915FF732CB1DD4C625F156E9784FD65F3779CE381F7DBF4D9E2B45",
    "evidence/msgdata_pk_native_batch04_evidence.v1.json": "F27F7D66C76189367C430535654E165DEADCBA70831FE889423E887176B05225",
    "review/msgdata_pk_native_batch04_review.v1.json": "6AD360B7695C119DFDD47C942B70A72535084DBF2D3E1CD48A732D852437310F",
    "validation.v1.json": "97D61846C5298350440438679490A8D26303ADE4EDF6B3E6FE71BFD3C61CE572",
}


class MsgdataPkNativeBatch04Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        candidates = [
            GAME_ROOT / batch.STOCK_SC_RELATIVE,
            GAME_ROOT
            / "KR_PATCH_BACKUP"
            / "file_only_transaction"
            / "pk-full-messages-seoulhangang-v1"
            / "originals"
            / "MSG_PK"
            / "SC"
            / "msgdata.bin",
        ]
        cls.stock_sc = next(
            (
                path
                for path in candidates
                if path.is_file() and digest(path) == batch.OFFICIAL_PINS["SC"]["sha256"]
            ),
            candidates[0],
        )
        cls.args = argparse.Namespace(
            stock_pk_jp=GAME_ROOT / "MSG_PK/JP/msgdata.bin",
            stock_pk_sc=cls.stock_sc,
            stock_pk_en=GAME_ROOT / "MSG_PK/EN/msgdata.bin",
            stock_pk_tc=GAME_ROOT / "MSG_PK/TC/msgdata.bin",
            target_catalog=REPO_ROOT / batch.TARGET_CATALOG_RELATIVE,
            progress=REPO_ROOT / batch.PROGRESS_RELATIVE,
            registration_root=REPO_ROOT,
            out_root=WORKSTREAM_ROOT,
        )
        cls.tables = {
            "SC": batch.load_pinned_table(cls.stock_sc, batch.OFFICIAL_PINS["SC"], "SC")[2],
            "JP": batch.load_pinned_table(
                cls.args.stock_pk_jp, batch.OFFICIAL_PINS["JP"], "JP"
            )[2],
            "EN": batch.load_pinned_table(
                cls.args.stock_pk_en, batch.OFFICIAL_PINS["EN"], "EN"
            )[2],
            "TC": batch.load_pinned_table(
                cls.args.stock_pk_tc, batch.OFFICIAL_PINS["TC"], "TC"
            )[2],
        }
        batch.initialize_and_validate_context(cls.tables)
        cls.overlay = json.loads(
            (WORKSTREAM_ROOT / "public/msgdata_ko_pk_native_batch04_300.v1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.evidence = json.loads(
            (WORKSTREAM_ROOT / "evidence/msgdata_pk_native_batch04_evidence.v1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.review = json.loads(
            (WORKSTREAM_ROOT / "review/msgdata_pk_native_batch04_review.v1.json").read_text(
                encoding="utf-8"
            )
        )
        cls.validation = json.loads(
            (WORKSTREAM_ROOT / "validation.v1.json").read_text(encoding="utf-8")
        )

    def make_args(self, out_root: Path) -> argparse.Namespace:
        return argparse.Namespace(**{**vars(self.args), "out_root": out_root})

    def test_selection_is_next_300_semantic_targets_and_owner_disjoint(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        structural = batch.classify_structural_prefix(self.tables, targets["ids"], owners["ids"])
        selection = batch.validate_selection(targets["ids"], owners["ids"], structural)
        ids = list(batch.SELECTED_IDS)
        self.assertEqual(300, len(ids))
        self.assertEqual(300, len(set(ids)))
        self.assertEqual(ids, sorted(ids))
        self.assertEqual((25006, 27101), (ids[0], ids[-1]))
        self.assertFalse(set(ids) & owners["ids"])
        self.assertFalse(set(ids) - targets["ids"])
        self.assertEqual(642, selection["structural_exclusion_count"])
        self.assertTrue(selection["next_300_semantic_after_batch03"])

    def test_overlay_has_zero_duplicate_ids_and_exact_source_hashes(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        batch.validate_overlay(self.overlay, self.tables["SC"], owners["ids"], targets["ids"])
        ids = [entry["id"] for entry in self.overlay["entries"]]
        self.assertEqual(0, len(ids) - len(set(ids)))
        self.assertEqual(list(batch.SELECTED_IDS), ids)
        for entry in self.overlay["entries"]:
            source = self.tables["SC"].texts[entry["id"]]
            self.assertEqual(batch.common.text_hash(source), entry["source_sc_utf16le_sha256"])

    def test_printf_esc_pua_controls_and_line_breaks_are_preserved(self) -> None:
        checked = 0
        for entry in self.overlay["entries"]:
            source = self.tables["SC"].texts[entry["id"]]
            source_contract = batch.common.message_invariants(source)
            target_contract = batch.common.message_invariants(entry["ko"])
            self.assertEqual(source_contract["printf"], target_contract["printf"])
            self.assertEqual(source_contract["unknown_percent_count"], target_contract["unknown_percent_count"])
            self.assertEqual(source_contract["esc"], target_contract["esc"])
            self.assertEqual(source_contract["controls"], target_contract["controls"])
            self.assertEqual(source_contract["line_breaks"], target_contract["line_breaks"])
            self.assertEqual(source_contract["pua"], target_contract["pua"])
            self.assertEqual(source_contract["leading_whitespace"], target_contract["leading_whitespace"])
            self.assertEqual(source_contract["trailing_whitespace"], target_contract["trailing_whitespace"])
            self.assertEqual([], batch.common.invariant_mismatches(source, entry["ko"]))
            checked += 1
        self.assertEqual(300, checked)

    def test_replacements_are_nul_free_hangul_and_source_script_free(self) -> None:
        for entry in self.overlay["entries"]:
            ko = entry["ko"]
            self.assertNotIn("\x00", ko)
            self.assertIsNotNone(batch.HANGUL_RE.search(ko))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(ko)
            )
        for relative in EXPECTED_ARTIFACT_HASHES:
            text = (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("\x00", text)
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(text)
            )

    def test_evidence_and_validation_report_exact_contract(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(300, self.validation["scope"]["selected_entry_count"])
        self.assertEqual(0, self.validation["scope"]["duplicate_id_count"])
        self.assertEqual(0, self.validation["scope"]["owner_overlap_count"])
        self.assertEqual(0, self.validation["scope"]["non_target_count"])
        self.assertEqual(300, self.validation["format_contract"]["source_hash_match_count"])
        self.assertTrue(self.validation["format_contract"]["printf_preserved"])
        self.assertTrue(self.validation["format_contract"]["esc_preserved"])
        self.assertTrue(self.validation["format_contract"]["pua_preserved"])
        self.assertTrue(self.validation["format_contract"]["line_breaks_preserved"])
        self.assertEqual(0, self.validation["format_contract"]["nul_count"])
        self.assertEqual(0, self.validation["format_contract"]["source_cjk_or_kana_count"])
        self.assertEqual(300, self.review["summary"]["translated_count"])
        self.assertEqual(642, self.review["summary"]["explicit_structural_exclusion_count"])
        self.assertEqual(0, self.review["summary"]["runtime_reviewed_count"])
        self.assertEqual(300, len(self.evidence["entries"]))

    def test_public_artifact_hashes_are_pinned(self) -> None:
        for relative, expected in EXPECTED_ARTIFACT_HASHES.items():
            self.assertEqual(expected, digest(WORKSTREAM_ROOT / relative))

    def test_current_progress_accepts_unregistered_batch04(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        state = batch.validate_progress_catalog(
            self.args.progress, owners["ids"], targets["ids"], REPO_ROOT
        )
        self.assertFalse(state["self_registered"])
        self.assertEqual(0, state["successor_registration_count"])

    def test_isolated_builds_are_deterministic_and_inputs_unchanged(self) -> None:
        paths = [
            self.args.stock_pk_jp,
            self.args.stock_pk_sc,
            self.args.stock_pk_en,
            self.args.stock_pk_tc,
            self.args.target_catalog,
            self.args.progress,
            *(REPO_ROOT / row[0] for row in batch.OWNER_OVERLAYS),
        ]
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
