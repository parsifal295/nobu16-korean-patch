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
WORKSTREAM = ROOT / "workstreams" / "issue_124_region_names_v1"
BUILDER_PATH = WORKSTREAM / "build_issue_124_region_names_v1.py"
WORKSPACE = Path(os.environ.get("NOBU16_TEST_WORKSPACE", str(next(
    (parent for parent in (ROOT, *ROOT.parents) if (parent / "workspace.paths.json").is_file()),
    ROOT,
))))
INPUT_ROOT = (
    WORKSPACE
    / "scratch"
    / "issue124-region-names-safe-input-20260823-01"
)
JP_REFERENCE_ROOT = WORKSPACE / "private-inputs" / "rust-patcher-v0151" / "stock"
EN_REFERENCE_MSGDATA = (
    WORKSPACE
    / "archive"
    / "steam-game-root-full-pre-rust-v0151-20260727-1745"
    / "MSG_PK"
    / "EN"
    / "msgdata.bin"
)
PUBLIC_RECEIPT = ROOT / "workstreams/v095_image_completion_v1/validation.v1.json"
CURRENT_V095_MSGDATA = {
    "size": 476_948,
    "sha256": "7630EA5C4B6809C91F1F9DE3721C54769FC52EDD16FB89B3D111F7A58CC8238C",
}
CURRENT_V095_STRDATA = {
    "size": 940_981,
    "sha256": "44A3621C5E4E6833260C2A8C0207D5FD74EB1F4A455E7AF81E7B93C571FB7029",
}


