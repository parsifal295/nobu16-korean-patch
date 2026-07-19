#!/usr/bin/env python3
"""Independent checks for the private direct-PC B17 static candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_b17_direct_static_candidate_v2.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("b17_direct_static_candidate_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B17 direct static candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class B17DirectStaticCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = load_builder()
        cls.bundle = cls.m.prepare_candidate()

    def test_exact_scope_and_holds(self) -> None:
        observed = tuple((target.resource, *target.slot) for target in self.m.TARGETS)
        self.assertEqual(observed, self.m.EXPECTED_SCOPE)
        self.assertEqual(len(observed), 44)
        self.assertEqual(self.bundle.audit["changed_literal_count"], 44)
        self.assertEqual(self.bundle.audit["changed_record_count"], 44)
        self.assertEqual(
            self.bundle.audit["changed_literal_count_by_resource"],
            {self.m.BASE_RESOURCE: 4, self.m.PK_RESOURCE: 40},
        )
        self.assertEqual(
            self.bundle.audit["changed_record_count_by_resource"],
            {self.m.BASE_RESOURCE: 4, self.m.PK_RESOURCE: 40},
        )
        self.assertTrue(set(observed).isdisjoint(self.m.EXCLUDED_HOLD_SLOTS))
        for hold in self.m.EXCLUDED_HOLD_SLOTS:
            self.assertNotIn(hold, observed)

    def test_exact_w45_preimages_complete_targets_and_pc_jp(self) -> None:
        audit_rows = {
            (row["resource"], row["slot"]): row for row in self.bundle.audit["records"]
        }
        for target in self.m.TARGETS:
            source = self.bundle.sources[target.resource]
            block, record, literal = target.slot
            current = self.m.parse_record_literals(source.archive.blocks[block].records[record])[literal].text
            jp_text = self.m.parse_record_literals(source.jp_archive.blocks[block].records[record])[literal].text
            self.assertEqual(current, target.current_ko)
            self.assertEqual(jp_text, target.pc_jp)
            self.assertNotEqual(target.current_ko, target.target_ko)
            self.assertEqual(
                self.m.literal_signature(target.current_ko),
                self.m.literal_signature(target.target_ko),
            )
            row = audit_rows[(target.resource, target.slot_text)]
            self.assertEqual(row["current_ko"], target.current_ko)
            self.assertEqual(row["target_ko"], target.target_ko)
            self.assertEqual(row["pc_jp"], target.pc_jp)
            self.assertEqual(
                row["current_ko_utf16le_sha256"],
                self.m.text_hash(target.current_ko),
            )
            self.assertEqual(
                row["target_ko_utf16le_sha256"],
                self.m.text_hash(target.target_ko),
            )

    def test_token_adjacent_scope_is_literal_only(self) -> None:
        rows = {
            (row["resource"], row["slot"]): row for row in self.bundle.audit["records"]
        }
        for slot in ("17:950:0", "17:951:0", "17:952:0"):
            row = rows[(self.m.PK_RESOURCE, slot)]
            self.assertEqual(row["target_ko"], "선봉 ")
        self.assertEqual(
            rows[(self.m.PK_RESOURCE, "17:971:0")]["target_ko"],
            "차륜진으로 간다, 먼저 선봉끼리 맞붙어라\n그 뒤 적의 본진…　",
        )
        for hold in (
            (self.m.PK_RESOURCE, 17, 226, 1),
            (self.m.PK_RESOURCE, 17, 510, 2),
            (self.m.PK_RESOURCE, 17, 920, 1),
            (self.m.PK_RESOURCE, 17, 991, 1),
            (self.m.PK_RESOURCE, 17, 282, 0),
        ):
            self.assertNotIn(hold, {(target.resource, *target.slot) for target in self.m.TARGETS})

    def test_whole_archive_target_only_and_control_scope(self) -> None:
        for resource in self.m.RESOURCE_ORDER:
            source = self.bundle.sources[resource]
            candidate = self.bundle.resources[resource]
            allowed_literals = {
                target.slot for target in self.m.TARGETS if target.resource == resource
            }
            allowed_records = {(block, record) for block, record, _ in allowed_literals}
            observed_literals = set()
            observed_records = set()
            self.assertEqual(len(source.archive.blocks), len(candidate.archive.blocks))
            for before_block, after_block in zip(source.archive.blocks, candidate.archive.blocks):
                self.assertEqual(before_block.block_id, after_block.block_id)
                self.assertEqual(len(before_block.records), len(after_block.records))
                for before, after in zip(before_block.records, after_block.records):
                    coordinate = (before.block_id, before.record_id)
                    if before.data != after.data:
                        observed_records.add(coordinate)
                        self.assertIn(coordinate, allowed_records)
                        self.assertEqual(
                            self.m.opaque_skeleton(before),
                            self.m.opaque_skeleton(after),
                        )
                    else:
                        self.assertNotIn(coordinate, allowed_records)
                    for old, new in zip(
                        self.m.parse_record_literals(before),
                        self.m.parse_record_literals(after),
                    ):
                        slot = (before.block_id, before.record_id, old.literal_id)
                        if old.text != new.text:
                            observed_literals.add(slot)
                            self.assertIn(slot, allowed_literals)
                            self.assertEqual(
                                self.m.literal_signature(old.text),
                                self.m.literal_signature(new.text),
                            )
                        else:
                            self.assertNotIn(slot, allowed_literals)
            self.assertEqual(observed_literals, allowed_literals)
            self.assertEqual(observed_records, allowed_records)

    def test_parser_round_trip_and_pinned_output_profiles(self) -> None:
        self.assertEqual(set(self.m.EXPECTED_OUTPUT_PROFILES), set(self.m.RESOURCE_ORDER))
        for resource in self.m.RESOURCE_ORDER:
            candidate = self.bundle.resources[resource]
            _header, raw = self.m.decompress_wrapper(candidate.packed)
            self.assertEqual(raw, candidate.raw)
            archive = self.m.parse_raw_msggame(raw)
            self.assertEqual(self.m.rebuild_raw_msggame(archive), raw)
            self.assertEqual(
                self.m.decompress_wrapper(self.m.rebuild_packed_msggame(candidate.packed))[1],
                raw,
            )
            self.m.require_profile(
                candidate.packed,
                candidate.raw,
                self.m.EXPECTED_OUTPUT_PROFILES[resource],
                resource,
            )

    def test_manifest_and_private_guards(self) -> None:
        self.assertEqual(
            self.m.sha256_bytes(self.m.canonical_json(self.bundle.audit)),
            self.bundle.manifest["audit_sha256"],
        )
        self.assertTrue(self.bundle.audit["candidate_only"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])
        accepted = self.m.require_private(self.m.TMP_ROOT / "candidate-test", "test private")
        self.assertTrue(accepted.is_relative_to(self.m.TMP_ROOT.resolve(strict=False)))
        with self.assertRaises(self.m.CandidateError):
            self.m.require_private(self.m.REPO / "outside-private", "outside")


if __name__ == "__main__":
    unittest.main(verbosity=2)
