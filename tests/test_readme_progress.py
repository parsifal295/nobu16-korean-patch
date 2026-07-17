from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
RELEASE_PROGRESS = ROOT / "data" / "public" / "steam_jp_117_candidate_v10_progress.v1.json"
SPEC = importlib.util.spec_from_file_location(
    "readme_progress", ROOT / "tools" / "update_readme_progress.py"
)
assert SPEC and SPEC.loader
readme_progress = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(readme_progress)


class ReadmeProgressTests(unittest.TestCase):
    def test_v010_release_ledger_has_the_public_progress_facts(self) -> None:
        payload = readme_progress.load_release_progress()
        self.assertEqual(payload, json.loads(RELEASE_PROGRESS.read_text(encoding="utf-8")))
        self.assertEqual(payload["candidate_release"], "v0.10.0")
        self.assertEqual(payload["status"], "released")
        self.assertEqual(payload["candidate"]["file_count"], 14)

        translation = payload["translation"]
        self.assertEqual(
            (
                translation["active_text_tables"],
                translation["korean_applied"],
                translation["high_confidence_scope"],
            ),
            (10, 2489, 2498),
        )
        self.assertEqual(
            translation["candidate_high_confidence_remaining"],
            translation["official_credit_preserved"]
            + translation["runtime_structure_preserved"],
        )

    def test_render_states_that_text_translation_is_complete(self) -> None:
        rendered = readme_progress.render()
        self.assertIn("v0.10.0 — 텍스트 번역 완료", rendered)
        self.assertIn("게임 내 번역 대상 텍스트 번역을 완료했습니다.", rendered)
        self.assertIn("순정 PC 일본어 원문과 PC EN/SC/TC 대조", rendered)
        self.assertIn("스위치판 한글은 기준으로 사용하지 않습니다.", rendered)
        self.assertIn("고확신 오역만 별도 검증 후 수정합니다.", rendered)
        self.assertIn("이벤트 스크립트 줄바꿈 전수 검수·보정은 완료했습니다.", rendered)
        self.assertIn("이미지 번역은 진행 중입니다.", rendered)
        self.assertNotIn("2,489", rendered)
        self.assertNotIn("추가 수동 검토", rendered)
        self.assertNotIn("SHA-256", rendered)
        self.assertNotIn("후보 ZIP", rendered)
        self.assertNotIn("설치=True", rendered)
        self.assertNotIn("RES_JP", rendered)

    def test_readme_progress_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, "-B", "tools/update_readme_progress.py", "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_readme_keeps_installation_release_and_rights_information(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertIn("**Japanese**", readme)
        self.assertIn("현재 공개 안정판은 [v0.10.2]", readme)
        self.assertIn("비공식 팬메이드", readme)
        self.assertIn("KOEI TECMO GAMES", readme)
        self.assertNotIn("<!-- active-text-audit:start -->", readme)


if __name__ == "__main__":
    unittest.main()
