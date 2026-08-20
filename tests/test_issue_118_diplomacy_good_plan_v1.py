from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSTREAM = ROOT / "workstreams" / "issue_118_diplomacy_good_plan_v1"
BUILDER_PATH = WORKSTREAM / "build_issue_118_diplomacy_good_plan_v1.py"
WORKSPACE = next(
    parent for parent in (ROOT, *ROOT.parents)
    if (parent / "workspace.paths.json").is_file()
)
INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "release-v0940-rc-20260819-01"
    / "resource-input"
    / "target"
)
RESOURCE_SPEC = (
    ROOT
    / "workstreams"
    / "rust_patcher_v1"
    / "rust"
    / "releases"
    / "v0.94"
    / "resources.toml"
)


def import_builder():
    spec = importlib.util.spec_from_file_location("issue118_diplomacy_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Issue118DiplomacyGoodPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        source = INPUT_ROOT / BUILDER.RESOURCE
        if not source.is_file():
            raise unittest.SkipTest(f"pinned v0.94 RC input is absent: {source}")

    def test_public_overlay_is_single_coordinate_and_source_free(self) -> None:
        payload = json.loads(BUILDER.OVERLAY_PATH.read_text(encoding="utf-8"))
        entry = payload["entries"][0]
        self.assertEqual(BUILDER.OVERLAY_SCHEMA, payload["schema"])
        self.assertEqual(1, payload["entry_count"])
        self.assertEqual(
            BUILDER.COORDINATE,
            (entry["block_id"], entry["record_id"], entry["literal_id"]),
        )
        self.assertEqual("\n좋은 방안", entry["ko"])
        self.assertEqual(
            BUILDER.FINAL_SPEC["literal_utf16le_sha256"][1],
            entry["ko_utf16le_sha256"],
        )
        self.assertTrue(all(value is False for value in payload["distribution_policy"].values()))

    def test_two_builds_are_identical_and_only_one_literal_changes(self) -> None:
        source_path = INPUT_ROOT / BUILDER.RESOURCE
        source_before = sha256(source_path)
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue118-v0940-test-", dir=scratch) as directory:
            temporary = Path(directory)
            candidate_a = temporary / "candidate-a"
            candidate_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(INPUT_ROOT, candidate_a)
            report_b = BUILDER.build_candidate(INPUT_ROOT, candidate_b)
            self.assertEqual(report_a, report_b)
            output_a = candidate_a / BUILDER.RESOURCE
            output_b = candidate_b / BUILDER.RESOURCE
            self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
            self.assertEqual(BUILDER.FINAL_SPEC["packed_sha256"], sha256(output_a))

            before = BUILDER.msggame.parse_packed_msggame(source_path.read_bytes()).archive
            after = BUILDER.msggame.parse_packed_msggame(output_a.read_bytes()).archive
            self.assertEqual((BUILDER.RECORD_COORDINATE,), BUILDER.changed_records(before, after))
            self.assertEqual((BUILDER.COORDINATE,), BUILDER.changed_literals(before, after))
            final_record = BUILDER.record_at(after)
            self.assertEqual(BUILDER.OPAQUE_SPANS, BUILDER.opaque_spans(final_record))
            self.assertEqual("\n좋은 방안", BUILDER.literal_texts(final_record)[1])
            self.assertTrue(report_a["vm_and_control_bytes_preserved"])
            self.assertFalse(report_a["steam_written"])
        self.assertEqual(source_before, sha256(source_path))

    def test_unpinned_input_is_rejected_without_output(self) -> None:
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue118-negative-", dir=scratch) as directory:
            temporary = Path(directory)
            source = INPUT_ROOT / BUILDER.RESOURCE
            target = temporary / "input" / BUILDER.RESOURCE
            target.parent.mkdir(parents=True)
            changed = bytearray(source.read_bytes())
            changed[-1] ^= 1
            target.write_bytes(changed)
            output = temporary / "output"
            with self.assertRaisesRegex(BUILDER.BuildError, "input packed/raw pin differs"):
                BUILDER.build_candidate(temporary / "input", output)
            self.assertFalse(output.exists())

    def test_steam_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(BUILDER.BuildError, "Steam installation"):
            BUILDER.build_candidate(
                INPUT_ROOT,
                BUILDER.DEFAULT_STEAM_ROOT / "issue118-output-must-not-exist",
            )

    def test_v0940_resource_spec_uses_the_corrected_target(self) -> None:
        if not RESOURCE_SPEC.is_file():
            self.skipTest("private product resource spec is not published")
        spec = tomllib.loads(RESOURCE_SPEC.read_text(encoding="utf-8"))
        targets = {value["relative_path"]: value for value in spec["targets"]}
        target = targets[BUILDER.RESOURCE.as_posix()]
        self.assertEqual(BUILDER.FINAL_SPEC["packed_size"], target["size"])
        self.assertEqual(BUILDER.FINAL_SPEC["packed_sha256"], target["sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
