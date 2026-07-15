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

import build_msgbre_batch10 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "6D74AE6E3D86F09C0A1356B0D25D97B1B2BEBC319A288544D31714039BAA2430",
    f"evidence/{batch.EVIDENCE_NAME}": "8E00A3C7C555EE75CBFC77D410E880CFAFCE5C212444331A7DCFA9D785D3195E",
    f"review/{batch.REVIEW_NAME}": "A04CD73D402B313835B7589E94655201C91A1BDF5C09A5028A16D64930F4A025",
    batch.VALIDATION_NAME: "A5271AA25C64A8293934273E628DD85631DAD94B83BDB1F1A14FE3DC8B2AE49A",
}

EXPECTED_TARGET = {
    "resource": "MSG_PK/SC/msgbre.bin",
    "entry_count": 45,
    "complete_target_included": False,
    "packed_size": 293909,
    "packed_sha256": "D7F0A47AD68919674B209D23A711B788EDFFE2A2347B043A0FD85F53489BB973",
    "raw_size": 292736,
    "raw_sha256": "BFBA8AED25F3DEC8031B19CDEA1E4A81BEDA7B8731069BB179A56BDA0D4225DA",
    "parse_rebuild_round_trip": True,
    "wrapper_round_trip": True,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgbreBatch10Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads(
            (WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8")
        )
        cls.evidence = json.loads(
            (WORKSTREAM_DIR / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8")
        )
        cls.review = json.loads(
            (WORKSTREAM_DIR / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8")
        )
        cls.validation = json.loads(
            (WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8")
        )

    def stock_paths(self) -> dict[str, Path]:
        return {
            language: batch.WORKSPACE_ROOT / pin["logical_path"]
            for language, pin in batch.SOURCE_PINS.items()
        }

    def test_scope_and_overlay_are_complete(self) -> None:
        expected = list(range(746, 791))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(expected, [entry["id"] for entry in self.overlay["entries"]])
        self.assertEqual(45, self.overlay["entry_count"])
        self.assertEqual(791, batch.NEXT_START_ID)
        self.assertEqual(
            "fixed_contiguous_parallel_slice",
            self.validation["scope"]["natural_boundary"]["selection_policy"],
        )
        self.assertEqual(745, self.validation["scope"]["natural_boundary"]["previous_batch_end_id"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            self.assertEqual(expected, digest(path))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.shared.script_counts(path.read_text(encoding="utf-8")),
            )
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])
        self.assertEqual(135, self.validation["source_alignment"]["selected_reference_hash_count"])

    def test_existing_overlay_coordinates_are_pinned_and_non_overlapping(self) -> None:
        observed = batch.verify_previous_overlays()
        self.assertEqual(9, len(observed))
        self.assertEqual(0, self.validation["prior_overlay_coordination"]["coordinate_collisions"])
        self.assertTrue(self.validation["prior_overlay_coordination"]["all_prior_hashes_unchanged"])
        self.assertEqual(observed, self.validation["prior_overlay_coordination"]["overlays"])

    def test_target_reconstruction_is_deterministic_and_source_preserving(self) -> None:
        paths = self.stock_paths()
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        source_before = {language: digest(path) for language, path in paths.items()}
        sc_packed, _, sc_table = batch.base.load_source(paths["SC"], "SC")
        target_a = batch.reconstruct_sc_target(sc_packed, sc_table)
        target_b = batch.reconstruct_sc_target(sc_packed, sc_table)
        self.assertEqual(EXPECTED_TARGET, target_a)
        self.assertEqual(target_a, target_b)
        self.assertEqual(EXPECTED_TARGET, self.validation["target_reconstruction"])
        self.assertFalse(target_a["complete_target_included"])
        self.assertEqual(source_before, {language: digest(path) for language, path in paths.items()})

    def test_isolated_rebuild_is_byte_identical(self) -> None:
        paths = self.stock_paths()
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        source_before = {language: digest(path) for language, path in paths.items()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            for name in ("a", "b"):
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
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_DIR / relative).read_bytes(), (outputs[0] / relative).read_bytes())
        self.assertEqual(source_before, {language: digest(path) for language, path in paths.items()})


if __name__ == "__main__":
    unittest.main()
