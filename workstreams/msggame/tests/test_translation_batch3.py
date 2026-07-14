from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_ROOT))

import build_translation_batch3 as batch  # noqa: E402
from build_literal_overlay import apply_overlay_blob  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "CFB91FBB1C9F962183908595C2DFADD3A60B04BB3469113FF68324EC053C34CA"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "AAECBCA5E046DE8AFA56A4786B846439A4E9074D6623BB49DB3E8D3E2FB7C269"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "A31C00E405F88E2863E48818EDA475E2C51DC0C732236E9A7EE0F0A6291C7D99"
    ),
    batch.VALIDATION_NAME: (
        "C306DC3C4CE14B31834B881AA4A66613477D85CCC936A94412B6FAF5E398E8F4"
    ),
}
EXPECTED_TARGET_SHA256 = (
    "80FCACB1565F10E4A94DBDC21DBCB5CC750B9271A5E34E900FDCAB3C5E50DD2B"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AssertionError(f"{path} root is not an object")
    return value


def walk_keys(value: object) -> list[str]:
    keys: list[str] = []
    if isinstance(value, dict):
        for key, child in value.items():
            keys.append(str(key))
            keys.extend(walk_keys(child))
    elif isinstance(value, list):
        for child in value:
            keys.extend(walk_keys(child))
    return keys


class MsggameTranslationBatch3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load_json(WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME)
        cls.evidence = load_json(WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load_json(WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME)
        cls.validation = load_json(WORKSTREAM_ROOT / batch.VALIDATION_NAME)

    def test_scope_is_exactly_150_linguistic_literals(self) -> None:
        coordinates = batch.selected_coordinates()
        self.assertEqual(150, len(coordinates))
        self.assertEqual(115, len(batch.selected_record_keys()))
        self.assertEqual((2, 298, 0), coordinates[0])
        self.assertEqual((2, 565, 0), coordinates[-1])
        self.assertEqual((2, 566, 0), batch.NEXT_COORDINATE)
        self.assertEqual(set(), set(batch.SKIPPED_CANDIDATES))
        self.assertTrue(set(coordinates).isdisjoint(batch.SKIPPED_CANDIDATES))
        self.assertEqual(150, self.validation["selection"]["scanned_visible_candidate_count"])
        self.assertEqual(0, self.validation["selection"]["nonlinguistic_visible_candidate_skips"])

    def test_overlay_is_source_free_and_literal_builder_compatible(self) -> None:
        self.assertEqual(
            {
                "schema",
                "overlay_id",
                "resource",
                "base_language",
                "defaults",
                "entry_count",
                "distribution_policy",
                "stock_sc",
                "entries",
            },
            set(self.overlay),
        )
        self.assertEqual("nobu16.kr.msggame-literal-overlay.v1", self.overlay["schema"])
        self.assertEqual("MSG_PK/SC/msggame.bin", self.overlay["resource"])
        self.assertEqual({"status": "translated"}, self.overlay["defaults"])
        self.assertEqual(150, self.overlay["entry_count"])
        entries = self.overlay["entries"]
        coordinates = [
            (entry["block_id"], entry["record_id"], entry["literal_id"])
            for entry in entries
        ]
        self.assertEqual(batch.selected_coordinates(), coordinates)
        self.assertTrue(set(coordinates).isdisjoint(batch.SKIPPED_CANDIDATES))
        required = {
            "block_id",
            "record_id",
            "literal_id",
            "source_sc_utf16le_sha256",
            "ko",
        }
        for coordinate, entry in zip(coordinates, entries, strict=True):
            with self.subTest(coordinate=coordinate):
                self.assertEqual(required, set(entry))
                self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")
                self.assertNotIn("\x00", entry["ko"])
        scan = batch.previous.script_counts(json.dumps(self.overlay, ensure_ascii=False))
        self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, scan)

    def test_alignment_uses_same_record_context_and_records_skip_reasons(self) -> None:
        self.assertEqual(115, self.evidence["record_count"])
        self.assertEqual(115, len(self.evidence["records"]))
        differing_shapes = 0
        for record in self.evidence["records"]:
            with self.subTest(record=(record["block_id"], record["record_id"])):
                self.assertEqual(set(batch.LANGUAGES), set(record["references"]))
                self.assertTrue(record["manual_same_record_semantic_crosscheck"])
                self.assertFalse(record["cross_language_literal_id_alignment_used"])
                if not record["literal_shape_aligned_across_languages"]:
                    differing_shapes += 1
                for reference in record["references"].values():
                    self.assertRegex(reference["record_data_sha256"], r"^[0-9A-F]{64}$")
                    self.assertRegex(reference["literal_hash_chain_sha256"], r"^[0-9A-F]{64}$")
        self.assertGreater(differing_shapes, 0)
        skipped = self.evidence["scope"]["skipped_candidates"]
        self.assertEqual([], skipped)
        forbidden_keys = {
            "text",
            "source_text",
            "original_text",
            "sc_text",
            "jp_text",
            "en_text",
            "tc_text",
        }
        self.assertTrue(forbidden_keys.isdisjoint(walk_keys(self.evidence)))
        self.assertFalse(self.evidence["contains_commercial_source_text"])

    def test_validation_records_binary_repack_and_safety_gates(self) -> None:
        self.assertTrue(self.validation["passed"])
        invariants = self.validation["replacement_invariants"]
        self.assertEqual(150, invariants["checked"])
        self.assertEqual(0, invariants["failures"])
        binary = self.validation["offline_binary_validation"]
        self.assertEqual(EXPECTED_TARGET_SHA256, binary["target_packed_sha256"])
        self.assertTrue(binary["literal_coordinates_preserved"])
        self.assertTrue(binary["record_coordinates_preserved"])
        self.assertTrue(binary["opaque_record_bytecode_preserved"])
        self.assertTrue(binary["top_level_offsets_recomputed_and_aligned"])
        self.assertTrue(binary["raw_parse_rebuild_byte_exact"])
        self.assertTrue(binary["skipped_candidates_unchanged"])
        self.assertFalse(binary["installed_game_file_written"])
        self.assertTrue(all(value is False for value in self.validation["safety"].values()))
        self.assertEqual(150, self.review["entry_count"])
        self.assertEqual(150, sum(entry["human_review_required"] for entry in self.review["entries"]))
        self.assertEqual(0, sum(entry["runtime_reviewed"] for entry in self.review["entries"]))

    def test_artifacts_are_pinned_and_have_no_commercial_source_script(self) -> None:
        for relative, expected_hash in EXPECTED_HASHES.items():
            path = WORKSTREAM_ROOT / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                self.assertEqual(
                    {"cjk_unified_count": 0, "kana_count": 0},
                    batch.previous.script_counts(path.read_text(encoding="utf-8")),
                )

    def test_a_b_builds_and_offline_binaries_are_byte_identical(self) -> None:
        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        source_before = {language: digest(path) for language, path in source_paths.items()}
        with tempfile.TemporaryDirectory() as temporary:
            roots = [Path(temporary) / name for name in ("isolated_a", "isolated_b")]
            results = []
            for root in roots:
                results.append(
                    batch.build(
                        Namespace(
                            stock_sc=source_paths["SC"],
                            stock_jp=source_paths["JP"],
                            stock_en=source_paths["EN"],
                            stock_tc=source_paths["TC"],
                            out_root=root,
                        )
                    )
                )
            self.assertEqual(EXPECTED_TARGET_SHA256, results[0]["target_packed_sha256"])
            self.assertEqual(results[0]["target_packed_sha256"], results[1]["target_packed_sha256"])
            for relative, expected_hash in EXPECTED_HASHES.items():
                with self.subTest(relative=relative):
                    self.assertEqual((roots[0] / relative).read_bytes(), (roots[1] / relative).read_bytes())
                    self.assertEqual((roots[0] / relative).read_bytes(), (WORKSTREAM_ROOT / relative).read_bytes())
                    self.assertEqual(expected_hash, digest(roots[0] / relative))
        self.assertEqual(
            source_before,
            {language: digest(path) for language, path in source_paths.items()},
        )

    def test_scope_is_the_next_150_visible_sc_literals(self) -> None:
        source_paths = {
            language: batch.WORKSPACE_ROOT / batch.SOURCE_PATHS[language]
            for language in batch.LANGUAGES
        }
        if not all(path.is_file() for path in source_paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        loaded = batch.previous.load_sources(source_paths)
        records = batch.previous._record_map(loaded["SC"]["parsed"].archive)
        scanned = []
        for record_id in range(298, 566):
            literals = batch.previous.parse_record_literals(records[(2, record_id)])
            if not literals or not all(
                batch.previous.is_visible_translation_candidate(item.text)
                for item in literals
            ):
                continue
            scanned.extend(
                (2, record_id, literal.literal_id) for literal in literals
            )
        self.assertEqual(150, len(scanned))
        self.assertEqual(batch.selected_coordinates(), scanned)

    def test_final_overlay_rebuilds_with_shared_builder(self) -> None:
        source_path = batch.WORKSPACE_ROOT / batch.RESOURCE
        if not source_path.is_file():
            self.skipTest("commercial stock SC resource is intentionally absent")
        before = digest(source_path)
        rebuilt, manifest = apply_overlay_blob(source_path.read_bytes(), self.overlay)
        self.assertEqual(150, manifest["entry_count"])
        self.assertEqual(EXPECTED_TARGET_SHA256, hashlib.sha256(rebuilt).hexdigest().upper())
        self.assertEqual({"OK"}, set(manifest["checks"].values()))
        self.assertFalse(manifest["installed_game_file_written"])
        self.assertEqual(before, digest(source_path))


if __name__ == "__main__":
    unittest.main()
