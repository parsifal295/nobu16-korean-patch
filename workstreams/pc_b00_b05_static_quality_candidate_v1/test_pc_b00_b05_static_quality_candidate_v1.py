#!/usr/bin/env python3
"""Independent checks for the private B00~B05 PC terminology candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_b00_b05_static_quality_candidate_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("b00_b05_candidate_test_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B00~B05 candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class B00B05CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = load_builder()
        cls.bundle = cls.m.prepare_candidate()

    def test_exact_eight_literal_scope(self) -> None:
        self.assertEqual(
            tuple((target.resource, *target.slot) for target in self.m.TARGETS),
            (
                (self.m.BASE_RESOURCE, 2, 88, 1),
                (self.m.BASE_RESOURCE, 2, 89, 1),
                (self.m.BASE_RESOURCE, 2, 93, 0),
                (self.m.BASE_RESOURCE, 2, 105, 0),
                (self.m.BASE_RESOURCE, 2, 106, 0),
                (self.m.PK_RESOURCE, 2, 99, 0),
                (self.m.PK_RESOURCE, 2, 111, 0),
                (self.m.PK_RESOURCE, 2, 112, 0),
            ),
        )
        self.assertEqual(self.bundle.audit["changed_literal_count"], 8)
        self.assertEqual(self.bundle.audit["changed_record_count"], 8)

    def test_exact_term_only_replacement_and_pc_jp_evidence(self) -> None:
        targets = {target.slot: target for target in self.m.TARGETS}
        for resource in self.m.RESOURCE_ORDER:
            source = self.bundle.sources[resource]
            for target in (item for item in self.m.TARGETS if item.resource == resource):
                block, record, literal = target.slot
                current = self.m.parse_record_literals(source.archive.blocks[block].records[record])[literal].text
                jp = self.m.parse_record_literals(source.jp_archive.blocks[block].records[record])[literal].text
                self.assertEqual(self.m.text_hash(current), target.preimage_utf16le_sha256)
                self.assertEqual(self.m.text_hash(jp), target.jp_utf16le_sha256)
                self.assertIn(self.m.JP_TERM, jp)
                self.assertEqual(current.count(self.m.OLD_TERM), 1)
                replacement = current.replace(self.m.OLD_TERM, self.m.NEW_TERM)
                self.assertEqual(self.m.text_hash(replacement), target.target_utf16le_sha256)
                self.assertEqual(self.m.literal_signature(current), self.m.literal_signature(replacement))
        self.assertEqual(len(targets), 8)

    def test_whole_file_scope_and_opaque_controls(self) -> None:
        for resource in self.m.RESOURCE_ORDER:
            source = self.bundle.sources[resource]
            candidate = self.bundle.resources[resource]
            allowed_literals = {target.slot for target in self.m.TARGETS if target.resource == resource}
            allowed_records = {(block, record) for block, record, _literal in allowed_literals}
            observed_literals = set()
            observed_records = set()
            self.assertEqual(len(source.archive.blocks), len(candidate.archive.blocks))
            for before_block, after_block in zip(source.archive.blocks, candidate.archive.blocks):
                self.assertEqual(before_block.block_id, after_block.block_id)
                self.assertEqual(len(before_block.records), len(after_block.records))
                for before, after in zip(before_block.records, after_block.records):
                    coordinate = (before.block_id, before.record_id)
                    before_literals = self.m.parse_record_literals(before)
                    after_literals = self.m.parse_record_literals(after)
                    if before.data != after.data:
                        observed_records.add(coordinate)
                        self.assertIn(coordinate, allowed_records)
                        self.assertEqual(self.m.opaque_skeleton(before), self.m.opaque_skeleton(after))
                    else:
                        self.assertNotIn(coordinate, allowed_records)
                    for old, new in zip(before_literals, after_literals):
                        slot = (before.block_id, before.record_id, old.literal_id)
                        if old.text != new.text:
                            observed_literals.add(slot)
                            self.assertIn(slot, allowed_literals)
                            self.assertEqual(new.text, old.text.replace(self.m.OLD_TERM, self.m.NEW_TERM))
                        else:
                            self.assertNotIn(slot, allowed_literals)
            self.assertEqual(observed_literals, allowed_literals)
            self.assertEqual(observed_records, allowed_records)

    def test_parser_and_pinned_profiles(self) -> None:
        for resource in self.m.RESOURCE_ORDER:
            candidate = self.bundle.resources[resource]
            header, raw = self.m.decompress_wrapper(candidate.packed)
            self.assertEqual(raw, candidate.raw)
            archive = self.m.parse_raw_msggame(raw)
            self.assertEqual(self.m.rebuild_raw_msggame(archive), raw)
            self.assertEqual(self.m.decompress_wrapper(self.m.rebuild_packed_msggame(candidate.packed))[1], raw)
            self.m.require_profile(candidate.packed, candidate.raw, candidate.spec.output_profile, resource)
            self.assertIsNotNone(header)

    def test_audit_manifest_integrity(self) -> None:
        self.assertEqual(
            self.m.sha256_bytes(self.m.canonical_json(self.bundle.audit)),
            self.bundle.manifest["audit_sha256"],
        )
        self.assertTrue(self.bundle.audit["candidate_only"])
        self.assertFalse(self.bundle.audit["source_policy"]["steam_game_resource_written"])
        self.assertEqual(self.bundle.audit["validation"]["exact_old_to_new"], "겐푸쿠 -> 원복")

    def test_private_output_guard(self) -> None:
        accepted = self.m.require_private(self.m.TMP_ROOT / "candidate-test", "test private root")
        self.assertTrue(accepted.is_relative_to(self.m.TMP_ROOT.resolve(strict=False)))
        with self.assertRaises(self.m.CandidateError):
            self.m.require_private(self.m.REPO / "outside-private", "test outside root")
        with self.assertRaises(self.m.CandidateError):
            self.m.require_private(self.m.TMP_ROOT, "test tmp root")


if __name__ == "__main__":
    unittest.main(verbosity=2)
