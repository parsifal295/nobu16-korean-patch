from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_dialogue_quality_wave39_static_dialogue_v1.py"
SPEC = importlib.util.spec_from_file_location("wave39_static_dialogue_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 39 static dialogue builder")
wave39 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave39
SPEC.loader.exec_module(wave39)


class Wave39StaticDialogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave39.prepare_candidate()
        cls.before = {resource: wave39.W27.records_by_coordinate(path.read_bytes()) for resource, path in wave39.RESOURCE_PATHS.items()}
        cls.after = {resource: wave39.W27.records_by_coordinate(packed) for resource, packed in cls.bundle.packed.items()}

    def test_exact_static_scope(self) -> None:
        self.assertEqual(len(wave39.CHANGES), 41)
        self.assertEqual(sum(change.resource == wave39.BASE_RESOURCE for change in wave39.CHANGES), 14)
        self.assertEqual(sum(change.resource == wave39.PK_RESOURCE for change in wave39.CHANGES), 27)
        self.assertEqual(self.bundle.audit["changed_record_count"], 41)
        self.assertEqual(self.bundle.audit["base_display_qa_required_coordinates"], ["6:4039", "6:4045"])
        self.assertEqual(self.bundle.audit["pk_display_qa_required_coordinates"], ["9:3880"])

    def test_pc_only_source_contract(self) -> None:
        policy = self.bundle.audit["source_policy"]
        self.assertTrue(policy["pc_jp_en_sc_tc_only"])
        self.assertFalse(policy["switch_korean_read"])
        for path, _hash in wave39.W37.PC_SOURCES.values():
            self.assertNotIn("switch", str(path).casefold())

    def test_only_declared_records_change(self) -> None:
        for resource in wave39.RESOURCE_PATHS:
            with self.subTest(resource=resource):
                changed = {coordinate for coordinate in self.before[resource] if self.before[resource][coordinate].data != self.after[resource][coordinate].data}
                expected = {change.coordinate for change in wave39.CHANGES if change.resource == resource}
                self.assertEqual(changed, expected)
                self.assertEqual(set(self.before[resource]), set(self.after[resource]))

    def test_static_structure_and_manual_linebreaks(self) -> None:
        advance, _font = wave39.W27.load_font_advance()
        for change in wave39.CHANGES:
            with self.subTest(change=change.name):
                before = self.before[change.resource][change.coordinate]
                after = self.after[change.resource][change.coordinate]
                self.assertEqual(len(wave39.W27.literal_texts(before)), len(change.target_literals))
                self.assertEqual(wave39.W27.literal_texts(after), change.target_literals)
                self.assertEqual(wave39.W27.opaque_spans(after), wave39.W27.opaque_spans(before))
                self.assertEqual(wave39.W27.marker_topology(after), wave39.W27.marker_topology(before))
                self.assertFalse(wave39.W27.complete_0143_commands(wave39.W27.opaque_spans(before)))
                self.assertFalse(any(span.startswith(b"\x02") for span in wave39.W27.opaque_spans(before)))
                self.assertEqual("".join(wave39.W27.literal_texts(before)).count("\n"), "".join(change.target_literals).count("\n"))
                layout = wave39.W27.line_layout(change.target_literals, advance)
                self.assertEqual(layout["wide_fallback_codepoints"], [])

    def test_pinned_profiles_and_private_guard(self) -> None:
        for resource, packed in self.bundle.packed.items():
            with self.subTest(resource=resource):
                target = wave39.TARGET_PROFILES[resource]
                self.assertEqual(len(packed), target["size"])
                self.assertEqual(wave39.sha256_bytes(packed), target["sha256"])
                self.assertEqual(len(self.bundle.raw[resource]), target["raw_size"])
                self.assertEqual(wave39.sha256_bytes(self.bundle.raw[resource]), target["raw_sha256"])
        with self.assertRaises(wave39.Wave39Error):
            wave39.require_private(wave39.REPO, "repository root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
