from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_event_static_quality_wave49_v1.py"
SPEC = importlib.util.spec_from_file_location("wave49_static_quality_builder", BUILDER)
if SPEC is None or SPEC.loader is None:  # pragma: no cover
    raise RuntimeError("cannot import Wave 49 builder")
wave49 = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = wave49
SPEC.loader.exec_module(wave49)


EXPECTED_IDS = [
    3240,
    3897,
    3949,
    3951,
    3953,
    3954,
    3957,
    6235,
    6343,
    6419,
    6724,
    6863,
    6911,
    6913,
    6925,
    6929,
    7033,
    7332,
    7525,
    7559,
    7562,
    7577,
    7940,
    7985,
    8026,
    8032,
    8615,
    8626,
    9148,
    9447,
    9470,
    9491,
    9540,
]


class Wave49StaticQualityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bundle = wave49.prepare_candidate()
        cls.before = wave49.load_table(
            wave49.STEAM_PK_EVENT,
            wave49.W45_INPUT_PROFILE,
            wave49.INPUT_RECORD_COUNT,
            "W45 Steam PK input",
            require_packed_round_trip=True,
        )
        _header, raw = wave49.decompress_wrapper(cls.bundle.packed)
        cls.after = wave49.parse_message_table(raw)

    def test_exact_static_scope_and_holds(self) -> None:
        self.assertEqual([change.entry_id for change in wave49.CHANGES], EXPECTED_IDS)
        self.assertEqual(len(wave49.CHANGES), 33)
        self.assertEqual(len(wave49.SEMANTIC_OR_REFLOW_HOLD), 25)
        self.assertEqual(len(wave49.TAG_INTERNAL_LINEBREAK_HOLD), 46)
        self.assertEqual(len(wave49.COLOR_ESCAPE_QA_HOLD), 25)
        self.assertEqual(wave49.NON_EVENT_PERSON_NAME_HOLD, (291, 292, 293))
        held = set().union(*(set(values) for values in wave49.hold_sets().values()))
        self.assertTrue(set(EXPECTED_IDS).isdisjoint(held))

    def test_only_declared_records_change(self) -> None:
        changed = [
            index
            for index, (before, after) in enumerate(zip(self.before.table.texts, self.after.texts))
            if before != after
        ]
        self.assertEqual(changed, EXPECTED_IDS)

    def test_token_tag_linebreak_and_width_contract(self) -> None:
        width = wave49.load_width_utility()
        advance, _font = width.load_event_font()
        for change in wave49.CHANGES:
            with self.subTest(entry_id=change.entry_id):
                before = self.before.table.texts[change.entry_id]
                after = self.after.texts[change.entry_id]
                self.assertEqual(width.protected_signature(before), width.protected_signature(after))
                widths = width.line_widths(after, advance)
                self.assertGreaterEqual(len(widths), 1)
                self.assertLessEqual(len(widths), 3)
                self.assertLessEqual(max(widths), wave49.PK_MAX_LINE_PX)

    def test_pinned_profiles_and_record_binding(self) -> None:
        self.assertEqual(
            wave49.sha256_bytes(self.bundle.packed),
            wave49.W49_OUTPUT_PROFILE.sha256,
        )
        self.assertEqual(len(self.bundle.packed), wave49.W49_OUTPUT_PROFILE.size)
        self.assertEqual(
            wave49.sha256_bytes(self.bundle.raw),
            wave49.W49_OUTPUT_PROFILE.raw_sha256,
        )
        self.assertEqual(len(self.bundle.raw), wave49.W49_OUTPUT_PROFILE.raw_size)
        self.assertEqual(self.bundle.audit["record_binding_sha256"], wave49.RECORD_BINDING_SHA256)
        self.assertEqual(len(self.bundle.audit["records"]), 33)
        self.assertEqual(
            [record["id"] for record in self.bundle.audit["records"]],
            EXPECTED_IDS,
        )
        self.assertEqual(
            self.bundle.manifest["audit_sha256"],
            wave49.sha256_bytes(wave49.canonical_json(self.bundle.audit)),
        )

    def test_pc_jp_record_evidence_is_bound(self) -> None:
        evidence = self.bundle.audit["pc_jp_evidence"]
        self.assertEqual(evidence["sha256"], wave49.LEGACY_PC_JP_PROFILE.sha256)
        self.assertEqual(
            evidence["legacy_to_steam_mapping_sha256"],
            wave49.STEAM_JP_MAPPING_SHA256,
        )
        for record in self.bundle.audit["records"]:
            with self.subTest(entry_id=record["id"]):
                self.assertEqual(record["legacy_jp_id"], record["id"])
                self.assertTrue(record["pc_jp_anchors"])
                self.assertEqual(len(record["pc_jp_utf16le_sha256"]), 64)
                self.assertEqual(len(record["current_utf16le_sha256"]), 64)
                self.assertEqual(len(record["target_utf16le_sha256"]), 64)

    def test_private_output_guard(self) -> None:
        with self.assertRaises(wave49.Wave49Error):
            wave49.require_private(wave49.REPO, "repository")


if __name__ == "__main__":
    unittest.main(verbosity=2)
