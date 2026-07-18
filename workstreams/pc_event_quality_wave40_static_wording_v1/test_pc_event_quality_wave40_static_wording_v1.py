from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_quality_wave40_static_wording_v1.py"
SPEC = importlib.util.spec_from_file_location("wave40_static_wording_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 40 builder")
wave40 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave40
SPEC.loader.exec_module(wave40)


class Wave40StaticWordingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave40.prepare_candidate()
        cls.before, _sources = wave40.load_tables()
        cls.after = {}
        for key, packed in cls.bundle.packed.items():
            _header, raw = wave40.W31.decompress_wrapper(packed)
            cls.after[key] = wave40.W31.parse_message_table(raw)

    def test_exact_scope(self) -> None:
        self.assertEqual(len(wave40.CHANGES), 5)
        self.assertEqual(sum(change.resource == "base" for change in wave40.CHANGES), 1)
        self.assertEqual(sum(change.resource == "pk" for change in wave40.CHANGES), 4)
        self.assertEqual(self.bundle.audit["changed_cell_count"], 5)

    def test_only_declared_cells_change(self) -> None:
        for key, before in self.before.items():
            with self.subTest(resource=key):
                changed = [index for index, (left, right) in enumerate(zip(before.table.texts, self.after[key].texts)) if left != right]
                expected = [change.entry_id for change in wave40.CHANGES if change.resource == key]
                self.assertEqual(changed, expected)

    def test_controls_and_linebreaks_are_preserved(self) -> None:
        for change in wave40.CHANGES:
            with self.subTest(change=change.entry_id):
                before = self.before[change.resource].table.texts[change.entry_id]
                after = self.after[change.resource].texts[change.entry_id]
                self.assertEqual(wave40.W31.protected_signature(before), wave40.W31.protected_signature(after))

    def test_profiles_and_private_guard(self) -> None:
        for key, packed in self.bundle.packed.items():
            with self.subTest(resource=key):
                profile = wave40.TARGET_PROFILES[key]
                self.assertEqual(len(packed), profile["size"])
                self.assertEqual(wave40.W31.sha256_bytes(packed), profile["sha256"])
                self.assertEqual(len(self.bundle.raw[key]), profile["raw_size"])
                self.assertEqual(wave40.W31.sha256_bytes(self.bundle.raw[key]), profile["raw_sha256"])
        with self.assertRaises(wave40.Wave40Error):
            wave40.require_private(wave40.REPO, "repo")


if __name__ == "__main__":
    unittest.main(verbosity=2)
