from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parents[1]
BUILDER_PATH = WORKSTREAM / "build_hanja_furigana_v0140.py"
APPLIER_PATH = WORKSTREAM / "apply_hanja_furigana_v0140.py"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import {name}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class HanjaFuriganaTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.builder = load_module("hanja_furigana_builder_test", BUILDER_PATH)
        cls.applier = load_module("hanja_furigana_applier_test", APPLIER_PATH)

    def test_initial_sound_examples(self):
        convert = self.builder.apply_initial_sound_rule
        self.assertEqual(convert(" ", "리"), "이")
        self.assertEqual(convert(" ", "녀"), "여")
        self.assertEqual(convert(" ", "뢰"), "뇌")
        self.assertEqual(convert("나", "률"), "율")
        self.assertEqual(convert("각", "률"), "률")

    def test_reviewed_variant_readings(self):
        select = self.builder.select_hanja_reading
        self.assertEqual(select(chr(0x6E13), {}), "계")
        self.assertEqual(select(chr(0x697D), {}), "락")
        self.assertEqual(select(chr(0x4E80), {}), "구")
        self.assertEqual(select(chr(0x82B8), {}), "예")
        self.assertEqual(select(chr(0x8336), {}), "차")
        self.assertEqual(select(chr(0x8A3C), {}), "증")
        self.assertEqual(self.builder.apply_initial_sound_rule(" ", "락"), "낙")

    def test_tracked_public_ledger_has_complete_scope(self):
        public_path = WORKSTREAM / "public" / "hanja_furigana_v0140.operations.json"
        validation_path = WORKSTREAM / "validation.v1.json"
        self.assertTrue(public_path.is_file(), "run the builder to refresh the public ledger")
        public = json.loads(public_path.read_text(encoding="utf-8"))
        validation = json.loads(validation_path.read_text(encoding="utf-8"))
        self.assertEqual(public["schema"], self.builder.SCHEMA)
        self.assertTrue(public["source_free"])
        self.builder.assert_source_free(public)
        self.builder.assert_source_free(validation)
        by_resource = {item["resource"]: item for item in public["resources"]}
        self.assertEqual(by_resource[self.builder.PK_RESOURCE]["operation_count"], 4569)
        self.assertEqual(by_resource[self.builder.BASE_RESOURCE]["operation_count"], 4556)
        self.assertEqual(validation["pair_counts"]["combined_operation_count"], 9125)
        pk = {item["id"]: item["replacement"] for item in by_resource[self.builder.PK_RESOURCE]["operations"]}
        base = {item["id"]: item["replacement"] for item in by_resource[self.builder.BASE_RESOURCE]["operations"]}
        self.assertEqual(pk[3416], "직전")
        self.assertEqual(pk[4598], "신장")
        self.assertEqual(base[3416], "직전")
        self.assertEqual(base[4598], "신장")
        for resource in by_resource.values():
            for operation in resource["operations"]:
                self.assertRegex(operation["replacement"], r"^[가-힣]+$")
                self.assertFalse(any(character.isspace() for character in operation["replacement"]))

    def test_build_is_deterministic_and_steam_is_read_only(self):
        args = self.builder.parse_args([])
        with tempfile.TemporaryDirectory() as first_name, tempfile.TemporaryDirectory() as second_name:
            first = Path(first_name)
            second = Path(second_name)
            args.output_root = first
            first_result = self.builder.build(args)
            args.output_root = second
            second_result = self.builder.build(args)
            self.assertEqual(
                first_result["pk_operations"], second_result["pk_operations"]
            )
            self.assertEqual(
                first_result["base_operations"], second_result["base_operations"]
            )
            self.assertEqual(
                Path(first_result["public"]).read_bytes(),
                Path(second_result["public"]).read_bytes(),
            )

    def test_public_ledger_replays_to_the_builder_candidates(self):
        source_paths = [
            self.builder.DEFAULT_STEAM_ROOT / self.builder.PK_RESOURCE,
            self.builder.DEFAULT_STEAM_ROOT / self.builder.BASE_RESOURCE,
        ]
        before = {path: self.builder.sha256_file(path) for path in source_paths}
        with tempfile.TemporaryDirectory() as build_name, tempfile.TemporaryDirectory() as apply_name:
            build_args = self.builder.parse_args([])
            build_args.output_root = Path(build_name)
            built = self.builder.build(build_args)
            apply_args = self.applier.parse_args(["--output-root", apply_name])
            applied = self.applier.apply(apply_args)
            self.assertEqual(
                Path(built["candidate_pk"]).read_bytes(),
                Path(applied["candidate_pk"]).read_bytes(),
            )
            self.assertEqual(
                Path(built["candidate_base"]).read_bytes(),
                Path(applied["candidate_base"]).read_bytes(),
            )
            report = json.loads(Path(applied["report"]).read_text(encoding="utf-8"))
            self.assertTrue(report["source_free"])
            self.assertFalse(report["steam_root_written"])
        self.assertEqual(before, {path: self.builder.sha256_file(path) for path in source_paths})

    def test_applier_rejects_a_steam_output_root(self):
        args = self.applier.parse_args(["--output-root", str(self.builder.DEFAULT_STEAM_ROOT)])
        with self.assertRaises(self.applier.builder.FuriganaError):
            self.applier.apply(args)


if __name__ == "__main__":
    unittest.main()
