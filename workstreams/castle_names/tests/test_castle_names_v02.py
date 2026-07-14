from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import unicodedata
from pathlib import Path
from typing import Any, Iterable


WORKSTREAM = Path(__file__).resolve().parents[1]
BUILDER_PATH = WORKSTREAM / "build_castle_names_v02.py"
BASE_PATH = WORKSTREAM / "public" / "castle_names_ko_9151_9542.v0.1.json"
RELEASE_PATH = WORKSTREAM / "public" / "castle_names_ko_9151_9542.v0.2.json"
VALIDATION_PATH = WORKSTREAM / "validation.v0.2.json"


def load_builder() -> Any:
    spec = importlib.util.spec_from_file_location("castle_names_v02_builder_test", BUILDER_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load castle-name v0.2 builder")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def walk_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, child in value.items():
            yield str(key)
            yield from walk_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_keys(child)


class CastleNamesV02Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_builder()
        cls.base = json.loads(BASE_PATH.read_text(encoding="utf-8"))
        cls.release = json.loads(RELEASE_PATH.read_text(encoding="utf-8"))
        cls.validation = json.loads(VALIDATION_PATH.read_text(encoding="utf-8"))

    def test_source_free_rebuild_is_byte_exact(self) -> None:
        with tempfile.TemporaryDirectory(prefix="nobu16-castle-v02-") as temporary:
            root = Path(temporary)
            overlay = root / "overlay.json"
            validation = root / "validation.json"
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(BUILDER_PATH),
                    "--output",
                    str(overlay),
                    "--validation-output",
                    str(validation),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(overlay.read_bytes(), RELEASE_PATH.read_bytes())
            self.assertEqual(validation.read_bytes(), VALIDATION_PATH.read_bytes())

    def test_all_392_entries_are_human_reviewed(self) -> None:
        entries = self.release["entries"]
        self.assertEqual(self.release["schema"], "nobu16.kr.castle-name-overlay.v0.2")
        self.assertTrue(self.release["source_text_free"])
        self.assertEqual(len(entries), 392)
        self.assertEqual([row["id"] for row in entries], list(range(9151, 9543)))
        self.assertEqual({row["status"] for row in entries}, {"reviewed"})
        self.assertEqual(self.release["review"]["reviewed_count"], 392)
        self.assertEqual(self.validation["reviewed_count"], 392)

    def test_exactly_53_review_changes_are_applied(self) -> None:
        before = {row["id"]: row["ko"] for row in self.base["entries"]}
        after = {row["id"]: row["ko"] for row in self.release["entries"]}
        changed = {entry_id for entry_id in before if before[entry_id] != after[entry_id]}
        self.assertEqual(len(changed), 53)
        self.assertEqual(self.release["review"]["approved_change_count"], 53)
        self.assertEqual(self.validation["approved_change_count"], 53)
        self.assertEqual(after[9256], "시즈")
        self.assertEqual(after[9447], "니타카야마")
        self.assertEqual(after[9361], "빗추 마쓰야마")
        self.assertFalse(any("츠" in value for value in after.values()))

    def test_public_overlay_contains_only_safe_korean_values(self) -> None:
        forbidden_keys = {"sc", "en", "jp", "source", "text", "translation"}
        self.assertFalse(forbidden_keys.intersection(key.lower() for key in walk_keys(self.release)))
        raw = RELEASE_PATH.read_text(encoding="utf-8")
        self.assertFalse(
            any(
                0x3400 <= ord(character) <= 0x4DBF
                or 0x4E00 <= ord(character) <= 0x9FFF
                or 0xF900 <= ord(character) <= 0xFAFF
                for character in raw
            )
        )
        for row in self.release["entries"]:
            value = row["ko"]
            self.assertEqual(value, unicodedata.normalize("NFC", value))
            self.assertTrue(value)
            self.assertEqual(value, value.strip(" "))
            self.assertNotIn("  ", value)
            self.assertTrue(all(char == " " or 0xAC00 <= ord(char) <= 0xD7A3 for char in value))

    def test_validation_contract_passes(self) -> None:
        self.assertTrue(self.validation["passed"])
        self.assertTrue(self.validation["geographic_tsu_uses_쓰"])
        self.assertEqual(self.validation["geographic_츠_remaining_count"], 0)
        self.assertTrue(self.validation["medium_confidence_long_vowel_decisions_applied"])
        self.assertTrue(self.validation["id_9361_space_preserved"])
        self.assertFalse(self.validation["installed_game_files_modified"])
        self.assertFalse(self.validation["process_memory_access"])
        self.assertFalse(self.validation["registry_access"])


if __name__ == "__main__":
    unittest.main()
