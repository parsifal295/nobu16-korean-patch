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

import build_switch_msgdata_v11 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "1C748373DFF712E52BA11459E032E3611ED5151EF18633E592452D3A2A78392E",
    f"evidence/{batch.EVIDENCE_NAME}": "3C82905218666C80CE12A699CD2FF20C998D7928CF8850AF68C7B9B7E108E713",
    f"review/{batch.REVIEW_NAME}": "44DCCFA27F56BF2C4212068F92D19AE5849A0CD85CD8EB7B29A9319381478639",
    batch.VALIDATION_NAME: "52D91312457EF4E58EE10F96F33323DEADC4DDE8E70B0F3976488C1527E28CBD",
}

EXPECTED_TARGET = {
    "resource": "MSG_PK/SC/msgdata.bin",
    "entry_count": 16176,
    "complete_target_included": False,
    "packed_size": 476013,
    "packed_sha256": "69BCAF13452A25A78BF8AF9ED78C472D6255FFC6B578E150135347F1628F626E",
    "raw_size": 474128,
    "raw_sha256": "F0661F229EC1DEC68AC167380D016AB9CA3D3FD0B8FBBF63A1AB0D14BF4B4519",
    "parse_rebuild_round_trip": True,
    "wrapper_round_trip": True,
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class SwitchMsgdataV11Tests(unittest.TestCase):
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

    def build_args(self, out_root: Path) -> Namespace:
        return Namespace(
            switch_zip=batch.PATCH_ROOT
            / "tmp"
            / "third_party_switch_v11"
            / "NobunagaShinsei_KoreanPatch_v1.1.zip",
            base_jp_strdata=batch.WORKSPACE_ROOT / "MSG" / "JP" / "strdata.bin",
            stock_pk_jp=batch.WORKSPACE_ROOT / "MSG_PK" / "JP" / "msgdata.bin",
            stock_pk_sc=batch.WORKSPACE_ROOT / "MSG_PK" / "SC" / "msgdata.bin",
            progress=batch.PATCH_ROOT / "data" / "public" / "translation_progress.v0.1.json",
            out_root=out_root,
        )

    def source_paths(self) -> list[Path]:
        args = self.build_args(WORKSTREAM_DIR)
        return [
            args.switch_zip,
            args.base_jp_strdata,
            args.stock_pk_jp,
            args.stock_pk_sc,
            args.progress,
        ]

    def test_scope_provenance_and_strict_selection_are_pinned(self) -> None:
        ids = [entry["id"] for entry in self.overlay["entries"]]
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, len(ids))
        self.assertEqual(ids, sorted(ids))
        self.assertEqual(batch.EXPECTED_SELECTED_IDS_SHA256, batch.ids_sha256(ids))
        self.assertEqual(batch.EXPECTED_SELECTED_COUNT, self.validation["scope"]["selected_entry_count"])
        self.assertEqual(batch.SOURCE_RELEASE["release_url"], self.validation["source_release"]["release_url"])
        self.assertEqual("v1.1", self.validation["source_release"]["tag"])
        self.assertEqual("GitHub user snake7594", self.validation["source_release"]["author_attribution"])
        strict = self.validation["strict_selection"]
        self.assertEqual(20807, strict["convergent_pk_jp_candidate_count"])
        self.assertEqual(8, strict["source_script_exclusion"]["count"])
        self.assertEqual(
            [22617, 24378, 24379, 24380, 24381, 24382, 24383, 24384],
            strict["source_script_exclusion"]["ids"],
        )
        self.assertEqual(140, strict["pk_sc_invariant_exclusion_count"])
        self.assertEqual(4483, strict["existing_overlay_collision_count"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            self.assertEqual(expected, digest(path))
            self.assertEqual(
                {"cjk_unified_count": 0, "kana_count": 0},
                batch.script_counts(path.read_text(encoding="utf-8")),
            )
        self.assertTrue(self.validation["passed"])
        self.assertFalse(self.validation["safety"]["zip_included"])
        self.assertFalse(self.validation["target_reconstruction"]["complete_target_included"])

    def test_translation_progress_overlays_are_pinned_and_disjoint(self) -> None:
        args = self.build_args(WORKSTREAM_DIR)
        claimed, snapshot = batch.load_existing_overlay_coordinates(args.progress)
        selected = {entry["id"] for entry in self.overlay["entries"]}
        self.assertFalse(selected.intersection(claimed))
        self.assertEqual(snapshot, self.validation["existing_overlay_exclusion"])
        self.assertEqual(1, snapshot["overlay_globs"].count(batch.SELF_OVERLAY_LOGICAL_PATH))
        self.assertEqual(
            {
                "logical_path": batch.SELF_OVERLAY_LOGICAL_PATH,
                "sha256": digest(WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME),
                "entry_count": batch.EXPECTED_SELECTED_COUNT,
                "ids_sha256": batch.EXPECTED_SELECTED_IDS_SHA256,
                "configured_exactly_once": True,
                "excluded_from_prior_claims": True,
            },
            snapshot["self_overlay_registration"],
        )
        self.assertNotIn(batch.SELF_OVERLAY_LOGICAL_PATH, snapshot["prior_overlay_globs"])
        self.assertEqual(4507, len(claimed))
        self.assertEqual(72, snapshot["cross_overlay_duplicate_coordinate_count"])

    def test_in_memory_target_reconstruction_is_deterministic_and_source_preserving(self) -> None:
        if not all(path.is_file() for path in self.source_paths()):
            self.skipTest("pinned external or stock inputs are intentionally absent")
        args = self.build_args(WORKSTREAM_DIR)
        before = {str(path): digest(path) for path in self.source_paths()}
        sc_packed, _, sc_table = batch._load_pk_msgdata(
            args.stock_pk_sc, batch.PK_SC_MSGDATA_PIN, "PK SC msgdata"
        )
        target_a = batch.reconstruct_sc_target(sc_packed, sc_table, self.overlay["entries"])
        target_b = batch.reconstruct_sc_target(sc_packed, sc_table, self.overlay["entries"])
        self.assertEqual(EXPECTED_TARGET, target_a)
        self.assertEqual(target_a, target_b)
        self.assertEqual(EXPECTED_TARGET, self.validation["target_reconstruction"])
        self.assertEqual(before, {str(path): digest(path) for path in self.source_paths()})

    def test_isolated_rebuild_is_byte_identical(self) -> None:
        if not all(path.is_file() for path in self.source_paths()):
            self.skipTest("pinned external or stock inputs are intentionally absent")
        before = {str(path): digest(path) for path in self.source_paths()}
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            for name in ("a", "b"):
                out_root = root / name
                batch.build(self.build_args(out_root))
                outputs.append(out_root)
            for relative in EXPECTED_HASHES:
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_DIR / relative).read_bytes(), (outputs[0] / relative).read_bytes())
        self.assertEqual(before, {str(path): digest(path) for path in self.source_paths()})


if __name__ == "__main__":
    unittest.main()
