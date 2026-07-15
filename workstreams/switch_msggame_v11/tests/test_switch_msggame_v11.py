from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = WORKSTREAM_ROOT.parents[1]
MSGGAME_ROOT = REPO_ROOT / "workstreams" / "msggame"
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(MSGGAME_ROOT))

import build_switch_msggame_v11 as batch  # noqa: E402
from msggame_format import MsgGameFormatError, parse_raw_msggame  # noqa: E402
from nobu16_lz4 import decompress_wrapper  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "245A73AA77B5649B686CE5A459C299CFBF7EE8EF5A6CDC56A7EB11288DECDFB5",
    f"evidence/{batch.EVIDENCE_NAME}": "5A6211F901EBC09BA5AB5164D9E2A1D2F282942FAE8161CE27B39324E77AF74C",
    f"review/{batch.REVIEW_NAME}": "321416550DBA417664789B861FD5C8898C81E5D7BA4E8CAA47267FDB41B255C6",
    batch.VALIDATION_NAME: "C4E35A3E49475C8F53F9F27962C4853F64EE6269AAA0D33B4B0BEDE2983162D3",
}
EXPECTED_TARGET_SHA256 = "869B5EBECE617BBCDCCF0BBDC5149B0243B44F2AC02365EFF35329A77E628803"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} root is not an object")
    return value


def source_digests() -> dict[str, str]:
    return {
        "switch_zip": digest(batch.REPO_ROOT / batch.SWITCH_ZIP_RELATIVE),
        "base_jp": digest(batch.GAME_ROOT / batch.SOURCE_PINS["base_jp"]["logical_path"]),
        "pk_jp": digest(batch.GAME_ROOT / batch.SOURCE_PINS["pk_jp"]["logical_path"]),
        "pk_sc": digest(batch.GAME_ROOT / batch.SOURCE_PINS["pk_sc"]["logical_path"]),
        "progress": digest(batch.REPO_ROOT / batch.PROGRESS_RELATIVE),
    }


