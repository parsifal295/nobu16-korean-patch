from __future__ import annotations

import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path


TEST_PATH = Path(__file__).resolve()
WORKSTREAM_ROOT = TEST_PATH.parents[1]
REPO_ROOT = TEST_PATH.parents[3]
GAME_ROOT = REPO_ROOT.parent
TOOLS_ROOT = REPO_ROOT / "tools"
sys.path.insert(0, str(WORKSTREAM_ROOT))
sys.path.insert(0, str(TOOLS_ROOT))

import build_common_message_overlay as common  # noqa: E402
import build_ev_strdata_batch1 as shared  # noqa: E402
import build_ev_strdata_batch25 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "34F787D2A41FE1525BCCE6DE5635E6D39B8E9F47887AAB94B19505381E83F0C7",
    f"evidence/{batch.EVIDENCE_NAME}": "D8AA2254479D7D09AE21A589F85A47B587E642D3847E31DB6541B45C2DBA0F1D",
    f"review/{batch.REVIEW_NAME}": "EEBC36F04FCF490124061D194EC1E85A51EB9FF8A58B3D77FD3BFB680257DC9B",
    batch.VALIDATION_NAME: "BDFBFBD186929BE4C431EC957F356881CAD59AF9D8EC60A3ED886363FD7FE0FA",
}
STOCK_AVAILABLE = all(
    (GAME_ROOT / "MSG" / language / "ev_strdata.bin").is_file()
    for language in shared.LANGUAGES
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load(relative: str) -> dict[str, object]:
    return json.loads(
        (WORKSTREAM_ROOT / relative).read_text(encoding="utf-8"),
        object_pairs_hook=common.strict_object,
    )


class EvStrDataBatch25Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = load(f"public/{batch.OVERLAY_NAME}")
        cls.evidence = load(f"evidence/{batch.EVIDENCE_NAME}")
        cls.review = load(f"review/{batch.REVIEW_NAME}")
        cls.validation = load(batch.VALIDATION_NAME)

    def test_scope_is_exactly_the_next_88_display_entries(self) -> None:
        ids = [int(entry["id"]) for entry in self.overlay["entries"]]
        self.assertEqual(list(range(4751, 4839)), ids)
        self.assertEqual(88, self.overlay["entry_count"])
        self.assertEqual(4839, self.evidence["scope"]["next_display_id"])
        self.assertEqual(frozenset(), batch.CURRENT_EXCLUDED_IDS)
        self.assertEqual(0, self.validation["scope"]["deferred_internal_entry_count"])

    def test_overlay_contract_and_translation_invariants_are_recorded(self) -> None:
        original_allowlist = common.ALLOWED_RESOURCES
        common.ALLOWED_RESOURCES = original_allowlist | shared.SUPPORTED_RESOURCES
        try:
            resource, stock, entries = common.validate_overlay_shape(self.overlay)
        finally:
            common.ALLOWED_RESOURCES = original_allowlist
        self.assertEqual(shared.RESOURCE, resource)
        self.assertEqual(shared.STRING_COUNT, stock["string_count"])
        self.assertEqual(88, len(entries))
        self.assertEqual(88, self.validation["replacement_invariants"]["checked"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(
            batch.TRANSLATION_MAP_SHA256,
            self.validation["translation"]["translation_map_sha256"],
        )

    def test_alignment_and_review_risks_are_pinned(self) -> None:
        self.assertEqual(88, self.evidence["entry_count"])
        self.assertEqual(88, len(self.review["entries"]))
        flagged = {
            int(entry["id"])
            for entry in self.review["entries"]
            if "cross_language_structure_difference_review" in entry["uncertainty_flags"]
        }
        self.assertEqual(batch.CROSS_REFERENCE_STRUCTURE_DIFFERENCE_IDS, flagged)
        self.assertEqual(
            len(batch.TERMINOLOGY_REVIEW_IDS), self.review["terminology_review_count"]
        )
        self.assertEqual([], self.evidence["deferred_internal_groups"])
        self.assertFalse(self.evidence["previous_deferred_overlap"]["overlap_detected"])

    def test_artifacts_and_new_batch_files_are_source_free_and_pinned(self) -> None:
        paths = (
            WORKSTREAM_ROOT / "build_ev_strdata_batch25.py",
            WORKSTREAM_ROOT / "BATCH25_V0.25_README_KO.md",
            WORKSTREAM_ROOT / "public" / batch.OVERLAY_NAME,
            WORKSTREAM_ROOT / "evidence" / batch.EVIDENCE_NAME,
            WORKSTREAM_ROOT / "review" / batch.REVIEW_NAME,
            WORKSTREAM_ROOT / batch.VALIDATION_NAME,
            WORKSTREAM_ROOT / "tests" / "test_ev_strdata_batch25.py",
        )
        self.assertEqual(7, len(paths))
        for path in paths:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                self.assertEqual(
                    {"han_or_kana_count": 0, "embedded_nul_count": 0},
                    shared.source_free_counts(path.read_bytes()),
                )
        for relative, expected_hash in EXPECTED_HASHES.items():
            with self.subTest(relative=relative):
                self.assertEqual(expected_hash, digest(WORKSTREAM_ROOT / relative))

    @unittest.skipUnless(STOCK_AVAILABLE, "installed SC/JP/TC stock resources are unavailable")
    def test_stock_replay_is_deterministic_and_install_is_unchanged(self) -> None:
        source_paths = [
            GAME_ROOT / "MSG" / language / "ev_strdata.bin"
            for language in shared.LANGUAGES
        ]
        before = {path: digest(path) for path in source_paths}
        loaded, _ = shared.load_sources(GAME_ROOT)
        ids = sorted(batch.TRANSLATIONS)
        self.assertEqual(
            batch.SOURCE_SC_HASHES_SHA256,
            shared.hash_json(
                [common.text_hash(loaded["SC"]["table"].texts[entry_id]) for entry_id in ids]
            ),
        )
        for language in shared.LANGUAGES:
            self.assertEqual(
                batch.NEXT_DISPLAY_REFERENCE_HASHES[language],
                common.text_hash(loaded[language]["table"].texts[batch.NEXT_DISPLAY_ID]),
            )
        with tempfile.TemporaryDirectory(prefix="nobu16-evstr25-test-") as temporary:
            result = batch.build_reproducibly(GAME_ROOT, Path(temporary))
            self.assertEqual(88, result["entry_count"])
            self.assertEqual(4839, result["next_display_id"])
            self.assertEqual(
                EXPECTED_HASHES,
                {
                    relative: hashlib.sha256(blob).hexdigest().upper()
                    for relative, blob in result["files"].items()
                },
            )
        self.assertEqual(before, {path: digest(path) for path in source_paths})


if __name__ == "__main__":
    unittest.main()
