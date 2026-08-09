#!/usr/bin/env python3
"""Regression tests for the deterministic issue #109 msggame correction."""

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
    WORKSPACE / "scratch" / "v0920-resource-input-20260808-02" / "target"
)


def import_builder():
    path = HERE / "build_issue109_marriage_support_v1.py"
    spec = importlib.util.spec_from_file_location("issue109_marriage_support_builder", path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Issue109MarriageSupportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        for relative_path in BUILDER.RESOURCE_SPECS:
            path = INPUT_ROOT / Path(relative_path)
            if not path.is_file():
                raise unittest.SkipTest(f"pinned v0.92 input is absent: {path}")

    def test_contract_scope_and_wording(self) -> None:
        self.assertEqual(
            {path: tuple(spec["coordinate"]) for path, spec in BUILDER.RESOURCE_SPECS.items()},
            {
                "MSG/JP/msggame.bin": (6, 3577),
                "MSG_PK/JP/msggame.bin": (6, 3584),
            },
        )
        self.assertEqual(
            BUILDER.REPLACEMENT_LITERALS,
            ("의 자격으로 ", "에게 힘이 되어 줄 준비는\n되어 있겠지"),
        )
        self.assertEqual(
            BUILDER.OPAQUE_SPANS, ("023C", "014301000000", "050505")
        )

    def test_two_builds_are_byte_identical_and_source_is_unchanged(self) -> None:
        before = {relative: sha256(INPUT_ROOT / relative) for relative in BUILDER.RESOURCE_SPECS}
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue109-test-", dir=scratch) as directory:
            temporary = Path(directory)
            candidate_a = temporary / "candidate-a"
            candidate_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(INPUT_ROOT, candidate_a)
            report_b = BUILDER.build_candidate(INPUT_ROOT, candidate_b)
            self.assertEqual(report_a, report_b)
            self.assertEqual(
                (candidate_a / BUILDER.VALIDATION_NAME).read_bytes(),
                (candidate_b / BUILDER.VALIDATION_NAME).read_bytes(),
            )

            final_records = []
            for relative_path, contract in BUILDER.RESOURCE_SPECS.items():
                output_a = candidate_a / Path(relative_path)
                output_b = candidate_b / Path(relative_path)
                self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
                self.assertEqual(sha256(output_a), contract["final"]["packed_sha256"])

                before_archive = BUILDER.msggame.parse_packed_msggame(
                    (INPUT_ROOT / Path(relative_path)).read_bytes()
                ).archive
                after_archive = BUILDER.msggame.parse_packed_msggame(output_a.read_bytes()).archive
                coordinate = tuple(contract["coordinate"])
                self.assertEqual(
                    BUILDER.changed_records(before_archive, after_archive), (coordinate,)
                )
                final_record = BUILDER.record_at(after_archive, coordinate)
                self.assertEqual(
                    BUILDER.literal_texts(final_record), BUILDER.REPLACEMENT_LITERALS
                )
                self.assertEqual(BUILDER.opaque_spans(final_record), BUILDER.OPAQUE_SPANS)
                self.assertEqual(
                    BUILDER.sha256(final_record.data), BUILDER.FINAL_RECORD_SHA256
                )
                final_records.append(final_record.data)
            self.assertEqual(final_records[0], final_records[1])

        after = {relative: sha256(INPUT_ROOT / relative) for relative in BUILDER.RESOURCE_SPECS}
        self.assertEqual(before, after)

    def test_unpinned_input_is_rejected_before_output(self) -> None:
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue109-negative-", dir=scratch) as directory:
            temporary = Path(directory)
            input_root = temporary / "input"
            for relative_path in BUILDER.RESOURCE_SPECS:
                source = INPUT_ROOT / Path(relative_path)
                target = input_root / Path(relative_path)
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
