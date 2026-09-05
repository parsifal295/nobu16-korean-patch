from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSTREAM = ROOT / "workstreams" / "issue_122_123_name_reading_fixes_v1"
BUILDER_PATH = WORKSTREAM / "build_issue_122_123_name_reading_fixes_v1.py"
WORKSPACE = Path(os.environ.get("NOBU16_TEST_WORKSPACE", str(next(
    (parent for parent in (ROOT, *ROOT.parents) if (parent / "workspace.paths.json").is_file()),
    ROOT,
))))
INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "boot-warning-v0950-release-20260904-01"
    / "generator-b"
    / "target"
)
JP_REFERENCE_ROOT = WORKSPACE / "private-inputs" / "rust-patcher-v0151" / "stock"
PUBLIC_RECEIPT = ROOT / "workstreams/v095_image_completion_v1/validation.v1.json"


def import_builder():
    spec = importlib.util.spec_from_file_location("issue122_123_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def entry(path: Path, identifier: int) -> dict[str, object]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    matches = [row for row in payload["entries"] if row["id"] == identifier]
    if len(matches) != 1:
        raise AssertionError(f"expected one id {identifier} in {path}, got {len(matches)}")
    return matches[0]


class Issue122123NameReadingFixesTests(unittest.TestCase):
    def require_private_inputs(self) -> None:
        required = [
            *(INPUT_ROOT / resource for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.READ_ONLY_DEPENDENCY_ORDER)),
            *(JP_REFERENCE_ROOT / resource for resource in BUILDER.RESOURCE_ORDER),
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise unittest.SkipTest(f"pinned issue #122/#123 inputs are absent: {missing}")

    def test_overlay_contract_and_approved_spellings(self) -> None:
        entries, anchors = BUILDER.load_overlay()
        self.assertEqual(4, sum(len(rows) for rows in entries.values()))
        self.assertEqual(2, len(anchors))
        self.assertEqual("모토우지", entries[BUILDER.MSG_DATA][2502]["ko"])
        self.assertEqual("하타야마 모토우지", entries[BUILDER.MSG_EV][1625]["ko"])
        self.assertEqual("모리 모토우지", entries[BUILDER.MSG_EV][2012]["ko"])
        self.assertEqual("야샤미노", entries[BUILDER.MSG_DATA][24765]["ko"])

    def test_two_builds_are_identical_and_change_only_four_coordinates(self) -> None:
        self.require_private_inputs()
        source_hashes = {
            resource: sha256(INPUT_ROOT / resource)
            for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.READ_ONLY_DEPENDENCY_ORDER)
        }
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue122-123-test-", dir=scratch) as directory:
            temporary = Path(directory)
            output_a = temporary / "candidate-a"
            output_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(INPUT_ROOT, JP_REFERENCE_ROOT, output_a)
            report_b = BUILDER.build_candidate(INPUT_ROOT, JP_REFERENCE_ROOT, output_b)
            self.assertEqual(report_a, report_b)
            self.assertEqual(2, report_a["changed_resource_count"])
            self.assertEqual(4, report_a["changed_text_count"])
            self.assertFalse(report_a["steam_written"])

            for resource in BUILDER.RESOURCE_ORDER:
                self.assertEqual(
                    (output_a / resource).read_bytes(),
                    (output_b / resource).read_bytes(),
                )
                self.assertEqual(
                    BUILDER.FINAL_SPECS[resource]["packed_sha256"],
                    sha256(output_a / resource),
                )

            _header, msgdata_raw = BUILDER.decompress_wrapper(
                (output_a / BUILDER.MSG_DATA).read_bytes()
            )
            msgdata = BUILDER.parse_message_table(msgdata_raw).texts
            self.assertEqual("모토우지", msgdata[2502])
            self.assertEqual("야샤미노", msgdata[24510])
            self.assertEqual("야샤미노", msgdata[24765])

            _header, msgev_raw = BUILDER.decompress_wrapper(
                (output_a / BUILDER.MSG_EV).read_bytes()
            )
            msgev = BUILDER.parse_message_table(msgev_raw).texts
            self.assertEqual("하타야마 모토우지", msgev[1625])
            self.assertEqual("모리 모토우지", msgev[2012])
            self.assertEqual("깃카와 모토우지", msgev[3085])

        for resource, expected in source_hashes.items():
            self.assertEqual(expected, sha256(INPUT_ROOT / resource))

    def test_modified_preimage_is_rejected_without_output(self) -> None:
        self.require_private_inputs()
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue122-123-negative-", dir=scratch) as directory:
            temporary = Path(directory)
            copied = temporary / "input"
            for resource in (*BUILDER.RESOURCE_ORDER, *BUILDER.READ_ONLY_DEPENDENCY_ORDER):
                destination = copied / resource
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(INPUT_ROOT / resource, destination)
            changed = bytearray((copied / BUILDER.MSG_DATA).read_bytes())
            changed[-1] ^= 1
            (copied / BUILDER.MSG_DATA).write_bytes(changed)
            output = temporary / "output"
            with self.assertRaisesRegex(BUILDER.BuildError, r"input msgdata\.bin packed/raw pin differs"):
                BUILDER.build_candidate(copied, JP_REFERENCE_ROOT, output)
            self.assertFalse(output.exists())

    def test_steam_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(BUILDER.BuildError, "Steam installation"):
            BUILDER.build_candidate(
                INPUT_ROOT,
                JP_REFERENCE_ROOT,
                BUILDER.DEFAULT_STEAM_ROOT / "issue122-123-output-must-not-exist",
            )

    def test_canonical_translation_sources_match_the_fixed_runtime(self) -> None:
        public_msgdata = ROOT / "data/public/msgdata_ko_officer_names_0000_2399.v0.1.json"
        public_msgev = ROOT / "data/public/msgev_ko_officer_names_0000_2399.v0.1.json"
        native_msgdata = (
            ROOT / "workstreams/steam_jp_common_messages_v1/public/msgdata_ko_steam_jp_native.v1.json"
        )
        native_msgev = (
            ROOT / "workstreams/steam_jp_common_messages_v1/public/msgev_ko_steam_jp_native.v1.json"
        )
        self.assertEqual("모토우지", entry(public_msgdata, 2502)["ko"])
        self.assertEqual("하타야마 모토우지", entry(public_msgev, 1625)["ko"])
        self.assertEqual("모리 모토우지", entry(public_msgev, 2012)["ko"])
        self.assertEqual("모토우지", entry(native_msgdata, 2502)["ko"])
        self.assertEqual("야샤미노", entry(native_msgdata, 24510)["ko"])
        self.assertEqual("야샤미노", entry(native_msgdata, 24765)["ko"])
        self.assertEqual("하타야마 모토우지", entry(native_msgev, 1625)["ko"])
        self.assertEqual("모리 모토우지", entry(native_msgev, 2012)["ko"])

    def test_v0950_public_receipt_pins_fixed_targets(self) -> None:
        targets = json.loads(PUBLIC_RECEIPT.read_text(encoding="utf-8"))["text_resources"]
        for resource in BUILDER.RESOURCE_ORDER:
            final = BUILDER.FINAL_SPECS[resource]
            target = targets[resource.as_posix()]
            self.assertEqual(final["packed_size"], target["size"])
            self.assertEqual(final["packed_sha256"], target["sha256"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
