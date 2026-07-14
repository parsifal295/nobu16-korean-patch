import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
V01 = ROOT / "public" / "province_names_ko_13975_14046.v0.1.json"
V02 = ROOT / "public" / "province_names_ko_13975_14046.v0.2.json"
VALIDATION = ROOT / "validation.v0.2.json"
BUILDER_PATH = ROOT / "build_province_names_v02.py"
KO_RE = re.compile(r"^[가-힣 ]+$")
CJK_RE = re.compile(r"[\u3040-\u30ff\u3400-\u9fff]")


def sha256(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def load_builder():
    spec = importlib.util.spec_from_file_location("province_names_v02_builder_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("failed to load province-name builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class ProvinceNamesTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.v01 = json.loads(V01.read_text(encoding="utf-8"))
        cls.v02 = json.loads(V02.read_text(encoding="utf-8"))
        cls.validation = json.loads(VALIDATION.read_text(encoding="utf-8"))
        cls.builder = load_builder()

    def test_v01_is_preserved_and_v02_scope_is_exact(self):
        self.assertTrue(V01.is_file())
        self.assertEqual(
            sha256(V01),
            self.validation["inputs"]["v0.1_overlay"]["sha256"],
        )
        for payload in (self.v01, self.v02):
            entries = payload["entries"]
            ids = [entry["id"] for entry in entries]
            self.assertEqual(ids, list(range(13975, 14047)))
            self.assertEqual(len(ids), 72)
            self.assertEqual(payload["scope"]["entry_count"], 72)

    def test_every_v02_entry_is_source_free_and_reviewed(self):
        for entry in self.v02["entries"]:
            self.assertEqual(set(entry), {"id", "ko", "status"})
            self.assertRegex(entry["ko"], KO_RE)
            self.assertEqual(entry["status"], "reviewed")
        self.assertTrue(self.v02["distribution_policy"]["contains_commercial_source_text"] is False)
        self.assertTrue(self.validation["source_text_free"])
        for path in (V01, V02, VALIDATION):
            self.assertIsNone(CJK_RE.search(path.read_text(encoding="utf-8")))

    def test_reviewed_overlay_is_a_deterministic_v01_merge(self):
        rebuilt = self.builder.build_reviewed_overlay(self.v01)
        self.assertEqual(self.builder.json_bytes(rebuilt), V02.read_bytes())
        self.assertEqual(rebuilt["review"]["changed_from_v0.1"], 0)
        self.assertEqual(rebuilt["review"]["reviewed_entry_count"], 72)

    def test_validation_pins_three_aligned_stock_tables(self):
        resources = self.validation["inputs"]["stock_resources"]
        self.assertEqual([item["language"] for item in resources], ["SC", "EN", "JP"])
        for item in resources:
            block = item["province_block"]
            self.assertEqual((block["first_id"], block["last_id"]), (13975, 14046))
            self.assertEqual(block["entry_count"], 72)
            self.assertEqual(block["nonempty_count"], 72)
            self.assertEqual(block["unique_source_label_count"], 72)
            self.assertEqual(len(block["sha256"]), 64)
            self.assertTrue(item["unchanged_parse_rebuild_byte_exact"])
        self.assertTrue(self.validation["result"]["same_ids_compared_in_sc_en_jp"])

    def test_validation_matches_public_artifact(self):
        artifact = self.validation["artifact"]
        self.assertEqual(artifact["path"], f"public/{V02.name}")
        self.assertEqual(artifact["sha256"], sha256(V02))
        self.assertEqual(self.validation["result"]["reviewed_entry_count"], 72)
        self.assertEqual(self.validation["result"]["changed_from_v0.1"], 0)

    def test_policy_decisions_are_stable(self):
        by_id = {entry["id"]: entry["ko"] for entry in self.v02["entries"]}
        self.assertEqual(by_id[13976], "무쓰")
        self.assertEqual(by_id[13995], "엣추")
        self.assertEqual(by_id[14015], "셋쓰")
        self.assertEqual(by_id[14018], "기이")
        self.assertEqual(by_id[14023], "빗추")
        self.assertEqual(by_id[14044], "사쓰마")
        self.assertEqual(by_id[14046], "쓰시마")
        self.assertEqual(by_id[13986], by_id[14034])
        self.assertEqual(len(set(by_id.values())), 71)
        self.assertEqual(self.v02["translation_policy"]["geographic_tsu"], "쓰")
        self.assertEqual(
            self.v02["translation_policy"]["japanese_long_vowels"],
            "not_duplicated",
        )


if __name__ == "__main__":
    unittest.main()
