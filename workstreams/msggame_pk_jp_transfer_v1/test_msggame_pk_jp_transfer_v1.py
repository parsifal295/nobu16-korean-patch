#!/usr/bin/env python3
"""Tests for the native-JP and SC-container-mirror msggame adapters."""

from __future__ import annotations

import argparse
import collections
import copy
import sys
import tempfile
import unittest
from pathlib import Path

WORKSTREAM_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_msggame_pk_jp_transfer_v1 as transfer


class MsggamePkJpTransferV1Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        private_sources = (
            transfer.DEFAULT_SC,
            transfer.DEFAULT_JP,
            transfer.DEFAULT_TC,
            transfer.DEFAULT_EN,
        )
        if not all(path.exists() for path in private_sources):
            raise unittest.SkipTest("pinned private PK multilingual msggame inputs are unavailable")
        cls.catalog = transfer.collect_overlay_inputs(transfer.DEFAULT_PROGRESS)
        cls.sc = transfer.load_source(transfer.DEFAULT_SC, "SC")
        cls.jp = transfer.load_source(transfer.DEFAULT_JP, "JP")
        cls.tc = transfer.load_source(transfer.DEFAULT_TC, "TC")
        cls.en = transfer.load_source(transfer.DEFAULT_EN, "EN")
        cls.classified = transfer.classify_entries(
            cls.sc, cls.jp, cls.tc, cls.en, cls.catalog
        )
        cls.root = transfer.WORKSTREAM_ROOT
        cls.recipe_path = cls.root / "public" / transfer.RECIPE_NAME
        cls.mirror_recipe_path = cls.root / "public" / transfer.MIRROR_RECIPE_NAME
        cls.evidence_path = cls.root / "evidence" / transfer.EVIDENCE_NAME
        cls.review_path = cls.root / "review" / transfer.REVIEW_NAME
        cls.validation_path = cls.root / transfer.VALIDATION_NAME
        cls.readme_path = transfer.README_PATH
        cls.recipe = transfer.read_json(cls.recipe_path)
        cls.mirror_recipe = transfer.read_json(cls.mirror_recipe_path)
        cls.evidence = transfer.read_json(cls.evidence_path)
        cls.review = transfer.read_json(cls.review_path)
        cls.validation = transfer.read_json(cls.validation_path)

    def test_cumulative_catalog_and_exact_native_partition(self) -> None:
        self.assertEqual(34, len(self.catalog["inputs"]))
        self.assertEqual(11_722, len(self.catalog["entries"]))
        self.assertEqual(7_449, len(self.classified["direct"]))
        self.assertEqual(861, len(self.classified["remapped"]))
        self.assertEqual(8_310, len(self.classified["transferable"]))
        self.assertEqual(3_412, len(self.classified["blocked"]))
        self.assertEqual(
            {
                "jp_coordinate_missing": 251,
                "jp_invariant_mismatch": 446,
                "record_literal_count_mismatch": 2_438,
                "record_skeleton_mismatch": 277,
            },
            self.classified["primary_reasons"],
        )
        self.assertEqual(
            {
                "jp_coordinate_missing": 251,
                "jp_invariant_mismatch": 2_146,
                "record_literal_count_mismatch": 2_438,
                "record_skeleton_mismatch": 2_715,
            },
            self.classified["nonexclusive_reasons"],
        )
        expected_ui = {
            "workstreams/msggame_pk_ui_priority_b05/public/msggame_ko_pk_ui_priority_b05_300.v1.json": {
                "blocked": 276,
                "transferable": 24,
            },
            "workstreams/msggame_pk_ui_priority_b06/public/msggame_ko_pk_ui_priority_b06_300.v1.json": {
                "blocked": 194,
                "remapped": 24,
                "transferable": 82,
            },
            "workstreams/msggame_pk_ui_priority_b07/public/msggame_ko_pk_ui_priority_b07_300.v1.json": {
                "blocked": 251,
                "remapped": 11,
                "transferable": 38,
            },
        }
        for path, counts in expected_ui.items():
            self.assertEqual(counts, self.classified["origin_counts"][path])
        self.assertEqual(144, sum(row.get("transferable", 0) for row in expected_ui.values()))
        self.assertEqual(35, sum(row.get("remapped", 0) for row in expected_ui.values()))
        self.assertEqual(721, sum(row["blocked"] for row in expected_ui.values()))

    def test_native_recipe_source_target_mapping_and_four_language_anchors(self) -> None:
        entries = transfer._validate_recipe_root(self.recipe)
        self.assertEqual(8_310, len(entries))
        methods = collections.Counter(entry["mapping_method"] for entry in entries)
        self.assertEqual(
            {
                "direct_coordinate_equal_record_structure": 7_449,
                "same_record_equal_cardinality_ordinal_marker_offset_remap": 861,
            },
            methods,
        )
        for entry in entries:
            coordinate = (entry["block_id"], entry["record_id"], entry["literal_id"])
            self.assertEqual(list(coordinate), entry["source_sc_coordinate"])
            literal = self.jp["literals"][coordinate]
            record = self.jp["records"][coordinate[:2]]
            self.assertEqual(transfer.text_hash(literal.text), entry["source_jp_utf16le_sha256"])
            self.assertEqual(
                transfer.record_structure_hash(record), entry["jp_record_structure_sha256"]
            )
            self.assertEqual(
                len(transfer.msggame.parse_record_literals(record)),
                entry["jp_record_literal_count"],
            )
            self.assertEqual([], transfer.common.invariant_mismatches(literal.text, entry["ko"]))
            transfer.validate_utf16_capacity(entry["ko"], coordinate=coordinate)
        remap_evidence = [
            item for item in self.evidence["entries"] if item["status"] == "remapped"
        ]
        self.assertEqual(861, len(remap_evidence))
        for item in remap_evidence:
            mapping = item["mapping"]
            self.assertEqual("exact_unique", mapping["confidence"])
            self.assertEqual(1, mapping["candidate_target_count"])
            self.assertEqual(["EN", "JP", "SC", "TC"], sorted(mapping["context"]))
            self.assertNotEqual(
                item["sc_record_structure_sha256"], item["jp_record_structure_sha256"]
            )
            self.assertEqual(item["sc_record_literal_count"], item["jp_record_literal_count"])

    def test_native_in_memory_ab_candidate_and_non_recipe_preservation(self) -> None:
        candidate, manifest = transfer.apply_recipe_blob(self.jp["packed"], self.recipe)
        self.assertEqual(1_651_697, len(candidate))
        self.assertEqual(transfer.EXPECTED_NATIVE_PACKED_SHA256, transfer.sha256(candidate))
        self.assertEqual(8_310, manifest["entry_count"])
        self.assertEqual(1_645_220, manifest["capacity"]["predicted_raw_size"])
        self.assertEqual(
            {
                "direct_coordinate_equal_record_structure": 7_449,
                "same_record_equal_cardinality_ordinal_marker_offset_remap": 861,
            },
            manifest["mapping_counts"],
        )
        self.assertTrue(all(manifest["checks"].values()))
        self.assertFalse(manifest["installed_game_file_written"])

    def test_sc_container_mirror_preserves_all_11722_entries(self) -> None:
        candidate, manifest = transfer.apply_mirror_recipe_blob(
            self.sc["packed"], self.jp["packed"], self.catalog, self.mirror_recipe
        )
        self.assertEqual(1_269_018, len(candidate))
        self.assertEqual(transfer.EXPECTED_MIRROR_PACKED_SHA256, transfer.sha256(candidate))
        self.assertEqual(11_722, manifest["entry_count"])
        self.assertEqual(11_717, manifest["changed_literal_count"])
        self.assertEqual(21_581, manifest["candidate"]["record_count"])
        self.assertEqual(25_598, manifest["candidate"]["literal_slot_count"])
        self.assertEqual(1_264_036, manifest["capacity"]["predicted_raw_size"])
        self.assertTrue(all(manifest["checks"].values()))
        self.assertFalse(manifest["installed_game_file_written"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        expected = {
            self.recipe_path: "A33070DE401B83F025DCC3B5EECEEEAC52F199C0EF4AF0E9C847F6EECB7E053D",
            self.mirror_recipe_path: "93CF4FCB6B1DAC93DED1A3A2208BDF7AEB3EDED1619524F76BA9D3916F27B7E5",
            self.evidence_path: "8F886B525C24C35F19D3E11E3135CDE3CCAE5AF21A44C71A5614AC5138657478",
            self.review_path: "A730AA90D5F0F4CB0BB9241BC251A0529F29596C30D840DF69805714E4071A40",
            self.validation_path: "B42652470759E7FEF2A8AADF9A8F7D10CE0E193C3A2ED30573461B8DDE9D6C28",
            self.readme_path: "0CC0CF47D82B807DB22A573F83ACEE00077C35061FFB1E8D757A4CFA9B50E984",
        }
        for path, digest in expected.items():
            self.assertEqual(digest, transfer.sha256(path.read_bytes()))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                transfer.script_counts(path.read_text(encoding="utf-8")),
            )
        self.assertTrue(self.validation["passed"])
        self.assertEqual(3_412, self.review["blocked_count"])
        self.assertEqual(3_412, len(self.review["entries"]))
        self.assertTrue(self.review["mirror_route_preserves_all_input_entries"])
        self.assertEqual(
            transfer.RUNTIME_VALIDATION_STATE,
            self.validation["runtime_validation"]["state"],
        )
        self.assertFalse(self.validation["runtime_validation"]["release_ready"])
        readme = self.readme_path.read_text(encoding="utf-8")
        self.assertIn("런타임 미검증", readme)
        self.assertIn("릴리스 준비 완료로 취급하면 안 된다", readme)

    def test_fail_closed_native_and_mirror_tampering(self) -> None:
        first = self.recipe["entries"][0]
        for mutation in ("false", "extra", "missing"):
            with self.subTest(native_adapter_policy=mutation):
                tampered = copy.deepcopy(self.recipe)
                if mutation == "false":
                    tampered["adapter_policy"]["coordinate_must_exist_in_jp"] = False
                elif mutation == "extra":
                    tampered["adapter_policy"]["unreviewed_override"] = True
                else:
                    del tampered["adapter_policy"]["coordinate_must_exist_in_jp"]
                with self.assertRaisesRegex(transfer.TransferError, "adapter_policy"):
                    transfer.apply_recipe_blob(self.jp["packed"], tampered)

        for mutation in ("false", "extra", "missing"):
            with self.subTest(mirror_container_policy=mutation):
                tampered = copy.deepcopy(self.mirror_recipe)
                key = "preserve_sc_record_directory_and_literal_coordinates"
                if mutation == "false":
                    tampered["container_policy"][key] = False
                elif mutation == "extra":
                    tampered["container_policy"]["unreviewed_override"] = True
                else:
                    del tampered["container_policy"][key]
                with self.assertRaisesRegex(transfer.TransferError, "container_policy"):
                    transfer.apply_mirror_recipe_blob(
                        self.sc["packed"], self.jp["packed"], self.catalog, tampered
                    )

        tampered = copy.deepcopy(self.recipe)
        tampered["entries"][0]["source_jp_utf16le_sha256"] = "0" * 64
        with self.assertRaisesRegex(transfer.TransferError, "source text hash mismatch"):
            transfer.apply_recipe_blob(self.jp["packed"], tampered)

        tampered = copy.deepcopy(self.recipe)
        tampered["entries"][0]["mapping_method"] = "guessed"
        with self.assertRaisesRegex(transfer.TransferError, "unsupported mapping method"):
            transfer.apply_recipe_blob(self.jp["packed"], tampered)

        tampered = copy.deepcopy(self.recipe)
        tampered["entries"][0]["ko"] = first["ko"] + "\n"
        with self.assertRaisesRegex(transfer.TransferError, "control/layout invariant mismatch"):
            transfer.apply_recipe_blob(self.jp["packed"], tampered)

        corrupted_stock = bytearray(self.jp["packed"])
        corrupted_stock[-1] ^= 1
        with self.assertRaisesRegex(transfer.TransferError, "packed JP source pin mismatch"):
            transfer.apply_recipe_blob(bytes(corrupted_stock), self.recipe)

        mirror_tampered = copy.deepcopy(self.mirror_recipe)
        mirror_tampered["expected_candidate"]["packed_sha256"] = "0" * 64
        with self.assertRaisesRegex(transfer.TransferError, "candidate digest or structure changed"):
            transfer.apply_mirror_recipe_blob(
                self.sc["packed"], self.jp["packed"], self.catalog, mirror_tampered
            )
        with self.assertRaisesRegex(transfer.TransferError, "JP target guard mismatch"):
            transfer.apply_mirror_recipe_blob(
                self.sc["packed"], bytes(corrupted_stock), self.catalog, self.mirror_recipe
            )

        with self.assertRaisesRegex(transfer.TransferError, "UTF-16 literal capacity"):
            transfer.validate_utf16_capacity("가", limit=1)
        with self.assertRaisesRegex(transfer.TransferError, "not valid UTF-16"):
            transfer.validate_utf16_capacity("\ud800")

    def test_private_staging_root_is_exact_and_live_paths_fail_closed(self) -> None:
        with self.assertRaisesRegex(transfer.TransferError, "explicit absolute"):
            transfer.validate_private_staging_root(Path("relative-stage"))
        for protected in (
            transfer.GAME_ROOT / "unsafe-stage",
            transfer.GAME_ROOT / "NOBU16PK.exe",
            transfer.DEFAULT_JP,
            transfer.REPO_ROOT / "unsafe-stage",
        ):
            with self.subTest(protected=protected):
                with self.assertRaisesRegex(
                    transfer.TransferError, "outside GAME_ROOT|binary or executable"
                ):
                    transfer.validate_private_staging_root(protected)

        parser_destinations = {action.dest for action in transfer.parser()._actions}
        self.assertIn("private_staging_root", parser_destinations)
        self.assertNotIn("private_candidate_out", parser_destinations)
        self.assertNotIn("private_mirror_candidate_out", parser_destinations)

        with tempfile.TemporaryDirectory(prefix="nobu16-stage-guard-") as temp_root:
            temp = Path(temp_root)
            with self.assertRaisesRegex(transfer.TransferError, "binary or executable"):
                transfer.validate_private_staging_root(temp / "arbitrary.bin")
            arbitrary_file = temp / "arbitrary-output"
            arbitrary_file.write_bytes(b"file")
            with self.assertRaisesRegex(transfer.TransferError, "directory, not a file"):
                transfer.validate_private_staging_root(arbitrary_file)

            occupied = temp / "occupied"
            occupied.mkdir()
            (occupied / "unrelated.txt").write_text("not managed", encoding="utf-8")
            with self.assertRaisesRegex(transfer.TransferError, "unexpected file"):
                transfer.validate_private_staging_root(occupied)

            link_target = temp / "link-target"
            link_target.mkdir()
            stage_link = temp / "stage-link"
            try:
                stage_link.symlink_to(link_target, target_is_directory=True)
            except OSError:
                pass
            else:
                with self.assertRaisesRegex(transfer.TransferError, "cannot be a symlink"):
                    transfer.validate_private_staging_root(stage_link)

            stage = temp / "isolated-stage"
            root, native, mirror = transfer.validate_private_staging_root(stage)
            self.assertEqual(stage.resolve(), root)
            self.assertEqual(transfer.NATIVE_STAGE_RELATIVE, native.relative_to(root))
            self.assertEqual(transfer.MIRROR_STAGE_RELATIVE, mirror.relative_to(root))
            result = transfer.write_private_candidates(stage, b"native", b"mirror")
            self.assertTrue(result["exact_layout"])
            files = {
                path.relative_to(stage.resolve())
                for path in stage.rglob("*")
                if path.is_file()
            }
            self.assertEqual(
                {transfer.NATIVE_STAGE_RELATIVE, transfer.MIRROR_STAGE_RELATIVE}, files
            )

    def test_build_is_deterministic_private_ab_and_all_inputs_are_read_only(self) -> None:
        input_paths = [
            transfer.DEFAULT_SC,
            transfer.DEFAULT_JP,
            transfer.DEFAULT_TC,
            transfer.DEFAULT_EN,
            transfer.DEFAULT_PROGRESS,
        ]
        input_paths += [transfer.REPO_ROOT / item["path"] for item in self.catalog["inputs"]]
        before = {path: transfer.sha256(path.read_bytes()) for path in input_paths}
        expected = {
            "public/" + transfer.RECIPE_NAME: transfer.sha256(self.recipe_path.read_bytes()),
            "public/" + transfer.MIRROR_RECIPE_NAME: transfer.sha256(
                self.mirror_recipe_path.read_bytes()
            ),
            "evidence/" + transfer.EVIDENCE_NAME: transfer.sha256(self.evidence_path.read_bytes()),
            "review/" + transfer.REVIEW_NAME: transfer.sha256(self.review_path.read_bytes()),
            transfer.VALIDATION_NAME: transfer.sha256(self.validation_path.read_bytes()),
        }
        with tempfile.TemporaryDirectory(prefix="nobu16-jp-transfer-") as temp_root:
            temp = Path(temp_root)
            out_root = temp / "artifacts"
            staging_root = temp / "private-stage"
            native_out = staging_root / transfer.NATIVE_STAGE_RELATIVE
            mirror_out = staging_root / transfer.MIRROR_STAGE_RELATIVE
            args = argparse.Namespace(
                pk_sc=transfer.DEFAULT_SC,
                pk_jp=transfer.DEFAULT_JP,
                pk_tc=transfer.DEFAULT_TC,
                pk_en=transfer.DEFAULT_EN,
                progress=transfer.DEFAULT_PROGRESS,
                out_root=out_root,
                private_staging_root=staging_root,
            )
            result = transfer.build(args)
            actual = {
                relative: transfer.sha256((out_root / relative).read_bytes())
                for relative in expected
            }
            self.assertEqual(transfer.EXPECTED_NATIVE_PACKED_SHA256, transfer.sha256(native_out.read_bytes()))
            self.assertEqual(transfer.EXPECTED_MIRROR_PACKED_SHA256, transfer.sha256(mirror_out.read_bytes()))
            self.assertTrue(result["private_candidate_written"])
            self.assertTrue(result["private_mirror_candidate_written"])
            self.assertFalse(any(path.suffix == ".bin" for path in out_root.rglob("*")))
        self.assertEqual(expected, actual)
        self.assertEqual(before, {path: transfer.sha256(path.read_bytes()) for path in input_paths})


if __name__ == "__main__":
    unittest.main(verbosity=2)
