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

import build_msgbre_batch6 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "0FB3F6F777E5110507EB4782C5B7C5E2B61EC50FBF9E8314E5FF2491C9D6ACD2",
    f"evidence/{batch.EVIDENCE_NAME}": "3E01B114901D3BE70497082514E02C8D5079AB6868974F55C783349103037841",
    f"review/{batch.REVIEW_NAME}": "37A371AEB1E2663CC5E1CA232951D820F92A344AF96774B57275B01F033CDB8B",
    batch.VALIDATION_NAME: "356127552FD5846F5ECCFA2152A46C4837FC770DBCB22E35A2B73CE94933D217",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgbreBatch6Tests(unittest.TestCase):
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

    def test_scope_and_overlay_are_complete(self) -> None:
        expected = list(range(566, 611))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(611, batch.NEXT_START_ID)
        self.assertEqual(expected, [entry["id"] for entry in self.overlay["entries"]])
        self.assertEqual(45, self.overlay["entry_count"])
        self.assertEqual(45, self.evidence["entry_count"])
        self.assertEqual(45, self.review["entry_count"])
        self.assertEqual("fixed_contiguous_parallel_slice", self.validation["scope"]["natural_boundary"]["selection_policy"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            self.assertEqual(expected, digest(path))
            counts = batch.shared.script_counts(path.read_text(encoding="utf-8"))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, counts)
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])

    def test_isolated_rebuild_is_byte_identical(self) -> None:
        paths = {
            language: batch.WORKSPACE_ROOT / pin["logical_path"]
            for language, pin in batch.SOURCE_PINS.items()
        }
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
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
                self.assertEqual(
                    (outputs[0] / relative).read_bytes(),
                    (outputs[1] / relative).read_bytes(),
                )
                self.assertEqual(
                    (WORKSTREAM_DIR / relative).read_bytes(),
                    (outputs[0] / relative).read_bytes(),
                )


if __name__ == "__main__":
    unittest.main()
