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

import build_msgbre_batch11 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "B1FD769444B4BE226257FFF9E7245CD78392258FAB3A5219AE822F82341088D7",
    f"evidence/{batch.EVIDENCE_NAME}": "D83118AF876C1F24E7E5FAE86A0A28D3AD9072D4F2A12686BB51F7476AAEC870",
    f"review/{batch.REVIEW_NAME}": "ED52CDF83C0E543199BAAA9547C4A84094AAA949082198308AA185C919A4BFD7",
    batch.VALIDATION_NAME: "D405662862DF381BADA91163DC8A5CF130E7061A97D9FD6E2DD6BA0EE6061EB1",
}

EXPECTED_TARGET = {
    "resource": "MSG_PK/SC/msgbre.bin",
    "entry_count": 45,
    "complete_target_included": False,
    "packed_size": 293841,
    "packed_sha256": "5748F73A9DC9BD6DF3E67D78618C7FE8BFC2FE10E3B3B2D70B85448F3AD12997",
    "raw_size": 292668,
    "raw_sha256": "16DA0F3F7CB1BA3A09186C8107CC625AE943229993073A916E72CD27D5160919",
    "parse_rebuild_round_trip": True,
    "wrapper_round_trip": True,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgbreBatch11Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads(
            (WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8")
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
        expected = list(range(791, 836))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(expected, [entry["id"] for entry in self.overlay["entries"]])
        self.assertEqual(45, self.overlay["entry_count"])
        self.assertEqual(836, batch.NEXT_START_ID)
        self.assertEqual(790, self.validation["scope"]["natural_boundary"]["previous_batch_end_id"])

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
        self.assertEqual(10, len(observed))
        self.assertEqual(0, self.validation["prior_overlay_coordination"]["coordinate_collisions"])
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
