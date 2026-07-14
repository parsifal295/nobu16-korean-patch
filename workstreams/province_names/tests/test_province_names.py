import json
import pathlib
import re
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
OVERLAY = ROOT / "public" / "province_names_ko_13975_14046.v0.1.json"
KO_RE = re.compile(r"^[가-힣 ]+$")


class ProvinceNamesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = json.loads(OVERLAY.read_text(encoding="utf-8"))
        cls.entries = cls.payload["entries"]

    def test_scope_is_exact_and_contiguous(self):
        ids = [entry["id"] for entry in self.entries]
        self.assertEqual(ids, list(range(13975, 14047)))
        self.assertEqual(len(ids), 72)
        self.assertEqual(self.payload["scope"]["entry_count"], 72)

    def test_public_entries_only_contain_id_and_korean(self):
        for entry in self.entries:
            self.assertEqual(set(entry), {"id", "ko"})
            self.assertRegex(entry["ko"], KO_RE)

    def test_public_overlay_is_source_free(self):
        text = OVERLAY.read_text(encoding="utf-8")
        self.assertIsNone(re.search(r"[\u3040-\u30ff\u3400-\u9fff]", text))
        self.assertFalse(
            {"source", "source_text", "sc", "jp", "en", "translation"}
            & set(self.payload)
        )


if __name__ == "__main__":
    unittest.main()
