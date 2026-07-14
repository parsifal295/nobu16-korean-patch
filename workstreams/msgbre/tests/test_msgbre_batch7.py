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

import build_msgbre_batch7 as batch  # noqa: E402


EXPECTED_HASHES = {
    f"public/{batch.OVERLAY_NAME}": "82FCFE650D8AA0EBDC70AFEEFEDE2EE14049AB0EB1979464ACBDD10B69F9B72C",
    f"evidence/{batch.EVIDENCE_NAME}": "7AA23287DCFD99C75C3DA46D77D654C9ADEF591BE4606DD0C2293C08CDEF8692",
    f"review/{batch.REVIEW_NAME}": "3736F3A2818CB67CED774E616AC49C1C6127773D517F71E31E5DAEFFC3EA50A1",
    batch.VALIDATION_NAME: "0D9C9EEE4D28EE425A4FD6250D7BB208A1460A89C4DB21B0BABFE29F20006843",
}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


class MsgbreBatch7Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.overlay = json.loads((WORKSTREAM_DIR / "public" / batch.OVERLAY_NAME).read_text(encoding="utf-8"))
        cls.evidence = json.loads((WORKSTREAM_DIR / "evidence" / batch.EVIDENCE_NAME).read_text(encoding="utf-8"))
        cls.review = json.loads((WORKSTREAM_DIR / "review" / batch.REVIEW_NAME).read_text(encoding="utf-8"))
        cls.validation = json.loads((WORKSTREAM_DIR / batch.VALIDATION_NAME).read_text(encoding="utf-8"))

    def test_scope_and_overlay_are_complete(self) -> None:
        expected = list(range(611, 656))
        self.assertEqual(expected, batch.selected_ids())
        self.assertEqual(expected, sorted(batch.TRANSLATIONS))
        self.assertEqual(expected, [entry["id"] for entry in self.overlay["entries"]])
        self.assertEqual(45, self.overlay["entry_count"])
        self.assertEqual(656, batch.NEXT_START_ID)
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
