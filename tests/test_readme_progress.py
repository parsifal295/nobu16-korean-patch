import json
import pathlib
import subprocess
import sys
import unittest

from tools import update_readme_progress as readme_progress


ROOT = pathlib.Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "data" / "public" / "translation_progress.v0.1.json"

EXPECTED_STRING_TARGETS = {
    "MSG_PK/SC/msgui.bin": (5100, 4037),
    "MSG_PK/SC/msgev.bin": (17910, 12906),
    "MSG_PK/SC/msgdata.bin": (29210, 25534),
    "MSG_PK/SC/msgbre.bin": (3000, 2217),
    "MSG_PK/SC/msgire.bin": (122, 122),
    "MSG_PK/SC/msgstf.bin": (20, 8),
    "MSG_PK/SC/msggame.bin": (25598, 16482),
    "MSG/SC/msggame.bin": (21225, 12268),
    "MSG/SC/strdata.bin": (32311, 26690),
    "MSG/SC/ev_strdata.bin": (17868, 11687),
}


class ReadmeProgressTests(unittest.TestCase):
    def test_pinned_string_inventory_is_complete(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        actual = {
            resource["path"]: (
                resource["total_slots"],
                resource["translation_target_total"],
            )
            for resource in payload["resources"]
            if resource["kind"] == "strings"
        }
        self.assertEqual(actual, EXPECTED_STRING_TARGETS)
        self.assertEqual(sum(target for _, target in actual.values()), 111951)
        self.assertEqual(payload["completed_statuses"], ["translated", "reviewed"])

    def test_msggame_record_and_literal_counts_are_explicit_and_included(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        actual = {
            resource["path"]: (
                resource["record_total"],
                resource["total_slots"],
                resource["translation_target_total"],
            )
            for resource in payload["resources"]
            if resource["path"].endswith("msggame.bin")
        }
        self.assertEqual(
            actual,
            {
                "MSG_PK/SC/msggame.bin": (21581, 25598, 16482),
                "MSG/SC/msggame.bin": (19152, 21225, 12268),
            },
        )

    def test_msggame_coordinate_overlay_is_counted_as_completed(self):
        coverage, completed = readme_progress.overlay_stats(
            [
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b01r0003_b02r0086_0197.v0.1.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0198_0297.v0.2.json",
                "workstreams/msggame/public/"
                "msggame_ko_system_messages_b02r0298_0565.v0.3.json",
            ],
            {"translated", "reviewed"},
        )
        self.assertEqual(450, len(coverage))
        self.assertEqual(coverage, completed)

    def test_readme_progress_is_current(self):
        result = subprocess.run(
            [sys.executable, "-B", "tools/update_readme_progress.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
