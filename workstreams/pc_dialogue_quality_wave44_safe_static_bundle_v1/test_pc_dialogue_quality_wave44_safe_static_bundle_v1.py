from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave44_safe_static_bundle_v1.py"
SPEC = importlib.util.spec_from_file_location("wave44_safe_static_bundle_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 44 builder")
wave44 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave44
SPEC.loader.exec_module(wave44)


class Wave44SafeStaticBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave44.prepare_candidate()
        cls.before = {
            resource: wave44.W27.records_by_coordinate(path.read_bytes())
            for resource, path in wave44.RESOURCE_PATHS.items()
        }
        cls.after = {
            resource: wave44.W27.records_by_coordinate(packed)
            for resource, packed in cls.bundle.packed.items()
        }

    def test_exact_conservative_scope(self) -> None:
        self.assertEqual(len(wave44.CHANGES), 51)
        self.assertEqual(sum(change.resource == wave44.BASE_RESOURCE for change in wave44.CHANGES), 13)
        self.assertEqual(sum(change.resource == wave44.PK_RESOURCE for change in wave44.CHANGES), 38)
        self.assertEqual(wave44.EXCLUDED_REAL_GAME_QA["wave32_pk_boundary"], ["7:2482", "15:2279"])
        self.assertEqual(wave44.EXCLUDED_NON_ERROR_CLARITY["wave35"], ["17:938"])

    def test_only_declared_records_change(self) -> None:
        for resource, before in self.before.items():
            with self.subTest(resource=resource):
                after = self.after[resource]
                changed = {coordinate for coordinate in before if before[coordinate].data != after[coordinate].data}
                expected = {change.coordinate for change in wave44.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)
                self.assertEqual(set(before), set(after))

    def test_safe_records_preserve_structure_and_stay_below_boundary(self) -> None:
        advance, _font = wave44.W27.load_font_advance()
        for change in wave44.CHANGES:
            with self.subTest(change=(change.resource, change.coordinate)):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(wave44.W27.opaque_spans(after), wave44.W27.opaque_spans(before))
                self.assertEqual(wave44.W27.marker_topology(after), wave44.W27.marker_topology(before))
                self.assertEqual("".join(wave44.W27.literal_texts(before)).count("\n"), "".join(wave44.W27.literal_texts(after)).count("\n"))
                layout = wave44.W27.line_layout(wave44.W27.literal_texts(after), advance)
                self.assertLess(layout["max_width_px"], wave44.MAX_SAFE_LINE_PX_EXCLUSIVE)
                self.assertLessEqual(layout["line_count"], 3)

    def test_profiles_and_private_guard(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                profile = wave44.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), profile["size"])
                self.assertEqual(wave44.W39.sha256_bytes(packed), profile["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), profile["raw_size"])
                self.assertEqual(wave44.W39.sha256_bytes(self.bundle.raw[resource]), profile["raw_sha256"])
        with self.assertRaises(wave44.Wave44Error):
            wave44.require_private(wave44.REPO, "repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
