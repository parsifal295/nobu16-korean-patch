from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent
VALIDATION = json.loads((ROOT / "validation.v1.json").read_text(encoding="utf-8"))
CONTRACT = json.loads((ROOT / "contract.v1.json").read_text(encoding="utf-8"))
OVERLAY = json.loads(next((ROOT / "public").glob("strdata_ko_jp_source_rebased_*.v1.json")).read_text(encoding="utf-8"))
HAN_KANA = re.compile(r"[\u2e80-\u2fff\u3040-\u30ff\u31f0-\u31ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")


class SteamJpRuntimeSkeletonTests(unittest.TestCase):
    def test_jp_only_source_contract(self) -> None:
        self.assertTrue(VALIDATION["passed"])
        self.assertFalse(VALIDATION["sc_container_read"])
        self.assertEqual("JP", OVERLAY["base_language"])
        self.assertEqual("MSG/JP/strdata.bin", OVERLAY["resource"])

    def test_exact_ten_paths(self) -> None:
        self.assertEqual(10, CONTRACT["candidate_root_file_count"])
        self.assertEqual(10, len(CONTRACT["candidate_root_paths"]))
        self.assertEqual(10, len(set(CONTRACT["candidate_root_paths"])))
        self.assertEqual(7, sum(path.startswith("MSG_PK/JP/") for path in CONTRACT["candidate_root_paths"]))
        self.assertTrue(VALIDATION["predecessor_vector"]["all_ten_exact"])
        self.assertEqual(10, VALIDATION["predecessor_vector"]["file_count"])

    def test_font_preservation(self) -> None:
        self.assertTrue(VALIDATION["fonts"]["all_passed"])
        self.assertEqual([[6, 7], [16, 17]], [row["changed_entries"] for row in VALIDATION["fonts"]["routes"]])
        for row in VALIDATION["fonts"]["routes"]:
            self.assertTrue(all(row["proofs"].values()))

    def test_source_free_public_json(self) -> None:
        for value in (OVERLAY, CONTRACT):
            text = json.dumps(value, ensure_ascii=False)
            self.assertIsNone(HAN_KANA.search(text))
            self.assertNotIn("\0", text)
        for entry in OVERLAY["entries"]:
            self.assertRegex(entry["source_jp_utf16le_sha256"], r"^[0-9A-F]{64}$")
            self.assertNotIn("source_jp", entry)

    def test_dry_run_fail_closed_until_complete(self) -> None:
        readiness = CONTRACT["readiness"]
        self.assertFalse(readiness["complete_candidate_root_ready"])
        self.assertFalse(CONTRACT["transaction"]["dry_run_allowed_now"])
        self.assertEqual(10, readiness["known_candidate_count"] + readiness["blocked_candidate_count"])


if __name__ == "__main__":
    unittest.main()
