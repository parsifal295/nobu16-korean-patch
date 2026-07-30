from __future__ import annotations

import importlib.util
import json
import re
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

# README is living documentation. Historical release wording belongs in the
# versioned release notes, so this contract deliberately does not pin a version.
CURRENT_RELEASE_RE = re.compile(
    r"현재 공개 안정판은 \[(v\d+\.\d+\.\d+)\]"
    r"\([^)\s]+/releases/tag/\1\)입니다\."
)


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
        self.assertIn("인물·이벤트 대사 번역 품질을 전수 감사", rendered)
        self.assertIn("이벤트 스크립트 줄바꿈 검수·보정과 이미지 번역은 진행 중입니다.", rendered)
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

    def test_readme_has_one_generated_progress_block(self) -> None:
        readme = README.read_text(encoding="utf-8")
        self.assertEqual(readme.count(readme_progress.START), 1)
        self.assertEqual(readme.count(readme_progress.END), 1)
        self.assertLess(
            readme.index(readme_progress.START),
            readme.index(readme_progress.END),
        )

    def test_current_release_link_and_section_agree(self) -> None:
        readme = README.read_text(encoding="utf-8")
        match = CURRENT_RELEASE_RE.search(readme)
        self.assertIsNotNone(match, "current stable release link is missing or inconsistent")
        current_release = match.group(1)
        self.assertIn(f"## {current_release} —", readme)

    def test_readme_keeps_current_installation_and_rights_contract(self) -> None:
        readme = README.read_text(encoding="utf-8")
        normalized = " ".join(readme.split())
        for text in (
            "**Japanese**",
            "게임 파일 무결성 확인",
            "비공식 팬메이드",
            "KOEI TECMO GAMES",
            "완전한 게임 리소스",
            "`NOBU16PK.exe`",
        ):
            self.assertIn(text, normalized)
        self.assertNotIn("<!-- active-text-audit:start -->", readme)


if __name__ == "__main__":
    unittest.main()
