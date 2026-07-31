from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
BUILDER_PATH = WORKSTREAM_ROOT / "build_runtime_combination_particle_spacing_fix_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("runtime_combination_particle_spacing_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime-combination builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class RuntimeCombinationParticleSpacingFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_root = builder.DEFAULT_INPUT_ROOT
        if not cls.input_root.is_dir():
            raise unittest.SkipTest(f"private v0.90 target unavailable: {cls.input_root}")
        with tempfile.TemporaryDirectory() as temporary:
            cls.candidate_root = Path(temporary) / "candidate"
            cls.manifest = builder.build(cls.input_root, cls.candidate_root)
            cls.files = {
                resource: (cls.candidate_root / resource).read_bytes()
                for resource in builder.RESOURCE_PINS
            }
            cls.validation = json.loads(
                (cls.candidate_root / "validation.v1.json").read_text(encoding="utf-8")
            )

    def test_exact_output_hashes_and_changed_ids(self) -> None:
        self.assertTrue(self.manifest["passed"])
        for resource, pins in builder.RESOURCE_PINS.items():
            packed = self.files[resource]
            self.assertEqual(pins["output"]["packed_size"], len(packed))
            self.assertEqual(
                pins["output"]["packed_sha256"],
                hashlib.sha256(packed).hexdigest().upper(),
            )
            record = next(item for item in self.manifest["resources"] if item["resource"] == resource)
            self.assertEqual(pins["changed_ids"], record["changed_ids"])

    def test_result_templates_are_particle_safe(self) -> None:
        for resource in ("MSG/JP/ev_strdata.bin", "MSG_PK/JP/msgev.bin"):
            _, raw = builder.decompress_wrapper(self.files[resource])
            table = builder.parse_message_table(raw)
            changed = builder.RESOURCE_PINS[resource]["changed_ids"]
            self.assertEqual("%s 사망", table.texts[changed[0]])
            self.assertEqual("%s에 의한 %s 제압", table.texts[changed[1]])
            self.assertEqual("%s에 의한 %s 제압", table.texts[changed[2]])

    def test_surname_components_end_in_one_ascii_space(self) -> None:
        resource = "MSG_PK/JP/msgdata.bin"
        _, raw = builder.decompress_wrapper(self.files[resource])
        table = builder.parse_message_table(raw)
        self.assertEqual("나쓰메 ", table.texts[3319])
        self.assertEqual("쓰카하라 ", table.texts[3323])
        self.assertFalse(table.texts[3319].endswith("  "))
        self.assertFalse(table.texts[3323].endswith("  "))

    def test_static_analysis_contract_and_examples(self) -> None:
        evidence = json.loads(builder.STATIC_EVIDENCE_PATH.read_text(encoding="utf-8"))
        runtime = evidence["message_runtime"]
        self.assertEqual("0x141C01D20", runtime["global_message_manager"])
        self.assertEqual("0x1409F7490", runtime["evaluate_message_id"])
        self.assertEqual("0x140A00FC0", runtime["select_record"])
        self.assertEqual("0x1409F7610", runtime["decode_to_utf16"])
        self.assertEqual(
            ["다케다 가문에 의한 후타마타성 제압", "나쓰메 히로쓰구 사망"],
            evidence["expected_runtime_examples"],
        )

    def test_build_is_deterministic_and_does_not_write_to_steam(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = root / "a"
            second = root / "b"
            builder.build(self.input_root, first)
            builder.build(self.input_root, second)
            for resource in builder.RESOURCE_PINS:
                self.assertEqual((first / resource).read_bytes(), (second / resource).read_bytes())
            self.assertFalse(json.loads((first / "validation.v1.json").read_text(encoding="utf-8"))["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
