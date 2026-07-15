import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "data" / "public" / "steam_jp_117_progress.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "readme_progress", ROOT / "tools" / "update_readme_progress.py"
)
assert SPEC and SPEC.loader
readme_progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readme_progress)


class ReadmeProgressTests(unittest.TestCase):
    def test_runtime_contract_is_steam_jp_117(self):
        payload = json.loads(PROGRESS.read_text(encoding="utf-8"))
        self.assertEqual(payload["release"], "v0.6.0")
        self.assertEqual(
            payload["runtime"],
            {
                "distribution": "Steam",
                "pk_version": "1.1.7",
                "steam_build_id": 18823764,
                "language_route": "JP",
                "launcher_language": "日本語 / Japanese",
            },
        )

    def test_translation_accounting_is_exact(self):
        translation = readme_progress.load_progress()["translation"]
        msgui = translation["msgui"]
        self.assertEqual(msgui["safely_mapped"], 3693)
        self.assertEqual(
            msgui["safely_mapped"],
            msgui["effective_changes"] + msgui["source_equal_noops"],
        )
        self.assertEqual(
            msgui["catalog_entries"], msgui["safely_mapped"] + msgui["withheld"]
        )

        common = translation["common_messages"]
        self.assertEqual((common["applied"], common["unresolved"]), (39507, 96))
        self.assertEqual(common["duplicate_context_collapsed"], 50)

        msggame = translation["msggame"]
        self.assertEqual(
            msggame["semantic_targets"], msggame["applied"] + msggame["remaining"]
        )
        self.assertEqual((msggame["applied"], msggame["remaining"]), (24211, 4061))

        strdata = translation["strdata"]
        self.assertEqual(strdata["safe_targets"], strdata["applied"] + strdata["withheld"])
        self.assertEqual((strdata["applied"], strdata["withheld"]), (24524, 1))
        self.assertEqual(translation["fonts"], {"containers": 2, "verified": 2})

    def test_render_is_japanese_runtime_only(self):
        rendered = readme_progress.render()
        self.assertIn("Steam PK v1.1.7", rendered)
        self.assertIn("`msgui.bin` | 안전 이식 3,693 / 4,037 (91.5%)", rendered)
        self.assertIn("`msggame.bin` | 적용 24,211 / 28,272 (85.6%)", rendered)
        self.assertIn("`strdata.bin` | 안전 이식 24,524 / 24,525", rendered)
        self.assertNotIn("MSG_PK/SC", rendered)
        self.assertNotIn("RES_SC", rendered)
        self.assertNotIn("비Steam", rendered)

    def test_runtime_qa_is_recorded(self):
        qa = readme_progress.load_progress()["runtime_qa"]
        self.assertTrue(qa["steam_install_applied"])
        self.assertTrue(qa["exact_ten_target_hashes"])
        self.assertEqual(qa["original_backups_valid"], 10)
        self.assertEqual(qa["launcher_update_label"], "Update 1.1.7")
        self.assertTrue(qa["korean_title_prompt_observed"])
        self.assertTrue(qa["korean_main_menu_observed"])

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

    def test_readme_has_no_simplified_chinese_runtime_instruction(self):
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        block = readme.split(readme_progress.START, 1)[1].split(
            readme_progress.END, 1
        )[0]
        self.assertIn("일본어 경로 한글 폰트", block)
        self.assertNotIn("MSG/SC", block)
        self.assertNotIn("MSG_PK/SC", block)
        self.assertNotIn("RES_SC", block)


if __name__ == "__main__":
    unittest.main()
