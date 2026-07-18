from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_private_union_composite_wave53_v1.py"
SPEC = importlib.util.spec_from_file_location("pc_private_union_composite_wave53_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover - import guard
    raise RuntimeError("cannot import Wave 53 private union builder")
wave53 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave53
SPEC.loader.exec_module(wave53)


class PrivateUnionCompositeWave53Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave53.prepare_candidate()
        cls.msggame_baselines, cls.table_baselines, cls.w45_audit = wave53.load_w45_baselines()

    def test_exact_component_and_union_counts(self) -> None:
        self.assertEqual(
            [component.workstream for component in self.bundle.components],
            [
                "pc_static_composite_wave52_v1",
                "pc_block15_runtime_candidate_v1",
                "pc_npc_name_quality_wave50_v1",
                "pc_event_color_tag_reflow_v1",
            ],
        )
        self.assertEqual(sum(component.changed_record_count for component in self.bundle.components), 289)
        self.assertEqual(
            {resource: len(coordinates) for resource, coordinates in self.bundle.union_coordinates.items()},
            {
                wave53.BASE_MSGGAME: 67,
                wave53.PK_MSGGAME: 166,
                wave53.PK_MSGDATA: 4,
                wave53.PK_EVENT: 52,
            },
        )
        self.assertEqual(self.bundle.manifest["changed_record_count"], 289)
        self.assertEqual(self.bundle.audit["union"]["changed_record_count"], 289)

    def test_pinned_w45_inputs_and_union_targets(self) -> None:
        self.assertEqual(self.w45_audit["schema"], wave53.W45_AUDIT_SCHEMA)
        self.assertEqual(self.w45_audit["component_builder_sha256"], wave53.W45_COMPONENT_BUILDERS)
        for resource, payload in self.bundle.files.items():
            with self.subTest(resource=resource):
                _header, _raw, profile = wave53.inspect_packed(payload, f"test union {resource}")
                self.assertEqual(profile, wave53.UNION_TARGET_PROFILES[resource])
                self.assertEqual(self.bundle.manifest["w45_inputs"][resource], wave53.profile_dict(wave53.W45_PROFILES[resource]))
                self.assertEqual(self.bundle.manifest["outputs"][resource], wave53.profile_dict(wave53.UNION_TARGET_PROFILES[resource]))

    def test_rebuilt_files_change_only_union_coordinates(self) -> None:
        for resource, payload in self.bundle.files.items():
            with self.subTest(resource=resource):
                actual = wave53.changed_coordinates_from_file(
                    resource,
                    payload,
                    self.msggame_baselines,
                    self.table_baselines,
                )
                self.assertEqual(actual, self.bundle.union_coordinates[resource])

    def test_component_scopes_are_disjoint(self) -> None:
        seen: set[tuple[str, object]] = set()
        for component in self.bundle.components:
            for resource, coordinates in component.changed_coordinates.items():
                for coordinate in coordinates:
                    key = (resource, coordinate)
                    self.assertNotIn(key, seen)
                    seen.add(key)
        self.assertEqual(len(seen), 289)

    def test_holds_never_enter_union(self) -> None:
        self.assertEqual(self.bundle.held_coordinates[wave53.BASE_MSGGAME], ((15, 1121),))
        self.assertEqual(
            self.bundle.held_coordinates[wave53.PK_EVENT],
            (3202, 3900, 3934, 3956, 4140, 8510, 8723, 9359, 10045),
        )
        for resource, held in self.bundle.held_coordinates.items():
            for coordinate in held:
                with self.subTest(resource=resource, coordinate=coordinate):
                    self.assertNotIn(coordinate, self.bundle.union_coordinates[resource])

    def test_component_hash_bindings_are_exact(self) -> None:
        specs = {spec.workstream: spec for spec in wave53.COMPONENT_SPECS}
        for binding in self.bundle.components:
            with self.subTest(component=binding.workstream):
                spec = specs[binding.workstream]
                self.assertEqual(binding.builder_sha256, spec.builder_sha256)
                self.assertEqual(binding.candidate_manifest_sha256, spec.candidate_manifest_sha256)
                self.assertEqual(binding.component_audit_sha256, spec.component_audit_sha256)

    def test_private_source_and_output_guards(self) -> None:
        self.assertTrue(wave53.require_private_source(wave53.W45_BASELINE_ROOT, "W45").is_dir())
        for spec in wave53.COMPONENT_SPECS:
            with self.subTest(component=spec.workstream):
                self.assertTrue(wave53.require_private_source(spec.candidate_root, spec.workstream).is_dir())
        with self.assertRaises(wave53.CompositeError):
            wave53.require_private_output(wave53.REPO, "repo")

    def test_duplicate_coordinate_registration_is_rejected_even_for_equal_payload(self) -> None:
        component = self.bundle.components[0]
        coordinate = component.changed_coordinates[wave53.BASE_MSGGAME][0]
        replacements: dict[str, dict[object, object]] = {}
        provenance: dict[str, dict[object, str]] = {}
        wave53.register_replacements(
            replacements,
            provenance,
            component,
            {wave53.BASE_MSGGAME: {coordinate: b"same"}},
        )
        with self.assertRaises(wave53.CompositeError):
            wave53.register_replacements(
                replacements,
                provenance,
                component,
                {wave53.BASE_MSGGAME: {coordinate: b"same"}},
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
