from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave58_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_composite_wave58_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import W58 builder")
wave58 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave58
SPEC.loader.exec_module(wave58)


class PrivateUnionCompositeWave58Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = wave58.load_sources()
        cls.component_diffs, cls.component_counts = wave58.load_component_diffs(cls.sources)
        cls.bundle = wave58.prepare(require_output_profiles=True)

    def test_exact_component_and_final_counts(self) -> None:
        self.assertEqual(
            self.component_counts,
            {
                "wave56": {
                    "MSG/JP/msggame.bin": 67,
                    "MSG_PK/JP/msggame.bin": 198,
                    "MSG_PK/JP/msgdata.bin": 4,
                    "MSG_PK/JP/msgev.bin": 91,
                },
                "b00_b05": {"MSG/JP/msggame.bin": 5, "MSG_PK/JP/msggame.bin": 3},
                "b07_b10": {"MSG/JP/msggame.bin": 3, "MSG_PK/JP/msggame.bin": 3},
                "b11_b13": {"MSG/JP/msggame.bin": 2, "MSG_PK/JP/msggame.bin": 6},
            },
        )
        actual = {resource: len(changed) for resource, changed in self.bundle.merged.items()}
        self.assertEqual(actual, wave58.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(actual.values()), 381)
        self.assertEqual(self.bundle.audit["overlap_count"], 1)
        self.assertEqual(
            self.bundle.overlaps,
            (
                {
                    "resource": "MSG_PK/JP/msggame.bin",
                    "coordinate": [9, 4113],
                    "previous_component": "wave56",
                    "incoming_component": "b07_b10",
                    "resolution": "same_payload_already_in_wave56",
                },
            ),
        )

    def test_incremental_dialogue_coordinates_are_all_present(self) -> None:
        base = self.bundle.merged["MSG/JP/msggame.bin"]
        pk = self.bundle.merged["MSG_PK/JP/msggame.bin"]
        self.assertTrue({(2, 88), (2, 89), (2, 93), (2, 105), (2, 106), (9, 3640), (9, 3776), (9, 3796), (13, 258), (13, 260)}.issubset(base))
        self.assertTrue({(2, 99), (2, 111), (2, 112), (9, 4094), (9, 4113), (9, 4114), (13, 260), (13, 262), (13, 353), (13, 452), (13, 575), (13, 615)}.issubset(pk))
        self.assertTrue(
            wave58.core.record_literal_texts(base[(2, 93)], (2, 93))[0].startswith("저도 원복…아니, 성인식을 마쳤기에")
        )
        self.assertEqual(wave58.core.record_literal_texts(pk[(9, 4113)], (9, 4113))[0], "복병이 있었다! 혼란한 틈에 쳐부수자!")
        self.assertIn("헌언", wave58.core.record_literal_texts(pk[(13, 452)], (13, 452))[0])

    def test_rebuilt_files_change_only_merged_records(self) -> None:
        for resource in wave58.core.RESOURCES:
            with self.subTest(resource=resource.relative):
                source = self.sources[resource.relative]
                output = self.bundle.outputs[resource.relative]
                if resource.kind == "msggame":
                    before = wave58.core.record_map(source.parsed)
                    after = wave58.core.record_map(wave58.core.msggame.parse_packed_msggame(output).archive)
                    actual = {key: after[key] for key in before if before[key] != after[key]}
                else:
                    _header, raw = wave58.core.decompress_wrapper(output)
                    table = wave58.core.parse_message_table(raw)
                    actual = {index: table.texts[index] for index, text in enumerate(source.parsed.texts) if text != table.texts[index]}
                self.assertEqual(actual, self.bundle.merged[resource.relative])
                self.assertEqual(wave58.core.profile(output), wave58.EXPECTED_OUTPUT_PROFILES[resource.relative])

    def test_duplicate_component_coordinate_fails(self) -> None:
        duplicate = {component.name: {} for component in wave58.COMPONENTS}
        duplicate["wave56"] = {"MSG_PK/JP/msggame.bin": {(2, 99): b"first"}}
        duplicate["b00_b05"] = {"MSG_PK/JP/msggame.bin": {(2, 99): b"second"}}
        with self.assertRaises(wave58.UnionError):
            wave58.merge_diffs(duplicate)

    def test_private_guard_and_non_apply_policy(self) -> None:
        self.assertEqual(wave58.candidate_root().parent, wave58.TMP_ROOT)
        with self.assertRaises(wave58.UnionError):
            wave58.require_private(wave58.REPO, "repo")
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
