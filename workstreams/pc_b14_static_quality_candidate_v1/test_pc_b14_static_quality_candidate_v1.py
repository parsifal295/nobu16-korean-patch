#!/usr/bin/env python3
"""Independent checks for the private B14 static-quality candidate."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


sys.dont_write_bytecode = True

WORKSTREAM = Path(__file__).resolve().parent
BUILDER = WORKSTREAM / "build_pc_b14_static_quality_candidate_v1.py"


def load_builder():
    spec = importlib.util.spec_from_file_location("b14_static_candidate_builder", BUILDER)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load B14 candidate builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class B14StaticQualityCandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.m = load_builder()
        cls.bundle = cls.m.prepare_candidate()

    def test_exact_ten_literal_scope(self) -> None:
        self.assertEqual(
            tuple((target.resource, *target.slot) for target in self.m.TARGETS),
            (
                (self.m.BASE_RESOURCE, 14, 32, 3),
                (self.m.BASE_RESOURCE, 14, 113, 1),
                (self.m.BASE_RESOURCE, 14, 117, 3),
                (self.m.PK_RESOURCE, 14, 48, 3),
                (self.m.PK_RESOURCE, 14, 51, 1),
                (self.m.PK_RESOURCE, 14, 156, 1),
                (self.m.PK_RESOURCE, 14, 157, 1),
                (self.m.PK_RESOURCE, 14, 225, 1),
                (self.m.PK_RESOURCE, 14, 226, 1),
                (self.m.PK_RESOURCE, 14, 227, 1),
            ),
        )
        self.assertEqual(self.bundle.audit["changed_literal_count"], 10)
        self.assertEqual(self.bundle.audit["changed_record_count"], 10)
        approved = {(target.resource, *target.slot) for target in self.m.TARGETS}
        self.assertTrue(approved.isdisjoint(self.m.EXCLUDED_SLOTS))

    def test_exact_w45_preimages_and_pristine_pc_jp(self) -> None:
        for target in self.m.TARGETS:
            source = self.bundle.sources[target.resource]
            block, record, literal = target.slot
            current = self.m.parse_record_literals(
                source.archive.blocks[block].records[record]
            )[literal].text
            jp_text = self.m.parse_record_literals(
                source.jp_archive.blocks[block].records[record]
            )[literal].text
            self.assertEqual(self.m.text_hash(current), target.preimage_utf16le_sha256)
            self.assertEqual(self.m.text_hash(jp_text), target.jp_utf16le_sha256)
            candidate = self.m.apply_edits(current, target.edits, target.slot_text)
            self.assertEqual(self.m.text_hash(candidate), target.target_utf16le_sha256)
            self.assertEqual(
                self.m.literal_signature(current),
                self.m.literal_signature(candidate),
            )

    def test_particles_are_corrected_with_the_noun_changes(self) -> None:
        rows = {
            (row["resource"], row["slot"]): row
            for row in self.bundle.audit["records"]
        }
        rank = rows[(self.m.BASE_RESOURCE, "14:32:3")]["target_ko"]
        self.assertIn("\u300c\uc870\ub450\u300d\ub85c\uc11c", rank)
        self.assertNotIn("\u300c\uc870\ub450\u300d\uc73c\ub85c\uc11c", rank)

        title = rows[(self.m.PK_RESOURCE, "14:226:1")]["target_ko"]
        for expected in (
            "\ubcc4\ud638\ub97c",
            "\ubcc4\ud638\ub294",
            "\ubcc4\ud638\uac00",
            "\ubcc4\ud638\uc5d0",
            "\ubcc4\ud638\uc640",
        ):
            self.assertIn(expected, title)
        self.assertNotIn("\ubcc4\ud638\uc744", title)
        self.assertNotIn("\ubcc4\ud638\uc740", title)
        self.assertNotIn("\ubcc4\ud638\uc774", title)
        self.assertNotIn("\ubcc4\ud638\uacfc", title)

        effect = rows[(self.m.PK_RESOURCE, "14:227:1")]["target_ko"]
        self.assertIn("\ubcc4\ud638\ub97c \uc9c0\ub2cc", effect)
        self.assertIn("\ubcc4\ud638 \ud6a8\uacfc", effect)
        self.assertNotIn("\ubcc4\ud638\uc744 \uc9c0\ub2cc", effect)

    def test_whole_archive_scope_and_opaque_controls(self) -> None:
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
        for resource in self.m.RESOURCE_ORDER:
            candidate = self.bundle.resources[resource]
            header, raw = self.m.decompress_wrapper(candidate.packed)
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
                candidate.spec.output_profile,
                resource,
            )
            self.assertIsNotNone(header)

    def test_audit_manifest_and_private_guards(self) -> None:
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
