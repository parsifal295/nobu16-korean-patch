from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


WORKSTREAM_ROOT = Path(__file__).resolve().parents[1]
BUILDER_PATH = WORKSTREAM_ROOT / "build_runtime_event_result_template_fix_v2.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("runtime_event_result_template_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime-event-result builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


builder = load_builder()


class RuntimeEventResultTemplateFixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.input_root = builder.DEFAULT_INPUT_ROOT
        if not cls.input_root.is_dir():
            raise unittest.SkipTest(f"private v0.90 target unavailable: {cls.input_root}")
        cls.temporary = tempfile.TemporaryDirectory()
        cls.candidate_root = Path(cls.temporary.name) / "candidate"
        cls.manifest = builder.build(cls.input_root, cls.candidate_root)
        cls.tables = {}
        for resource in builder.RESOURCE_PINS:
            packed = (cls.candidate_root / resource).read_bytes()
            _, raw = builder.decompress_wrapper(packed)
            cls.tables[resource] = builder.parse_message_table(raw)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temporary.cleanup()

    def test_exact_output_hashes_and_changed_ids(self) -> None:
        self.assertTrue(self.manifest["passed"])
        for resource, pins in builder.RESOURCE_PINS.items():
            packed = (self.candidate_root / resource).read_bytes()
            self.assertEqual(pins["output"]["packed_size"], len(packed))
            self.assertEqual(
                pins["output"]["packed_sha256"],
                hashlib.sha256(packed).hexdigest().upper(),
            )
            record = next(item for item in self.manifest["resources"] if item["resource"] == resource)
            self.assertEqual(pins["changed_ids"], record["changed_ids"])

    def test_base_and_pk_template_sets_match_semantically(self) -> None:
        base = self.tables["MSG/JP/ev_strdata.bin"]
        pk = self.tables["MSG_PK/JP/msgev.bin"]
        pairs = [
            (17302, 17344),
            (17303, 17345),
            (17308, 17350),
            (17316, 17358),
            (17319, 17361),
            (17321, 17363),
            (17339, 17381),
            (17340, 17382),
            (17344, 17386),
            (17345, 17387),
            (17346, 17388),
            (17347, 17389),
            (17350, 17392),
            (17351, 17393),
            (17378, 17420),
            (17410, 17452),
            (17464, 17508),
            (17478, 17522),
            (17482, 17526),
            (17626, 17672),
            (17627, 17673),
            (17645, 17691),
            (17663, 17709),
            (17664, 17710),
            (17668, 17714),
            (17670, 17716),
            (17671, 17717),
            (17674, 17720),
        ]
        for base_id, pk_id in pairs:
            self.assertEqual(base.texts[base_id], pk.texts[pk_id])

    def test_reported_outputs_render_naturally(self) -> None:
        table = self.tables["MSG_PK/JP/msgev.bin"]
        rendered = {
            table.texts[17392] % ("마쓰다이라 기요야스", "마쓰다이라 히로타다"),
            table.texts[17363] % ("마쓰다이라 가문", "이마가와 가문"),
            table.texts[17393] % "아시카가 하루나오",
            table.texts[17345] % ("오우치 가문", "모리 가문"),
            table.texts[17386] % ("다자카 젠케이", "모리 가문"),
            table.texts[17350] % ("오다 가문", "기요스성"),
            table.texts[17452] % ("다케다 하루노부", "다케다 신겐"),
        }
        self.assertEqual(
            {
                "당주 승계(전임: 마쓰다이라 기요야스 / 후임: 마쓰다이라 히로타다)",
                "마쓰다이라 가문, 이마가와 가문에 종속",
                "아시카가 하루나오 해임",
                "오우치 가문 멸망, 소속 무장들이 모리 가문에 합류",
                "다자카 젠케이 사망(모리 가문 소속 시)",
                "오다 가문 본거 이전: 기요스성",
                "개명 전: 다케다 하루노부 / 개명 후: 다케다 신겐",
            },
            rendered,
        )

    def test_all_rows_preserve_printf_token_sequence(self) -> None:
        overlay = json.loads(builder.OVERLAY_PATH.read_text(encoding="utf-8"))
        grouped = builder.validate_overlay(overlay)
        for resource, entries in grouped.items():
            packed = (builder.DEFAULT_INPUT_ROOT / resource).read_bytes()
            _, raw = builder.decompress_wrapper(packed)
            source = builder.parse_message_table(raw)
            for entry in entries:
                self.assertEqual(
                    [],
                    builder.invariant_mismatches(
                        source.texts[entry["id"]],
                        entry["ko"],
                        allow_edge_whitespace_change=entry["allow_edge_whitespace_change"],
                    ),
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
            validation = json.loads((first / "validation.v2.json").read_text(encoding="utf-8"))
            self.assertFalse(validation["steam_write_performed"])


if __name__ == "__main__":
    unittest.main()
