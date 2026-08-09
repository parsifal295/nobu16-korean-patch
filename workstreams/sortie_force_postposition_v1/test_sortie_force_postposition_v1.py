#!/usr/bin/env python3
"""Regression tests for the sortie-dialogue postposition correction."""

from __future__ import annotations

import hashlib
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[3]
INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "v0920-resource-input-20260809-policy-readings-01"
    / "target"
)


def import_builder():
    path = HERE / "build_sortie_force_postposition_v1.py"
    spec = importlib.util.spec_from_file_location("sortie_force_postposition_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def matching_literals(path: Path, needle: str) -> list[tuple[int, int, int, str]]:
    archive = BUILDER.msggame.parse_packed_msggame(path.read_bytes()).archive
    matches: list[tuple[int, int, int, str]] = []
    for block in archive.blocks:
        for record in block.records:
            for index, literal in enumerate(BUILDER.msggame.parse_record_literals(record)):
                if needle in literal.text:
                    matches.append((record.block_id, record.record_id, index, literal.text))
    return matches


class SortieForcePostpositionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for relative_path in BUILDER.RESOURCE_SPECS:
            path = INPUT_ROOT / Path(relative_path)
            if not path.is_file():
                raise unittest.SkipTest(f"pinned v0.92 input is absent: {path}")

    def test_scope_is_exactly_the_seven_affected_records(self) -> None:
        self.assertEqual(
            {
                path: tuple(spec["records"].keys())
                for path, spec in BUILDER.RESOURCE_SPECS.items()
            },
            {
                "MSG/JP/msggame.bin": (
                    (7, 2418),
                    (7, 2419),
                    (7, 2420),
                    (7, 2421),
                    (7, 2422),
                ),
                "MSG_PK/JP/msggame.bin": ((7, 2463), (7, 2464)),
            },
        )
        self.assertEqual(
            sum(len(spec["records"]) for spec in BUILDER.RESOURCE_SPECS.values()), 7
        )

    def test_two_builds_are_identical_and_only_target_records_change(self) -> None:
        before_hashes = {
            relative: sha256(INPUT_ROOT / relative)
            for relative in BUILDER.RESOURCE_SPECS
        }
        with tempfile.TemporaryDirectory(prefix="sortie-postposition-", dir=WORKSPACE / "scratch") as directory:
            temporary = Path(directory)
            candidate_a = temporary / "candidate-a"
            candidate_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(INPUT_ROOT, candidate_a)
            report_b = BUILDER.build_candidate(INPUT_ROOT, candidate_b)
            self.assertEqual(report_a, report_b)
            self.assertEqual(report_a["changed_record_count"], 7)
            self.assertEqual(
                (candidate_a / BUILDER.VALIDATION_NAME).read_bytes(),
                (candidate_b / BUILDER.VALIDATION_NAME).read_bytes(),
            )

            for relative, contract in BUILDER.RESOURCE_SPECS.items():
                output_a = candidate_a / relative
                output_b = candidate_b / relative
                self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
                self.assertEqual(sha256(output_a), contract["final"]["packed_sha256"])
                before = BUILDER.msggame.parse_packed_msggame(
                    (INPUT_ROOT / relative).read_bytes()
                ).archive
                after = BUILDER.msggame.parse_packed_msggame(output_a.read_bytes()).archive
                self.assertEqual(
                    BUILDER.changed_records(before, after), tuple(contract["records"].keys())
                )

        self.assertEqual(
            before_hashes,
            {relative: sha256(INPUT_ROOT / relative) for relative in BUILDER.RESOURCE_SPECS},
        )

    def test_bad_postposition_is_removed_without_touching_other_literals(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sortie-postposition-scan-", dir=WORKSPACE / "scratch") as directory:
            output = Path(directory) / "candidate"
            BUILDER.build_candidate(INPUT_ROOT, output)
            old_before = []
            old_after = []
            for relative in BUILDER.RESOURCE_SPECS:
                old_before.extend(matching_literals(INPUT_ROOT / relative, BUILDER.OLD_PREFIX))
                old_after.extend(matching_literals(output / relative, BUILDER.OLD_PREFIX))
            self.assertEqual(len(old_before), 7)
            self.assertEqual(old_after, [])

    def test_tampered_input_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="sortie-postposition-negative-", dir=WORKSPACE / "scratch") as directory:
            temporary = Path(directory)
            input_root = temporary / "input"
            for relative in BUILDER.RESOURCE_SPECS:
                source = INPUT_ROOT / relative
                target = input_root / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(source.read_bytes())
            target = input_root / "MSG_PK/JP/msggame.bin"
            changed = bytearray(target.read_bytes())
            changed[-1] ^= 1
            target.write_bytes(changed)
            output_root = temporary / "output"
            with self.assertRaisesRegex(BUILDER.BuildError, "input pin differs"):
                BUILDER.build_candidate(input_root, output_root)
            self.assertFalse(output_root.exists())


if __name__ == "__main__":
    unittest.main()
