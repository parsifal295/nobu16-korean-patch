from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave55_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_composite_wave55_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import Wave 55 private union builder")
wave55 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave55
SPEC.loader.exec_module(wave55)


class PrivateUnionCompositeWave55Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.sources = {spec.relative: wave55.load_source(spec) for spec in wave55.RESOURCES}
        cls.component_diffs, cls.component_counts = wave55.load_component_diffs(cls.sources)
        cls.bundle = wave55.prepare(require_output_profiles=True)

    def test_exact_component_and_final_counts(self) -> None:
        self.assertEqual(
            self.component_counts,
            {
                "wave53": {
                    "MSG/JP/msggame.bin": 67,
                    "MSG_PK/JP/msggame.bin": 166,
                    "MSG_PK/JP/msgdata.bin": 4,
                    "MSG_PK/JP/msgev.bin": 52,
                },
                "event3956": {"MSG_PK/JP/msgev.bin": 1},
                "semantic8": {"MSG_PK/JP/msgev.bin": 8},
                "event_batch_a": {"MSG_PK/JP/msgev.bin": 10},
                "event_batch_b": {"MSG_PK/JP/msgev.bin": 10},
                "event_batch_c": {"MSG_PK/JP/msgev.bin": 11},
                "b17": {"MSG_PK/JP/msggame.bin": 31},
            },
        )
        final_counts = {resource: len(changes) for resource, changes in self.bundle.merged.items()}
        self.assertEqual(final_counts, wave55.EXPECTED_FINAL_RECORD_COUNTS)
        self.assertEqual(sum(final_counts.values()), 358)
        self.assertEqual(self.bundle.audit["final_total_records"], 358)
        self.assertEqual(self.bundle.manifest["final_total_records"], 358)

    def test_only_the_two_declared_overlaps_are_resolved(self) -> None:
        self.assertEqual(
            self.bundle.overlaps,
            (
                {
                    "resource": "MSG_PK/JP/msgev.bin",
                    "coordinate": 3960,
                    "previous_component": "wave53",
                    "incoming_component": "event_batch_c",
                    "resolution": "incoming_event_batch_c_replaces_wave53_name_only",
                },
                {
                    "resource": "MSG_PK/JP/msggame.bin",
                    "coordinate": [17, 1064],
                    "previous_component": "wave53",
                    "incoming_component": "b17",
                    "resolution": "keep_wave53_existing_semantic_fix_project_ellipsis_style",
                },
            ),
        )
        event = "MSG_PK/JP/msgev.bin"
        self.assertEqual(self.bundle.merged[event][3960], wave55.EVENT_3960_TARGET)
        dialogue = "MSG_PK/JP/msggame.bin"
        wave53_value = self.component_diffs["wave53"][dialogue][(17, 1064)]
        b17_value = self.component_diffs["b17"][dialogue][(17, 1064)]
        self.assertEqual(
            wave55.record_literal_texts(wave53_value, (17, 1064))[1],
            wave55.WAVE53_B17_1064_TARGET,
        )
        self.assertEqual(
            wave55.record_literal_texts(b17_value, (17, 1064))[1],
            wave55.B17_COMPONENT_1064_TARGET,
        )
        self.assertEqual(self.bundle.merged[dialogue][(17, 1064)], wave53_value)

    def test_rebuilt_files_change_only_merged_records(self) -> None:
        for spec in wave55.RESOURCES:
            with self.subTest(resource=spec.relative):
                before = self.sources[spec.relative]
                output = self.bundle.outputs[spec.relative]
                if spec.kind == "msggame":
                    after = wave55.record_map(wave55.msggame.parse_packed_msggame(output).archive)
                    baseline = wave55.record_map(before.parsed)
                    actual = {key: after[key] for key in baseline if baseline[key] != after[key]}
                else:
                    _header, raw = wave55.decompress_wrapper(output)
                    after_table = wave55.parse_message_table(raw)
                    actual = {
                        index: after_table.texts[index]
                        for index, text in enumerate(before.parsed.texts)
                        if text != after_table.texts[index]
                    }
                self.assertEqual(actual, self.bundle.merged[spec.relative])
                self.assertEqual(wave55.profile(output), wave55.EXPECTED_OUTPUT_PROFILES[spec.relative])

    def test_declared_holds_remain_at_the_w45_value(self) -> None:
        base = self.sources["MSG/JP/msggame.bin"]
        pk = self.sources["MSG_PK/JP/msggame.bin"]
        base_after = wave55.record_map(wave55.msggame.parse_packed_msggame(self.bundle.outputs["MSG/JP/msggame.bin"]).archive)
        pk_after = wave55.record_map(wave55.msggame.parse_packed_msggame(self.bundle.outputs["MSG_PK/JP/msggame.bin"]).archive)
        self.assertEqual(base_after[(15, 1121)], wave55.record_map(base.parsed)[(15, 1121)])
        self.assertEqual(pk_after[(17, 920)], wave55.record_map(pk.parsed)[(17, 920)])

    def test_private_output_guard_and_non_apply_policy(self) -> None:
        self.assertEqual(wave55.candidate_root().parent, wave55.TMP_ROOT)
        with self.assertRaises(wave55.UnionError):
            wave55.require_private(wave55.REPO, "repo")
        policy = self.bundle.audit["source_policy"]
        self.assertFalse(policy["switch_read"])
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")


if __name__ == "__main__":
    unittest.main(verbosity=2)