class SwitchMsggameV11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load_json(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load_json(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load_json(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load_json(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_published_artifacts_are_source_free_and_pinned(self) -> None:
        self.assertEqual(6018, self.overlay["entry_count"])
        self.assertEqual(batch.RESOURCE, self.overlay["resource"])
        self.assertEqual("SC", self.overlay["base_language"])
        self.assertFalse(self.overlay["distribution_policy"]["contains_commercial_source_text"])
        self.assertEqual("snake7594", self.overlay["migration_provenance"]["author"])
        self.assertEqual("v1.1", self.overlay["migration_provenance"]["release_tag"])
        self.assertEqual(batch.SOURCE_PROVENANCE["zip_sha256"], self.overlay["migration_provenance"]["asset_sha256"])

        coordinates = [
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        ]
        self.assertEqual(len(coordinates), len(set(coordinates)))
        for entry in self.overlay["entries"]:
            self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")
            self.assertTrue(batch.has_semantic_text(entry["ko"]))
            self.assertTrue(batch.has_hangul_syllable(entry["ko"]))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(entry["ko"]))

        self.assertEqual(6018, self.evidence["entry_count"])
        self.assertEqual(6018, self.review["entry_count"])
        self.assertTrue(self.validation["passed"])
        self.assertEqual(batch.EXPECTED_COUNTS, {
            key: self.validation["selection"][key]
            for key in batch.EXPECTED_COUNTS
        })
        self.assertEqual(395, self.validation["selection"]["same_coordinate"])
        self.assertEqual(5623, self.validation["selection"]["source_hash_transfer"])
        self.assertEqual(EXPECTED_TARGET_SHA256, self.validation["offline_binary_validation"]["target_packed_sha256"])
        self.assertFalse(self.validation["offline_binary_validation"]["installed_game_file_written"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))

        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            self.assertEqual(expected_hash, digest(path))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.script_counts(path.read_text(encoding="utf-8")))

    def test_switch_end_padding_is_read_only_and_structurally_safe(self) -> None:
        zip_path = batch.REPO_ROOT / batch.SWITCH_ZIP_RELATIVE
        before = digest(zip_path)
        with zipfile.ZipFile(zip_path) as archive:
            switch_packed = archive.read(batch.SWITCH_MEMBER)
        _header, raw = decompress_wrapper(switch_packed)
        self.assertEqual(0x16DD42, len(raw))
        with self.assertRaises(MsgGameFormatError):
            parse_raw_msggame(raw)
        padded = raw + b"\0\0"
        parsed = parse_raw_msggame(padded)
        self.assertEqual(0x16DD42, parsed.blocks[-1].offset + parsed.blocks[-1].size)
        self.assertEqual(b"\0\0", parsed.blocks[-1].gap_after)
        self.assertEqual(padded, batch.rebuild_raw_msggame(parsed))
        self.assertEqual(before, digest(zip_path))

    def test_existing_progress_and_local_catalog_coordinates_are_excluded(self) -> None:
        existing = batch.collect_existing_pk_coordinates(batch.REPO_ROOT / batch.PROGRESS_RELATIVE)
        self.assertEqual(3300, len(existing["coordinates"]))
        selected = {
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in self.overlay["entries"]
        }
        self.assertTrue(selected.isdisjoint(existing["coordinates"]))
        self.assertEqual(23, len(existing["progress_overlay_globs"]))
        self.assertIn(
            "workstreams/msggame/public/msggame_ko_system_messages_b06r3841_3930.v0.22.json",
            existing["all_paths"],
        )
        self.assertNotIn(batch.SELF_OVERLAY_RELATIVE, existing["all_paths"])

    def test_final_progress_catalog_registers_this_overlay_exactly_once(self) -> None:
        """The published catalog counts this batch without feeding it back into selection."""

        existing = batch.collect_existing_pk_coordinates(batch.REPO_ROOT / batch.PROGRESS_RELATIVE)
        registration = existing["self_overlay_registration"]
        self.assertEqual(batch.SELF_OVERLAY_RELATIVE, registration["expected_relative_path"])
        self.assertEqual(1, registration["configured_reference_count"])
        self.assertEqual(1, registration["resolved_reference_count"])
        self.assertEqual([batch.SELF_OVERLAY_RELATIVE], registration["resolved_paths"])
        self.assertTrue(registration["excluded_from_prior_existing_coordinates"])
        self.assertEqual(
            1,
            sum(pattern == batch.SELF_OVERLAY_RELATIVE for pattern in existing["progress_overlay_globs"]),
        )

    def test_isolated_builds_are_byte_identical_and_do_not_modify_sources(self) -> None:
        before = source_digests()
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("isolated_a", "isolated_b")]
            results = [
                batch.build(
                    type(
                        "Args",
                        (),
                        {
                            "switch_zip": batch.REPO_ROOT / batch.SWITCH_ZIP_RELATIVE,
                            "base_jp": batch.GAME_ROOT / batch.SOURCE_PINS["base_jp"]["logical_path"],
                            "pk_jp": batch.GAME_ROOT / batch.SOURCE_PINS["pk_jp"]["logical_path"],
                            "pk_sc": batch.GAME_ROOT / batch.SOURCE_PINS["pk_sc"]["logical_path"],
                            "progress": batch.REPO_ROOT / batch.PROGRESS_RELATIVE,
                            "out_root": root,
                        },
                    )()
                )
                for root in roots
            ]
            self.assertEqual(6018, results[0]["entry_count"])
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative, expected_hash in EXPECTED_HASHES.items():
                self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())
                self.assertEqual(expected_hash, digest(roots[0] / relative))
        self.assertEqual(before, source_digests())

    def test_final_overlay_rebuild_matches_pinned_pk_target(self) -> None:
        source_path = batch.GAME_ROOT / batch.RESOURCE
        before = digest(source_path)
        rebuilt, manifest = batch.apply_overlay_blob(source_path.read_bytes(), self.overlay)
        self.assertEqual(6018, manifest["entry_count"])
        self.assertEqual(EXPECTED_TARGET_SHA256, hashlib.sha256(rebuilt).hexdigest().upper())
        self.assertEqual({"OK"}, set(manifest["checks"].values()))
        self.assertEqual(before, digest(source_path))


if __name__ == "__main__":
    unittest.main()
