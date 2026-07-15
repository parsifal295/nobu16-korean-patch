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

import build_msgbre_batch8 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "6791F39371E7C34F2792AE03EB88CD3CEB0FA0980D21178EFF4A86B7793063BA",
    f"evidence/{batch.EVIDENCE_NAME}": "9B4D96923E47D6AED00FC202D4653D990A3EEB474B0ED024B193229F93761E59",
    f"review/{batch.REVIEW_NAME}": "FF5A6C659EF1420590B633345C625D2F0A811818AB0377D351C85DCF26259DBC",
    batch.VALIDATION_NAME: "D785B303EBC266562BFBF687CD9FCC2061A4180789FCD5B65E5E84865DA07975",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgbreBatch8Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads((WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM_DIR / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM_DIR / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"))

    def test_scope_and_overlay_are_complete(self) -> None:
        expected = list(range(656, 701))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(expected, [entry["id"] for entry in self.overlay["entries"]])
        self.assertEqual(45, self.overlay["entry_count"])
        self.assertEqual(701, batch.NEXT_START_ID)
        self.assertEqual("fixed_contiguous_parallel_slice", self.validation["scope"]["natural_boundary"]["selection_policy"])

    def test_public_artifacts_are_source_free_and_pinned(self) -> None:
        for relative, expected in EXPECTED_HASHES.items():
            path = WORKSTREAM_DIR / relative
            self.assertEqual(expected, digest(path))
            self.assertEqual({"cjk_unified_count": 0, "kana_count": 0}, batch.shared.script_counts(path.read_text(encoding="utf-8")))
        self.assertTrue(self.validation["passed"])
        self.assertEqual(0, self.validation["replacement_invariants"]["failures"])

    def test_isolated_rebuild_is_byte_identical(self) -> None:
        paths = {language: batch.WORKSPACE_ROOT / pin["logical_path"] for language, pin in batch.SOURCE_PINS.items()}
        if not all(path.is_file() for path in paths.values()):
            self.skipTest("commercial stock resources are intentionally absent")
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            outputs = []
            for name in ("a", "b"):
                out_root = root / name
                batch.build(Namespace(stock_sc=paths["SC"], stock_jp=paths["JP"], stock_en=paths["EN"], out_root=out_root))
                outputs.append(out_root)
            for relative in EXPECTED_HASHES:
                self.assertEqual((outputs[0] / relative).read_bytes(), (outputs[1] / relative).read_bytes())
                self.assertEqual((WORKSTREAM_DIR / relative).read_bytes(), (outputs[0] / relative).read_bytes())


if __name__ == "__main__":
    unittest.main()
