from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from collections import defaultdict
from pathlib import Path


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
GAME_ROOT = REPO_ROOT.parent
BUILDER_PATH = WORKSTREAM_ROOT / "build_msgdata_pk_native_batch06.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("test_msgdata_pk_native_batch06_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load batch06 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


batch = load_builder()


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


EXPECTED_ARTIFACT_HASHES = {
    "public/msgdata_ko_pk_native_batch06_final_278.v1.json": "53A64CC10C28D48A829F984FEAB3D3F3A27318C2E5A3EE814DF39380EF8DF181",
    "evidence/msgdata_pk_native_batch06_evidence.v1.json": "472897363F1A2B2A86339F1DE67C892EEC45E010FAA0E058E9A3B0243C15F097",
    "review/msgdata_pk_native_batch06_review.v1.json": "71B8AEEC7CBA3B3B28E78A5230728B54B973305651015EC9752514B5831828A8",
    "validation.v1.json": "0FEC13B11C1485BE8222C2ED32015F12E286210491FA4E2F1FC33C0386DD55DD",
}


class MsgdataPkNativeBatch06Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        candidates = [
            GAME_ROOT / batch.STOCK_SC_RELATIVE,
            GAME_ROOT / "KR_PATCH_BACKUP/file_only_transaction/pk-full-messages-seoulhangang-v1/originals/MSG_PK/SC/msgdata.bin",
        ]
        cls.stock_sc = next(
            path for path in candidates
            if path.is_file() and digest(path) == batch.OFFICIAL_PINS["SC"]["sha256"]
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
            "JP": batch.load_pinned_table(cls.args.stock_pk_jp, batch.OFFICIAL_PINS["JP"], "JP")[2],
            "EN": batch.load_pinned_table(cls.args.stock_pk_en, batch.OFFICIAL_PINS["EN"], "EN")[2],
            "TC": batch.load_pinned_table(cls.args.stock_pk_tc, batch.OFFICIAL_PINS["TC"], "TC")[2],
        }
        batch.initialize_and_validate_context(cls.tables)
        cls.overlay = json.loads((WORKSTREAM_ROOT / "public/msgdata_ko_pk_native_batch06_final_278.v1.json").read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM_ROOT / "evidence/msgdata_pk_native_batch06_evidence.v1.json").read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM_ROOT / "review/msgdata_pk_native_batch06_review.v1.json").read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM_ROOT / "validation.v1.json").read_text(encoding="utf-8"))

    def make_args(self, out_root: Path) -> argparse.Namespace:
        return argparse.Namespace(**{**vars(self.args), "out_root": out_root})

    def test_final_selection_exhausts_all_remaining_semantic_targets(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        structural = batch.classify_structural_prefix(self.tables, targets["ids"], owners["ids"])
        selection = batch.validate_selection(targets["ids"], owners["ids"], structural)
        self.assertEqual(278, len(batch.SELECTED_IDS))
        self.assertEqual((2086, 29208), (batch.SELECTED_IDS[0], batch.SELECTED_IDS[-1]))
        self.assertFalse(set(batch.SELECTED_IDS) & owners["ids"])
        self.assertFalse(set(batch.SELECTED_IDS) - targets["ids"])
        self.assertEqual(4110, selection["structural_exclusion_count"])
        self.assertEqual(0, selection["remaining_semantic_count_after_batch"])
        self.assertTrue(selection["final_semantic_completion_after_batch05"])

    def test_overlay_source_hashes_and_format_contracts(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        batch.validate_overlay(self.overlay, self.tables["SC"], owners["ids"], targets["ids"])
        self.assertEqual(list(batch.SELECTED_IDS), [entry["id"] for entry in self.overlay["entries"]])
        for entry in self.overlay["entries"]:
            source = self.tables["SC"].texts[entry["id"]]
            self.assertEqual(batch.common.text_hash(source), entry["source_sc_utf16le_sha256"])
            self.assertEqual([], batch.common.invariant_mismatches(source, entry["ko"]))

    def test_repeated_sc_source_groups_are_translation_consistent(self) -> None:
        groups: dict[str, list[str]] = defaultdict(list)
        for entry in self.overlay["entries"]:
            groups[self.tables["SC"].texts[entry["id"]]].append(entry["ko"])
        repeated = [replacements for replacements in groups.values() if len(replacements) > 1]
        self.assertEqual(33, len(repeated))
        for replacements in repeated:
            self.assertEqual(1, len(set(replacements)))

    def test_replacements_and_artifacts_are_source_script_free(self) -> None:
        for entry in self.overlay["entries"]:
            self.assertNotIn("\x00", entry["ko"])
            self.assertIsNotNone(batch.engine.HANGUL_RE.search(entry["ko"]))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(entry["ko"]))
        for relative in EXPECTED_ARTIFACT_HASHES:
            text = (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8")
            self.assertNotIn("\x00", text)
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(text))

    def test_evidence_review_and_validation_contract(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertEqual(278, self.validation["scope"]["selected_entry_count"])
        self.assertEqual(4110, self.validation["scope"]["excluded_count"])
        self.assertEqual(0, self.validation["scope"]["duplicate_id_count"])
        self.assertEqual(0, self.validation["scope"]["owner_overlap_count"])
        self.assertEqual(0, self.validation["scope"]["non_target_count"])
        self.assertEqual(278, self.validation["format_contract"]["source_hash_match_count"])
        self.assertEqual(0, self.validation["format_contract"]["nul_count"])
        self.assertEqual(278, len(self.evidence["entries"]))
        self.assertEqual(278, self.review["summary"]["translated_count"])
        self.assertEqual(0, self.review["summary"]["runtime_reviewed_count"])

    def test_progress_contains_batch05_and_accepts_batch06_registration(self) -> None:
        owners = batch.load_owner_catalog()
        targets = batch.load_target_catalog(self.args.target_catalog)
        state = batch.validate_progress_catalog(self.args.progress, owners["ids"], targets["ids"], REPO_ROOT)
        self.assertTrue(state["batch05_registered"])
        self.assertIsInstance(state["self_registered"], bool)
        self.assertEqual(0, state["successor_registration_count"])

    def test_public_artifact_hashes_are_pinned(self) -> None:
        for relative, expected in EXPECTED_ARTIFACT_HASHES.items():
            self.assertEqual(expected, digest(WORKSTREAM_ROOT / relative))

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
