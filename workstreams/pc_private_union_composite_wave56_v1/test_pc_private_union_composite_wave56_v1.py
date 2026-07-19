from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave56_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_composite_wave56_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import Wave 56 private union builder")
wave56 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave56
SPEC.loader.exec_module(wave56)


class PrivateUnionCompositeWave56Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = wave56.load_sources()
        cls.component_diffs, cls.component_counts = wave56.load_component_diffs(cls.sources)
        cls.bundle = wave56.prepare(require_output_profiles=True)

    def test_exact_component_and_final_counts(self) -> None:
        self.assertEqual(
            self.component_counts,
            {
                "wave55": {
                    "MSG/JP/msggame.bin": 67,
                    "MSG_PK/JP/msggame.bin": 196,
                    "MSG_PK/JP/msgdata.bin": 4,
                    "MSG_PK/JP/msgev.bin": 91,
                },
                "b06": {"MSG_PK/JP/msggame.bin": 2},
            },
        )
        actual = {relative: len(changed) for relative, changed in self.bundle.merged.items()}
        self.assertEqual(actual, wave56.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(actual.values()), 360)

    def test_b06_records_are_the_only_new_msggame_coordinates(self) -> None:
        resource = "MSG_PK/JP/msggame.bin"
        b06 = self.component_diffs["b06"][resource]
        self.assertEqual(set(b06), {(6, 3144), (6, 3455)})
        for coordinate, target in b06.items():
            with self.subTest(coordinate=coordinate):
                self.assertEqual(self.bundle.merged[resource][coordinate], target)
                self.assertEqual(
                    wave56.wave55.record_literal_texts(target, coordinate)[0].count("\n"),
                    wave56.wave55.record_literal_texts(
                        wave56.wave55.record_map(self.sources[resource].parsed)[coordinate], coordinate
                    )[0].count("\n"),
                )

    def test_rebuilt_files_change_only_merged_records(self) -> None:
        for resource in wave56.wave55.RESOURCES:
            with self.subTest(resource=resource.relative):
                before = self.sources[resource.relative]
                output = self.bundle.outputs[resource.relative]
                if resource.kind == "msggame":
                    before_map = wave56.wave55.record_map(before.parsed)
                    after_map = wave56.wave55.record_map(
                        wave56.wave55.msggame.parse_packed_msggame(output).archive
                    )
                    actual = {key: after_map[key] for key in before_map if before_map[key] != after_map[key]}
                else:
                    _header, raw = wave56.wave55.decompress_wrapper(output)
                    table = wave56.wave55.parse_message_table(raw)
                    actual = {
                        index: table.texts[index]
                        for index, text in enumerate(before.parsed.texts)
                        if text != table.texts[index]
                    }
                self.assertEqual(actual, self.bundle.merged[resource.relative])
                self.assertEqual(wave56.wave55.profile(output), wave56.EXPECTED_OUTPUT_PROFILES[resource.relative])

    def test_component_overlap_fails(self) -> None:
        duplicate = {
            "wave55": {"MSG_PK/JP/msggame.bin": {(6, 3144): b"first"}},
            "b06": {"MSG_PK/JP/msggame.bin": {(6, 3144): b"second"}},
        }
        with self.assertRaises(wave56.UnionError):
            wave56.merge_diffs(duplicate)

    def test_private_output_guard_and_non_apply_policy(self) -> None:
        self.assertEqual(wave56.candidate_root().parent, wave56.TMP_ROOT)
        with self.assertRaises(wave56.UnionError):
            wave56.require_private(wave56.REPO, "repo")
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
