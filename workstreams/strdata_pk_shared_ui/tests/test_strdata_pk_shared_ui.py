from __future__ import annotations

import importlib.util
import json
import re
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
MODULE_PATH = ROOT / "workstreams" / "strdata_pk_shared_ui" / "build_strdata_pk_shared_ui.py"
SPEC = importlib.util.spec_from_file_location("build_strdata_pk_shared_ui", MODULE_PATH)
assert SPEC and SPEC.loader
builder = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(builder)
GAME_ROOT = ROOT.parent
HAN_OR_KANA_RE = re.compile(r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class StrdataPkSharedUiTests(unittest.TestCase):
    def test_public_overlay_is_source_free_and_pinned(self) -> None:
        overlay_path = MODULE_PATH.parent / "public" / builder.OVERLAY_NAME
        overlay = json.loads(overlay_path.read_text(encoding="utf-8"))
        builder.validate_overlay(overlay)
        self.assertEqual(overlay["entry_count"], 1)
        self.assertIsNone(HAN_OR_KANA_RE.search(overlay_path.read_text(encoding="utf-8")))

    def test_candidate_changes_only_shared_back_button_coordinate(self) -> None:
        with tempfile.TemporaryDirectory(prefix="n16_strdata_shared_ui_") as temporary:
            root = Path(temporary)
            candidate = root / builder.RESOURCE
            validation = builder.build(GAME_ROOT, root / "artifacts", candidate)
            self.assertTrue(candidate.is_file())
            self.assertEqual(validation["candidate"]["changed_coordinate_count"], 1)
            self.assertEqual(validation["candidate"]["unchanged_coordinate_count"], 32310)
            self.assertTrue(validation["deterministic_builds_identical"])

    def test_committed_validation_matches_rebuild(self) -> None:
        committed = json.loads((MODULE_PATH.parent / builder.VALIDATION_NAME).read_text(encoding="utf-8"))
        packed = builder.load_pinned_stock(GAME_ROOT)
        target, stats = builder.build_candidate(packed, builder.make_overlay())
        self.assertEqual(builder.sha256(target), committed["candidate"]["target_packed_sha256"])
        self.assertEqual(stats, committed["candidate"])


if __name__ == "__main__":
    unittest.main()
