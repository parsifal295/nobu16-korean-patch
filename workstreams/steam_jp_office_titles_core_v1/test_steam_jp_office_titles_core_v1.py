#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import importlib.util
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
MODULE_PATH = HERE / "build_steam_jp_office_titles_core_v1.py"
SPEC = importlib.util.spec_from_file_location("steam_jp_office_titles_core_v1", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = module
SPEC.loader.exec_module(module)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SteamJpOfficeTitlesCoreV1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.stock = module.DEFAULT_STOCK_ROOT / Path(module.RESOURCE)
        if cls.stock.is_file():
            cls.before = (cls.stock.stat().st_size, digest(cls.stock))
            cls.context = module.build_wave08_baseline(module.DEFAULT_STOCK_ROOT)
        else:
            cls.before = None
            cls.context = None

    def require_stock(self) -> None:
        if self.before is None:
            self.skipTest("pinned pristine Steam 1.1.7 JP msgdata is unavailable")

    def test_exact_scope_dictionary_and_exclusions(self) -> None:
        self.assertEqual(146, len(module.SCOPE_DISPLAY_IDS))
        self.assertEqual(146, len(module.CANONICAL_KO_BY_DISPLAY_ID))
        self.assertEqual(tuple(sorted(module.SCOPE_DISPLAY_IDS)), module.SCOPE_DISPLAY_IDS)
        self.assertEqual(set(module.SCOPE_DISPLAY_IDS), set(module.CANONICAL_KO_BY_DISPLAY_ID))
        self.assertEqual(module.SCOPE_DISPLAY_IDS_SHA256, module.COMMON.canonical_hash(list(module.SCOPE_DISPLAY_IDS)))
        rows = [{"id": key, "ko": module.CANONICAL_KO_BY_DISPLAY_ID[key]} for key in module.SCOPE_DISPLAY_IDS]
        self.assertEqual(module.CANONICAL_DICTIONARY_SHA256, module.COMMON.canonical_hash(rows))
        self.assertFalse(set(range(16614, 16625)) & set(module.CANONICAL_KO_BY_DISPLAY_ID))
        self.assertEqual("우대신", module.CANONICAL_KO_BY_DISPLAY_ID[16402])
        self.assertEqual("대납언", module.CANONICAL_KO_BY_DISPLAY_ID[16404])
        self.assertEqual("우근위대장", module.CANONICAL_KO_BY_DISPLAY_ID[16410])
        self.assertEqual("참의", module.CANONICAL_KO_BY_DISPLAY_ID[16413])
        self.assertEqual("정이대장군", module.CANONICAL_KO_BY_DISPLAY_ID[16613])
        self.assertEqual(
            {
                16424: "사코노에노추조",
                16425: "사코노에곤노추조",
                16446: "사코노에노쇼쇼",
                16447: "사코노에곤노쇼쇼",
                16585: "사효에노다이조",
                16601: "사에몬노쇼조",
                16603: "사효에노쇼조",
                16613: "세이이다이쇼군",
            },
            module.JAPANESE_READING_OVERRIDES_BY_DISPLAY_ID,
        )

    def test_overlay_is_source_free_and_pairs_use_same_target(self) -> None:
        self.require_stock()
        assert self.context is not None
        overlay = module.expected_overlay(self.context)
        self.assertEqual("JP", overlay["base_language"])
        self.assertFalse(overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertFalse(overlay["distribution_policy"]["contains_complete_game_resource"])
        self.assertTrue(overlay["provenance"]["explicit_id_dictionary_used"])
        self.assertFalse(overlay["provenance"]["generic_hanja_conversion_used"])
        self.assertEqual(module.COMMON.pretty_bytes(overlay), module.OVERLAY_PATH.read_bytes())
        targets = module.target_by_coordinate(self.context.table.texts)
        for display_id in module.SCOPE_DISPLAY_IDS:
            self.assertEqual(module.CANONICAL_KO_BY_DISPLAY_ID[display_id], targets[display_id][2])
        for entry in overlay["entries"]:
            self.assertNotIn("source_jp", entry)
            self.assertNotIn("baseline_ko", entry)
            self.assertEqual(targets[entry["id"]][2], entry["ko"])
        self.assertEqual(module.TARGET_CONTRACT_COUNT, overlay["target_contract_count"])
        for contract in overlay["target_contracts"]:
            self.assertNotIn("source_jp", contract)
            self.assertNotIn("baseline_ko", contract)
            self.assertEqual(targets[contract["id"]][2], contract["ko"])
        self.assertEqual("관백", targets[16399][2])
        self.assertEqual("간파쿠", targets[16670][2])
        self.assertEqual("우대신", targets[16402][2])
        self.assertEqual("우다이진", targets[16673][2])
        self.assertEqual("대납언", targets[16404][2])
        self.assertEqual("다이나곤", targets[16675][2])
        self.assertEqual("정이대장군", targets[16613][2])
        self.assertEqual("세이이다이쇼군", targets[16884][2])

    def test_initial_v08_baseline_and_candidate_are_pinned(self) -> None:
        self.require_stock()
        assert self.context is not None
        self.assertEqual(module.WAVE08_MSGDATA_BASELINE_PIN, module.packed_spec(self.context.packed))
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate))
        composed, composed_metrics = module.apply_to_packed(
            module.DEFAULT_STOCK_ROOT, self.context.packed
        )
        self.assertEqual(candidate, composed)
        self.assertEqual(module.WAVE08_MSGDATA_BASELINE_PIN, composed_metrics["input_baseline"])
        self.assertEqual(module.EXPECTED_CHANGED_DISPLAY_COUNT, metrics["translation"]["changed_display_count"])
        self.assertEqual(module.EXPECTED_CHANGED_READING_COUNT, metrics["translation"]["changed_reading_count"])
        self.assertEqual(module.EXPECTED_CHANGED_ENTRY_COUNT, metrics["translation"]["changed_entry_count"])
        self.assertEqual("우대신", metrics["anchors"]["16402"])
        self.assertEqual("우다이진", metrics["anchors"]["16673"])
        self.assertEqual("관백", metrics["anchors"]["16399"])
        self.assertEqual("간파쿠", metrics["anchors"]["16670"])
        self.assertEqual("대납언", metrics["anchors"]["16404"])
        self.assertEqual("다이나곤", metrics["anchors"]["16675"])
        self.assertEqual("정이대장군", metrics["anchors"]["16613"])
        self.assertEqual("세이이다이쇼군", metrics["anchors"]["16884"])

    def test_all_pairs_canonical_and_non_targets_preserved(self) -> None:
        self.require_stock()
        candidate, metrics = module.build_blob(module.DEFAULT_STOCK_ROOT)
        _header, raw = module.COMMON.decompress_wrapper(candidate)
        texts = module.COMMON.parse_message_table(raw).texts
        assert self.context is not None
        changed = {entry["id"] for entry in module.load_overlay(self.context)[0]["entries"]}
        targets = module.target_by_coordinate(self.context.table.texts)
        for display_id, korean in module.CANONICAL_KO_BY_DISPLAY_ID.items():
            self.assertEqual(korean, texts[display_id])
            self.assertEqual(targets[display_id + module.PAIR_OFFSET][2], texts[display_id + module.PAIR_OFFSET])
        for entry_id, baseline in enumerate(self.context.table.texts):
            if entry_id not in changed:
                self.assertEqual(baseline, texts[entry_id])
        self.assertTrue(metrics["proofs"]["only_rows_requiring_target_output_changed"])
        self.assertTrue(metrics["proofs"]["all_146_display_rows_canonical_korean"])
        self.assertTrue(metrics["proofs"]["all_146_reading_rows_japanese_hangul"])

    def test_composable_api_preserves_later_non_targets_and_rejects_target_drift(self) -> None:
        self.require_stock()
        assert self.context is not None
        non_target_id = 15_000
        self.assertNotIn(non_target_id, module.target_by_coordinate(self.context.table.texts))
        later_texts = list(self.context.table.texts)
        later_texts[non_target_id] = later_texts[non_target_id] + "·후속"
        later_raw = module.COMMON.rebuild_message_table(self.context.table, later_texts)
        later_packed = module.COMMON.recompress_wrapper(later_raw, self.context.packed)
        candidate, metrics = module.apply_to_packed(module.DEFAULT_STOCK_ROOT, later_packed)
        _header, raw = module.COMMON.decompress_wrapper(candidate)
        texts = module.COMMON.parse_message_table(raw).texts
        self.assertEqual(later_texts[non_target_id], texts[non_target_id])
        self.assertEqual(module.packed_spec(later_packed), metrics["input_baseline"])
        self.assertTrue(metrics["proofs"]["all_292_target_contracts_fail_closed"])
        self.assertTrue(metrics["proofs"]["later_baseline_target_hashes_fail_closed"])
        self.assertTrue(metrics["proofs"]["same_source_free_delta_applied"])

        drifted_texts = list(self.context.table.texts)
        drifted_texts[16402] = "변조"
        drifted_raw = module.COMMON.rebuild_message_table(self.context.table, drifted_texts)
        drifted_packed = module.COMMON.recompress_wrapper(drifted_raw, self.context.packed)
        with self.assertRaises(module.OfficeTitlesCoreError):
            module.apply_to_packed(module.DEFAULT_STOCK_ROOT, drifted_packed)

    def test_verify_is_read_only_and_matches_validation(self) -> None:
        self.require_stock()
        result = module.verify(module.DEFAULT_STOCK_ROOT)
        self.assertEqual("PASS", result["status"])
        self.assertTrue(result["deterministic_ab_equal"])
        self.assertEqual(self.before, (self.stock.stat().st_size, digest(self.stock)))
        self.assertEqual([], list(HERE.glob("*.bin")))
        validation, blob = module.COMMON.read_json(module.VALIDATION_PATH)
        self.assertEqual(module.validation_model(result), validation)
        self.assertEqual(module.COMMON.pretty_bytes(validation), blob)

    def test_build_writes_only_a_new_tmp_candidate(self) -> None:
        self.require_stock()
        scratch = Path(tempfile.mkdtemp(prefix="office-titles-core-v1-", dir=module.REPO / "tmp"))
        target_root = scratch / "candidate"
        try:
            destination = module.build(module.DEFAULT_STOCK_ROOT, target_root)
            self.assertEqual(target_root.resolve(), destination)
            candidate = destination / Path(module.RESOURCE)
            self.assertTrue(candidate.is_file())
            self.assertEqual(module.OUTPUT_CANDIDATE_PIN, module.packed_spec(candidate.read_bytes()))
            self.assertTrue((destination / "private_manifest.json").is_file())
        finally:
            shutil.rmtree(scratch, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
