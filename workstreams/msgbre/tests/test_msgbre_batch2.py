from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_DIR = TEST_PATH.parents[1]
sys.path.insert(0, str(WORKSTREAM_DIR))

import build_msgbre_batch2 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": (
        "FDB2511970F1E8CEF194E661CBCE3F8D912B372382BCFD89129FD1F8B309A4D3"
    ),
    f"evidence/{batch.EVIDENCE_NAME}": (
        "BB7BCEE074FC3D9A42B1E57CDD0CE635DE2F1C35CC755911379220E5399F7087"
    ),
    f"review/{batch.REVIEW_NAME}": (
        "B6B281B77CF981CEF76A250420DD83E7ABC9CE8A06B0FF7F5724EF674D8ABF82"
    ),
    batch.VALIDATION_NAME: (
        "D24AB6A3B575AB25B81209C743AE121E1D197F974A086376003F1A4581DCE2C0"
    ),
}

EXPECTED_V01_HASHES = {
    "public/msgbre_ko_biographies_0000_0128.v0.1.json": (
        "DDD87FDF972F4EE907D310387074D0879E620C61B15C26B7F8A7FBA40BE52E00"
    ),
    "evidence/alignment_evidence.v0.1.json": (
        "1E6AE3EC563338F371CA0C4E02DEB6B6EC3AA78DF5AAC7E4446174F6C1E052F6"
    ),
    "review/review_index.v0.1.json": (
        "8D5003CAFDF9BCCC460A52B2125B549C8B9EE6CE31B4203D56D49F6855E45438"
    ),
    "validation.v0.1.json": (
        "FE86E50A1F006DA4773862E2923AF78DDF3521D5C73E1153EE8E0A0586A70812"
    ),
}


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


class MsgbreBatch2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load_json(WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME)
        cls.evidence = load_json(WORKSTREAM_DIR / "evidence" / batch.EVIDENCE_NAME)
        cls.review = load_json(WORKSTREAM_DIR / "review" / batch.REVIEW_NAME)
        cls.validation = load_json(WORKSTREAM_DIR / batch.VALIDATION_NAME)

    def test_scope_is_122_consecutive_biographies_at_natural_boundary(self) -> None:
        expected = list(range(129, 251))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(122, len(expected))
        self.assertEqual(251, batch.NEXT_START_ID)
        self.assertEqual(129, self.evidence["scope"]["start_id"])
        self.assertEqual(250, self.evidence["scope"]["end_id"])
        self.assertEqual(251, self.evidence["scope"]["next_start_id"])

    def test_overlay_entries_contain_only_id_sc_hash_and_korean(self) -> None:
        self.assertEqual("MSG_PK/SC/msgbre.bin", self.overlay["resource"])
        self.assertEqual(122, self.overlay["entry_count"])
        entries = self.overlay["entries"]
        self.assertEqual(list(range(129, 251)), [entry["id"] for entry in entries])
        for entry in entries:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual(
                    {"id", "source_sc_utf16le_sha256", "ko"}, set(entry)
                )
                self.assertRegex(entry["source_sc_utf16le_sha256"], r"^[0-9A-F]{64}$")
                self.assertEqual(batch.TRANSLATIONS[entry["id"]], entry["ko"])

    def test_alignment_is_hash_only_for_sc_jp_en(self) -> None:
        self.assertEqual(122, self.evidence["entry_count"])
        self.assertEqual(122, len(self.evidence["entries"]))
        for entry in self.evidence["entries"]:
            with self.subTest(entry_id=entry["id"]):
                self.assertEqual({"SC", "JP", "EN"}, set(entry["references"]))
                self.assertIs(True, entry["manual_semantic_crosscheck"])
                for reference in entry["references"].values():
                    self.assertEqual({"utf16le_sha256", "structure"}, set(reference))
                    self.assertRegex(reference["utf16le_sha256"], r"^[0-9A-F]{64}$")
        self.assertFalse(self.evidence["contains_commercial_source_text"])
        forbidden = {"text", "source_text", "original_text", "sc_text", "jp_text", "en_text"}
        self.assertTrue(forbidden.isdisjoint(walk_keys(self.evidence)))

    def test_artifacts_are_pinned_source_free_and_v01_is_unchanged(self) -> None:
        for relative, expected_hash in {**EXPECTED_HASHES, **EXPECTED_V01_HASHES}.items():
            path = WORKSTREAM_DIR / relative
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(path))
                if relative in EXPECTED_HASHES:
                    counts = batch.shared.script_counts(path.read_text(encoding="utf-8"))
                    self.assertEqual(0, counts["cjk_unified_count"])
                    self.assertEqual(0, counts["kana_count"])

    def test_invariants_review_state_and_safety_are_recorded(self) -> None:
        self.assertIs(True, self.validation["passed"])
        invariants = self.validation["replacement_invariants"]
        self.assertEqual(122, invariants["checked"])
        self.assertEqual(122, invariants["custom_bracket_placeholder_checks"])
        self.assertEqual(0, invariants["failures"])
        self.assertEqual(
            {
                "printf_tokens",
                "unknown_percent_count",
                "leading_whitespace",
                "trailing_whitespace",
                "esc_sequences_in_order",
                "control_characters",
                "line_break_sequence",
                "private_use_codepoints",
                "custom_bracket_placeholders_in_order",
            },
            set(invariants["preserved"]),
        )
        self.assertEqual(122, self.review["entry_count"])
        self.assertEqual(122, self.validation["translation_status"]["human_review_required"])
        self.assertEqual(0, self.validation["translation_status"]["runtime_reviewed"])
        safety = self.validation["safety"]
        for key in (
            "installed_game_files_modified",
            "font_files_modified",
            "installer_modified",
            "root_readme_modified",
            "common_builder_modified",
            "other_workstreams_modified",
            "existing_v01_artifacts_modified",
        ):
            self.assertFalse(safety[key])

    def test_isolated_a_b_builds_are_byte_identical_when_sources_exist(self) -> None:
        paths = {
            language: batch.WORKSPACE_ROOT / pin["logical_path"]
            for language, pin in batch.SOURCE_PINS.items()
        }
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs: list[Path] = []
            for name in ("isolated_a", "isolated_b"):
                out_root = root / name
                batch.build(
                    Namespace(
                        stock_sc=paths["SC"],
                        stock_jp=paths["JP"],
                        stock_en=paths["EN"],
                        out_root=out_root,
                    )
                )
                outputs.append(out_root)
            for relative in EXPECTED_HASHES:
                with self.subTest(relative=relative):
                    self.assertEqual(
                        (outputs[0] / relative).read_bytes(),
                        (outputs[1] / relative).read_bytes(),
                    )


if __name__ == "__main__":
    unittest.main()
