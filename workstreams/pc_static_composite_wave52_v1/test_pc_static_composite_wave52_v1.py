from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_static_composite_wave52_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_static_composite_wave52_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import Wave 52 static composite builder")
wave52 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave52
SPEC.loader.exec_module(wave52)


class StaticCompositeWave52Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave52.prepare_candidate()

    def test_exact_component_and_union_counts(self) -> None:
        self.assertEqual(len(self.bundle.components), 6)
        self.assertEqual(
            [component.name for component in self.bundle.components],
            [
                "wave47_battle_dialogue_static",
                "wave48_static_ui_0143",
                "wave49_event_static",
                "wave50_dialogue_static_blocks9_12",
                "wave51_tutorial_static_blocks13_14",
                "wave51_terminal_static_0143",
            ],
        )
        self.assertEqual(sum(component.changed_record_count for component in self.bundle.components), 249)
        self.assertEqual(
            {resource: len(coordinates) for resource, coordinates in self.bundle.union_coordinates.items()},
            {
                wave52.BASE_MSGGAME: 59,
                wave52.PK_MSGGAME: 157,
                wave52.PK_EVENT: 33,
            },
        )
        self.assertEqual(self.bundle.manifest["changed_record_count"], 249)
        self.assertEqual(self.bundle.audit["union"]["changed_record_count"], 249)

    def test_w45_inputs_and_target_profiles_are_pinned(self) -> None:
        for resource, payload in self.bundle.files.items():
            with self.subTest(resource=resource):
                _header, _raw, profile = wave52.inspect_packed(payload, f"test union {resource}")
                self.assertEqual(profile, wave52.UNION_TARGET_PROFILES[resource])
                self.assertEqual(
                    self.bundle.manifest["w45_inputs"][resource],
                    wave52.profile_dict(wave52.W45_PROFILES[resource]),
                )
                self.assertEqual(
                    self.bundle.manifest["outputs"][resource],
                    wave52.profile_dict(wave52.UNION_TARGET_PROFILES[resource]),
                )

    def test_rebuilt_files_change_only_the_union_coordinates(self) -> None:
        baselines = {
            wave52.BASE_MSGGAME: wave52.load_msggame_baseline(wave52.BASE_MSGGAME),
            wave52.PK_MSGGAME: wave52.load_msggame_baseline(wave52.PK_MSGGAME),
        }
        for resource, baseline in baselines.items():
            with self.subTest(resource=resource):
                records = wave52.W27.records_by_coordinate(self.bundle.files[resource])
                actual = tuple(
                    sorted(
                        coordinate
                        for coordinate, record in records.items()
                        if record.data != baseline.records[coordinate].data
                    )
                )
                self.assertEqual(actual, self.bundle.union_coordinates[resource])

        event_baseline = wave52.load_event_baseline()
        _header, raw, _profile = wave52.inspect_packed(self.bundle.files[wave52.PK_EVENT], "test union event")
        event_table = wave52.parse_message_table(raw)
        actual_event_ids = tuple(
            index
            for index, text in enumerate(event_table.texts)
            if text != event_baseline.table.texts[index]
        )
        self.assertEqual(actual_event_ids, self.bundle.union_coordinates[wave52.PK_EVENT])

    def test_component_scopes_are_disjoint_and_w46_is_absent(self) -> None:
        seen: set[tuple[str, object]] = set()
        for component in self.bundle.components:
            for resource, coordinates in component.changed_coordinates.items():
                for coordinate in coordinates:
                    key = (resource, coordinate)
                    self.assertNotIn(key, seen)
                    seen.add(key)
        self.assertEqual(len(seen), 249)
        self.assertEqual(
            self.bundle.manifest["excluded_component_workstreams"],
            ["pc_dialogue_runtime_repair_wave46_v1"],
        )
        self.assertNotIn("pc_dialogue_runtime_repair_wave46_v1", [component.workstream for component in self.bundle.components])

    def test_private_guard_and_policy(self) -> None:
        with self.assertRaises(wave52.CompositeError):
            wave52.require_private(wave52.REPO, "repo")
        policy = self.bundle.audit["source_policy"]
        self.assertEqual(policy["switch_korean_input"], "forbidden")
        self.assertFalse(policy["steam_game_resource_written"])
        self.assertEqual(policy["steam_apply_or_transaction_capability"], "absent")
        self.assertEqual(policy["git_operation_capability"], "absent")
        self.assertEqual(policy["network_capability"], "absent")
        self.assertEqual(policy["release_capability"], "absent")

    def test_duplicate_coordinate_registration_is_rejected(self) -> None:
        component = self.bundle.components[0]
        replacements: dict[str, dict[object, object]] = {}
        provenance: dict[str, dict[object, str]] = {}
        coordinate = component.changed_coordinates[wave52.PK_MSGGAME][0]
        payload = b"first"
        wave52.register_replacements(
            replacements,
            provenance,
            component,
            {wave52.PK_MSGGAME: {coordinate: payload}},
        )
        with self.assertRaises(wave52.CompositeError):
            wave52.register_replacements(
                replacements,
                provenance,
                component,
                {wave52.PK_MSGGAME: {coordinate: payload}},
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
