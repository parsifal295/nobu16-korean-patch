from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import sys
import tempfile
import tomllib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSTREAM = ROOT / "workstreams" / "issue_113_116_text_fixes_v1"
BUILDER_PATH = WORKSTREAM / "build_issue_113_116_text_fixes_v1.py"
WORKSPACE = next(
    parent for parent in (ROOT, *ROOT.parents) if (parent / "workspace.paths.json").is_file()
)
INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "release-v0940-rc-20260819-02"
    / "resource-input"
    / "target"
)
RUST = ROOT / "workstreams" / "rust_patcher_v1" / "rust"
RESOURCE_SPEC = RUST / "releases" / "v0.94" / "resources.toml"
GENERATOR = RUST / "tools" / "New-V0940ResourceSpec.ps1"


def import_builder():
    spec = importlib.util.spec_from_file_location("issue113_116_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Issue113116TextFixesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        missing = [
            resource.as_posix()
            for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.PASSTHROUGH_ORDER)
            if not (INPUT_ROOT / resource).is_file()
        ]
        if missing:
            raise unittest.SkipTest(f"pinned v0.94 inputs are absent: {missing}")

    def test_public_overlay_has_only_the_three_source_free_coordinates(self) -> None:
        payload = json.loads(BUILDER.OVERLAY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(BUILDER.OVERLAY_SCHEMA, payload["schema"])
        self.assertEqual(3, payload["entry_count"])
        coordinates = {
            (
                entry["issue"],
                entry["resource"],
                entry.get("block_id"),
                entry.get("slot_id", entry.get("id")),
            )
            for entry in payload["entries"]
        }
        self.assertEqual(
            {
                (113, "MSG_PK/JP/msgui.bin", None, 2690),
                (116, "MSG_PK/JP/msgdata.bin", None, 10220),
                (116, "MSG/JP/strdata.bin", 0, 10136),
            },
            coordinates,
        )
        self.assertTrue(all(value is False for value in payload["distribution_policy"].values()))

    def test_two_builds_are_identical_and_only_three_texts_change(self) -> None:
        source_hashes = {
            resource: sha256(INPUT_ROOT / resource)
            for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.PASSTHROUGH_ORDER)
        }
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue113-116-v0940-test-", dir=scratch) as directory:
            temporary = Path(directory)
            candidate_a = temporary / "candidate-a"
            candidate_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(INPUT_ROOT, candidate_a)
            report_b = BUILDER.build_candidate(INPUT_ROOT, candidate_b)
            self.assertEqual(report_a, report_b)
            self.assertEqual(3, report_a["changed_text_count"])
            self.assertFalse(report_a["steam_written"])

            for resource in BUILDER.RESOURCE_ORDER:
                output_a = candidate_a / resource
                output_b = candidate_b / resource
                self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
                self.assertEqual(BUILDER.FINAL_SPECS[resource]["packed_sha256"], sha256(output_a))
            for resource in BUILDER.PASSTHROUGH_ORDER:
                self.assertEqual(
                    (INPUT_ROOT / resource).read_bytes(),
                    (candidate_a / resource).read_bytes(),
                )

            _header, msgui_raw = BUILDER.decompress_wrapper((candidate_a / BUILDER.MSG_UI).read_bytes())
            msgui = BUILDER.parse_message_table(msgui_raw).texts
            self.assertEqual("%s %s", msgui[2690])
            self.assertEqual("적 부대의 병력 감소", msgui[2690] % (msgui[2312], msgui[2693]))
            self.assertEqual("자기 부대의 방어 상승", msgui[2690] % (msgui[2310], msgui[2713]))

            _header, msgdata_raw = BUILDER.decompress_wrapper((candidate_a / BUILDER.MSG_DATA).read_bytes())
            msgdata = BUILDER.parse_message_table(msgdata_raw).texts
            self.assertEqual("고마", msgdata[10220])
            _header, strdata_raw = BUILDER.decompress_wrapper((candidate_a / BUILDER.STR_DATA).read_bytes())
            strdata = BUILDER.coordinate_texts(BUILDER.parse_raw_strdata(strdata_raw))
            self.assertEqual("고마", strdata[(0, 10136)])

        for resource, before in source_hashes.items():
            self.assertEqual(before, sha256(INPUT_ROOT / resource))

    def test_modified_preimage_is_rejected_without_output(self) -> None:
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue113-116-negative-", dir=scratch) as directory:
            temporary = Path(directory)
            copied = temporary / "input"
            for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.PASSTHROUGH_ORDER):
                target = copied / resource
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(INPUT_ROOT / resource, target)
            changed = bytearray((copied / BUILDER.MSG_UI).read_bytes())
            changed[-1] ^= 1
            (copied / BUILDER.MSG_UI).write_bytes(changed)
            output = temporary / "output"
            with self.assertRaisesRegex(BUILDER.BuildError, "input packed/raw pin differs"):
                BUILDER.build_candidate(copied, output)
            self.assertFalse(output.exists())

    def test_steam_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(BUILDER.BuildError, "Steam installation"):
            BUILDER.build_candidate(
                INPUT_ROOT,
                BUILDER.DEFAULT_STEAM_ROOT / "issue113-116-output-must-not-exist",
            )

    def test_v0940_generator_and_resource_spec_pin_all_final_targets(self) -> None:
        if not GENERATOR.is_file() or not RESOURCE_SPEC.is_file():
            self.skipTest("private release generator and resource spec are not published")
        generator = GENERATOR.read_text(encoding="utf-8")
        spec = tomllib.loads(RESOURCE_SPEC.read_text(encoding="utf-8"))
        targets = {entry["relative_path"]: entry for entry in spec["targets"]}
        for resource in BUILDER.RESOURCE_ORDER:
            final = BUILDER.FINAL_SPECS[resource]
            self.assertIn(final["packed_sha256"], generator)
            self.assertEqual(final["packed_size"], targets[resource.as_posix()]["size"])
            self.assertEqual(final["packed_sha256"], targets[resource.as_posix()]["sha256"])
        self.assertIn(BUILDER.ISSUE118_SPEC["packed_sha256"], generator)
        for expected in BUILDER.PASSTHROUGH_SPECS.values():
            self.assertIn(expected["sha256"], generator)


if __name__ == "__main__":
    unittest.main(verbosity=2)
