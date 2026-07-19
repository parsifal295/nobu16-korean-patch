from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_quality_wave42_safe_static_bundle_v1.py"
SPEC = importlib.util.spec_from_file_location("wave42_safe_static_bundle_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 42 builder")
wave42 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave42
SPEC.loader.exec_module(wave42)


class Wave42SafeStaticBundleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave42.prepare_candidate()
        cls.before = {key: wave42.W31.load_table(spec, key) for key, spec in wave42.W31.RESOURCES.items()}
        cls.after = {}
        for key, packed in cls.bundle.packed.items():
            _header, raw = wave42.W31.decompress_wrapper(packed)
            cls.after[key] = wave42.W31.parse_message_table(raw)

    def test_exact_safe_scope(self) -> None:
        self.assertEqual(len(wave42.CHANGES), 26)
        self.assertEqual(sum(change.resource == "base" for change in wave42.CHANGES), 8)
        self.assertEqual(sum(change.resource == "pk" for change in wave42.CHANGES), 18)
        self.assertEqual(wave42.EXCLUDED_DISPLAY_QA["wave31"]["pk"], [3898, 5528])
        self.assertEqual(wave42.EXCLUDED_DISPLAY_QA["wave33"]["base"], [6772, 6941, 8776, 8803, 8947, 9292])
        self.assertEqual(wave42.EXCLUDED_DISPLAY_QA["wave33"]["pk"], [6772])

    def test_only_declared_cells_change(self) -> None:
        for key, before in self.before.items():
            with self.subTest(resource=key):
                changed = [index for index, (left, right) in enumerate(zip(before.table.texts, self.after[key].texts)) if left != right]
                expected = sorted(change.entry_id for change in wave42.CHANGES if change.resource == key)
                self.assertEqual(changed, expected)

    def test_no_layout_or_control_topology_change(self) -> None:
        advance, _font = wave42.W31.load_event_font()
        for change in wave42.CHANGES:
            with self.subTest(change=(change.resource, change.entry_id)):
                before = self.before[change.resource].table.texts[change.entry_id]
                after = self.after[change.resource].texts[change.entry_id]
                self.assertEqual(wave42.W31.protected_signature(before), wave42.W31.protected_signature(after))
                widths = wave42.W31.line_widths(after, advance)
                self.assertLessEqual(len(widths), 3)
                if change.resource == "pk":
                    self.assertLessEqual(max(widths), wave42.PK_MAX_LINE_PX)

    def test_profiles_and_private_guard(self) -> None:
        for key, packed in self.bundle.packed.items():
            with self.subTest(resource=key):
                profile = wave42.TARGET_PROFILES[key]
                self.assertEqual(len(packed), profile["size"])
                self.assertEqual(wave42.W31.sha256_bytes(packed), profile["sha256"])
                self.assertEqual(len(self.bundle.raw[key]), profile["raw_size"])
                self.assertEqual(wave42.W31.sha256_bytes(self.bundle.raw[key]), profile["raw_sha256"])
        with self.assertRaises(wave42.Wave42Error):
            wave42.require_private(wave42.REPO, "repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