def import_builder():
    spec = importlib.util.spec_from_file_location("issue124_region_name_builder", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot import builder: {BUILDER_PATH}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


BUILDER = import_builder()


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class Issue124RegionNamesTests(unittest.TestCase):
    def require_private_inputs(self) -> None:
        required = [
            INPUT_ROOT / BUILDER.MSG_DATA,
            INPUT_ROOT / BUILDER.STR_DATA,
            JP_REFERENCE_ROOT / BUILDER.MSG_DATA,
            JP_REFERENCE_ROOT / BUILDER.STR_DATA,
            EN_REFERENCE_MSGDATA,
        ]
        missing = [str(path) for path in required if not path.is_file()]
        if missing:
            raise unittest.SkipTest(f"pinned issue #124 inputs are absent: {missing}")

    def test_source_free_full_place_policy_contract(self) -> None:
        payload = json.loads(BUILDER.POLICY_PATH.read_text(encoding="utf-8"))
        self.assertEqual(BUILDER.POLICY_SCHEMA, payload["schema"])
        self.assertEqual(2_014, payload["classifier"]["total_pair_count"])
        self.assertEqual(720, payload["classifier"]["shared_label_count"])
        self.assertEqual(1_294, payload["classifier"]["place_name_count"])
        self.assertEqual(1_293, payload["classifier"]["jp_en_mora_match_count"])
        self.assertEqual(88, payload["classifier"]["multiword_place_count"])
        self.assertEqual([10_388], [row["id"] for row in payload["classifier"]["mora_match_exceptions"]])
        self.assertEqual(306, payload["expected_output"]["changed_pair_count"])
        self.assertEqual(348, payload["expected_output"]["changed_text_count"])
        self.assertTrue(all(value is False for value in payload["distribution_policy"].values()))
        raw = BUILDER.POLICY_PATH.read_text(encoding="utf-8")
        self.assertNotIn("Ocean", raw)
        self.assertNotIn("海路", raw)

    def test_two_builds_are_identical_and_cover_all_2014_pairs(self) -> None:
        self.require_private_inputs()
        source_hashes = {
            resource: sha256(INPUT_ROOT / resource)
            for resource in BUILDER.RESOURCE_ORDER + BUILDER.READ_ONLY_DEPENDENCY_ORDER
        }
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue124-v0950-test-", dir=scratch) as directory:
            temporary = Path(directory)
            candidate_a = temporary / "candidate-a"
            candidate_b = temporary / "candidate-b"
            report_a = BUILDER.build_candidate(
                INPUT_ROOT,
                JP_REFERENCE_ROOT,
                EN_REFERENCE_MSGDATA,
                candidate_a,
            )
            report_b = BUILDER.build_candidate(
                INPUT_ROOT,
                JP_REFERENCE_ROOT,
                EN_REFERENCE_MSGDATA,
                candidate_b,
            )
            self.assertEqual(report_a, report_b)
            self.assertEqual(2_014, report_a["coverage"]["total_pair_count"])
            self.assertEqual(1_294, report_a["coverage"]["target_pair_count"])
            self.assertEqual(306, report_a["coverage"]["changed_pair_count"])
            self.assertEqual(988, report_a["coverage"]["already_correct_place_pair_count"])
            self.assertEqual(240, report_a["coverage"]["display_changed_count"])
            self.assertEqual(108, report_a["coverage"]["reading_changed_count"])
            self.assertEqual(1_293, report_a["coverage"]["jp_en_mora_match_count"])
            self.assertEqual(1, report_a["coverage"]["jp_en_mora_exception_count"])
            self.assertEqual(88, report_a["coverage"]["multiword_place_count"])
            self.assertEqual(348, report_a["changed_text_count"])
            self.assertEqual(1, report_a["changed_resource_count"])
            self.assertEqual(1, report_a["output_resource_count"])
            self.assertFalse(report_a["steam_written"])

            for resource in BUILDER.RESOURCE_ORDER:
                output_a = candidate_a / resource
                output_b = candidate_b / resource
                self.assertEqual(output_a.read_bytes(), output_b.read_bytes())
                self.assertEqual(BUILDER.FINAL_SPECS[resource]["packed_sha256"], sha256(output_a))

            _header, msg_raw = BUILDER.decompress_wrapper(
                (candidate_a / BUILDER.MSG_DATA).read_bytes()
            )
            msgdata = BUILDER.parse_message_table(msg_raw).texts
            self.assertEqual("나카사토", msgdata[9955])
            self.assertEqual("나카사토", msgdata[9955 + BUILDER.READING_OFFSET])
            self.assertEqual("마사카", msgdata[10001])
            self.assertEqual("마사카", msgdata[10001 + BUILDER.READING_OFFSET])
            self.assertEqual("모노", msgdata[10015])
            self.assertEqual("모노", msgdata[10015 + BUILDER.READING_OFFSET])
            self.assertEqual("히타치 고치", msgdata[10119])
            self.assertEqual("히타치 고치", msgdata[10119 + BUILDER.READING_OFFSET])
            self.assertEqual("시모사 가이조", msgdata[10156])
            self.assertEqual("시모사 가이조", msgdata[10156 + BUILDER.READING_OFFSET])
            self.assertEqual("오지야", msgdata[10388])
            self.assertEqual("오지야", msgdata[10388 + BUILDER.READING_OFFSET])
            self.assertEqual("노로시", msgdata[10439])
            self.assertEqual("구조", msgdata[10587])
            self.assertEqual("구조", msgdata[10587 + BUILDER.READING_OFFSET])
            self.assertEqual("쓰이키", msgdata[11071])
            self.assertEqual("쓰이키", msgdata[11071 + BUILDER.READING_OFFSET])
            self.assertEqual("에시로", msgdata[11185])
            self.assertEqual("에시로", msgdata[11185 + BUILDER.READING_OFFSET])
            self.assertEqual("스이타", msgdata[11310])
            self.assertEqual("스이타", msgdata[11310 + BUILDER.READING_OFFSET])
            self.assertEqual("에비에", msgdata[11311])
            self.assertEqual("에비에", msgdata[11311 + BUILDER.READING_OFFSET])

            self.assertFalse((candidate_a / BUILDER.STR_DATA).exists())
            str_resource = next(
                row for row in report_a["resources"] if row["resource"] == BUILDER.STR_DATA.as_posix()
            )
            self.assertEqual("read_only_dependency", str_resource["role"])
            self.assertEqual(0, str_resource["changed_text_count"])
            self.assertFalse(str_resource["output_emitted"])
            self.assertTrue(str_resource["shared_translation_surface_preserved"])

            audit = json.loads((candidate_a / BUILDER.AUDIT_NAME).read_text(encoding="utf-8"))
            self.assertEqual(2_014, audit["row_count"])
            self.assertEqual(720, audit["classification_counts"]["special_shared_label"])
            self.assertEqual(1_294, audit["classification_counts"]["full_place_transcription"])
            shared_row = next(
                row for row in audit["rows"] if row["classification"] == "special_shared_label"
            )
            self.assertFalse(shared_row["msgdata_changed"])
            self.assertEqual(shared_row["before_ko"], shared_row["after_ko"])
            mismatch_row = next(row for row in audit["rows"] if row["id"] == 10_388)
            self.assertFalse(mismatch_row["jp_en_mora_match"])
            self.assertEqual("오지야", mismatch_row["after_ko"]["display"])

        for resource, before in source_hashes.items():
            self.assertEqual(before, sha256(INPUT_ROOT / resource))

    def test_modified_preimage_is_rejected_without_output(self) -> None:
        self.require_private_inputs()
        scratch = WORKSPACE / "scratch"
        with tempfile.TemporaryDirectory(prefix="issue124-negative-", dir=scratch) as directory:
            temporary = Path(directory)
            copied = temporary / "input"
            for resource in BUILDER.RESOURCE_ORDER + BUILDER.READ_ONLY_DEPENDENCY_ORDER:
                target = copied / resource
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(INPUT_ROOT / resource, target)
            changed = bytearray((copied / BUILDER.MSG_DATA).read_bytes())
            changed[-1] ^= 1
            (copied / BUILDER.MSG_DATA).write_bytes(changed)
            output = temporary / "output"
            with self.assertRaisesRegex(BUILDER.BuildError, "input msgdata packed/raw pin differs"):
                BUILDER.build_candidate(
                    copied,
                    JP_REFERENCE_ROOT,
                    EN_REFERENCE_MSGDATA,
                    output,
                )
            self.assertFalse(output.exists())

    def test_steam_output_is_rejected(self) -> None:
        with self.assertRaisesRegex(BUILDER.BuildError, "Steam installation"):
            BUILDER.build_candidate(
                INPUT_ROOT,
                JP_REFERENCE_ROOT,
                EN_REFERENCE_MSGDATA,
                BUILDER.DEFAULT_STEAM_ROOT / "issue124-output-must-not-exist",
            )

    def test_v0950_public_receipt_pins_current_composite_targets(self) -> None:
        targets = json.loads(PUBLIC_RECEIPT.read_text(encoding="utf-8"))["text_resources"]
        self.assertEqual(CURRENT_V095_MSGDATA, targets[BUILDER.MSG_DATA.as_posix()])
        self.assertEqual(CURRENT_V095_STRDATA, targets[BUILDER.STR_DATA.as_posix()])


if __name__ == "__main__":
    unittest.main(verbosity=2)
